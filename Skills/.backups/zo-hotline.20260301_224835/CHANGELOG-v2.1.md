---
created: 2026-02-14
version: 2.1
provenance: zo-hotline-optimization-session
---

# Zoseph Hotline v2.1 — Change Log & Baseline

## Pre-Change Baseline (v2.0)

### Model
- **LLM:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Estimated TTFT:** ~1,000ms
- **LLM cost:** $3/$15 per M tokens (input/output)

### Timing Configuration
| Parameter | v2.0 Value |
|---|---|
| `startSpeakingPlan.waitSeconds` | 0.6 |
| `transcriptionEndpointingPlan.onPunctuationSeconds` | 0.1 |
| `transcriptionEndpointingPlan.onNoPunctuationSeconds` | 1.2 |
| `transcriptionEndpointingPlan.onNumberSeconds` | 0.5 |
| `responseDelaySeconds` | 0.3 |
| `stopSpeakingPlan.numWords` | 0 |
| `stopSpeakingPlan.voiceSeconds` | 0.2 |
| `stopSpeakingPlan.backoffSeconds` | 1.0 |

### TTS Configuration
| Parameter | v2.0 Value |
|---|---|
| `voice.stability` | 0.45 |
| `voice.similarityBoost` | 0.75 |
| `voice.style` | 0.65 |
| `voice.model` | eleven_flash_v2_5 |
| `voice.optimizeStreamingLatency` | 4 |
| `chunkPlan.minCharacters` | 20 |

### System Prompt
- **Word count:** ~1,020 words / ~1,400 tokens
- **Modes:** 2 (Discover, Guide)
- **Verbosity levels:** 3 defined (terse, normal, detailed) via env var
- **Settings mode:** None
- **Testing mode:** None
- **Assessment trigger:** Listed in tools section only, no behavioral trigger
- **Escalation:** SMS to V only, no Calendly link
- **Contact validation:** Accepts any string (Discord, social handles, etc.)
- **Creator/privacy info:** None
- **Mid-call switching:** Not addressed
- **Intro message:** "... Hey, welcome to the Zo hotline. I'm Zoseph. I can help you in two ways — exploring what Zo can do for you, or walking through something specific you're trying to set up. Which sounds right?"

### Estimated Per-Turn Latency Stack (v2.0)
| Component | Estimated Time |
|---|---|
| Turn detection (worst case: no punctuation) | 1,200ms |
| Wait before processing | 600ms |
| Response delay | 300ms |
| LLM TTFT (Sonnet 4) | ~1,000ms |
| TTS first audio | ~100ms |
| **Total worst case** | **~3,200ms** |

---

## v2.1 Changes

### Phase 1: Latency Optimizations

#### Model Swap
- **Before:** Claude Sonnet 4 (`claude-sonnet-4-20250514`) — TTFT ~1,000ms, $3/$15 per M
- **After:** Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) — TTFT ~600ms, $1/$5 per M
- **Impact:** ~400ms faster TTFT, 67% cheaper on LLM costs

#### Turn Detection Timing
| Parameter | Before | After | Savings |
|---|---|---|---|
| `waitSeconds` | 0.6 | 0.4 | 200ms |
| `onNoPunctuationSeconds` | 1.2 | 0.8 | 400ms |
| `onNumberSeconds` | 0.5 | 0.4 | 100ms |

#### Response Delay
- **Before:** 0.3s → **After:** 0.1s — **Savings:** 200ms

#### TTS Stability
- **Before:** 0.45 → **After:** 0.35 — slightly faster streaming

### Phase 2: System Prompt Rewrite

- Content words: ~1,020 → ~1,436 (net increase due to 7 new behavioral capabilities, despite trimming redundancy)
- Removed: bad example block, "Adding Modes (Future)" section, verbose verbosity descriptions, redundant opening protocol
- Added 7 new capabilities: settings mode (verbosity toggle), secret testing mode, take-charge behavior, assessment triggers, mid-call mode switching, loop-back, privacy/creator/investor/contact-validation sections
- New intro message with Vibe Thinker Hotline branding + human escalation offer at outset
- Note: Larger prompt adds ~50-100ms TTFT vs old, but Haiku 4.5 swap saves ~400ms — net positive

### Phase 3: Escalation Flow Update

- Escalation SMS now includes Calendly link placeholder
- Contact collection prompt encourages email/phone over social handles
- V's public contact info (LinkedIn: Vrijen Attawar, Twitter: @thevibethinker) available for sharing

### Estimated Per-Turn Latency Stack (v2.1)
| Component | Estimated Time |
|---|---|
| Turn detection (worst case: no punctuation) | 800ms |
| Wait before processing | 400ms |
| Response delay | 100ms |
| LLM TTFT (Haiku 4.5) | ~600ms |
| TTS first audio | ~100ms |
| **Total worst case** | **~2,000ms** |

### Summary
- **Worst-case latency:** 3,200ms → 2,000ms (**37.5% reduction**)
- **LLM cost:** 67% reduction ($3/$15 → $1/$5 per M tokens)
- **Prompt size:** ~20% smaller (fewer tokens to process)
