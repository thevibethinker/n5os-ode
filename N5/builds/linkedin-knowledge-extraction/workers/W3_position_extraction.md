---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zTfB7kehxEEHmaoC
---

# WORKER ASSIGNMENT: W3 — Position Extraction

**Blocked by:** W0 (needs `posts.jsonl`, `articles.jsonl`)
**Objective:** Extract worldview position candidates from V's LinkedIn corpus for the Positions System.

## Context from Parent

V has an existing Positions System with 106 positions across 8 domains:
- ai-automation
- careerspan
- education
- epistemology
- founder
- hiring-market
- personal-foundations
- worldview

New positions from LinkedIn should be checked against existing ones. If overlap ≥50%, **extend the existing position** rather than creating a new one.

## What Is a Position?

A position is a **belief V holds about how the world works** — not just an opinion, but a stake in the ground with reasoning and conditions.

Example position:
```yaml
domain: hiring-market
title: ATS systems create false negatives at scale
statement: Applicant tracking systems reject qualified candidates through keyword matching, creating a market failure where good talent can't reach hiring managers.
reasoning: Keyword-based filtering optimizes for false positive reduction (not hiring bad candidates) at the cost of massive false negatives (rejecting good ones).
stakes: High — affects millions of job seekers and causes companies to miss talent.
conditions: Applies to high-volume hiring; less relevant for executive search or small companies.
```

## Input Files

From W0's conversation workspace:
- `posts.jsonl` — Primary source (V's stated beliefs)
- `articles.jsonl` — Secondary source (longer-form arguments)

Note: Comments are useful for psychographic analysis but less useful for position extraction (reactive rather than declarative).

## Extraction Process

### Step 1: Identify Position-Bearing Content

Scan for posts/articles that contain:
- Declarative beliefs ("X is true," "Y doesn't work")
- Causal claims ("X causes Y," "Because of X, we see Y")
- Prescriptive statements ("You should X," "Companies need to Y")
- Critique with reasoning ("X is broken because...")
- Contrarian takes ("Everyone thinks X, but actually Y")

### Step 2: Extract Candidate Positions

For each position-bearing piece of content, extract:

```json
{
  "source_id": "post_042",
  "source_date": "2025-07-15",
  "domain": "hiring-market",
  "title": "Short title for position",
  "statement": "The core belief in 1-2 sentences",
  "reasoning": "Why V believes this",
  "stakes": "Why it matters",
  "conditions": "When/where this applies (or 'universal')",
  "original_excerpt": "The specific text that expressed this position",
  "confidence": 0.85
}
```

**Confidence scoring:**
- 0.9+ : Explicitly stated, clearly argued
- 0.7-0.9: Strongly implied, consistent with other content
- 0.5-0.7: Inferred, would benefit from V's confirmation

### Step 3: Deduplicate Within Extraction

If multiple posts express the same position, merge them:
- Keep the strongest articulation
- Note all source_ids
- Boost confidence if position appears multiple times

## Output Artifact

Create `position_candidates.jsonl` in your conversation workspace:

```json
{
  "candidate_id": "pc_001",
  "source_ids": ["post_042", "post_089"],
  "domain": "hiring-market",
  "title": "ATS systems create false negatives at scale",
  "statement": "...",
  "reasoning": "...",
  "stakes": "...",
  "conditions": "...",
  "original_excerpt": "...",
  "confidence": 0.9,
  "extraction_method": "linkedin-corpus-2026-01"
}
```

## Output Summary

Also create `extraction_summary.md`:

```markdown
# Position Extraction Summary

## Stats
- Posts analyzed: X
- Articles analyzed: Y
- Position candidates extracted: Z
- By confidence tier:
  - High (0.9+): N
  - Medium (0.7-0.9): M
  - Lower (0.5-0.7): L

## Domain Distribution
- hiring-market: X candidates
- ai-automation: Y candidates
- ...

## Sample Candidates (Top 5 by Confidence)
1. [domain] **Title** — confidence X.XX
2. ...
```

## Success Criteria

1. Position candidates follow the schema exactly
2. Each candidate has reasoning + stakes + conditions
3. Duplicates merged (no repeated positions)
4. Confidence scores justified
5. Output files created in conversation workspace

## On Completion

1. Print paths to both output files
2. Print: "Extracted X position candidates across Y domains"
3. Update STATUS.md: mark W3 as ✅ Complete
4. Declare: "W3 complete. W3b (Position Integration) is now unblocked."

## Reference

Existing positions system: `file 'N5/capabilities/internal/positions-system.md'`
Positions CLI: `python3 N5/scripts/positions.py --help`

