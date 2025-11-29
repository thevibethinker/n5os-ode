---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Arsenal Productivity Dashboard - Protection & Recovery

## 🔒 Protection Layers

### 1. Git Version Control
- **Commit:** a1e5ef0a (2025-11-03)
- **Files tracked:**
  - `Sites/productivity-dashboard/index.tsx` (main app)
  - `Sites/productivity-dashboard/sync_gmail.py` (email sync)
  - `Sites/productivity-dashboard/DO_NOT_DELETE.md` (protection doc)

### 2. Database Protection
- **Location:** `/home/workspace/productivity_tracker.db` (MUST NOT MOVE)
- **Marker file:** `/.productivity_db_protected` (warns cleanup scripts)
- **Backup location:** `/home/workspace/N5/backups/productivity-dashboard/`
- **Backup frequency:** Daily via Daily File Guardian
- **Retention:** Last 30 days

### 3. Service Registration
- **Service ID:** `svc_J6eAPxM04_4`
- **Label:** `productivity-dashboard`
- **Port:** 3000
- **URL:** https://productivity-dashboard-va.zocomputer.io
- **Auto-restart:** Enabled

### 4. Directory Protection
- **Protected by:** n5_protect.py (Sites/productivity-dashboard directory)
- **Reason:** Hosts deployed web applications

## 🚨 What Went Wrong (Nov 3, 2025)

### Incident Timeline
1. **First wipe:** Database moved to `Records/Personal/`
2. **Second wipe:** Database recreated empty at root
3. **Third wipe:** Git checkout reverted working code

### Root Causes
- Cleanup scripts moving loose `.db` files
- Git checkout without checking current version
- No backup/protection system in place

## ✅ Current Protection Status

- ✅ Code committed to git
- ✅ Database backed up daily
- ✅ Protection markers in place
- ✅ Service auto-restart enabled
- ✅ Documentation created
- ✅ Recovery procedures documented

## 🔧 Recovery Procedures

### If Dashboard Shows Old Version

```bash
cd /home/workspace
git log --oneline Sites/productivity-dashboard/index.tsx | head -5
git checkout a1e5ef0a -- Sites/productivity-dashboard/index.tsx
# Restart service via Zo or update_user_service
```

### If Database is Missing/Empty

```bash
# Find latest backup
ls -lt /home/workspace/N5/backups/productivity-dashboard/

# Restore (replace DATE with actual backup date)
cp /home/workspace/N5/backups/productivity-dashboard/productivity_tracker_DATE.db \
   /home/workspace/productivity_tracker.db

# Verify
sqlite3 /home/workspace/productivity_tracker.db "SELECT COUNT(*) FROM daily_stats"
```

### If Service is Down

```bash
# Check service status
curl -s -o /dev/null -w "%{http_code}" https://productivity-dashboard-va.zocomputer.io

# Check logs
tail -50 /dev/shm/productivity-dashboard_err.log

# Restart via Zo or:
# update_user_service with new RESTART timestamp
```

## 📋 Features Implemented (Nov 3, 2025)

1. **7-Day View** - Shows 2 days back, today (highlighted), 4 days forward
2. **Arsenal Status Hierarchy** - Dynamic level based on 7-day RPI average:
   - Youth Player (0-60)
   - Reserve (60-80)
   - Squad Player (80-100)
   - First Team (100-125)
   - Star Player (125-150)
   - Club Legend (150+)
3. **100% Reference Line** - Vertical line at midpoint of all bars
4. **Color-Coded Bars:**
   - Red (<75) = Behind
   - Orange (75-99) = Catch Up
   - Blue (100-124) = Meeting
   - Green (125-149) = Top
   - Gold (150+) = Invincible

## 🔗 Related Files

- Dashboard code: file 'Sites/productivity-dashboard/index.tsx'
- Database: `/home/workspace/productivity_tracker.db`
- Backup script: file 'N5/scripts/backup_productivity_db.sh'
- Service protection: file 'Sites/productivity-dashboard/DO_NOT_DELETE.md'

## 📞 Support

For issues, reference this document and the protection markers.
All changes to this system should be documented here.
