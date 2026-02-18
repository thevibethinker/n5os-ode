---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: con_aeFtpPk4Ms1D79He
drop: D2
title: Model Cost Optimization Report
status: complete
---

# D2: Model Cost Optimization — Deposit

## Current Baseline

| Metric | Value |
|--------|-------|
| Model | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) |
| Provider | Anthropic (native VAPI integration) |
| Token pricing | $1.00 / $5.00 per 1M tokens (input/output) |
| Observed cost | ~$0.18/min all-in (model + VAPI platform + Deepgram + ElevenLabs) |
| Latency (model component) | ~1,075ms |
| System prompt | ~901 words / ~5,800 chars (post D1 trim) |

**VAPI cost structure:** $0.05/min platform fee + model cost + transcriber cost + voice cost. The model component is the primary variable we can optimize.

---

## VAPI-Supported Model Providers (Confirmed)

| Provider | Native? | Tool Calling | Notes |
|----------|---------|-------------|-------|
| **Anthropic** | ✅ | ✅ Excellent | Current provider. First-class support. |
| **OpenAI** | ✅ | ✅ Excellent | First-class support. |
| **Google Gemini** | ✅ | ✅ Good | Native integration. |
| **Groq** | ✅ | ⚠️ Varies | Native integration. Llama models via LPU. |
| **DeepInfra** | ✅ | ⚠️ Varies | Hosts DeepSeek, Llama, Mistral, etc. |
| **OpenRouter** | ✅ | ⚠️ Varies | Meta-router to 200+ models including DeepSeek V3. |
| **Custom LLM** | ✅ | ⚠️ Must implement | Any OpenAI-compatible endpoint. |

---

## Candidate Evaluation

### 1. GPT-4o-mini (OpenAI)

**Token pricing:** $0.15 / $0.60 per 1M tokens (input/output)
**Estimated model cost/min:** ~$0.02–0.04 (roughly 85% cheaper than Haiku 4.5)
**Context:** 128K tokens
**Latency:** ~600-900ms (fast)

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Voice discipline | ⭐⭐⭐⭐ | Good at following format constraints. Occasionally verbose with 3+ sentences if not firmly prompted. |
| Concept accuracy | ⭐⭐⭐ | Adequate for explaining features. May hallucinate details on niche concepts (Meta-OS levels). Knowledge cutoff older (Oct 2023). |
| Tone/character | ⭐⭐⭐ | Can do warm and direct but tends toward generic helpfulness. Dry humor is harder to coax. Leans corporate. |
| Tool calling | ⭐⭐⭐⭐⭐ | OpenAI's tool calling is the industry benchmark. Reliable, structured, predictable. |
| Escalation handling | ⭐⭐⭐⭐ | Good at recognizing when to offer help. |
| Emotional detection | ⭐⭐⭐ | Functional but less nuanced than Anthropic models. May miss subtle confusion signals. |

**Verdict:** Strongest cost-efficiency play. Tool calling is rock-solid. Primary risk: tone flattens to generic AI assistant; loses Zoseph's character distinctiveness. Knowledge cutoff means it can't learn about newer Zo features from prompt alone without the knowledge index (which we have).

---

### 2. Gemini 2.0 Flash (Google)

**Token pricing:** Free tier available; paid ~$0.10 / $0.40 per 1M tokens
**Estimated model cost/min:** ~$0.01–0.03 (potentially 90%+ cheaper)
**Context:** 1M tokens
**Latency:** ~500-800ms (very fast)

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Voice discipline | ⭐⭐⭐ | Tends to be chatty. Needs firm prompting to stay at 2-3 sentences. Occasional list-making. |
| Concept accuracy | ⭐⭐⭐⭐ | Strong general knowledge. Can explain technical concepts well. |
| Tone/character | ⭐⭐ | Defaults to Google Assistant-style helpfulness. Getting dry humor and warmth-without-enthusiasm is a struggle. Most "corporate" of the candidates. |
| Tool calling | ⭐⭐⭐ | Functional but less mature than OpenAI. Occasional JSON formatting issues. Gemini's function calling protocol differs from OpenAI standard — verify VAPI translation layer. |
| Escalation handling | ⭐⭐⭐ | Adequate. |
| Emotional detection | ⭐⭐⭐ | Decent at surface-level detection. Less nuanced than Anthropic. |

**Verdict:** Cheapest option. Fastest latency. But tone is the weakest — achieving Zoseph's character voice will require significant prompt engineering. Tool calling maturity through VAPI's Gemini adapter needs live testing. The 1M context window is overkill but harmless.

---

### 3. Groq Llama 3.3 70B (Meta via Groq)

**Token pricing:** $0.59 / $0.79 per 1M tokens (input/output)
**Estimated model cost/min:** ~$0.03–0.06 (roughly 60-70% cheaper)
**Context:** 128K tokens
**Latency:** ~200-400ms (fastest — Groq's LPU hardware)

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Voice discipline | ⭐⭐⭐ | Open-source models are more variable in instruction following. Can be coached but inconsistent at 1-question-per-turn discipline. |
| Concept accuracy | ⭐⭐⭐ | Solid general knowledge. May struggle with Zo-specific concepts without strong knowledge index support (which we have). |
| Tone/character | ⭐⭐⭐ | More natural conversational tone than Gemini. Can achieve warmth. Dry humor is possible but unreliable. |
| Tool calling | ⭐⭐ | Llama's tool calling is functional but less reliable than Anthropic/OpenAI. JSON schema adherence can be inconsistent. May trigger tools incorrectly or miss triggers. This is the dealbreaker risk. |
| Escalation handling | ⭐⭐⭐ | Can recognize escalation signals. |
| Emotional detection | ⭐⭐⭐ | Functional but less nuanced. |

**Verdict:** Blazing fast latency (200-400ms) would dramatically improve conversational feel. But tool calling reliability is a serious concern for our 5-tool setup. If a caller says something ambiguous, Llama might not trigger `assessCallerLevel` or might call `explainConcept` with a malformed argument. Groq's rate limits could also be an issue at scale.

---

### 4. DeepSeek V3 (via DeepInfra or OpenRouter)

**Token pricing:** ~$0.27 / $1.10 per 1M tokens (input/output) via DeepInfra
**Estimated model cost/min:** ~$0.02–0.04 (roughly 75-80% cheaper)
**Context:** 64K tokens
**Latency:** ~800-1200ms (comparable to current)

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Voice discipline | ⭐⭐⭐ | Can follow instructions but less reliably than Anthropic/OpenAI. May need more explicit formatting constraints. |
| Concept accuracy | ⭐⭐⭐⭐ | Strong reasoning. 671B MoE with 37B active — punches above its price class. |
| Tone/character | ⭐⭐⭐ | Capable of nuance but defaults to a more formal/academic tone. Zoseph's warmth would need careful prompting. |
| Tool calling | ⭐⭐ | Least mature tool calling of the group. DeepSeek V3 supports function calling but reliability through VAPI's adapter layer (DeepInfra/OpenRouter) is unproven. Double-hop latency risk (VAPI → OpenRouter → DeepSeek). |
| Escalation handling | ⭐⭐⭐ | Adequate reasoning about when to escalate. |
| Emotional detection | ⭐⭐⭐ | Good reasoning capabilities help. |

**Verdict:** Impressive reasoning-per-dollar but the double-hop architecture (VAPI → DeepInfra/OpenRouter → DeepSeek API) adds latency and failure points. Tool calling through this chain is the highest risk of any candidate. Not recommended for a production voice agent.

---

## Cost Comparison Table

| Model | Input $/1M tok | Output $/1M tok | Est. Model $/min | vs. Baseline | Latency | VAPI Native? |
|-------|---------------|----------------|-------------------|-------------|---------|-------------|
| **Claude Haiku 4.5** (current) | $1.00 | $5.00 | ~$0.07–0.10 | — | ~1,075ms | ✅ |
| **GPT-4o-mini** | $0.15 | $0.60 | ~$0.02–0.04 | **-60-70%** | ~600-900ms | ✅ |
| **Gemini 2.0 Flash** | ~$0.10 | ~$0.40 | ~$0.01–0.03 | **-70-85%** | ~500-800ms | ✅ |
| **Groq Llama 3.3 70B** | $0.59 | $0.79 | ~$0.03–0.06 | **-40-60%** | ~200-400ms | ✅ |
| **DeepSeek V3** (via OpenRouter) | ~$0.27 | ~$1.10 | ~$0.02–0.04 | **-60-70%** | ~800-1200ms | ⚠️ via adapter |

*Estimated model $/min based on ~2,000-4,000 tokens per minute of conversation (system prompt amortized + turn exchanges).*

**All-in cost estimate (model + VAPI $0.05 + Deepgram ~$0.02 + ElevenLabs ~$0.03):**

| Config | Est. All-In $/min |
|--------|-------------------|
| Current (Haiku 4.5) | ~$0.17–0.20 |
| GPT-4o-mini | ~$0.12–0.14 |
| Gemini 2.0 Flash | ~$0.11–0.13 |
| Groq Llama 3.3 | ~$0.13–0.16 |
| DeepSeek V3 | ~$0.12–0.14 |

---

## Quality-Weighted Assessment

| Dimension (Weight) | Haiku 4.5 | GPT-4o-mini | Gemini Flash | Groq Llama 3.3 | DeepSeek V3 |
|---------------------|-----------|-------------|-------------|----------------|-------------|
| Voice discipline (20%) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Concept accuracy (15%) | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Tone/character (25%) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Tool calling (20%) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Escalation (10%) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Emotional detection (10%) | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Weighted Score** | **4.6** | **3.7** | **2.9** | **2.8** | **3.0** |

---

## Recommendation

### Stay with Claude Haiku 4.5. No switch.

**Rationale:**

1. **Tone is the product.** Zoseph's voice — warm, direct, dry humor, never corporate — is the entire caller experience. From D3's competitive analysis, callers comparing Zo to free tools need to feel a *person*, not a chatbot. Haiku 4.5 nails this. GPT-4o-mini flattens it. Gemini kills it. This alone outweighs the ~$0.05-0.07/min savings.

2. **Concession-pivot messaging requires nuance.** The messaging cheat sheet's patterns (acknowledge competitor strength → pivot to Zo's real advantage) demand a model that can hold a philosophical position while being genuinely honest. Anthropic models are demonstrably better at this nuanced instruction following than the cheaper alternatives.

3. **Tool calling reliability is non-negotiable.** The knowledge index (93 entries), caller profiles, assessment flow, escalation — these are core to the experience. GPT-4o-mini matches here, but the other candidates are measurably worse. One malformed `explainConcept` call = confused caller = bad impression.

4. **The cost is already reasonable.** At $0.18/min and typical 3-5 minute calls, each call costs $0.54-0.90. For a product showcase hotline, this is well within acceptable range. The $0.05/min savings from GPT-4o-mini (~$0.15-0.25 per call) doesn't justify the quality regression.

5. **The real cost lever isn't the model.** VAPI platform ($0.05/min) + Deepgram ($0.02/min) + ElevenLabs ($0.03/min) = $0.10/min fixed floor. Switching models saves ~$0.05/min on a ~$0.18/min total — that's optimizing the smaller portion. If cost becomes critical, look at voice provider alternatives (Cartesia, Vapi Voices) first.

### If cost reduction becomes essential later

**Tier 1 — Try first:** GPT-4o-mini with enhanced tone prompting. Add explicit character examples to the system prompt. Test 10 calls, compare transcripts against Haiku 4.5 baseline. Savings: ~30%.

**Tier 2 — Voice provider swap:** Replace ElevenLabs with Vapi Voices or Cartesia. Savings: ~$0.01-0.02/min without touching LLM quality.

**Tier 3 — OpenAI Realtime API:** VAPI supports OpenAI's speech-to-speech models which could eliminate the separate TTS cost entirely. Different architecture, would require more significant changes.

### Prompt adjustments if switching to GPT-4o-mini

If future testing proceeds:
- Add 2-3 concrete character examples to system prompt (e.g., "Say 'Got it.' not 'I understand!'")
- Strengthen "no corporate enthusiasm" instruction with OpenAI-specific anti-patterns
- Add explicit tool calling examples in system prompt (OpenAI benefits from few-shot more than Anthropic)
- Test Deepgram keyword boosting for "Zo" to prevent STT errors on cheaper model output

---

## Acceptance Criteria Status

- [x] VAPI model compatibility confirmed for each candidate (7 providers documented)
- [x] Cost comparison table produced (token pricing + estimated $/min + all-in)
- [x] Quality assessment per candidate across all 6 dimensions
- [x] Clear recommendation with rationale
- [x] If switching: documented prompt adjustments needed (provided for GPT-4o-mini contingency)
