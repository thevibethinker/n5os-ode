# N5 OS Core — Scheduled Tasks (Optional)

**Automated maintenance tasks for N5 OS**

---

## Overview

N5 Core works without scheduled tasks. These are **quality-of-life improvements** that keep your system healthy automatically.

**Start Manual. Automate What Proves Valuable.**

---

## Essential Tasks (Recommended)

### 1. Daily Index Rebuild
**Purpose**: Keep search/navigation current  
**Frequency**: Daily at 6am  
**Command**: `python3 N5/scripts/n5_index_rebuild.py`

**Setup**:
```bash
# Via Zo scheduled tasks
RRULE: FREQ=DAILY;BYHOUR=6;BYMINUTE=0
Instruction: "Run N5 index rebuild: python3 /home/workspace/N5/scripts/n5_index_rebuild.py"
```

**Why**: Ensures N5 knows about all your files without manual rebuilds.

---

### 2. Weekly Git Safety Check
**Purpose**: Prevent data loss from uncommitted work  
**Frequency**: Weekly on Monday at 9am  
**Command**: `python3 N5/scripts/n5_git_check.py`

**Setup**:
```bash
RRULE: FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0
Instruction: "Run N5 git safety check: python3 /home/workspace/N5/scripts/n5_git_check.py"
```

**Why**: Alerts if you have uncommitted changes > 48 hours old.

---

### 3. Empty File Cleanup
**Purpose**: Remove accidentally created empty files  
**Frequency**: Daily at 2am  
**Command**: Custom script (see below)

**Setup**:
```bash
RRULE: FREQ=DAILY;BYHOUR=2;BYMINUTE=0
Instruction: "Find and flag empty files for review:
find /home/workspace -type f -empty -mtime +1 | while read f; do echo \"Empty: $f\"; done | tee /tmp/empty_files.log && cat /tmp/empty_files.log"
```

**Why**: Prevents clutter from failed operations.

---

### 4. Orphaned Git Status
**Purpose**: Find uncommitted work  
**Frequency**: Weekly on Friday at 5pm  
**Command**: Custom check

**Setup**:
```bash
RRULE: FREQ=WEEKLY;BYDAY=FR;BYHOUR=17;BYMINUTE=0
Instruction: "Check for uncommitted git changes:
cd /home/workspace && git status --short | head -20"
```

**Why**: End-of-week reminder to commit your work.

---

### 5. List Health Check
**Purpose**: Detect stale or orphaned list items  
**Frequency**: Weekly on Sunday at 8am  
**Command**: Custom script

**Setup**:
```bash
RRULE: FREQ=WEEKLY;BYDAY=SU;BYHOUR=8;BYMINUTE=0
Instruction: "Check Lists health:
for f in /home/workspace/Lists/*.jsonl; do echo \"$f: $(wc -l < $f) items\"; done"
```

**Why**: Track list growth, spot issues early.

---

## How to Set Up

### Via Zo Scheduled Tasks (Recommended)

**Step 1**: Go to https://[your-username].zo.computer/agents

**Step 2**: Click "Create Agent"

**Step 3**: Fill in:
- Name: "N5 Daily Index"
- RRULE: `FREQ=DAILY;BYHOUR=6;BYMINUTE=0`
- Instruction: (copy from task above)

**Step 4**: Save and enable

**Step 5**: Repeat for other tasks

### Via Cron (Alternative)

```bash
# Edit crontab
crontab -e

# Add tasks
0 6 * * * cd /home/workspace && python3 N5/scripts/n5_index_rebuild.py
0 9 * * 1 cd /home/workspace && python3 N5/scripts/n5_git_check.py
0 2 * * * find /home/workspace -type f -empty -mtime +1 -delete
0 17 * * 5 cd /home/workspace && git status --short
0 8 * * 0 for f in /home/workspace/Lists/*.jsonl; do wc -l $f; done
```

---

## Testing

**Test each task manually first**:
```bash
# Index rebuild
python3 N5/scripts/n5_index_rebuild.py --dry-run

# Git check
python3 N5/scripts/n5_git_check.py

# Empty files
find /home/workspace -type f -empty -mtime +1

# Git status
cd /home/workspace && git status

# Lists health
for f in Lists/*.jsonl; do echo "$f: $(wc -l < $f) items"; done
```

---

## Optional: Advanced Tasks

### 6. Backup Key Files (Weekly)
```bash
RRULE: FREQ=WEEKLY;BYDAY=SUN;BYHOUR=0;BYMINUTE=0
Instruction: "Backup N5 config: cp N5/config/commands.jsonl N5/config/commands.jsonl.backup-$(date +%Y-%m-%d)"
```

### 7. Session State Cleanup (Monthly)
```bash
RRULE: FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=3;BYMINUTE=0
Instruction: "Clean old session states: find /home/workspace/.z/sessions -type f -mtime +90 -delete"
```

---

## Philosophy

**Manual First**: Don't automate until you've done it manually 3+ times and know it's valuable.

**Start Small**: Begin with tasks 1-2 only. Add more after a month.

**Review Results**: Check logs weekly. If a task never helps, disable it.

**Self-Healing**: These tasks detect problems, they don't fix automatically (except empty file cleanup).

---

**Version**: 1.0-core  
**Date**: 2025-10-26  
**Essential**: Tasks 1-5  
**Optional**: Tasks 6-7
