---
created: 2026-01-11
last_edited: 2026-01-11
version: 1.0
provenance: con_oW7mu5kHUmEdKTAP
---

# Build Plan: Raleigh Flight Search & Booking Prep (raleigh-trip-search)

Search for round-trip flights between NYC and Raleigh (RDU) for Jan 22-24, 2026, strictly adhering to V's baseline preferences and the friend's landing constraints.

## Open Questions
- Is JetBlue (B6) or Delta (DL) currently operating JFK/LGA to RDU with nonstops? (Search will confirm)
- Are there specific arrival time constraints for the return flight? (Friend's red-eye lands at 8-9 AM, but V's preference is for a "midday return")

## Checklist
- [ ] Phase 1: Search & Analysis
  - [ ] Run `google_flights.py` with `--booking-link`
  - [ ] Filter by baseline carriers (JetBlue/Delta)
  - [ ] Enforce "no land before noon" constraint on Jan 22
- [ ] Phase 2: Selection & Reporting
  - [ ] Select top 3 departure options (midday/afternoon Jan 22)
  - [ ] Select top 3 cheapest midday return options (Jan 24)
  - [ ] Verify "Main Cabin" (non-basic) availability

## Success Criteria
- Three viable outbound options landing after 12:00 PM ET on Jan 22.
- Three cheapest midday return options on Jan 24.
- Priority given to JetBlue (JFK override) or Delta (LGA).
- Direct booking links included for all options.

## Phase 1: Search & Analysis
**Affected Files:** `N5/builds/raleigh-trip-search/search_results.json` (temporary)
**Changes:** Execute Google Flights integration script with specific flags.
**Unit Tests:** Verify results include JetBlue/Delta and exclude Spirit/Frontier.

## Phase 2: Selection & Reporting
**Affected Files:** Chat response
**Changes:** Synthesize results into the Route Report format defined in the prompt.
**Unit Tests:** Match landing constraints (> 12:00 PM on 22nd) and return timing (midday on 24th).

## Risks & Mitigations
- **Risk:** No JetBlue/Delta nonstops available at requested times.
- **Mitigation:** Present best available nonstops from secondary carriers or 1-stop options if necessary, highlighting the trade-off.
- **Risk:** Prices for Main Cabin are significantly higher than Basic.
- **Mitigation:** Explicitly label prices as Main Cabin (RT) to avoid confusion.

## Alternatives Considered (Nemawashi)
1. **LGA vs JFK:** I will prioritize JFK if JetBlue is the carrier, otherwise LGA.
2. **EWR:** Only considered if JFK/LGA options are highly inconvenient or non-existent.

## Trap Doors
- Booking a non-refundable flight (mitigated by looking for Main Cabin/JetBlue flexible fares).

