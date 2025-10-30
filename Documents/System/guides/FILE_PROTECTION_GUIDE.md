# N5 File Protection System - User Guide

**Last Updated:** 2025-10-09  
**Status:** Active and Enforced

---

## Overview

The N5 File Protection System is a multi-layer defense mechanism designed to prevent accidental overwrites and data loss of critical system files. After two incidents of N5.md being accidentally overwritten (2025-09-20 and 2025-10-09), we've implemented comprehensive protection.

---

## Protection Layers

### Layer 1: Prominent Warning in prefs.md ✅

**Location:** Top of `N5/prefs/prefs.md`

All AIs loading the preferences file will see a critical warning at the top requiring:
- Read file first before any write
- Show user what will be lost
- Get explicit "APPROVED" confirmation
- Automatic backup (handled by system)

**Protected Files:**
- `Documents/N5.md` - System entry point
- `N5/prefs/prefs.md` - System preferences  
- `Recipes/recipes.jsonl` - Command registry

### Layer 2: Automatic Backup System ✅

**Location:** `N5/scripts/file_backup.py`

**Features:**
- Automatic timestamped backups before file modifications
- Keeps 5 most recent backups per file
- Backup manifest tracking in `/home/workspace/.n5_backups/`
- Command-line interface for manual backups and restores

**Usage:**

```bash
# Create backup manually
python3 N5/scripts/file_backup.py backup /path/to/file "reason"

# List all backups
python3 N5/scripts/file_backup.py list

# List backups for specific file
python3 N5/scripts/file_backup.py list /home/workspace/Documents/N5.md

# Check file before write (pre-flight check)
python3 N5/scripts/file_backup.py check /home/workspace/Documents/N5.md

# Restore backup
python3 N5/scripts/file_backup.py restore /path/to/backup.file /path/to/target
```

**Backup Location:** `/home/workspace/.n5_backups/`

### Layer 3: Git Pre-Commit Hook ✅

**Location:** `.git/hooks/pre-commit`

**Features:**
- Blocks commits with empty protected files
- Warns about files below minimum size thresholds
- Alerts on >50% size reductions
- Shows git diff stats for verification

**Minimum Sizes:**
- Documents/N5.md: 2000 bytes
- N5/prefs/prefs.md: 5000 bytes
- Recipes/recipes.jsonl: 1000 bytes
- N5/timeline/system-timeline.jsonl: 500 bytes

**Bypass (if absolutely necessary):**
```bash
git commit --no-verify -m "your message (explain why!)"
```

### Layer 4: File Protector Script ✅

**Location:** `N5/scripts/file_protector.py`

**Features:**
- Classifies files by protection level (HARD, MEDIUM, SOFT)
- Integrated with backup system
- Architectural validation

**Usage:**
```bash
# Check file classification
python3 N5/scripts/file_protector.py /path/to/file

# Validate write operation
python3 N5/scripts/file_protector.py /path/to/file write
```

### Layer 5: File System Watcher (Optional Background Daemon) ✅

**Location:** `N5/scripts/file_watcher.py`

**Features:**
- Real-time monitoring of protected files
- Detects emptied files, significant size reductions
- Automatic emergency backups on suspicious changes
- Alert logging to `/home/workspace/.n5_backups/watcher_alerts.jsonl`

**Usage:**

```bash
# Check current status
python3 N5/scripts/file_watcher.py status

# Run single check
python3 N5/scripts/file_watcher.py check

# View recent alerts
python3 N5/scripts/file_watcher.py alerts

# Start watching (foreground)
python3 N5/scripts/file_watcher.py start

# Start as background daemon
nohup python3 N5/scripts/file_watcher.py start > /dev/shm/file_watcher.log 2>&1 &

# Check if running
ps aux | grep file_watcher

# Stop daemon
pkill -f file_watcher.py
```

---

## Incident History

### Incident 1: 2025-09-20 04:37 UTC
- **File:** Documents/N5.md
- **Cause:** Accidental overwrite during timeline system creation
- **Result:** Recovered from git
- **Response:** Created file_protector.py v1.0

### Incident 2: 2025-10-09 04:49 UTC
- **File:** Documents/N5.md
- **Cause:** Unknown (no conversation artifacts)
- **Result:** Recovered from git
- **Response:** Implemented full multi-layer protection system

---

## For AI Agents

### Before Writing to Protected Files

**MANDATORY CHECKLIST:**

1. ✅ **Read file first** - Verify current content
   ```python
   current_content = Path(file_path).read_text()
   size = len(current_content)
   ```

2. ✅ **Check if file has content**
   ```python
   if size > 0:
       # File has content - requires approval
   ```

3. ✅ **Show user preview**
   ```python
   print(f"Current size: {size} bytes")
   print(f"First 10 lines:\n{preview}")
   ```

4. ✅ **Get explicit approval**
   ```
   User must type "APPROVED" to proceed
   ```

5. ✅ **Create backup automatically**
   ```bash
   python3 N5/scripts/file_backup.py backup <file_path> <operation>
   ```

6. ✅ **Verify write succeeded**
   ```python
   new_size = Path(file_path).stat().st_size
   assert new_size > 0
   ```

### Never Do This

❌ **Direct overwrite without reading first:**
```python
# WRONG - Don't do this!
create_or_rewrite_file("/home/workspace/Documents/N5.md", new_content)
```

✅ **Correct approach:**
```python
# Read current content first
current = read_file("/home/workspace/Documents/N5.md")

# Show user what will be replaced
print(f"Current content: {len(current)} bytes")
print("Preview:", current[:500])

# Get explicit approval
print("Type APPROVED to proceed")
# Wait for user confirmation

# Create backup
run_bash_command("python3 N5/scripts/file_backup.py backup /home/workspace/Documents/N5.md 'planned update'")

# Then proceed with write
create_or_rewrite_file("/home/workspace/Documents/N5.md", new_content)
```

---

## Recovery Procedures

### If File is Accidentally Overwritten

**Option 1: Restore from N5 Backup**
```bash
# List available backups
python3 N5/scripts/file_backup.py list /home/workspace/Documents/N5.md

# Restore specific backup
python3 N5/scripts/file_backup.py restore \
  /home/workspace/.n5_backups/Documents_N5.md.20251009_054435.backup \
  /home/workspace/Documents/N5.md
```

**Option 2: Restore from Git**
```bash
# Find last good commit
git log --oneline -10 -- Documents/N5.md

# View file from specific commit
git show <commit-hash>:Documents/N5.md

# Restore file
git show <commit-hash>:Documents/N5.md > Documents/N5.md
```

**Option 3: Check File Watcher Alerts**
```bash
# View recent alerts (may have saved previous version)
python3 N5/scripts/file_watcher.py alerts
```

### If Git Hook Blocks Your Commit

1. **Verify the file is not actually empty:**
   ```bash
   ls -lh Documents/N5.md
   cat Documents/N5.md | head -10
   ```

2. **If file is legitimately empty, investigate why:**
   ```bash
   git log --oneline -5 -- Documents/N5.md
   git diff HEAD -- Documents/N5.md
   ```

3. **Restore from backup if needed** (see above)

4. **If intentional, document in commit message and bypass:**
   ```bash
   git commit --no-verify -m "Intentional restructure: reason..."
   ```

---

## Maintenance

### Weekly
- Review backup inventory: `python3 N5/scripts/file_backup.py list`
- Check file watcher alerts: `python3 N5/scripts/file_watcher.py alerts`

### Monthly
- Verify git hooks are still active: `ls -la .git/hooks/pre-commit`
- Test backup/restore procedure
- Review incident log in system timeline

### After System Updates
- Verify file paths are still correct in all scripts
- Test each protection layer independently
- Run full integration test

---

## System Health Check

Run this to verify all protection layers are active:

```bash
# Check backup system
python3 N5/scripts/file_backup.py list | head -5

# Check git hook exists and is executable
ls -la .git/hooks/pre-commit

# Check file protector
python3 N5/scripts/file_protector.py /home/workspace/Documents/N5.md

# Check file watcher status
python3 N5/scripts/file_watcher.py status

# Verify prefs warning is present
head -50 N5/prefs/prefs.md | grep "CRITICAL FILE PROTECTION"
```

---

## Related Files

- **Analysis:** `/home/.z/workspaces/con_rftEK15ZZ8An0qMc/n5_overwrite_incident_analysis.md`
- **Timeline Entry:** `N5/timeline/system-timeline.jsonl` (2025-10-09)
- **Protection Policy:** `N5/prefs/system/file-protection.md`
- **Backup Scripts:** `N5/scripts/file_backup.py`, `N5/scripts/file_watcher.py`
- **Git Hook:** `.git/hooks/pre-commit`

---

## Questions?

If you experience issues or have questions about the file protection system:
1. Review this guide
2. Check the incident analysis document
3. Review system timeline for context
4. Test each protection layer individually

**Remember:** Multiple failures must occur simultaneously for data loss. The system is designed with redundancy.

## Full Documentation

See: `N5/System Documentation/FILE_PROTECTION_GUIDE.md`

**Quick Reference:** `file 'N5/System Documentation/protection-quick-ref.md'`

**Incident Analysis:** `file 'Documents/Archive/2025-10-09-N5-Protection/incident_analysis.md'`
