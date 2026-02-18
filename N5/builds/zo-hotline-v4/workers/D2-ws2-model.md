---
created: 2026-02-17
last_edited: 2026-02-18
version: 2.1
provenance: con_D22Ewo8OGuQrMBrx
spawn_mode: manual
status: pending
dependencies: [D1]
---
# D2: Model Cost Optimization

## Context from Prior Drops

**Current baseline (from VAPI dashboard + D1):**
- Model: Claude Haiku 4.5 (Anthropic) via VAPI
- Cost: ~$0.18/min
- Latency: ~1,075ms
- System prompt: 901 words / ~5,800 chars (trimmed 53% in D1)
- Prompt path: `Skills/zo-hotline/prompts/zoseph-system-prompt.md`

**From D3 (competitive landscape):**
- Callers frequently compare Zo to free ChatGPT/Claude — cost sensitivity matters for the product, and for us operationally
- The messaging cheat sheet (`Knowledge/zo-hotline/97-conversational-playbook/messaging-cheat-sheet.md`) contains concession-pivot patterns that require **nuance** — the model must acknowledge competitor strengths then pivot gracefully, not just blindly promote Zo
- Idealism talking points require the model to hold a philosophical position convincingly

**Quality bar from D1 infrastructure:**
- Model must trigger tool calls reliably (assessCallerLevel, explainConcept, requestEscalation, collectFeedback)
- Model must respect voice discipline (1 question per turn, max 2 options, 2-3 sentences)
- Model must handle the knowledge index lookup pattern (explainConcept reads files from disk)

**Test material for evaluation:**
- System prompt: `Skills/zo-hotline/prompts/zoseph-system-prompt.md`
- Messaging patterns: `Knowledge/zo-hotline/97-conversational-playbook/messaging-cheat-sheet.md`
- Competitive responses: `Knowledge/zo-hotline/50-use-case-inspiration/competitive-landscape.md`

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
