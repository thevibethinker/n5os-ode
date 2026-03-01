# Ingestion Capability

**Status:** active

The office mailroom — receives, stamps, classifies, and routes inbound content from all channels. Every inbound item flows: receive → security gate → classify → route → audit log → return.

## Components

- `handlers/base.py` — Base handler class with standard pipeline
- `handlers/email_handler.py` — Email intake with [TAG] subject parsing
- `handlers/voice_handler.py` — Voice/VAPI skeleton (Layer 1)
- `handlers/webhook_handler.py` — Generic webhook with source-based routing
- `handlers/zo2zo_handler.py` — Zo2Zo intake with trust checking
- `classify.py` — Keyword-based content classifier
- `config.yaml` — Channel configs, tag routing, classification patterns

## API Surface

### Channel Handlers

```python
from Zoffice.capabilities.ingestion.handlers.email_handler import EmailHandler
from Zoffice.capabilities.ingestion.handlers.voice_handler import VoiceHandler
from Zoffice.capabilities.ingestion.handlers.webhook_handler import WebhookHandler
from Zoffice.capabilities.ingestion.handlers.zo2zo_handler import Zo2ZoHandler

handler = EmailHandler()
item = handler.receive({"subject": "...", "from": "...", "body": "..."}) -> InboundItem dict
```

### InboundItem Dict

```python
{
    "id": str,                    # UUID v4
    "timestamp": str,             # ISO 8601
    "channel": str,               # email, voice, webhook, zo2zo
    "raw_content": dict,          # Original input
    "content": str,               # Extracted text
    "classification": {           # From classifier
        "type": str,              # inquiry, request, complaint, information, escalation
        "urgency": str,           # low, normal, high, critical
        "topics": list[str]
    },
    "routing_recommendation": str, # Employee slug
    "security_result": dict,       # From inbound gate
    "tags": list[str],            # Extracted tags
    "metadata": dict              # Channel-specific metadata
}
```

### Classifier

```python
from Zoffice.capabilities.ingestion.classify import classify_content

result = classify_content(text) -> {"type": str, "urgency": str, "topics": list[str]}
```

## Configuration

See `config.yaml` for channel settings, tag→employee routing, source routing, and classification keyword patterns.
