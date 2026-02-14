---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: career-coaching-hotline/D3.3
---

# Career Coaching Hotline — Call Logs Dataset

Analytics dataset for the Career Coaching Hotline, a VAPI-powered voice AI career advisor built on V's decade of coaching experience through Careerspan.

## Quick Start

```bash
# Initialize (idempotent)
python3 Skills/career-coaching-hotline/scripts/init_db.py

# Verify
python3 Skills/career-coaching-hotline/scripts/init_db.py --verify

# Query
duckdb Datasets/career-coaching-calls/data.duckdb "SHOW TABLES"
duckdb Datasets/career-coaching-calls/data.duckdb "SELECT * FROM calls LIMIT 5"
```

## Tables

| Table | Purpose | Rows (live) |
|-------|---------|-------------|
| `calls` | Call log with career stage and topics | Updated per call |
| `escalations` | Careerspan session requests | Updated per escalation |
| `feedback` | Post-call satisfaction (1-5) | Updated per feedback |
| `daily_analysis` | LLM-generated daily insights | 1 row per day |
| `caller_profiles` | Fillout intake form data | Updated per submission |
| `caller_insights` | Merged caller intelligence | Updated by analysis loop |

## Career Stages

The diagnostic tool assesses callers into one of 5 stages:

1. **Groundwork** — Pre-search introspection and self-reflection
2. **Materials** — Resume, cover letter, LinkedIn preparation
3. **Outreach** — Networking, cold outreach, systematic job search
4. **Performance** — Interview prep, offer negotiation, conversion
5. **Transition** — Career change, layoff recovery, industry switch

See `N5/builds/career-coaching-hotline/artifacts/career-stages.md` for full framework.

## Key Metrics

- **Careerspan conversion rate**: `escalations / total_calls`
- **Career stage distribution**: Which stages callers are in
- **Topic frequency**: What coaching topics are most discussed
- **Satisfaction trend**: Daily average from feedback
- **Drop-off rate**: Calls < 1 min (diagnostic for greeting/UX issues)

## Daily Analysis

The `call_analysis_loop.py` script runs daily and generates:

- Substantive call pattern extraction (LLM-powered)
- Drop-off classification and diagnosis
- Satisfaction trend analysis
- Careerspan conversion tracking
- Ranked improvement suggestions

```bash
# Run analysis for yesterday
python3 Skills/career-coaching-hotline/scripts/call_analysis_loop.py

# Preview without writing
python3 Skills/career-coaching-hotline/scripts/call_analysis_loop.py --dry-run

# Analyze specific date
python3 Skills/career-coaching-hotline/scripts/call_analysis_loop.py --date 2026-02-14
```

Reports are written to `Skills/career-coaching-hotline/analysis/`.

## Data Sources

- **VAPI Webhook**: Real-time call events → calls, escalations, feedback
- **Fillout Intake Form**: Pre-call profiles → caller_profiles
- **Analysis Loop**: Daily LLM analysis → daily_analysis, caller_insights

## Privacy

- `calls`: Contains phone numbers for profile matching; raw_data has full VAPI payloads
- `caller_profiles`: PII with explicit consent via intake form
- `escalations`: Contact info for Careerspan booking only
- `feedback`: First names only (voluntary)
- `caller_insights`: Merged from above; phone for matching
- `daily_analysis`: Aggregate patterns, no PII

## Schema

See `schema.yaml` for full column definitions, indexes, and example queries.
