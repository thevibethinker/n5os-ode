---
created: 2026-02-17
last_edited: 2026-02-18
version: 2.0
provenance: con_D22Ewo8OGuQrMBrx
spawn_mode: manual
status: complete
dependencies: [D1, D2, D3, D5]
---
# D4: Conversation Design v3 — The Capstone

## Objective
Rewrite Zoseph's system prompt and conversation architecture using everything learned from D1 (infrastructure), D2 (model), D3 (research + competitive intel), and D5 (knowledge base + playbook).

## This Drop Synthesizes:
- D1's trimmed prompt baseline + caller profile injection pattern
- D1's knowledge index (how explainConcept now works)
- D2's model recommendation (stay with Claude Haiku 4.5 — no need to constrain prompt for cheaper models)
- D3's use cases, competitive landscape, messaging cheat sheet, idealism angle
- D5's playbook (explorer/challenger/builder pathways, proven phrases, danger zones)
- V's diagnostic observations from real calls
- The Master Pattern: Elicit → Mirror → Layer → Anchor

## Prior Drop Deposits (Read These First)

**D1 — Infrastructure:**
- Deposit: `N5/builds/zo-hotline-v4/deposits/D1-deposit.json`
- Trimmed system prompt: `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (901 words — this is your baseline to rewrite)
- Knowledge index: `Knowledge/zo-hotline/00-knowledge-index.md` (93 entries)
- Webhook (current): `Skills/zo-hotline/scripts/hotline-webhook.ts` (1,278 lines)

**D2 — Model:**
- Deposit: `N5/builds/zo-hotline-v4/deposits/D2-deposit.json`
- Full report: `N5/builds/zo-hotline-v4/deposits/D2-model-cost-optimization.md`
- **Decision: Stay with Claude Haiku 4.5.** Design freely around Anthropic strengths — nuanced instruction following, concession-pivot patterns, reliable tool calling. Token budget is comfortable; you can expand slightly from 901 words if the pathways need it.

**D3 — Research + Competitive:**
- Deposit: `N5/builds/zo-hotline-v4/deposits/D3-deposit.json`
- Community use cases: `Knowledge/zo-hotline/50-use-case-inspiration/community-use-cases.md`
- Competitive landscape: `Knowledge/zo-hotline/50-use-case-inspiration/competitive-landscape.md`
- Messaging cheat sheet: `Knowledge/zo-hotline/97-conversational-playbook/messaging-cheat-sheet.md`
- Idealism talking points: `Knowledge/zo-hotline/97-conversational-playbook/idealism-talking-points.md`
- Gap analysis: `Knowledge/zo-hotline/50-use-case-inspiration/gap-analysis-d3.md`
- **⚠️ These 5 files need concept mapping entries added to the webhook's `conceptFiles` object.**

**D5 — Zo Docs + Playbook:**
- Deposit: `N5/builds/zo-hotline-v4/deposits/D5-gap-analysis.md`
- Platform docs: `Knowledge/zo-hotline/96-zo-platform/` (41 files)
- Playbook: `Knowledge/zo-hotline/97-conversational-playbook/` (overview, explorer, challenger, builder, proven-phrases, danger-zones)
- Existing concept mappings: ~280 entries already in webhook

**Thematic analysis (the evidence base):**
- `Research/zo-hotline/hotline-thematic-analysis.md` (8 real calls analyzed)

**Environment note:** `DEEPGRAM_API_KEY` and `ANTHROPIC_API_KEY` are now available as env vars if needed for any testing.

## Scope

### 1. Pathway-Specific Socratic Sequences
Each pathway gets its own custom discovery + response flow:

**Explorer Pathway:**
- Discovery: "What kind of work?" → "What wastes your time?" → "What would change if that was handled?"
- Response: Paint specific future using Anchor technique. Lead with one concrete use case.
- Emotional awareness: Watch for spark of interest → go deeper. Watch for overwhelm → simplify.

**Challenger Pathway:**
- Discovery: "What tools are you using now?" → "What's not working?" → "Do you care about owning your stack?"
- Response: Concede ("Claude is great for X"), pivot to autonomy + persistence.
- Idealism vector: If they bite on open source / ownership → talk V's projects, community, Skill Exchange vision.
- Emotional awareness: Watch for defensiveness → don't push. Watch for curiosity → lean into differentiation.

**Builder Pathway:**
- Discovery: "What are you trying to build?" → "How technical are you, 1 to 5?" → "What have you tried so far?"
- Response: Calibrate technical depth to stated level. Expose calibration: "I can go more or less technical — just say the word."
- Layered solutions: Always offer simple version first, then advanced upgrade.
- Emotional awareness: Watch for confusion → drop technical level. Watch for impatience → skip basics, go direct.

### 2. Anti-Pattern Blockers (Hard Rules in System Prompt)
Wire the top danger zones directly into the prompt as NEVER rules:
- NEVER list more than 2 options
- NEVER use jargon without translating it
- NEVER describe mechanisms ("IMAP polling with regex") — describe outcomes ("it watches your email and pulls out the data")
- NEVER say "I can't do that" without offering what you CAN do
- NEVER ask more than 1 question per turn
- NEVER use corporate enthusiasm ("Absolutely!", "Great question!")

### 3. Emotional / Tonal Detection
Add explicit system prompt instructions for detecting and responding to:
- Silence after a statement → "Did that land, or should I explain it differently?"
- "Wait, really?" / surprise → lean in, go deeper
- "I don't know..." / overwhelm → simplify, offer the easy version
- Rapid-fire questions → match energy, be concise
- Skeptical tone / challenging → switch to Challenger pathway if not already there
- Confusion / consternation → slow down, use an analogy

### 4. Technical Calibration
- Builder pathway starts with "How technical are you?"
- Expose the calibration: "I can adjust anytime — just tell me more or less technical"
- Map calibration to language choices:
  - Level 1-2: "Click this button", "It watches your email"
  - Level 3: "Set up a scheduled agent", "Create a webhook"
  - Level 4-5: "Write a Bun script", "Use the zo.space API route"

### 5. Master Pattern Integration
Ensure all pathways follow Elicit → Mirror → Layer → Anchor:
- **Elicit**: Pathway-specific discovery questions (above)
- **Mirror**: Explicit instruction to reflect back what was heard before advising
- **Layer**: Simple solution → advanced upgrade (always)
- **Anchor**: Paint a specific future ("Imagine tomorrow morning...")

### 6. Competitive Response Framework
From D3's messaging cheat sheet, wire in:
- Honest concessions for each competitor
- Pivot language to Zo's actual advantages
- "Zo works while you sleep" as the anchor differentiation
- Idealism angle when caller shows affinity

### 7. Knowledge Index Integration
- System prompt references the knowledge index for concept lookups
- explainConcept tool uses index to decide which file to read
- Reduces hallucination: Zoseph knows what it knows

### 8. Daily Analysis Loop Enhancement
- Update `call_analysis_loop.py` to include:
  - Messaging effectiveness tracking (which approaches correlated with which outcomes)
  - Standout call spotlights (from D1's flagging) rolled into the daily digest
  - "Messaging That Worked This Week" section
  - Trend detection: is a particular approach gaining or losing effectiveness?

### 9. New Modes (from original D4 scope)
- **Troubleshoot mode**: Caller has a specific error or broken thing
- **Compare mode**: Caller is comparing Zo to another tool
- **Onboard mode**: Caller just signed up, needs first-15-minutes guidance

### 10. Edge Case Handling
- Silence (caller goes quiet)
- Rapid-fire (caller asking question after question without pausing)
- Emotional caller (frustrated, anxious about career/AI)
- Off-topic (caller asking about unrelated things)
- Career crossover (caller asking about career advice → this is Zo hotline, not Careerspan)

## Key Files
- `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (major rewrite)
- `Skills/zo-hotline/scripts/hotline-webhook.ts` (mode handling, tool updates)
- `Knowledge/zo-hotline/97-conversational-playbook/*` (extend pathways)
- `Skills/zo-hotline/scripts/call_analysis_loop.py` (messaging effectiveness)

## Acceptance Criteria
- [ ] All 3 pathways have custom Socratic discovery + response sequences
- [ ] Anti-pattern blockers wired as hard NEVER rules in system prompt
- [ ] Emotional detection instructions explicit in system prompt
- [ ] Technical calibration built into Builder pathway
- [ ] Master Pattern (Elicit → Mirror → Layer → Anchor) integrated across all pathways
- [ ] Competitive response framework wired in with honest concessions + pivots
- [ ] Knowledge index integrated into explainConcept flow
- [ ] Daily analysis enhanced with messaging effectiveness tracking
- [ ] All 12 test scenarios covered (original + new modes)
- [ ] System prompt production-ready and within token budget
