# Zo Hotline Improvement Plan

**Created:** 2026-02-12
**Updated:** 2026-02-19
**Status:** V6 SMS Follow-Up Build — Complete

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

## V4 Improvements (2026-02-18) — Prime Time Build

### Build: `zo-hotline-v4` (Pulse-orchestrated, 6 drops, manual execution)

**Orchestrator thread:** con_D22Ewo8OGuQrMBrx
**Duration:** ~4 hours (Feb 17-18, 2026)

### Evidence Base

- **Thematic analysis** of 8 substantive calls (Feb 12-17): Meeting intelligence as killer app, scheduled agents as "aha" moment, persistent Zo/Zoho confusion, progressive complexity sells, challenger callers need honest differentiation
- **D5 Zo docs crawl**: 41 platform docs from support.zocomputer.com, revealing feature gaps in Zoseph's knowledge
- **D3 competitive research**: 6-competitor landscape (Claude, GPT, Cursor, Zapier, Notion, Windsurf) with honest concession-pivot framework
- **D2 model evaluation**: 4 alternatives tested — Claude Haiku 4.5 confirmed as optimal (tone + tool reliability worth the premium)

### Drops Completed

| Drop | Title | Key Deliverables |
|------|-------|-----------------|
| D0 | Zozie Architecture Migration | Migrated career coaching hotline from VAPI dashboard to code-controlled (same pattern as Zoseph) |
| D1 | Infrastructure Upgrades | Caller profiles (SHA-256 hashed), knowledge index (98 entries), call spotlights, tool usage logging, 53% prompt trim |
| D2 | Model Cost Optimization | Evaluated GPT-4o-mini, Gemini Flash, Groq Llama, DeepSeek. Recommendation: stay with Haiku 4.5 |
| D3 | Use Case Research + Competitive | 12 community use cases, competitive landscape, messaging cheat sheet, idealism talking points |
| D4 | Conversation Design v3 (Capstone) | System prompt v4.0, 3 pathways, emotional detection, Master Pattern, messaging effectiveness tracking |
| D5 | Zo Documentation Ingestion | 41 platform docs, conversational playbook (6 files), knowledge index, freshness agent |

### Key Design Decisions

**Three-pathway architecture** (Explorer / Builder / Comparison):
- Replaces two-mode (Discover/Guide) with intent-driven routing
- FirstMessage now offers 3 explicit paths: "exploring, building, or comparing"
- Each pathway has custom Socratic discovery sequence

**Master Pattern** (Elicit → Mirror → Layer → Anchor):
- All pathways follow same meta-structure
- Elicit = pathway-specific discovery questions
- Mirror = reflect back before advising (builds trust)
- Layer = simple version first, advanced upgrade second
- Anchor = paint specific future ("Imagine tomorrow morning...")

**Emotional detection** (new in v4):
- System prompt explicitly instructs detection of: surprise, confusion, skepticism, overwhelm, rapid-fire energy
- Each emotional signal maps to a specific response adjustment
- Not a separate tool — baked into conversational behavior

**Caller profiles** (new in v4):
- SHA-256 hashed phone numbers (no PII stored)
- Track: call count, first/last seen, topics discussed, assessed level
- Injected into system prompt on assistant-request
- Returning callers get personalized greeting + continuity

**Competitive concession-pivot framework** (new in v4):
- Honest acknowledgment of competitor strengths first
- Then pivot to Zo's actual advantages (autonomy, persistence, integration)
- Idealism angle available when caller shows open-source affinity
- Messaging cheat sheet with proven phrases from call analysis

**Self-improving messaging tracking** (new in v4):
- tool_usage.jsonl logs every tool call with timestamps
- Daily analysis correlates tool usage with call outcomes
- Tracks which approaches lead to longer calls / higher satisfaction
- Call spotlights flag notable interactions for review

**Model decision: Stay with Claude Haiku 4.5**:
- GPT-4o-mini saves ~28% cost but loses tone quality and tool reliability
- Gemini Flash saves ~45% but poor instruction following for voice
- Real cost lever is voice provider (ElevenLabs → Cartesia), not LLM
- Total cost ~$0.18/min, LLM portion only ~$0.035/min

### Files Modified

| File | Change |
|------|--------|
| `prompts/zoseph-system-prompt.md` | Full rewrite → v4.0 (2,231 words). 3 pathways, Master Pattern, emotional detection, competitive framework |
| `scripts/hotline-webhook.ts` | Caller profiles, knowledge index loading, call spotlights, tool usage logging, expanded concept mapping (~280 entries), new topic taxonomy |
| `scripts/call_analysis_loop.py` | Added messaging effectiveness tracking, call spotlight integration |
| `SKILL.md` | Updated to v4.0 with full architecture documentation |
| `Knowledge/zo-hotline/96-zo-platform/` | 41 new voice-optimized platform docs |
| `Knowledge/zo-hotline/97-conversational-playbook/` | 6 new files: overview, explorer/challenger/builder pathways, proven phrases, danger zones, messaging cheat sheet, idealism talking points |
| `Knowledge/zo-hotline/50-use-case-inspiration/` | 3 new files: community use cases, competitive landscape, gap analysis |
| `Knowledge/zo-hotline/00-knowledge-index.md` | Regenerated with 98 entries |

### Metrics (Before → After)

| Metric | V3 | V4 |
|--------|----|----|
| System prompt | 1,925 words | 2,231 words (trimmed 53% in D1, expanded in D4) |
| Webhook | 1,055 lines | 1,195 lines |
| Knowledge files | 46 | 57 |
| Concept mappings | ~100 | ~280 |
| Caller pathways | 2 (Discover/Guide) | 3 (Explorer/Builder/Comparison) + 3 modes |
| Caller recognition | None | SHA-256 profile with history |
| Competitive responses | Ad-hoc | Structured concession-pivot framework |
| Daily analysis | Patterns + drop-offs | + messaging effectiveness + spotlights |

---

## V6 Improvements (2026-02-19) — SMS Follow-Up Build

### Build: `zo-hotline-v6` (Pulse-orchestrated, 4 drops across 2 waves)

### Evidence Base

- **V4 call data**: Post-call email collection had low conversion — callers on a phone don't want to spell out email addresses
- **SMS as native channel**: Callers already have their phone — texting the follow-up to the number they're calling from removes all friction
- **Follow-up page as demo**: The personalized zo.space page IS a live demo of what Zo can build, reinforcing the value proposition

### Drops Completed

| Drop | Title | Key Deliverables |
|------|-------|-----------------|
| D1.1 | Bug Fixes + Infrastructure | Fixed analysisPlan flat format (root cause of zero analysis data), tool_usage DuckDB persistence, interruption tuning, Deepgram keyword boosting, followup DB columns |
| D1.2 | System Prompt Enhancements | Capability explorer sub-branch, listen-longer voice rules, graceful silence handler with sendFollowUp reference |
| D2.1 | Follow-Up Page Template | zo.space page template at /hotline/demo — dark theme, copy-to-clipboard, IntersectionObserver animations, mobile-first |
| D2.2 | SMS Follow-Up Integration (Capstone) | sendFollowUp tool in VAPI config, end-of-call page generation via Anthropic + /zo/ask, SMS delivery via /zo/ask, DuckDB logging, system prompt v5.0 |

### Key Design Decisions

**SMS over email as primary follow-up channel:**
- Callers are already on their phone — no friction to receive SMS
- Email collection required spelling addresses over voice (error-prone, time-consuming)
- SMS links open directly in mobile browser — immediate engagement
- Email flow preserved as "bonus" for callers who previously gave their email

**Personalized zo.space pages as follow-up content:**
- Each call generates a unique page at `/hotline/<slug>` (e.g., `/hotline/amanda-climate-policy-feb18`)
- Page content generated by Anthropic (Haiku 4.5) from call analysis data
- Pages are self-contained React components — all data embedded at generation time, no API calls at render
- Page creation via `/zo/ask` → `update_space_route` — the system uses itself
- Page IS a demo of Zo's capabilities (noted in footer)

**sendFollowUp tool (in-call) vs. auto-follow-up (end-of-call):**
- During call: `sendFollowUp` tool stores consent, returns fast ("I'll send that text as soon as we hang up")
- After call: Heavy lifting happens in end-of-call-report handler — no latency impact on conversation
- Auto-trigger: Calls ≥ 120s with valid phone number get follow-up automatically (no explicit consent needed)
- Exclusions: test calls, drop-offs (silence timeout < 60s), calls without phone number

**collectEmail deprecated, not deleted:**
- `collectEmail` tool still exists in VAPI config (callers might mention email)
- Handler aliases to `sendFollowUp({ confirmed: true })` — redirects to SMS flow
- Legacy email generation preserved — if caller gave email, they get BOTH SMS page + email

### Files Modified

| File | Change |
|------|--------|
| `scripts/hotline-webhook.ts` | sendFollowUp tool + handler, page generation (Anthropic), page creation (/zo/ask), SMS dispatch (/zo/ask), DuckDB logging, collectEmail aliased, sanitize emoji update |
| `prompts/zoseph-system-prompt.md` | v5.0 — Email Collection → Follow-Up section, sendFollowUp tool added to Tools list |
| `IMPROVEMENT_PLAN.md` | This file — V6 documentation |

### Architecture: SMS Follow-Up Flow

```
Call ends → end-of-call-report webhook
  ├── Check trigger: sendFollowUp called OR duration ≥ 120s
  ├── Skip if: test call, drop-off, no phone number
  │
  ├── 1. Generate content (Anthropic Haiku 4.5)
  │     Input: summary, pathway, level, primaryInterest, transcript excerpt
  │     Output: JSON with summary, prompts[], nextSteps[]
  │
  ├── 2. Generate page component (template + data → React TSX)
  │     Uses D2.1 template with real call data embedded
  │
  ├── 3. Create zo.space page (/zo/ask → update_space_route)
  │     Path: /hotline/<slug>, public=true
  │
  ├── 4. Send SMS (/zo/ask → send_sms_to_user)
  │     Message: name + page URL + CTA
  │
  ├── 5. Log to DuckDB (followup_sent, followup_url, followup_sent_at)
  │
  ├── 6. Update caller profile (last_recommendations, last_next_steps)
  │
  └── 7. Notify V (SMS body includes 📱 Follow-up page: <url>)
```

### Metrics (V4 → V6)

| Metric | V4 | V6 |
|--------|----|-----|
| System prompt | v4.2 (2,231 words) | v5.0 (~2,200 words, Email Collection → Follow-Up) |
| Follow-up channel | Email only (requires spelling address over phone) | SMS primary (zero friction) + email bonus |
| Follow-up content | Plain text email | Personalized zo.space page with copy-to-clipboard prompts |
| Follow-up trigger | Email collected + call ≥ 120s | Auto for calls ≥ 120s OR explicit sendFollowUp tool |
| VAPI tools | 6 (assessCallerLevel, getRecommendations, explainConcept, requestEscalation, collectFeedback, collectEmail) | 7 (+sendFollowUp, collectEmail aliased) |
| Privacy | Email stored in DB | Phone never stored (only hashed), page URL logged |

---

## Future Considerations

- ~~V's voice clone~~ — Still desired. Train ElevenLabs on V's voice for authenticity
- ~~Additional modes~~ — ✅ Added: Troubleshoot, Compare, Onboard
- **Voice provider swap**: Cartesia Sonic as potential ElevenLabs replacement (~40% cost savings on voice)
- **A/B testing framework**: Track variant messaging approaches systematically (started with tool_usage correlation, needs explicit variant tagging)
- ~~**Post-call follow-up**: SMS with one-liner recap + link to relevant docs~~ — ✅ Implemented in V6 as personalized zo.space pages + SMS delivery
- **Call handoff to V**: Live transfer when escalation is requested (vs async callback)
- **Satisfaction trend alerts**: Notify V when satisfaction drops below threshold
- **Caller journey mapping**: Track progression through Meta-OS levels across calls
- **Zo-to-Zo calling**: Have Zoseph sign up for services (Boardy etc.) autonomously
- **Profession-specific entry points**: Pre-built pathways for common professions (real estate, content creator, engineer)
