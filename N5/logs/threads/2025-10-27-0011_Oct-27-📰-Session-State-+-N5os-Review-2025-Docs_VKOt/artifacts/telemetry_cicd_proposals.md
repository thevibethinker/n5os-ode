# Telemetry + CI/CD Proposals
**Conversation:** con_BD6xkpxbTZVbVKOt  
**Date:** 2025-10-26 19:40 ET

---

## 1. Basic Telemetry System

### What It Does

Surfaces key metrics about your n5OS health and Zero-Touch alignment:

- **Flow Efficiency:** Files moving through Records → Knowledge/Lists
- **Principle Adherence:** How often scripts follow architectural principles
- **System Health:** Stale files, orphaned tasks, uncommitted changes
- **Usage Patterns:** Which commands/scripts run most, error rates

### Proposal: Lightweight Dashboard

```
N5/telemetry/
├── collectors/
│   ├── flow_metrics.py          # Track Records → Knowledge movement
│   ├── principle_scanner.py     # Scan code for P0-P33 violations
│   └── health_checker.py        # Empty files, orphans, etc.
├── dashboard.py                 # Generate daily summary
└── config.json                  # What to track
```

**Output:** Daily digest showing:
- Files moved today: X (target: >10/day)
- Stale items in Records/: Y files (target: <5)
- Principle violations detected: Z (target: 0 critical)
- Most-used commands: top 5
- Error rate: N% (target: <2%)

**Implementation:** ~2 hours
**Value:** Immediate visibility into Zero-Touch effectiveness

---

## 2. CI/CD Explained (Non-Technical)

### What Is CI/CD?

**CI = Continuous Integration**: Automatic checks when you commit code  
**CD = Continuous Deployment**: Automatic pushes to production when checks pass

Think of it like:
- **CI** = Your assistant double-checking your work before you send an email
- **CD** = Your assistant sending the email automatically once it's perfect

### What It Looks For

1. **Syntax errors** (will this code even run?)
2. **Test failures** (does this break existing functionality?)
3. **Style violations** (does this follow our architectural principles?)
4. **Security issues** (does this expose sensitive data?)

### Your n5OS CI/CD

**On every git commit**, automatically run:

1. **Syntax Check**: `python3 -m py_compile` on changed scripts
2. **Schema Validation**: Verify `.jsonl` files match N5 schemas
3. **Safety Check**: Run `n5_safety.py` on protected files
4. **Principle Scanner**: Flag violations of P0-P33
5. **Test Suite**: Run critical path tests (meeting-process, lists, etc.)

**If all pass** → ✅ Commit accepted  
**If any fail** → ❌ Commit blocked, show errors

---

## 3. Implementation Plan

### Phase 1: Telemetry (Week 1, ~4 hours)

**Day 1-2: Build collectors**
```python
# flow_metrics.py
def analyze_flow():
    records_count = count_files("Records/Temporary/")
    knowledge_adds = git_log_since_yesterday("Knowledge/")
    return {
        "records_pending": records_count,
        "knowledge_adds_24h": knowledge_adds,
        "flow_rate": knowledge_adds / max(records_count, 1)
    }
```

**Day 3: Dashboard**
```python
# dashboard.py
def generate_daily_summary():
    metrics = {
        "flow": analyze_flow(),
        "health": check_system_health(),
        "usage": analyze_command_usage()
    }
    render_markdown(metrics, "N5/telemetry/daily_report.md")
```

**Day 4: Schedule it**
- Run daily at 8am ET via scheduled task
- Email summary to you

### Phase 2: CI/CD (Week 2, ~6 hours)

**GitHub Actions Setup** (`.github/workflows/n5-ci.yml`):

```yaml
name: n5OS CI
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Syntax Check
        run: |
          find N5/scripts -name "*.py" -exec python3 -m py_compile {} \;
      
      - name: Schema Validation
        run: |
          python3 N5/scripts/n5_schema_validation.py --all
      
      - name: Safety Check
        run: |
          python3 N5/scripts/n5_safety.py --dry-run
      
      - name: Run Tests
        run: |
          pytest N5/tests/ -v
```

**What This Does:**
- Runs on every commit
- Takes ~2-3 min
- Shows ✅ or ❌ in GitHub UI
- Blocks merge if tests fail (optional)

### Phase 3: Integration (Week 3, ~2 hours)

- Link telemetry → CI/CD (fail CI if metrics degrade)
- Add principle scanner to CI checks
- Set up notifications (email on failure)

---

## Quick Wins (Start Today)

### 1. Manual Health Check Script (30 min)

```bash
#!/usr/bin/env bash
# N5/scripts/health_check.sh

echo "📊 n5OS Health Check"
echo "===================="
echo ""
echo "Stale Records:"
find Records/Temporary -type f -mtime +7 | wc -l
echo ""
echo "Empty Files:"
find N5 Knowledge Documents -type f -empty | wc -l
echo ""
echo "Uncommitted Changes:"
git status --short | wc -l
```

Run: `bash N5/scripts/health_check.sh`

### 2. Add Pre-Commit Hook (15 min)

Already exists! Your `n5_safety.py` runs on commit.  
Extend it to check principle violations:

```python
# Add to n5_safety.py
def check_principles(changed_files):
    violations = []
    for file in changed_files:
        if "TODO" in file.read_text():
            violations.append(f"{file}: Undocumented placeholder (P21)")
    return violations
```

### 3. Command Usage Tracker (20 min)

```python
# N5/scripts/track_usage.py
import json
from pathlib import Path
from datetime import datetime

def log_command_use(command_name):
    log_file = Path("N5/telemetry/command_usage.jsonl")
    log_file.parent.mkdir(exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": command_name,
        "user": "V"
    }
    
    with log_file.open('a') as f:
        f.write(json.dumps(entry) + "\n")
```

Add one line to each command script: `track_usage("meeting-process")`

---

## Recommendations

**Start with:**
1. ✅ Manual health check (30 min, today)
2. ✅ Command usage tracker (20 min, today)
3. ⏳ Full telemetry dashboard (4 hours, this week)
4. ⏳ CI/CD setup (6 hours, next week)

**Why this order:**
- Health check gives immediate value
- Usage tracker is fire-and-forget
- Telemetry provides data for principle alignment
- CI/CD prevents regressions once system stabilizes

**Your call:** Which do you want to tackle first?

---

*v1.0 | 2025-10-26 19:40 ET*
