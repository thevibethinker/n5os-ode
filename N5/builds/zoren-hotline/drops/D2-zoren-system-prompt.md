---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_gFL5uhApy1RZtlSJ
drop_id: D2
title: Zøren System Prompt
status: pending
dependencies: [D1]
---

# D2: Zøren System Prompt

## Objective
Adapt Zoseph system prompt into Zøren — the FounderMaxxing AI concierge. Different persona, pathways, audience, and tone.

## Inputs
- `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (Zoseph v5.0)
- `Personal/Business/FounderMaxxing-Concept-V1.md`
- D1 output (FounderMaxxing knowledge base)

## Outputs
- `Skills/zoren-hotline/prompts/zoren-system-prompt.md`

## Key Design Decisions
- **Identity:** Zøren — elite, direct, rockstar energy. Male voice.
- **Audience:** Funded founders (technical AND non-technical). Smart, busy, skeptical.
- **Tone:** Raw, zero pretense. Match FounderMaxxing brand. No corporate enthusiasm.
- **Core pathways:**
  - **Intake/Application** — screening through conversation (replaces form)
  - **Member Support** — onboarding, troubleshooting, co-building
  - **FAQ** — program details, pricing, what to expect
  - **Co-Building** — live diagnostic + prompt generation (inherited from Zoseph)
- **Screening signals:** Loyalty, engagement, intellect/passion (NOT company stage/revenue/funding)
- **Can share:** Payment links, program details, V's background
- **Cannot access:** Caller's Zo, V's primary Zo, member data

## Acceptance Criteria
- [ ] Distinct identity from Zoseph (no copy-paste personality)
- [ ] All pathways defined with discovery sequences
- [ ] Voice rules adapted for founder audience
- [ ] Screening criteria embedded in intake pathway
- [ ] Payment link sharing mechanism defined
- [ ] Returning caller handling adapted
- [ ] Tools section updated for Zøren-specific tools
