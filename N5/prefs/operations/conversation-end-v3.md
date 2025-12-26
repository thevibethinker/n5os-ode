---
created: 2025-12-18
last_edited: 2025-12-26
version: 3.1
provenance: con_thiVbfdLjmmBE7ol
---

# Conversation-End System v3.1

> **Single Source of Truth** for conversation closure workflow.

## Overview

Tiered system that defaults to quick closure and escalates based on conversation markers.

**Division of Labor:**
- **Scripts** = Mechanics (file scanning, git status, pattern detection)
- **Librarian** = Semantics (summaries, state crystallization, filing decisions)

| Tier | Name | Use Case | Cost Target | Time Target |
|------|------|----------|-------------|-------------|
| 1 | Quick | Simple discussions, Q&A | <$0.05 | <30s |
| 2 | Standard | Research, substantial discussions | <$0.08 | <90s |
| 3 | Full Build | Build/orchestrator sessions | <$0.20 | <180s |

## Persona Ownership

| Phase | Owner | Responsibility |
|-------|-------|----------------|
| Tier Detection | Script | `conversation_end_router.py` |
| Mechanical Close | Script | File lists, git status, basic structure |
| Semantic Close | **Librarian** | Summaries, state sync, filing, AAR enhancement |
| Final Output | Operator | Present results, handle git commit prompt |

**Librarian invocation:** `set_active_persona("1bb66f53-9e2a-4152-9b18-75c2ee2c25a3")`

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

**Script (mechanics):**
1. Scan workspace files
2. Check git status
3. Update SESSION_STATE status=closed

**Librarian (semantics):**
4. Generate meaningful title
5. Write 2-3 sentence summary
6. Audit SESSION_STATE for completeness

### Tier 2: Standard Close

**Script (mechanics):**
- All Tier 1 script steps, plus:
- Categorized file organization
- Open items detection

**Librarian (semantics):**
- All Tier 1 Librarian steps, plus:
7. Extract key decisions with rationale
8. Identify open questions
9. Recommend file moves

### Tier 3: Full Build Close

**Script (mechanics):**
- All Tier 2 script steps, plus:
- Build workspace detection
- Placeholder scan
- DEBUG_LOG check

**Librarian (semantics):**
- All Tier 2 Librarian steps, plus:
10. Full AAR enhancement with conversation context
11. Lesson extraction (if debug session)
12. Capability registry check
13. Build STATUS.md verification

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


