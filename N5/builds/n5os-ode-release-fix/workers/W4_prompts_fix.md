---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_oaJd6YmS7ETcg4UZ
worker_id: W4_prompts_fix
status: complete
dependencies: [W2_init_build_script]
---
# Worker Assignment: W4_prompts_fix

**Project:** n5os-ode-release-fix  
**Component:** prompt_references_fix  
**Orchestrator:** con_oaJd6YmS7ETcg4UZ  
**Estimated time:** 45 minutes

**DEPENDENCY:** Wait for W2_init_build_script to complete (creates init_build.py that Build Capability references)

---

## Objective

Fix broken file references and script paths in three key prompts.

---

## Context

Several prompts reference non-existent files or use incorrect relative paths. This breaks the user experience when they try to use these workflows.

**Working directory:** `/home/workspace/N5/export/n5os-ode/`

---

## Tasks

### Task 1: Simplify Close Conversation Prompt

The current `Prompts/Close Conversation.prompt.md` references 10+ scripts that don't exist in the export. 

**Action:** Rewrite to be a self-contained guidance prompt without external script dependencies.

Read the current file first, then rewrite it with this structure:

```markdown
---
description: |
  Unified conversation close - auto-detects mode (Worker vs Full) and tier.
  Workers do partial close (handoff to orchestrator). Full close includes commits.
tool: true
tags:
  - workflow
  - state
  - close
---

# Close Conversation

Systematic conversation close procedure for N5OS-Ode.

## When to Use

Call `@Close Conversation` when:
- Ending a work session
- Switching contexts
- Before extended breaks
- After completing major deliverables

## Close Procedure

### 1. State Crystallization

Update SESSION_STATE.md with:
- What was accomplished this session
- Any decisions made
- Open questions or blockers
- Next steps

If SESSION_STATE.md doesn't exist, create a brief summary note instead.

### 2. Artifact Check

Verify all created/modified files:
- [ ] Files saved to correct locations
- [ ] No orphaned files in workspace root
- [ ] Temporary files cleaned up

### 3. Handoff Summary

Provide a clear handoff for the next session:

```
## Session Summary

**Accomplished:**
- [List completed items]

**In Progress:**
- [List partial work]

**Next Session:**
- [List priority items]

**Blockers:**
- [List any blockers, or "None"]
```

## Worker Mode (Partial Close)

If this is a worker thread spawned from an orchestrator:

1. Summarize what was completed
2. List any files created/modified
3. Note any issues encountered
4. Prepare handoff for orchestrator

Do NOT attempt git commits - the orchestrator handles that.

## Full Mode (Interactive Session)

If this is an interactive session:

1. Complete state crystallization
2. Verify all artifacts
3. Stage changes for git if appropriate
4. Provide handoff summary

---

## Tips

- Be specific about what changed
- Include file paths for modified files
- Flag any concerns or uncertainties
- Don't mark "done" until actually done
```

### Task 2: Fix Journal Prompt Script Paths

Edit `Prompts/Journal.prompt.md` to use correct paths.

**Find and replace:**
- `scripts/journal.py` → `N5/scripts/journal.py`
- Any other relative script paths → full paths from workspace root

Read the file first to understand all references, then fix them.

### Task 3: Fix Build Capability Prompt Script Paths

Edit `Prompts/Build Capability.prompt.md` to use correct paths.

**Find and replace:**
- `scripts/init_build.py` → `N5/scripts/init_build.py`
- Any other relative script paths → full paths from workspace root

Read the file first to understand all references, then fix them.

---

## Verification

After fixing all prompts:

```bash
cd /home/workspace/N5/export/n5os-ode

# 1. Close Conversation has no broken file references
# Manual check: read through and verify no `file '...'` refs to non-existent files
cat Prompts/Close\ Conversation.prompt.md | grep -E "file\s*'" || echo "PASS: No file refs or all valid"

# 2. Journal prompt has correct script path
grep "N5/scripts/journal.py" Prompts/Journal.prompt.md && echo "PASS: Journal paths fixed"

# 3. Build Capability has correct script path  
grep "N5/scripts/init_build.py" Prompts/Build\ Capability.prompt.md && echo "PASS: Build Capability paths fixed"

# 4. No references to plain "scripts/" without N5 prefix in prompts
rg "scripts/.*\.py" Prompts/*.prompt.md | grep -v "N5/scripts" && echo "FAIL: Found relative paths" || echo "PASS: All paths absolute"
```

---

## Handoff

When complete:
1. Report: "W4_prompts_fix complete. Fixed 3 prompts."
2. For Close Conversation: note it was rewritten to be self-contained
3. For Journal & Build Capability: list the path fixes made
4. Show verification output
5. Do NOT commit yet - W6 will handle all commits

---

## Files to Edit

All paths relative to `/home/workspace/N5/export/n5os-ode/`:

1. `Prompts/Close Conversation.prompt.md` — full rewrite
2. `Prompts/Journal.prompt.md` — path fixes
3. `Prompts/Build Capability.prompt.md` — path fixes


