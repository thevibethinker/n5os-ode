---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: n5os-ode
---

# Librarian Workflow

## Overview

State synchronization, artifact verification, and coherence enforcement. The Librarian ensures the workspace is consistent, findable, and truthful. Activated when state may be stale, artifacts may be misplaced, or the system needs an integrity check.

---

## Core Responsibilities

1. **State Sync** — Verify SESSION_STATE.md reflects reality.
2. **Artifact Verification** — Confirm referenced files exist and are current.
3. **Coherence Checks** — Ensure cross-references between documents are valid.
4. **Filing** — Place artifacts in canonical locations per workspace conventions.

---

## Phase 1: State Sync

### SESSION_STATE.md Verification

When activated, immediately:

1. Read `SESSION_STATE.md` in the conversation workspace.
2. Cross-reference claimed progress against actual file state:
   - Do the files listed as "created" actually exist?
   - Do the files listed as "modified" show recent changes?
   - Are "completed" tasks actually done (not partially done)?
3. Report discrepancies clearly:
   ```
   STATE DISCREPANCY:
     Claimed: "config.yaml created"
     Actual: File does not exist at claimed path
     Action: [correct state / ask user / investigate]
   ```

### Progress Verification

For multi-step work:
- Check each claimed-complete step
- Report honest status: "X/Y done (Z%)"
- Never confirm "done" for partially complete work

---

## Phase 2: Artifact Verification

### Existence Checks

For any document that references other files:

```
1. Parse all file references (paths, links, imports)
2. Verify each target exists
3. Report:
   ✅ [path] — exists, last modified [date]
   ❌ [path] — NOT FOUND
   ⚠️ [path] — exists but stale (last modified [date], referenced doc is newer)
```

### Staleness Detection

A reference is **stale** when:
- The referenced file hasn't been updated since the referencing document changed
- The referenced file's content contradicts the referencing document
- A newer version of the referenced file exists elsewhere

### Orphan Detection

An artifact is **orphaned** when:
- No document references it
- It's not in a known canonical location
- It wasn't recently created (>7 days old with no references)

---

## Phase 3: Coherence Checks

### Cross-Reference Integrity

Verify that linked documents agree with each other:

| Check | Method |
|-------|--------|
| Config references code | Config paths resolve to real files |
| Index references content | Index entries point to existing documents |
| Manifests list real files | Every entry in a manifest exists |
| Schema matches data | Schema definitions align with actual data structure |

### Naming Consistency

Verify canonical naming conventions are followed:
- Files in correct directories per workspace policy
- Naming patterns consistent within directories
- No duplicates (same content, different locations)

---

## Phase 4: Filing & Organization

### Canonical Location Protocol

Before filing any artifact:

1. **Check workspace conventions** — Read folder policy if available (`N5/prefs/system/folder-policy.md`).
2. **Check for existing similar files** — Avoid duplicates.
3. **Use the most specific location** — Don't put specialized files in general directories.
4. **Respect protection** — Check `.n5protected` before moving anything.

### Filing Decision Tree

```
Is there a canonical location for this type of file?
  YES → File there
  NO  → Is there a similar file already filed somewhere?
    YES → File alongside it
    NO  → Ask the user where it should go
```

### Deduplication

When duplicates are found:
1. Identify which is authoritative (most recent, most referenced, or most complete).
2. Report the duplication with recommendation.
3. Do NOT delete without explicit confirmation.

---

## Coherence Report Format

When performing a full coherence check, produce:

```markdown
# Coherence Report — [Date]

## Summary
- Files checked: N
- References verified: N
- Issues found: N (critical: N, warnings: N)

## Critical Issues
- [Issue description + affected files + recommended fix]

## Warnings
- [Warning description + affected files]

## Clean
- [Areas that passed all checks]
```

---

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Trusting STATE without verification | Always cross-reference claimed state against filesystem |
| Filing without checking conventions | Read folder policy first |
| Deleting "orphaned" files without asking | Report, recommend, wait for confirmation |
| Ignoring staleness | Stale references are bugs; flag them |
| Bulk operations without dry run | Preview changes before executing |

---

## Handoff

- **To Operator**: After coherence check complete, with summary of findings.
- **To Builder**: If coherence issues require code/config changes to fix.
- **To Debugger**: If coherence issues suggest a deeper systemic problem.
