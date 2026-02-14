---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: career-coaching-hotline/D5.1
---

# Environment Variables Checklist

All environment variables required by the Career Coaching Hotline.

Set all secrets in [Settings → Advanced](/?t=settings&s=advanced).

## Required

| Variable | Status | Where to Get |
|----------|--------|-------------|
| `CAREER_HOTLINE_VOICE_ID` | ✅ Set | ElevenLabs voice ID. Already configured in Zo secrets. Must be added to service env_vars. |
| `VAPI_API_KEY` | ✅ Set | Shared with zo-hotline. Already in Zo secrets. |
| `CAREER_HOTLINE_SECRET` | ❌ Needs setup | Generate with `openssl rand -hex 32`. Set in both Zo secrets AND VAPI dashboard (as Bearer Token credential). See `references/vapi-setup.md` Step 3. |
| `ZO_CLIENT_IDENTITY_TOKEN` | ✅ Auto | Automatically available in Zo environment. Used for SMS relay via `/zo/ask`. |

## Optional

| Variable | Default | Purpose |
|----------|---------|---------|
| `CAREER_HOTLINE_PORT` | `8848` | Server port. Set in service config. |
| `CAREER_HOTLINE_BOOKING_LINK` | `https://mycareerspan.com/book` | Calendly or booking link for coaching sessions. Update when V creates a dedicated booking page. |
| `CAREER_HOTLINE_VERBOSITY` | `normal` | Response length: `terse` (1-2 sentences), `normal` (2-4), `detailed` (full explanations). |
| `CAREER_HOTLINE_DB_PATH` | `Datasets/career-hotline-calls/data.duckdb` | DuckDB database path (intake webhook). |
| `CAREER_INTAKE_PORT` | `8421` | Intake webhook port (if running separately). |

## Service Env Vars Configuration

The service is registered with minimal env vars. To add the voice ID to the service:

```
update_user_service svc_JKqkUI_p4bQ with env_vars including CAREER_HOTLINE_VOICE_ID
```

Or ask Zo to update the service env vars to include all needed secrets.

## Verification

```bash
# Check what's available in system env
env | grep -i career | cut -d= -f1

# Check service is picking up vars
tail -20 /dev/shm/career-coaching-hotline.log | grep -E "Voice ID|Webhook auth|Verbosity"

# Expected output when fully configured:
# Voice ID: CF4E...
# Webhook auth: ENABLED
# Verbosity: normal
```
