# 🚨 URGENT: PII Breach Remediation Plan

**Date:** 2025-10-24 16:02 ET  
**Severity:** CRITICAL  
**Status:** ACTIVE BREACH

---

## BREACH SUMMARY

**Your personal information is currently public on GitHub:**
- Repository: `https://github.com/vrijenattawar/ZoATS`
- Exposed Data: Full resume with email (vsa6@cornell.edu) and phone (857-869-3264)
- Commits Containing PII: At least 2 (d5212ce, 1bc57d7)
- Files Tracked: 18 files containing "vrijen" including resume PDFs and parsed text

**Additional Exposed PII:**
- Other test candidates' resumes (Erika Underwood, Amanda Sachs, Alfred Sogja, Zihuan Nie)
- 119 total job-related files tracked in Git

---

## IMMEDIATE ACTIONS REQUIRED

### Option 1: Nuclear - Delete & Recreate Repository (FASTEST)
**Time:** 5 minutes  
**Pros:** Completely removes all history  
**Cons:** Loses all commit history

```bash
# 1. Delete remote repository (via GitHub web interface)
# 2. Re-initialize local repo
cd /home/workspace/ZoATS
rm -rf .git
git init
git add .
git commit -m "feat: Initial ZoATS system (sanitized)"
# 3. Create new GitHub repo and push
```

### Option 2: Git History Rewrite (THOROUGH)
**Time:** 15-30 minutes  
**Pros:** Preserves sanitized history  
**Cons:** More complex, requires force push

```bash
cd /home/workspace/ZoATS

# Install BFG Repo-Cleaner (faster than filter-branch)
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar -O /tmp/bfg.jar

# Remove all files matching patterns
java -jar /tmp/bfg.jar --delete-files "*.pdf" .
java -jar /tmp/bfg.jar --delete-files "*.docx" .
java -jar /tmp/bfg.jar --delete-folders "vrijen" .
java -jar /tmp/bfg.jar --delete-folders "candidates" --no-blob-protection .

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (DESTRUCTIVE - rewrites history)
git push --force --all
git push --force --tags
```

### Option 3: Make Repository Private (TEMPORARY MITIGATION)
**Time:** 1 minute  
**Pros:** Immediate privacy  
**Cons:** Data still exists in history

1. Go to: https://github.com/vrijenattawar/ZoATS/settings
2. Scroll to "Danger Zone"
3. Click "Change visibility" → "Make private"

**⚠️ This is NOT a complete fix - data remains in git history!**

---

## RECOMMENDED APPROACH

**Phase 1: Immediate (NOW)**
1. Make repository private (Option 3)
2. Prevent further commits

**Phase 2: Cleanup (Next 30 min)**
1. Run BFG Repo-Cleaner to remove PII from history (Option 2)
2. Force push cleaned history
3. Verify PII removed

**Phase 3: Prevention (Today)**
1. Strengthen .gitignore
2. Install pre-commit hook
3. Test protection measures

---

## DETAILED REMEDIATION SCRIPT

### Step 1: Make Private (IMMEDIATE)
```bash
# Via GitHub CLI (if installed)
gh repo edit vrijenattawar/ZoATS --visibility private

# Or via web: https://github.com/vrijenattawar/ZoATS/settings
```

### Step 2: Identify All PII Files
```bash
cd /home/workspace/ZoATS

# List all tracked candidate data
git ls-files | grep -E "(candidates|inbox_drop)" > /tmp/pii_files.txt

# Show sample
head -20 /tmp/pii_files.txt
```

### Step 3: Remove from Git History
```bash
cd /home/workspace/ZoATS

# Backup current state
tar -czf /home/workspace/.zoats-backup-$(date +%Y%m%d-%H%M%S).tar.gz .

# Method A: BFG (Recommended - Fast)
cd /tmp
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

cd /home/workspace/ZoATS
# Remove specific file patterns
java -jar /tmp/bfg-1.14.0.jar --delete-files "{*.pdf,*.docx,*.doc}" .
java -jar /tmp/bfg-1.14.0.jar --delete-folders "{candidates,inbox_drop}" --no-blob-protection .

# Clean up repository
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Method B: git-filter-repo (Alternative)
# pip3 install git-filter-repo
# git filter-repo --path-glob "jobs/*/candidates/**" --invert-paths
# git filter-repo --path-glob "jobs/*/inbox_drop/**" --invert-paths
```

### Step 4: Update .gitignore (BEFORE pushing)
```bash
cd /home/workspace/ZoATS

cat >> .gitignore << 'EOF'

# === CRITICAL PII PROTECTION ===
# NEVER commit candidate data or test resumes

# All candidate data (strict)
jobs/*/candidates/**
jobs/*/inbox_drop/**
!jobs/*/candidates/.gitkeep
!jobs/*/inbox_drop/.gitkeep

# Resume files (explicit)
**/*.pdf
**/*.docx
**/*.doc
**/*.rtf

# Test data containing V's information
**/vrijen*
**/Vrijen*
**/VRIJEN*
**/v_mostrecentresume*
**/attawar*
**/Attawar*

# Parsed resume text (contains PII)
jobs/*/candidates/*/parsed/**
jobs/*/candidates/*/raw/**
jobs/*/candidates/*/outputs/**

# Other PII patterns
**/vsa6@*
**/857-869-*
EOF

git add .gitignore
git commit -m "sec: Strengthen .gitignore - prevent PII commits"
```

### Step 5: Create Pre-Commit Hook
```bash
cd /home/workspace/ZoATS

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# ZoATS Pre-Commit Hook: Block PII commits

echo "🔒 Checking for PII in staged files..."

# Check for resume files
if git diff --cached --name-only | grep -E "\.(pdf|docx|doc|rtf)$" > /dev/null; then
  echo "❌ ERROR: Attempting to commit resume file!"
  echo "   Resume files contain PII and must never be committed."
  exit 1
fi

# Check for candidate data directories
if git diff --cached --name-only | grep -E "jobs/.*/candidates/" > /dev/null; then
  echo "❌ ERROR: Attempting to commit candidate data!"
  echo "   Candidate directories contain PII."
  exit 1
fi

# Check for V's name/info
if git diff --cached --name-only | grep -iE "(vrijen|attawar|vsa6@|857-869-)" > /dev/null; then
  echo "❌ ERROR: Attempting to commit test data with V's information!"
  exit 1
fi

# Check file contents for email/phone patterns
STAGED_FILES=$(git diff --cached --name-only)
for file in $STAGED_FILES; do
  if [ -f "$file" ]; then
    if grep -qE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" "$file" 2>/dev/null; then
      if [[ ! "$file" =~ \.(py|md|json|txt)$ ]] || grep -qE "vsa6@cornell|@example\.com" "$file"; then
        echo "⚠️  WARNING: File contains email pattern: $file"
        echo "   Review carefully before committing."
      fi
    fi
  fi
done

echo "✅ PII check passed"
exit 0
EOF

chmod +x .git/hooks/pre-commit

# Test the hook
echo "Testing pre-commit hook..."
touch test_vrijen.pdf
git add test_vrijen.pdf
git commit -m "test" 2>&1 | grep "ERROR"
git reset HEAD test_vrijen.pdf
rm test_vrijen.pdf
```

### Step 6: Force Push Cleaned History
```bash
cd /home/workspace/ZoATS

# Verify current status
git log --oneline | head -5
git ls-files | grep -E "(vrijen|candidates)" | wc -l  # Should be 0

# Force push (DESTRUCTIVE - point of no return)
git push --force origin main

# Verify remote is clean
git ls-remote --heads origin
```

### Step 7: Verify Cleanup
```bash
# Clone fresh copy to verify
cd /tmp
git clone https://github.com/vrijenattawar/ZoATS test-clone
cd test-clone

# Search for PII
git log --all --full-history --source --pretty=format: --name-only | \
  grep -iE "(vrijen|vsa6@|857-869-)" | wc -l
# Should output: 0

# Search all commits for email pattern
git log --all -S "vsa6@cornell" --pretty=format: | wc -l
# Should output: 0
```

---

## PREVENTION MEASURES

### Updated .gitignore (Comprehensive)
```gitignore
# === GENERATED/RUNTIME FILES ===
outbox/*.eml
logs/*.log
*.pyc
__pycache__/
.DS_Store

# === CRITICAL PII PROTECTION ===
# NEVER commit candidate resumes, parsed data, or test files

# Candidate data (blanket exclusion)
jobs/*/candidates/**
jobs/*/inbox_drop/**
!jobs/*/candidates/.gitkeep
!jobs/*/inbox_drop/.gitkeep

# Resume file types
**/*.pdf
**/*.docx
**/*.doc
**/*.rtf
**/*resume*.pdf
**/*resume*.docx
**/*cv*.pdf

# Parsed candidate data (contains PII)
jobs/*/candidates/*/parsed/text.md
jobs/*/candidates/*/parsed/fields.json
jobs/*/candidates/*/raw/**
jobs/*/candidates/*/outputs/**

# Test data with V's information
**/vrijen*
**/Vrijen*
**/VRIJEN*
**/v_mostrecentresume*
**/attawar*
**/Attawar*
**/ATTAWAR*

# Email patterns (safety net)
**/*vsa6@*
**/*857-869-*

# === KEEP STRUCTURE FILES ONLY ===
# These patterns allow structural files to be tracked
!jobs/*/.gitkeep
!jobs/*/README.md
!jobs/*/job_description.md
!jobs/*/rubric.json
!jobs/*/config.json
```

### Documentation Updates

**Add to README.md:**
```markdown
## 🔒 Security & Privacy

### PII Protection
This system handles sensitive candidate information. **NEVER commit:**
- Resume files (PDF, DOCX, DOC, RTF)
- Parsed candidate data (`parsed/`, `raw/`, `outputs/`)
- Test files containing real names, emails, or phone numbers

### Protected by Design
- `.gitignore` excludes all candidate data directories
- Pre-commit hook blocks PII commits
- Test jobs use synthetic data only

### For Developers
Before committing, run:
```bash
git status | grep -E "(candidates|inbox_drop|\.pdf|\.docx)"
# Should return nothing
```
```

**Create SECURITY.md:**
```markdown
# Security Policy

## Sensitive Data Handling

### What is Considered PII
- Candidate resumes and CVs
- Contact information (email, phone, address)
- Parsed candidate data (names, work history)
- Test data using real people's information

### Data Protection Measures
1. All candidate data stored in `.gitignore`d directories
2. Pre-commit hooks prevent accidental commits
3. Test data uses synthetic profiles only
4. Production deployments use environment variables for credentials

### Reporting a Security Issue
If you discover a security vulnerability, email: [REDACTED]

Do NOT create a public GitHub issue for security vulnerabilities.
```

---

## TESTING CHECKLIST

After remediation, verify:

- [ ] Repository is private (temporarily)
- [ ] `git ls-files | grep vrijen` returns nothing
- [ ] `git log --all -S "vsa6@cornell"` returns nothing  
- [ ] Clone fresh copy - no PII found in any commit
- [ ] Pre-commit hook blocks: `git add test.pdf && git commit`
- [ ] .gitignore verified: `git check-ignore -v jobs/test-job/candidates/test/resume.pdf`
- [ ] Test commit without PII succeeds
- [ ] Force push completed successfully

---

## POST-REMEDIATION ACTIONS

### Immediate (Today)
1. ✅ Make repo private
2. ✅ Clean git history
3. ✅ Strengthen .gitignore
4. ✅ Install pre-commit hook
5. ✅ Verify cleanup successful

### Short-term (This Week)
6. Create SECURITY.md
7. Update README with privacy guidelines
8. Generate synthetic test data (replace real resumes)
9. Set up GitHub secret scanning
10. Consider making repo public again (after verified clean)

### Long-term (Ongoing)
11. Regular audits: `git ls-files | grep -E "(candidates|pdf|docx)"`
12. Train collaborators on PII handling
13. Implement automated PII scanning in CI/CD
14. Use test fixtures instead of real resumes

---

## IF SOMETHING GOES WRONG

### Backup exists
```bash
ls -lh /home/workspace/.zoats-backup-*.tar.gz
```

### Restore from backup
```bash
cd /home/workspace
rm -rf ZoATS
tar -xzf .zoats-backup-YYYYMMDD-HHMMSS.tar.gz
cd ZoATS
git log --oneline | head -5  # Verify restoration
```

### Emergency contacts
- GitHub Support: https://support.github.com/
- Contact: [Your emergency contact]

---

## LESSONS LEARNED

### What Went Wrong
1. `.gitignore` had `jobs/*/candidates/*/` but files were added BEFORE .gitignore
2. No pre-commit hook to catch mistakes
3. Test data used real resumes instead of synthetic data
4. No awareness check before `git add .`

### Process Improvements
1. **Test data first:** Create synthetic profiles before testing
2. **Check before commit:** Always run `git status` and review changed files
3. **Hooks mandatory:** Pre-commit hook should be part of setup
4. **Regular audits:** Weekly check for PII in tracked files
5. **Private by default:** Start repos private, make public only when verified clean

---

## QUESTIONS FOR V

1. **Immediate action:** Which remediation option do you prefer? (Nuclear delete vs. BFG cleanup vs. Private only)
2. **Repository visibility:** OK to keep private permanently? Or need public for distribution?
3. **Test data:** Should I create synthetic test resumes to replace real ones?
4. **Git history:** OK to force-push rewritten history? (This will affect any collaborators)
5. **Monitoring:** Want GitHub secret scanning enabled? (Scans for exposed credentials)

---

**AWAITING YOUR GO-AHEAD TO EXECUTE REMEDIATION**

Recommend: **Option 3 (private) immediately, then Option 2 (BFG cleanup) within next hour**

