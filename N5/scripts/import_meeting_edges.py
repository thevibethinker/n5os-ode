#!/usr/bin/env python3
"""Ingest backfill meeting edges into `brain.db`."""

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, "/home/workspace")
from N5.cognition.graph_store import GraphStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
LOG = logging.getLogger("import_meeting_edges")

PENDING_DIR = Path("/home/workspace/N5/review/edges/pending")
COMMITTED_DIR = Path("/home/workspace/N5/review/edges/backfill/completed")


def load_entries(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def summarize_metadata(entry: Dict[str, any], batch_name: str) -> Dict[str, any]:
    return {
        "source_display": entry.get("source_display"),
        "target_display": entry.get("target_display"),
        "evolution_type": entry.get("evolution_type"),
        "batch_file": batch_name,
        "raw_entry": entry,
    }


def ensure_edge_types(store: GraphStore, relations):
    for rel in relations:
        store.add_edge_type(
            relation=rel,
            category="meeting",
            description="Imported from Context Graph backfill",
            inverse_relation=None,
        )


def ingest(pending_dir: Path, move_files: bool = True) -> None:
    pending_files = sorted(pending_dir.glob("*.jsonl"))
    if not pending_files:
        LOG.info("No pending edge files to process")
        return
    store = GraphStore()
    added_relations = set()
    try:
        for batch_path in pending_files:
            LOG.info("Processing %s", batch_path.name)
            batch_added = 0
            batch_skipped = 0
            for entry in load_entries(batch_path):
                relation = entry.get("relation")
                meeting_id = entry.get("context_meeting_id")
                if not relation or not meeting_id:
                    batch_skipped += 1
                    continue
                source_type = entry.get("source_type", "idea")
                source_id = entry.get("source_id")
                target_type = entry.get("target_type", "idea")
                target_id = entry.get("target_id")
                evidence = entry.get("evidence") or entry.get("context")
                if not source_id or not target_id:
                    batch_skipped += 1
                    continue
                normalized_relation = store.normalize_relation_type(relation)
                added_relations.add(normalized_relation)
                if store.has_meeting_edge(source_id, relation, target_id, meeting_id):
                    batch_skipped += 1
                    continue
                metadata = summarize_metadata(entry, batch_path.name)
                store.add_meeting_edge(
                    source_type=source_type,
                    source_id=source_id,
                    relation=relation,
                    target_type=target_type,
                    target_id=target_id,
                    meeting_id=meeting_id,
                    evidence=evidence or None,
                    metadata=metadata,
                )
                batch_added += 1
            LOG.info("Batch %s: added %d edges, skipped %d", batch_path.name, batch_added, batch_skipped)
            if move_files:
                dest = COMMITTED_DIR / batch_path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(batch_path), str(dest))
                LOG.info("Moved %s → %s", batch_path.name, dest)
    finally:
        ensure_edge_types(store, added_relations)
        store.close()


def main():
    parser = argparse.ArgumentParser(description="Import meeting edges into brain.db")
    parser.add_argument("--pending-dir", type=Path, default=PENDING_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-files", action="store_true", help="Don't move files after importing")
    args = parser.parse_args()

    ingest(args.pending_dir, move_files=not args.keep_files and not args.dry_run)
    if args.dry_run:
        LOG.info("Dry-run complete; no files moved.")


if __name__ == "__main__":
    main()
