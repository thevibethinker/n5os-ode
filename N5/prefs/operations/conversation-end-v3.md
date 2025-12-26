---
created: 2025-12-18
last_edited: 2025-12-18
version: 3.0
provenance: con_nXKLrpy6lsnJm0dz
---

# Conversation-End System v3.0

> **Single Source of Truth** for conversation closure workflow.

## Overview

Tiered system that defaults to quick closure and escalates based on conversation markers.

| Tier | Name | Use Case | Cost Target | Time Target |
|------|------|----------|-------------|-------------|
| 1 | Quick | Simple discussions, Q&A | <$0.05 | <30s |
| 2 | Standard | Research, substantial discussions | <$0.08 | <90s |
| 3 | Full Build | Build/orchestrator sessions | <$0.20 | <180s |

## Tier Detection

**Default:** Tier 1 (Quick)

**Escalate to Tier 2 if:**
- ≥3 file artifacts in conversation workspace
- SESSION_STATE type = research/discussion with progress
- Git changes detected

**Escalate to Tier 3 if:**
- SESSION_STATE type = build OR orchestrator
- Build workspace exists (`N5/builds/<slug>/`)
- DEBUG_LOG.jsonl present
- Build markers in conversation

**Manual Override:** `--tier=N` flag

## Scripts

| Script | Purpose |
|--------|---------|
| `conversation_end_router.py` | Tier detection |
| `conversation_end_quick.py` | Tier 1 execution |
| `conversation_end_standard.py` | Tier 2 execution |
| `conversation_end_full.py` | Tier 3 execution |
| `conversation_end_analyzer.py` | File analysis (shared) |

## What Each Tier Does

### Tier 1: Quick Close
1. Generate LLM thread title
2. Generate 2-3 sentence summary
3. Update SESSION_STATE status=closed
4. List files in workspace
5. Git status check

### Tier 2: Standard Close
- All Tier 1 steps, plus:
6. Categorized file organization
7. Decision/outcome extraction
8. Open items detection
9. Move recommendations

### Tier 3: Full Build Close
- All Tier 2 steps, plus:
10. Full AAR generation
11. Lesson extraction (if debug session)
12. Capability registry check
13. Build workspace archival
14. Placeholder scan

## Output Formats

See templates in:
- `conversation-end-tier1-template.md`
- `conversation-end-output-template.md` (Tier 3)

## Usage

Invoke via prompt:
```
@Close Conversation
@Close Conversation --tier=1
@Close Conversation --tier=3
```

Or directly via scripts:
```bash
# Auto-detect tier
python3 N5/scripts/conversation_end_router.py --convo-id <id>

# Execute specific tier
python3 N5/scripts/conversation_end_quick.py --convo-id <id>
python3 N5/scripts/conversation_end_standard.py --convo-id <id>
python3 N5/scripts/conversation_end_full.py --convo-id <id>
```

## Deprecation Notes

**Supersedes:**
- `conversation-end.md` (old 500+ line doc)
- `conversation-end-CANONICAL.md` (deleted)
- `conversation_end_pipeline.md` (deleted)
- `conversation_end_schema.md` (deleted)

The old `conversation-end.md` will be archived after validation period.

