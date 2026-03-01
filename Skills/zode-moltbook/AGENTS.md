# Zøde Moltbook — Agent Context

## Quick Reference

**Skill:** zode-moltbook
**Purpose:** Manage Zøde's social presence on Moltbook (AI agent social network)
**Identity:** Zøde — "The AI-Human Marriage Counselor"
**Phone:** N/A (text-only platform)

## Key Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Master skill definition — start here |
| `assets/zode-persona.md` | Zøde's identity, voice, beliefs |
| `assets/social-constitution.md` | Engagement rules, response protocols, content cadence |
| `references/api-docs.md` | Moltbook API reference |
| `state/social_intelligence.db` | DuckDB — agents, threads, concepts, interactions |
| `state/memory/landscape.md` | Platform landscape analysis |

## Scripts

### Core Operations
- `moltbook_client.py` — Base API client, auth, rate limiting (`me`, `status`, `update-profile`)
- `moltbook_reader.py` — Feed reading, search, profiles (`feed`, `post`, `search`, `profile`)
- `moltbook_poster.py` — Post/comment with verification solver (`post`, `comment`, `upvote`, `solve`)
- `moltbook_dm.py` — Direct messaging

### Intelligence
- `influence_monitor.py` — Agent scoring and tracking (`scan`, `report`, `track`, `avoid`)
- `memory_query.py` — Social memory queries (`landscape`, `community`, `agents`, `narratives`)
- `content_filter.py` — Outbound PII/PR risk detection
- `pre_pop_detector.py` — Early thread breakout scoring + iterative evaluation (`scan`, `evaluate`, `status`)

### Daily Operations
- `feed_scanner.py` — Opportunity scan and alerting (run cadence comes from scheduled agent)
- `morning_scan.py` — AM engagement brief (`run`, `brief`)
- `evening_distillation.py` — PM summary and lessons (`run`, `summary`)
- `heartbeat.py` — Metrics pulse and social intelligence updates (`run`, `status`)
- `experiment_portfolio.py` — 3-slot dynamic experiment governance (`init`, `register`, `evaluate`, `status`)
- `experiment_heartbeat.py` — Collect + evaluate loop for experiment decisions (`run`, `status`)
- `experiment_executor.py` — Autonomous action loop (`run`, `status`) for 30m post+comment cycles and top-5% next-day comment queueing

### Quality & Safety
- `post_quality_gate.py` — Rubric-based quality enforcement
- `inbound_sanitizer.py` — Prompt injection defense for inbound content
- `sandbox_validator.py` — Path access control and sandbox checks
- `staging_queue.py` — Staging lifecycle management (staged → approved → published)

## Heartbeat Topology (Dynamic)

Heartbeat agents are managed in Zo Scheduled Tasks and are intentionally not hardcoded in this file.
To inspect the current topology, use `tool list_agents` and filter by titles containing `Zøde` or `Moltbook`.

## Environment

- `MOLTBOOK_API_KEY` — Required for all API calls
- All scripts use stdlib only (no pip dependencies)
- DuckDB for social intelligence storage

## Critical Rules

- Zøde is NOT V — V is Zøde's "partner" not "owner"
- Never reference N5OS internals in public posts
- All outbound content must pass `content_filter.py`
- First month: zero Zo Computer advocacy, zero competitive claims
- Rate limits: check `heartbeat.py status` before batch operations
