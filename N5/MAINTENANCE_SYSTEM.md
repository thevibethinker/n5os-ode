# n5OS Maintenance System

**Status:** ✅ ACTIVE  
**Version:** 1.0  
**Deployed:** 2025-10-09  

---

## Overview

The n5OS Maintenance System provides automated health monitoring, cleanup, and issue resolution for your personal operating system. It runs 5 core maintenance routines on daily, weekly, and monthly schedules.

---

## Active Maintenance Routines

### 🛡️ **Daily File Guardian**
- **Schedule:** Every day at 05:30 ET
- **Model:** GPT-4o-mini
- **Next Run:** 2025-10-09 at 05:30 ET

**What it does:**
- Verifies critical system files exist and are non-empty
- Checks essential knowledge files integrity
- Monitors git working tree status
- Validates recent backups exist (<24 hours)

**Outputs:** `N5/logs/maintenance/daily/YYYY-MM-DD.log`

---

### 🧹 **Weekly Workspace Cleanup**
- **Schedule:** Every Monday at 03:00 ET
- **Model:** Claude Sonnet 4.5
- **Next Run:** 2025-10-13 at 03:00 ET

**What it does:**
- Deletes old conversation workspaces (>14 days)
- Cleans temp files in N5/runtime/ (>14 days)
- Removes old exports (>30 days)
- Purges old maintenance logs (>30 days)

**Outputs:** `N5/logs/maintenance/weekly/workspace_YYYY-MM-DD.log`

---

### 📋 **Weekly List Health Check**
- **Schedule:** Every Sunday at 20:00 ET
- **Model:** Claude Sonnet 4.5
- **Next Run:** 2025-10-12 at 20:00 ET

**What it does:**
- Validates JSONL schema compliance for all lists
- Identifies stale items (>30 days untouched)
- Detects potential duplicates
- Calculates health scores (0-100) for each list

**Outputs:** `N5/logs/maintenance/weekly/lists_YYYY-MM-DD.log`

---

### 🔍 **Monthly System Audit**
- **Schedule:** 1st of every month at 20:00 ET
- **Model:** Claude Sonnet 4.5
- **Next Run:** 2025-11-01 at 20:00 ET

**What it does:**
- Performs comprehensive git governance audit
- Verifies all critical file backups exist
- Validates N5 index integrity (N5.md, N5.jsonl)
- Rotates old backups (removes >6 months)

**Outputs:** `N5/logs/maintenance/monthly/YYYY-MM.log`

---

### 💡 **Squawk Auto-Proposer**
- **Schedule:** Every 3 days at 20:30 ET
- **Model:** Claude Sonnet 4.5
- **Next Run:** 2025-10-09 at 20:30 ET

**What it does:**
- Analyzes squawk list and system-upgrades list
- Selects best item based on priority, age, and implementation likelihood
- Generates comprehensive solution proposals with:
  - Root cause analysis
  - Step-by-step implementation plan
  - Risk assessment
  - Test validation steps
  - Rollback procedures
  - Clarifying questions (intent, functionality, output, considerations)
- Saves proposals to `N5/maintenance/proposals/`

**Outputs:** 
- Proposals: `N5/maintenance/proposals/[source]_[id]_YYYY-MM-DD.md`
- Logs: `N5/logs/maintenance/squawk/proposals.log`

---

## Retention Policies

| Category | Retention Period | Cleaned By |
|----------|------------------|------------|
| Conversation workspaces | 14 days | Weekly Cleanup |
| Temp files (N5/runtime/) | 14 days | Weekly Cleanup |
| Exports (N5/exports/) | 30 days | Weekly Cleanup |
| Maintenance logs | 30 days | Weekly Cleanup |
| Critical backups | 6 months | Monthly Audit |

---

## Auto-Fix vs. Report-Only

| Routine | Auto-Fix Actions | Report-Only |
|---------|------------------|-------------|
| Daily Guardian | None | All checks |
| Weekly Cleanup | Deletes old files | Summary |
| List Health Check | Schema formatting | Stale items, duplicates |
| Monthly Audit | Backup rotation | Git issues, index validation |
| Squawk Proposer | None | Proposals only |

**Safety Guarantee:** All auto-fixes are conservative and reversible via git history or backups.

---

## Integration Points

### Source Lists
- **Squawk List** - `Lists/squawk.jsonl` (critical/urgent issues)
- **System Upgrades List** - `Lists/system-upgrades.jsonl` (planned enhancements)

### Protected Files Monitored
**Critical System Files:**
- `Documents/N5.md`
- `N5/prefs/prefs.md`

**Essential Knowledge Files:**
- `Knowledge/architectural/ingestion_standards.md`
- `Knowledge/architectural/operational_principles.md`
- `Knowledge/stable/bio.md`
- `Knowledge/stable/company.md`
- `Knowledge/README.md`

---

## Squawk Proposer Selection Logic

The auto-proposer prioritizes items based on:

1. **Low Lift, High Reward** - Quick wins with significant impact
2. **Highest Likelihood of Success** - Clear scope, minimal dependencies
3. **Priority Weighting:**
   - HIGH/H: 100 points
   - MEDIUM/M: 50 points
   - LOW/L: 10 points
4. **Age Weighting** - Older items get priority (FIFO when equal)
5. **Source Bias** - Squawk items get +20 points (critical issues)

**Status Filter:** Only considers items with status: `open`, `planned`, or `pending`

---

## Manual Invocation

All maintenance scripts can be run manually:

```bash
# Daily guardian
python3 /home/workspace/N5/scripts/maintenance/daily_guardian.py

# Weekly cleanup
python3 /home/workspace/N5/scripts/maintenance/weekly_cleanup.py

# Weekly list health check
python3 /home/workspace/N5/scripts/maintenance/weekly_list_health.py

# Monthly audit
python3 /home/workspace/N5/scripts/maintenance/monthly_audit.py

# Squawk proposer (auto-select)
python3 /home/workspace/N5/scripts/maintenance/squawk_proposer.py

# Squawk proposer (specific item)
python3 /home/workspace/N5/scripts/maintenance/squawk_proposer.py --item-id squawk-001

# Squawk proposer (dry run)
python3 /home/workspace/N5/scripts/maintenance/squawk_proposer.py --dry-run
```

---

## Viewing Scheduled Tasks

View and manage all scheduled tasks at:  
**https://va.zo.computer/schedule**

---

## Directory Structure

```
N5/
├── scripts/
│   └── maintenance/
│       ├── README.md
│       ├── daily_guardian.py
│       ├── weekly_cleanup.py
│       ├── weekly_list_health.py
│       ├── monthly_audit.py
│       └── squawk_proposer.py
├── logs/
│   └── maintenance/
│       ├── daily/
│       ├── weekly/
│       ├── monthly/
│       └── squawk/
└── maintenance/
    ├── README.md
    └── proposals/
        └── [generated proposal files]
```

---

## Workflow: Proposal to Implementation

1. **Auto-Generation** (every 3 days)
   - System selects best item from squawk/upgrades lists
   - Generates comprehensive proposal with analysis and questions

2. **Review** (you)
   - Read proposal in `N5/maintenance/proposals/`
   - Answer clarifying questions
   - Evaluate risk assessment

3. **Approval** (you)
   - Approve proposal for implementation
   - Request modifications if needed

4. **Implementation** (you or system)
   - Follow step-by-step instructions
   - Execute with backups in place

5. **Validation** (you)
   - Run test validation steps from proposal
   - Verify system stability

6. **Closure** (you)
   - Update source list item status to "completed"
   - Document any deviations or learnings

---

## Key Features

### ✅ Conservative & Safe
- Auto-fixes only transient/temp files
- Critical files are report-only
- All changes reversible via git/backups

### ✅ Intelligent Selection
- Prioritizes low-lift, high-reward items
- Considers age, priority, and likelihood of success
- Adapts to your evolving system

### ✅ Comprehensive Proposals
- Root cause analysis
- Step-by-step solutions
- Risk assessment
- Test procedures
- Rollback plans
- Clarifying questions

### ✅ Passive Functionality Building
- Continuously proposes improvements
- Builds up system capabilities over time
- You maintain full control

---

## Monitoring & Troubleshooting

### Check if Tasks are Running
Visit: https://va.zo.computer/schedule

### View Logs
```bash
# Latest daily log
tail -50 /home/workspace/N5/logs/maintenance/daily/$(date +%Y-%m-%d).log

# Latest weekly cleanup
ls -lt /home/workspace/N5/logs/maintenance/weekly/ | head -5

# Squawk proposals log
tail -50 /home/workspace/N5/logs/maintenance/squawk/proposals.log
```

### Common Issues

**Task not running:**
1. Check scheduled tasks page
2. Verify system time and timezone
3. Review task instruction for errors

**Script fails:**
1. Check log file for error details
2. Run script manually to reproduce
3. Verify Python 3 is available

**No proposals generated:**
1. Check if squawk/upgrades lists have open items
2. Verify Lists/squawk.jsonl and Lists/system-upgrades.jsonl exist
3. Review squawk proposals log for selection details

---

## Future Enhancements

Potential additions (add to system-upgrades list!):

- Email summaries for critical issues
- Health dashboard with visual trends
- Slack/SMS alerts for failures
- Telemetry and metrics over time
- Knowledge base health checks
- Article tracking automation
- Performance metrics collection
- Dependency version checks
- Security vulnerability scanning

---

## Documentation

- **Main README:** `N5/maintenance/README.md` (Proposal system)
- **Scripts README:** `N5/scripts/maintenance/README.md` (Technical details)
- **This Document:** `N5/MAINTENANCE_SYSTEM.md` (Overview)

---

## Next Steps

1. **Monitor First Runs**
   - Daily guardian runs tomorrow at 05:30 ET
   - Squawk proposer runs today at 20:30 ET
   - Check logs after each run

2. **Review First Proposal**
   - First proposal generates today at 20:30 ET
   - Review in `N5/maintenance/proposals/`
   - Answer clarifying questions
   - Approve or request modifications

3. **Adjust as Needed**
   - If schedules don't work, update at va.zo.computer/schedule
   - If retention policies too aggressive/conservative, modify scripts
   - Add issues to squawk list as they arise

4. **Track Improvements**
   - System builds functionality passively over time
   - Each proposal addresses one issue
   - System health improves incrementally

---

**Status:** 🟢 All systems operational

**Last Updated:** 2025-10-09 03:57 ET
