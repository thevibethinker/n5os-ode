---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_Gf4RTSYH9Lo3JFkx
---

# Deprecated Event Pipeline Scripts

**Deprecated on:** 2025-12-27
**Reason:** Replaced by LLM-first daily events agent (Simple Events System v1)

## Scripts (do not use, keep for reference)

| Script | Original Purpose | Replacement |
|--------|-----------------|-------------|
| `event_recommender.py` | Python scoring algorithm | LLM judgment in agent |
| `manage_allowlist.py` | Manage email allowlists | Hardcoded in agent prompt |
| `manage_must_go.py` | Track must-go organizers | Hardcoded in agent prompt |
| `get_allowlist_query.py` | Generate Gmail queries | Hardcoded in agent prompt |
| `smart_event_detector.py` | NLP event detection | LLM reads emails directly |
| `seed_event_sources.py` | One-time seeding | Not needed |

## Config Files (preferences now in agent prompt)

- `N5/config/allowlists.json`
- `N5/config/event_preferences.json`

## Deprecated Agents

- "NYC Networking Events Recommendations" (c2f4a7b3-c8c8-4893-9fa0-d958afe22535)
- "Luma Event Digest" (21befe69-5763-40aa-a41c-af1068342244)  
- "Daily Luma Events (NYC)" (a5b5f17d-42fa-4e3b-a9c3-4e8837a98361)
- "Allowlist Email Management" (7ee1773a-c07f-4d79-8761-920bded334f0)

## What's Still Active

- `luma_scraper.py` — Populates calendar site with broader event data
- `events-calendar` service — Visual browsing at https://events-calendar-va.zocomputer.io
- New "Daily Event Recommendations" agent — LLM-first email digest

## New Architecture

```
Gmail (7-day) → LLM reads → LLM filters → Email to V
                                ↓
                       Calendar site (visual reference)
```
