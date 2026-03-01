---
name: audit-system
description: Dual-sided audit logger for the Zoffice Consultancy Stack. Tracks ALL communications between va and zoputer with cryptographic integrity verification and cross-instance discrepancy detection.
compatibility: Created for Zo Computer
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_GwlFHPrBi5KsNm1X
metadata:
  author: va.zo.computer
  skill_version: "1.0"
  created: "2026-02-06"
---

# Audit System

## Purpose

Immutable audit trail for all Zoffice communications. Independent logging on both va and zoputer sides enables discrepancy detection and forensic analysis.

## Usage

```bash
# Initialize database
python3 Skills/audit-system/scripts/audit_logger.py init

# Log an API call
python3 Skills/audit-system/scripts/audit_logger.py log \
  --type api_call \
  --direction va-to-zoputer \
  --payload '{"skill": "content-classifier", "action": "scan"}' \
  --correlation-id "uuid-from-request"

# Log an email
python3 Skills/audit-system/scripts/audit_logger.py log \
  --type email \
  --direction zoputer-to-client \
  --payload "Email body content..." \
  --correlation-id "email-thread-id"

# View recent entries
python3 Skills/audit-system/scripts/audit_logger.py list --limit 20

# Verify integrity
python3 Skills/audit-system/scripts/audit_logger.py verify

# Export for cross-check with other instance
python3 Skills/audit-system/scripts/audit_logger.py export

# Cross-check against other instance's export
python3 Skills/audit-system/scripts/audit_logger.py cross-check \
  --other-export /path/to/zoputer_export.json

# Statistics
python3 Skills/audit-system/scripts/audit_logger.py stats
```

## Database Schema

**Table: audit_entries**
- `id` - Auto-increment primary key
- `timestamp` - UTC ISO timestamp
- `zo_instance` - "va" or "zoputer"
- `entry_type` - Type of communication (api_call, email, skill_bundle, etc.)
- `direction` - Communication direction
- `correlation_id` - Links related entries across instances
- `payload_hash` - SHA-256 hash for integrity verification
- `payload` - Full content (encrypted if sensitive)
- `metadata` - JSON metadata
- `verified_at` - When integrity was last checked
- `verification_status` - pending, verified, or FAILED_INTEGRITY_CHECK

## Entry Types

| Type | Description |
|------|-------------|
| `api_call` | API request/response between Zo's |
| `email` | Email sent/received |
| `skill_bundle` | Exported skill package |
| `security_scan` | Security gate result |
| `consultation` | Advisory session record |

## Directions

- `va-to-zoputer` - Export from va to zoputer
- `zoputer-to-va` - Response/acknowledgment from zoputer
- `zoputer-to-client` - Client-facing communication
- `client-to-zoputer` - Inbound from client

## Correlation IDs

Always generate a correlation ID for linked operations:
```python
import uuid
correlation_id = str(uuid.uuid4())
```

Both sides log with the same correlation_id for cross-referencing.

## Cross-Checking

1. Export from va: `python3 Skills/audit-system/scripts/audit_logger.py export`
2. Send export to zoputer
3. On zoputer: `python3 Skills/audit-system/scripts/audit_logger.py cross-check --other-export va_export.json`
4. Reverse: Export from zoputer, cross-check on va

## Integration

All Zoffice operations should log to this system:

```python
import sys
import json
sys.path.insert(0, '/home/workspace/Skills/audit-system/scripts/')
from audit_logger import log_entry

entry_id = log_entry(
    entry_type="api_call",
    direction="va-to-zoputer",
    payload=json.dumps(payload),
    correlation_id=correlation_id,
    metadata={"skill_version": "1.2.0"}
)
```
