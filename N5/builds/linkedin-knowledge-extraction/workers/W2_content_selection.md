---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zTfB7kehxEEHmaoC
---

# WORKER ASSIGNMENT: W2 — Top Posts Selection

**Blocked by:** W0 (needs `posts.jsonl`)
**Objective:** Identify V's best LinkedIn posts for Content Library ingestion based on **originality** and **evergreen** criteria.

## Context from Parent

V's criteria for "top tier" posts:
1. **Originality** — Not a reshare; V's own thinking
2. **Evergreen** — Still relevant; not tied to a specific moment that has passed

Explicitly NOT filtering on: length/substance, shareability metrics

## Input Files

From W0's conversation workspace:
- `posts.jsonl` — 130 posts (includes `is_reshare` flag)

## Selection Process

### Step 1: Filter Out Reshares
Remove any post where `is_reshare == true`

### Step 2: Score Remaining Posts

For each original post, score on two dimensions (1-5 scale):

**Originality Score:**
- 5: Novel insight, unique framing, original thinking
- 4: Fresh take on known topic
- 3: Solid but conventional perspective
- 2: Common opinion, nothing new
- 1: Generic/boilerplate

**Evergreen Score:**
- 5: Timeless principle, always relevant
- 4: Long shelf life (years)
- 3: Relevant for ~1 year
- 2: Tied to recent context but not dead
- 1: Dated/stale, moment has passed

**Combined Score:** `(originality * 0.6) + (evergreen * 0.4)`

### Step 3: Rank and Select

- Rank by combined score descending
- Select top 25 posts (or top 20% if fewer qualify)
- Flag any "honorable mentions" (score 3.5-4.0) for potential inclusion

## Output Artifact

Create `top_posts_candidates.jsonl` in your conversation workspace:

```json
{
  "id": "post_042",
  "date": "2025-07-15",
  "text": "Full post text...",
  "originality_score": 5,
  "originality_rationale": "Novel framework for...",
  "evergreen_score": 4,
  "evergreen_rationale": "Principle applies regardless of...",
  "combined_score": 4.6,
  "recommendation": "INCLUDE",
  "suggested_tags": ["career-strategy", "job-search"]
}
```

`recommendation` values:
- `INCLUDE` — Top tier, ingest to Content Library
- `MAYBE` — Honorable mention, V should review
- `SKIP` — Doesn't meet criteria (don't include in output)

## Output Summary

Also create `selection_summary.md`:

```markdown
# Top Posts Selection Summary

## Stats
- Total posts analyzed: X
- Reshares filtered out: Y
- Original posts scored: Z
- INCLUDE recommendations: N
- MAYBE recommendations: M

## Top 10 Posts (Preview)
1. [date] — [first 50 chars]... (score: X.X)
2. ...

## Domain Distribution of Top Posts
- Career coaching: X posts
- Hiring critique: Y posts
- ...
```

## Success Criteria

1. All original posts scored on both dimensions
2. Rationale provided for each score
3. Top 25 (or 20%) selected with INCLUDE
4. No reshares in final selection
5. Output files created in conversation workspace

## On Completion

1. Print paths to both output files
2. Print: "Selected X posts for Content Library (Y honorable mentions)"
3. Update STATUS.md: mark W2 as ✅ Complete
4. Declare: "W2 complete. W2b (Content Ingestion) is now unblocked."

