---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
type: build_plan
status: ready
provenance: con_FnY8AtrJwbVpnq6I
---

# Plan: Where's V: Trip & Leg System

**Objective:** Transform "Where's V" from single-flight tracker into trip-aware system with Calendar+Gmail ingestion, distinguishing between Trips (NYC→somewhere→NYC) and Legs (individual flight segments), with time-based UX states.

**Trigger:** V wants parents to see richer travel context—last trip, upcoming trip, legs within trips, hotel info, and smart pre-departure details starting 7 days before any leg.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved during conversation with V -->
- [x] Pre-departure trigger timing? → **7 days**, regardless of domestic/international
- [x] Hotel info display? → Show **prominently at destination**
- [x] Return flight handling? → Own **leg with own pre-departure state**
- [x] Trip detection logic? → NYC is home base; **Trip = departure from NYC until return to NYC**
- [x] Multi-city handling? → Each flight is a **Leg**; Legs grouped into **Trip**

---

## Alternatives Considered (Nemawashi)

### Alternative A: Regex/Rule-Based Parsing
- Parse Gmail flight confirmations and Calendar events with regex patterns
- **Rejected:** Brittle, breaks on format changes, misses edge cases

### Alternative B: LLM-Based Extraction (SELECTED ✓)
- Send raw Calendar events + Gmail snippets to Zo via `/zo/ask` API
- LLM extracts structured Trip/Leg data with understanding of context
- **Selected:** More robust, handles variations, can infer city names from airport codes

### Alternative C: External Flight API (FlightAware, etc.)
- Query flight status APIs for real-time data
- **Deferred:** Nice-to-have for Phase 2; adds complexity and cost

---

## Trap Doors 🚪

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| JSONL storage format | ✅ Easy to migrate | Keep simple for now |
| LLM for extraction | ✅ Reversible | Can swap to regex if LLM unreliable |
| 7-day pre-departure trigger | ✅ Config change | Hardcoded but trivial to update |
| NYC as home base | ⚠️ Medium | Hardcoded; would need refactor if V moves |

---

## Checklist

### Phase 1: Data Model & Ingestion Pipeline
- ☑ Create new `trip_store_v2.py` with Trip/Leg model
- ☑ Create `ingest_calendar.py` - fetch travel events from Google Calendar
- ☑ Create `ingest_gmail.py` - fetch flight confirmations from Gmail
- ☑ Create `extract_trips.py` - LLM-based extraction orchestrator
- ☑ Test: Manual trigger produces valid Trip/Leg JSON from real Calendar data

### Phase 2: Backend API Updates
- ☑ Update `server.ts` with new endpoints (`/api/trips`, `/api/current-state`)
- ☑ Implement state machine logic (home → pre-departure → in-transit → at-destination)
- ☑ Add last-trip and next-trip queries
- ☑ Test: `/api/current-state` returns correct state based on mock trip data

### Phase 3: Frontend UX States
- ☑ Refactor `App.tsx` for new state machine
- ☑ Implement Hero component variants (home, pre-departure, in-transit, at-destination)
- ☑ Add trip context display (leg X of Y, hotel info, return date)
- ☑ Rebuild and deploy
- ☑ Test: Visual verification of all 4 states with mock data

---

## Phase 1: Data Model & Ingestion Pipeline

### Affected Files
- `Sites/wheres-v-staging/scripts/trip_store_v2.py` - CREATE - New Trip/Leg data model
- `Sites/wheres-v-staging/scripts/ingest_calendar.py` - CREATE - Google Calendar fetcher
- `Sites/wheres-v-staging/scripts/ingest_gmail.py` - CREATE - Gmail flight confirmation fetcher
- `Sites/wheres-v-staging/scripts/extract_trips.py` - CREATE - LLM extraction orchestrator
- `Sites/wheres-v-staging/data/trips_v2.jsonl` - CREATE - New data file

### Changes

**1.1 New Data Model (`trip_store_v2.py`):**

```python
# Trip: Container for a round-trip journey
Trip = {
    "id": "trip_20251227...",
    "home_base": "NYC",                    # Constant for now
    "status": "upcoming|active|complete",
    "created_at": "ISO timestamp",
    "legs": ["leg_id_1", "leg_id_2", ...], # References to Leg IDs
    "sources": {                           # For debugging/audit
        "calendar_event_ids": [],
        "gmail_message_ids": []
    }
}

# Leg: Individual flight segment within a trip  
Leg = {
    "id": "leg_20251227...",
    "trip_id": "trip_...",                 # Parent trip reference
    "sequence": 1,                         # Order within trip (1, 2, 3...)
    "flight": {
        "number": "UA123",
        "departure_airport": "JFK",
        "arrival_airport": "MIA",
        "departure_time": "ISO timestamp",
        "arrival_time": "ISO timestamp"
    },
    "destination_city": "Miami",           # Human-readable
    "hotel": {                             # Optional
        "name": "Hotel Name",
        "address": "123 Main St",
        "check_in": "ISO date",
        "check_out": "ISO date"
    } | null
}
```

**1.2 Calendar Ingestion (`ingest_calendar.py`):**
- Use `use_app_google_calendar` via Zo's app tools
- Fetch events from primary calendar with keywords: "flight", "travel", airline names
- Look back 30 days (for last trip) and forward 60 days (for upcoming)
- Output: Raw event data as JSON for LLM processing

**1.3 Gmail Ingestion (`ingest_gmail.py`):**
- Use `use_app_gmail` via Zo's app tools  
- Search for flight confirmation emails (from: airlines, subject: confirmation/itinerary)
- Look back 30 days, forward 60 days
- Output: Raw email snippets as JSON for LLM processing

**1.4 LLM Extraction (`extract_trips.py`):**
- Orchestrates Calendar + Gmail ingestion
- Sends combined data to Zo via `/zo/ask` API with extraction prompt
- Extraction prompt asks for structured Trip/Leg output
- Handles Trip grouping logic: legs departing from non-NYC after arriving at non-NYC = same trip
- Stores results via `trip_store_v2.py`

### Unit Tests
- `python3 trip_store_v2.py test` - Create/read/query trips and legs
- `python3 extract_trips.py --dry-run` - Show what would be extracted without saving

---

## Phase 2: Backend API Updates

### Affected Files
- `Sites/wheres-v-staging/server.ts` - UPDATE - Add new endpoints
- `Sites/wheres-v-staging/scripts/trip_store_v2.py` - UPDATE - Add state machine logic

### Changes

**2.1 State Machine Logic:**

```python
def get_current_state() -> dict:
    """
    Returns current UX state based on trips/legs and current time.
    
    States:
    - home: No active trip, or next leg departure >7 days away
    - pre_departure: Next leg departs within 7 days
    - in_transit: Currently between leg departure and arrival times
    - at_destination: Arrived at non-NYC location, not yet departed on next leg
    
    Returns:
    {
        "state": "home|pre_departure|in_transit|at_destination",
        "current_leg": Leg | null,
        "current_trip": Trip | null,
        "last_trip": Trip | null,      # Most recent completed trip
        "next_trip": Trip | null,       # Next upcoming trip (if state=home)
        "message": "Human-readable status",
        "context": {                    # Additional display data
            "leg_number": 1,
            "total_legs": 2,
            "return_date": "ISO date",
            "hotel": {...} | null
        }
    }
    """
```

**2.2 New API Endpoints:**
- `GET /api/current-state` - Returns full state machine output (replaces `/api/status`)
- `GET /api/trips` - List all trips (for debugging/admin)
- `POST /api/refresh` - Trigger re-ingestion from Calendar/Gmail

**2.3 Backward Compatibility:**
- Keep `/api/status` working, map to new state machine output

### Unit Tests
- `curl localhost:54179/api/current-state` - Returns valid state JSON
- Mock different times and verify correct state transitions

---

## Phase 3: Frontend UX States

### Affected Files
- `Sites/wheres-v-staging/src/App.tsx` - UPDATE - Major refactor for state machine
- `Sites/wheres-v-staging/src/components/HeroHome.tsx` - CREATE - Home state hero
- `Sites/wheres-v-staging/src/components/HeroPreDeparture.tsx` - CREATE - Pre-departure hero
- `Sites/wheres-v-staging/src/components/HeroInTransit.tsx` - CREATE - In-flight hero
- `Sites/wheres-v-staging/src/components/HeroAtDestination.tsx` - CREATE - At destination hero
- `Sites/wheres-v-staging/src/components/TripContext.tsx` - CREATE - Leg X of Y, return info
- `Sites/wheres-v-staging/index.html` - UPDATE - Already done (title fix)

### Changes

**3.1 Hero Components:**

| State | Hero Content | Secondary Content |
|-------|--------------|-------------------|
| `home` | "V is home in NYC" | Last trip summary ← / Next trip preview → |
| `pre_departure` | "V is heading to Miami in 3 days" | Flight details, hotel info, leg context |
| `in_transit` | "V is in the air → Miami" | Flight progress, ETA, leg context |
| `at_destination` | "V is in Miami" | Hotel info, next leg preview, return date |

**3.2 App.tsx Refactor:**
- Fetch from `/api/current-state` instead of `/api/status`
- Render appropriate Hero component based on `state` field
- Pass full context to components for rich display

**3.3 Visual Design:**
- Keep existing color scheme (green=home, yellow=departing, blue=flying, purple=arrived)
- Add subtle animations for state transitions
- Mobile-responsive (already using Tailwind)

### Unit Tests
- Build succeeds: `bun run build`
- Visual check: Screenshot all 4 states (requires mock data)
- Responsive check: Mobile viewport renders correctly

---

## Success Criteria

1. **Ingestion works:** Running `python3 extract_trips.py` pulls real data from V's Calendar and creates Trip/Leg records
2. **State machine correct:** `/api/current-state` returns appropriate state based on current time vs trip data
3. **Frontend displays all states:** Each of the 4 hero states renders correctly with mock data
4. **Trip grouping works:** Multi-leg trips (NYC→MIA→NYC) are grouped as single Trip with 2 Legs
5. **Parent-friendly:** Non-technical users (V's parents) can understand current status at a glance

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Calendar/Gmail parsing fails | LLM-based extraction is robust; fallback to manual entry |
| LLM extraction hallucinations | Validate output schema strictly; log raw inputs for debugging |
| Timezone confusion | Store all times as UTC; convert to display timezone on frontend |
| No trips in Calendar | Graceful fallback to "home" state; show empty last/next trip |
| Rate limits on `/zo/ask` | Batch requests; cache results; only refresh on demand or schedule |

---

## Level Upper Review

*Skipped for this build - straightforward extension of existing system.*

---

## Execution Notes

**Recommended execution order:**
1. Phase 1 first (get data flowing)
2. Phase 2 (backend can be tested with mock data)
3. Phase 3 (frontend polish)

**Builder should:**
- Test each phase before proceeding to next
- Use V's real Calendar data for Phase 1 testing (with V's permission)
- Rebuild + restart service after each phase

---

## Handoff to Builder

Plan is complete and ready for execution.

**Start with:** Phase 1
**Plan location:** `file 'N5/builds/wheres-v-trips/PLAN.md'`




