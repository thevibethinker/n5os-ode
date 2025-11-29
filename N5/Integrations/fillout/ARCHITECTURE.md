---
created: 2025-11-27
last_edited: 2025-11-27
version: 1.0
---

# Fillout Integration Architecture (Personal Zo)

## Overview

This integration provides an event-driven pipeline from Fillout to the personal Zo computer. It focuses on:

- Receiving Fillout form submissions via webhooks
- Persisting events as append-only JSONL logs
- Enabling local analysis and querying via scripts and AI assistance

## Components

### 1. Webhook Service

- **Technology**: FastAPI (Python)
- **Location**: `N5/Integrations/fillout/app.py`
- **Endpoints**:
  - `POST /webhooks/fillout` – primary webhook receiver for Fillout submissions
  - `GET /health` – health check for monitoring and service diagnostics
- **Responsibilities**:
  - Accept JSON POST payloads from Fillout
  - Capture minimal request metadata (e.g., received timestamp, headers of interest)
  - Append normalized events to a JSONL event log
  - Return fast, clear HTTP responses (`200` on success, `4xx/5xx` on errors)

### 2. Event Log (JSONL Storage)

- **Format**: One JSON object per line (JSONL)
- **Location**: `N5/Integrations/fillout/events/`
- **File naming**: `YYYY-MM-DD.jsonl` (UTC date of receipt)
- **Event shape (per line)**:
  - `source`: fixed string `"fillout"`
  - `type`: event kind, e.g. `"submission_created"`
  - `received_at`: ISO 8601 timestamp (UTC) when Zo received the event
  - `headers`: selected HTTP headers (e.g., signatures for future verification)
  - `payload`: full Fillout JSON payload (unmodified)

### 3. Query & Analysis Layer

- **Primary consumers**:
  - Ad-hoc Python scripts
  - AI assistant reading and interpreting JSONL content
- **Approach**:
  - Scripts stream JSONL files line-by-line for scalability
  - Filtering by form ID, date range, submission fields, etc.
  - Summaries, reports, and transformations performed by scripts, then interpreted by AI

### 4. Optional: Fillout REST API Backfill

- **Base URL**: `https://api.fillout.com/v1/api`
- **Auth**: `Authorization: Bearer <API_KEY>` (provided via environment/config, never hard-coded)
- **Usage** (optional, not core architecture):
  - Backfill historical submissions for a form
  - Reconcile local logs with Fillout as the source of truth

## Design Principles

- **Event-driven first**: Webhooks are the primary ingestion path; polling the REST API is reserved for repair and backfill.
- **Append-only logs**: JSONL files act as an immutable event history. Higher-level representations can be derived from logs later if needed.
- **Local-first querying**: Analysis and reporting are driven from local logs; external APIs are not on the critical path.
- **No secrets in code**: API keys or secrets are supplied via environment variables or configuration, not committed to source files.
- **Small, composable scripts**: Query and analysis behavior lives in focused scripts that can be called on demand.

