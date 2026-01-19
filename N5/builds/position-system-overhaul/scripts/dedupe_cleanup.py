#!/usr/bin/env python3
"""
Option D: LLM-powered semantic dedupe of the 44 positions created today.

For each new position:
1. Find top 3 semantic matches from the 124 older positions
2. Ask LLM: Is this a duplicate? If so, should we merge or delete?
3. Execute the decision with proper tracking

Checkpoints after every position to allow resume.
"""

import json
import sqlite3
import asyncio
import aiohttp
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/home/workspace/N5/data/positions.db")
BUILD_DIR = Path("/home/workspace/N5/builds/position-system-overhaul")
CHECKPOINT_PATH = BUILD_DIR / "dedupe_checkpoint.json"
RESULTS_PATH = BUILD_DIR / "dedupe_results.json"
REVIEW_PATH = BUILD_DIR / "dedupe_review.md"

ZO_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")


def load_positions():
    """Load positions, split into today vs older."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, title, insight, domain, reasoning, created_at, extraction_method
        FROM positions
        WHERE date(created_at) = '2026-01-15'
    """)
    new_positions = [dict(row) for row in cur.fetchall()]
    
    cur.execute("""
        SELECT id, title, insight, domain, reasoning, created_at
        FROM positions
        WHERE date(created_at) < '2026-01-15'
    """)
    old_positions = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    return new_positions, old_positions


def find_top_matches(new_pos, old_positions, top_n=3):
    """Simple text similarity to find candidate matches."""
    new_text = f"{new_pos.get('title', '')} {new_pos.get('insight', '')}".lower()
    
    scores = []
    for old in old_positions:
        old_text = f"{old.get('title', '')} {old.get('insight', '')}".lower()
        
        # Jaccard similarity on words
        new_words = set(new_text.split())
        old_words = set(old_text.split())
        
        if not new_words or not old_words:
            score = 0
        else:
            intersection = len(new_words & old_words)
            union = len(new_words | old_words)
            score = intersection / union if union > 0 else 0
        
        scores.append((old, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scores[:top_n]]


async def ask_llm_dedupe(session, new_pos, candidates):
    """Ask LLM to determine if new position is a duplicate."""
    
    candidates_text = "\n\n".join([
        f"--- EXISTING POSITION {i+1} (id: {c['id']}) ---\n"
        f"Title: {c.get('title', 'N/A')}\n"
        f"Domain: {c.get('domain', 'N/A')}\n"
        f"Insight: {c.get('insight', 'N/A')[:500]}"
        for i, c in enumerate(candidates)
    ])
    
    prompt = f"""You are auditing a position database for duplicates.

A NEW position was created today. Compare it against the EXISTING positions below.

--- NEW POSITION (id: {new_pos['id']}) ---
Title: {new_pos.get('title', 'N/A')}
Domain: {new_pos.get('domain', 'N/A')}
Insight: {new_pos.get('insight', 'N/A')[:500]}

{candidates_text}

TASK: Determine if the NEW position is a duplicate of any EXISTING position.

Consider:
- Same core claim = duplicate (even if worded differently)
- Additional nuance/examples in new = MERGE candidate (keep existing, enrich insight)
- Genuinely different thesis = KEEP as new

Respond with EXACTLY ONE of these JSON formats:

If DUPLICATE (delete new, existing is sufficient):
{{"decision": "DELETE", "reason": "...", "matched_id": "existing-position-id"}}

If MERGE (new has nuance worth preserving):
{{"decision": "MERGE", "reason": "...", "matched_id": "existing-position-id", "merge_addition": "The specific new nuance to append to existing insight"}}

If KEEP (genuinely new position):
{{"decision": "KEEP", "reason": "..."}}

Respond with only the JSON, no other text."""

    try:
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": ZO_TOKEN,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            result = await resp.json()
            output = result.get("output", "")
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[^{}]+\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"decision": "ERROR", "reason": f"Could not parse: {output[:200]}"}
    except Exception as e:
        return {"decision": "ERROR", "reason": str(e)}


def execute_decision(decision, new_pos, old_positions):
    """Execute the LLM's decision in the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    action_taken = None
    
    if decision["decision"] == "DELETE":
        cur.execute("DELETE FROM positions WHERE id = ?", (new_pos["id"],))
        action_taken = f"Deleted {new_pos['id']}"
        
    elif decision["decision"] == "MERGE":
        matched_id = decision.get("matched_id")
        merge_addition = decision.get("merge_addition", "")
        
        if matched_id and merge_addition:
            # Append the new nuance to the existing position's insight
            cur.execute("""
                UPDATE positions 
                SET insight = insight || '\n\n[Merged nuance]: ' || ?,
                    updated_at = ?
                WHERE id = ?
            """, (merge_addition, datetime.now().isoformat(), matched_id))
            
            # Delete the duplicate
            cur.execute("DELETE FROM positions WHERE id = ?", (new_pos["id"],))
            action_taken = f"Merged into {matched_id}, deleted {new_pos['id']}"
        else:
            action_taken = f"MERGE requested but missing data, skipped"
            
    elif decision["decision"] == "KEEP":
        # Mark as legitimately new
        cur.execute("""
            UPDATE positions 
            SET extraction_method = 'dedupe_verified_new'
            WHERE id = ?
        """, (new_pos["id"],))
        action_taken = f"Kept {new_pos['id']} as verified new"
        
    else:
        action_taken = f"ERROR: {decision.get('reason', 'unknown')}"
    
    conn.commit()
    conn.close()
    return action_taken


def load_checkpoint():
    """Load checkpoint if exists."""
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return {"completed": [], "results": []}


def save_checkpoint(checkpoint):
    """Save checkpoint."""
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(checkpoint, f, indent=2)


def generate_review_doc(results):
    """Generate a markdown review document."""
    from collections import Counter
    
    decisions = Counter(r["decision"] for r in results)
    
    content = f"""---
created: 2026-01-15
provenance: con_AVUiANpq2GYAc3Qz
type: dedupe_results
---

# Position Dedupe Results

## Summary

| Decision | Count |
|----------|-------|
| DELETE (pure duplicate) | {decisions.get('DELETE', 0)} |
| MERGE (with nuance) | {decisions.get('MERGE', 0)} |
| KEEP (genuinely new) | {decisions.get('KEEP', 0)} |
| ERROR | {decisions.get('ERROR', 0)} |
| **Total processed** | {len(results)} |

## Details

"""
    
    for r in results:
        decision = r["decision"]
        emoji = {"DELETE": "🗑️", "MERGE": "🔀", "KEEP": "✅", "ERROR": "❌"}.get(decision, "❓")
        content += f"""### {emoji} {r['new_id'][:50]}...

- **Decision**: {decision}
- **Reason**: {r.get('reason', 'N/A')}
- **Action**: {r.get('action_taken', 'N/A')}

"""
    
    with open(REVIEW_PATH, "w") as f:
        f.write(content)
    
    return REVIEW_PATH


async def main():
    print("Loading positions...")
    new_positions, old_positions = load_positions()
    print(f"  New (today): {len(new_positions)}")
    print(f"  Old (baseline): {len(old_positions)}")
    
    checkpoint = load_checkpoint()
    completed_ids = set(checkpoint["completed"])
    results = checkpoint["results"]
    
    remaining = [p for p in new_positions if p["id"] not in completed_ids]
    print(f"  Already processed: {len(completed_ids)}")
    print(f"  Remaining: {len(remaining)}")
    
    if not remaining:
        print("\nAll positions already processed!")
        generate_review_doc(results)
        return
    
    print(f"\nProcessing {len(remaining)} positions...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for i, new_pos in enumerate(remaining):
            print(f"\n[{i+1}/{len(remaining)}] {new_pos['id'][:50]}...")
            
            # Find top matches
            candidates = find_top_matches(new_pos, old_positions)
            
            # Ask LLM
            decision = await ask_llm_dedupe(session, new_pos, candidates)
            print(f"  Decision: {decision['decision']}")
            if decision.get('reason'):
                print(f"  Reason: {decision['reason'][:80]}...")
            
            # Execute
            action_taken = execute_decision(decision, new_pos, old_positions)
            print(f"  Action: {action_taken}")
            
            # Record result
            result = {
                "new_id": new_pos["id"],
                "new_title": new_pos.get("title", "")[:100],
                "decision": decision["decision"],
                "reason": decision.get("reason"),
                "matched_id": decision.get("matched_id"),
                "action_taken": action_taken
            }
            results.append(result)
            
            # Checkpoint
            checkpoint["completed"].append(new_pos["id"])
            checkpoint["results"] = results
            save_checkpoint(checkpoint)
    
    # Final report
    print("\n" + "=" * 50)
    print("DEDUPE COMPLETE")
    
    from collections import Counter
    decisions = Counter(r["decision"] for r in results)
    print(f"\n  DELETE: {decisions.get('DELETE', 0)}")
    print(f"  MERGE: {decisions.get('MERGE', 0)}")
    print(f"  KEEP: {decisions.get('KEEP', 0)}")
    print(f"  ERROR: {decisions.get('ERROR', 0)}")
    
    review_path = generate_review_doc(results)
    print(f"\nReview doc: {review_path}")
    
    # Save final results
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results: {RESULTS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())

