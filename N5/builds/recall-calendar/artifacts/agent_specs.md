---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.0
provenance: con_4AqxTM7MxqENXxDr
build_slug: recall-calendar
drop_id: D2.2
---

# Recall Calendar - Scheduled Agent Specifications

This document defines the scheduled agents needed for the Recall.ai calendar integration.
**Note: These agents are documented for V's review and must be created manually.**

---

## Agent 1: Recall Calendar Sync (Primary)

**Title:** `⇱ Recall Calendar Sync`

**Cornerstone:** Yes (⇱) — This agent should not be deleted or modified without explicit confirmation.

### Schedule
```
RRULE: FREQ=MINUTELY;INTERVAL=15;BYHOUR=8,9,10,11,12,13,14,15,16,17,18,19,20
```

**Timezone:** America/New_York

**Coverage:** 8 AM - 8 PM Eastern, every 15 minutes

### Instruction

```
Run calendar-to-Recall sync:

1. python3 /home/workspace/Integrations/recall_ai/calendar_scheduler.py sync --hours 24

2. If any errors occur, send SMS alert to V:
   "[RECALL] Calendar sync error: {error_message}"

3. If new bots are scheduled, log to N5/logs/recall_calendar_sync.log (no notification needed for normal operation)

4. Skip notifications for normal sync runs (only alert on errors)
```

### Notes

- Primary coverage during business hours when most meetings are scheduled
- 15-minute cadence catches newly scheduled meetings while staying under rate limits
- Uses default quiet behavior (only errors trigger alerts)

---

## Agent 2: Recall Calendar Sync (Off-hours)

**Title:** `Recall Calendar Sync (Off-hours)`

**Cornerstone:** No

### Schedule
```
RRULE: FREQ=HOURLY;INTERVAL=1;BYHOUR=0,1,2,3,4,5,6,7,21,22,23
```

**Timezone:** America/New_York

**Coverage:** Overnight (midnight-8 AM) and evening (9 PM-midnight), hourly

### Instruction

```
Run calendar sync for overnight coverage:

1. python3 /home/workspace/Integrations/recall_ai/calendar_scheduler.py sync --hours 12 --quiet

2. Only alert on errors via SMS:
   "[RECALL] Off-hours sync error: {error_message}"

3. Log to N5/logs/recall_calendar_sync.log
```

### Notes

- Catches early morning meetings scheduled overnight
- Hourly cadence is sufficient for off-hours (less meeting volume)
- Uses `--quiet` flag to suppress non-error output
- Scans 12 hours ahead to cover the next business day

---

## Agent 3: Recall Bot Health Check

**Title:** `Recall Bot Health Check`

**Cornerstone:** No

### Schedule
```
RRULE: FREQ=MINUTELY;INTERVAL=30
```

**Timezone:** UTC (runs every 30 minutes)

### Instruction

```
Check for stuck/failed Recall bots:

1. Run health check:
   python3 /home/workspace/Integrations/recall_ai/recall_client.py health-check --max-hours 4

2. If stuck bots found (recording >4 hours), send SMS for each:
   "[RECALL] Bot {bot_id} has been recording for {X.X} hours - may be stuck"

3. If fatal status bots found, send SMS for each:
   "[RECALL] Fatal error on bot {bot_id}: {error_message}"

4. Log all health checks to N5/logs/recall_health_check.log
```

### Notes

- Monitors for bots stuck in "in_call_recording" state
- 4-hour threshold for stuck detection (adjustable via --max-hours)
- Also checks for fatal status bots
- Sends one SMS per problematic bot

---

## Agent Configuration Reference

### Agent ID Storage

Once created, agent IDs should be stored in `N5/config/recall_agents.json`:

```json
{
  "agents": {
    "primary_sync": {
      "title": "⇱ Recall Calendar Sync",
      "agent_id": "<agent_id>",
      "rrule": "FREQ=MINUTELY;INTERVAL=15;BYHOUR=8,9,10,11,12,13,14,15,16,17,18,19,20",
      "cornerstone": true,
      "created_at": "2026-01-25T..."
    },
    "off_hours_sync": {
      "title": "Recall Calendar Sync (Off-hours)",
      "agent_id": "<agent_id>",
      "rrule": "FREQ=HOURLY;INTERVAL=1;BYHOUR=0,1,2,3,4,5,6,7,21,22,23",
      "cornerstone": false,
      "created_at": "2026-01-25T..."
    },
    "health_check": {
      "title": "Recall Bot Health Check",
      "agent_id": "<agent_id>",
      "rrule": "FREQ=MINUTELY;INTERVAL=30",
      "cornerstone": false,
      "created_at": "2026-01-25T..."
    }
  },
  "updated_at": "2026-01-25T..."
}
```

### Creation Command Template

```bash
python3 N5/scripts/create_agent.py \
  --title "⇱ Recall Calendar Sync" \
  --rrule "FREQ=MINUTELY;INTERVAL=15;BYHOUR=8,9,10,11,12,13,14,15,16,17,18,19,20" \
  --instruction "Run calendar-to-Recall sync:
1. python3 /home/workspace/Integrations/recall_ai/calendar_scheduler.py sync --hours 24
2. If any errors, send SMS: '[RECALL] Calendar sync error: {error}'
3. Log normally, no notification on success."
```

---

## Rate Limit Considerations

### Recall API
- **Rate Limit:** 60 requests per minute
- **Impact:** Each scheduled bot counts as 1 API call
- **Mitigation:** 15-minute sync cadence during business hours = ~4 syncs/hour = ~48 syncs/day
- **Safety Margin:** Even with 10 meetings per sync = 480 calls/day, well within limits

### Google Calendar API
- **Daily Quota:** ~1,000,000 quota units
- **Impact:** ~100 quota units per event listing
- **Mitigation:** 15-minute sync cadence = 96 listings/day = ~9,600 quota units/day
- **Safety Margin:** Negligible impact on quota

---

## Log Files

Agents should log to:

- `N5/logs/recall_calendar_sync.log` — Sync operations
- `N5/logs/recall_health_check.log` — Health check results

Ensure `N5/logs/` directory exists before agents first run.

---

## Testing Before Activation

Before activating agents in production:

1. [ ] Run `python3 Integrations/recall_ai/calendar_scheduler.py test` — verify config OK
2. [ ] Run `python3 Integrations/recall_ai/calendar_scheduler.py sync --dry-run` — verify sync logic
3. [ ] Run `python3 Integrations/recall_ai/recall_client.py test` — verify Recall API connection
4. [ ] Create agents in test mode first (if available)
5. [ ] Monitor first few runs manually via log files

---

## Troubleshooting

### No bots being scheduled
- Check: Is RECALL_API_KEY set in agent environment?
- Check: Does calendar have upcoming meetings with video links?
- Check: Are meetings marked with [NR] or [SKIP]?

### Too many SMS alerts
- Check: Is sync completing successfully?
- Check: Adjust RRULE frequency if needed

### Bot health check always alerting
- Check: Are meetings actually running long?
- Check: Adjust --max-hours threshold if needed
- Check: Are bots properly ending meetings?

---

## Review Checklist

- [ ] All RRULEs are correct for desired schedules
- [ ] Timezones are set correctly
- [ ] Instructions are clear and complete
- [ ] Error handling includes SMS alerts
- [ ] Rate limits are respected
- [ ] Log paths exist and are writable
- [ ] Cornerstone agent (⇱) is marked appropriately
- [ ] Agent IDs will be stored in `N5/config/recall_agents.json`
