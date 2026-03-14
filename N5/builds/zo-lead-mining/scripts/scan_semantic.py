#!/usr/bin/env python3
"""
Scan semantic memory for Zo Computer lead signals.

Usage:
    python3 scan_semantic.py --mode tech --deposit D1.3
    python3 scan_semantic.py --mode influence --deposit D1.4
    python3 scan_semantic.py --dry-run --mode tech
"""

import argparse
import asyncio
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

import aiohttp

VECTORS_DB = Path("/home/workspace/N5/cognition/vectors_v2.db")
DEPOSITS_DIR = Path("/home/workspace/N5/builds/zo-lead-mining/deposits")
ZO_API = "https://api.zo.computer/zo/ask"
MODEL_NAME = "byok:0771a084-ed26-496e-ac1b-bddc85ba2653"
MAX_CONCURRENT = 3
BATCH_SIZE = 20

TECH_QUERIES = [
    "%AI tool%",
    "%automation%",
    "%developer%",
    "%Zo Computer%",
    "%personal OS%",
    "%workflow%",
    "%API%",
    "%integration%",
    "%machine learning%",
    "%startup%",
    "%SaaS%",
    "%engineer%",
    "%CTO%",
    "%technical founder%",
    "%build%product%",
    "%deploy%",
    "%code%",
    "%open source%",
]

INFLUENCE_QUERIES = [
    "%investor%",
    "%venture%capital%",
    "%CEO%",
    "%founder%",
    "%influencer%",
    "%content creator%",
    "%advisor%",
    "%community%leader%",
    "%thought leader%",
    "%audience%",
    "%newsletter%",
    "%podcast%",
    "%executive%",
    "%director%",
    "%VP %",
    "%partner%fund%",
    "%angel%invest%",
    "%board%member%",
]

EXTRACT_PROMPT = """You are extracting named individuals from text blocks that come from a personal knowledge base. 
These blocks may be from conversations, meeting notes, emails, documents, or CRM records.

Your task: identify any NAMED INDIVIDUALS mentioned who could be leads for Zo Computer — a personal AI computer (remote Linux server with AI assistant that manages files, apps, calendar, email, code, workflows).

For each person you find, assess their Zo potential:
- 5 = Perfect fit (tech founder/creator who would deeply adopt a personal AI computer)
- 4 = Strong fit (tech-forward leader, active builder, influential voice)
- 3 = Good fit (would benefit, has relevant network/influence)
- 2 or below = skip

Archetypes: Power User, Promoter, Creator, Strategic Leader, Investor/Advisor

Respond with ONLY a JSON array. Each element:
{{"name": "Full Name", "org": "Org if known", "role": "Role if known", "score": N, "archetypes": [...], "rationale": "1 line — what signal from this text"}}

Only include people scoring >= 3. If none, return [].
IMPORTANT: Do NOT include "V" or "Vrijen" — that's the system owner.

Text blocks to analyze:

"""


def query_blocks(mode: str) -> list[dict]:
    """Query semantic memory for relevant blocks."""
    queries = TECH_QUERIES if mode == "tech" else INFLUENCE_QUERIES

    conn = sqlite3.connect(str(VECTORS_DB))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    seen_ids = set()
    blocks = []

    for pattern in queries:
        cursor.execute(
            """
            SELECT b.id, b.content, r.path 
            FROM blocks b 
            JOIN resources r ON b.resource_id = r.id 
            WHERE b.content LIKE ? 
            AND length(b.content) > 50
            LIMIT 50
            """,
            (pattern,),
        )
        for row in cursor.fetchall():
            if row["id"] not in seen_ids:
                seen_ids.add(row["id"])
                blocks.append(
                    {
                        "content": row["content"][:600],
                        "path": row["path"],
                    }
                )

    conn.close()
    print(f"Found {len(blocks)} unique blocks from {len(queries)} queries")
    return blocks


async def extract_leads_from_batch(
    session: aiohttp.ClientSession,
    batch: list[dict],
    semaphore: asyncio.Semaphore,
    batch_num: int,
    dry_run: bool = False,
) -> list[dict]:
    """Extract leads from a batch of semantic memory blocks."""
    block_text = "\n---\n".join(
        f"[Source: {b['path']}]\n{b['content']}" for b in batch
    )
    prompt = EXTRACT_PROMPT + block_text

    if dry_run:
        print(f"  [DRY-RUN] Batch {batch_num}: {len(batch)} blocks, prompt ~{len(prompt)} chars")
        return []

    async with semaphore:
        try:
            async with session.post(
                ZO_API,
                headers={
                    "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                    "content-type": "application/json",
                },
                json={
                    "input": prompt,
                    "model_name": MODEL_NAME,
                },
            ) as resp:
                data = await resp.json()
                output = data.get("output", "")

                json_match = re.search(r"\[.*\]", output, re.DOTALL)
                if json_match:
                    leads = json.loads(json_match.group())
                    # Add source info
                    source_paths = [b["path"] for b in batch]
                    for lead in leads:
                        lead["source"] = f"semantic:{batch_num}"
                    print(f"  Batch {batch_num}: {len(leads)} leads extracted")
                    return leads
                else:
                    print(f"  Batch {batch_num}: No leads found")
                    return []
        except Exception as e:
            print(f"  Batch {batch_num} ERROR: {e}")
            return []


async def main():
    parser = argparse.ArgumentParser(description="Scan semantic memory for Zo leads")
    parser.add_argument("--mode", required=True, choices=["tech", "influence"])
    parser.add_argument("--deposit", required=True, help="Deposit ID: D1.3 or D1.4")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Semantic Scan: mode={args.mode}, deposit={args.deposit}")

    blocks = query_blocks(args.mode)

    batches = [blocks[i : i + BATCH_SIZE] for i in range(0, len(blocks), BATCH_SIZE)]
    print(f"Processing {len(batches)} batches of ~{BATCH_SIZE}")

    all_leads = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with aiohttp.ClientSession() as session:
        tasks = [
            extract_leads_from_batch(session, batch, semaphore, i + 1, args.dry_run)
            for i, batch in enumerate(batches)
        ]
        results = await asyncio.gather(*tasks)

    for batch_leads in results:
        all_leads.extend(batch_leads)

    # Deduplicate by name within this deposit
    seen_names = {}
    deduped = []
    for lead in all_leads:
        name = lead.get("name", "").lower().strip()
        if name and name not in seen_names:
            seen_names[name] = True
            deduped.append(lead)
        elif name in seen_names:
            # Update score if higher
            for existing in deduped:
                if existing.get("name", "").lower().strip() == name:
                    if lead.get("score", 0) > existing.get("score", 0):
                        existing["score"] = lead["score"]
                        existing["rationale"] = lead["rationale"]
                    break

    print(f"\nTotal leads (score >= 3, deduped): {len(deduped)}")

    if args.dry_run:
        print("[DRY-RUN] Would write deposit — exiting.")
        return

    deposit = {
        "drop_id": args.deposit,
        "status": "complete",
        "queries_run": len(TECH_QUERIES if args.mode == "tech" else INFLUENCE_QUERIES),
        "blocks_scanned": len(blocks),
        "leads": deduped,
    }

    deposit_path = DEPOSITS_DIR / f"{args.deposit}.json"
    deposit_path.write_text(json.dumps(deposit, indent=2))
    print(f"Deposit written: {deposit_path}")


if __name__ == "__main__":
    asyncio.run(main())
