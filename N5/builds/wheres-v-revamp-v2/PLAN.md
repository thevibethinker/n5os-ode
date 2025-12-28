---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.1
type: build-plan
provenance: con_JVzbW0S6LreS3vRW
---

# Where's V: Simplified Parent-Friendly Tracker

## Checklist

### Phase 1: Data Layer
- [x] Clean up trips.jsonl schema (simplify to essentials)
- [x] Create trip_store.py with add/update/get_active functions

### Phase 2: LLM Prompts
- [x] Create flight_filter.prompt.md (cheap model: "is this a flight confirmation for V?")
- [x] Create flight_extractor.prompt.md (smart model: extract flight details)

### Phase 3: Email Scanner Agent
- [x] Create scheduled agent: daily scan of "Travel Reservations" label
- [x] Agent uses tiered LLM approach (filter → extract → store)

### Phase 4: Frontend Simplification
- [x] Strip App.tsx to single-page status display
- [x] Show: current status, flight details, ETA
- [x] Remove all admin/trip management UI

### Phase 5: API Simplification
- [x] Single endpoint: GET /api/status
- [x] Returns: { status, flight, departure, arrival, eta }

### Phase 6: Deploy & Test
- [x] Register user service (https://wheres-v-va.zocomputer.io)
- [ ] Test with real email from Travel Reservations
- [x] Verify API endpoint works

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Gmail: Travel Reservations                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Scheduled Agent (daily, 6 AM ET)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Step 1: Query last 7 days of Travel Reservations        │   │
│  │  Step 2: For each email → Cheap LLM: "Flight for V?"     │   │
│  │  Step 3: If yes → Smart LLM: Extract flight details      │   │
│  │  Step 4: Update trips.jsonl                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Sites/wheres-v/                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ trips.jsonl │ ←→ │   api.ts    │ ←→ │   Parent Page       │  │
│  │   (data)    │    │ GET /status │    │   "V is in NYC"     │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Affected Files

### Phase 1: Data Layer
- `Sites/wheres-v-staging/data/trips.jsonl` — simplify schema
- `Sites/wheres-v-staging/scripts/trip_store.py` — new, replaces trip_manager.py

### Phase 2: LLM Prompts
- `Prompts/wheres-v/flight_filter.prompt.md` — new
- `Prompts/wheres-v/flight_extractor.prompt.md` — new

### Phase 3: Email Scanner Agent
- Scheduled task created via `create_scheduled_task`

### Phase 4: Frontend
- `Sites/wheres-v-staging/src/App.tsx` — simplify to status-only

### Phase 5: API
- `Sites/wheres-v-staging/server/api.ts` — simplify to single endpoint

### Phase 6: Deploy
- User service: `wheres-v`

---

## Decisions Made

1. **LLM over Python for parsing** — Flight emails are too varied for regex
2. **Tiered LLM approach** — Cheap model filters, smart model extracts
3. **Use existing "Travel Reservations" label** — No new labeling workflow needed
4. **Daily scan at 6 AM ET** — Catches overnight booking confirmations
5. **7-day lookback** — Catches emails that might have been missed

---

## Open Questions (Resolved)

| Question | Answer |
|----------|--------|
| Travel sources | JetBlue, Delta, United, American, Expedia, Hotels.com, OneKey, Chase Travel, Amex Travel, Airbnb, Amtrak |
| Email label | Use existing "Travel Reservations" (Label_4999101574974696630) |
| Disambiguation | LLM prompt explicitly asks "is this for V (not parents, not wife)?" |
| Parent access | TBD during Phase 4 (likely bookmarked URL) |
| Parent timezone | ET (same as V) |

---

## Unit Tests

### Phase 1
- [ ] trip_store.py: add_trip creates entry
- [ ] trip_store.py: get_active_trip returns current/upcoming trip

### Phase 3
- [ ] Agent correctly filters non-flight emails
- [ ] Agent correctly extracts flight details from sample email

### Phase 5
- [ ] GET /api/status returns correct format
- [ ] Status correctly reflects trip state (home/departing/flying/arrived)




