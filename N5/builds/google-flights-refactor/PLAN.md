# Plan: Google Flights Integration Refactor
**Slug:** google-flights-refactor
**Status:** In Progress
**Persona:** Vibe Builder

## Checklist
- [x] Create unit tests for baseline loading and IATA mapping
- [x] Implement `--from` and `--to` parameterization
- [x] Remove hardcoded "NYC Metro" and fixed origin logic
- [x] Add time-of-day preference scoring (`morning`, `midday`, `evening`)
- [x] Add aircraft type filtering (e.g., `--aircraft airbus`)
- [x] Update documentation and examples

## Affected Files
- `Integrations/google_flights.py`
- `Knowledge/reference/travel_baseline.yaml` (read-only verification)

## Phase 1: Infrastructure & Testing
- Create `/home/workspace/Integrations/tests/test_google_flights.py`
- Verify baseline loading works as expected
- Expand `IATA_MAP` significantly

## Phase 2: Core Refactor
- Modify `multi_airport_search` to accept `departure` and `arrival`
- Update CLI `argparse` to include `--from`, `--departure-time`, `--aircraft`
- Update `score_flight` to include time-of-day bonuses

## Phase 3: Validation
- Run test search from SAN → JFK
- Verify Airbus filtering works
- Verify "Midday" scoring works

---
**Unit Tests:**
- `test_normalize_airport_code`: Verifies "San Diego" -> "SAN"
- `test_score_flight_time`: Verifies "midday" preference increases score
- `test_multi_airport_search_direction`: Verifies correct origin/destination flow


