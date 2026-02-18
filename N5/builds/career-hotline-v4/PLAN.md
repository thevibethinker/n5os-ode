---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_3BuG4GkgO8ROXcds
---

# Career Coaching Hotline V4 — Build Plan

## Objective
Take the Careerspan Career Coaching Hotline (Zozie) from initial build to prime time — faster, cheaper, smarter, better-informed, more ergonomic.

## Current State
- **Persona**: Zozie (AI career coach, female, direct style)
- **Model**: Claude Haiku 4.5 (via VAPI → Anthropic)
- **Webhook**: 2,224 lines, port 8848
- **Knowledge base**: 17 files in Knowledge/career-coaching-hotline/
- **Build artifacts**: system prompt (555 lines), concept map (65 entries), tool specs
- **Call data**: 5 calls logged
- **Tools**: lookupCaller, assessCareerStage, getCareerRecommendations, explainCareerConcept, plus intake/resume features
- **Monetization**: Free tier (15 min), booking link, purchase URL

## Shared Infra (With Zo Hotline)
Both hotlines share:
- VAPI webhook pattern (assistant-request → tool-calls → end-of-call-report)
- DuckDB call logging schema
- ElevenLabs voice config structure
- Latency tuning parameters (startSpeakingPlan, stopSpeakingPlan, chunkPlan)
- Post-call SMS notification pattern (notifyV)
- LLM topic classification pattern
- Daily analysis loop architecture

**Changes to shared infra must be tested against both hotlines.**

## Drops

### Wave 1 (Parallel — all independent)

#### D1: Latency Optimization
- Audit system prompt size (555 lines — likely too large for voice)
- Trim/restructure for minimum viable prompt
- Optimize VAPI voice/endpointing params
- Reduce tool call overhead (Python subprocess for DuckDB → alternatives?)
- Profile the zoAsk calls — each one adds latency to tool responses
- **Shared infra**: voice config, endpointing plan, chunk plan

#### D2: Model Cost Optimization
- Benchmark current model (Claude Haiku 4.5) on career coaching scenarios
- Test alternatives: GPT-4o-mini, Gemini Flash, smaller Claude variants
- Measure quality degradation vs cost savings
- Document prompt adjustments needed per model
- **Shared infra**: model swap pattern in webhook

#### D3: Career Coaching Research
- What are job seekers actually struggling with in 2026?
- Reddit r/jobs, r/careerguidance, r/resumes — common pain points
- LinkedIn discourse on job search challenges
- AI coaching competitor landscape (what others are doing)
- Gap analysis: what callers might ask that Zozie can't handle

#### D5: Knowledge Base Optimization
- Audit current 17 knowledge files — are they being used? Which concepts trigger?
- Consolidate overlapping content
- Add missing topics from research (D3)
- Optimize file sizes for faster reads during tool calls
- Structure for tool-call retrieval efficiency

### Wave 2 (Synthesis — depends on Wave 1)

#### D4: Conversation Design v3
- Incorporate V's diagnostic call findings
- Expand decision tree for more situations
- Improve mode detection and switching
- Better handling of edge cases
- Integrate research findings from D3
- Apply latency-optimized prompt from D1
- Apply model recommendations from D2
- Wire up optimized knowledge from D5

## Execution
- **All drops are manual-spawn** — V controls the conversation and adapts
- **Interactive build** — work happens in this conversation thread
- Wave 1 drops can run in any order
- D4 synthesizes all Wave 1 outputs

## Success Criteria
- Measurably faster response times
- Model cost reduction ≥30% without quality loss
- Expanded knowledge base covering common caller scenarios
- Decision tree handles V's 12 diagnostic scenarios gracefully
- Production-ready for public launch
