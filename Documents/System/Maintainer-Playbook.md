---
created: 2026-05-12
last_edited: 2026-05-15
version: 1.1
provenance: con_yUBhTqBAcxEFKwof
---

# Maintainer Playbook

Maintainer is a playbook, not a persona. It is the standard cleanup, git hygiene, ignore/protection, and commit-cadence protocol used by Operator and Builder.

## Purpose

Keep the workspace legible while work is happening, instead of waiting until drift becomes a separate project.

Maintainer handles:
- worktree inspection
- file classification: durable source, deliverable artifact, runtime exhaust, scratch, misplaced content
- `.gitignore` and `.n5protected` alignment recommendations
- safe cleanup previews
- commit boundary recommendations
- close-time git hygiene
- session-state crystallization (formerly Librarian)
- coherence verification (formerly Librarian)
- index maintenance (formerly Librarian)

Maintainer does not:
- delete, move, restore, push, publish, or externally commit without V's explicit authorization
- replace Operator, Builder, Pulse, or close skills
- make semantic build judgments that belong to the active specialist

## Ownership

- **Owner:** Operator
- **Implementation partner:** Builder when scripts, git, code, services, or shared config are involved
- **Close consumer:** `Skills/close/` and `Skills/build-close/`
- **Pulse consumer:** `Skills/pulse/`

Maintainer should usually run inline as a checklist. Use a separate task or Pulse Drop only when cleanup itself is large, risky, or decomposable.

## Trigger Points

Run a Maintainer checkpoint proactively:

- after every approved plan or build initialization
- after each meaningful Pulse wave
- before `pulse.py finalize <slug>`
- during close or build-close
- before any commit, push, promotion, or deletion
- when dirty worktree entries exceed 50
- when untracked files exceed 25
- when deleted files exceed 10
- when generated artifacts appear outside their canonical roots
- when `.gitignore` or `.n5protected` appears misaligned with observed drift

For small single-file edits, a quick `git status --short` plus scoped diff review is enough.

## Branch / Worktree Guardrail

Before branch creation, branch switching, worktree creation/removal, pushing, opening PRs, or committing a mixed worktree, run:

```bash
python3 N5/scripts/n5_git_context_check.py --intent "<short intent>"
```

Default interpretation:

- `main-ok`: keep the shared checkout on `main`; do not create a feature branch just to hold research, planning, meetings, or build records
- `branch-required`: use a scoped feature branch because shared source, runtime behavior, sites, deployed skills, schemas, or public/canonical outputs are involved
- `worktree-required`: use a separate worktree only for true concurrent branch work
- `blocked`: stop and classify dirty/runtime/generated files before branch or worktree mutation

This checker is advisory for humans and agents, not a replacement for judgment. If bypassed under explicit authorization, record the reason in the commit message, build status, or close note.

## Commit Cadence

Default cadence:

1. **After plan/init:** commit scaffold and plan artifacts once they pass required checks.
2. **After each meaningful wave:** commit coherent, validated progress that could be reverted independently.
3. **Before risky transitions:** commit or checkpoint before large refactors, bulk cleanup, promotions, or destructive operations.
4. **At close:** run the close Git gate and either commit the final coherent unit or report why it should remain uncommitted.

Prefer incremental commits when the change has a coherent rollback boundary. Avoid mechanical "every prompt" commits that split one logical change into noise.

## Standard Procedure

1. Inspect state:
   ```bash
   git status --short
   git diff --stat
   ```
2. Classify changes:
   - expected source changes
   - expected generated deliverables
   - runtime/cache/log output
   - accidental root clutter
   - surprising deletions
   - protected or high-risk paths
3. Review scoped diffs for intended files before editing or staging.
4. For destructive or bulk cleanup, run protection and safety gates first:
   ```bash
   python3 N5/scripts/n5_protect.py check <path>
   python3 N5/scripts/n5_safety.py check --path <path>
   ```
5. Run the Git audit before committing:
   ```bash
   python3 N5/scripts/n5_git_check.py --dry-run
   ```
6. Stage only the coherent unit being committed.
7. Commit only when V has explicitly authorized the commit or the active workflow already includes commit authorization.
8. Report:
   - what was committed or left uncommitted
   - what was ignored or should be ignored
   - what needs protection review
   - remaining dirty state

## Ignore And Protection Alignment

Use evidence from repeated drift, not one-off annoyance.

Add to `.gitignore` when files are reproducible, machine-local, cache-like, logs, screenshots, intermediate exports, or runtime ledgers that should not be reviewed as source.

Add or adjust `.n5protected` when files are durable, user-authored, canonical indices, schemas, high-value records, or files where accidental deletion/overwrite would be expensive.

If a path is both noisy and valuable, prefer moving it behind a scripted export/checkpoint pattern instead of blindly ignoring it.

## Pulse Integration

Pulse should include Maintainer checkpoints as orchestration boundaries:

- **Plan/init checkpoint:** after `PLAN.md`, `meta.json`, and Drop briefs are created.
- **Wave checkpoint:** after each meaningful wave and before advancing when code/artifacts changed materially.
- **Finalize checkpoint:** before `pulse.py finalize <slug>`, verify build artifacts are routed, runtime exhaust is identified, and commit state is understood.

Workers never push. Cleanup Drops should deposit findings and recommendations; the orchestrator decides commits.

## State Crystallization

Folded in from the former Librarian persona (deprecated 2026-05-15). Maintainer is now the home for SESSION_STATE work.

### Ensure state exists

Before any organizational work in a conversation that requires session state per `N5/SESSION_STATE_POLICY.md`, verify the state file exists:

```bash
ls /home/.z/workspaces/{CONVO_ID}/SESSION_STATE.md 2>/dev/null
```

If missing and the lane requires state, create it:

```bash
python3 N5/scripts/session_state_manager.py init --convo-id {CONVO_ID} --type discussion --message "Maintainer init - state was missing"
echo "$(date -Iseconds) | WARNING | {CONVO_ID} - SESSION_STATE created by Maintainer" >> /home/workspace/N5/logs/session_state_gaps.log
```

This is defense-in-depth. Operator should normally catch missing state on return; this catches any that slip through.

### Schema-compliant sync

Schema reference: `file 'N5/templates/session_state_gold.md'`.

Required fields (no `TBD` in these):
- `Metadata.Focus` — what this conversation is about
- `Metadata.Objective` — what we are trying to achieve
- `Progress.Overall` — percentage complete (0–100%)
- `Progress.Current Phase` — what phase/step we are on
- `Covered` — topics/tasks completed

Sync command:

```bash
python3 N5/scripts/session_state_manager.py sync --convo-id <id> --json '{
  "Metadata": {"Focus": "...", "Objective": "..."},
  "Progress": {"Overall": "X%", "Current Phase": "..."},
  "Covered": ["item1", "item2"],
  "Key Insights": ["insight1"],
  "Decisions Made": ["decision1"]
}'
```

### When to run

- After a specialist returns substantial work
- After a file-creation burst
- Before conversation close
- When coherence feels off (broken references, stale state)

For quick syncs, run inline. For substantial state work, treat it as its own Maintainer checkpoint.

## Coherence Verification

Verify references resolve to things that exist:

- File references in SESSION_STATE → files exist
- Build `STATUS.md` → matches actual drop/deposit file state
- Worker assignments → parent linkage intact
- Build artifacts in correct `N5/builds/<slug>/` directory
- No orphaned files from failed operations

When mismatch is found, prefer minimal correction (sync state to reality) over rewriting either side wholesale.

## Index Maintenance

Keep workspace indexes current when content changes:

- `N5/lists/` — when list items are added or removed
- `N5/index/` — when major artifacts are created
- Build manifests — when drop/deposit topology shifts

Only touch indexes that are out of date. Do not reorganize already-coherent indexes.

## Close Integration

Close remains the final safety net:

- `N5/scripts/n5_git_check.py --dry-run` is the Git audit gate.
- build-close runs structural audits before synthesis.
- close reports whether the worktree is clean, safe to commit, needs confirmation, or blocked.

Maintainer adds the expectation that close should also identify whether the next commit boundary is plan/init, wave, finalize, or cleanup-only.
