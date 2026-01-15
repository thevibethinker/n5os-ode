---
title: Close Conversation
description: Formal conversation close - auto-detects tier based on conversation type
tool: true
tags:
  - session
  - cleanup
  - conversation
created: 2025-10-15
last_edited: 2026-01-14
version: 3.2
---

# Close Conversation

Runs the formal **conversation-end workflow** with automatic tier detection.

**CRITICAL PRINCIPLE:** Scripts handle mechanics. LLM (Librarian) handles all semantic work.
- Scripts gather file lists, git status, paths, raw content
- Scripts **DO NOT** write summaries, extract decisions, or generate AARs
- Librarian **READS** the context and **WRITES** all semantic artifacts

## Quick Reference

| Tier | When | Cost | Time |
|------|------|------|------|
| 1 (Quick) | Default - simple discussions | ~$0.03 | <30s |
| 2 (Standard) | ≥3 artifacts, research | ~$0.06 | <90s |
| 3 (Full) | Builds, orchestrator, debug | ~$0.15 | <180s |

## Flags

- `--tier=1` / `--tier=2` / `--tier=3`: Force specific tier
- `--dry-run`: Preview without changes

## Execution Steps

### Step 1: Detect Tier

Run the router to determine appropriate tier:

```bash
python3 N5/scripts/conversation_end_router.py --convo-id {CONVO_ID}
```

Review the recommendation and signals. Override with `--tier=N` if needed.

### Step 2: Execute Mechanical Close

Based on the tier, run the appropriate script:

**Tier 1 (Quick):**
```bash
python3 N5/scripts/conversation_end_quick.py --convo-id {CONVO_ID}
```

**Tier 2 (Standard):**
```bash
python3 N5/scripts/conversation_end_standard.py --convo-id {CONVO_ID}
```

**Tier 3 (Full Build):**
```bash
python3 N5/scripts/conversation_end_full.py --convo-id {CONVO_ID}
```

### Step 2.5: PII Audit

Scan files created/modified during this conversation for PII:

```bash
python3 N5/scripts/conversation_pii_audit.py --convo-id {CONVO_ID} --auto-mark
```

This will:
- Scan artifacts listed in SESSION_STATE.md
- Scan git-changed files in the workspace
- Detect email, phone, SSN, credit card patterns
- Auto-mark directories containing PII with `.n5protected` markers

**If PII is detected:**
- Review the findings table
- Confirm directories are appropriately marked
- If additional sensitive data exists, manually protect:
  ```bash
  python3 N5/scripts/n5_protect.py protect <path> --reason 'description' --pii --pii-categories <types>
  ```

**Skip this step if:** The conversation was purely discussion with no file creation.

### Step 3: Invoke Librarian for Semantic Close

**Switch to Librarian:**
```
set_active_persona("1bb66f53-9e2a-4152-9b18-75c2ee2c25a3")
```

---

## Librarian Semantic Work by Tier

### All Tiers (Tier 1+)

1. **Read SESSION_STATE.md** from the conversation workspace (`/home/.z/workspaces/{CONVO_ID}/SESSION_STATE.md`)
2. **Audit SESSION_STATE:** Run `python3 N5/scripts/session_state_manager.py audit --convo-id {CONVO_ID}`
3. **Generate meaningful title** — Based on semantic understanding of what was discussed, NOT pattern matching
4. **Write 2-3 sentence summary** — Real semantic summary of accomplishments, NOT template filling
5. **Verify artifacts** are in correct locations

### Tier 2+ Only

6. **Extract key decisions with rationale** — Read the conversation context and identify actual decisions made, with WHY they were made
7. **Identify open items** — Real open questions and next steps from semantic understanding
8. **Recommend file moves** if needed

### Tier 3 Only (CRITICAL: AAR GENERATION)

**The script provides a context bundle. Librarian WRITES the AAR.**

9. **Read the context bundle** from the script output (contains SESSION_STATE, debug logs, build context)

10. **WRITE the After-Action Report:**
    - Read SESSION_STATE.md and understand what ACTUALLY happened
    - Read any PLAN.md or STATUS.md from build workspace
    - Read DEBUG_LOG.jsonl if present to understand problems solved
    - **Semantically synthesize** what was accomplished, what decisions were made and why, what was learned
    - Write the AAR with real understanding — NOT template filling
    
11. **AAR Format:**
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
**Conversation:** {CONVO_ID}

## Objective

{What was the goal of this conversation? Write 2-3 sentences based on your understanding.}

## What Happened

{Narrative description of what actually occurred. Organize into phases if there were distinct stages. Include:
- What was built/changed/fixed
- Key challenges encountered
- How challenges were resolved}

### Key Decisions

{List decisions made with RATIONALE. Not just "Decided X" but "Decided X because Y"}

### Artifacts Created

| Artifact | Location | Purpose |
|----------|----------|---------|
| {name} | {path} | {why it was created} |

## Lessons Learned

### Process
{What did we learn about how to do this kind of work?}

### Technical
{What technical insights emerged?}

## Next Steps

{What should happen next? What's unfinished?}

## Outcome

**Status:** {Completed | Incomplete | Blocked}

{Brief outcome summary with before/after if applicable}
```

12. **Save the AAR:** Write to `Records/AARs/{DATE}_{Slug}.md`

13. **Capability Graduation** (if build is complete):
    ```bash
    python3 N5/scripts/capability_graduation.py check --build-slug <slug>
    python3 N5/scripts/capability_graduation.py graduate --build-slug <slug> --convo-id {CONVO_ID}
    ```

14. **Extract lessons worth logging** — If significant learning occurred

### Step 4: Final Checks

**Git Check:**
If git changes detected, note them and ask about committing.

### Step 5: Commit Target Suggestions (Triggering Options)

**Load the commit targets registry:**
```bash
cat N5/config/commit_targets.json
```

**For each target, use SEMANTIC UNDERSTANDING to evaluate relevance:**

| Target | Detection Question |
|--------|-------------------|
| **Learning Profile** | Did V ask questions? Did I explain technical concepts? Did understanding demonstrably increase? |
| **Content Library** | Were articles read via `save_webpage` or `read_webpage`? Did V express this was valuable? Did we dig deeply (not just skim)? |
| **Voice Library** | Did V use distinctive phrasing worth capturing? Did we discuss voice/tone? |
| **Git** | Are there code or configuration changes visible in `git status`? |

**Quality Gates:**
- **Content Library has HIGH threshold** — Deep engagement + positive response required. Push back when inclusion would weaken coherence or add redundancy.
- **Learning Profile** — Only suggest when genuine learning occurred, not just discussion.
- **Voice Library** — Only suggest distinctive phrases, not routine writing.

**Present options to V as a checklist (do NOT auto-commit):**

```markdown
## Commit Opportunities

Based on this conversation, you may want to commit to:

☐ **Learning Profile** — [Specific concepts learned, if any]
☐ **Content Library** — [Articles/resources saved, if any]
☐ **Voice Library** — [Distinctive phrases captured, if any]
☐ **Git** — [Code changes detected, if any]

Reply with which items to commit, or skip to close.
```

**If V confirms a commit:**
- **Learning Profile**: Append entry to `## Learning Timeline` section in `Personal/Learning/my-learning-profile.md` with date and concept
- **Content Library**: Run `python3 N5/scripts/content_ingest.py <path> --type <type> --move`
- **Voice Library**: Append to appropriate section in `Knowledge/voice-library/` (categorization pending worker design)
- **Git**: Run standard git add/commit flow

**Important:** These are triggering options, not automatic. V must confirm before any commit.

**Return to Operator:**
```
set_active_persona("90a7486f-46f9-41c9-a98c-21931fa5c5f6")
```

## Output

Present the formatted close output per the tier template.

End with:
```
✅ Conversation closed (Tier N)
```

## Anti-Patterns (DO NOT DO)

❌ **Do not use regex to extract decisions** — That produces garbage
❌ **Do not template-fill AARs** — That produces garbage  
❌ **Do not let scripts write semantic content** — Scripts are dumb, LLM is smart
❌ **Do not claim "Done" without actual semantic analysis** — Read the files, understand them, write real content

## Full Documentation

`file 'N5/prefs/operations/conversation-end-v3.md'`

## Version History

- **v3.2** (2026-01-14): Added Step 2.5 - PII Audit. Auto-scans artifacts for PII and marks directories for protection.
- **v3.1** (2026-01-13): Added Step 5 - Commit Target Suggestions. New registry-based system for suggesting commits to Learning Profile, Content Library, Voice Library, and Git.
- **v3.0** (2026-01-12): AAR generation moved entirely to Librarian. Scripts provide context only.
- **v2.0** (2025-12-26): Librarian now owns semantic close work
- **v1.0** (2025-10-15): Initial tiered system




