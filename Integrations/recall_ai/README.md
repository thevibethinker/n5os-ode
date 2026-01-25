---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_2am5bxIzjC2JGV3F
---

# Recall.ai Integration

Replaces Fireflies.ai for meeting recording ingestion. Recall.ai bots join video calls (Zoom, Google Meet, Teams, etc.) and deliver:
- Audio recordings
- Video recordings (180-day retention)
- Real-time transcripts
- Participant events (join/leave)

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│  Calendar Event │ ───▶ │  Create Bot API  │ ───▶ │  Bot joins meeting  │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
                                                            │
                                                            ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│ Personal/Mtgs/  │ ◀─── │ Webhook Receiver │ ◀─── │ Recording Complete  │
│ {date}_{title}/ │      │    (port 8846)   │      │   (Recall event)    │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
```

## Components

| File | Purpose |
|------|---------|
| `recall_client.py` | REST API client for Recall.ai |
| `webhook_receiver.py` | FastAPI server for webhook events |
| `meeting_depositor.py` | Deposits recordings into meeting pipeline |
| `config.py` | Configuration and env vars |

## Environment Variables

```bash
RECALL_API_KEY=<your-api-key>          # Required - from recall.ai dashboard
RECALL_REGION=us-west-2                 # Default region (us-east-1, us-west-2, eu-central-1, ap-northeast-1)
RECALL_WEBHOOK_SECRET=<secret>          # Optional - for signature verification
```

## CLI Usage

```bash
# Create a bot to join a meeting
python3 recall_client.py create-bot "https://zoom.us/j/123456789" --bot-name "Zo Notetaker"

# Create scheduled bot (10+ minutes in future)
python3 recall_client.py create-bot "https://meet.google.com/abc-defg-hij" --join-at "2026-01-25T14:00:00Z"

# List recent bots
python3 recall_client.py list-bots --limit 10

# Get bot status
python3 recall_client.py get-bot <bot-id>

# Download recording artifacts
python3 recall_client.py download <bot-id> --output-dir /path/to/output

# Test connection
python3 recall_client.py test
```

## Webhook Events

The receiver listens for these events:

| Event | Action |
|-------|--------|
| `bot.status_change` | Log status transitions |
| `recording.ready` | Download audio + video |
| `transcript.ready` | Download and format transcript |
| `bot.done` | Finalize meeting folder |

## Meeting Folder Output

When a recording completes, creates:

```
Personal/Meetings/YYYY-MM-DD_{meeting-title}/
├── manifest.json           # Meeting metadata
├── audio.mp3               # Audio recording
├── video.mp4               # Video recording (if available)
├── transcript.json         # Raw transcript data
├── transcript.txt          # Formatted transcript
└── participants.json       # Join/leave events
```

## Service Registration

```bash
# Register webhook receiver as Zo service
register_user_service(
    label="recall-webhook",
    protocol="http",
    local_port=8846,
    entrypoint="uvicorn Integrations.recall-ai.webhook_receiver:app --host 0.0.0.0 --port 8846",
    workdir="/home/workspace"
)
```

Webhook URL: `https://va.zo.computer/webhook/recall`

## Bot Configuration

Default bot settings (see `config.py`):

```python
DEFAULT_BOT_CONFIG = {
    "bot_name": "Zo Notetaker",
    "recording_mode": "speaker_view",
    "recording_mode_options": {
        "participant_video_when_screenshare": "hide"
    },
    "transcription_options": {
        "provider": "default"
    },
    "real_time_transcription": {
        "destination_url": None,  # Can add for real-time streaming
        "partial_results": False
    },
    "automatic_leave": {
        "waiting_room_timeout": 600,  # 10 min
        "noone_joined_timeout": 600,
        "everyone_left_timeout": 60
    },
    "automatic_video_output": {
        "in_call_recording": True,
        "video_retention_period": 180  # 180 days
    },
    "automatic_audio_output": {
        "in_call_recording": True
    }
}
```

## Related

- `file 'Documents/System/guides/meeting-queue-protocol.md'` - Meeting ingestion protocol
- `file 'N5/capabilities/integrations/fireflies-webhook.md'` - Previous Fireflies integration
