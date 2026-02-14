---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: career-coaching-hotline/D5.1
---

# VAPI Assistant Setup Guide

Step-by-step guide to create and configure the Career Coaching Hotline assistant in VAPI.

## Prerequisites

- VAPI account with API access
- `VAPI_API_KEY` set in [Settings → Advanced](/?t=settings&s=advanced) (shared with zo-hotline)
- Service deployed at: `https://career-coaching-hotline-va.zocomputer.io`

## Step 1: Create a New Assistant

1. Go to [VAPI Dashboard → Assistants](https://dashboard.vapi.ai/assistants)
2. Click **Create Assistant**
3. Name it: **V (Career Coach)**

## Step 2: Configure the Server URL

Under **Advanced → Server URL**:

```
https://career-coaching-hotline-va.zocomputer.io
```

This tells VAPI to send all webhook events to our server. The server handles:
- `assistant-request` → Returns the full assistant config (prompt, voice, tools, transcriber)
- `tool-calls` → Executes career coaching tools server-side
- `end-of-call-report` → Logs calls to DuckDB and sends SMS to V

## Step 3: Configure Webhook Authentication

1. Generate a random secret:
   ```bash
   openssl rand -hex 32
   ```
2. In VAPI Dashboard → **Credentials** → **Add Credential**:
   - Type: **Custom Bearer Token**
   - Token: paste the generated secret
3. In the assistant settings → **Server URL** section:
   - Select the Bearer Token credential you just created
4. Add the same secret to Zo:
   - Go to [Settings → Advanced](/?t=settings&s=advanced)
   - Add secret: `CAREER_HOTLINE_SECRET` = the same value

The webhook server validates the `X-Vapi-Secret` header on every request.

## Step 4: Configure Server Messages

Under **Advanced → Server Messages**, enable:
- ✅ `assistant-request`
- ✅ `tool-calls`
- ✅ `end-of-call-report`

Disable all others (status-update, speech-update, etc.) — they're not needed and add unnecessary latency.

## Step 5: Provision a Phone Number

1. Go to [VAPI Dashboard → Phone Numbers](https://dashboard.vapi.ai/phone-numbers)
2. Click **Buy Number** or **Import Number**
3. Recommended: Choose a number in the 857 area code (Boston) to match V's existing numbers
4. Assign the number to the **V (Career Coach)** assistant

Note the phone number — it goes in the SKILL.md.

## Step 6: Test the Configuration

### Quick Test (VAPI Dashboard)
1. Open the assistant in the dashboard
2. Click the **Test** button (phone icon)
3. Verify:
   - First message plays ("Hey — this is V on the Careerspan Career Coaching Hotline...")
   - Voice sounds correct (ElevenLabs, expressive style)
   - Responding to career questions works
   - Tools fire correctly (try: "I'm not sure where I am in my career search")

### Full Test (Phone Call)
1. Call the provisioned number from a personal phone
2. Run through a typical caller flow:
   - Describe a career situation
   - Ask about a career concept (e.g., "What is ATS?")
   - Ask for a coaching session
3. After the call, verify:
   - SMS notification arrived on V's phone
   - Call logged in DuckDB: `duckdb Datasets/career-hotline-calls/data.duckdb -c "SELECT * FROM calls ORDER BY started_at DESC LIMIT 1"`

## Troubleshooting

| Issue | Check |
|-------|-------|
| No response from webhook | `tail -50 /dev/shm/career-coaching-hotline.log` |
| 401 errors | Verify `CAREER_HOTLINE_SECRET` matches VAPI Bearer Token credential |
| Voice sounds wrong | Confirm `CAREER_HOTLINE_VOICE_ID` env var is set on the service |
| Tools not working | Check for tool-call errors in logs |
| Call not logged | Verify DuckDB path exists: `ls Datasets/career-hotline-calls/data.duckdb` |

## Reference Configuration

The file `Skills/career-coaching-hotline/config/hotline-assistant.json` contains the reference assistant config. However, the **webhook server is the source of truth** — it dynamically returns the full assistant config on every `assistant-request` event, including the system prompt, tools, voice settings, and transcriber config.

You do NOT need to manually configure any of these in the VAPI dashboard. The webhook handles it all.
