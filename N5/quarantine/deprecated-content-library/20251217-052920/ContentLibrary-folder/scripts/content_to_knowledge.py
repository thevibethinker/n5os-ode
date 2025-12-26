#!/usr/bin/env python3
"""
content_to_knowledge.py.new - Bridge Content Library v3 → Knowledge facts.

This is an append-only bridge that promotes selected content library segments
into the N5 knowledge facts store (`N5/knowledge/facts.jsonl`).

Differences from the legacy version:
- Reads from the v3 SQLite DB instead of the JSON library
- Works primarily at the block level (blocks table) when available
- Tracks promotions in the `knowledge_refs` table (one row per block_id)

Behavior:
- Given an item/entry ID, selects candidate blocks (or falls back to summary/notes)
- For each selected index, writes a fact if not already present
- Avoids duplicates via text-level check + knowledge_refs guarding
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("content_library_v3_content_to_knowledge")

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")
KNOWLEDGE_FACTS_PATH = Path("/home/workspace/N5/knowledge/facts.jsonl")


def load_knowledge_facts() -> List[dict]:
    facts: List[dict] = []
    if KNOWLEDGE_FACTS_PATH.exists():
        with KNOWLEDGE_FACTS_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        facts.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.warning("Skipping malformed fact line: %s", line[:80])
    return facts


def fact_exists(facts: Iterable[dict], subject: str, predicate: str, obj: str) -> bool:
    for fact in facts:
        if (
            fact.get("subject") == subject
            and fact.get("predicate") == predicate
            and fact.get("object") == obj
        ):
            return True
    return False


def append_fact(fact: dict) -> None:
    KNOWLEDGE_FACTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with KNOWLEDGE_FACTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fact, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Promote Content Library v3 blocks/summary into N5 knowledge facts (append-only)"
        ),
    )
    parser.add_argument(
        "--entry-id",
        "--item-id",
        dest="entry_id",
        required=True,
        help="Content Library item ID to promote from",
    )
    parser.add_argument(
        "--finding-indices",
        nargs="+",
        type=int,
        help=(
            "Indices of segments to promote (0-based). If omitted, promote all candidates.\n"
            "For block-based items, indices correspond to blocks ordered by block_code."
        ),
    )

    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        item_row = conn.execute(
            "SELECT * FROM items WHERE id = ?",
            (args.entry_id,),
        ).fetchone()
        if not item_row:
            print(f"Error: Entry/Item ID {args.entry_id} not found in Content Library v3")
            return 1

        item = dict(item_row)
        title = item.get("title") or args.entry_id

        # Prefer blocks table when available
        block_rows = list(
            conn.execute(
                "SELECT id, block_code, block_type, content, confidence "
                "FROM blocks WHERE item_id = ? ORDER BY block_code",
                (args.entry_id,),
            )
        )

        candidates: List[dict] = []
        use_blocks = bool(block_rows)

        if use_blocks:
            for br in block_rows:
                candidates.append(
                    {
                        "kind": "block",
                        "block_id": br["id"],
                        "text": br["content"],
                        "block_code": br["block_code"],
                        "block_type": br["block_type"],
                    }
                )
        else:
            # Fallback: use summary, then notes
            summary = (item.get("summary") or "").strip()
            notes = (item.get("notes") or "").strip()

            if summary:
                candidates.append(
                    {
                        "kind": "summary",
                        "block_id": None,
                        "text": summary,
                        "block_code": None,
                        "block_type": "summary",
                    }
                )
            if notes:
                candidates.append(
                    {
                        "kind": "notes",
                        "block_id": None,
                        "text": notes,
                        "block_code": None,
                        "block_type": "notes",
                    }
                )

        if not candidates:
            print(
                f"Error: No blocks, summary, or notes found for entry {args.entry_id}; "
                "nothing to promote.",
            )
            return 1

        if args.finding_indices:
            indices: Iterable[int] = args.finding_indices
        else:
            indices = range(len(candidates))

        facts = load_knowledge_facts()
        promoted = 0

        for idx in indices:
            if idx < 0 or idx >= len(candidates):
                print(f"Warning: Candidate index {idx} out of range; skipping")
                continue

            cand = candidates[idx]
            text = str(cand["text"]).strip()
            if not text:
                logger.info("Skipping empty text at index %s", idx)
                continue

            subject = title
            predicate = "has-key-finding"
            obj = text

            # Skip if fact already exists textually
            if fact_exists(facts, subject, predicate, obj):
                print(f"Skipping duplicate fact for index {idx}: already exists in facts store")
                continue

            # Guard with knowledge_refs for block-based promotions
            block_id = cand.get("block_id")
            if block_id:
                existing_ref = conn.execute(
                    "SELECT 1 FROM knowledge_refs WHERE block_id = ?",
                    (block_id,),
                ).fetchone()
                if existing_ref:
                    print(
                        "Skipping block %s at index %s: already recorded in knowledge_refs"
                        % (block_id, idx),
                    )
                    continue

            fact_id = (
                f"fact_{args.entry_id}_{idx}_"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )

            fact = {
                "id": fact_id,
                "subject": subject,
                "predicate": predicate,
                "object": obj,
                "source_entry_id": args.entry_id,
                "source_block_id": block_id,
                "date_added": datetime.now().isoformat(),
            }

            append_fact(fact)
            facts.append(fact)
            promoted += 1

            # Record promotion in knowledge_refs when we have a block_id
            if block_id:
                conn.execute(
                    "INSERT OR REPLACE INTO knowledge_refs "
                    "(block_id, knowledge_type, knowledge_id, source_type, source_id, promoted_at, notes) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        block_id,
                        "fact",
                        fact_id,
                        "content_library_v3",
                        args.entry_id,
                        datetime.now().isoformat(),
                        None,
                    ),
                )

            print(f"Promoted fact {fact_id}")

        conn.commit()

    finally:
        conn.close()

    print(f"Total promoted: {promoted}")
    return 0 if promoted > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

