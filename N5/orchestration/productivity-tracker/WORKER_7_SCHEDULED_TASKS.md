# Worker 7: Scheduled Tasks

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W7-SCHEDULED-TASKS  
**Estimated Time:** 30 minutes  
**Dependencies:** Worker 5 (RPI Calculator)

---

## Mission

Set up scheduled tasks to automatically scan emails/meetings every 30 minutes and recalculate RPI, keeping the productivity tracker up-to-date without manual intervention.

---

## Context

Automation is critical for seamless daily usage. The system should:
- Scan new emails every 30 min
- Scan today's meetings every 30 min
- Recalculate RPI after scans
- Run silently in background
- Log progress for debugging

---

## Dependencies

Worker 5 complete (all scripts ready)

---

## Deliverables

1. Two scheduled tasks created:
   - `productivity-email-scanner` (every 30 min)
   - `productivity-meeting-scanner` (every 30 min)
2. Wrapper script that chains: email → meeting → RPI
3. Logs confirming automated execution

---

## Requirements

### Scheduled Task Specs

**Email + Meeting Scanner:**
- **Frequency:** Every 30 minutes
- **Command:** Run wrapper script
- **Delivery:** None (silent operation, logs only)
- **Error handling:** Log failures, don't block

### Wrapper Script

```bash
#!/bin/bash
# /home/workspace/N5/scripts/productivity/auto_scan.sh

LOG_FILE="/home/workspace/logs/productivity_auto_scan.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date -Iseconds)] Starting auto scan" >> "$LOG_FILE"

# Scan emails (today only)
python3 /home/workspace/N5/scripts/productivity/email_scanner.py --scan-range today 2>&1 | tee -a "$LOG_FILE"

# Scan meetings (today only)
python3 /home/workspace/N5/scripts/productivity/meeting_scanner.py --scan-range today 2>&1 | tee -a "$LOG_FILE"

# Recalculate RPI
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py 2>&1 | tee -a "$LOG_FILE"

echo "[$(date -Iseconds)] Auto scan complete" >> "$LOG_FILE"
```

---

## Implementation

Use `create_scheduled_task` tool:

```python
# Task 1: Productivity Auto-Scan
create_scheduled_task(
    rrule="FREQ=MINUTELY;INTERVAL=30;BYHOUR=7,8,9,10,11,12,13,14,15,16,17,18,19,20",
    instruction="Run the productivity tracker auto-scan script at /home/workspace/N5/scripts/productivity/auto_scan.sh to scan emails, meetings, and recalculate RPI. Log output to /home/workspace/logs/productivity_auto_scan.log. Do not email results.",
    delivery_method=None
)
```

**Note:** Schedule only during waking hours (7am-8pm) to avoid unnecessary scans

---

## Testing

### Manual Test
```bash
bash /home/workspace/N5/scripts/productivity/auto_scan.sh
cat /home/workspace/logs/productivity_auto_scan.log
```

### Verify Scheduled Task
```bash
# Check task is created
# Monitor logs after 30 min
tail -f /home/workspace/logs/productivity_auto_scan.log
```

---

## Report Back

1. ✅ Wrapper script created at `/home/workspace/N5/scripts/productivity/auto_scan.sh`
2. ✅ Scheduled task created (every 30 min, 7am-8pm)
3. ✅ Manual test successful
4. ✅ Logs confirm automation working
5. ✅ System fully automated!

---

**Orchestrator Contact:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 00:18 ET
