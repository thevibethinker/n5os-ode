# Git Check v2 - Comprehensive Change Auditor

**Version:** 2.0.0  
**Date:** 2025-10-13  
**Script:** `N5/scripts/git_change_checker_v2.py`

---

## Purpose

Comprehensive pre-commit audit for staged Git changes to prevent:
- Accidental overwrite of protected files
- Data loss through large deletions
- Committing sensitive credentials
- Large file bloat
- Empty file overwrites

---

## Exit Codes

- `0` = Clean, safe to commit
- `1` = Issues found, review required (BLOCKS commit)
- `2` = Git error, cannot audit
- `3` = Invalid repository state

---

## Features

### 1. Protected File Detection

Flags modifications to critical system files:

**Core Configs:**
- `N5/config/commands.jsonl`
- `N5/config/*.json`
- `N5/schemas/*.json`

**Architectural Knowledge:**
- `Knowledge/architectural/**/*.md`
- `Knowledge/architectural/principles/*.md`

**Action Lists:**
- `Lists/index.jsonl`
- `Lists/schemas/*.json`
- `Lists/*.jsonl`

**Secrets & Credentials:**
- `**/.env*`
- `**/secrets/**`
- `N5/config/credentials/**`
- `**/*_credentials.json`

**Critical Components:**
- `N5/intelligence/*.json`
- `N5/stakeholders/index.jsonl`

**Severity Levels:**
- 🚨 CRITICAL: `.git/**`, secrets, credentials, `.env`
- ⚠️  WARNING: Other protected patterns

---

### 2. Quantitative Deletion Threshold

**Threshold:** >50 lines deleted AND >70% of changes are deletions

**Example:**
```
File: 10 additions, 150 deletions
Total: 160 changes
Ratio: 150/160 = 93.75% deletions
Result: ⚠️  WARNING (exceeds threshold)
```

**Rationale:** Prevents accidental massive data loss while allowing normal refactoring.

---

### 3. Sensitive Data Scanning

Scans file contents for:
- Private keys: `-----BEGIN .* PRIVATE KEY-----`
- API keys: `api_key = <value>`
- Passwords: `password = <value>`
- Tokens: `token = <value>`
- OpenAI keys: `sk-...`
- AWS access keys: `AKIA...`
- GitHub tokens: `ghp_...`

**Smart Detection:**
- Skips pattern definition files (this script itself)
- Ignores regex pattern strings (`r'...'`)
- Ignores comments (`# password = ...`)
- Skips binary files
- Skips files >1MB

---

### 4. Large File Detection

**Threshold:** 1MB (1,048,576 bytes)

Flags files that may bloat repository:
```
⚠️  media/video.mp4: Large file (25.3MB)
```

---

### 5. Empty File Detection

🚨 CRITICAL: Detects empty files (0 bytes) that may indicate overwrite bugs:
```
🚨 CRITICAL: N5/config/commands.jsonl is now empty (potential data loss)
```

---

### 6. Binary File Overwrite Detection

Detects complete binary file rewrites:
```
⚠️  images/logo.png: Binary file completely rewritten
```

---

## Usage

### Standard Check
```bash
cd /home/workspace
python3 N5/scripts/n5_git_check.py
```

### Dry-Run Mode
```bash
python3 N5/scripts/n5_git_check.py --dry-run
```

### Via Command
```markdown
command N5/commands/git-check.md
```

---

## Configuration

Edit `N5/scripts/git_change_checker_v2.py`:

```python
DELETION_THRESHOLD = {
    'min_lines': 50,      # Minimum lines deleted
    'min_ratio': 0.7      # 70% of changes must be deletions
}

LARGE_FILE_THRESHOLD_MB = 1

PROTECTED_PATTERNS = [
    'N5/config/commands.jsonl',
    # Add more patterns...
]

SENSITIVE_PATTERNS = [
    (r'pattern', 'Name'),
    # Add more patterns...
]
```

---

## Example Output

### Clean Repository
```
2025-10-13T21:44:14Z INFO Verifying git repository state...
2025-10-13T21:44:14Z INFO Git repository root: /home/workspace
2025-10-13T21:44:14Z INFO Retrieving staged files...
2025-10-13T21:44:14Z INFO Found 2 staged files
2025-10-13T21:44:14Z INFO Checking protected files...
2025-10-13T21:44:14Z INFO Checking for empty files...
2025-10-13T21:44:14Z INFO Scanning for sensitive data...
2025-10-13T21:44:14Z INFO Checking large files...
2025-10-13T21:44:14Z INFO Checking binary overwrites...
2025-10-13T21:44:14Z INFO Checking for significant deletions...
2025-10-13T21:44:14Z INFO ✅ No issues detected - safe to commit
```

### Issues Found
```
2025-10-13T21:44:14Z WARNING ❌ Found 3 issue(s) - REVIEW REQUIRED

============================================================
GIT CHECK FAILED - Issues detected:
============================================================
🚨 CRITICAL: Protected file staged: N5/config/commands.jsonl
⚠️  N5/scripts/large_file.zip: Large file (5.2MB)
🚨 CRITICAL: config/.env contains potential API key
============================================================

Review these changes before committing.
To commit anyway: git commit --no-verify
```

---

## Bypass Check

If you've reviewed changes and want to commit anyway:

```bash
git commit --no-verify
```

**⚠️  Use with caution!**

---

## Integration with Git Hooks

To automatically run on every commit, create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python3 N5/scripts/n5_git_check.py
exit $?
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Principles Applied

- **P5 (Anti-Overwrite):** Protected file checks
- **P7 (Dry-Run):** `--dry-run` flag
- **P11 (Failure Modes):** Exit codes for automation
- **P15 (Complete):** All 6 check categories implemented
- **P16 (Accuracy):** Quantitative thresholds, not speculation
- **P18 (Verification):** State checks before auditing
- **P19 (Error Handling):** Comprehensive try-catch, logging

---

## Version History

### v2.0.0 (2025-10-13)
- ✅ Exit code semantics (0/1/2/3)
- ✅ Quantitative deletion threshold (50 lines, 70% ratio)
- ✅ Protected file patterns (18 patterns)
- ✅ Large file detection (1MB threshold)
- ✅ Sensitive data scanning (8 patterns)
- ✅ Binary overwrite detection
- ✅ Empty file detection
- ✅ Dry-run mode
- ✅ State verification
- ✅ Comprehensive logging
- ✅ Smart false-positive reduction

### v1.0.0 (2025-09-20)
- Basic checks: empty files, deletions (rough heuristic)
- No exit codes, no protection, no secrets scanning

---

## Troubleshooting

**"Not in a git repository"**
- Ensure you're in `/home/workspace` or a subdirectory
- Check that `.git` directory exists

**"Unmerged files detected"**
- Resolve merge conflicts first: `git status`

**False positives for secrets**
- Pattern definition files are automatically skipped
- Regex patterns (`r'...'`) are ignored
- Add file to exclusion logic if needed

**Protected file warning for legitimate change**
- Review the change carefully
- If intentional, commit with `--no-verify`

---

## Future Enhancements

- [ ] Config file for patterns (vs. hard-coded)
- [ ] Whitelist for approved large files
- [ ] Integration with CI/CD pipelines
- [ ] JSON/YAML output format for automation
- [ ] Repository-specific rules (`.gitcheck.yml`)
- [ ] Incremental checks (only changed lines)

---

**Maintained by:** N5 System  
**Questions:** See `file Knowledge/architectural/architectural_principles.md`
