# N5OS Lite Troubleshooting Guide

**Version:** 1.2.2  
**Purpose:** Common issues and solutions

---

## 🔍 Quick Diagnostics

Run health check first:
```bash
python3 tests/system_health_check.py
```

---

## Common Issues

### 1. ModuleNotFoundError

**Symptom:**
```
ModuleNotFoundError: No module named 'n5_safety'
```

**Solution:**
```bash
# Check if all scripts present
ls -1 scripts/*.py | wc -l  # Should be 18+

# Missing scripts? Re-extract package
tar -xzf n5os-lite-v1.2.2-COMPLETE.tar.gz
```

**Files needed:**
- n5_safety.py
- executable_manager.py
- direct_ingestion_mechanism.py
- conversation_registry.py

---

### 2. Schema Validation Errors

**Symptom:**
```
ValidationError: 'name' is a required property
```

**Cause:** Script using old field names

**Solution:**
```bash
# Check your script uses correct fields
grep -n "title.*body" scripts/n5_lists_add.py  # Should be empty
grep -n "name.*description" scripts/n5_lists_add.py  # Should exist
```

**Correct format:**
```python
item = {
    "name": "My Tool",           # NOT "title"
    "description": "What it does",  # NOT "body"
    "status": "active"           # NOT "open"
}
```

---

### 3. Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'scripts/n5_lists_add.py'
```

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.py bootstrap.sh setup.sh

# Or run with python3
python3 scripts/n5_lists_add.py --help
```

---

### 4. Directory Not Found

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: '.n5os/lists'
```

**Solution:**
```bash
# Run bootstrap to create structure
./bootstrap.sh

# Or manually create
mkdir -p .n5os/{lists,personas,config}
mkdir -p {Prompts,Knowledge,Documents,Inbox,Lists}
```

---

### 5. Invalid JSON in Lists

**Symptom:**
```
json.JSONDecodeError: Expecting property name enclosed in double quotes
```

**Solution:**
```bash
# Validate list file
python3 scripts/validate_list.py Lists/tools.jsonl

# Fix issues automatically
python3 scripts/validate_list.py Lists/tools.jsonl --fix
```

---

### 6. Persona Not Found

**Symptom:**
```
Warning: Persona 'builder' not found, using default
```

**Solution:**
```bash
# Check personas installed
ls -1 personas/*.yaml

# Re-run setup if missing
./setup.sh
```

---

### 7. State File Corruption

**Symptom:**
```
Session state file appears corrupted or empty
```

**Solution:**
```bash
# Backup and reinitialize
cp SESSION_STATE.md SESSION_STATE.md.backup
python3 scripts/session_state_manager.py init --convo-id <ID>
```

---

### 8. Import Errors with Relative Paths

**Symptom:**
```
ImportError: attempted relative import with no known parent package
```

**Solution:**
```bash
# Run from workspace root
cd /home/workspace
python3 .n5os/scripts/n5_lists_add.py ...

# Or add to PYTHONPATH
export PYTHONPATH="/home/workspace/.n5os/scripts:$PYTHONPATH"
```

---

### 9. Git Integration Issues

**Symptom:**
```
fatal: not a git repository
```

**Solution:**
```bash
# Initialize git (optional)
cd /home/workspace
git init
git add .n5os/ Prompts/ Knowledge/
git commit -m "Initialize N5OS Lite"
```

---

### 10. Conversation Registry Database Locked

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Wait for other operations to complete, or
# Check for hanging processes
ps aux | grep conversation_registry

# If needed, remove lock
rm N5/data/conversations.db-journal
```

---

## Performance Issues

### Slow Script Execution

**Check:**
1. Large list files (>10MB)? Split them
2. Many artifacts in conversation? Archive old ones
3. Python version? Need 3.10+

**Solutions:**
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Profile script
time python3 scripts/n5_lists_find.py --query "test"

# Optimize lists
python3 scripts/n5_lists_health_check.py
```

---

## Installation Issues

### Bootstrap Fails

**Solution:**
```bash
# Check requirements
python3 --version  # 3.10+
which tar          # Should exist
which chmod        # Should exist

# Run with verbose output
bash -x bootstrap.sh 2>&1 | tee bootstrap.log
```

### Tests Fail

**Expected:** Some tests may fail in fresh environment

**Critical tests to pass:**
- Directory structure exists
- Scripts are executable
- Basic list operations work
- Schema validation works

**Run minimal test:**
```bash
# Quick smoke test
python3 scripts/validate_list.py --help  # Should show help
python3 scripts/n5_lists_add.py --dry-run --name "Test" --type "tool" --description "Test tool"
```

---

## Getting Help

### Self-Help Checklist

1. ✅ Read `QUICKSTART.md`
2. ✅ Run `system_health_check.py`
3. ✅ Check `ASSUMPTIONS.md` for dependencies
4. ✅ Review `INSTALLATION.md` for setup steps
5. ✅ Try `QUICKREF.md` for common patterns

### Still Stuck?

**Gather diagnostics:**
```bash
# System info
python3 --version
uname -a
pwd

# File structure
tree -L 2 .n5os/
ls -la scripts/

# Health check
python3 tests/system_health_check.py --verbose > health.log
```

**Check documentation:**
- `ARCHITECTURE.md` - System design
- `ASSUMPTIONS.md` - Dependencies
- `CRITICAL_FIXES_v1.2.2.md` - Recent fixes

---

## Known Limitations

### Current Version (v1.2.2)

1. **No Web UI** - Command-line only
2. **No Cloud Sync** - Local filesystem only
3. **No Multi-User** - Single user per installation
4. **No Real-Time Collaboration** - Sequential only
5. **Limited Error Recovery** - Manual intervention needed
6. **No Automated Backups** - User responsible

### Workarounds

1. Web UI → Use AI assistant directly
2. Cloud Sync → Use file syncing (Syncthing, etc)
3. Multi-User → Each user installs separately
4. Collaboration → Use git for sharing
5. Error Recovery → See troubleshooting above
6. Backups → Schedule via cron/scheduled tasks

---

## Principle-Based Debugging

When debugging, apply principles:

**P15: Complete Before Claiming**
- Don't assume it works, verify it

**P16: Accuracy Over Sophistication**
- Simple reproduction > complex speculation

**P19: Error Handling**
- Check logs, capture full error messages

**P21: Document Assumptions**
- What did you expect vs. what happened?

---

**Most issues are environment or setup related. Follow the installation guide carefully.**

*Troubleshooting Guide v1.2.2 | 2025-11-03*
