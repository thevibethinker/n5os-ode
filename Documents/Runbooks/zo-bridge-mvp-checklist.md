# Zo Bridge MVP Checklist (Gmail, Google Drive, Notion)

Status: Draft
Owner: Careerspan

## Goals
- Idempotent setup that can be safely re-run
- Connectors: Gmail, Google Drive, Notion
- Secrets handled via env files; no secrets in repo
- Verification step outputs a state report

## Prerequisites
- Workspace ready (folders, permissions)
- .env created from .env.sample with real values
- API credentials available for Gmail, Drive, Notion

## .env.sample Keys
- GMAIL_CLIENT_ID=
- GMAIL_CLIENT_SECRET=
- GMAIL_REDIRECT_URI=
- GDRIVE_SERVICE_ACCOUNT_JSON_PATH=
- NOTION_API_KEY=
- NOTION_DB_IDS= (comma-separated if relevant)

## Setup Steps
1) Load env and validate required keys exist
2) Run Gmail connector health check (list labels; send test to self in dry-run)
3) Run Drive connector health check (create temp folder/file, then delete)
4) Run Notion connector health check (read database schema; create/delete test page)
5) Write verification report to Records/Operational/zo-bridge/<date>/state.json

## Safety & Logging
- Default to dry-run; require --confirm to perform writes
- Log to /dev/shm/zo-bridge.log and summarize to console

## Verification Report (must include)
- Timestamp and workspace identifier
- Connector status: gmail, drive, notion (ok/fail + messages)
- Permissions sanity checks
- Paths and IDs of created test resources (if any)

## Failure Modes to Handle
- Missing/invalid credentials
- Permission errors (scopes)
- Network timeouts/retries
- Partial success; ensure cleanup of test artifacts

## Exit Criteria for MVP
- All three connectors pass health checks on two distinct workspaces
- Setup completes in <15 minutes including OAuth steps
- Re-running is safe (no duplicate artifacts)
