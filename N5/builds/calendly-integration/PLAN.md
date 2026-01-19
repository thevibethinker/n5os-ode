---
created: 2026-01-12
last_edited: 2026-01-16
version: 2.1
provenance: con_Ok7qEYOax94psy7F
---

# PLAN: Calendly API Integration (OAuth + Webhook)

Full OAuth integration with Calendly API v2. Enables authenticated access, webhook-driven CRM intake, and Content Library ingestion.

## Open Questions
- [x] ~~PAT vs OAuth?~~ → **OAuth** (V created an app with Client ID/Secret)
- [x] ~~What redirect URI did V configure in Calendly?~~ → `https://calendly-auth-va.zocomputer.io/callback`
- [x] ~~Signing Key env var name?~~ → `CALENDLY_WEBHOOK_SIGNING_KEY`

## Architecture (Final)

```
Calendly Booking → Webhook → CRM Profile + Enrichment Queue
                              ├── Gmail thread search
                              └── Aviato/LinkedIn enrichment
```

**Key decision:** Calendly is the CRM gatekeeper, NOT the meeting folder creator. Transcripts (Fireflies, Granola) create meeting folders.

## Checklist

### Phase 1: OAuth Callback Service
- [ ] Create Hono server to handle `/callback` (exchange code for tokens)
- [ ] Store access/refresh tokens securely (`.calendly_tokens.json` in `~/.config/`)
- [ ] Register as User Service on port 50001
- [ ] Test full OAuth flow end-to-end

### Phase 2: CLI & Token Refresh
- [ ] Update `calendly_client.py` to use OAuth tokens (not PAT)
- [ ] Implement automatic token refresh
- [ ] CLI commands: `verify`, `links`, `events`

### Phase 3: Webhook Receiver & Semantic Gate
- [ ] Add `/webhook` endpoint to same service
- [ ] Verify webhook signatures using Signing Key
- [ ] Implement semantic gate (filter which meetings trigger folder creation)
- [ ] Create meeting folder in `Personal/Meetings/Inbox/` for qualified bookings

### Phase 4: Content Library Sync
- [ ] Sync scheduling links to `Knowledge/content-library/links/calendly/`
- [ ] Create orchestration prompt `Prompts/Calendly.prompt.md`

---

## Phase 1: OAuth Callback Service

**Objective:** Handle the OAuth redirect, exchange authorization code for tokens, store them for CLI use.

### Affected Files
- `Integrations/calendly/server.ts` (NEW — Hono/Bun server)
- `~/.config/calendly_tokens.json` (NEW — token storage)

### Changes
1. Create Hono server with route `GET /callback`:
   - Extract `code` query parameter
   - POST to `https://auth.calendly.com/oauth/token` with:
     - `grant_type: authorization_code`
     - `code: <from query>`
     - `redirect_uri: <must match what's in Calendly>`
     - `client_id` / `client_secret` from env
   - Store `access_token`, `refresh_token`, `expires_at` to JSON file
   - Display success page

2. Register service:
   ```bash
   register_user_service(
     label="calendly-auth",
     protocol="http", 
     local_port=50001,
     entrypoint="bun run /home/workspace/Integrations/calendly/server.ts"
   )
   ```

### Test
- Visit `https://auth.calendly.com/oauth/authorize?client_id=<ID>&redirect_uri=<URI>&response_type=code`
- Confirm redirect lands on Zo, tokens saved

---

## Phase 2: CLI & Token Refresh

**Objective:** Update client to use OAuth tokens with automatic refresh.

### Affected Files
- `Integrations/calendly/calendly_client.py` (UPDATE)
- `Integrations/calendly/calendly_cli.py` (UPDATE)

### Changes
1. `CalendlyClient.__init__()`:
   - Load tokens from `~/.config/calendly_tokens.json`
   - Check `expires_at`; if expired, call refresh endpoint
   - Use `access_token` in Authorization header

2. Token refresh:
   - POST to `https://auth.calendly.com/oauth/token` with `grant_type=refresh_token`
   - Update stored tokens

3. CLI commands:
   - `verify` — GET `/users/me`
   - `links` — GET `/event_types`
   - `events --days N` — GET `/scheduled_events` for next N days

### Test
```bash
python3 Integrations/calendly/calendly_cli.py verify
python3 Integrations/calendly/calendly_cli.py links
```

---

## Phase 3: Webhook Receiver & Semantic Gate

**Objective:** Receive real-time booking notifications, filter by meeting type, create meeting folders.

### Affected Files
- `Integrations/calendly/server.ts` (UPDATE — add `/webhook` route)
- `Integrations/calendly/gate_rules.yaml` (NEW — semantic filtering config)

### Changes
1. Add `POST /webhook` route:
   - Verify signature using `CALENDLY_SIGNING_KEY` (HMAC-SHA256)
   - Parse `invitee.created` event
   - Extract: invitee name, email, event type, scheduled time

2. Semantic Gate logic:
   - Load rules from `gate_rules.yaml`
   - If event type matches `include_patterns` → proceed
   - If event type matches `exclude_patterns` → ignore (log only)

3. Meeting folder creation:
   - Create `Personal/Meetings/Inbox/YYYY-MM-DD_<Name>_<EventType>/`
   - Write `manifest.json` with Calendly metadata
   - Optionally trigger CRM lookup for invitee

4. Register webhook with Calendly:
   ```bash
   python3 calendly_cli.py webhook-create --url https://va.zo.computer/s/calendly-auth/webhook --events invitee.created
   ```

### Test
- Book a test meeting via Calendly link
- Verify folder appears in `Personal/Meetings/Inbox/`

---

## Phase 4: Content Library Sync

**Objective:** Make Calendly links discoverable via Knowledge system.

### Affected Files
- `Integrations/calendly/sync_links.py` (NEW)
- `Knowledge/content-library/links/calendly/` (NEW directory)
- `Prompts/Calendly.prompt.md` (NEW)

### Changes
1. `sync_links.py`:
   - Fetch all `event_types` via API
   - For each, create markdown file with frontmatter:
     ```yaml
     ---
     type: calendly-link
     slug: discovery-call
     name: Discovery Call
     duration_minutes: 30
     url: https://calendly.com/vrijen/discovery
     synced_at: 2026-01-15
     ---
     ```
   - Save to `Knowledge/content-library/links/calendly/<slug>.md`

2. `Calendly.prompt.md`:
   - Commands: `link-list`, `sync`, `book-for <person>`
   - Integration with CRM for "send booking link" workflows

### Test
- `python3 sync_links.py`
- `@Knowledge Find calendly` returns links

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| OAuth vs PAT | Medium | OAuth is more complex but enables refresh; can fall back to PAT later |
| Port 50001 | Easy | Can change via service update |
| Token storage location | Easy | Just a file path |
| Webhook URL | Medium | Changing requires re-registering with Calendly |

## Alternatives Considered

1. **PAT-only (no OAuth)**: Simpler, but tokens don't refresh and can't be used for multi-user apps. Rejected because V already created OAuth app.

2. **Polling instead of webhooks**: Simpler but delayed. Rejected because real-time is valuable for CRM sync.

3. **Store tokens in env vars**: Simpler but can't refresh automatically. Rejected for token file approach.

## Success Criteria
- [ ] OAuth flow completes: visit auth URL → redirected → tokens stored
- [ ] `calendly_cli.py verify` returns user info using OAuth token
- [ ] Webhook receives `invitee.created` and creates meeting folder
- [ ] Calendly links searchable via Knowledge system

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Token expiration during long gap | Automatic refresh on CLI invocation |
| Webhook signature verification fails | Confirm signing key env var name with V |
| Service goes down | User Service auto-restarts; logs to `/dev/shm/` |
| Calendly API rate limits | Implement backoff; cache event_types locally |
