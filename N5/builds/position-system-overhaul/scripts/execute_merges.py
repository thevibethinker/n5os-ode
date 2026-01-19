#!/usr/bin/env python3
"""
Execute approved merges and promotions.
- 18 merges: LLM generates merged insight, updates positions.db
- 2 rejections: Mark in candidates file
- 1 promotion: Add new position to positions.db
"""
import asyncio
import aiohttp
import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/home/workspace/N5/data/positions.db")
CANDIDATES_PATH = Path("/home/workspace/N5/data/position_candidates.jsonl")
BUILD_DIR = Path("/home/workspace/N5/builds/position-system-overhaul")
CHECKPOINT_PATH = BUILD_DIR / "merge_checkpoint.json"
RESULTS_PATH = BUILD_DIR / "merge_execution_results.json"

# V's decisions
APPROVED_MERGES = [
    ("cand_20251228_2025-12-23_rochelmycareerspancom_002", "market-fundability-and-professional-acceptability-"),
    ("cand_20251228_2025-12-26_Zo-demo-planning-brainstorm_002", "a-truly-effective-productivity-tool-functions-as-a-2025-12-26"),
    ("cand_20251228_20251226_Careerspan_Demo_001", "ais-primary-value-is-in-shifting-human-experts"),
    ("cand_20251228_20251226_Careerspan_Demo_002", "professional-identity-is-semantic-rather-than-synt-20251226_C"),
    ("cand_20251228_20251226_Careerspan_Demo_003", "reducing-latency-in-trust-networks-transforms-inst-20251226_C"),
    ("cand_20251228_2025-12-23_rochelmycareerspancom_001", "the-efficacy-of-automated-habit-tracking-systems-i"),
    ("cand_20251228_2025-12-22_Jatin-Sandilya-x-Vrijen-Attawar_003", "the-internet-of-careers-functions-as-a-collective"),
    ("cand_20251228_2025-12-23_2025-12-23-Melhrubingmailcom_001", "in-a-career-pivot-a-candidates-primary-objective"),
    ("cand_20251228_2025-12-23_2025-12-23-Melhrubingmailcom_002", "a-sustainable-job-search-requires-a-dietary-balanc"),
    ("cand_20251228_2025-12-23_2025-12-23-Davisteamworkonlinecom_002", "there-is-a-strategic-advantage-in-decoupling-human"),
    ("cand_20251228_2025-12-22_Vrijen-&-Rochel---Job-Applying-Powwow_001", "internal-self-assessment-systematically-lags-exter"),
    ("cand_20251228_2025-12-22_2025-12-22-Swd-Cvsh-Vys_001", "the-recruitment-market-is-systematically-inefficie"),
    ("cand_20251228_2025-12-22_Christine-Song-Ribbon-Partnership-Sync_001", "the-traditional-resume-is-a-failed-data-structure-2025-12-22"),
    ("cand_20251228_2025-12-22_2025-12-22-Swd-Cvsh-Vys_001_b", "the-traditional-resume-is-a-failed-data-structure-2025-12-22"),  # GPS analogy
    ("cand_20251229_20251226_Careerspan_Demo_no_transcript_003", "reducing-latency-in-trust-networks-transforms-inst-20251226_C"),
    ("cand_20260103_2025-12-23_Kristen-Habacht-Elly-AI-x-Vrijen-Attawar_001", "data-collected-independent-of-a-specific-job-appli"),
    ("cand_20260103_2025-12-23_Kristen-Habacht-Elly-AI-x-Vrijen-Attawar_002", "hiring-should-be-treated-as-an-optimization-for-bu"),
    ("cand_20260103_2025-12-23_Kristen-Habacht-Elly-AI-x-Vrijen-Attawar_003", "linkedin-s-shift-in-focus-from-a-professional-util"),
]

REJECTED = [
    "cand_20251228_2025-12-26_Careerspan-demo_001",  # Duplicate of #3
    "cand_20251228_2025-12-26_Careerspan-demo_003",  # "BS-ey/muddled"
]

NEW_POSITION = "cand_20251228_2025-12-23_Kristen-Habacht-Elly-AI-x-Vrijen-Attawar_003"

def load_candidates():
    candidates = {}
    with open(CANDIDATES_PATH) as f:
        for line in f:
            c = json.loads(line)
            candidates[c.get('id', c.get('candidate_id', ''))] = c
    return candidates

def load_position(position_id_prefix):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM positions WHERE id LIKE ?", (f"{position_id_prefix}%",))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_position(position_id, new_insight, new_reasoning):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE positions 
        SET insight = ?, reasoning = ?, updated_at = ?
        WHERE id LIKE ?
    """, (new_insight, new_reasoning, datetime.now().isoformat(), f"{position_id}%"))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected

async def generate_merge(session, candidate, existing_position):
    """Use /zo/ask to generate merged insight and reasoning."""
    prompt = f"""You are merging a new nuance into an existing position. Preserve ALL existing content while integrating the new nuance seamlessly.

EXISTING POSITION:
Title: {existing_position.get('title', 'Unknown')}
Insight: {existing_position.get('insight', '')}
Reasoning: {existing_position.get('reasoning', '')}

NEW NUANCE TO INTEGRATE:
{candidate.get('insight', '')}

TASK:
1. Write an UPDATED INSIGHT that incorporates the new nuance naturally. Do not lose any existing content.
2. Write UPDATED REASONING that includes the new framing/terminology/examples.

Respond in this exact JSON format:
{{"merged_insight": "...", "merged_reasoning": "..."}}
"""
    
    try:
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={
                "input": prompt,
                "output_format": {
                    "type": "object",
                    "properties": {
                        "merged_insight": {"type": "string"},
                        "merged_reasoning": {"type": "string"}
                    },
                    "required": ["merged_insight", "merged_reasoning"]
                }
            }
        ) as resp:
            result = await resp.json()
            return result.get("output", {})
    except Exception as e:
        return {"error": str(e)}

def save_checkpoint(completed, results):
    with open(CHECKPOINT_PATH, 'w') as f:
        json.dump({"completed": completed, "results": results}, f, indent=2)

def load_checkpoint():
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return {"completed": [], "results": []}

async def main():
    candidates = load_candidates()
    checkpoint = load_checkpoint()
    completed = set(checkpoint.get("completed", []))
    results = checkpoint.get("results", [])
    
    print(f"=== EXECUTING MERGES ===")
    print(f"Already completed: {len(completed)}")
    print(f"Remaining: {len(APPROVED_MERGES) - len(completed)}")
    print()
    
    async with aiohttp.ClientSession() as session:
        for i, (cand_id, pos_id_prefix) in enumerate(APPROVED_MERGES):
            if cand_id in completed:
                continue
                
            print(f"[{i+1}/{len(APPROVED_MERGES)}] Merging {cand_id[:40]}...")
            
            # Handle the duplicate entry for GPS analogy
            actual_cand_id = cand_id.replace("_b", "")
            candidate = candidates.get(actual_cand_id, {})
            position = load_position(pos_id_prefix)
            
            if not position:
                print(f"  ⚠️ Position not found: {pos_id_prefix}")
                results.append({"candidate": cand_id, "status": "error", "reason": "position_not_found"})
                completed.add(cand_id)
                continue
            
            if not candidate:
                print(f"  ⚠️ Candidate not found: {actual_cand_id}")
                results.append({"candidate": cand_id, "status": "error", "reason": "candidate_not_found"})
                completed.add(cand_id)
                continue
            
            merged = await generate_merge(session, candidate, position)
            
            if "error" in merged:
                print(f"  ❌ Error: {merged['error']}")
                results.append({"candidate": cand_id, "status": "error", "reason": merged["error"]})
            else:
                # Update the position in the database
                affected = update_position(
                    pos_id_prefix,
                    merged.get("merged_insight", position.get("insight")),
                    merged.get("merged_reasoning", position.get("reasoning"))
                )
                print(f"  ✓ Merged into {position.get('id', pos_id_prefix)} ({affected} rows updated)")
                results.append({
                    "candidate": cand_id,
                    "position": position.get("id"),
                    "status": "merged",
                    "new_insight_preview": merged.get("merged_insight", "")[:100] + "..."
                })
            
            completed.add(cand_id)
            save_checkpoint(list(completed), results)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
    
    # Handle rejections
    print("\n=== MARKING REJECTIONS ===")
    for cand_id in REJECTED:
        print(f"  Rejecting: {cand_id}")
        results.append({"candidate": cand_id, "status": "rejected", "reason": "v_decision"})
    
    # Handle new position promotion
    print("\n=== PROMOTING NEW POSITION ===")
    new_cand = candidates.get(NEW_POSITION, {})
    if new_cand:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Generate a proper ID
        new_id = f"linkedin-utility-gap-strategic-suicide-{datetime.now().strftime('%Y%m%d')}"
        
        cur.execute("""
            INSERT INTO positions (id, domain, title, insight, reasoning, confidence, stability, created_at, updated_at, extraction_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_id,
            new_cand.get("domain_suggestion", "worldview"),
            "LinkedIn's Strategic Suicide Creates a Utility Gap",
            new_cand.get("insight", ""),
            new_cand.get("reasoning", ""),
            3,
            "emerging",
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            "manual_promotion"
        ))
        conn.commit()
        conn.close()
        print(f"  ✓ Promoted: {new_id}")
        results.append({"candidate": NEW_POSITION, "status": "promoted", "new_position_id": new_id})
    else:
        print(f"  ⚠️ New position candidate not found")
        results.append({"candidate": NEW_POSITION, "status": "error", "reason": "not_found"})
    
    # Save final results
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print("\n" + "="*60)
    print("=== EXECUTION COMPLETE ===")
    merged_count = sum(1 for r in results if r.get("status") == "merged")
    error_count = sum(1 for r in results if r.get("status") == "error")
    rejected_count = sum(1 for r in results if r.get("status") == "rejected")
    promoted_count = sum(1 for r in results if r.get("status") == "promoted")
    
    print(f"  Merged: {merged_count}")
    print(f"  Promoted: {promoted_count}")
    print(f"  Rejected: {rejected_count}")
    print(f"  Errors: {error_count}")
    print(f"\nResults saved to {RESULTS_PATH}")

if __name__ == "__main__":
    asyncio.run(main())


