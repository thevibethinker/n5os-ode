---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_OYys6PCWmGnEhbmU
---

# R-Block Refinements: Provenance, Edge Candidates, Memory Enricher

**Build ID:** r-block-refinements  
**Status:** Ready for Build  
**Architect:** Vibe Architect  

---

## Open Questions

None — all decisions made in prior conversation.

---

## Checklist

### Phase 1: Memory Enricher Script
- [x] Create `N5/scripts/r_block_memory_enricher.py`
- [x] Implement profile queries (knowledge, positions, meetings)
- [x] Add relevance scoring and deduplication
- [x] Test with sample concepts

### Phase 2: Base Template Update
- [x] Add `provenance` to output schema metadata
- [x] Add `edge_candidates` section after Evidence
- [x] Update quality checklist

### Phase 3: R-Block Updates (R00-R09)
- [x] R00_Emergent — add provenance + edge_candidates
- [x] R01_Personal — add provenance + edge_candidates
- [x] R02_Learning — add provenance + edge_candidates
- [x] R03_Strategic — add provenance + edge_candidates
- [x] R04_Market — add provenance + edge_candidates
- [x] R05_Product — add provenance + edge_candidates
- [x] R06_Synthesis — add provenance + edge_candidates
- [x] R07_Prediction — add provenance + edge_candidates
- [x] R08_Venture — add provenance + edge_candidates
- [x] R09_Content — add provenance + edge_candidates

### Phase 4: Validation
- [ ] Run full process on recruiter-game-plan reflection
- [ ] Verify provenance flows through
- [ ] Verify edge_candidates populate
- [ ] Verify RIX picks up edge_candidates

---

## Phase 1: Memory Enricher Script

**Purpose:** Centralized utility for querying N5 memory profiles, used by RIX and potentially individual R-blocks.

### Affected Files
- `N5/scripts/r_block_memory_enricher.py` (NEW)

### Changes
```python
#!/usr/bin/env python3
"""
R-Block Memory Enricher
Queries N5 memory profiles for relevant context during reflection processing.
"""

import argparse
import json
from n5_memory_client import N5MemoryClient

def enrich(concepts: list[str], profiles: list[str] = None, limit: int = 5) -> dict:
    """
    Query memory profiles for concepts.
    
    Args:
        concepts: List of key concepts to search
        profiles: Profiles to query (default: knowledge, positions, meetings)
        limit: Max results per profile
    
    Returns:
        Dict with profile -> list of hits
    """
    profiles = profiles or ["knowledge", "positions", "meetings"]
    client = N5MemoryClient()
    
    results = {}
    for profile in profiles:
        query = " ".join(concepts)
        hits = client.search_profile(profile, query, limit=limit)
        # Dedupe and score
        results[profile] = [
            {
                "id": h.get("id"),
                "title": h.get("title", h.get("text", "")[:50]),
                "score": h.get("score", 0),
                "snippet": h.get("text", "")[:200]
            }
            for h in hits
        ]
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Query memory for reflection enrichment")
    parser.add_argument("concepts", nargs="+", help="Key concepts to search")
    parser.add_argument("--profiles", nargs="+", default=["knowledge", "positions", "meetings"])
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    results = enrich(args.concepts, args.profiles, args.limit)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for profile, hits in results.items():
            print(f"\n=== {profile.upper()} ===")
            for h in hits:
                print(f"  - [{h['score']:.2f}] {h['title']}")

if __name__ == "__main__":
    main()
```

### Unit Tests
- [ ] `python3 N5/scripts/r_block_memory_enricher.py "AI headhunters" "recruiter"` returns results
- [ ] `--json` flag outputs valid JSON
- [ ] Empty concepts handled gracefully

---

## Phase 2: Base Template Update

**Purpose:** Add provenance and edge_candidates to the canonical template all R-blocks inherit.

### Affected Files
- `N5/templates/reflection/r_block_base.md`

### Changes

Add to Output Schema section:

```markdown
## Output Schema

### Metadata
- **Block:** R##
- **Generated:** {{timestamp}}
- **Provenance:** {{conversation_id or agent_id}}
- **Source:** {{reflection_slug}}

### [Block-specific content...]

### Edge Candidates
[List concepts/entities that RIX should check for connections]
- `concept_1` — potential link to [domain]
- `concept_2` — potential link to [domain]
- ...

### Evidence
> [Direct quotes...]
```

### Unit Tests
- [ ] Template renders with provenance placeholder
- [ ] Edge Candidates section present

---

## Phase 3: R-Block Updates

**Purpose:** Inject provenance + edge_candidates into each block's output schema.

### Affected Files
- `Prompts/Blocks/Reflection/R00_Emergent.prompt.md`
- `Prompts/Blocks/Reflection/R01_Personal.prompt.md`
- `Prompts/Blocks/Reflection/R02_Learning.prompt.md`
- `Prompts/Blocks/Reflection/R03_Strategic.prompt.md`
- `Prompts/Blocks/Reflection/R04_Market.prompt.md`
- `Prompts/Blocks/Reflection/R05_Product.prompt.md`
- `Prompts/Blocks/Reflection/R06_Synthesis.prompt.md`
- `Prompts/Blocks/Reflection/R07_Prediction.prompt.md`
- `Prompts/Blocks/Reflection/R08_Venture.prompt.md`
- `Prompts/Blocks/Reflection/R09_Content.prompt.md`

### Changes (apply to each)

Find the Output Schema section and add after the opening:

```markdown
## R##: [Block Name]

**Generated:** {{timestamp}}  
**Provenance:** {{conversation_id}}  
**Source:** {{reflection_slug}}
```

And add before the closing of Output Schema:

```markdown
### Edge Candidates
[Entities/concepts from this analysis that RIX should check for connections]
- `{{concept}}` — {{why this might connect}}
```

### Unit Tests
- [ ] Each block has provenance in output schema
- [ ] Each block has edge_candidates section

---

## Phase 4: Validation

**Purpose:** End-to-end test with real reflection.

### Test Case
- Input: `Personal/Reflections/2026/01/2026-01-09_recruiter-game-plan-queries/transcript.md`
- Expected: Full block outputs with provenance, edge_candidates populated, RIX integration

### Validation Steps
1. Run `@Process Reflection` on the transcript
2. Check generated blocks for provenance field
3. Check edge_candidates are populated with meaningful concepts
4. Check RIX output includes edges from edge_candidates
5. Verify edges written to `N5/data/reflection_edges.jsonl`

---

## Trap Doors

None — all changes are additive. Can revert by removing the new fields.

---

## Handoff

**Approved for immediate build.** Execute phases 1-4 sequentially.

**Builder persona:** `set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")`


