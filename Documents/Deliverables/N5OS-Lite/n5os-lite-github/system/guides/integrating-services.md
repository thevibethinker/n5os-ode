---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
title: "Integration Best Practices: The N5 Way"
---

# Integrating Services with N5OS

N5OS is designed to be the "central nervous system" of your digital life. Integrating external services (Calendar, Email, Tasks, CRM) is a core capability, but it must be done with **architectural discipline** to prevent the system from becoming a fragile web of APIs.

## The Core Philosophy: "State-First, Not Call-First"

Most AI integrations just "call the API" when asked. N5OS does not do this.
**N5OS mirrors the external state locally, then reasons over the local copy.**

### The Pattern

1.  **Ingest:** A script fetches data from the external service (e.g., `fetch_gcal.py`).
2.  **Store:** Data is saved to a local SQLite database or JSONL registry (e.g., `crm.db`).
3.  **Reason:** The AI reads the *local* database to answer questions or make decisions.
4.  **Act:** The AI queues an action, which a script then pushes back to the external service (e.g., `push_gcal.py`).

### Why?
*   **Speed:** Local queries are instant.
*   **Reliability:** If the API is down, the AI still knows your schedule.
*   **Context:** The AI can see "all" data at once, not just what the API pagination allows.

---

## Standard Integration Architecture

When adding a new service (e.g., Tally, Akiflow, Slack), follow this structure:

### 1. The Connector (Script)
Do not rely solely on the LLM calling `use_app_xyz`. Create a Python script in `scripts/` that wraps the tool.

```python
# scripts/sync_my_service.py
# GOOD: Handles pagination, error catching, and state saving.
def sync_data():
    items = fetch_all_items() # Uses use_app_tool internally
    db.save(items)
```

### 2. The Local Registry (Database)
Create a table in `data/integrations.db` or a dedicated file.
*   **Must have:** `remote_id` (The service's ID), `last_synced` (Timestamp).
*   **Should have:** `raw_json` (Store the full payload so you don't have to migrate schema often).

### 3. The "Action" Tool
If the integration allows writing back (sending messages, creating tasks), create a dedicated script for it.
*   **Example:** `scripts/send_slack_message.py`
*   **Rule:** It must log the action to a local `audit_log.jsonl` before sending.

---

## Security & Auth

*   **NEVER** hardcode API keys in scripts.
*   **ALWAYS** use the N5OS `use_app_*` tool primitives which handle OAuth securely.
*   **IF** you must use a raw API key, store it in `N5/config/secrets/` and read it via `lib.secrets.py`.

## Checklist for New Integrations

- [ ] **Ingestion Script:** Can it fetch all data without crashing?
- [ ] **Local Store:** Is the schema defined?
- [ ] **Idempotence:** If I run the script twice, does it duplicate data? (It should not).
- [ ] **Logs:** Does it write to `logs/integration_name.log`?
- [ ] **Orchestrator:** Is there a way for the AI to trigger it?

---

*“The AI is the brain. The scripts are the hands. The database is the memory. Do not let the brain try to be the hands.”*

