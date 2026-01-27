---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_QhxodiRRMWjBEvCa
---

# Agent Audit Report
**Build:** meeting-system-migration
**Drop:** D1.1
**Date:** 2026-01-26

## Executive Summary

**35 scheduled agents** audited across **10 domains**:
- **27 active agents** (77%)
- **8 disabled agents** (23%)
- **2 temporary agents** (event and Pulse sentinel related)

### Key Findings

| Category | Count | Notes |
|----------|-------|-------|
| Safe to delete | 6 | Disabled agents with clear supersession notes |
| Consolidation candidates | 3 groups | Health checkpoints, Meeting pipeline, Morning briefings |
| Frequency concerns | 5 | Some agents running too frequently |
| Cornerstone tasks | 2 | Database backup, Meeting organization (⇱ protected) |

---

## Domain Breakdown

### Health (9 agents)
| ID | Title | Active | Frequency | Notes |
|----|-------|--------|-----------|-------|
| `0077f07e` | Daily Health Data Sync | ✅ | Daily 7:30 AM | Main health sync |
| `4e2a98ad` | Morning Health Checkpoint: Fasted | ✅ | Daily 7:00 AM | Uses health_checkpoint.py |
| `59e5df9a` | Post-Workout Shake Health Check | ✅ | Daily 8:30 AM | Uses health_checkpoint.py |
| `4163c54c` | Pre-Sleep Health Checkpoint | ✅ | Daily 10:00 PM | Uses health_checkpoint.py |
| `c6ca2440` | Health Checkpoint: The One Meal | ✅ | Daily 9:00 AM | Uses health_checkpoint.py |
| `22b8032a` | Evening Wind-Down Health Check | ✅ | Daily 6:00 PM | Uses health_checkpoint.py |
| `75764953` | Sync Fitbit Workouts & Summary | ✅ | Daily 8:00 AM | Fitbit → Life Counter bridge |
| `f58056ad` | Fitbit Sync & Checkpoint | ❌ | 4x daily | DISABLED - Consolidated |
| `529ed812` | Backfill Fitbit Data | ❌ | Hourly × 24 | DISABLED - One-time completed |

### Meetings (6 agents)
| ID | Title | Active | Frequency | Notes |
|----|-------|--------|-----------|-------|
| `0c53b7ba` | Meeting Manifest Generation [MG-1] | ✅ | 5x daily | Prompts: `Meeting Manifest Generation.prompt.md` |
| `0a08e6a8` | Meeting Intelligence Generation [MG-2] | ✅ | 5x daily | Prompts: `Meeting Block Generation.prompt.md` |
| `ce6995b8` | Meeting Warm Intro Email Drafts [MG-4] | ✅ | 5x daily | Prompts: `Meeting Warm Intro Generation.prompt.md` |
| `f339ca26` | Meeting State Transition [MG-6] | ✅ | 5x daily | Uses manifest.json status |
| `5579f899` | Meeting Blurb Generation | ❌ | 5x daily | DISABLED - Replaced by Zo Take Heed |
| `c7d010d5` | Meeting Follow-Up Generation | ❌ | 5x daily | DISABLED - Replaced by Zo Take Heed |

### CRM/Deals (3 agents)
| ID | Title | Active | Frequency | Notes |
|----|-------|--------|-----------|-------|
| `f0abd2aa` | Weekly CRM Gmail Enrichment | ✅ | Weekly Sun 6:00 AM | Uses unified `N5/data/n5_core.db` |
| `806f7fcc` | Deal Sync & Meeting Routing | ✅ | 4x daily | Consolidated hub |
| `259a13c8` | Acquisition Deal Tracking | ❌ | Daily 8:00 AM | DISABLED - Consolidated |

### Positions (2 agents)
| ID | Title | Active | Frequency | Notes |
|----|-------|--------|-----------|-------|
| `4ce1dca6` | Daily B32 Positions Extraction | ✅ | Daily 5:00 AM | Runs b32_position_extractor.py |
| `dd19d90e` | Weekly Position Triage Summary | ❌ | Weekly Sun 6:00 PM | DISABLED - Past next_run |

### Task Management (2 agents)
| ID | Title | Active | Frequency | Notes |
|----|-------|--------|-----------|-------|
| `9b09d4a3` | Morning Task Briefing | ✅ | Daily 7:00 AM | Uses task-system briefing.py |
| `f5ec46f0` | Evening Accountability Check-In | ✅ | Daily 9:00 PM | Uses task-system briefing.py |

### Other Domains
| Domain | Count | Key Agents |
|--------|-------|------------|
| System | 3 | Daily Database Backup (⇱), Weekly Meeting Organization (⇱), Persona Routing Audit |
| Monitoring | 3 | Recall Bot Health Check (30 min), Pulse Sentinels (temporary) |
| Events | 1 | NYC Unified Luma Events Pipeline |
| Stakeholders | 1 | Stakeholder Profile Auto-Creation |
| Context Intelligence | 1 | Context Graph Deep Backfill (9x daily) |
| Careerspan | 1 | Scan Results Email Monitor (12x daily) |
| Digest | 1 | Unified Morning Digest |
| Survey | 1 | Next Play Pre-Event Survey (temporary) |
| Performance | 1 | Weekly Performance Dashboard |

---

## Deletion Candidates (6)

These agents are **disabled and explicitly superseded**:

1. **`f58056ad`** - Fitbit Sync & Checkpoint Verification
   - Reason: Consolidated into Daily Health Data Sync
   - Note: Caused Fitbit API rate limiting at 4x daily

2. **`529ed812`** - Backfill Fitbit Health Data
   - Reason: One-time backfill task, completed
   - Note: `next_run: null` indicates no future runs

3. **`259a13c8`** - Daily Acquisition Deal Tracking
   - Reason: PAUSED - Consolidated into Deal Sync & Meeting Routing
   - Note: Meeting→deal routing now handled by `806f7fcc`

4. **`5579f899`** - Meeting Blurb Generation
   - Reason: Replaced by Zo Take Heed system (2026-01-19)
   - Note: Blurbs now generated only on explicit request

5. **`c7d010d5`** - Meeting Follow-Up Generation
   - Reason: Replaced by Zo Take Heed system (2026-01-19)
   - Note: Follow-ups now generated only on explicit request

6. **`dd19d90e`** - Weekly Position Triage Summary
   - Reason: DISABLED, next_run in past (Jan 4, 2026)
   - Note: May have been superseded or paused indefinitely

---

## Consolidation Opportunities (3 groups)

### 1. Health Checkpoint Orchestration
**Agents:** `4e2a98ad`, `59e5df9a`, `4163c54c`, `c6ca2440`, `22b8032a`
- All use same `health_checkpoint.py` script
- Run at 5 different times throughout day
- Could consolidate into single orchestrator agent

**Recommended:** Create "Health Checkpoint Orchestrator" that routes to different checkpoint types based on time.

### 2. Meeting Processing Pipeline
**Agents:** `0c53b7ba`, `0a08e6a8`, `ce6995b8`, `f339ca26`
- MG-1, MG-2, MG-4, MG-6 all run at identical times (5x daily)
- Represent sequential pipeline stages
- Could run as single "Meeting Pipeline" agent

**Recommended:** Consider sequential execution within single agent to reduce scheduling overhead.

### 3. Morning Briefings
**Agents:** `9b09d4a3` (Morning Task Briefing), `ad169b76` (Unified Morning Digest)
- Run at 7:00 AM and 8:00 AM
- Similar output: briefings for the day
- Could be unified single output

**Recommended:** Merge into "Morning Briefing" with task + digest sections.

---

## Frequency Concerns (5)

| Agent | Current | Recommended | Reason |
|-------|---------|-------------|--------|
| Context Graph Deep Backfill | 9x daily | 3x daily | Quality-over-speed task; excessive frequency |
| Careerspan Scan Monitor | 12x daily | 4x daily | Scan results don't need hourly checks |
| Recall Bot Health Check | 48x daily (30 min) | Every 2 hours | Non-critical monitoring |
| Weekly Performance Dashboard | Sun 8:00 PM | Sun 9:00 AM | More useful for week planning |
| Thought Provoker Notification | Daily 8:00 AM | Review title | Generic title, unclear purpose |

---

## Dependency Risks (4)

Meeting agents reference prompt files that should be verified:

1. **MG-1** - `Prompts/Meeting Manifest Generation.prompt.md`
2. **MG-2** - `Prompts/Meeting Block Generation.prompt.md`
3. **MG-4** - `Prompts/Meeting Warm Intro Generation.prompt.md`
4. **MG-6** - Relies on `manifest.json` status field schema

**Action:** Verify these prompt files exist and schema is current before migration.

---

## Time Conflict Analysis

### Peak Hour: 8:00 AM - 9:00 AM
Four agents running simultaneously at 8:00 AM:
- Unified Morning Digest
- Script Execution Notification (Thought Provoker)
- Sync Fitbit Workouts & Weekly Summary
- Meeting agents (MG-1, MG-2 run at 9 AM slot)

### Morning Cluster (7:00 - 7:30 AM)
Three agents running at 7:00 AM:
- Morning Health Checkpoint
- Morning Task Briefing
- NYC Unified Luma Events Pipeline

Plus Daily Health Data Sync at 7:30 AM

**Recommendation:** Stagger morning agents to reduce resource contention.

---

## Temporary Agents

| Agent | Expiry | Purpose |
|-------|--------|---------|
| Next Play Survey Auto-Refresh | Jan 30, 2026 | Pre-event survey monitoring |
| Pulse Sentinel: b05-backfill-extended | COUNT=60 (~5 hours) | Build monitoring |
| Pulse Sentinel: meeting-system-migration | COUNT=50 (~4.2 hours) | Current build monitoring |

---

## Cornerstone Tasks (Protected ⇱)

These agents are marked as cornerstone and **cannot be deleted**:

1. **`0a2c48cf`** - Daily Database Backup
2. **`9b813d5c`** - Weekly Meeting Organization [v2]

---

## Recommendations Summary

| Priority | Action | Impact |
|----------|--------|--------|
| **High** | Delete 6 disabled agents | Clean slate, reduce confusion |
| **Medium** | Consolidate health checkpoints | Reduce 5 agents → 1 |
| **Medium** | Reduce monitoring frequencies | Lower API costs |
| **Low** | Consolidate meeting pipeline | Cleaner architecture |
| **Low** | Verify prompt file dependencies | Prevent migration failures |

---

## Appendix: Full Agent List

```
ACTIVE (27):
  Health: 0077f07e, 4e2a98ad, 59e5df9a, 4163c54c, c6ca2440, 22b8032a, 75764953
  Meetings: 0c53b7ba, 0a08e6a8, ce6995b8, f339ca26
  CRM/Deals: f0abd2aa, 806f7fcc
  Positions: 4ce1dca6
  System: 0a2c48cf, 9b813d5c, 8e05d139
  Task Management: 9b09d4a3, f5ec46f0
  Monitoring: 63ac046b, 632e3b97, f8c5ae47
  Events: 8828e095
  Stakeholders: b1495b64
  Context Intelligence: 13199a59
  Careerspan: 4d3ac290
  Digest: ad169b76
  Survey: 51c1e23e
  Performance: 6006fb46

DISABLED (8):
  Health: f58056ad, 529ed812
  Meetings: 5579f899, c7d010d5
  CRM/Deals: 259a13c8
  Positions: dd19d90e
```
