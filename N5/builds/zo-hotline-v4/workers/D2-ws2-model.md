---
created: 2026-02-17
last_edited: 2026-02-18
version: 2.0
provenance: con_D22Ewo8OGuQrMBrx
spawn_mode: manual
status: pending
---
# D2: Model Cost Optimization

## Objective
Find a cheaper model that maintains Zoseph's voice quality. Test AFTER D1's prompt trim (testing a bloated prompt on a cheaper model is the wrong experiment).

## Scope
- Research VAPI-supported models and pricing
- Evaluate candidates: GPT-4o-mini, Gemini Flash 2.0, Groq Llama 3.3, DeepSeek V3
- Test each on:
  - Voice discipline compliance (1 question per turn, max 2 options, 2-3 sentences)
  - Concept accuracy (does it explain Meta-OS correctly?)
  - Tone/character (warm, direct, dry humor — not corporate)
  - Tool calling reliability (does it trigger assessCallerLevel correctly?)
  - Escalation handling (does it know when to offer V?)
  - Emotional detection (can it notice confusion/surprise from caller language?)
- Produce cost comparison table ($/min or $/1K tokens)
- Clear recommendation with tradeoff analysis

## Key Files
- `Skills/zo-hotline/config/hotline-assistant.json` (model config reference)
- `Skills/zo-hotline/scripts/hotline-webhook.ts` (model setting in assistant-request)

## Dependencies
- D1 should be complete first (trimmed prompt = fair test)

## Acceptance Criteria
- [ ] VAPI model compatibility confirmed for each candidate
- [ ] Cost comparison table produced
- [ ] Quality assessment per candidate across all 6 dimensions
- [ ] Clear recommendation with rationale
- [ ] If switching: documented prompt adjustments needed
