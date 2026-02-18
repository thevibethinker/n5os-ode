---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_3BuG4GkgO8ROXcds
---

# Zo Hotline V4 — Build Plan

## Objective
Take the Zo Hotline from "working prototype" to "prime time" — faster, cheaper, smarter, better-informed, more ergonomic.

## Build Type
Interactive manual-spawn. V controls each workstream conversationally.

## Workstreams (4 Active Drops)

### D1: Latency Optimization (`ws1-latency`)
**Goal**: Reduce time-to-first-word and overall responsiveness.
**Levers**:
- System prompt length reduction (currently ~2500 words + dynamic context)
- VAPI config tuning (startSpeakingPlan, endpointing, chunk sizing)
- Knowledge retrieval path optimization (Python subprocess overhead)
- Recent call context injection trimming
- Tool response latency (DuckDB query overhead via subprocess)
**Inputs**: Current hotline-webhook.ts, zoseph-system-prompt.md, VAPI docs
**Outputs**: Optimized config, trimmed prompt, measured benchmarks
**spawn_mode**: manual

### D2: Model Cost Optimization (`ws2-model`)
**Goal**: Evaluate cheaper model alternatives without quality degradation.
**Candidates**:
- GPT-4o-mini (VAPI native, very cheap)
- Gemini 2.0 Flash (check VAPI support)
- Groq Llama 3.3 70B (ultra-fast inference)
- DeepSeek (cost leader)
**Method**: Compare on V's diagnostic test scenarios — voice discipline compliance, concept accuracy, escalation handling, tone
**Inputs**: VAPI model docs, test scenario results, current Haiku baseline
**Outputs**: Model recommendation with tradeoff analysis, A/B test plan
**spawn_mode**: manual

### D3: Use Case Research (`ws3-research`)
**Goal**: Discover what real Zo users are actually building to inform Zoseph's knowledge.
**Sources**:
- Zo Discord (showcases, help, general channels)
- r/ZoComputer subreddit
- X/Twitter: @zocomputer mentions, community posts
- Zo blog / changelog for recent features
**Inputs**: External community sources
**Outputs**: Synthesized use case library, knowledge base update recommendations
**spawn_mode**: manual

### D4: Conversation Design v3 (`ws5-conversation`)
**Goal**: Expand decision tree beyond Discover/Guide, improve edge case handling.
**New modes to consider**:
- Troubleshoot mode (debugging-specific flow)
- Compare mode ("Zo vs X" questions)
- Build mode (walk through building something step-by-step)
- Onboard mode (structured first-time setup walkthrough)
**Also**: Better silence handling, rapid-fire, emotional callers, off-topic, career crossover
**Inputs**: V's diagnostic call observations, WS3 use cases, WS6 call patterns
**Outputs**: Updated system prompt, expanded mode definitions, fallback behaviors
**spawn_mode**: manual
**Dependencies**: Benefits from D1 (latency), D2 (model), D3 (research) outputs

## Deferred Workstreams

### WS4: Knowledge Base Audit (not in this build — may run separately)
### WS6: Deep Call Data Analysis (may be done as part of V's diagnostic or separately)

## Wave Structure
- **Wave 1**: D1 (Latency) + D2 (Model) + D3 (Research) — can proceed in parallel
- **Wave 2**: D4 (Conversation Design) — synthesis, benefits from Wave 1 outputs
- V's diagnostic calls feed observations into D4

## Success Criteria
- Measurably faster response times (TTFW baseline → improved)
- Model cost reduction ≥30% without quality loss
- 10+ new use cases from community research incorporated
- Expanded decision tree covering all 12 test scenarios gracefully
