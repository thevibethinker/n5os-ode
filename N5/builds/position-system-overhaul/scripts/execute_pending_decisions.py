#!/usr/bin/env python3
"""
Execute approved pending decisions:
- 10 merges
- 40 promotions
- 4 skips (1 merge, 3 promotions)
"""
import asyncio
import aiohttp
import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import random
import string

BUILD_DIR = Path("/home/workspace/N5/builds/position-system-overhaul")
CANDIDATES_PATH = Path("/home/workspace/N5/data/position_candidates.jsonl")
POSITIONS_DB = Path("/home/workspace/N5/data/positions.db")
CHECKPOINT_PATH = BUILD_DIR / "pending_execution_checkpoint.json"
RESULTS_PATH = BUILD_DIR / "pending_execution_results.json"

# Approved merges (10) - using partial IDs for flexible matching
APPROVED_MERGES = [
    ("Vrijen-Attawar-and-Nic-Mahaney_001", "identity-in-the-labor-market-is-semantic-not"),
    ("Vrijen-Attawar-and-Nic-Mahaney_003", "as-generative-ai-commoditizes-highquality-output-t"),
    ("Ilya-sync_001", "ai-implementation-should-elevate-human-experts-hig"),
    ("David-x-Careerspan-Part-2_001", "ai-implementation-should-elevate-human-experts-hig"),
    ("David-x-Careerspan-Part-1_001", "the-recruitment-market-is-structured-around-a-mass"),
    ("David-x-Careerspan-Part-1_002", "in-the-ai-era-the-decision-to-hire"),
    ("Holly-x-V_002", "hiring-signal-collapse"),
    ("Holly-x-V_003", "the-recruitment-market-is-structured-around-a-mass"),
    ("Daily-co-founder-standup_002", "vibe-coding-should-be-positioned-as-a-strategic"),
    ("Shane-Murphy-reuter-X-Vr_001", "the-strategic-value-in-the-labor-market-is"),
]

# Skipped (not approved)
SKIPPED_MERGES = ["cand_20260114_2026-01-12_fxu-mjpr-tum_003"]
SKIPPED_PROMOTIONS = [
    "cand_20260107_2026-01-06_David-x-Vrijen_003",
    "cand_20260108_raw_meeting_test_[M]_002",
    "cand_20260114_2026-01-12_2026-01-12-Shane-Murphy-reuter-X-Vr_002",
]

def load_checkpoint():
    if CHECKPOINT_PATH.exists():
        return json.loads(CHECKPOINT_PATH.read_text())
    return {"completed_merges": [], "completed_promotions": [], "skipped": []}

def save_checkpoint(data):
    CHECKPOINT_PATH.write_text(json.dumps(data, indent=2))

def load_candidates():
    candidates = {}
    for line in CANDIDATES_PATH.read_text().strip().split('\n'):
        c = json.loads(line)
        cid = c.get("id") or c.get("candidate_id")
        if cid:
            candidates[cid] = c
    return candidates

def get_position(position_id_prefix):
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM positions WHERE id LIKE ?", (f"{position_id_prefix}%",))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_position(position_id, new_insight, new_reasoning):
    conn = sqlite3.connect(POSITIONS_DB)
    cur = conn.cursor()
    cur.execute("""
        UPDATE positions 
        SET insight = ?, reasoning = ?, updated_at = ?
        WHERE id LIKE ?
    """, (new_insight, new_reasoning, datetime.now().isoformat(), f"{position_id}%"))
    conn.commit()
    conn.close()

def generate_position_id(title):
    slug = title.lower()
    slug = ''.join(c if c.isalnum() or c == ' ' else '' for c in slug)
    slug = '-'.join(slug.split()[:6])
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"{slug}-{timestamp}-{random_suffix}"

def create_position(candidate):
    conn = sqlite3.connect(POSITIONS_DB)
    cur = conn.cursor()
    
    # Generate title from insight
    insight = candidate.get("insight", "")
    title = insight[:80].rsplit(' ', 1)[0] if len(insight) > 80 else insight
    position_id = generate_position_id(title)
    
    domain = candidate.get("domain", "worldview")
    reasoning = candidate.get("reasoning", "")
    confidence = candidate.get("confidence", 0.7)
    
    cur.execute("""
        INSERT INTO positions (id, domain, title, insight, reasoning, confidence, created_at, updated_at, extraction_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        position_id,
        domain,
        title,
        insight,
        reasoning,
        confidence,
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        "manual_promotion_pending"
    ))
    conn.commit()
    conn.close()
    return position_id

async def llm_merge(session, candidate_insight, existing_insight, existing_reasoning):
    """Use LLM to merge candidate nuance into existing position."""
    prompt = f"""Merge a new candidate insight into an existing position, preserving all nuance from both.

EXISTING POSITION:
Insight: {existing_insight}
Reasoning: {existing_reasoning or 'None'}

NEW CANDIDATE (adds nuance):
{candidate_insight}

Create a merged version that:
1. Preserves the core thesis of the existing position
2. Integrates the new nuance/specificity from the candidate
3. Does NOT lose any detail from either source
4. Reads as a single coherent position

Respond with JSON only:
{{"merged_insight": "...", "merged_reasoning": "..."}}"""

    try:
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            result = await resp.json()
            output = result.get("output", "")
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[^{}]*"merged_insight"[^{}]*\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
    except Exception as e:
        print(f"    LLM error: {e}")
        return None

async def main():
    checkpoint = load_checkpoint()
    candidates = load_candidates()
    
    results = {
        "merges": [],
        "promotions": [],
        "skipped": []
    }
    
    # Mark skipped items first
    for cid in SKIPPED_MERGES + SKIPPED_PROMOTIONS:
        if cid not in checkpoint["skipped"]:
            results["skipped"].append({"candidate": cid, "status": "skipped_by_user"})
            checkpoint["skipped"].append(cid)
            save_checkpoint(checkpoint)
    print(f"Marked {len(SKIPPED_MERGES) + len(SKIPPED_PROMOTIONS)} as skipped")
    
    # Execute merges
    print(f"\n=== EXECUTING MERGES ===")
    print(f"Already completed: {len(checkpoint['completed_merges'])}")
    print(f"Remaining: {len(APPROVED_MERGES) - len(checkpoint['completed_merges'])}")
    
    async with aiohttp.ClientSession() as session:
        for i, (cand_id, target_prefix) in enumerate(APPROVED_MERGES):
            if cand_id in checkpoint["completed_merges"]:
                continue
            
            print(f"\n[{i+1}/{len(APPROVED_MERGES)}] Merging {cand_id[:40]}...")
            
            candidate = candidates.get(cand_id)
            if not candidate:
                # Try partial match
                for k, v in candidates.items():
                    if cand_id in k or k in cand_id:
                        candidate = v
                        break
            
            if not candidate:
                print(f"    SKIP: Candidate not found")
                continue
            
            position = get_position(target_prefix)
            if not position:
                print(f"    SKIP: Target position {target_prefix} not found")
                continue
            
            # LLM merge
            merge_result = await llm_merge(
                session,
                candidate.get("insight", ""),
                position.get("insight", ""),
                position.get("reasoning", "")
            )
            
            if merge_result:
                update_position(
                    target_prefix,
                    merge_result["merged_insight"],
                    merge_result.get("merged_reasoning", "")
                )
                print(f"    ✓ Merged into {position['id'][:40]}")
                results["merges"].append({
                    "candidate": cand_id,
                    "target": position["id"],
                    "status": "merged"
                })
            else:
                print(f"    ✗ Merge failed, using simple append")
                # Fallback: append candidate insight
                combined = f"{position.get('insight', '')}\n\n[Additional nuance]: {candidate.get('insight', '')}"
                update_position(target_prefix, combined, position.get("reasoning", ""))
                results["merges"].append({
                    "candidate": cand_id,
                    "target": position["id"],
                    "status": "merged_fallback"
                })
            
            checkpoint["completed_merges"].append(cand_id)
            save_checkpoint(checkpoint)
    
    # Execute promotions
    print(f"\n=== EXECUTING PROMOTIONS ===")
    
    # Get all pending candidates that are NEW and not skipped
    pending_results = json.loads((BUILD_DIR / "pending_checkpoint.json").read_text())
    new_candidates = [
        r for r in pending_results["completed"]
        if r.get("decision") == "NEW" 
        and r.get("candidate_id") not in SKIPPED_PROMOTIONS
        and r.get("candidate_id") not in checkpoint["completed_promotions"]
    ]
    
    print(f"Promoting {len(new_candidates)} new positions...")
    
    for i, result in enumerate(new_candidates):
        cand_id = result["candidate_id"]
        candidate = candidates.get(cand_id)
        
        if not candidate:
            for k, v in candidates.items():
                if cand_id in k or k in cand_id:
                    candidate = v
                    break
        
        if not candidate:
            print(f"  [{i+1}] SKIP: {cand_id[:30]} not found")
            continue
        
        # Add domain from result if missing
        if not candidate.get("domain"):
            candidate["domain"] = result.get("candidate_domain", "worldview")
        
        position_id = create_position(candidate)
        print(f"  [{i+1}] ✓ Created: {position_id[:50]}")
        
        results["promotions"].append({
            "candidate": cand_id,
            "position_id": position_id,
            "domain": candidate.get("domain"),
            "status": "promoted"
        })
        
        checkpoint["completed_promotions"].append(cand_id)
        save_checkpoint(checkpoint)
    
    # Save final results
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    
    print(f"\n=== EXECUTION COMPLETE ===")
    print(f"  Merges: {len(results['merges'])}")
    print(f"  Promotions: {len(results['promotions'])}")
    print(f"  Skipped: {len(results['skipped'])}")
    print(f"\nResults saved to {RESULTS_PATH}")

if __name__ == "__main__":
    asyncio.run(main())


