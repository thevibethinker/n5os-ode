---
created: 2025-12-27
last_edited: 2025-12-27
version: 2.0
provenance: con_JVzbW0S6LreS3vRW
---

# Where's V?

A simple flight tracker for V's parents.

## How It Works

1. **Daily Agent** scans Gmail "Travel Reservations" for flight confirmations
2. **LLM Filter** identifies which emails are flights for V (not parents, not wife)
3. **LLM Extractor** parses flight details (number, airports, times)
4. **Parent Page** shows current status: home / departing / flying / arrived

## Files

- `server.ts` — Hono server, single `/api/status` endpoint
- `src/App.tsx` — React frontend for parents
- `scripts/trip_store.py` — JSONL trip storage
- `data/trips.jsonl` — Trip data

## Development

```bash
bun install
bun run server.ts
```

## Deployment

Registered as user service `wheres-v`.

