# N5 Maintenance Scripts

Automated maintenance routines for n5OS system health and integrity.

---

## Scripts Overview

### 1. `daily_guardian.py`
**Frequency:** Daily at 05:30 ET  
**Model:** GPT-4o-mini  
**Purpose:** Critical file integrity and git health monitoring

**Checks:**
- Critical system files exist and are non-empty
- Essential knowledge files integrity
- Git working tree status
- Recent backup verification (<24h)

**Logs:** `N5/logs/maintenance/daily/YYYY-MM-DD.log`

---

### 2. `weekly_cleanup.py`
**Frequency:** Weekly (Mondays) at 03:00 ET  
**Model:** Claude Sonnet 4.5  
**Purpose:** Workspace cleanup and temporary file management

**Actions:**
- Delete conversation workspaces >14 days old
- Clean temp files in N5/runtime/ >14 days old
- Clean exports in N5/exports/ >30 days old
- Clean maintenance logs >30 days old

**Logs:** `N5/logs/maintenance/weekly/workspace_YYYY-MM-DD.log`

---

### 3. `weekly_list_health.py`
**Frequency:** Weekly (Sundays) at 20:00 ET  
**Model:** Claude Sonnet 4.5  
**Purpose:** List validation and health monitoring

**Checks:**
- JSONL schema compliance
- Stale items (>30 days untouched)
- Potential duplicates
- Overall health score (0-100)

**Logs:** `N5/logs/maintenance/weekly/lists_YYYY-MM-DD.log`

---

### 4. `monthly_audit.py`
**Frequency:** Monthly (1st) at 20:00 ET  
**Model:** Claude Sonnet 4.5  
**Purpose:** Comprehensive system audit

**Checks:**
- Full git governance audit
- Critical file backup verification
- Index validation (N5.md, N5.jsonl)
- Backup rotation (remove >6 months old)

**Logs:** `N5/logs/maintenance/monthly/YYYY-MM.log`

---

### 5. `squawk_proposer.py`
**Frequency:** Every 3 days at 20:30 ET  
**Model:** Claude Sonnet 4.5  
**Purpose:** Auto-generate proposals for issue resolution

**Features:**
- Analyzes squawk and system-upgrades lists
- Selects items based on lift/reward ratio and implementation likelihood
- Generates comprehensive proposals with clarifying questions
- Outputs to `N5/maintenance/proposals/`

**Logs:** `N5/logs/maintenance/squawk/proposals.log`

**Manual Usage:**
```bash
# Auto-select best item
python3 squawk_proposer.py

# Target specific item
python3 squawk_proposer.py --item-id squawk-001

# Dry run (show selection without generating)
python3 squawk_proposer.py --dry-run

# Target specific source
python3 squawk_proposer.py --source squawk
```

---

## Retention Policies

| Category | Retention | Cleaned By |
|----------|-----------|------------|
| Conversation workspaces | 14 days | weekly_cleanup |
| Temp files (N5/runtime/) | 14 days | weekly_cleanup |
| Exports (N5/exports/) | 30 days | weekly_cleanup |
| Maintenance logs | 30 days | weekly_cleanup |
| Critical backups | 6 months | monthly_audit |

---

## Manual Execution

All scripts can be run manually:

```bash
# Daily guardian
python3 /home/workspace/N5/scripts/maintenance/daily_guardian.py

# Weekly cleanup
python3 /home/workspace/N5/scripts/maintenance/weekly_cleanup.py

# Weekly list health
python3 /home/workspace/N5/scripts/maintenance/weekly_list_health.py

# Monthly audit
python3 /home/workspace/N5/scripts/maintenance/monthly_audit.py

# Squawk proposer
python3 /home/workspace/N5/scripts/maintenance/squawk_proposer.py
```

---

## Scheduled Task Configuration

These scripts are configured as scheduled tasks at:  
https://va.zo.computer/schedule

**Task Details:**
- **daily-guardian** - FREQ=DAILY;BYHOUR=5;BYMINUTE=30
- **weekly-cleanup** - FREQ=WEEKLY;BYDAY=MO;BYHOUR=3;BYMINUTE=0
- **weekly-list-health** - FREQ=WEEKLY;BYDAY=SU;BYHOUR=20;BYMINUTE=0
- **monthly-audit** - FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=20;BYMINUTE=0
- **squawk-proposer** - FREQ=DAILY;INTERVAL=3;BYHOUR=20;BYMINUTE=30

---

## Logging

All maintenance activities are logged to:
```
N5/logs/maintenance/
├── daily/
│   └── YYYY-MM-DD.log
├── weekly/
│   ├── workspace_YYYY-MM-DD.log
│   └── lists_YYYY-MM-DD.log
├── monthly/
│   └── YYYY-MM.log
└── squawk/
    └── proposals.log
```

Logs are automatically cleaned after 30 days by `weekly_cleanup.py`.

---

## Auto-Fix Behavior

| Script | Auto-Fix | Report-Only |
|--------|----------|-------------|
| daily_guardian | None | File issues, git status, backup status |
| weekly_cleanup | Deletes old files | Summary of deletions |
| weekly_list_health | Schema formatting | Stale items, duplicates |
| monthly_audit | Backup rotation | Git issues, index issues |
| squawk_proposer | None | Proposal generation |

**Safety:** All auto-fixes are reversible via git history or backups.

---

## Integration with N5 System

These maintenance scripts integrate with:
- **Squawk List** (`Lists/squawk.jsonl`) - Critical issues
- **System Upgrades List** (`Lists/system-upgrades.jsonl`) - Planned enhancements
- **Git governance** - File protection and tracking
- **Backup system** - N5/backups/ directory
- **Command registry** - Can be invoked as commands

---

## Monitoring & Alerts

Currently, maintenance runs silently with logs only. Future enhancements:
- Email summaries for critical issues
- Dashboard integration for health scores
- Slack/SMS alerts for failures
- Telemetry tracking over time

---

## Troubleshooting

**Script fails to run:**
1. Check log file for error details
2. Verify Python 3 is available: `python3 --version`
3. Check file permissions: `ls -la /home/workspace/N5/scripts/maintenance/`

**No logs generated:**
1. Verify log directory exists: `ls -la /home/workspace/N5/logs/maintenance/`
2. Check scheduled task status: https://va.zo.computer/schedule

**Scheduled task not running:**
1. Verify task is registered in Zo schedule
2. Check system time and timezone settings
3. Review scheduled task logs in Zo interface

---

## Future Enhancements

Potential additions to the maintenance system:
- Knowledge base health checks
- Article tracking cleanup
- Email digest generation
- Performance metrics collection
- Dependency version checks
- Security vulnerability scanning
