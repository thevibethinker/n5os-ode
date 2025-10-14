# Scheduling Configuration

**Module:** Operations  
**Version:** 2.0.0  
**Date:** 2025-10-09

---

## Configuration Parameters

### Status
**Enabled:** false

*Scheduling system is currently disabled by default. Enable only with explicit user consent.*

---

### Retry Policy

**Max Retries:** 2

**Backoff Seconds:**
- First retry: 60 seconds
- Second retry: 300 seconds (5 minutes)

**Strategy:** Exponential backoff

---

### Lock Timeout

**Timeout:** 3600 seconds (1 hour)

**Purpose:** Prevent hung jobs from blocking scheduler

**Behavior:** After timeout, lock is released and job can be retried

---

### Missed Run Policy

**Policy:** skip

**Options:**
- `skip` — Do not run missed jobs
- `run` — Execute missed jobs on next scheduler cycle
- `queue` — Queue missed jobs for sequential execution

**Current setting:** Skip missed runs to avoid backlog accumulation

---

### Timezone

**Default:** UTC

**User Timezone:** America/New_York (ET)

**Handling:**
- Store all timestamps in UTC
- Convert to user timezone for display
- Accept user input in their timezone (ET)
- Always include timezone in date/time strings

---

## Safety Requirements

### Never Schedule Without Consent

**Before scheduling:**
1. Show proposed schedule
2. Explain what will run and when
3. Request explicit approval
4. Confirm timezone interpretation

**See:** `file 'N5/prefs/system/safety.md'` for safety rules

---

## Scheduling Commands

**Available commands:**
- View schedule: Check `/home/va.zo.computer/schedule`
- Create task: Via Zo scheduling interface
- Modify task: Via Zo scheduling interface
- Delete task: Via Zo scheduling interface

**Command-line access:** Currently not exposed via N5 commands

---

## Related Files

- **Scheduled Task Protocol:** `file 'N5/prefs/operations/scheduled-task-protocol.md'` (creation standards)
- **Safety Requirements:** `file 'N5/prefs/system/safety.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Clarified enabled status (disabled by default)
- Added safety requirements section
- Added user timezone reference
- Documented scheduling command access
