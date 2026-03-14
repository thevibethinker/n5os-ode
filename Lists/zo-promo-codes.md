---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: con_ojJjBMXeSFSDCk0k
---

# Zo Promo Codes Tracker

Tracks everyone V has offered a Zo promo code to, what was promised, and redemption status.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | Auto-generated |
| `created_at` | ISO 8601 | When entry was added |
| `name` | string | Person's name |
| `context` | string | How you know them / where offered |
| `promo_code` | string | Specific code if any |
| `offer` | string | What was promised |
| `date_offered` | YYYY-MM-DD | When the offer was made |
| `status` | enum | `offered` / `redeemed` / `expired` |
| `notes` | string | Optional extra detail |

## Quick Add

```bash
python3 N5/scripts/zo_promo_add.py "Name" "Context" "Offer" --code "CODE" --date 2026-03-10 --notes "Optional"
```

Minimal (defaults to today, status=offered, no code):
```bash
python3 N5/scripts/zo_promo_add.py "Jane Doe" "Met at demo day" "3 months free"
```

## View

```bash
python3 N5/scripts/zo_promo_add.py --list
```
