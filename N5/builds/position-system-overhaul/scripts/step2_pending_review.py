#!/usr/bin/env python3
"""
Step 2 for Pending: LLM semantic matching to determine:
- DUPLICATE: Same idea as existing position (mark already_in_db)
- MERGE: Adds nuance to existing position
- NEW: Genuinely new position to promote
- REJECT: Not a real position (observation, external wisdom not worth keeping)
"""
import asyncio
import aiohttp
import json
import os
from pathlib import Path

QUEUE_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/pending_merge_queue.json")
CHECKPOINT_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/pending_checkpoint.json")
REVIEW_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/pending_review.md")

async def analyze_candidate(session, candidate, all_positions):
    """Use LLM to classify this candidate."""
    
    cand_insight = candidate["candidate"].get("insight", "")[:1500]
    cand_domain = candidate["candidate"].get("domain_suggestion", candidate["candidate"].get("domain", "unknown"))
    cand_classification = candidate["candidate"].get("classification", "unknown")
    cand_id = candidate["candidate"].get("id") or candidate["candidate"].get("candidate_id")
    
    # Get top 10 most relevant positions (same domain + source overlap)
    relevant_positions = []
    
    # First add source overlaps
    for p in candidate.get("source_overlap_positions", []):
        relevant_positions.append(p)
    
    # Then add same-domain positions
    for p in all_positions:
        if p["domain"] == cand_domain and p["id"] not in [rp["id"] for rp in relevant_positions]:
            relevant_positions.append(p)
        if len(relevant_positions) >= 10:
            break
    
    positions_context = "\n\n".join([
        f"[{p['id']}] ({p['domain']}): {p.get('insight', '')[:300]}..."
        for p in relevant_positions[:10]
    ])
    
    prompt = f"""Analyze this position candidate against existing positions.

CANDIDATE:
- Classification: {cand_classification}
- Domain: {cand_domain}
- Insight: {cand_insight}

EXISTING POSITIONS (same domain or source):
{positions_context}

TASK: Determine the right action:

1. DUPLICATE - The candidate expresses the SAME core idea as an existing position (even if worded differently). The existing position already captures the essence.

2. MERGE - The candidate adds MEANINGFUL NEW NUANCE to an existing position. Not just different words, but new angles, examples, implications, or conditions that would enrich the existing position.

3. NEW - This is a genuinely distinct position not captured by any existing position. It represents a belief, thesis, or stance that V holds that isn't already in the system.

4. REJECT - This is not actually a position. It might be:
   - An observation without a stance
   - External wisdom V is citing but doesn't personally hold
   - Too vague or generic to be actionable
   - A hypothesis that's too speculative

Respond with ONLY a JSON object (no markdown, no explanation outside the JSON):
{{"decision": "DUPLICATE|MERGE|NEW|REJECT", "target_position_id": "id if DUPLICATE or MERGE, null otherwise", "confidence": "HIGH|MEDIUM|LOW", "reasoning": "One sentence explaining the decision"}}"""

    try:
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            result = await resp.json()
            raw_output = result.get("output", "")
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', raw_output, re.DOTALL)
            if json_match:
                try:
                    output = json.loads(json_match.group())
                    return {
                        "candidate_id": cand_id,
                        "decision": output.get("decision", "ERROR"),
                        "target_position_id": output.get("target_position_id"),
                        "confidence": output.get("confidence", "LOW"),
                        "reasoning": output.get("reasoning", "No reasoning"),
                        "candidate_insight": cand_insight[:200],
                        "candidate_domain": cand_domain,
                        "candidate_classification": cand_classification
                    }
                except json.JSONDecodeError:
                    pass
            
            # If we get here, couldn't parse
            return {
                "candidate_id": cand_id,
                "decision": "ERROR",
                "error": f"Could not parse response: {raw_output[:200]}",
                "candidate_insight": cand_insight[:200],
                "candidate_domain": cand_domain,
                "candidate_classification": cand_classification
            }
    except Exception as e:
        return {
            "candidate_id": cand_id,
            "decision": "ERROR",
            "error": str(e),
            "candidate_insight": cand_insight[:200],
            "candidate_domain": cand_domain,
            "candidate_classification": cand_classification
        }

async def main():
    import sqlite3
    
    # Load queue
    queue = json.loads(QUEUE_PATH.read_text())
    
    # Load all positions
    conn = sqlite3.connect("/home/workspace/N5/data/positions.db")
    conn.row_factory = sqlite3.Row
    all_positions = [dict(r) for r in conn.execute("SELECT * FROM positions").fetchall()]
    
    # Load checkpoint
    completed = []
    if CHECKPOINT_PATH.exists():
        completed = json.loads(CHECKPOINT_PATH.read_text()).get("completed", [])
    
    completed_ids = {c["candidate_id"] for c in completed}
    remaining = [q for q in queue if (q["candidate"].get("id") or q["candidate"].get("candidate_id")) not in completed_ids]
    
    print(f"Processing {len(queue)} pending candidates...")
    print(f"Already completed: {len(completed)}")
    print(f"Remaining: {len(remaining)}")
    
    async with aiohttp.ClientSession() as session:
        for i, item in enumerate(remaining):
            cand_id = item["candidate"].get("id") or item["candidate"].get("candidate_id")
            print(f"\n[{len(completed)+1}/{len(queue)}] {cand_id[:50]}...")
            
            result = await analyze_candidate(session, item, all_positions)
            completed.append(result)
            
            print(f"  → {result['decision']} ({result.get('confidence', 'N/A')})")
            if result.get("target_position_id"):
                print(f"     Target: {result['target_position_id']}")
            
            # Checkpoint every 5
            if len(completed) % 5 == 0:
                CHECKPOINT_PATH.write_text(json.dumps({"completed": completed}, indent=2))
                print(f"  [Checkpoint saved]")
    
    # Final save
    CHECKPOINT_PATH.write_text(json.dumps({"completed": completed}, indent=2))
    
    # Generate review document
    by_decision = {"DUPLICATE": [], "MERGE": [], "NEW": [], "REJECT": [], "ERROR": []}
    for r in completed:
        by_decision[r.get("decision", "ERROR")].append(r)
    
    md = f"""---
created: 2026-01-15
provenance: con_AVUiANpq2GYAc3Qz
type: pending_review
---

# Pending Candidates Review

## Summary

| Decision | Count |
|----------|-------|
| DUPLICATE | {len(by_decision['DUPLICATE'])} |
| MERGE | {len(by_decision['MERGE'])} |
| NEW | {len(by_decision['NEW'])} |
| REJECT | {len(by_decision['REJECT'])} |
| ERROR | {len(by_decision['ERROR'])} |

---

## 1. Duplicates ({len(by_decision['DUPLICATE'])})
*Already captured by existing positions — recommend marking `already_in_db`*

"""
    for r in by_decision["DUPLICATE"]:
        md += f"""### {r['candidate_id'][:60]}
- **Target**: `{r.get('target_position_id', 'unknown')}`
- **Confidence**: {r.get('confidence', 'N/A')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- **Insight preview**: {r.get('candidate_insight', '')[:150]}...
- [ ] Confirm duplicate

"""

    md += f"""---

## 2. Merge Candidates ({len(by_decision['MERGE'])})
*Add nuance to existing positions*

"""
    for r in by_decision["MERGE"]:
        md += f"""### {r['candidate_id'][:60]}
- **Merge into**: `{r.get('target_position_id', 'unknown')}`
- **Confidence**: {r.get('confidence', 'N/A')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- **Insight preview**: {r.get('candidate_insight', '')[:150]}...
- [ ] Approve merge

"""

    md += f"""---

## 3. New Positions ({len(by_decision['NEW'])})
*Genuinely new — recommend promotion to positions.db*

"""
    for r in by_decision["NEW"]:
        md += f"""### {r['candidate_id'][:60]}
- **Domain**: {r.get('candidate_domain', 'unknown')}
- **Classification**: {r.get('candidate_classification', 'unknown')}
- **Confidence**: {r.get('confidence', 'N/A')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- **Insight preview**: {r.get('candidate_insight', '')[:150]}...
- [ ] Approve promotion

"""

    md += f"""---

## 4. Reject ({len(by_decision['REJECT'])})
*Not real positions — recommend rejection*

"""
    for r in by_decision["REJECT"]:
        md += f"""### {r['candidate_id'][:60]}
- **Confidence**: {r.get('confidence', 'N/A')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- **Insight preview**: {r.get('candidate_insight', '')[:150]}...
- [ ] Confirm rejection

"""

    REVIEW_PATH.write_text(md)
    
    print(f"\n=== COMPLETE ===")
    print(f"DUPLICATE: {len(by_decision['DUPLICATE'])}")
    print(f"MERGE: {len(by_decision['MERGE'])}")
    print(f"NEW: {len(by_decision['NEW'])}")
    print(f"REJECT: {len(by_decision['REJECT'])}")
    print(f"\nReview doc: {REVIEW_PATH}")

if __name__ == "__main__":
    asyncio.run(main())



