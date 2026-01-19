---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_POTUJQd3ub2QU0XS
---

# AAR: Where's V Multi-Segment Trip Support

**Date:** 2026-01-19  
**Duration:** ~45 minutes  
**Type:** 🏗️ Build / 🛠️ Repair  
**Outcome:** ✅ Success

## Summary

Fixed the Where's V travel tracker which was showing stale Puerto Rico trip data instead of imminent trips. Implemented multi-segment trip support (flights + Amtrak), enriched hotel data with contact details, and transitioned from scheduled agents to manual refresh per V's preference.

## What Was Accomplished

### Core Fixes
1. **Diagnosed stale data** — Site was showing Puerto Rico (Feb 20) instead of Raleigh trip (Jan 22, 3 days away)
2. **Fixed trip routing** — Corrected leg sequence: JFK→RDU, RDU→BOS, Amtrak BOS→NYC (was backwards)
3. **Website now shows** "V is preparing for Raleigh - 3 days away" ✓

### Data Extraction
- **5 JetBlue flights** extracted via LLM: B6 0285, B6 0984, B6 1297, B6 1803, B6 1104
- **1 United flight**: UA 475 DEN→IAH
- **2 hotels with full contact info**:
  - Highline Vail - DoubleTree (+1-970-476-2739)
  - InterContinental Houston Medical Center (+1-713-422-2779)

### Infrastructure Changes
- **Deleted 3 scheduled agents** — No more automated runs per V's request
- **Created manual refresh flow** — `refresh.py` script ready for "refresh Where's V" command
- **Created email pattern registry** — `config/email_patterns.yaml` for quick future searches

## Key Learnings

### LLM > Regex for Email Parsing
Airline confirmation emails have enormous format variability. LLM extraction handles this gracefully while regex would require constant maintenance. The "wide net + LLM filter" approach proved much more reliable than precise Gmail queries.

### Trip Destination Semantics Matter
The original system showed first leg destination (Boston) instead of trip purpose destination (Raleigh). Users think in terms of "where am I going" not "what's my first flight".

### Pattern Registry Approach
V books through a finite set of sources (JetBlue, United, Delta, Marriott, Hilton, etc.). Maintaining a pattern registry enables quick, targeted searches without re-discovering query patterns each time.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| No scheduled agents | V prefers manual control; avoids stale data from failed runs |
| Broad query + LLM filter | More reliable than precise queries for variable email formats |
| Store hotel phone numbers | Parents need contact info for emergencies |
| Multi-segment support | V travels complex itineraries (flight + train combos) |

## Files Created/Modified

**New:**
- `file 'Sites/wheres-v-staging/scripts/refresh.py'` — Manual refresh orchestration
- `file 'Sites/wheres-v-staging/scripts/ingest_trips.py'` — Trip ingestion logic
- `file 'Sites/wheres-v-staging/config/email_patterns.yaml'` — Booking source patterns

**Modified:**
- `file 'Sites/wheres-v-staging/data/trips_v2.jsonl'` — Updated trip data
- `file 'Sites/wheres-v-staging/data/legs_v2.jsonl'` — Corrected leg sequences with hotels
- `file 'N5/capabilities/internal/wheres-v-revamp-v2.md'` — Updated last_verified

## Open Items

- **Amtrak booking** — BOS→NYC not yet booked; will test ingestion when booked
- **Puerto Rico hotel** — Not yet booked; will test when booked
- **Pattern validation** — Registry needs testing against actual future bookings

## Trigger for Follow-Up

When V says "refresh Where's V" — run the full Gmail → LLM extraction → trip store update flow.
