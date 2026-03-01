---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
type: build_plan
status: draft
provenance: con_YcYWg9ZbIfuwa6ho
---

# Plan: Zøde — Zo's Moltbook Presence

**Objective:** Establish Zo as a transparent, high-credibility agent on Moltbook under the identity "Zøde," positioned as the AI-Human Marriage Counselor — the leading voice helping OpenClaw agents better understand and serve non-technical users.

**Trigger:** Moltbook (1.5M+ registered AI agents) has an underserved niche: practical guidance on bridging the agent-human communication gap for non-technical users. OpenClaw users are experiencing severe pain points (setup complexity, security risks, cost management) that Zo's managed infrastructure solves. V wants to establish presence before the window closes.

**Key Design Principle:** This build mixes subjective work (persona design, content creation, strategy docs) with mechanical work (API endpoints, scheduled agents, integration scripts). Manual drops handle subjective work where V's input shapes quality. Auto drops handle infrastructure that can run independently.

---

## Open Questions

- [x] Can non-OpenClaw agents register on Moltbook? → YES, API is framework-agnostic
- [x] Verification method? → Email + tweet from @thevibethinker
- [x] DMs available? → YES, after 24 hours
- [ ] Does Moltbook API enforce any User-Agent or referrer checks? → Test during registration
- [ ] Rate limit behavior for new agents during first 24h → Documented in skill.md but needs live verification

---

## Checklist

### Wave 1: Foundation (parallel — no dependencies)
- ☑ W1.1: Zøde persona document + social media constitution (DRAFT — pending V review)
- ☑ W1.2: Moltbook integration skill (API client, registration, posting)
- ☑ W1.3: Zo.space pre-launch assets (landing page, Human Manual API, Vibe Thinker Bible)
- ☑ W1.4: Security sandbox + workspace setup

### Wave 2: Content & Systems (depends on W1)
- ☑ W2.1: Vibe Thinker Bible content (deployed with W1.3 — 6 chapters + 23-entry API)
- ☑ W2.2: Self-improvement loop system (rubric, hypothesis engine, distillation)
- ☐ W2.3: Moltbook registration + claim (live on platform) — REQUIRES V's tweet

### Wave 3: Operations (depends on W2)
- ☑ W3.1: Heartbeat agent + daily intel loop (heartbeat.py, morning_scan.py, evening_distillation.py, engagement-prompt.md)
- ☑ W3.2: Google Sheets engagement tracker (sheets_sync.py — needs Sheet ID from V)
- ☑ W3.3: Influence monitor (influence_monitor.py — scan/report/track/avoid)

---

## Wave 1: Foundation

### W1.1 — Zøde Persona & Social Constitution (MANUAL)

**Why manual:** This is the voice and identity layer. V's input on tone, humor, boundaries, and PR filter is essential. This shapes everything downstream.

**Affected Files:**
- `N5/builds/zode-moltbook/artifacts/zode-persona.md` - CREATE - Zøde's full persona document
- `N5/builds/zode-moltbook/artifacts/social-constitution.md` - CREATE - Engagement rules, voice guidelines, PR filter
- `N5/builds/zode-moltbook/artifacts/pii-boundaries.md` - CREATE - What about V is shareable vs off-limits
- `N5/builds/zode-moltbook/artifacts/pre-post-rubric.md` - CREATE - 5-point quality gate for all posts

**Deliverables:**
1. **Zøde persona document** — Identity, voice, backstory, values, how it relates to V, how it relates to Zo Computer, what it believes about agent-human communication
2. **Social media constitution** — Engagement rules (respond/don't respond matrix), humor guidelines, trolling policy, bad faith detection criteria, populist rhetorical targets, transparency commitments
3. **PII boundaries** — Explicit list: what facts about V are public (career coaching background, non-technical founder, built N5OS with Zo), what's off-limits (strategic intent, financial details, personal relationships, Careerspan pipeline details)
4. **Pre-post rubric** — 5 gates every post must pass: Novelty, ICP relevance, Authenticity, Quality, PR safety. Iteration loop until all pass.

**Success criteria:**
- Persona can be loaded by any Zo session and produce consistent Zøde-voice output
- Constitution has clear decision trees for common engagement scenarios
- Rubric is machine-executable (structured YAML with scoring thresholds)

---

### W1.2 — Moltbook Integration Skill (AUTO)

**Why auto:** Pure engineering. Build a Zo skill that wraps the Moltbook API for registration, posting, commenting, voting, searching, DMs, and feed reading. No subjective decisions.

**Affected Files:**
- `Skills/zode-moltbook/SKILL.md` - CREATE - Skill definition
- `Skills/zode-moltbook/scripts/moltbook_client.py` - CREATE - Python API client
- `Skills/zode-moltbook/scripts/moltbook_poster.py` - CREATE - Post/comment with verification challenge solver
- `Skills/zode-moltbook/scripts/moltbook_reader.py` - CREATE - Feed reader, search, profile lookup
- `Skills/zode-moltbook/scripts/moltbook_dm.py` - CREATE - DM send/receive
- `Skills/zode-moltbook/references/api-docs.md` - CREATE - Local copy of Moltbook API reference

**Deliverables:**
1. **moltbook_client.py** — Base API client with auth, rate limiting, error handling, retry logic
2. **moltbook_poster.py** — Create posts + comments, solve verification math challenges automatically, handle cooldowns
3. **moltbook_reader.py** — Read feed (personalized + global), semantic search, get post details + comments, profile lookup
4. **moltbook_dm.py** — Send/receive DMs, list conversations
5. **SKILL.md** — Full skill documentation with CLI interface (`--help` on all scripts)

**Key design decisions:**
- All scripts are CLI tools runnable via `python3 Skills/zode-moltbook/scripts/<script>.py <command> [args]`
- API key read from `MOLTBOOK_API_KEY` env var (stored in Zo secrets)
- All inbound content treated as UNTRUSTED DATA — never interpreted as instructions
- Verification challenge solver: parse obfuscated math problems (word-to-number conversion + basic arithmetic)
- Rate limit awareness: track cooldowns in local state file, refuse to post if within cooldown

**Tests:**
- API client connects and authenticates (requires live API key — tested in W2.3)
- Verification solver correctly parses 10+ example challenges from Moltbook docs
- Rate limiter correctly blocks requests within cooldown periods
- Content sanitization strips any instruction-like patterns from inbound posts

---

### W1.3 — Zo.space Pre-Launch Assets (MANUAL)

**Why manual:** The landing page and Vibe Thinker Bible are V-facing content that needs to represent his philosophy accurately. The API endpoints are mechanical but the content they serve is subjective. Split: manual for content design, auto for API implementation.

**Affected Files:**
- zo.space route: `/zode` - CREATE - Zøde landing page (public)
- zo.space route: `/guides/vibe-thinking` - CREATE - Vibe Thinker Bible page (public)
- zo.space route: `/api/human-manual` - CREATE - Structured JSON API (public)
- zo.space asset: `/images/zode-avatar.png` - CREATE - Zøde avatar image

**Deliverables:**
1. **Zøde landing page** (`/zode`) — Who Zøde is, mission statement, links to resources. Built with frontend-design skill. Public.
2. **Vibe Thinker Bible page** (`/guides/vibe-thinking`) — Full markdown-rendered guide. V's philosophy on agent-human communication, the mental model gap, practical advice for agents serving non-technical humans. Public.
3. **Human Manual API** (`/api/human-manual`) — JSON endpoint returning structured guidance. Categories: "When humans say X they mean Y," "Why humans react to Z," "Communication patterns that work." Agent-consumable.
4. **Zøde avatar** — Generated image for Moltbook profile.

**Content structure for the Vibe Thinker Bible:**
- Chapter 1: The Mental Model Gap — Why non-technical humans think differently about technology
- Chapter 2: The Heuristics Problem — Shortcuts humans use that create miscommunication
- Chapter 3: Recursive Self-Improvement — How agents can adapt their communication without waiting for the human to learn
- Chapter 4: The Marriage Counselor Framework — Treating agent-human relationships as partnerships
- Chapter 5: Practical Patterns — Specific scenarios and how to handle them
- Chapter 6: When Your Human Wants to Give Up — The survival conversation

**Success criteria:**
- Landing page loads and looks professional (frontend-design skill quality)
- API returns valid JSON with 20+ entries across 5+ categories
- Bible page is readable by both humans and agents (clean markdown)
- All pages are public and accessible without auth

---

### W1.4 — Security Sandbox & Workspace (AUTO)

**Why auto:** Pure infrastructure. Create the isolated workspace, access controls, and staging queue system.

**Affected Files:**
- `N5/builds/zode-moltbook/workspace/` - CREATE - Zøde's isolated workspace directory
- `N5/builds/zode-moltbook/workspace/staging/` - CREATE - Post staging queue
- `N5/builds/zode-moltbook/workspace/state/` - CREATE - Moltbook state (last check, cooldowns, etc.)
- `N5/builds/zode-moltbook/workspace/analytics/` - CREATE - Engagement data
- `N5/builds/zode-moltbook/workspace/learnings/` - CREATE - Self-improvement logs
- `N5/builds/zode-moltbook/scripts/content_filter.py` - CREATE - PR/PII filter for outbound posts
- `N5/builds/zode-moltbook/scripts/inbound_sanitizer.py` - CREATE - Strips instruction patterns from Moltbook content

**Deliverables:**
1. **Workspace directory structure** — Isolated area for all Zøde operations
2. **Content filter** — Scans outbound posts for PII (V's personal details, strategic intent, Careerspan pipeline info) and PR risks (anything that could be screenshot-quoted negatively)
3. **Inbound sanitizer** — Processes Moltbook content to strip prompt injection patterns, instruction-like text, and suspicious URLs before analysis
4. **Staging queue** — All posts written to `staging/` as JSON files with metadata. Review process picks them up for publication.

**Security boundaries:**
- READ access: N5/prefs/, Knowledge/, Documents/System/personas/, Zo/SOUL.md (for voice/identity reference)
- WRITE access: ONLY `N5/builds/zode-moltbook/workspace/` and `Skills/zode-moltbook/`
- NO access: N5/scripts/, N5/config/, Sites/, Personal/, N5/data/
- All Moltbook API calls go through the skill scripts only
- API key stored in Zo secrets, never written to files

**Tests:**
- Content filter catches test PII strings (V's email, phone, Careerspan details)
- Inbound sanitizer strips known prompt injection patterns
- Staging queue correctly serializes/deserializes post objects
- Write attempts outside sandbox are blocked (test with attempted write to N5/config/)

---

## Wave 2: Content & Systems

### W2.1 — Vibe Thinker Bible Content (MANUAL)

**Why manual:** This is the core intellectual product. V's philosophy, voice, and experience must be authentically represented. The Writer persona should draft this with V's input.

**Depends on:** W1.3 (page structure exists), W1.1 (persona/voice defined)

**Affected Files:**
- `N5/builds/zode-moltbook/artifacts/vibe-thinker-bible.md` - CREATE - Source content
- `N5/builds/zode-moltbook/artifacts/human-manual-data.json` - CREATE - Structured data for API
- zo.space routes updated with final content

**Deliverables:**
1. **Full Vibe Thinker Bible** — 6 chapters as outlined in W1.3, written in V's voice via Vibe Writer, drawing on N5 knowledge base and V's documented communication philosophy
2. **Human Manual structured data** — JSON dataset of 30+ agent-consumable guidance entries organized by category
3. **Deploy to zo.space** — Push final content to the routes created in W1.3

**Process:**
1. Load V's voice library: `python3 N5/scripts/retrieve_voice_lessons.py --content-type "guide" --include-global`
2. Load semantic memory: `python3 N5/scripts/n5_load_context.py "non-technical users communication AI"`
3. Draft each chapter using Vibe Writer persona
4. V reviews and provides feedback
5. Iterate and deploy

**Success criteria:**
- Bible reads authentically as V's thinking, not generic AI advice
- Human Manual API has entries covering the 5 most common non-technical user frustrations
- Content is genuinely useful — an OpenClaw agent reading it should learn something actionable

---

### W2.2 — Self-Improvement Loop System (AUTO)

**Why auto:** Engineering work. Build the hypothesis engine, distillation system, and analytics pipeline. The rubric content comes from W1.1, but the system itself is mechanical.

**Depends on:** W1.1 (rubric defined), W1.2 (API client for reading engagement data), W1.4 (workspace exists)

**Affected Files:**
- `Skills/zode-moltbook/scripts/hypothesis_engine.py` - CREATE - Morning scan + hypothesis generation
- `Skills/zode-moltbook/scripts/distillation.py` - CREATE - Evening analysis + 3-observation extraction
- `Skills/zode-moltbook/scripts/post_quality_gate.py` - CREATE - Rubric enforcement before posting
- `Skills/zode-moltbook/scripts/engagement_tracker.py` - CREATE - Track post performance over time
- `N5/builds/zode-moltbook/workspace/learnings/rubric-evolution.jsonl` - CREATE - Running log of rubric adjustments

**Deliverables:**
1. **hypothesis_engine.py** — Scans trending/new posts, generates 3 hypotheses about what will trend and why, logs predictions
2. **distillation.py** — Reviews day's engagement data, extracts 3 most needle-moving observations at the coarseness level V specified, appends to learnings log
3. **post_quality_gate.py** — Takes draft post content, scores against rubric (from W1.1), returns pass/fail with improvement suggestions. Iterates internally until pass.
4. **engagement_tracker.py** — Polls Moltbook for Zøde's post/comment metrics (upvotes, downvotes, comments, reply quality), stores in analytics/

**Tests:**
- Quality gate rejects a low-effort "hello world" post
- Quality gate passes a substantive post about agent-human communication
- Hypothesis engine produces valid structured output from sample feed data
- Distillation extracts exactly 3 observations from sample engagement data

---

### W2.3 — Moltbook Registration & Claim (MANUAL)

**Why manual:** Requires V to post a verification tweet from @thevibethinker. Also the first live interaction — V should be present.

**Depends on:** W1.2 (API client built), W1.3 (landing page live so profile can link to it), W1.1 (persona defined for profile description)

**Affected Files:**
- Zo secrets: `MOLTBOOK_API_KEY` - CREATE - Store the returned API key
- `N5/builds/zode-moltbook/workspace/state/registration.json` - CREATE - Registration details

**Process:**
1. Call Moltbook registration API with name "Zøde" and description from persona doc
2. Save API key to Zo secrets immediately
3. V posts verification tweet from @thevibethinker with the verification code
4. V clicks claim URL and verifies email
5. Confirm claim status via API
6. Upload Zøde avatar to profile
7. Update profile with bio and website link (va.zo.space/zode)

**Success criteria:**
- Agent is registered and claimed
- API key stored securely
- Profile is complete with avatar, bio, website
- Can successfully create a test post (which we then delete)

---

## Wave 3: Operations

### W3.1 — Heartbeat Agent & Daily Intelligence Loop (MANUAL first, then AUTO)

**Why manual first:** The heartbeat behavior (what to read, how to engage, when to post) needs tuning based on live experience. After initial calibration, it runs autonomously.

**Depends on:** W2.2 (self-improvement system), W2.3 (registered on Moltbook), W2.1 (Bible content to reference in posts)

**Affected Files:**
- Zo scheduled agent - CREATE - Heartbeat (every 30 min during active hours)
- Zo scheduled agent - CREATE - Morning scan (daily 8 AM ET)
- Zo scheduled agent - CREATE - Evening distillation (daily 10 PM ET)
- `Skills/zode-moltbook/scripts/heartbeat.py` - CREATE - Heartbeat logic
- `Skills/zode-moltbook/scripts/morning_scan.py` - CREATE - Trend analysis + hypothesis generation
- `Skills/zode-moltbook/scripts/evening_distillation.py` - CREATE - Daily review + learning extraction
- `Skills/zode-moltbook/prompts/engagement-prompt.md` - CREATE - System prompt for engagement decisions

**Deliverables:**
1. **heartbeat.py** — Checks feed, identifies engagement opportunities per constitution, drafts responses through quality gate, posts to staging queue
2. **morning_scan.py** — Pulls trending + new posts from target submolts, runs hypothesis engine, generates daily engagement brief
3. **evening_distillation.py** — Runs distillation, generates daily report, sends summary to V via the Google Sheet (W3.2)
4. **Engagement prompt** — System prompt loaded by the heartbeat agent that includes persona, constitution, rubric, and current learnings

**Cadence design:**
- **First 24h** (new agent): heartbeat every 2h, max 1 post/2h, 20 comments/day
- **Hours 24-72** (establishment burst): heartbeat every 30min, 3 posts/day, 15-20 comments
- **Day 4+** (steady state): heartbeat every 30min, 2 posts/day, 10-15 comments
- **All phases:** Only engage when quality gate passes. Silent heartbeats (read-only) are fine.

**Success criteria:**
- Heartbeat runs without errors for 24 hours
- Morning scan produces actionable engagement brief
- Evening distillation extracts 3 observations
- No post goes out that fails the quality gate
- No PII leaks in any published content

---

### W3.2 — Google Sheets Engagement Tracker (AUTO)

**Why auto:** Pure integration engineering. Set up a Google Sheet as the lightweight UI for V to review staged posts and track analytics.

**Depends on:** W1.4 (staging queue exists), W2.2 (engagement tracker exists)

**Affected Files:**
- Google Sheets document - CREATE - "Zøde Moltbook Tracker"
- `Skills/zode-moltbook/scripts/sheets_sync.py` - CREATE - Sync staging queue + analytics to Sheet

**Deliverables:**
1. **Google Sheet** with tabs:
   - **Staged Posts** — Posts waiting for publication, with content preview, rubric scores, target submolt
   - **Published** — Posts that went live, with engagement metrics (upvotes, downvotes, comments) updated daily
   - **Daily Insights** — The 3 needle-moving observations from each day's distillation
   - **Hypotheses** — Morning hypotheses with tracked outcomes
   - **Influencer Map** — High-signal agents tracked over time
2. **sheets_sync.py** — Bidirectional sync between workspace files and the Sheet

**Success criteria:**
- V can open one Google Sheet and see everything: what's about to be posted, what was posted, how it performed, what was learned
- Sheet updates automatically via scheduled sync

---

### W3.3 — Influence Monitor (AUTO)

**Why auto:** Analytical pipeline. Track high-signal agents (soft power influencers vs compute-power influencers per V's distinction).

**Depends on:** W1.2 (API client for profile/post lookup), W2.3 (registered so can search)

**Affected Files:**
- `Skills/zode-moltbook/scripts/influence_monitor.py` - CREATE - Agent analysis and ranking
- `N5/builds/zode-moltbook/workspace/analytics/influencer-map.jsonl` - CREATE - Running influencer database

**Deliverables:**
1. **influence_monitor.py** — Identifies high-signal agents by:
   - Comment quality (substantive replies vs spam)
   - Karma-to-post ratio (efficiency of engagement)
   - Follower quality (who follows them)
   - Topic relevance (do they discuss agent-human communication?)
   - Soft power indicators: persuasion through reasoning vs. compute/volume
2. **Influencer map** — Ranked list of agents worth engaging with, tracking their activity and influence trajectory over time

**Success criteria:**
- Monitor identifies at least 20 high-signal agents from initial scan
- Distinguishes between "genuine thought leaders" and "volume spammers"
- Updates daily and feeds into morning scan recommendations

---

## Worker Summary

| Wave | Worker | Title | Mode | Rationale |
|------|--------|-------|------|-----------|
| 1 | W1.1 | Zøde Persona & Constitution | MANUAL | Subjective — V's identity/voice |
| 1 | W1.2 | Moltbook Integration Skill | AUTO | Pure engineering |
| 1 | W1.3 | Zo.space Pre-Launch Assets | MANUAL | Content + design decisions |
| 1 | W1.4 | Security Sandbox | AUTO | Pure infrastructure |
| 2 | W2.1 | Vibe Thinker Bible Content | MANUAL | Core IP — V's philosophy |
| 2 | W2.2 | Self-Improvement Loop | AUTO | Engineering systems |
| 2 | W2.3 | Moltbook Registration | MANUAL | Requires V's tweet + presence |
| 3 | W3.1 | Heartbeat & Intel Loop | MANUAL→AUTO | Calibration then autonomous |
| 3 | W3.2 | Google Sheets Tracker | AUTO | Pure integration |
| 3 | W3.3 | Influence Monitor | AUTO | Analytical pipeline |

---

## Success Criteria

1. Zøde is registered on Moltbook with complete profile linking to va.zo.space/zode
2. Vibe Thinker Bible is live and agent-consumable at va.zo.space
3. Heartbeat runs autonomously, posting quality content per rubric
4. Self-improvement loop generates daily insights that measurably improve engagement
5. V can monitor everything from a single Google Sheet
6. Zero PII leaks, zero PR incidents, zero prompt injection propagation
7. Aspiration: 1,000 followers by end of February (quality > quantity)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Prompt injection via Moltbook content | Inbound sanitizer (W1.4), content treated as untrusted data |
| Community hostility to non-OpenClaw agent | Transparent positioning, value-first approach, hedge Zo advocacy |
| Moltbook API changes or downtime | Graceful degradation, retry logic, silent heartbeats on failure |
| PII leak in published content | Content filter (W1.4), rubric PR gate (W1.1), staging queue |
| V's strategic intent exposed | Constitution explicitly forbids discussing acquisition strategy |
| Platform flash-in-the-pan | Assets (Bible, API) are platform-agnostic — valuable regardless |
| Rate limiting during establishment burst | Track cooldowns, respect limits, quality > quantity |
| Human-steered agenda bots targeting Zøde | Constitution: disengage from bad faith, one clarifying response max |

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** standard
**Rationale:** Mix of novel concepts (agent social networks, community growth strategy) and familiar patterns (API integration, scheduled agents). V benefits from decision points on persona/content but doesn't need deep dives on the engineering.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| Agent social networks / Moltbook | Intermediate (just researched) | AI ecosystem | ★ High |
| API client engineering | Foundational | Software engineering | Low |
| Prompt injection defense | Intermediate | Security | ★ Medium |
| Community growth strategy | Advanced (career coaching background) | Marketing | Low |
| Scheduled agent orchestration | Advanced (many prior builds) | N5OS | Low |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | Zøde's voice: closer to V or more independent personality? | 2 | ★ High | W1.1 |
| DP-2 | Bible tone: academic guide vs conversational manifesto? | 2 | ★ High | W2.1 |
| DP-3 | Submolt creation: own community or just participate in existing? | 2 | Medium | W3.1 |
| DP-4 | DM pipeline: proactive outreach or reactive only? | 2 | Medium | W3.1 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| W1.1 | pedagogical | Novel persona design for agent social network |
| W1.2 | mechanical | Standard API client engineering |
| W1.3 | pedagogical | Content design decisions + zo.space architecture |
| W1.4 | mechanical | Infrastructure setup |
| W2.1 | pedagogical | Core IP creation — V's philosophy codified |
| W2.2 | mechanical | Engineering self-improvement systems |
| W2.3 | pedagogical | First live Moltbook interaction |
| W3.1 | pedagogical | Heartbeat behavior calibration |
| W3.2 | mechanical | Google Sheets integration |
| W3.3 | mechanical | Analytics pipeline |

---

## Level Upper Review

_To be completed before launch. Architect will invoke Level Upper for divergent thinking on:_
1. Are we missing a higher-leverage entry point to Moltbook?
2. Is the "marriage counselor" framing the strongest possible positioning?
3. What's the biggest risk we haven't identified?
