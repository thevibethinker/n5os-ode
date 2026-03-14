---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zTfB7kehxEEHmaoC
---

# WORKER ASSIGNMENT: W3b — Position Integration

**Blocked by:** W3 (needs `position_candidates.jsonl`)
**Objective:** Integrate extracted position candidates into V's Positions System, extending existing positions where overlap ≥50%.

## Context from Parent

**Key decision:** If a candidate overlaps ≥50% with an existing position, **extend the existing position** (don't create new or flag for review).

V's existing system has 106 positions across 8 domains.

## Input Files

From W3's conversation workspace:
- `position_candidates.jsonl` — Extracted position candidates

## Positions System

Database: `/home/workspace/N5/data/positions.db`
CLI: `python3 /home/workspace/N5/scripts/positions.py`

### Useful CLI Commands

```bash
# List existing positions in a domain
python3 N5/scripts/positions.py list --domain hiring-market

# Check overlap between candidate and existing positions
python3 N5/scripts/positions.py check-overlap --statement "candidate statement here" --threshold 0.5

# Add new position
python3 N5/scripts/positions.py add --domain X --title "Y" --statement "Z" --reasoning "..." --stakes "..." --conditions "..."

# Extend existing position (add evidence/strengthen)
python3 N5/scripts/positions.py extend --id [position_id] --evidence "New supporting evidence from LinkedIn" --source "linkedin-export-2026-01"
```

## Integration Process

### Step 1: Load Existing Positions

Query database for all 106 existing positions to use as comparison set.

### Step 2: For Each Candidate

1. **Check overlap** with existing positions in same domain
2. **If overlap ≥0.5:**
   - Find the most similar existing position
   - EXTEND it with the LinkedIn evidence
   - Log: "Extended position [id]: [title]"
3. **If overlap <0.5:**
   - This is a genuinely new position
   - ADD it to the database
   - Log: "Added new position: [title]"

### Step 3: Handle Low-Confidence Candidates

For candidates with confidence <0.7:
- Stage for V's review instead of auto-integrating
- Create review file at `N5/review/positions/linkedin_candidates_2026-01-12.md`

## Output Artifacts

1. Database updates (extensions and additions)
2. Review file for low-confidence candidates (if any)
3. Integration log

## Integration Log Format

Create `integration_log.md` in your conversation workspace:

```markdown
# Position Integration Log

## Summary
- Candidates processed: X
- Existing positions extended: Y
- New positions added: Z
- Staged for review: W

## Extensions
| Existing Position | Extended With |
|-------------------|---------------|
| [id] Title | LinkedIn evidence summary |

## New Positions Added
| Domain | Title | Confidence |
|--------|-------|------------|
| ... | ... | ... |

## Staged for Review
| Domain | Title | Confidence | Reason |
|--------|-------|------------|--------|
| ... | ... | 0.65 | Low confidence |
```

## Success Criteria

1. All high-confidence candidates (≥0.7) integrated
2. Overlap check performed for each candidate
3. Extensions add value (not redundant)
4. Low-confidence candidates staged for review
5. Integration log complete

## On Completion

1. Print: "Integrated X positions (Y extensions, Z new)"
2. Print: "W candidates staged for review at [path]"
3. Update STATUS.md: mark W3b as ✅ Complete

