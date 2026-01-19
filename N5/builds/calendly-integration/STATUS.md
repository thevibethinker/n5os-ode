---
created: 2026-01-15
last_edited: 2026-01-16
build_slug: calendly-integration
provenance: con_Ok7qEYOax94psy7F
---

# Build Status: calendly-integration

## Current Phase
✅ COMPLETE (Refactored)

## Architecture
```
Calendly Booking → Webhook → CRM Intake
                              ├── Profile creation/update
                              ├── Gmail enrichment queue
                              └── Aviato/LinkedIn enrichment queue
```

**Key decision:** Calendly does NOT create meeting folders. That's Fireflies/Granola/manual's job. Calendly is the CRM gatekeeper.

## Progress
- [x] Phase 1: OAuth Service (PKCE flow, token storage)
- [x] Phase 2: CLI + Webhook registration
- [x] Phase 3: Content Library sync (18 links)
- [x] Phase 4: CRM Intake (refactored from meeting folders)
- [x] Prompt documentation

## What Happens on Booking

1. Calendly sends `invitee.created` webhook
2. Webhook calls `crm_intake.py` with name, email, event type, scheduled time
3. Script:
   - Creates CRM profile if new (or finds existing)
   - Infers category (INVESTOR, ADVISOR, COMMUNITY, NETWORKING)
   - Appends meeting context to profile YAML
   - Queues enrichment (checkpoint_2 + checkpoint_gmail)
4. Enrichment workers process asynchronously

## Artifacts
- `Integrations/calendly/server.ts` - OAuth + webhook service
- `Integrations/calendly/calendly_client.py` - API client
- `Integrations/calendly/calendly_cli.py` - CLI
- `Integrations/calendly/crm_intake.py` - CRM profile creation
- `Integrations/calendly/sync_links.py` - Content Library sync
- `Prompts/Calendly.prompt.md` - Orchestration prompt
- `~/.config/calendly_tokens.json` - OAuth tokens
- `Knowledge/content-library/links/calendly/` - 18 scheduling links

## Service
- **URL:** https://calendly-auth-va.zocomputer.io
- **Port:** 50001
- **Webhook:** Registered for invitee.created, invitee.canceled

## Learnings
- Calendly OAuth requires PKCE (code_challenge/code_verifier)
- Calendly OAuth accepts NO scope parameter (not even "default")
- Meeting folders should be created by transcript source, not booking source
- CRM is the right hook point for booking events

