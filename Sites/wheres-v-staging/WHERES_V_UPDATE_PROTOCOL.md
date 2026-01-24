---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_yhhn4WVEouu3kMAb
---

# Where's V Update Protocol

## The Problem
The automated ingestion system doesn't handle flight cancellations/rebookings. When V cancels a flight and rebooks on a different airline, the system:
- Keeps the old (cancelled) leg in the data
- May or may not pick up the new booking
- Results in stale/incorrect data on the dashboard

## Quick Update Protocol

When V cancels/rebooks a flight, send a message like:

```
wheres-v update:
- CANCELLED: JetBlue RDU→BOS Jan 24 (conf ISNQLK)
- NEW: Delta RDU→LGA Jan 24 11:50am-1:33pm (conf F8UJ44)
```

Or simpler:
```
wheres-v: cancelled jetblue return, rebooked delta RDU→LGA tomorrow 11:50am
```

I (Zo) will:
1. Pull the new booking details from Gmail
2. Update `data/legs_v2.jsonl` and `data/trips_v2.jsonl`
3. Restart the service

## Future Improvements (TODO)

### Cancellation Detection (Not Yet Implemented)
The ingestion script should scan for:
- Emails with subjects containing "cancelled", "cancellation", "refund"
- JetBlue "Plans change" emails
- Delta itinerary change emails
- Match confirmation codes to existing legs and mark them cancelled

### Automatic Replacement Detection
When a cancellation is detected:
- Look for new bookings within 48 hours of the cancelled flight
- Same origin, similar destination (or return to home base)
- Auto-link as replacement

## Data Files

- `data/legs_v2.jsonl` - Individual flight/train segments
- `data/trips_v2.jsonl` - Trip containers linking legs together

## Service

- URL: https://wheres-v-va.zocomputer.io
- Service ID: svc_ydOCeyyhaQE
- Workdir: /home/workspace/Sites/wheres-v-staging
