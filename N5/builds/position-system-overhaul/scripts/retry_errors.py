#!/usr/bin/env python3
"""
Retry failed domain audit positions.
"""
import asyncio
import aiohttp
import json
import sqlite3
from pathlib import Path
import os

POSITIONS_DB = Path("/home/workspace/N5/data/positions.db")
CHECKPOINT_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/domain_audit_checkpoint.json")

VALID_DOMAINS = [
    "hiring-market", "worldview", "careerspan", "ai-automation",
    "epistemology", "founder", "personal-foundations", "education", "product-strategy"
]

SEMAPHORE = asyncio.Semaphore(3)  # Lower concurrency for retries

async def audit_position(session, position):
    """Ask LLM to verify/suggest domain for a position."""
    async with SEMAPHORE:
        prompt = f"""You are auditing domain assignments for a position system.

VALID DOMAINS:
- hiring-market: Hiring, recruiting, talent acquisition, job market dynamics, employer-candidate relationships
- worldview: Meta-beliefs, philosophy of life, general principles that span multiple domains
- careerspan: Careerspan company-specific strategy, product decisions, business model
- ai-automation: AI technology, automation tools, LLMs, technology trends
- epistemology: How we know things, truth-seeking, knowledge systems, cognitive biases
- founder: Entrepreneurship, startup journey, founder psychology, company building
- personal-foundations: Personal habits, productivity, self-development, lifestyle
- education: Learning, teaching, skill acquisition, training
- product-strategy: Product thinking, design decisions, feature prioritization

POSITION TO AUDIT:
- Current Domain: {position['domain']}
- ID: {position['id']}
- Insight: {position['insight']}

TASK: Determine if this position is in the correct domain.

Respond with JSON only:
{{"correct_domain": "<domain-name>", "confidence": "HIGH|MEDIUM|LOW", "reasoning": "<brief explanation>", "change_needed": true|false}}
"""
    
        try:
            async with session.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                    "content-type": "application/json"
                },
                json={"input": prompt},
                timeout=aiohttp.ClientTimeout(total=90)  # Longer timeout
            ) as resp:
                result = await resp.json()
                output = result.get("output", "")
                
                import re
                json_match = re.search(r'\{[^{}]+\}', output, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return {
                        "position_id": position['id'],
                        "current_domain": position['domain'],
                        "correct_domain": parsed.get("correct_domain", position['domain']),
                        "confidence": parsed.get("confidence", "LOW"),
                        "reasoning": parsed.get("reasoning", ""),
                        "change_needed": parsed.get("change_needed", False),
                        "status": "success"
                    }
        except Exception as e:
            return {
                "position_id": position['id'],
                "current_domain": position['domain'],
                "status": "error",
                "error": str(e)
            }
    
        return {
            "position_id": position['id'],
            "current_domain": position['domain'],
            "status": "error",
            "error": "Could not parse response"
        }

async def main():
    # Load checkpoint
    checkpoint = json.loads(CHECKPOINT_PATH.read_text())
    completed = checkpoint.get("completed", [])
    
    # Find errors
    errors = [r for r in completed if r.get("status") == "error"]
    error_ids = {e["position_id"] for e in errors}
    
    print(f"Found {len(errors)} errors to retry")
    
    if not errors:
        print("No errors to retry!")
        return
    
    # Load position data for errors
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    placeholders = ",".join("?" * len(error_ids))
    cur.execute(f"SELECT id, domain, title, insight FROM positions WHERE id IN ({placeholders})", list(error_ids))
    positions = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    print(f"Loaded {len(positions)} positions to retry")
    
    # Retry
    async with aiohttp.ClientSession() as session:
        tasks = [audit_position(session, p) for p in positions]
        new_results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            new_results.append(result)
            print(f"  Retried {i+1}/{len(positions)}: {result['position_id'][:40]}... → {result['status']}")
    
    # Update checkpoint - replace errors with new results
    success_count = sum(1 for r in new_results if r["status"] == "success")
    still_error = sum(1 for r in new_results if r["status"] == "error")
    
    # Remove old errors, add new results
    updated = [r for r in completed if r["position_id"] not in error_ids]
    updated.extend(new_results)
    
    checkpoint["completed"] = updated
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, indent=2))
    
    print(f"\n=== RETRY COMPLETE ===")
    print(f"Success: {success_count}")
    print(f"Still errored: {still_error}")

if __name__ == "__main__":
    asyncio.run(main())

