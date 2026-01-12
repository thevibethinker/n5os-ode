---
created: 2026-01-11
last_edited: 2026-01-11
version: 2.0
type: build_plan
status: ready_for_builder
provenance: con_an9JiKXgrCY551K6
---

# Flight Search Prompt & Integration Refactor

## Open Questions
- [x] Can we get direct airline booking links? **YES** — 3-step API flow works
- [x] How does multi-city work? **Native support** via `type=3` + `multi_city_json`
- [ ] Should we cache booking tokens to reduce API calls? (defer to v2)

## Root Cause Analysis

**Issue 1: Price confusion ($472 vs $313)**
- API returns correct round-trip prices when `return_date` is provided
- LLM was running separate one-way searches and summing prices
- Fix: Default to round-trip, add clear RT/OW labels

**Issue 2: No booking links**
- Previously assumed "too complicated"
- Investigation revealed clean 3-step flow:
  1. Initial search → `departure_token`
  2. Search with departure_token → `booking_token`
  3. Search with booking_token → `booking_options` with redirect URL
  4. POST to redirect URL → meta refresh contains **direct airline URL**

## Checklist

### Phase 1: Price Display & Trip Type Labels
- [x] Add `(RT)` or `(OW)` suffix to all price displays
- [x] Add trip type header in report output
- [x] Verify price matches actual round-trip fare
- [x] Unit test: RT search returns RT prices

### Phase 2: Default Round-Trip + Multi-City Support
- [x] Change default behavior: assume round-trip unless `--one-way` flag
- [x] Add `--one-way` flag for explicit one-way searches
- [x] Add `--multi-city` flag with JSON input for multi-leg trips
- [x] Update prompt instructions to reflect new defaults
- [x] Unit test: Default search is round-trip
- [x] Unit test: Multi-city with 3 legs

### Phase 3: Direct Airline Booking Links
- [x] Implement `get_booking_url(departure_token, booking_token)` function
- [x] Extract airline URL from meta refresh in redirect page
- [x] Add `--booking-link` flag to include booking URLs in output
- [x] Handle cases where airline URL isn't available (fallback to Google Flights link)
- [x] Unit test: Booking link for JetBlue flight
- [x] Unit test: Booking link for Delta flight

---

## Phase 1: Price Display & Trip Type Labels

### Affected Files
- `Integrations/google_flights.py`

### Changes

**1. Add trip type to output header**
```python
# In generate_report() function
trip_type = "Round Trip" if return_date else "One Way"
print(f"Date: {outbound_date}" + (f" → {return_date} ({trip_type})" if return_date else f" ({trip_type})"))
```

**2. Add RT/OW suffix to prices**
```python
# In format_flight() or wherever price is displayed
price_suffix = "(RT)" if search_params.get("return_date") else "(OW)"
print(f"${price} {price_suffix}")
```

### Unit Tests
```bash
# Test 1: Round-trip shows RT label
python3 Integrations/google_flights.py search --to RDU --date 2026-01-22 --return-date 2026-01-24 | grep -q "(RT)"

# Test 2: One-way shows OW label  
python3 Integrations/google_flights.py search --to RDU --date 2026-01-22 --one-way | grep -q "(OW)"
```

---

## Phase 2: Default Round-Trip + Multi-City Support

### Affected Files
- `Integrations/google_flights.py`
- `Prompts/Flight Search.prompt.md`

### Changes

**1. Change argument defaults**
```python
# Current: return_date is optional, one-way is default
# New: return_date prompts if missing, round-trip is default

parser.add_argument("--one-way", action="store_true", help="Search one-way only")
parser.add_argument("--multi-city", type=str, help="JSON array of legs: [{from, to, date}, ...]")
```

**2. Add logic to handle trip types**
```python
if args.multi_city:
    # Parse JSON, set type=3, use multi_city_json param
    legs = json.loads(args.multi_city)
    params["type"] = "3"
    params["multi_city_json"] = json.dumps(legs)
elif args.one_way:
    # No return_date
    pass
else:
    # Default: round-trip
    if not args.return_date:
        # Could prompt or require, for now require
        raise ValueError("Round-trip requires --return-date. Use --one-way for one-way search.")
```

**3. Update prompt instructions**
```markdown
## Usage
- **Round-trip (default):** `--date <outbound> --return-date <return>`
- **One-way:** `--date <date> --one-way`
- **Multi-city:** `--multi-city '[{"from":"JFK","to":"LAX","date":"2026-01-22"},{"from":"LAX","to":"SFO","date":"2026-01-25"}]'`
```

### Unit Tests
```bash
# Test 1: Missing return-date without --one-way should error
python3 Integrations/google_flights.py search --to RDU --date 2026-01-22 2>&1 | grep -q "requires --return-date"

# Test 2: --one-way works without return-date
python3 Integrations/google_flights.py search --to RDU --date 2026-01-22 --one-way | grep -q "(OW)"

# Test 3: Multi-city parses correctly
python3 Integrations/google_flights.py search --multi-city '[{"from":"JFK","to":"RDU","date":"2026-01-22"},{"from":"RDU","to":"JFK","date":"2026-01-24"}]' | grep -q "Multi"
```

---

## Phase 3: Direct Airline Booking Links

### Affected Files
- `Integrations/google_flights.py`

### Changes

**1. Add booking link retrieval function**
```python
async def get_booking_url(session, base_params: dict, departure_token: str, return_flight_index: int = 0) -> str | None:
    """
    3-step flow to get direct airline booking URL.
    
    Step 1: Already done (we have departure_token from initial search)
    Step 2: Get return options with booking_token
    Step 3: Get booking_options with redirect URL
    Step 4: POST to redirect, extract airline URL from meta refresh
    """
    # Step 2: Get return flights
    params2 = {**base_params, "departure_token": departure_token}
    async with session.get(SERPAPI_BASE, params=params2) as resp:
        data2 = await resp.json()
    
    return_flights = data2.get("other_flights", [])
    if not return_flights or return_flight_index >= len(return_flights):
        return None
    
    booking_token = return_flights[return_flight_index].get("booking_token")
    if not booking_token:
        return None
    
    # Step 3: Get booking options
    params3 = {**base_params, "booking_token": booking_token}
    async with session.get(SERPAPI_BASE, params=params3) as resp:
        data3 = await resp.json()
    
    booking_options = data3.get("booking_options", [])
    if not booking_options:
        return None
    
    # Find airline direct booking (prefer over 3rd party)
    for opt in booking_options:
        together = opt.get("together", {})
        if together.get("airline"):  # Direct airline booking
            br = together.get("booking_request", {})
            if br.get("url") and br.get("post_data"):
                return await extract_airline_url(session, br["url"], br["post_data"])
    
    return None

async def extract_airline_url(session, redirect_url: str, post_data: str) -> str | None:
    """POST to Google redirect, extract airline URL from meta refresh."""
    import re
    async with session.post(redirect_url, data=post_data) as resp:
        html = await resp.text()
    
    # Extract URL from meta refresh
    match = re.search(r'content="[^"]*url=\'?([^"\']+)\'?"', html, re.I)
    if match:
        url = match.group(1)
        # Unescape HTML entities
        url = url.replace("&amp;", "&")
        return url
    
    return None
```

**2. Add --booking-link flag**
```python
parser.add_argument("--booking-link", action="store_true", 
                    help="Include direct airline booking URLs (requires additional API calls)")
```

**3. Update output format**
```python
# In report output, after flight details:
if args.booking_link and booking_url:
    print(f"  📎 Book: {booking_url}")
```

### Unit Tests
```bash
# Test 1: Booking link for round-trip
python3 Integrations/google_flights.py search --from JFK --to RDU --date 2026-01-22 --return-date 2026-01-24 --booking-link | grep -q "delta.com\|jetblue.com"

# Test 2: Booking link contains flight details
python3 Integrations/google_flights.py search --from JFK --to RDU --date 2026-01-22 --return-date 2026-01-24 --booking-link | grep -q "itinSegment"
```

---

## Success Criteria

1. **Price accuracy:** RT search shows single RT price, not sum of one-ways
2. **Clear labeling:** All prices show (RT) or (OW) suffix
3. **Default behavior:** Missing return-date errors unless --one-way specified
4. **Multi-city:** Can search 3+ leg trips with --multi-city JSON
5. **Booking links:** --booking-link produces clickable airline URLs

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Booking link API calls add latency | Make --booking-link opt-in, not default |
| Airline URLs may expire | Document that links are session-based, use promptly |
| Multi-city JSON format errors | Validate JSON structure, provide clear examples |
| Meta refresh format changes | Add fallback to Google Flights link if extraction fails |

## Handoff to Builder

**Entry point:** `file 'Integrations/google_flights.py'`
**Prompt to update:** `file 'Prompts/Flight Search.prompt.md'`
**Execute phases:** 1 → 2 → 3 sequentially
**Test after each phase** before proceeding





