---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
---

# Fathom Webhook Receiver Service

Production-ready FastAPI service for receiving real-time webhook notifications from Fathom.ai when meeting transcripts are completed.

## Features

- ✅ **HMAC Signature Verification**: Secure webhook authentication
- ✅ **SQLite Logging**: Persistent webhook event storage
- ✅ **Production-Ready**: Request size limits, timeouts, error handling
- ✅ **Health Monitoring**: `/health` endpoint for service status
- ✅ **Comprehensive Tests**: Unit tests with pytest
- ✅ **Async Architecture**: FastAPI + uvicorn for high performance

## Architecture

```
Fathom.ai → Webhook POST → FastAPI Receiver → SQLite Logger
                                    ↓
                              Response (200ms)
```

**Design Principle**: Fast acknowledgment (< 500ms), deferred processing.

## Installation

```bash
cd /home/workspace/N5/services/fathom_webhook
pip install fastapi uvicorn[standard] python-dotenv pydantic aiofiles
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Set your Fathom API key:
```bash
FATHOM_API_KEY=your-api-key-here
```

3. (Optional) Configure webhook secret for HMAC verification:
```bash
FATHOM_WEBHOOK_SECRET=your-secret-here
```

## Running the Service

### Development Mode

```bash
cd /home/workspace/N5/services/fathom_webhook
python -m webhook_receiver
```

### Production Mode (User Service)

Register as a persistent service:

```bash
# Via Zo tools
register_user_service(
    label="fathom-webhook",
    protocol="http",
    local_port=8768,
    entrypoint="python3 -m uvicorn webhook_receiver:app --host 0.0.0.0 --port 8768",
    workdir="/home/workspace/N5/services/fathom_webhook"
)
```

Or manually:
```bash
cd /home/workspace/N5/services/fathom_webhook
nohup uvicorn webhook_receiver:app --host 0.0.0.0 --port 8768 > /dev/shm/fathom_webhook.log 2>&1 &
```

## Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "fathom_webhook",
  "timestamp": "2025-11-15T12:00:00",
  "database_connected": true,
  "api_key_configured": true
}
```

### `POST /webhook/fathom`
Main webhook receiver endpoint.

**Headers:**
- `Content-Type: application/json`
- `X-Fathom-Signature: sha256=<hmac>` (optional, if secret configured)

**Request Body:**
```json
{
  "meetingId": "transcript-uuid",
  "eventType": "Transcription completed",
  "clientReferenceId": "optional-reference"
}
```

**Response:**
```json
{
  "status": "received",
  "webhook_id": "unique-webhook-id",
  "message": "Webhook queued for processing"
}
```

## Testing

Run unit tests:
```bash
cd /home/workspace/N5/services/fathom_webhook
pytest tests/ -v --cov=. --cov-report=term-missing
```

Test individual components:
```bash
# Test receiver endpoints
pytest tests/test_receiver.py -v

# Test processor logic
pytest tests/test_processor.py -v
```

## Database Schema

Location: `/home/workspace/N5/data/fathom_webhooks.db`

**Table: `fathom_webhooks`**
```sql
CREATE TABLE fathom_webhooks (
    webhook_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    transcript_id TEXT NOT NULL,
    received_at TEXT NOT NULL,
    processed_at TEXT,
    status TEXT DEFAULT 'pending',
    payload TEXT,
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## Querying Webhooks

```python
import sqlite3

conn = sqlite3.connect("/home/workspace/N5/data/fathom_webhooks.db")
cursor = conn.cursor()

# Get pending webhooks
cursor.execute("SELECT * FROM fathom_webhooks WHERE status = 'pending'")
pending = cursor.fetchall()

# Get recent webhooks
cursor.execute("""
    SELECT webhook_id, transcript_id, received_at, status 
    FROM fathom_webhooks 
    ORDER BY received_at DESC 
    LIMIT 10
""")
recent = cursor.fetchall()
```

## Monitoring

### Logs
- **File**: `/home/workspace/N5/logs/fathom_webhook.log`
- **Format**: `2025-11-15T12:00:00Z INFO Message`

### Service Status
```bash
# Check if service is running
curl http://localhost:8768/health

# View recent logs
tail -f /home/workspace/N5/logs/fathom_webhook.log
```

## Security

1. **HMAC Verification**: Configure `FATHOM_WEBHOOK_SECRET` for signature validation
2. **Request Size Limits**: 5MB max payload size (configurable)
3. **Response Timeouts**: 500ms response target
4. **Input Validation**: Pydantic models enforce schema

## Integration with Fathom

1. Log into Fathom.ai dashboard
2. Navigate to **Settings → Integrations → Webhooks**
3. Add webhook URL: `https://your-domain.zo.computer/webhook/fathom`
4. (Optional) Configure webhook secret
5. Test the webhook from Fathom dashboard

## Troubleshooting

### Service won't start
- Check API key is configured: `echo $FATHOM_API_KEY`
- Verify port 8768 is available: `netstat -tuln | grep 8768`
- Check logs: `tail -50 /home/workspace/N5/logs/fathom_webhook.log`

### Webhooks returning 401
- Verify HMAC secret matches Fathom configuration
- Check signature header: `X-Fathom-Signature` or `x-hub-signature`

### Database issues
- Ensure directory exists: `mkdir -p /home/workspace/N5/data`
- Check permissions: `ls -la /home/workspace/N5/data/fathom_webhooks.db`
- Recreate schema: Delete DB file and restart service

## Next Steps (Phase 2)

After webhook receiver is operational:
1. Build transcript fetcher service
2. Create ingestion pipeline to meeting system
3. Implement webhook → transcript → meeting flow
4. Add scheduled reconciliation for missed webhooks

## References

- [Fathom API Documentation](https://docs.fathom.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Webhook Security Best Practices](https://docs.github.com/webhooks/securing)

