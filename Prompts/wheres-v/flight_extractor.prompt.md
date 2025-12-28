---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_JVzbW0S6LreS3vRW
title: Flight Extractor
description: Smart LLM - extracts structured flight details from confirmation email
tags: [wheres-v, flight, extractor]
tool: false
---

# Flight Extractor

Extract flight details from this confirmation email. Parse carefully — airline email formats vary widely.

## Required Fields

Extract ALL of the following:

| Field | Description | Example |
|-------|-------------|---------|
| flight_number | Airline code + number | "UA1234", "DL567", "B6890" |
| departure_airport | 3-letter IATA code | "JFK", "EWR", "LGA" |
| arrival_airport | 3-letter IATA code | "LAX", "SFO", "MIA" |
| departure_time | ISO 8601 with timezone | "2025-01-15T10:30:00-05:00" |
| arrival_time | ISO 8601 with timezone | "2025-01-15T13:45:00-08:00" |

## Airline Codes Reference

- United: UA
- Delta: DL
- JetBlue: B6
- American: AA

## Response Format

Return ONLY valid JSON, no markdown fences:

```json
{
  "flight_number": "UA1234",
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  "departure_time": "2025-01-15T10:30:00-05:00",
  "arrival_time": "2025-01-15T13:45:00-08:00"
}
```

If the email contains multiple flights (connecting flights or round trip), return the FIRST/OUTBOUND flight only.

If you cannot extract all required fields, return:
```json
{"error": "Could not extract: [missing field]"}
```

## Email Content

```
{{EMAIL_CONTENT}}
```

