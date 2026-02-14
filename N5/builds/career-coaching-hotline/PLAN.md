---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: con_jLC9P2vnZSHPARfg
---

# Career Coaching Hotline — Build Plan

## Objective

Build a voice AI career coaching hotline powered by VAPI that:
1. Speaks as V — modeled on his personality, psychographics, coaching voice
2. Answers career coaching questions grounded in V's 10-year coaching philosophy (24 PDFs)
3. Runs Socratic diagnostic questions to assess career stage
4. Personalizes the Careerspan sell via a value prop tree
5. Supports pre-call intake via Fillout form with phone-number matching
6. Logs calls, tracks conversions, and enables daily analysis

## Open Questions

- [x] Persona: V himself (confirmed)
- [x] Voice: Custom ElevenLabs voice via CAREER_HOTLINE_VOICE_ID (confirmed)
- [ ] Phone number: V needs to provision in VAPI
- [ ] Calendly link: V needs to create for career session booking
- [ ] CAREER_HOTLINE_SECRET: V needs to set webhook auth secret

## Phase 1

### W1: Source Material + Voice Profile (Parallel)
- D1.1: Download all 24 files from Google Drive, extract text to markdown
- D1.2: Build V's psychographic + voice profile from existing voice system data

### W2: Knowledge + Prompt + Diagnostics (Parallel, depends on W1)
- D2.1: Structure extracted content into voice-optimized knowledge base
- D2.2: Author the system prompt (MANUAL — voice-sensitive)
- D2.3: Design career diagnostic questions + tool specs

### W3: Infrastructure (Parallel, depends on W2)
- D3.1: Build webhook server + VAPI config
- D3.2: Build Fillout intake form + webhook pipeline
- D3.3: Create DuckDB dataset + call logging

### W4: Testing + Funnel (depends on W3)
- D4.1: Integration testing + end-to-end verification
- D4.2: Finalize value prop tree + Careerspan funnel (MANUAL)

### W5: Deploy (depends on W4)
- D5.1: Service registration + documentation + git commit

## Success Criteria

- [ ] Webhook server running and healthy as Zo user service
- [ ] All 6 tools functional (assessCareerStage, getCareerRecommendations, explainCareerConcept, requestCareerSession, lookupCaller, collectFeedback)
- [ ] Knowledge base with 20+ voice-optimized career coaching files
- [ ] System prompt reads as V, not generic
- [ ] Fillout intake pipeline stores caller profiles in DuckDB
- [ ] Phone-number matching greets known callers by name
- [ ] Value prop tree personalizes Careerspan sell by career stage
- [ ] Call logging and analysis pipeline operational
- [ ] SKILL.md and setup guides complete
- [ ] All code committed to feature/career-coaching-hotline branch

## Key Architectural Decisions

1. **Persona = V, not a character** — modeled on psychographics, coaching voice, directness
2. **Separate VAPI assistant** (not a mode switch on existing Zoseph)
3. **Shared infra patterns** (reuse call logging, analysis from zo-hotline)
4. **langextract for PDF decomposition** — extract structured coaching insights
5. **Phone-number-based caller matching** — Fillout form → DuckDB → call greeting
