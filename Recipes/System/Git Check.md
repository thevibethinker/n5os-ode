---
description: 'Blocks unsafe commits by detecting:'
tags:
- git
- audit
- safety
- pre-commit
---
# `git-check`

Version: 2.0.0

Summary: Comprehensive pre-commit audit for staged Git changes - prevents overwrites, data loss, and credential leaks

Aliases: audit-changes, check-staged

Workflow: safety

Tags: git, audit, safety, pre-commit, protected-files

## Purpose

Blocks unsafe commits by detecting:
- Protected file modifications (commands.jsonl, schemas, Knowledge, Lists)
- Significant deletions (>50 lines, >70% ratio)
- Sensitive credentials (API keys, tokens, passwords)
- Large files (>1MB)
- Empty file overwrites
- Binary file rewrites

## Exit Codes

- `0` = Clean, safe to commit
- `1` = Issues found, BLOCKS commit (review required)
- `2` = Git error, cannot audit
- `3` = Invalid repository state

## Usage

### Standard Check
```bash
command N5/commands/git-check.md
```

### Dry-Run Mode
```bash
python3 N5/scripts/n5_git_check.py --dry-run
```

### Bypass (after review)
```bash
git commit --no-verify
```

## Outputs
- **report** : text — Comprehensive audit report with severity levels
- **exit_code** : 0/1/2/3 — Automation-friendly status

## Protected Patterns (18 total)

### Core System Configs
- `N5/config/commands.jsonl`
- `N5/config/*.json`
- `N5/schemas/*.json`
- `N5/prefs/**/*.json`

### Architectural Knowledge
- `Knowledge/architectural/**/*.md`
- `Knowledge/architectural/principles/*.md`

### Action Lists
- `Lists/index.jsonl`
- `Lists/schemas/*.json`
- `Lists/*.jsonl`

### Secrets & Credentials
- `**/.env*`
- `**/secrets/**`
- `N5/config/credentials/**`
- `**/*_credentials.json`

### Critical Components
- `N5/intelligence/*.json`
- `Knowledge/crm/individuals/index.jsonl`

## Detection Features

### 1. Quantitative Deletion Threshold
Flags: >50 lines deleted AND >70% of changes are deletions
```
Example: 10 adds, 150 dels → 93.75% deletions → ⚠️  WARNING
```

### 2. Sensitive Data Scanner
Scans content for:
- Private keys, API keys, passwords, tokens
- OpenAI keys (sk-...), AWS keys (AKIA...), GitHub tokens (ghp_...)
- Smart false-positive reduction (skips pattern definitions, comments, regex strings)

### 3. Large File Detection
Threshold: 1MB (1,048,576 bytes)

### 4. Empty File Detection
Critical: Files with 0 bytes (potential overwrite bugs)

### 5. Binary Overwrite Detection
Flags complete binary file rewrites

### 6. Repository State Verification
Checks for valid git repo, no merge conflicts

## Examples
```bash
# Standard check
N5: run git-check

# Dry-run (preview checks)
N5: run git-check --dry-run

# After reviewing issues, commit anyway
git commit --no-verify -m "Reviewed and approved"
```

## Failure Modes
- **Exit 3:** Not in git repository or unmerged files
- **Exit 2:** Git command errors
- **Exit 1:** Issues detected (see report)
- **False positives:** Pattern definition files auto-skipped

## Related Components

**Scripts**: 
- `file N5/scripts/git_change_checker_v2.py` — Main checker
- `file N5/scripts/n5_git_check.py` — Wrapper

**Documentation**: `file N5/scripts/README_git_check_v2.md` 

**Related Commands**: [`docgen`](../commands/docgen.md), [`index-update`](../commands/index-update.md)

**Principles Applied**: P5 (Anti-Overwrite), P7 (Dry-Run), P11 (Failure Modes), P15 (Complete), P16 (Accuracy), P18 (Verification), P19 (Error Handling)

## Side Effects
None (read-only audit)

## Inputs
- **--dry-run** (optional) : Preview checks without executing

## Configuration

Edit `N5/scripts/git_change_checker_v2.py`:
- `DELETION_THRESHOLD`: min_lines, min_ratio
- `LARGE_FILE_THRESHOLD_MB`: 1 (default)
- `PROTECTED_PATTERNS`: list of glob patterns
- `SENSITIVE_PATTERNS`: list of (regex, name) tuples

## Integration

### Git Hook (Automatic)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python3 N5/scripts/n5_git_check.py
exit $?
```

Make executable: `chmod +x .git/hooks/pre-commit`

## Version History
- **2.0.0** (2025-10-13): Comprehensive rewrite with exit codes, quantitative thresholds, secrets scanning, 6 check categories
- **1.0.0** (2025-09-20): Initial version with basic checks
