---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_2am5bxIzjC2JGV3F
---

# Build Plan: Recall.ai Calendar Integration

## Summary

Full calendar integration for Recall.ai to automatically schedule meeting bots. Replaces Fireflies.ai as the primary meeting recording system. Integrates with existing Google Calendar via Zo's OAuth, listens for calendar sync events from Recall, and auto-schedules bots for meetings.

## Open Questions

1. ~~Do we use Recall's Calendar V1 or V2?~~ → **V2** (more control, we handle scheduling logic)
2. Should we sync calendars to Recall, or use Zo's existing Google Calendar integration? → **Use existing Zo GCal OAuth**, sync calendar events ourselves, schedule bots via Recall API
3. Bot naming convention? → "Zo Notetaker" 
4. Do we want to auto-record ALL meetings or have opt-out markers? → Support opt-out via `[NR]` in event title

## Architecture Decision

**Option A: Full Recall Calendar V2** - Give Recall our Google OAuth refresh token, let them sync calendar
- Pro: Recall handles calendar polling
- Con: Giving refresh token to third party, less control, duplicate OAuth

**Option B: Zo-controlled scheduling (CHOSEN)**
- Zo polls Google Calendar → Detects meetings with video links → Schedules bots via Recall API
- Pro: Single OAuth source, full control over scheduling logic, integrates with existing CRM/meeting intelligence
- Con: We maintain the scheduler

**Decision**: Option B. We already have Google Calendar connected. No need to duplicate OAuth to Recall.

## Checklist

### Phase 1: Webhook Enhancement
- [ ] Update webhook receiver to handle ALL bot events (not just bot.done)
- [ ] Add event logging for observability
- [ ] Store event history in SQLite
- [ ] Handle bot.fatal with alerting

### Phase 2: Calendar Scheduler
- [ ] Create `calendar_scheduler.py` - polls GCal, finds meetings with video URLs
- [ ] Schedule bots 10+ min before meeting time
- [ ] Track scheduled bots in SQLite to avoid duplicates
- [ ] Support opt-out via `[NR]` marker in event title
- [ ] Handle meeting reschedules (update bot join_at)
- [ ] Handle meeting cancellations (delete scheduled bot)

### Phase 3: Scheduled Agent
- [ ] Create scheduled agent that runs every 5 min
- [ ] Scans upcoming meetings (next 24 hours)
- [ ] Schedules bots for any unscheduled meetings
- [ ] Alerts on failures

### Phase 4: Integration & Testing
- [ ] End-to-end test with real meeting
- [ ] Verify deposit flow works
- [ ] Update capability doc
- [ ] Retire Fireflies integration

## Phase Details

### Phase 1: Webhook Enhancement

**Affected Files:**
- `Integrations/recall_ai/webhook_receiver.py` (modify)
- `Integrations/recall_ai/config.py` (modify)

**Changes:**
- Add handlers for all bot events: joining_call, in_waiting_room, in_call_not_recording, recording_permission_allowed/denied, in_call_recording, call_ended, done, fatal
- Log all events to SQLite with timestamps
- Send SMS alert on bot.fatal
- Track bot lifecycle state

**Unit Tests:**
- Test each event type handler
- Verify SQLite logging
- Test alert on fatal

### Phase 2: Calendar Scheduler

**Affected Files:**
- `Integrations/recall_ai/calendar_scheduler.py` (create)
- `Integrations/recall_ai/models.py` (create - SQLite models)
- `Integrations/recall_ai/config.py` (modify)

**Changes:**
- `calendar_scheduler.py`:
  - `get_upcoming_meetings(hours=24)` - fetches from Google Calendar
  - `extract_video_url(event)` - extracts Zoom/Meet/Teams URL
  - `should_record(event)` - checks for [NR] opt-out marker
  - `schedule_bot_for_event(event)` - calls Recall API
  - `sync_scheduled_bots()` - main sync function
  - `handle_rescheduled(event)` - updates bot join_at
  - `handle_cancelled(event)` - deletes scheduled bot
  
- `models.py`:
  - ScheduledBot table: bot_id, event_id, meeting_url, scheduled_at, join_at, status
  - BotEvent table: bot_id, event_type, timestamp, payload

**Unit Tests:**
- Test video URL extraction from various providers
- Test opt-out marker detection
- Test duplicate prevention

### Phase 3: Scheduled Agent

**Affected Files:**
- Scheduled agent via create_agent

**Changes:**
- Create cornerstone scheduled task (⇱)
- Runs FREQ=MINUTELY;INTERVAL=5
- Calls `calendar_scheduler.sync_scheduled_bots()`
- Texts on new bots scheduled or failures

### Phase 4: Integration Testing

**Affected Files:**
- `Integrations/recall_ai/README.md` (update)
- `N5/capabilities/integrations/recall-webhook.md` (update)

**Changes:**
- Document full flow
- Add troubleshooting guide
- Mark Fireflies as deprecated

## Success Criteria

1. ✅ All calendar events with video URLs get bots scheduled automatically
2. ✅ Bots join 2 minutes before meeting start time
3. ✅ [NR] marker prevents bot scheduling
4. ✅ Rescheduled meetings update bot join_at
5. ✅ Cancelled meetings delete scheduled bots
6. ✅ bot.done triggers deposit into Personal/Meetings/
7. ✅ bot.fatal triggers SMS alert
8. ✅ No duplicate bots for same meeting

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google Calendar API rate limits | High | Batch requests, cache results |
| Recall API rate limits (60/min) | Medium | Queue with backoff |
| Missed webhooks | High | Polling fallback, event replay |
| Bot joins wrong time | Medium | Verify join_at before scheduling |
| Duplicate bots | Medium | Deduplication by event_id + start_time |

## Stream/Drop Structure (Pulse v3)

**Stream 1 (Parallel):**
- D1.1: Webhook Enhancement
- D1.2: SQLite Models

**Stream 2 (Sequential, depends on S1):**
- D2.1: Calendar Scheduler Core
- D2.2: Scheduled Agent Setup

**Stream 3 (Sequential, depends on S2):**
- D3.1: Integration Testing & Docs
