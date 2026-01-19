---
title: Close Conversation
description: Formal conversation close with session state update and optional artifact handling
tool: true
tags:
  - session
  - cleanup
  - conversation
created: 2025-10-15
last_edited: 2026-01-14
version: 3.0
---

# Close Conversation

Runs the formal **conversation-end workflow** to properly close a session.

## Quick Reference

| Tier | When | Scope |
|------|------|-------|
| 1 (Quick) | Default - simple discussions | State update, summary |
| 2 (Standard) | ≥3 artifacts, research sessions | + decisions, open items |
| 3 (Full) | Builds, complex work | + After-Action Report |

## Execution Steps

### Step 1: Assess Conversation Type

Determine which tier is appropriate based on:
- Number of artifacts created
- Complexity of work done
- Whether this was a build/project

### Step 2: Update Session State

1. **Read SESSION_STATE.md** from the conversation workspace
2. **Generate meaningful title** — Based on what was actually discussed
3. **Write 2-3 sentence summary** — Real summary of accomplishments
4. **Verify artifacts** are in correct locations

### Step 3: Tier-Specific Work

**Tier 2+ Only:**
- Extract key decisions with rationale
- Identify open items and next steps
- Recommend file moves if needed

**Tier 3 Only (Build Work):**
- Write After-Action Report (AAR) with:
  - Objective
  - What happened (narrative)
  - Key decisions and why
  - Artifacts created
  - Lessons learned
  - Next steps
- Save AAR to `Records/AARs/`

### Step 4: Final Checks

**Git Check:**
If git changes detected, note them and offer to commit.

**Commit Opportunities:**
Present optional commits:
- Learning Profile updates
- Content Library additions
- Code changes

### Step 5: Present Close Summary

```markdown
## Conversation Close

**Title:** [Generated title]
**Summary:** [2-3 sentences]

### Artifacts
- [List of files created/modified]

### Decisions Made
- [Key decisions, if any]

### Open Items
- [What remains, if any]

---
✅ Conversation closed (Tier N)
```

## AAR Format (Tier 3)

```markdown
---
created: {DATE}
last_edited: {DATE}
version: 1.0
provenance: {CONVO_ID}
---

# After-Action Report: {Descriptive Title}

**Date:** {DATE}
**Type:** {build|planning|research|debug|etc}

## Objective
{What was the goal? 2-3 sentences.}

## What Happened
{Narrative description. Include:
- What was built/changed/fixed
- Key challenges encountered
- How challenges were resolved}

### Key Decisions
{Decisions made with RATIONALE — not just "Decided X" but "Decided X because Y"}

### Artifacts Created
| Artifact | Location | Purpose |
|----------|----------|---------|
| {name} | {path} | {why} |

## Lessons Learned

### Process
{What did we learn about how to do this kind of work?}

### Technical
{What technical insights emerged?}

## Next Steps
{What should happen next? What's unfinished?}

## Outcome
**Status:** {Completed | Incomplete | Blocked}
{Brief outcome summary}
```

## Anti-Patterns

❌ Don't use templates without actual content
❌ Don't claim "Done" without reviewing what happened
❌ Don't skip the summary for complex sessions
❌ Don't auto-commit without user confirmation

## Documentation

See `prefs/operations/conversation-end.md` for full protocol.

