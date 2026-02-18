---
created: 2026-02-17
version: 1.0
provenance: con_3BuG4GkgO8ROXcds
spawn_mode: manual
status: pending
---
# D6: Backend & Data Layer Hardening

## Objective
Ensure resume ingestion, caller notes, and caller profiles are stored,
maintained, and surfaced to Zozie during live calls — so she coaches with context.

## Current State
- 10 DuckDB tables (calls, caller_profiles, caller_resumes, caller_lookup, etc.)
- Resume ingestion pipeline exists (resume_ingest.py) with AISS decomposition
- 5 caller_profiles, 5 caller_resumes (2 unprocessed)
- Intake webhook (intake-webhook.ts) handles Fillout form submissions
- Caller profiles track: name, email, challenges, resume stage, bullet quality

## Work Items

### Resume Pipeline
- Audit resume_ingest.py: 2 resumes have processed_at=NULL — why?
- Ensure duplicate resume uploads don't create duplicate records
- Verify AISS decomposition quality (spot check existing processed_data JSON)
- Add retry logic for failed LLM decompositions

### Caller Notes
- Add a `caller_notes` table for per-call coaching notes
- Auto-extract key coaching points from end-of-call transcripts
- Surface notes to Zozie on return calls (inject into system prompt context)

### Caller Profile Enrichment
- On return calls, inject caller profile summary into system prompt
- Include: name, challenges, resume stage, prior topics, satisfaction history
- Ensure phone-number matching works reliably across VAPI format variations

### Data Hygiene
- Clean up test data in caller_profiles (Test Intake Runner, Idem Test User, etc.)
- Add indexes on phone_number columns for fast lookup
- Ensure all tables have proper DDL in webhook initDb()

## Key Files
- Skills/career-coaching-hotline/scripts/hotline-webhook.ts
- Skills/career-coaching-hotline/scripts/resume_ingest.py
- Skills/career-coaching-hotline/scripts/intake-webhook.ts
- Datasets/career-hotline-calls/data.duckdb
