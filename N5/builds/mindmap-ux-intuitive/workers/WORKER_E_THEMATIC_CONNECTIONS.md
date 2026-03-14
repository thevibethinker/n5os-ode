---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_jmgVLfK7jKZO9X1i
---

# WORKER ASSIGNMENT: Thematic Connection Descriptions

**Assigned to:** Zo (Builder Mode)
**Objective:** Replace generic relationship labels with meaningful thematic descriptions.

## Context

The Mind Map shows connections between V's intellectual positions. Currently, connections display generic labels like "weakly related" which provide no insight into WHY positions are connected.

## Problem

See `file '/home/.z/chat-images/image (339).png'` — The "Connected Ideas" section shows:
- "The traditional resume is a failed data structure..." — weakly related
- "AI has reduced the marginal cost of BS to zero" — weakly related
- "Ghost jobs are a systemic problem..." — weakly related

These should instead show thematic connections like:
- "explores hiring signal degradation"
- "examines AI's impact on trust"
- "addresses systemic market dysfunction"

## Files

- `file 'N5/data/positions.db'` — SQLite database
- `file 'Sites/vrijenattawar-staging/src/pages/MindMap.tsx'` — UI display

## Current Schema

The `connections` column in positions table contains JSON:
```json
[
  {"target_id": "some-position-id", "relationship": "weakly_related"},
  {"target_id": "another-id", "relationship": "strongly_related"}
]
```

## Task

### Step 1: Enhance connections schema

Update connections JSON structure to include thematic description:
```json
[
  {
    "target_id": "some-position-id", 
    "relationship": "weakly_related",
    "thematic_description": "explores hiring signal degradation"
  }
]
```

### Step 2: Create thematic analysis script

Create `file 'N5/scripts/generate_thematic_connections.py'` that:
1. For each position, reads its connections
2. For each connection, reads BOTH positions' titles and insights
3. Uses LLM to generate a short (3-6 word) thematic description of what connects them
4. Updates the connections JSON with thematic_description

### Step 3: Run analysis

Process all connections. There are ~195 connections to analyze.

Use prompt like:
```
Position A: "{title_a}"
Insight A: "{insight_a}"

Position B: "{title_b}"  
Insight B: "{insight_b}"

These positions are connected. In 3-6 words, describe the thematic thread that connects them.
Focus on the intellectual relationship, not generic terms.

Good examples: "hiring signal authenticity", "AI trust erosion", "market dysfunction patterns"
Bad examples: "related ideas", "similar topics", "both about hiring"
```

### Step 4: Update UI

Modify MindMap.tsx Connected Ideas section to:
1. Display `thematic_description` if available
2. Fall back to formatted `relationship` if no thematic description
3. Style thematic descriptions in a muted but readable way

## Deliverables

1. `N5/scripts/generate_thematic_connections.py` script
2. All 195 connections enriched with thematic_description
3. MindMap.tsx updated to display thematic connections
4. Backup of positions.db before modification

## Success Criteria

- Connected Ideas shows meaningful descriptions, not "weakly related"
- Descriptions are concise (3-6 words) and intellectually meaningful
- No broken connections — all target_ids still valid

## Output

When complete, write results to:
`file 'N5/builds/mindmap-ux-intuitive/workers/WORKER_E_OUTPUT.md'`

Include:
- Number of connections enriched
- Sample of 10 thematic descriptions generated
- Any connections that failed
- Code locations of all changes
