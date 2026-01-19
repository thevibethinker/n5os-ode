#!/usr/bin/env python3
"""
Step 2: Sequential LLM Merge
Processes ambiguous candidates one at a time, updating corpus after each decision.
"""
import json
import sqlite3
import asyncio
import aiohttp
import os
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

QUEUE_PATH = Path('/home/workspace/N5/builds/position-system-overhaul/step2_merge_queue.json')
DB_PATH = Path('/home/workspace/N5/data/positions.db')
OUTPUT_DIR = Path('/home/workspace/N5/builds/position-system-overhaul')
CHECKPOINT_PATH = OUTPUT_DIR / 'step2_checkpoint.json'
RESULTS_PATH = OUTPUT_DIR / 'step2_merge_results.json'

ZO_TOKEN = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')

def normalize(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip().lower())

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def get_top_similar_positions(candidate_insight: str, positions: list, n: int = 5) -> list:
    """Get top N most similar positions by text similarity."""
    scored = []
    for p in positions:
        sim = similarity(candidate_insight, p.get('insight', ''))
        scored.append((p, sim))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:n]

async def ask_llm(session, prompt: str) -> str:
    """Call Zo API."""
    async with session.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": ZO_TOKEN,
            "content-type": "application/json"
        },
        json={"input": prompt}
    ) as resp:
        result = await resp.json()
        return result.get("output", "")

async def process_candidate(session, candidate: dict, positions: list, idx: int, total: int) -> dict:
    """Process a single candidate and return merge decision."""
    cand_id = candidate['candidate_id']
    cand_data = candidate['candidate']
    cand_insight = cand_data.get('insight', '')
    cand_domain = cand_data.get('domain_suggestion', cand_data.get('domain', 'unknown'))
    
    # Get top 5 similar positions
    top_similar = get_top_similar_positions(cand_insight, positions)
    
    # Build context for LLM
    positions_context = ""
    for i, (p, sim) in enumerate(top_similar, 1):
        positions_context += f"""
**Position {i}** (ID: {p['id']}, similarity: {sim:.0%})
- Domain: {p.get('domain', 'unknown')}
- Insight: {p.get('insight', '')[:500]}
- Reasoning: {(p.get('reasoning') or '')[:200]}
"""
    
    prompt = f"""You are helping merge duplicate intellectual positions.

## CANDIDATE (being reviewed)
- ID: {cand_id}
- Domain: {cand_domain}
- Insight: {cand_insight}
- Reasoning: {cand_data.get('reasoning', '')[:300]}
- Stakes: {cand_data.get('stakes', '')[:200]}

## EXISTING POSITIONS (potential matches)
{positions_context}

## YOUR TASK
Determine if this candidate is:
1. **DUPLICATE** - Same core idea as an existing position (even if worded differently)
2. **NEW** - A genuinely distinct intellectual position not captured by any existing position

If DUPLICATE:
- Identify which position it duplicates
- Note any NEW NUANCE the candidate adds that should be merged into the existing position
- New nuance = specific phrasing, examples, implications, or angles not in the original

Respond with JSON only:
{{
  "verdict": "DUPLICATE" or "NEW",
  "matched_position_id": "<position_id>" or null,
  "similarity_score": 0.0-1.0,
  "new_nuance": "<specific new insight to merge>" or null,
  "merge_recommendation": "<how to update the existing position's insight>" or null,
  "reasoning": "<brief explanation>"
}}"""

    print(f"  [{idx}/{total}] Processing {cand_id}...")
    
    try:
        response = await ask_llm(session, prompt)
        # Extract JSON
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            result = json.loads(response[start:end])
            result['candidate_id'] = cand_id
            result['candidate_insight'] = cand_insight[:200]
            return result
        else:
            return {
                'candidate_id': cand_id,
                'verdict': 'ERROR',
                'error': 'Could not parse LLM response',
                'raw_response': response[:500]
            }
    except Exception as e:
        return {
            'candidate_id': cand_id,
            'verdict': 'ERROR',
            'error': str(e)
        }

def save_checkpoint(processed: list, remaining: list):
    """Save progress checkpoint."""
    with open(CHECKPOINT_PATH, 'w') as f:
        json.dump({
            'processed': processed,
            'remaining_count': len(remaining),
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)

async def main():
    # Load queue
    with open(QUEUE_PATH) as f:
        queue = json.load(f)
    
    # Check for existing checkpoint
    processed = []
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            checkpoint = json.load(f)
            processed = checkpoint.get('processed', [])
            processed_ids = {p['candidate_id'] for p in processed}
            queue = [c for c in queue if c['candidate_id'] not in processed_ids]
            print(f"Resuming from checkpoint: {len(processed)} already processed, {len(queue)} remaining")
    
    # Load current positions (will be updated as we go)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    positions = [dict(r) for r in conn.execute("SELECT * FROM positions").fetchall()]
    conn.close()
    
    print(f"Processing {len(queue)} candidates against {len(positions)} positions...")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        for idx, candidate in enumerate(queue, len(processed) + 1):
            result = await process_candidate(session, candidate, positions, idx, len(queue) + len(processed))
            processed.append(result)
            
            # Checkpoint every 5
            if idx % 5 == 0:
                save_checkpoint(processed, queue[idx - len(processed):])
                print(f"  [Checkpoint saved at {idx}]")
    
    # Final save
    with open(RESULTS_PATH, 'w') as f:
        json.dump(processed, f, indent=2)
    
    # Summary
    from collections import Counter
    verdicts = Counter(p.get('verdict') for p in processed)
    
    print("\n" + "="*60)
    print("=== STEP 2 COMPLETE ===")
    for verdict, count in verdicts.most_common():
        print(f"  {verdict}: {count}")
    
    # Count merge opportunities
    with_nuance = [p for p in processed if p.get('verdict') == 'DUPLICATE' and p.get('new_nuance')]
    print(f"\nDuplicates with new nuance to merge: {len(with_nuance)}")
    
    print(f"\nResults saved to {RESULTS_PATH}")
    
    # Generate review doc
    generate_review_doc(processed)

def generate_review_doc(results: list):
    """Generate markdown review document."""
    doc_path = OUTPUT_DIR / 'step2_merge_review.md'
    
    lines = [
        "---",
        "created: " + datetime.now().strftime("%Y-%m-%d"),
        "provenance: con_AVUiANpq2GYAc3Qz",
        "type: merge_review",
        "---",
        "",
        "# Step 2: Merge Review",
        "",
        "## Summary",
        ""
    ]
    
    from collections import Counter
    verdicts = Counter(r.get('verdict') for r in results)
    for v, c in verdicts.most_common():
        lines.append(f"- **{v}**: {c}")
    
    # Duplicates with nuance (need human approval for merge)
    dupes_with_nuance = [r for r in results if r.get('verdict') == 'DUPLICATE' and r.get('new_nuance')]
    if dupes_with_nuance:
        lines.append("")
        lines.append(f"## Duplicates With New Nuance ({len(dupes_with_nuance)})")
        lines.append("*These require a merge to preserve nuance. Review and approve.*")
        lines.append("")
        
        for r in dupes_with_nuance:
            lines.append(f"### {r['candidate_id']}")
            lines.append(f"- **Matches**: `{r.get('matched_position_id')}`")
            lines.append(f"- **Similarity**: {r.get('similarity_score', 0):.0%}")
            lines.append(f"- **New nuance**: {r.get('new_nuance')}")
            lines.append(f"- **Merge recommendation**: {r.get('merge_recommendation')}")
            lines.append(f"- [ ] Approve merge")
            lines.append("")
    
    # Duplicates without nuance (auto-mark)
    dupes_no_nuance = [r for r in results if r.get('verdict') == 'DUPLICATE' and not r.get('new_nuance')]
    if dupes_no_nuance:
        lines.append("")
        lines.append(f"## Duplicates Without New Nuance ({len(dupes_no_nuance)})")
        lines.append("*These can be auto-marked as `already_in_db`.*")
        lines.append("")
        for r in dupes_no_nuance:
            lines.append(f"- `{r['candidate_id']}` → matches `{r.get('matched_position_id')}`")
    
    # New positions
    new_positions = [r for r in results if r.get('verdict') == 'NEW']
    if new_positions:
        lines.append("")
        lines.append(f"## Truly New Positions ({len(new_positions)})")
        lines.append("*These should be promoted to positions.db.*")
        lines.append("")
        for r in new_positions:
            lines.append(f"### {r['candidate_id']}")
            lines.append(f"- **Insight**: {r.get('candidate_insight', '')[:200]}...")
            lines.append(f"- **Reasoning**: {r.get('reasoning')}")
            lines.append(f"- [ ] Approve promotion")
            lines.append("")
    
    # Errors
    errors = [r for r in results if r.get('verdict') == 'ERROR']
    if errors:
        lines.append("")
        lines.append(f"## Errors ({len(errors)})")
        for r in errors:
            lines.append(f"- `{r['candidate_id']}`: {r.get('error')}")
    
    with open(doc_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Review doc saved to {doc_path}")

if __name__ == "__main__":
    asyncio.run(main())

