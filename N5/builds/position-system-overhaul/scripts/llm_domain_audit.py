#!/usr/bin/env python3
"""
LLM-powered domain audit - reviews each position and suggests correct domain.
Groups results by confidence for efficient human review.
"""
import asyncio
import aiohttp
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import os

POSITIONS_DB = Path("/home/workspace/N5/data/positions.db")
CHECKPOINT_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/domain_audit_checkpoint.json")
RESULTS_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/domain_audit_results.json")
REVIEW_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/domain-audit-review.md")

VALID_DOMAINS = [
    "hiring-market",      # Hiring, recruiting, talent acquisition, job market dynamics
    "worldview",          # Epistemology, philosophy, meta-beliefs, general life principles
    "careerspan",         # Careerspan-specific strategy, product, business
    "ai-automation",      # AI, automation, technology trends, tools
    "epistemology",       # How we know what we know, truth, knowledge
    "founder",            # Founder journey, entrepreneurship, startups
    "personal-foundations", # Personal productivity, habits, self-development
    "education",          # Learning, teaching, skill development
    "product-strategy"    # Product thinking, strategy, design
]

SEMAPHORE = asyncio.Semaphore(5)

def load_checkpoint():
    if CHECKPOINT_PATH.exists():
        return json.loads(CHECKPOINT_PATH.read_text())
    return {"completed": []}

def save_checkpoint(data):
    CHECKPOINT_PATH.write_text(json.dumps(data, indent=2))

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
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                result = await resp.json()
                output = result.get("output", "")
                
                # Parse JSON from response
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

def generate_review_doc(results):
    """Generate markdown review document grouped by action needed."""
    changes_needed = [r for r in results if r.get("change_needed") and r.get("status") == "success"]
    confirmed = [r for r in results if not r.get("change_needed") and r.get("status") == "success"]
    errors = [r for r in results if r.get("status") == "error"]
    
    # Group changes by confidence
    high_conf_changes = [r for r in changes_needed if r.get("confidence") == "HIGH"]
    med_conf_changes = [r for r in changes_needed if r.get("confidence") == "MEDIUM"]
    low_conf_changes = [r for r in changes_needed if r.get("confidence") == "LOW"]
    
    doc = f"""---
created: {datetime.now().strftime("%Y-%m-%d")}
provenance: con_AVUiANpq2GYAc3Qz
type: domain_audit_review
---

# Domain Audit Review

## Summary
- **Total positions**: {len(results)}
- **Changes recommended**: {len(changes_needed)}
- **Confirmed correct**: {len(confirmed)}
- **Errors**: {len(errors)}

---

## 1. High-Confidence Changes ({len(high_conf_changes)})
*These are strongly recommended to change.*

"""
    for r in high_conf_changes:
        doc += f"""### [ ] `{r['position_id'][:50]}`
- **Current**: `{r['current_domain']}` → **Suggested**: `{r['correct_domain']}`
- **Reasoning**: {r['reasoning']}

"""
    
    doc += f"""
---

## 2. Medium-Confidence Changes ({len(med_conf_changes)})
*Review these - LLM is moderately confident.*

"""
    for r in med_conf_changes:
        doc += f"""### [ ] `{r['position_id'][:50]}`
- **Current**: `{r['current_domain']}` → **Suggested**: `{r['correct_domain']}`
- **Reasoning**: {r['reasoning']}

"""
    
    doc += f"""
---

## 3. Low-Confidence Changes ({len(low_conf_changes)})
*These are uncertain - use your judgment.*

"""
    for r in low_conf_changes:
        doc += f"""### [ ] `{r['position_id'][:50]}`
- **Current**: `{r['current_domain']}` → **Suggested**: `{r['correct_domain']}`
- **Reasoning**: {r['reasoning']}

"""
    
    doc += f"""
---

## 4. Confirmed Correct ({len(confirmed)})
*LLM agrees with current domain assignment. Collapsed for brevity.*

<details>
<summary>Click to expand ({len(confirmed)} positions)</summary>

"""
    for r in confirmed:
        doc += f"- ✓ `{r['position_id'][:50]}` in `{r['current_domain']}`\n"
    
    doc += """
</details>
"""
    
    if errors:
        doc += f"""
---

## 5. Errors ({len(errors)})

"""
        for r in errors:
            doc += f"- ⚠️ `{r['position_id']}`: {r.get('error', 'Unknown error')}\n"
    
    return doc

async def main():
    # Load all positions
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, domain, title, insight FROM positions ORDER BY domain, id")
    positions = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    print(f"Auditing {len(positions)} positions...")
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    completed_ids = {r["position_id"] for r in checkpoint["completed"]}
    
    remaining = [p for p in positions if p["id"] not in completed_ids]
    print(f"Already completed: {len(checkpoint['completed'])}")
    print(f"Remaining: {len(remaining)}")
    
    if remaining:
        async with aiohttp.ClientSession() as session:
            # Process in concurrent batches
            tasks = [audit_position(session, p) for p in remaining]
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result:
                    checkpoint["completed"].append(result)
                    # Save checkpoint after each completion
                    save_checkpoint(checkpoint)
                    count = len(checkpoint["completed"])
                    if count % 10 == 0:
                        print(f"  Processed {count}/{len(positions)}...")
    
    # Use checkpoint as final results
    results = checkpoint["completed"]
    
    # Save results
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    
    # Generate review doc
    review_doc = generate_review_doc(results)
    REVIEW_PATH.write_text(review_doc)
    
    # Summary
    changes = [r for r in results if r.get("change_needed")]
    print(f"\n=== AUDIT COMPLETE ===")
    print(f"Total: {len(results)}")
    print(f"Changes recommended: {len(changes)}")
    print(f"Review doc: {REVIEW_PATH}")

if __name__ == "__main__":
    asyncio.run(main())




