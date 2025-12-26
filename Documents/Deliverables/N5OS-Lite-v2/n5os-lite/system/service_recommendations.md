# N5OS Lite Service Recommendations

**Version:** 1.0  
**Purpose:** Recommended services and integrations for N5OS Lite  
**Status:** Optional enhancements

---

## Overview

N5OS Lite works standalone but can be enhanced with external services. This document recommends integrations based on use case.

**Core Principle:** Start minimal. Add services only when needed.

---

## No Services Required

**N5OS Lite runs completely standalone:**
- No databases required
- No external APIs needed  
- No cloud services necessary
- Self-contained operation

**Everything works with:**
- File system storage (JSONL, MD, YAML)
- Local scripts (Python, Bash)
- Your AI assistant

---

## Recommended Integrations (Optional)

### For Knowledge Management

**Git (Highly Recommended)**
```bash
# Initialize version control
cd /home/workspace
git init
git add .
git commit -m "Initial N5OS Lite setup"
```

**Benefits:**
- Version history
- Rollback capability  
- Collaboration support
- Backup via remote

**Setup:** Built into most systems

---

### For Automation

**Cron / Scheduled Tasks (Recommended)**

Schedule recurring workflows:
```cron
# Daily health check
0 9 * * * cd /home/workspace && python3 tests/system_health_check.py

# Weekly list maintenance  
0 0 * * 0 cd /home/workspace && python3 scripts/validate_list.py Lists/*.jsonl
```

**Benefits:**
- Automated maintenance
- Regular health checks
- Scheduled updates

**Setup:** Platform-dependent (see examples/scheduled_tasks.md)

---

### For File Sync (Optional)

**Syncthing / Dropbox / Drive**

Sync workspace across devices:
```
/home/workspace → Cloud → Other devices
```

**Benefits:**
- Multi-device access
- Automatic backup
- Real-time sync

**Setup:** Install sync client, point to workspace

**Warning:** Use with `.n5protected` carefully to avoid sync conflicts

---

### For Advanced Users

**Python Virtual Environment (Recommended)**

```bash
# Create isolated environment
python3 -m venv /home/workspace/.venv
source /home/workspace/.venv/bin/activate
pip install -r requirements.txt
```

**Benefits:**
- Isolated dependencies
- Version control
- Clean uninstall

**Setup:** Standard Python practice

---

**Docker (Advanced)**

Containerize N5OS Lite:
```dockerfile
FROM python:3.12-slim
WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "scripts/system_health_check.py"]
```

**Benefits:**
- Reproducible environment
- Easy deployment
- Isolation

**Setup:** Requires Docker knowledge

---

## Service Setup Priority

### Tier 1: Essential (Recommended for all)
1. **Git** - Version control
2. **Scheduled Tasks** - Automation (if supported)

### Tier 2: Productivity (Recommended for regular use)
3. **File Sync** - Multi-device access
4. **Python venv** - Dependency management

### Tier 3: Advanced (Power users)
5. **Docker** - Containerization
6. **CI/CD** - Automated testing
7. **Monitoring** - System health tracking

---

## Integration Patterns

### Git Workflow

```bash
# Daily workflow
git add .
git commit -m "Daily update: $(date +%Y-%m-%d)"
git push origin main

# Before major changes
git checkout -b feature/new-system
# ... make changes ...
git checkout main
git merge feature/new-system
```

### Scheduled Maintenance

```bash
#!/bin/bash
# daily-maintenance.sh

# Health check
python3 tests/system_health_check.py

# Validate lists
python3 scripts/validate_list.py Lists/*.jsonl

# Generate docs
# (Tell AI: "generate documentation")

# Commit changes
git add .
git commit -m "Automated maintenance: $(date)"
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Create timestamped archive
tar -czf "backups/n5os-$(date +%Y%m%d).tar.gz" \
    Lists/ \
    Knowledge/ \
    Prompts/ \
    Personal/ \
    .n5os/

# Keep last 30 days
find backups/ -name "n5os-*.tar.gz" -mtime +30 -delete
```

---

## What NOT to Install

**Avoid unnecessary complexity:**
- ❌ Databases (JSONL files work great)
- ❌ Web servers (unless hosting)
- ❌ Message queues (overkill for single-user)
- ❌ Container orchestration (K8s, etc.)
- ❌ Microservices (keep it simple)

**Remember:** N5OS Lite is designed to work WITHOUT external services.

---

## Platform-Specific Notes

### Zo Computer
- Built-in scheduled tasks
- Native file sync available
- Git pre-installed
- No additional setup needed

### Local Machine
- Use cron for scheduling
- Configure backup solution
- Install Git if missing

### Cloud VM
- Set up automated backups
- Configure firewall if exposing services
- Use systemd for service management

---

## Testing Integrations

### After Adding Service

1. **Health check:** Run system_health_check.py
2. **Validate:** Ensure core workflows still work
3. **Monitor:** Check for conflicts or issues
4. **Document:** Update this file with learnings

### Rollback Plan

If service causes issues:
```bash
# 1. Disable service
# 2. Restore from backup
tar -xzf backups/n5os-YYYYMMDD.tar.gz

# 3. Verify system health
python3 tests/system_health_check.py

# 4. Document issue
# 5. Decide: fix or remove
```

---

## Configuration Files

### Recommended .gitignore

```gitignore
# Temporary
*.tmp
*.bak
*~

# OS
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
.venv/

# Local
local/
.env
secrets/
```

### Recommended crontab

```cron
# N5OS Lite Maintenance
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# Daily health check (9 AM)
0 9 * * * cd /home/workspace && python3 tests/system_health_check.py

# Weekly backup (Sunday midnight)
0 0 * * 0 cd /home/workspace && ./scripts/backup.sh

# Monthly deep clean (1st of month, 2 AM)
0 2 1 * * cd /home/workspace && ./scripts/monthly_maintenance.sh
```

---

## Support Matrix

| Service | Required | Recommended | Optional |
|---------|----------|-------------|----------|
| Git | ❌ | ✅ | - |
| Scheduled Tasks | ❌ | ✅ | - |
| File Sync | ❌ | ⚠️ | ✅ |
| Python venv | ❌ | ⚠️ | ✅ |
| Docker | ❌ | ❌ | ✅ |
| Database | ❌ | ❌ | ❌ |

Legend:
- ✅ Recommended for most users
- ⚠️ Recommended for specific use cases
- ❌ Not recommended

---

## Related

- System: `filesystem_standard.md` - Directory structure
- System: `preferences_system.md` - Configuration
- Examples: `scheduled_tasks.md` - Automation examples
- Scripts: All maintenance scripts

---

**Start simple. Add services when you need them, not because you can.**

*Last Updated: 2025-11-03*
