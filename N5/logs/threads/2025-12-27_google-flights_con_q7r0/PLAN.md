---
created: 2025-12-21
last_edited: 2025-12-21
version: 1.2
type: build_plan
status: ready
provenance: con_q7r0aONFiaolYKUe
---

# Plan: Google Flights "Route Report" Foundation

**Objective:** Build a Python-based travel intelligence engine that performs natural language flight searches filtered by Vrijen's baseline preferences, returning a "Route Report" with historical price analysis.

**Trigger:** Vrijen's request to integrate SerpApi Google Flights into Zo for personalized, intelligent flight search and monitoring.

**Key Design Principle:** Deterministic Foundation (Python) + Squishy Intelligence (LLM). Use the environment's `SERPAPI_PRIVATE_KEY` for authentication.

---

## Open Questions
- [x] **API Key**: Verified as `SERPAPI_PRIVATE_KEY` in the environment.
- [x] **Baselines**: Airport priority (LGA > JFK > EWR), JetBlue/Delta focus, Spirit/Frontier exclusion.

---

## Checklist

### Phase 1: Baseline & Core Client
- ☐ Create `file 'Knowledge/reference/travel_baseline.yaml'` with Vrijen's preferences.
- ☐ Create `file 'Integrations/google_flights.py'` - The core execution script.
- ☐ Test: Run a simple search for "NYC to LAX" and verify JetBlue/JFK are prioritized and Spirit/Frontier are purged.

### Phase 2: TripIntent & Route Report
- ☐ Create `file 'N5/templates/travel/route_report.md'` - The structured output template.
- ☐ Implement `TripIntent` update logic: At end of search, prompt V for baseline updates.
- ☐ Test: Generate a full "Route Report" for a real destination (e.g., "NYC to London in March").

---

## Phase 1: Baseline & Core Client

### Affected Files
- `Knowledge/reference/travel_baseline.yaml` - CREATE - Stores airport/airline rankings and cabin rules.
- `Integrations/google_flights.py` - CREATE - Primary CLI tool for SerpApi interaction.
- `N5/builds/google-flights/STATUS.md` - UPDATE - Tracking progress.

### Changes

**1.1 Preference Codification:**
Store the following in `travel_baseline.yaml`:
- Airports: `[LGA, JFK, EWR]` (descending order).
- Preferred Airlines: `[JetBlue, Delta]`.
- Excluded Airlines: `[Spirit, Frontier]`.
- Cabin: `Economy` (Filtered for `exclude_basic: true`).

**1.2 Deterministic Search Script:**
`google_flights.py` will:
1. Load `SERPAPI_PRIVATE_KEY`.
2. Map natural language dates/locations (via LLM) to IATA codes and YYYY-MM-DD.
3. Call SerpApi Google Flights engine.
4. Filter results: Purge Excluded, Sort by Airport Priority + Airline Preference.

---

## Success Criteria
1. One-command search: `python3 Integrations/google_flights.py --query "NYC to London March 1-7"`.
2. Output follows "Route Report" format with Historical Price Analysis (Typical/Low/High).
3. System learns: After search, it asks "Should I update your baseline with [new insight]?"

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API Credit Usage | Cache search results in `CONVERSATION_WORKSPACE` for 24h. |
| IATA Hallucination | Use a lookup table or verify airport IDs before calling API. |
| Inflexible Baselines | Use the `TripIntent` protocol to update YAML at end of every session. |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. **"Shadow Tracking"**: Don't just report; offer to spawn a scheduled agent immediately if the current price is "High".
2. **"Points over Price"**: Add a specific flag for "Optimize for TrueBlue" to prioritize JFK-JetBlue even when 15% more expensive.

### Incorporated:
- **Shadow Tracking**: Added as a suggestion at the end of the Route Report.
- **TripIntent Learning**: Dynamic baseline updates to prevent manual config fatigue.

### Rejected (with rationale):
- **Automated Booking**: Too high risk for Phase 1 (Trap Door). Focus on intelligence first.

