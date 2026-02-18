# Zo Hotline Improvement Plan

**Created:** 2026-02-12
**Updated:** 2026-02-14
**Status:** V3 Self-Improving Analysis Loop — Implemented

---

## V1 Improvements (2026-02-12) — COMPLETED

All items from the original plan have been implemented:

- [x] Rename persona from "Guide" to "Zoseph"
- [x] Latency optimization (startSpeakingPlan, stopSpeakingPlan, smart endpointing, chunk streaming)
- [x] Verbosity control via ZOSEPH_VERBOSITY env var (terse/normal/detailed)
- [x] Zo/Zoho disambiguation (Deepgram keyword boosting + system prompt priming)
- [x] Vibe Thinking Protocol integration (Expand/Synthesize/Threshold/Crystallize)
- [x] ElevenLabs voice tuning (stability 0.45, style 0.65, Daniel voice)
- [x] Backchanneling enabled
- [x] Post-call SMS notifications (rule whitelisting fix applied 2026-02-12)

---

## V2 Improvements (2026-02-13) — Conversation Design Overhaul

### Evidence Base

**Call data review:** 12 calls analyzed from Feb 12-13 via DuckDB. 5 substantive calls reviewed in detail.

**Caller frustration themes identified:**
1. Name confusion (Zo vs Zoho/Zelle)
2. Getting cut off when conversation gets useful (no persistence)
3. Zoseph can't DO anything (advisory-only gap)

**David Spiegel feedback session** (post-hotline-call debrief, 2026-02-12):
- First utterance gets clipped on call connect
- Sentences too long — "use as short as sentences as possible"
- Multiple options are unlistable — "by the time I'm saying number three, you can't remember 1 and 2"
- Missing caller context — "I don't know what the agenda is, why did I call this thing?"
- IVR best practices as the reference model
- Use case / intent routing — different modes for different caller needs
- Positive: Zo differentiation pitch was convincing when challenged

**Best practices research:** Google Dialogflow CX, VoiceInfra, Marlie.ai, Ada voice agent guides.

### Problems Addressed

| # | Problem | Solution | Status |
|---|---------|----------|--------|
| 1 | Questions too long/branching | Voice Discipline rules: 1 question per turn, max 2 options, 2-3 sentences max | Implemented |
| 2 | No warm intro | Opening Protocol: friendly intro + two clear paths (Discover / Guide) | Implemented |
| 3 | No mode detection | Two modes: Discover (new/curious) and Guide (active user, specific task) | Implemented |
| 4 | Purpose not fulfilled | Reframed as onboarding concierge, not detached advisor | Implemented |
| 5 | First utterance clipped | Added pause buffer in first message + bumped waitSeconds to 0.6 | Implemented |

### Files Modified

| File | Change |
|------|--------|
| `prompts/zoseph-system-prompt.md` | Full rewrite — V2 conversation design with voice discipline, opening protocol, Discover/Guide modes |
| `scripts/hotline-webhook.ts` | New first message with pause buffer, waitSeconds 0.6 |
| `IMPROVEMENT_PLAN.md` | This file — updated with V2 analysis and status |

### Key Design Decisions

**Voice Discipline rules** (from IVR best practices + David feedback):
- One question per turn — never two
- Max 2 options — never 3 or 4 (callers can't hold more than 2 in audio)
- Each option is a short phrase, not a sentence
- 2-3 sentences max per turn
- No branching logic ("if X then... but if Y then...")
- End with silence, not trailing filler

**Two-mode architecture** (extensible):
- **Discover mode:** For new/curious callers. Goal = get them excited about one concrete use case.
- **Guide mode:** For active users with a specific task. Goal = unblock them or give the next clear step.
- Additional modes can be added later following the same Trigger/Goal/Approach pattern.

**First message design:**
- Starts with `...` to absorb the audio connection delay (prevents clipped opening)
- Friendly, brief intro ("Hey, welcome...")
- Names the two help modes explicitly
- Ends with a single question ("Which sounds right?")

**Zo differentiation talking points added:**
- Persistent server (always on, not session-based)
- Model choice (not locked to one provider)
- Autonomous background agents
- Single surface vs stitching tools together
- Cost effective ($9/mo + compute vs $100+/mo)

---

## Testing Checklist (V2)

- [ ] Restart hotline service: `supervisorctl restart zo-hotline-webhook`
- [ ] Test call: verify first message plays cleanly (no clipping)
- [ ] Test Discover mode: call as curious newcomer, verify 1-question-at-a-time flow
- [ ] Test Guide mode: call with a specific task, verify focused troubleshooting
- [ ] Test option discipline: confirm Zoseph never offers more than 2 choices
- [ ] Test sentence length: confirm responses stay at 2-3 sentences
- [ ] Test Zo differentiation: ask "why Zo instead of Claude?" — verify solid answer
- [ ] Test escalation: ask for hands-on help, verify SMS notification to V

---

## Success Metrics (V2)

| Metric | V1 Baseline | V2 Target |
|--------|-------------|-----------|
| Avg response length | ~4-6 sentences | 1-3 sentences |
| Options per question | 3-4 (unbounded) | Max 2 |
| Questions per turn | 1-2 | Exactly 1 |
| First message clipping | Reported | Eliminated |
| Caller knows purpose | No (confused) | Yes (two clear paths) |
| Caller sentiment (positive) | 60% (3/5) | 80%+ |

---

## V3 Improvements (2026-02-14) — Self-Improving Analysis Loop

### What Changed

| # | Enhancement | Description | Status |
|---|-------------|-------------|--------|
| 1 | LLM-powered drop-off analysis | Replaced regex-based `dropoff_analyzer.py` with `/zo/ask` LLM classification | Implemented |
| 2 | Daily scheduled analysis agent | 6pm ET daily agent runs `call_analysis_loop.py` covering previous day | Implemented |
| 3 | Caller insights tracking | `caller_insights` table tracks returning callers, topics, satisfaction trends | Implemented |
| 4 | Webhook DDL completeness | Added `daily_analysis`, `caller_insights` table DDL to webhook `initDb()` | Implemented |
| 5 | Topic history merging | `update_caller_insights` merges deduplicated topics from call data | Implemented |
| 6 | Schema documentation | Updated `schema.yaml` with all new tables and query examples | Implemented |
| 7 | Zo team executive summary | Daily LLM briefing with Product/GTM/Founders sections | Implemented |
| 8 | Caller profile building | Extracts caller identity from transcripts (name, role, interests) | Implemented |
| 9 | JSON parsing robustness | Fallback extraction for LLM responses with surrounding text | Implemented |
| 10 | Schema column fix | Fixed `rating`→`satisfaction` mismatch in schema.yaml | Implemented |

### Key Design Decisions

**LLM over regex:** All semantic classification uses `/zo/ask` API calls. Regex was previously used for drop-off categorization (duration thresholds + keyword matching). LLM classification provides richer, context-aware diagnosis of why callers dropped off.

**Single-batch LLM calls:** Drop-off analyzer sends all short calls in one prompt rather than one-per-call, reducing API overhead and enabling cross-call pattern recognition.

**Daily analysis cadence:** 6pm ET chosen to capture full business day. The agent runs `call_analysis_loop.py` which writes a markdown report and structured data to DuckDB.

**Caller insights from feedback:** The `caller_insights` table is populated from voluntary feedback entries (first name matching). No phone numbers or PII beyond first names.

### Files Modified

| File | Change |
|------|--------|
| `scripts/dropoff_analyzer.py` | Full rewrite — regex → LLM classification via `/zo/ask` |
| `scripts/call_analysis_loop.py` | Enhanced caller insights, added executive summary + caller profile extraction, robust JSON parsing |
| `scripts/hotline-webhook.ts` | Added DDL for `daily_analysis` and `caller_insights` tables |
| `SKILL.md` | Added self-improving analysis section, updated architecture listing |
| `IMPROVEMENT_PLAN.md` | This file — V3 documentation |
| `Datasets/zo-hotline-calls/schema.yaml` | Documented `feedback`, `daily_analysis`, `caller_insights` tables; fixed `rating`→`satisfaction` |

### Testing Checklist (V3)

- [ ] Run `call_analysis_loop.py --dry-run` — verify LLM analysis output
- [ ] Run `dropoff_analyzer.py --dry-run` — verify LLM drop-off classification
- [ ] Verify daily agent fires at 6pm ET and sends email summary
- [ ] Check `daily_analysis` table populated after agent run
- [ ] Check `caller_insights` table populated after feedback with topic merge
- [ ] Verify returning caller topic history deduplication works correctly

---

## Future Considerations

- **V's voice clone:** Train ElevenLabs on V's voice for authenticity
- **Zo-to-Zo calling:** Have Zoseph sign up for services (Boardy etc.) autonomously
- **Additional modes:** Billing, competitive comparison, API troubleshooting — add as patterns emerge
- **Post-call follow-up:** SMS with a one-liner recap + link to relevant docs
- **Call handoff to V:** Live transfer when escalation is requested (vs async callback)
- **Satisfaction trend alerts:** Notify V when satisfaction drops below threshold
- **Caller journey mapping:** Track progression through Meta-OS levels across calls
