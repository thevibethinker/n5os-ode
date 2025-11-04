# ⚠️ CRITICAL PRODUCTION SERVICE - DO NOT DELETE

## Arsenal Productivity Dashboard

**Status:** PRODUCTION - ACTIVELY USED  
**Service:** `productivity-dashboard` (svc_J6eAPxM04_4)  
**URL:** https://productivity-dashboard-va.zocomputer.io  
**Last Stable:** 2025-11-03

### Critical Files

1. **index.tsx** - Main dashboard application (WORKING VERSION - DO NOT MODIFY)
2. **productivity_tracker.db** - Database at `/home/workspace/productivity_tracker.db`
3. **sync_gmail.py** - Email sync script

### Protection Measures

- ✅ Git committed (commit: 70f7ec4a)
- ✅ Database backed up to `N5/backups/productivity-dashboard/`
- ✅ Service registered and auto-restart enabled
- ✅ This directory protected by n5_protect.py

### Recovery Instructions

If dashboard breaks:
```bash
# Restore code from git
cd /home/workspace && git checkout Sites/productivity-dashboard/index.tsx

# Restore database from backup
cp /home/workspace/N5/backups/productivity-dashboard/productivity_tracker.db /home/workspace/

# Restart service
# Via Zo: update service with new RESTART timestamp
```

### Database Location

**CRITICAL:** Database MUST remain at `/home/workspace/productivity_tracker.db`

Do NOT move to:
- ❌ `/home/workspace/Records/Personal/`
- ❌ `/home/workspace/N5/data/`
- ❌ Any other location

### Last Incident: 2025-11-03
Database was wiped 3 times. Root cause: cleanup scripts moving/deleting loose .db files.

**DO NOT RUN cleanup on workspace root without excluding this file.**
