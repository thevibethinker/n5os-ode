---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_POTUJQd3ub2QU0XS
---

# Where's V: Multi-Segment Trip Support

## Open Questions

1. **Amtrak detection**: How do we reliably detect Amtrak bookings? Calendar events only, or also email confirmations from Amtrak?
2. **Hotel enrichment**: Should we auto-enrich hotel contact info (phone numbers) via web lookup, or require manual entry?
3. **Return flight detection**: For trips like Denver→Houston, there's no return to NYC - how should we handle "open-ended" trips?
4. **Update frequency**: Daily scan OK, or should we increase to 2x/day when trips are imminent?

## Checklist

### Phase 1: Data Model Update
- [ ] Extend `trip_store_v2.py` to support `type: "train"` segments alongside flights
- [ ] Add `confirmation` field at trip level (not just leg level)
- [ ] Add `hotels[]` array with `name`, `city`, `check_in`, `check_out`, `phone`, `confirmation`
- [ ] Update frontend to display train segments and hotel info

### Phase 2: Reliable Ingestion Script
- [ ] Create `Sites/wheres-v-staging/scripts/ingest_trips.py` - single entry point
- [ ] Query Gmail: JetBlue, United, Delta, Amtrak confirmations (query-based, not label-dependent)
- [ ] Query Calendar: cross-reference flight events, detect train trips
- [ ] Send to LLM for extraction (single prompt, no regex)
- [ ] Deduplicate against existing trips by confirmation code
- [ ] Write to `trips_v2.jsonl` and `legs_v2.jsonl`
- [ ] Update `last_scan.txt` with timestamp

### Phase 3: Scheduled Agent
- [ ] Create/update scheduled agent to run daily at 6 AM ET
- [ ] Agent calls `ingest_trips.py` via Zo conversation
- [ ] Log results to confirm what was added/updated

### Phase 4: Frontend Updates
- [ ] Show train segments with 🚂 icon
- [ ] Display hotel info on trip cards
- [ ] Show multiple upcoming trips, not just the nearest one

## Phase 1: Data Model Update

**Affected Files:**
- `Sites/wheres-v-staging/scripts/trip_store_v2.py`
- `Sites/wheres-v-staging/data/trips_v2.jsonl`
- `Sites/wheres-v-staging/data/legs_v2.jsonl`

**Changes:**
1. Update `create_leg()` to accept `type` parameter ("flight" or "train")
2. Add hotel support at the leg or trip level
3. Ensure backward compatibility with existing data

**Unit Tests:**
- Create a trip with mixed flight+train segments
- Verify state machine handles train arrival times correctly

## Phase 2: Reliable Ingestion Script

**Affected Files:**
- `Sites/wheres-v-staging/scripts/ingest_trips.py` (NEW)
- `Sites/wheres-v-staging/scripts/ingest_gmail.py` (UPDATE)
- `Sites/wheres-v-staging/scripts/ingest_calendar.py` (UPDATE)

**Changes:**

### `ingest_trips.py` - Main orchestrator
```python
# Pseudocode
1. Query Gmail for flight confirmations (last 90 days, next 60 days)
   - JetBlue: from:jetblue.com subject:(confirmation OR itinerary)
   - United: from:united.com subject:(confirmation OR receipt)
   - Delta: from:delta.com subject:(confirmation)
   - Amtrak: from:amtrak.com subject:(confirmation)
   
2. Query Gmail for hotel confirmations
   - Marriott, Hilton, Hyatt, IHG, Airbnb, etc.
   
3. Query Calendar for travel events (cross-reference)

4. Send ALL raw data to LLM with extraction prompt:
   - Filter to V's trips only (exclude family)
   - Extract multi-segment trips
   - Include train segments
   - Include hotel details with contact info

5. Deduplicate against existing trips (by confirmation code)

6. Write new/updated trips to store

7. Update last_scan.txt
```

**LLM Extraction Prompt** (key elements):
- V lives in NYC (JFK/LGA/EWR)
- ONLY V's trips (exclude Sandeep, other family)
- Multi-segment trips are ONE trip (Denver→Houston)
- Include train segments (Amtrak)
- Include hotels with contact details

**Unit Tests:**
- Mock Gmail/Calendar data, verify extraction output
- Test deduplication logic

## Phase 3: Scheduled Agent

**Affected Files:**
- Scheduled agent (via `create_agent` tool)

**Agent Instruction:**
```
Run the Where's V trip ingestion:

1. Call ingest_trips.py with appropriate Gmail/Calendar queries
2. Use LLM to extract V's trips from raw email/calendar data  
3. Update trips_v2.jsonl with any new trips
4. Log: "Where's V scan complete. Added X trips, updated Y trips."

Reference: file 'Sites/wheres-v-staging/scripts/ingest_trips.py'
```

**RRULE:** `FREQ=DAILY;BYHOUR=6;BYMINUTE=0` (6 AM ET daily)

## Phase 4: Frontend Updates

**Affected Files:**
- `Sites/wheres-v-staging/src/App.tsx`
- `Sites/wheres-v-staging/src/components/HeroHome.tsx`
- `Sites/wheres-v-staging/src/components/TripCard.tsx` (NEW)

**Changes:**
1. Display train segments with 🚂 icon
2. Show hotel info (name, check-in/out dates)
3. List multiple upcoming trips on home screen
4. Improve "at destination" state to show hotel details

## Success Criteria

1. ✅ Running the ingestion picks up ALL V's upcoming trips (Raleigh, Denver, Houston, San Juan)
2. ✅ Multi-segment trips (Denver→Houston) display correctly
3. ✅ Train segments (Amtrak) display with 🚂 icon
4. ✅ Hotels display with contact info when available
5. ✅ Daily scheduled scan keeps data current without manual intervention
6. ✅ Family members' trips are correctly excluded

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Gmail API rate limits | Batch queries, cache results, scan daily not hourly |
| LLM extraction errors | Log raw inputs for debugging, manual override capability |
| Amtrak emails not parseable | Fall back to calendar events for train detection |
| Hotel contact info unavailable | Leave phone field null, enrich later if needed |

## Trap Doors (Irreversible Decisions)

⚠️ **Data format change**: If we change `legs_v2.jsonl` schema, need migration script for existing data.

## Alternatives Considered

1. **Regex-based parsing** - REJECTED: Too fragile for varied email formats
2. **Label-based Gmail filtering** - REJECTED: Labels not reliably applied
3. **TripIt integration** - Considered: Could supplement email parsing, but adds dependency
