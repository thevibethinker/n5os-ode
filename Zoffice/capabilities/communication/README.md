# Communication Capability

**Status:** active

The outbound system — dispatches messages through the right channel, enforces autonomy-based approval gates, renders markdown templates, and rate-limits to prevent duplicates. Communication does NOT actually send messages — it prepares SendRequests for rice-integration to wire.

## Components

- `channels/dispatch.py` — Multi-channel dispatcher with template rendering
- `channels/approval.py` — Autonomy-aware approval gate
- `channels/rate_limiter.py` — In-memory deduplication and rate limiting
- `templates/` — Markdown templates with {{variable}} substitution
- `config.yaml` — Channel preferences, rate limit settings

## API Surface

### Dispatch

```python
from Zoffice.capabilities.communication.channels.dispatch import prepare_send, render_template, list_templates

send_req = prepare_send(
    recipient="jane@example.com",
    content="Hello Jane",
    channel="email",
    employee="receptionist",
    confidence=0.95,
    template="acknowledgment",        # optional
    template_vars={"name": "Jane"},   # optional
) -> SendRequest dict

rendered = render_template("acknowledgment", {"name": "Jane", "topic": "inquiry"}) -> str
templates = list_templates() -> list[str]
```

### Approval Gate

```python
from Zoffice.capabilities.communication.channels.approval import check_approval

result = check_approval(
    action="respond_to_inquiry",
    confidence=0.95,
    employee="receptionist",
) -> {"decision": "auto_act"|"act_and_notify"|"escalate_to_parent"|"escalate_to_human", "reason": str}
```

### Rate Limiter

```python
from Zoffice.capabilities.communication.channels.rate_limiter import check_rate_limit, record_send

result = check_rate_limit(recipient, content_hash, window_seconds=300) -> {"allowed": bool, "reason": str}
record_send(recipient, content_hash)  # Records a send event
```

## Templates

| Template | Variables | Purpose |
|----------|-----------|---------|
| acknowledgment | name, topic | Confirm receipt of a message |
| escalation-notice | employee_or_human, topic | Notify about escalation |
| follow-up | topic, content | Follow up on a conversation |

## Configuration

See `config.yaml` for default channel, rate limit window, and template directory settings.
Reads `Zoffice/config/autonomy.yaml` for approval thresholds (never modifies it).
