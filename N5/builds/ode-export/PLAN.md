---
created: 2026-02-18
last_edited: 2026-02-18
version: 2.0
provenance: con_o9nkV9huRbIpeEGn
---

# Ode Export Pipeline — Build Plan v2

## Objective

Create a skill that syncs designated live workspace files → n5os-ode repo with PII gating, validation, drift reporting, and install testing.

## Architecture Decision

**Allowlist-only manifest (Option B from strategy review):**
- Only explicitly listed files get exported
- Directory groups with glob patterns to reduce line count
- `repo_managed` section for files edited directly in repo
- Nothing flows in unless V adds it to the manifest

## Deliverables

### 1. `Skills/ode-export/SKILL.md`
Skill documentation.

### 2. `Skills/ode-export/scripts/export.py`
Main export script. Flags:
- `--dry-run` — show what would change, don't write
- `--init` — first-time bulk sync (structured commit msg)
- `--diff` — show live-vs-repo drift report
- `--test` — post-export smoke test (run install.sh in tmpdir)
- `--threshold N` — skip files diverging by <N chars (default 50)
- `--force` — ignore threshold, sync everything in manifest

Pipeline stages:
1. Load manifest → resolve globs → build file list
2. Compare live vs repo (hash + size delta)
3. Filter by threshold (unless --force)
4. PII gate (scan for personal patterns)
5. Copy changed files to repo
6. Run validate_repo.py on result
7. If --test: run install.sh smoke test in tmpdir
8. Report: files synced, skipped (trivial), PII blocked, repo-only staleness
9. Auto-increment version in CHANGELOG (if not --dry-run)

### 3. `Skills/ode-export/ode_manifest.yaml`
Allowlist manifest with:
- `exports` section: directory groups with glob includes
- `repo_managed` section: files managed directly in repo
- `pii_patterns` section: regex patterns to block
- `settings`: threshold default, repo path

## Level-Up Improvements (v2 additions)

| # | Improvement | Implementation |
|---|-------------|---------------|
| 1 | `--init` mode | Separate code path, structured commit msg |
| 2 | Repo-only staleness | Check mtime of repo_managed files, flag >60 days |
| 3 | `--test` smoke test | Run install.sh in /tmp/ode-test-XXXXX |
| 4 | `--threshold` filter | Default 50 chars, skip trivial drifts |
| 5 | `repo_managed` manifest | Complete scope document |

## Success Criteria

- [ ] `--dry-run` shows accurate diff without writing
- [ ] `--init` does clean bulk sync
- [ ] PII gate catches test patterns
- [ ] validate_repo.py passes after export
- [ ] `--test` smoke test runs install.sh successfully
- [ ] `--threshold` filters trivial drifts
- [ ] `--diff` shows full drift report including repo-only staleness
- [ ] Manifest covers all 236 current repo files via groups
- [ ] Script has logging, exit codes, error handling per build standards
