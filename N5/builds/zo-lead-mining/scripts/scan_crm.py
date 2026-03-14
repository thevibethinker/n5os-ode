#!/usr/bin/env python3
"""
Scan CRM individuals and score them for Zo Computer lead potential.

Usage:
    python3 scan_crm.py --range a-j --deposit D1.1
    python3 scan_crm.py --range k-z --deposit D1.2
    python3 scan_crm.py --dry-run --range a-j
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

import aiohttp

CRM_DIR = Path("/home/workspace/Personal/Knowledge/CRM/individuals")
DEPOSITS_DIR = Path("/home/workspace/N5/builds/zo-lead-mining/deposits")
ZO_API = "https://api.zo.computer/zo/ask"
MODEL_NAME = "byok:0771a084-ed26-496e-ac1b-bddc85ba2653"
MAX_CONCURRENT = 5
BATCH_SIZE = 15

ZO_LEAD_PROMPT = """You are scoring contacts for Zo Computer lead potential. Zo is a personal AI computer — a remote Linux server with an AI assistant that has full access to your files, apps, calendar, email, and can run code, deploy sites, automate workflows, and more.

Score each person 1-5:
- 5 = Perfect fit (tech founder/creator who would deeply adopt a personal AI computer)
- 4 = Strong fit (tech-forward leader, active builder, influential voice in tech/AI)
- 3 = Good fit (would benefit from Zo, has relevant network/influence)
- 2 = Possible (some signals but unclear fit)
- 1 = Low fit (no clear connection to Zo use case)

Archetypes (assign all that apply):
- Power User: Would deeply use AI workflows, automation, personal OS
- Promoter: Content creator, influencer who would talk about Zo publicly
- Creator: Builder who would create skills/integrations for Zo
- Strategic Leader: CEO/founder who would adopt Zo for their team
- Investor/Advisor: VC or advisor in AI/productivity/dev-tools

For each person, respond with ONLY a JSON array. Each element:
{"name": "Full Name", "org": "Org", "role": "Role", "score": N, "archetypes": [...], "rationale": "1 line why"}

Only include people scoring >= 3. If none qualify, return [].

Here are the contacts to score:

"""


def parse_crm_file(filepath: Path) -> dict:
    """Extract key fields from a CRM markdown file."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    lines = text.strip().split("\n")

    result = {
        "filename": filepath.name,
        "name": "",
        "org": "",
        "role": "",
        "lead_type": "",
        "status": "",
        "summary": "",
    }

    in_frontmatter = False
    content_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue

        if stripped.startswith("# ") and not result["name"]:
            result["name"] = stripped[2:].strip()
        elif "**Organization:**" in stripped:
            result["org"] = re.sub(r"\*\*Organization:\*\*\s*", "", stripped).strip()
        elif "**Role:**" in stripped:
            result["role"] = re.sub(r"\*\*Role:\*\*\s*", "", stripped).strip()
        elif "**Lead Type:**" in stripped:
            result["lead_type"] = re.sub(r"\*\*Lead Type:\*\*\s*", "", stripped).strip()
        elif "**Status:**" in stripped:
            result["status"] = re.sub(r"\*\*Status:\*\*\s*", "", stripped).strip()
        else:
            content_lines.append(stripped)

    # Take first 500 chars of content as summary context
    content = " ".join(l for l in content_lines if l and not l.startswith("|"))
    result["summary"] = content[:500]

    return result


def format_contact_for_prompt(contact: dict) -> str:
    """Format a contact for inclusion in the scoring prompt."""
    parts = [f"**{contact['name']}**"]
    if contact["org"]:
        parts.append(f"Org: {contact['org']}")
    if contact["role"]:
        parts.append(f"Role: {contact['role']}")
    if contact["lead_type"]:
        parts.append(f"Lead Type: {contact['lead_type']}")
    if contact["status"]:
        parts.append(f"Status: {contact['status']}")
    if contact["summary"]:
        parts.append(f"Context: {contact['summary'][:300]}")
    return " | ".join(parts)


async def score_batch(
    session: aiohttp.ClientSession,
    batch: list[dict],
    semaphore: asyncio.Semaphore,
    batch_num: int,
    dry_run: bool = False,
) -> list[dict]:
    """Score a batch of contacts via /zo/ask."""
    contact_text = "\n".join(
        f"{i+1}. {format_contact_for_prompt(c)}" for i, c in enumerate(batch)
    )
    prompt = ZO_LEAD_PROMPT + contact_text

    if dry_run:
        print(f"  [DRY-RUN] Batch {batch_num}: {len(batch)} contacts, prompt ~{len(prompt)} chars")
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

                # Extract JSON from response
                # Try to find JSON array in the output
                json_match = re.search(r"\[.*\]", output, re.DOTALL)
                if json_match:
                    leads = json.loads(json_match.group())
                    print(f"  Batch {batch_num}: {len(leads)} leads found")
                    # Add source filenames
                    name_to_file = {c["name"].lower(): c["filename"] for c in batch}
                    for lead in leads:
                        lead_name_lower = lead.get("name", "").lower()
                        lead["crm_file"] = name_to_file.get(lead_name_lower, "unknown")
                    return leads
                else:
                    print(f"  Batch {batch_num}: No JSON array in response")
                    return []
        except Exception as e:
            print(f"  Batch {batch_num} ERROR: {e}")
            return []


async def main():
    parser = argparse.ArgumentParser(description="Scan CRM for Zo leads")
    parser.add_argument("--range", required=True, help="Letter range: a-j or k-z")
    parser.add_argument("--deposit", required=True, help="Deposit ID: D1.1 or D1.2")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    # Parse range
    start_letter, end_letter = args.range.split("-")

    # Get matching files
    all_files = sorted(CRM_DIR.glob("*.md"))
    filtered = [
        f
        for f in all_files
        if f.name[0].lower() >= start_letter and f.name[0].lower() <= end_letter
    ]

    print(f"CRM Scan: range={args.range}, files={len(filtered)}, deposit={args.deposit}")

    # Parse all contacts
    contacts = []
    for filepath in filtered:
        contact = parse_crm_file(filepath)
        if contact["name"]:
            contacts.append(contact)

    print(f"Parsed {len(contacts)} contacts with names")

    # Batch and score
    batches = [contacts[i : i + BATCH_SIZE] for i in range(0, len(contacts), BATCH_SIZE)]
    print(f"Processing {len(batches)} batches of ~{BATCH_SIZE}")

    all_leads = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with aiohttp.ClientSession() as session:
        tasks = [
            score_batch(session, batch, semaphore, i + 1, args.dry_run)
            for i, batch in enumerate(batches)
        ]
        results = await asyncio.gather(*tasks)

    for batch_leads in results:
        all_leads.extend(batch_leads)

    print(f"\nTotal leads (score >= 3): {len(all_leads)}")

    if args.dry_run:
        print("[DRY-RUN] Would write deposit — exiting.")
        return

    # Write deposit
    deposit = {
        "drop_id": args.deposit,
        "status": "complete",
        "total_scanned": len(contacts),
        "leads": all_leads,
    }

    deposit_path = DEPOSITS_DIR / f"{args.deposit}.json"
    deposit_path.write_text(json.dumps(deposit, indent=2))
    print(f"Deposit written: {deposit_path}")


if __name__ == "__main__":
    asyncio.run(main())
