---
created: 2025-12-21
last_edited: 2025-12-21
version: 1.5
type: build_plan
status: ready
provenance: con_dKOZnDjzzmLfuL4I
---

# Plan: 2025 Travel Wrapped — Completed-Trips Rebuild

## Open Questions (must be answered before Phase 1)
- *(Resolved)* Counting unit: **segments**
- *(Resolved)* Completed trips definition: **exclude cancellations entirely from segment counts**
- *(Resolved)* City inclusion even without IATA: **Yes**
- *(Resolved)* Change counting: **each change email increments**
- *(Resolved)* Home grouping: treat **JFK/LGA/EWR** as **New York (city)**

## Checklist

### Phase 1 — Definitions + Normalization
- ☐ Implement canonical counting + summary recomputation from `trips[]` (no hardcoded summaries)
- ☐ Add city normalization layer (destinations + home=New York)
- ☐ Add cancellation exclusion policy + separate `change_events_count`
- ☐ Add airport stats (IATA-level) AND city stats (city-level)
- ☐ Add time-of-day insights: depart-most + return-most
- ☐ Regenerate `travel_metrics.json` and verify invariants

### Phase 2 — Data Acquisition Tightening (Gmail + Calendar)
- ☐ Update Gmail queries to prioritize major providers + aggregators
- ☐ Add Calendar corroboration pass (detect travel events not in Gmail)
- ☐ Produce a deterministic, reviewable manifest (CSV/MD) derived from raw events

### Phase 3 — Dashboard Rendering
- ☐ Update dashboard cards to reflect new definitions (segments vs cities vs airports)
- ☐ Add breakdown tables: Flights (segments), Airports (IATA), Cities (destinations)
- ☐ Add “Funny” stats (changes/rebookings count) without polluting core totals

---

## Nemawashi (Alternatives Considered)

### Option A: Gmail-only (cheap)
- **Pros:** Simple, viral, minimal permissions
- **Cons:** Misses trips booked outside email, weaker time-of-day accuracy
- **Verdict:** Rejected (accuracy pain already surfaced)

### Option B: Gmail + Calendar corroboration (balanced) ✅
- **Pros:** Catches missing trips; good for time-of-day and “returning” inference; still local
- **Cons:** Requires calendar integration access; may include non-travel events unless filtered
- **Verdict:** Selected

### Option C: Add Wallet/Bank transaction parsing (heavier)
- **Pros:** Highest completeness (captures Amex/Chase/travel portals)
- **Cons:** High privacy surface; messy; not reliably available
- **Verdict:** Deferred (future enhancement)

---

## Phase 1: Definitions + Normalization (Execute Next)

### Affected Files
- `N5/builds/travel-wrapped-2025/engine.py` (update to compute canonical metrics)
- `Travel Wrapped/2025/travel_metrics.json` (regenerate)
- `travel-wrapped-2025/src/pages/travel-wrapped.tsx` (update UI labels + cards)
- `N5/builds/travel-wrapped-2025/comprehensive_manifest.md` (regenerate from computed trips)

### Changes

**1.1 Canonical “Completed Trips” Policy**
- A segment counts iff `status == "Confirmed"` (or equivalent) and not cancelled.
- Cancellations do **not** contribute to totals.
- Changes/rebookings counted separately via `change_events_count`.

**1.2 City Stats vs Airport Stats**
- Maintain airport stats using IATA codes (e.g., JFK, ATL) for rankings.
- Maintain city stats using normalized city names.
- Define NYC airports: JFK/LGA/EWR → city = **New York**.

**1.3 Time-of-Day Insights**
- Determine travel time-of-day based on best-available timestamp:
  - Prefer explicit departure timestamp from email/calendar.
  - If absent, use email send time as proxy **with low-confidence flag**.
- Compute:
  - `depart_time_bucket_mode`
  - `return_time_bucket_mode` (segments where destination city == New York)

### Unit Tests
- **Invariant 1:** `summary.total_flights == count(trips where type=flight AND status=Confirmed)`
- **Invariant 2:** `summary.total_trains == count(trips where type=train AND status=Confirmed)`
- **Invariant 3:** `summary.total_destination_cities == count(unique(dest_city) for Confirmed segments)`
- **Invariant 4:** No cancelled segments appear in `trips[]` output (they must be in separate `incidents[]`)
- **Invariant 5:** NYC mapping: any segment with dest_airport in {JFK,LGA,EWR} yields dest_city == "New York"

---

## Success Criteria
- Dashboard and JSON agree on all totals (no mismatches).
- “Cities visited” reflects **unique destination cities from completed (non-cancelled) segments**.
- Cancellation/change information appears only as separate “incidental/funny” stat.
- Output remains portable: any Zo user can run the same prompt and get a coherent result.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Missing timestamps for time-of-day | Use calendar as primary timestamp source; fall back to email time with confidence flag |
| City inference errors | Keep city mapping minimal (NYC airports) and prefer explicit city strings from confirmations |
| Over-counting changes | Only count change-emails when subject/body indicates change/cancel/rebook |

---

## Trap Doors
- **Schema choice for metrics file** (`travel_metrics.json` structure). Changing later breaks dashboard + prompt sharing. Keep it stable and versioned.

