---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_Ok7qEYOax94psy7F
---

# PLAN: Calendly API Integration & Selective Webhook Sync

Build a robust integration with Calendly API v2 to automate meeting ingestion and link management.

## Open Questions
- [ ] What is the exact schema for `Knowledge/content-library/links/`? (Need to verify if it exists or if I need to create the directory structure).
- [ ] Should we use a public tunnel (ProxyResult) for the initial webhook testing, or go straight to a User Service?

## Checklist
- [ ] Phase 1: CLI & Verification (PAT Setup)
- [ ] Phase 2: Content Library Ingestion
- [ ] Phase 3: Webhook Service & Semantic Gate
- [ ] Phase 4: Custom Landing Page Scaffold (Optional/Future)

---

## Phase 1: CLI & Verification
**Objective:** Establish authenticated connection and provide baseline management tools.

### Affected Files
- `Integrations/calendly/calendly_client.py`
- `Integrations/calendly/calendly_cli.py`
- `Prompts/Calendly.prompt.md`

### Changes
- Implement `CalendlyClient` using `CALENDLY_API_KEY` (PAT).
- Support `GET /users/me` for verification.
- Support `GET /event_types` to list available scheduling links.
- Create `calendly-cli` entry point.

### Unit Tests
- `python3 Integrations/calendly/calendly_cli.py verify`
- `python3 Integrations/calendly/calendly_cli.py links --list`

---

## Phase 2: Content Library Ingestion
**Objective:** Sync Calendly event types into the searchable Content Library.

### Affected Files
- `Integrations/calendly/sync_links.py`
- `Knowledge/content-library/links/calendly/` (New directory)

### Changes
- Script to fetch all active `event_types`.
- Convert each to a markdown link file with frontmatter (slug, name, duration, description).
- Auto-run `python3 N5/scripts/content_ingest.py` for each.

### Unit Tests
- Verify links appear in `Knowledge Find` results.

---

## Phase 3: Webhook Service & Semantic Gate
**Objective:** Automate meeting setup for high-signal calls only.

### Affected Files
- `Integrations/calendly/webhook_handler.py` (Hono/Bun service)
- `N5/config/calendly_gate_rules.yaml`

### Changes
- Create a Hono server (Bun) to listen for `invitee.created`.
- Implement semantic gate:
    - Check meeting name against `include_list`.
    - If match: Create meeting folder in `Personal/Meetings/Inbox/`.
    - If match: Trigger `meeting-process` prompt.
- Register as User Service via `register_user_service`.

### Unit Tests
- Send mock payload to webhook and verify meeting folder creation.

---

## Success Criteria
- [ ] `calendly-cli verify` returns successful user info.
- [ ] All Calendly links synced to Content Library.
- [ ] Webhook successfully filters a "Coffee Chat" (ignored) vs "Discovery Call" (logged).

## Risks & Mitigations
- **Risk:** Webhook URL changes if not using a permanent domain.
- **Mitigation:** Use Zo's User Service which provides a persistent public endpoint.
- **Risk:** Token expiration.
- **Mitigation:** Use PAT (doesn't expire like OAuth tokens) and provide clear error messages if unauthorized.

