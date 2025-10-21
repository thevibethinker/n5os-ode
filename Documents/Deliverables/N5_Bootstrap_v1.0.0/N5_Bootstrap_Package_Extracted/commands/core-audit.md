---
date: '2025-09-20T18:39:00Z'
last-tested: '2025-09-20T18:39:00Z'
generated_date: '2025-09-20T18:39:00Z'
checksum: core_audit_v1_0_0
tags: [audit, health-check, manifest]
category: audit
priority: high
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/core-audit.md
---
# `core-audit`

Version: 1.0.0

**DEPENDENCY**: `N5/core_manifest.json` must exist

Workflow: audit

Summary: Lightweight daily audit that engine-layer files (per core_manifest.json) exist, are non-empty, and remain git-tracked.

Tags: audit, manifest, health-check

## Inputs
(None)

## Outputs
- **report**: object - `{pass: bool, timestamp: epoch, issues: [string, ...]}`

## Exit Codes
- 0: all checks passed
- 1: any issue found or runtime error

## Side Effects
- writes: append-only entry to `runtime/audit/core_audit.log`

## Examples
```
N5: run core-audit
```

## Related Commands
- **hygiene-preflight**: fail-fast guard run before bulk operations
- **git-check**: git-diff and uncommitted audit
- **system-audit**: broader system diagnostics

## Implementation
- reads script: `N5/scripts/core_audit.py`
- uses core_manifest.json defined bill-of-materials
- performs: existence, min-size, git-tracked, regex presence, registry exists, append-only heuristic