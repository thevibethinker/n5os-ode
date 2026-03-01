# Memory Capability

**Status:** active

The office's persistent storage layer. Provides CRUD operations for contacts, conversations, and decisions via helper functions over the shared DuckDB database. Employees never touch the database directly — they call Memory's helper functions.

## Components

- `db_helpers.py` — Core DB connection + generic query helpers
- `contact_manager.py` — Contact CRUD + lookup
- `conversation_logger.py` — Conversation tracking
- `decision_queue.py` — Decision create/resolve/expire lifecycle
- `config.yaml` — DB path, retention settings

## API Surface

### DB Helpers

```python
from Zoffice.capabilities.memory.db_helpers import get_db, execute_query

conn = get_db(db_path=None)           # DuckDB connection (singleton)
rows = execute_query(query, params)    # Returns list[dict]
```

### Contact Manager

```python
from Zoffice.capabilities.memory.contact_manager import (
    upsert_contact, find_contact, get_contact, update_contact, list_contacts
)

id = upsert_contact(name, email=None, phone=None, organization=None,
                     relationship=None, tags=None, profile=None) -> str
contact = find_contact(email=None, phone=None, name=None) -> dict | None
contact = get_contact(id) -> dict | None
ok = update_contact(id, **fields) -> bool
contacts = list_contacts(relationship=None, tag=None, limit=50) -> list[dict]
```

Upsert logic: if email OR phone matches existing contact, update. Otherwise create new.

### Conversation Logger

```python
from Zoffice.capabilities.memory.conversation_logger import (
    log_conversation, get_conversations, end_conversation
)

id = log_conversation(channel, employee, counterparty_id=None, summary=None,
                       duration_seconds=None, satisfaction=None, metadata=None) -> str
convos = get_conversations(counterparty_id=None, employee=None, channel=None,
                            since=None, limit=50) -> list[dict]
ok = end_conversation(id, summary=None, satisfaction=None) -> bool
```

### Decision Queue

```python
from Zoffice.capabilities.memory.decision_queue import (
    create_decision, get_pending_decisions, resolve_decision, expire_decisions
)

id = create_decision(summary, origin_employee=None, full_context=None,
                      options=None, recommendation=None) -> str
pending = get_pending_decisions(employee=None) -> list[dict]
ok = resolve_decision(id, resolution, resolved_by) -> bool
count = expire_decisions(older_than_days=30) -> int
```

## Configuration

See `config.yaml`:
- `db_path` — Path to office.db (default: `Zoffice/data/office.db`)
- `retention` — Data retention settings
- `defaults` — Default values for optional fields

## Notes

- All functions return plain Python dicts, never DuckDB internal types
- All IDs are UUID v4 strings
- The audit table is managed by the Security capability, not Memory
