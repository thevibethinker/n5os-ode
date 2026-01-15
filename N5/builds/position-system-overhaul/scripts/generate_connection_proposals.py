#!/usr/bin/env python3
"""
Generate connection proposals for orphaned positions using the /zo/ask API.
Processes in batches to manage API costs.
"""
import asyncio
import aiohttp
import json
import os
from pathlib import Path

BUILD_DIR = Path("/home/workspace/N5/builds/position-system-overhaul")

async def propose_connections(session, orphan: dict, targets: list[dict]) -> dict:
    """Ask Zo to propose connections for a single orphan."""
    
    # Build target context (limit to avoid token explosion)
    target_summaries = "\n".join([
        f"- **{t['id']}** ({t['domain']}): {t['title']}"
        for t in targets[:30]  # Cap at 30 targets
    ])
    
    prompt = f"""You are analyzing positions in V's worldview knowledge base.

**Orphan Position to Connect:**
- ID: `{orphan['id']}`
- Title: {orphan['title']}
- Insight: {orphan['insight']}

**Existing Connected Positions (potential targets):**
{target_summaries}

**Task:** Propose 1-3 connections from the orphan to existing positions.

For each proposed connection, provide:
1. `target_id`: The ID of the target position
2. `relationship`: One of: `supports`, `contradicts`, `extends`, `implies`, `prerequisite`, `example_of`
3. `reasoning`: One sentence explaining WHY these ideas connect

Respond in JSON format:
```json
[
  {{"target_id": "...", "relationship": "...", "reasoning": "..."}}
]
```

If no meaningful connections exist, respond with an empty array: `[]`
Be conservative—only propose connections that are genuinely meaningful."""

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
            output = result.get("output", "[]")
            
            # Try to parse JSON from response
            try:
                # Find JSON array in response
                start = output.find("[")
                end = output.rfind("]") + 1
                if start >= 0 and end > start:
                    proposals = json.loads(output[start:end])
                else:
                    proposals = []
            except json.JSONDecodeError:
                proposals = []
            
            return {
                "orphan_id": orphan["id"],
                "orphan_title": orphan["title"],
                "proposals": proposals,
                "raw_response": output[:500]  # For debugging
            }
    except Exception as e:
        return {
            "orphan_id": orphan["id"],
            "orphan_title": orphan["title"],
            "proposals": [],
            "error": str(e)
        }

async def main():
    # Load data
    orphans = json.loads((BUILD_DIR / "careerspan_orphans.json").read_text())
    targets = json.loads((BUILD_DIR / "connected_positions.json").read_text())
    
    # Also add all positions as potential targets (not just connected ones)
    all_positions = json.loads((BUILD_DIR / "positions_export.json").read_text())
    
    print(f"Processing {len(orphans)} careerspan orphans...")
    print(f"Target pool: {len(all_positions)} positions")
    
    results = []
    semaphore = asyncio.Semaphore(5)  # Limit concurrency
    
    async with aiohttp.ClientSession() as session:
        async def process_with_semaphore(orphan):
            async with semaphore:
                return await propose_connections(session, orphan, all_positions)
        
        tasks = [process_with_semaphore(o) for o in orphans]
        results = await asyncio.gather(*tasks)
    
    # Save results
    output_path = BUILD_DIR / "careerspan_connection_proposals.json"
    output_path.write_text(json.dumps(results, indent=2))
    
    # Generate review markdown
    review_lines = [
        "---",
        "created: 2026-01-15",
        "provenance: con_AVUiANpq2GYAc3Qz",
        "type: review_queue",
        "---",
        "",
        "# Careerspan Connection Proposals",
        "",
        "Review each proposed connection. Mark with:",
        "- `[✓]` to approve",
        "- `[✗]` to reject", 
        "- `[?]` if unsure",
        "",
    ]
    
    total_proposals = 0
    for r in results:
        review_lines.append(f"## `{r['orphan_id']}`")
        review_lines.append(f"**{r['orphan_title']}**")
        review_lines.append("")
        
        if r.get("error"):
            review_lines.append(f"⚠️ Error: {r['error']}")
        elif not r["proposals"]:
            review_lines.append("*No connections proposed*")
        else:
            for p in r["proposals"]:
                total_proposals += 1
                review_lines.append(f"- [ ] → `{p.get('target_id', 'unknown')}` ({p.get('relationship', '?')})")
                review_lines.append(f"  - {p.get('reasoning', 'No reasoning provided')}")
        
        review_lines.append("")
    
    review_lines.append("---")
    review_lines.append(f"**Summary:** {len(orphans)} orphans, {total_proposals} proposed connections")
    
    review_path = BUILD_DIR / "careerspan-connections-review.md"
    review_path.write_text("\n".join(review_lines))
    
    print(f"\nResults saved to {output_path}")
    print(f"Review doc saved to {review_path}")
    print(f"Total proposals: {total_proposals}")

if __name__ == "__main__":
    asyncio.run(main())

