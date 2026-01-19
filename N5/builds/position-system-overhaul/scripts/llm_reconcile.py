#!/usr/bin/env python3
"""
LLM-powered reconciliation of position candidates against existing positions.
Uses /zo/ask API for semantic matching.
"""
import asyncio
import aiohttp
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime

CANDIDATES_PATH = Path("/home/workspace/N5/data/position_candidates.jsonl")
DB_PATH = Path("/home/workspace/N5/data/positions.db")
OUTPUT_DIR = Path("/home/workspace/N5/builds/position-system-overhaul")

async def match_candidate(session, candidate, existing_positions, semaphore):
    """Use LLM to find semantic matches for a candidate."""
    async with semaphore:
        # Build condensed position list for context
        positions_context = "\n".join([
            f"- ID: {p['id']} | Domain: {p['domain']} | Title: {p['title']}\n  Insight: {p['insight'][:200]}..."
            for p in existing_positions
        ])
        
        candidate_text = f"""
CANDIDATE ID: {candidate.get('id', 'unknown')}
DOMAIN: {candidate.get('domain_suggestion', candidate.get('domain', 'unknown'))}
INSIGHT: {candidate.get('insight', 'NO INSIGHT')}
REASONING: {candidate.get('reasoning', 'N/A')[:300]}
"""
        
        prompt = f"""You are matching a position CANDIDATE against EXISTING positions to find semantic duplicates or near-duplicates.

CANDIDATE TO MATCH:
{candidate_text}

EXISTING POSITIONS (124 total):
{positions_context}

TASK: Determine if this candidate is:
1. EXACT_DUPE - Same core idea, no new nuance (identify which existing position)
2. NEAR_DUPE_MERGE - Very similar but candidate adds nuance worth merging (identify target + what's new)
3. RELATED_BUT_DISTINCT - Connected idea but genuinely different position (identify related positions)
4. TRULY_NEW - No meaningful overlap with existing positions

Respond in this exact JSON format:
{{
  "match_type": "EXACT_DUPE|NEAR_DUPE_MERGE|RELATED_BUT_DISTINCT|TRULY_NEW",
  "matched_position_id": "id or null",
  "related_position_ids": ["id1", "id2"],
  "new_nuance": "description of what candidate adds, or null",
  "confidence": "HIGH|MEDIUM|LOW",
  "reasoning": "brief explanation"
}}"""

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
                output = result.get("output", "")
                
                # Parse JSON from response
                try:
                    # Find JSON in response
                    start = output.find("{")
                    end = output.rfind("}") + 1
                    if start >= 0 and end > start:
                        match_result = json.loads(output[start:end])
                        match_result["candidate_id"] = candidate.get("id")
                        match_result["candidate_insight"] = candidate.get("insight", "")[:150]
                        return match_result
                except json.JSONDecodeError:
                    pass
                
                return {
                    "candidate_id": candidate.get("id"),
                    "match_type": "ERROR",
                    "error": "Could not parse LLM response",
                    "raw_output": output[:500]
                }
        except Exception as e:
            return {
                "candidate_id": candidate.get("id"),
                "match_type": "ERROR", 
                "error": str(e)
            }

def load_candidates():
    """Load approved candidates."""
    candidates = []
    with open(CANDIDATES_PATH) as f:
        for line in f:
            c = json.loads(line)
            if c.get("status") == "approved":
                candidates.append(c)
    return candidates

def load_existing_positions():
    """Load all existing positions from DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, domain, insight FROM positions")
    positions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return positions

def generate_review_doc(results):
    """Generate markdown review document."""
    by_type = {
        "EXACT_DUPE": [],
        "NEAR_DUPE_MERGE": [],
        "RELATED_BUT_DISTINCT": [],
        "TRULY_NEW": [],
        "ERROR": []
    }
    
    for r in results:
        match_type = r.get("match_type", "ERROR")
        if match_type in by_type:
            by_type[match_type].append(r)
        else:
            by_type["ERROR"].append(r)
    
    doc = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
provenance: con_AVUiANpq2GYAc3Qz
type: reconciliation_review
---

# Position Candidate Reconciliation Review

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary

| Category | Count | Action |
|----------|-------|--------|
| Exact Duplicates | {len(by_type['EXACT_DUPE'])} | Mark as `already_in_db` |
| Near Dupes (Merge) | {len(by_type['NEAR_DUPE_MERGE'])} | **Review merge proposals** |
| Related but Distinct | {len(by_type['RELATED_BUT_DISTINCT'])} | Promote + add connections |
| Truly New | {len(by_type['TRULY_NEW'])} | Promote directly |
| Errors | {len(by_type['ERROR'])} | Re-process |

---

## 1. Exact Duplicates ({len(by_type['EXACT_DUPE'])})
*These candidates are semantically identical to existing positions. Recommend marking as `already_in_db`.*

"""
    for r in by_type["EXACT_DUPE"]:
        doc += f"""### {r.get('candidate_id', 'unknown')[:50]}
- **Matched to**: `{r.get('matched_position_id', 'unknown')}`
- **Confidence**: {r.get('confidence', 'unknown')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- [ ] Confirm: Mark as duplicate

"""

    doc += f"""---

## 2. Near Duplicates - Merge Candidates ({len(by_type['NEAR_DUPE_MERGE'])})
*These candidates overlap with existing positions but add nuance worth preserving. Review each merge proposal.*

"""
    for r in by_type["NEAR_DUPE_MERGE"]:
        doc += f"""### {r.get('candidate_id', 'unknown')[:50]}
- **Merge into**: `{r.get('matched_position_id', 'unknown')}`
- **New nuance to add**: {r.get('new_nuance', 'N/A')}
- **Confidence**: {r.get('confidence', 'unknown')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- **Candidate insight**: {r.get('candidate_insight', 'N/A')}
- [ ] Approve merge
- [ ] Reject (promote as separate)
- [ ] Skip

"""

    doc += f"""---

## 3. Related but Distinct ({len(by_type['RELATED_BUT_DISTINCT'])})
*These are genuinely new positions that should be promoted with connections to related existing positions.*

"""
    for r in by_type["RELATED_BUT_DISTINCT"]:
        related = r.get('related_position_ids', [])
        doc += f"""### {r.get('candidate_id', 'unknown')[:50]}
- **Related to**: {', '.join([f'`{rid}`' for rid in related]) if related else 'None identified'}
- **Confidence**: {r.get('confidence', 'unknown')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- [ ] Promote with connections

"""

    doc += f"""---

## 4. Truly New ({len(by_type['TRULY_NEW'])})
*No meaningful overlap with existing positions. Promote directly.*

"""
    for r in by_type["TRULY_NEW"]:
        doc += f"""### {r.get('candidate_id', 'unknown')[:50]}
- **Confidence**: {r.get('confidence', 'unknown')}
- **Reasoning**: {r.get('reasoning', 'N/A')}
- [ ] Promote

"""

    if by_type["ERROR"]:
        doc += f"""---

## 5. Errors ({len(by_type['ERROR'])})
*These need re-processing.*

"""
        for r in by_type["ERROR"]:
            doc += f"""- `{r.get('candidate_id', 'unknown')}`: {r.get('error', 'Unknown error')}
"""

    return doc

async def main():
    print("Loading data...")
    candidates = load_candidates()
    existing = load_existing_positions()
    
    print(f"Matching {len(candidates)} candidates against {len(existing)} positions...")
    print("This will take a few minutes (running in parallel batches)...\n")
    
    # Semaphore to limit concurrency
    semaphore = asyncio.Semaphore(15)
    
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [
            match_candidate(session, c, existing, semaphore)
            for c in candidates
        ]
        
        # Process with progress
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            completed += 1
            if completed % 10 == 0:
                print(f"  Processed {completed}/{len(candidates)}...")
    
    # Save raw results
    results_path = OUTPUT_DIR / "reconciliation_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw results saved to {results_path}")
    
    # Generate review doc
    review_doc = generate_review_doc(results)
    review_path = OUTPUT_DIR / "reconciliation-review.md"
    with open(review_path, "w") as f:
        f.write(review_doc)
    print(f"Review document saved to {review_path}")
    
    # Print summary
    by_type = {}
    for r in results:
        mt = r.get("match_type", "ERROR")
        by_type[mt] = by_type.get(mt, 0) + 1
    
    print("\n=== SUMMARY ===")
    for mt, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {mt}: {count}")

if __name__ == "__main__":
    asyncio.run(main())

