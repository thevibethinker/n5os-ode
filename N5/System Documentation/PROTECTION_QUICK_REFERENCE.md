# N5 File Protection - Quick Reference

**⚠️ READ THIS BEFORE MODIFYING PROTECTED FILES ⚠️**

---

## Protected Files (Never Overwrite Without Approval)

- `Documents/N5.md` - System entry point
- `N5/prefs/prefs.md` - System preferences
- `N5/config/commands.jsonl` - Command registry

---

## Mandatory Workflow (For AI Agents)

```
1. READ file first
2. SHOW user current content preview
3. GET explicit "APPROVED" from user
4. BACKUP automatically (system does this)
5. WRITE file
6. VERIFY success
```

---

## Quick Commands

### Backup & Recovery
```bash
# List backups
python3 N5/scripts/file_backup.py list

# Create manual backup
python3 N5/scripts/file_backup.py backup <file> "reason"

# Restore backup
python3 N5/scripts/file_backup.py restore <backup> <target>

# Check file status
python3 N5/scripts/file_watcher.py status
```

### System Health
```bash
# Quick health check
ls -la .git/hooks/pre-commit  # Hook exists?
python3 N5/scripts/file_backup.py list | head -5  # Backups?
head -30 N5/prefs/prefs.md  # Warning visible?
```

---

## If File Gets Overwritten

**Option 1: N5 Backup**
```bash
python3 N5/scripts/file_backup.py list Documents/N5.md
python3 N5/scripts/file_backup.py restore <backup> Documents/N5.md
```

**Option 2: Git History**
```bash
git log --oneline -10 -- Documents/N5.md
git show <commit>:Documents/N5.md > Documents/N5.md
```

---

## Full Documentation

See: `N5/System Documentation/FILE_PROTECTION_GUIDE.md`

**Incident Analysis:** `file '/home/.z/workspaces/con_rftEK15ZZ8An0qMc/n5_overwrite_incident_analysis.md'`

---

**Remember:** Multiple protections must fail for data loss. The system is redundant by design.
