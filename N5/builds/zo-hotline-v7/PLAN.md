---
created: 2026-02-19
last_edited: 2026-02-19
version: 1.0
provenance: con_tdpDMlVT0VZmXDPS
---

# Zo Hotline v7 — Zo-Native Follow-Up + Co-Build Mode

## Objective

Transform post-call follow-up from generic AI prompts into Zo-implementation-ready outputs. Add co-build diagnostic mode that gathers enough signal during the call to generate prompts that actually work on Zo (rules, scheduled agents, personas, pipelines). Enhance follow-up page with community/social CTAs and V's branding.

## Streams

### Stream 1: Zo-Native Prompt Generation (Meta-Prompter)
Build a condensed meta-prompter context that knows what Zo can do (rules, scheduled agents, personas, zo.space, datasets, integrations, pipelines) and generates prompts callers can paste into Zo that actually create working systems — not vanilla ChatGPT-style prompts.

### Stream 2: Co-Build Mode
Add a diagnostic flow where Zoseph asks targeted questions during the call to gather enough context for high-quality prompt generation. Triggered as an option ("Want me to help you build something specific?"). Uses Sonnet for prompt generation, Haiku for everything else. Zoseph wraps up smoothly: "Check your texts in 2-3 minutes."

### Stream 3: Follow-Up Page Enhancement
Add Discord CTA, V's socials (X, LinkedIn, personal site), Vibe Thinker branding/logo, and personal touch. Make the page feel like a real product touchpoint, not a generic summary.

## Drops

| Drop | Stream | Description | Model |
|------|--------|-------------|-------|
| D1 | S1 | Meta-Prompter Context — condensed Zo capabilities index for prompt generation | Opus |
| D2 | S2 | Co-Build Diagnostic Flow — system prompt additions, tool handlers, question trees | Opus |
| D3 | S2 | Sonnet-Powered Prompt Generator — upgraded generateFollowUpContent using Sonnet + meta-prompter | Opus |
| D4 | S3 | Follow-Up Page Redesign — Discord, socials, branding, logo, improved layout | Opus |
| D5 | S1+S2 | Integration & Wiring — connect co-build flow to prompt generator, update end-of-call handler, smooth handoff | Opus |

## Dependencies

- D1 must complete before D3 (meta-prompter context feeds prompt generation)
- D2 must complete before D5 (co-build diagnostic data feeds integration)
- D3 must complete before D5 (prompt generator must exist before wiring)
- D4 is independent (parallel with D1-D3)
- D5 is the integration drop (depends on D1, D2, D3)

## Execution Order

```
Parallel: D1, D2, D4
Then: D3 (needs D1)
Then: D5 (needs D1, D2, D3)
```

## Branch

`feature/zo-hotline-v7`

## Key Decisions

- **Model split**: Sonnet 4.6 for co-build prompt generation ONLY. Haiku for all other LLM work (summaries, emails, standard follow-ups).
- **Meta-prompter**: Condensed sub-index (~2-3KB) with periodic refresh capability. Can pull expanded docs from knowledge base for specific topics.
- **Co-build exit**: Zoseph says "Check your texts in 2-3 minutes" and ends smoothly. No dragging calls.
- **Page branding**: V's logo/insignia, Discord invite, X/LinkedIn/personal site links in footer.
