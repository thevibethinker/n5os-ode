---
date: '2025-09-20T18:39:00Z'
last-tested: '2025-09-20T18:39:00Z'
generated_date: '2025-09-20T18:39:00Z'
checksum: hygiene_preflight_v1_0_0
tags: [audit, hygiene, validation]
category: audit
priority: high
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/hygiene-preflight.md
---
# `hygiene-preflight`

Version: 1.0.0

**DEPENDENCY**: `N5/core_manifest.json` must exist

Workflow: preflight

Summary: Fail-fast guard: ensures core-manifest engine files are NOT missing, empty, or ignored before any bulk rename / hygiene / upgrade run.

Tags: preflight, guard, hygiene, rename, upgrade

## Inputs
(None)

## Outputs
- **result**: object - `{pass: true/false, timestamp: epoch}`

## Exit Codes
- 0: all checks passed — safe to proceed with hygiene/rename
- 1: any check failed — operation aborted, log written

## Side Effects
- writes: same append-only line as core-audit to `runtime/audit/core_audit.log`

## Examples
```
N5: run hygiene-preflight                        # manual check
# --- or called automatically before hygiene ---
bash: ./hygiene_script.sh && N5 run hygiene-preflight
```

## Related Commands
- **core-audit**: same checks, non-blocking, returns full report
- **git-check**: pre-commit audit of staged changes

## Implementation
- re-uses `N5/scripts/hygiene_preflight.py`, internally calls core_audit run
- fails *immediately* on first issue, prints concise error to stderr
- intended to be invoked right before any bulk operation that touches files