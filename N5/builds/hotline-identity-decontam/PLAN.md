---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
build_slug: hotline-identity-decontam
---

# Plan: Career Hotline — Zozie Identity Decontamination + Free Tier

## Objective

Fix the Career Coaching Hotline so the AI identifies as **Zozie** (not V/Vrijen), treats the hotline as an independent free resource supported by Careerspan (not a Careerspan booking funnel), and correctly implements the 15-minute free tier per phone number.

## Problem

The LLM (Claude Haiku) absorbs identity from ALL content it reads — not just the Identity section of the system prompt. Multiple artifact files loaded at startup and via tool calls contain:
- First-person "V" voice ("I've seen the biggest transformations")
- "V will reach out" / "book directly" CTAs
- "V's coaching angle" / "V's philosophy" attributions
- 74 "Vrijen says/explains/advocates" patterns in extracted concept files
- "V (Career Coach)" name and "this is V" firstMessage in webhook

The zozie-persona.md identity anchor file was created but never integrated into the webhook.

## Success Criteria

- [ ] Zero "V" identity references in any content the LLM reads at runtime
- [ ] Zero "book a session" / "booking link" language — hotline is independent, supported by Careerspan
- [ ] Zozie persona file prepended to system prompt before all other content
- [ ] 30 bonus minutes offer for Careerspan signup present in system prompt
- [ ] Free tier = 15 minutes lifetime per phone number
- [ ] Service restarts cleanly and passes health check
- [ ] Live call test confirms Zozie identity

## Phases

### Wave 1: Identity Decontamination (5 parallel drops)

**Drops:**
- D1.1: Webhook — persona prepend + name/firstMessage/voicemail/requestCareerSession/BOOKING_LINK fixes
- D1.2: System prompt — remove all V references, fix Careerspan framing, verify bonus offer
- D1.3: Value prop tree — fix all V CTAs, first-person pitch lines, booking language
- D1.4: Career stages + diagnostic questions + tool specs — fix all V attributions
- D1.5: Extracted concept files — decontaminate 74 Vrijen attributions across 11 files

**Gate:** `grep -r "V's\|V will\|V can\|this is V\|ask V\|have V\|Vrijen says\|Vrijen explains\|Vrijen notes\|Vrijen advocates\|Vrijen emphasizes\|Vrijen identifies\|book.*session\|booking.*link" artifacts/ scripts/` returns zero matches in runtime-loaded content.

### Wave 2: Free Tier Update + Deploy

**Drops:**
- D2.1: Update free tier to 15 minutes lifetime per phone number (verify in webhook balance logic)
- D2.2: Restart service, run verification tests, confirm via live call

**Gate:** Service healthy, curl tests pass, live call confirms Zozie identity.

## Affected Files

| File | Change |
|------|--------|
| `Skills/career-coaching-hotline/scripts/hotline-webhook.ts` | Persona prepend, name, firstMessage, voicemail, requestCareerSession, BOOKING_LINK, free tier |
| `N5/builds/career-coaching-hotline/artifacts/career-coach-system-prompt.md` | V refs, Careerspan framing |
| `N5/builds/career-coaching-hotline/artifacts/value-prop-tree.md` | V CTAs, booking language, first-person pitch |
| `N5/builds/career-coaching-hotline/artifacts/career-stages.md` | "V's coaching angle" attributions |
| `N5/builds/career-coaching-hotline/artifacts/diagnostic-questions.md` | "V's coaching style" attributions |
| `N5/builds/career-coaching-hotline/artifacts/tool-specs.json` | "V's knowledge base", session booking desc |
| `N5/builds/career-coaching-hotline/artifacts/extracted/*.md` (11 files) | 74 Vrijen attributions |
| `Skills/career-coaching-hotline/config/hotline-assistant.json` | Reference config updates (low priority) |

## Risks

- Changing too much coaching content voice could reduce effectiveness — preserve coaching quality while removing identity contamination
- Service restart could fail if syntax errors introduced — verify with `bun check` before restart
- Missing a reference that only appears in tool call responses (mid-call injection) — must verify extracted files too
