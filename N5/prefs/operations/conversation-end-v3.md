---
created: 2025-12-18
last_edited: 2026-01-12
version: 4.0
provenance: con_wCDYWdPur68NGfGX
---

# Conversation-End System v4.0

> **Single Source of Truth** for conversation closure workflow.

## Overview

Tiered system that defaults to quick closure and escalates based on conversation markers.

**CRITICAL Division of Labor:**
- **Scripts** = Mechanics ONLY (file scanning, git status, path gathering, raw content reading)
- **Librarian (LLM)** = ALL Semantics (summaries, decisions, AARs, lessons, state crystallization)

**Scripts DO NOT:**
- Extract decisions (no regex)
- Generate AARs (no template filling)
- Write summaries (no pattern matching)
- Make semantic judgments

**Scripts DO:**
- Scan files and categorize by type
- Check git status
- Read raw SESSION_STATE.md content
- Gather debug log entries
- Find build workspaces
- Provide context bundles for LLM

| Tier | Name | Use Case | Cost Target | Time Target |
|------|------|----------|-------------|-------------|
| 1 | Quick | Simple discussions, Q&A | <$0.05 | <30s |
| 2 | Standard | Research, substantial discussions | <$0.08 | <90s |
| 3 | Full Build | Build/orchestrator sessions | <$0.20 | <180s |

## Persona Ownership

| Phase | Owner | Responsibility |
|-------|-------|----------------|
| Tier Detection | Script | `conversation_end_router.py` |
| Mechanical Close | Script | File lists, git status, context bundle |
| Semantic Close | **Librarian** | Summaries, decisions, AARs, lessons, filing |
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
| `conversation_end_quick.py` | Tier 1: Basic file scan, session state update |
| `conversation_end_standard.py` | Tier 2: File organization, git status, raw content |
| `conversation_end_full.py` | Tier 3: Context bundle with build/debug info |
| `capability_graduation.py` | Build → Capability graduation |

## What Each Tier Does

### Tier 1: Quick Close

**Script (mechanics):**
1. Scan workspace files
2. Check git status
3. Update SESSION_STATE status=closed

**Librarian (semantics):**
4. Read SESSION_STATE.md
5. Generate meaningful title (semantic, not pattern-based)
6. Write 2-3 sentence summary (real understanding)
7. Audit SESSION_STATE for completeness

### Tier 2: Standard Close

**Script (mechanics):**
- All Tier 1 script steps, plus:
- Categorized file organization
- Raw content gathering for LLM

**Librarian (semantics):**
- All Tier 1 Librarian steps, plus:
8. Extract key decisions WITH RATIONALE (semantic, not regex)
9. Identify open questions (semantic understanding)
10. Recommend file moves based on content understanding

### Tier 3: Full Build Close

**Script (mechanics):**
- All Tier 2 script steps, plus:
- Build workspace detection
- DEBUG_LOG.jsonl reading
- PLAN.md / STATUS.md reading
- **Output: Context bundle JSON** (NOT formatted AAR)

**Librarian (semantics) — CRITICAL:**
- All Tier 2 Librarian steps, plus:

11. **WRITE the After-Action Report:**
    - Read context bundle from script
    - Read SESSION_STATE.md with semantic understanding
    - Read PLAN.md, STATUS.md, DEBUG_LOG if present
    - **Synthesize what actually happened** — narrative, not template
    - **Extract real decisions with rationale** — not regex patterns
    - **Identify real lessons** — based on understanding, not keyword matching
    - Write the AAR to `Records/AARs/{DATE}_{Slug}.md`

12. **Capability Graduation** (if build complete)
13. **Lesson extraction** (semantic, from understanding)
14. **Build STATUS.md verification**

## AAR Template (for Librarian to FILL SEMANTICALLY)

```markdown
---
created: {DATE}
last_edited: {DATE}
version: 1.0
provenance: {CONVO_ID}
---

# After-Action Report: {Descriptive Title - Semantic}

**Date:** {DATE}
**Type:** {build|planning|research|debug|etc}
**Conversation:** {CONVO_ID}

## Objective

{2-3 sentences from semantic understanding of conversation purpose}

## What Happened

{Narrative description organized by phases. What was built, challenges, resolutions.}

### Key Decisions

{Decisions WITH rationale. "Decided X because Y" not just "Decided X"}

### Artifacts Created

| Artifact | Location | Purpose |
|----------|----------|---------|

## Lessons Learned

### Process
{Process insights from semantic understanding}

### Technical
{Technical insights from semantic understanding}

## Next Steps

{What's next, what's unfinished}

## Outcome

**Status:** {Completed | Incomplete | Blocked}
{Brief outcome summary}
```

## Anti-Patterns

❌ **Regex decision extraction** — Produces garbage like "chose to use the API"
❌ **Template-filled AARs** — Produces hollow documents without understanding
❌ **Scripts writing semantic content** — Scripts are pattern matchers, not reasoners
❌ **Claiming "Done" without reading files** — Must read and understand before writing

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

## Version History

- **v4.0** (2026-01-12): AAR generation fully owned by Librarian. Scripts provide context only. Removed all regex extraction.
- **v3.2** (2026-01-09): Capability graduation flow
- **v3.0** (2025-12-18): Tiered system with Librarian ownership

