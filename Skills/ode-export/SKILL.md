---
name: ode-export
description: |
  Export designated live workspace files to the n5os-ode GitHub repo with PII gating,
  validation, drift reporting, and install smoke testing. Allowlist-only — nothing
  flows in unless explicitly listed in ode_manifest.yaml.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0.0"
  created: "2026-02-18"
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: con_o9nkV9huRbIpeEGn
---

# Ode Export Pipeline

Sync live workspace files → n5os-ode repo. Allowlist-only manifest controls what's in scope.

## Quick Start

```bash
# See what's drifted
python3 Skills/ode-export/scripts/export.py --diff

# Preview what would change
python3 Skills/ode-export/scripts/export.py --dry-run

# Export changed files
python3 Skills/ode-export/scripts/export.py

# Export + smoke test install.sh
python3 Skills/ode-export/scripts/export.py --test

# First-time bulk sync
python3 Skills/ode-export/scripts/export.py --init

# Include trivial drifts
python3 Skills/ode-export/scripts/export.py --force
```

## Architecture

```
Live Workspace                     n5os-ode Repo
├── N5/scripts/foo.py ──────┐
├── N5/prefs/bar.md ────────┤
├── Skills/pulse/SKILL.md ──┤     ode_manifest.yaml
├── N5/scripts/secret.py    │     (allowlist)
│   (NOT in manifest) ──────┘         │
│                                     ▼
│                           ┌── Resolve globs ──┐
│                           │ Compare live/repo  │
│                           │ Filter threshold   │
│                           │ PII gate           │
│                           │ Copy changed       │
│                           │ Validate           │
│                           │ Smoke test (opt)   │
│                           └────────────────────┘
```

## Manifest

Edit `ode_manifest.yaml` to control what's exported:

- **exports**: Directory groups with explicit file lists or globs
- **repo_managed**: Files edited directly in-repo (docs/, .github/, LICENSE)
- **settings.pii_patterns**: Regex patterns that block export if matched

To add a new file to the export scope, add it to the appropriate group in `exports`.

## Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Preview without writing |
| `--init` | First-time bulk sync |
| `--diff` | Drift report only (no writes) |
| `--test` | Run install.sh smoke test after export |
| `--threshold N` | Skip files diverging by <N chars (default 50) |
| `--force` | Ignore threshold, sync everything in manifest |
| `--repo PATH` | Override repo path (default /tmp/n5os-ode) |

## Pipeline Stages

1. Load manifest → resolve globs → build file list
2. Compare live vs repo (SHA-256 + size delta)
3. Filter by threshold (unless `--force`)
4. PII gate (scan for personal patterns)
5. Copy changed files to repo
6. Run validate_repo.py on result
7. If `--test`: run install.sh in temp directory
8. Report: synced, skipped, blocked, stale repo-managed files

## Typical Workflow

```bash
# 1. Check drift
python3 Skills/ode-export/scripts/export.py --diff

# 2. Export with test
python3 Skills/ode-export/scripts/export.py --test

# 3. Review and commit
cd /tmp/n5os-ode
git diff --stat
git add -A && git commit -m "chore: sync from live"
git push
```
