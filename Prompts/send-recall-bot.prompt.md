---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.0
provenance: con_2am5bxIzjC2JGV3F
---

# Send Recall Bot to Meeting

Dispatch "Jared Dunn, Chief of Staff (AI Notetaker)" to any meeting on demand.

## Usage

Trigger this prompt with a meeting URL:
- Zoom: `https://zoom.us/j/123456789`
- Google Meet: `https://meet.google.com/abc-defg-hij`
- Microsoft Teams: Teams meeting link

## Execution

```bash
python3 /home/workspace/Integrations/recall_ai/send_bot.py "{{MEETING_URL}}"
```

## Optional Tags

Add these to customize the bot:

| Tag | Effect |
|-----|--------|
| `--preset audio` | Audio-only recording (no video) |
| `--preset demo` | Optimized for screenshare demos |
| `--preset interview` | Interview mode (equal participant focus) |
| `--preset internal` | Internal team meeting (minimal recording) |

## Examples

**Standard:**
```bash
python3 /home/workspace/Integrations/recall_ai/send_bot.py "https://meet.google.com/abc-defg-hij"
```

**Audio-only:**
```bash
python3 /home/workspace/Integrations/recall_ai/send_bot.py "https://zoom.us/j/123456789" --preset audio
```

## Response

Confirm with V:
- Bot ID
- Expected join time
- Meeting platform detected

If the meeting already has an active bot, report that instead of creating a duplicate.
