---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_jmgVLfK7jKZO9X1i
---

# WORKER ASSIGNMENT: Position Insight Enrichment

**Assigned to:** Zo (Builder Mode)
**Objective:** Enrich position insights with better formatting and Content Library references.

## Context

The Mind Map at https://vrijenattawar-va.zocomputer.io/mind displays V's intellectual positions. Currently, the insight text for each position is a wall of text without formatting or references to related content V has written/read.

## Problem

See `file '/home/.z/chat-images/image (338).png'` — The insight panel shows unformatted text. We need:
1. Properly formatted paragraphs (the text is already sentence-structured, just needs visual breaks)
2. References to Content Library articles that relate to this position

## Files

- `file 'N5/data/positions.db'` — SQLite database with positions table
- `file 'Knowledge/content-library/'` — Content Library with articles V has saved
- `file 'Sites/vrijenattawar-staging/src/pages/MindMap.tsx'` — UI that displays insights

## Schema

Current positions table has:
```sql
id TEXT PRIMARY KEY,
domain TEXT,
title TEXT,
insight TEXT,  -- Current unformatted text
stability TEXT,
confidence INTEGER,
connections TEXT,  -- JSON array
formed_date TEXT
```

## Task

### Step 1: Add schema for enriched content

Add new columns to positions table:
```sql
ALTER TABLE positions ADD COLUMN formatted_insight TEXT;
ALTER TABLE positions ADD COLUMN references TEXT;  -- JSON array of {title, path, relevance}
```

### Step 2: Create enrichment script

Create `file 'N5/scripts/enrich_position_insights.py'` that:
1. Reads each position's insight text
2. Formats it into proper paragraphs (split on sentence boundaries, group 2-3 sentences per paragraph)
3. Searches Content Library for relevant articles using semantic similarity
4. Stores formatted_insight and references JSON

### Step 3: Run enrichment

Run the script on all 164 positions. Use batching to avoid timeout.

### Step 4: Update UI

Modify MindMap.tsx to:
1. Display `formatted_insight` if available, else fall back to `insight`
2. Show references section with links to Content Library articles

## Deliverables

1. Schema migration applied to positions.db
2. `N5/scripts/enrich_position_insights.py` script
3. All positions enriched with formatted_insight
4. At least 50% of positions have 1+ Content Library references
5. MindMap.tsx updated to display enriched content

## Success Criteria

- Detail panel shows properly paragraphed text (not wall of text)
- References section shows "Related Reading" with clickable links
- No data loss — original insight preserved

## Output

When complete, write results to:
`file 'N5/builds/mindmap-ux-intuitive/workers/WORKER_D_OUTPUT.md'`

Include:
- Number of positions enriched
- Number with Content Library references
- Any positions that failed enrichment
- Code locations of all changes
