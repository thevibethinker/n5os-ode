# Security Capability

**Status:** active

Validates inbound content, filters PII, and maintains an immutable audit trail. Security cannot be disabled once active (architectural decision D7).

## Components

- `gates/inbound_gate.py` — Adversarial detection + PII filter
- `audit/writer.py` — Audit trail writer with SHA-256 hash verification
- `audit/schema.sql` — Reference SQL for the audit table (documentation only)
- `config.yaml` — Detection rules, sensitivity levels, PII patterns

## API Surface

### Inbound Gate

```python
from Zoffice.capabilities.security.gates.inbound_gate import validate

result = validate(content: str, config_path: str | None = None) -> dict
# Returns: {"allowed": bool, "flags": list[str], "filtered_content": str | None}
```

**Flags:** `adversarial_prompt_injection`, `pii_detected`

### Audit Writer

```python
from Zoffice.capabilities.security.audit.writer import log_audit

entry_id = log_audit(
    capability: str,       # e.g. "security", "memory", "ingestion"
    employee: str | None,  # employee slug or None for system events
    action: str,           # what happened
    channel: str | None,   # email, voice, webhook, zo2zo
    counterparty: str | None,
    metadata: dict | None,
    parent_event_id: str | None,
    db_path: str | None,   # override for testing
) -> str  # UUID of the audit entry
```

**All capabilities MUST call `log_audit()` for every action they perform.**

## Configuration

See `config.yaml` for:

- `sensitivity` — `strict` (default), `standard`, or `low`
- `adversarial_patterns` — regex patterns for prompt injection detection
- `pii_patterns` / `pii_labels` — PII regex patterns and redaction labels
- `audit.db_path` — path to office.db
- `audit.hash_algorithm` — hash algorithm (sha256)

### Sensitivity Levels

| Level | Adversarial Detection | PII Filtering |
|-------|----------------------|---------------|
| strict | Active | Redact |
| standard | Active | Warn only |
| low | Active | Disabled |
