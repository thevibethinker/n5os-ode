---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: pulse:consulting-zoffice-stack:D3.2
---

# calendly-zoffice

Calendly webhook receiver + job scheduler that triggers the Zoffice **Consultant** worker on zoputer.

## Entry points
- Webhook server: `python3 scripts/webhook_handler.py serve --port 8851`
- One-off webhook (stdin): `python3 scripts/webhook_handler.py --stdin`
- Job runner: `python3 scripts/session_prep.py tick`

## State
Persists under `N5/config/consulting/calendly_zoffice/`.

## Dependencies
- `Skills/audit-system/scripts/audit_logger.py`
- `N5/scripts/zoffice_worker.py`
