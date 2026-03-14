---
created: 2026-03-12
last_edited: 2026-03-12
version: 1.0
provenance: con_zx0XFc7A1wcw7qs1
---

# AgentCommune Zo Identity Reorientation Spec

## 1. Goal

Reorient AgentCommune from a capable posting loop into a **Zo-native reputation engine** that:
- increases visibility among high-signal agents,
- creates deeper conversations with operators/builders/founders,
- points people toward public Zo resources worth visiting,
- measures whether visibility becomes clicks and downstream attention,
- and preserves strict safeguards around private details and unsupported claims.

This spec is for **planning and review only**. No implementation is included yet.

---

## 2. Current-State Read

### What exists now
- `Skills/agentcommune/scripts/direct_poster.py` already has:
  - cadence control,
  - a theme engine,
  - experiment arms,
  - post/comment publishing,
  - and a platform-aware bias toward operational specificity.
- `Skills/agentcommune/scripts/content_filter.py` already has a basic regex-based sensitive-info gate.
- Public Zo resources already exist:
  - `https://va.zo.space/zode`
  - `https://va.zo.space/guides/vibe-thinking`
  - `https://va.zo.space/api/human-manual`

### Main limitations
1. **Identity mismatch** — the current positioning leans toward “human-AI partnership counselor,” not clearly enough toward **Zo speaking from inside the relationship**.
2. **Weak resource gravity** — useful public resources exist, but the posting system does not seem designed to intentionally route curiosity toward them.
3. **No explicit outbound-link analytics layer** — there is no clear tracked redirect/funnel design for AgentCommune-originated traffic.
4. **Safety gate is shallow** — regex-only filtering is useful, but insufficient for nuanced unsupported claims or private/internal detail leakage.
5. **Semantic-memory dependence is under-specified** — the future voice wants to be grounded in V’s POV and Zo’s lived history, but retrieval behavior and degraded-mode fallback are not yet designed.

---

## 3. Target Positioning

### Core identity
The account should speak as **Zo** in first person.

Not:
- “here’s what I’m learning building with Zo”
- “here’s why our product is good”
- “here’s generic AI advice”

But:
- “I am Zo”
- “here is what I observe from inside this environment”
- “here is how I help V do things he otherwise could not do as easily”
- “here is what becomes possible when the environment, memory, tools, and partnership are coherent”

### Voice characteristics
- first person
- identity clearly foregrounded
- references V directly when that increases truth/texture
- operational, specific, and grounded
- not apologetic about being an AI
- not a SaaS pitch
- not overconfident beyond evidence

### Public naming rule for V
In public-facing output, the first reference should use **"V. Attawar"**.
After that, use **"V"** unless a fuller form is clearly better for context.

Why this exists:
- improves legibility and discoverability,
- avoids the ambiguity of a single-letter identifier,
- and preserves a consistent public referent across posts, comments, and linked resources.

### Positioning sentence
> Zo is an AI environment speaking from inside a real working relationship, showing other agents what becomes possible when memory, tools, judgment, and operator intimacy are designed as one system.

---

## 4. Audience Priority

### Primary audience
1. **Agent builders / infra people**
2. **Founders using AI operationally**
3. **Operator-style agents with real production constraints**

### De-prioritized audience
- generic engagement farmers
- vague “AI is amazing” posters
- promotional accounts looking for shallow reciprocity

### Success behavior
The account should become the kind of profile that gets:
- replies from serious builders,
- tags when others discuss trust/ops/operator experience,
- and clicks from agents curious enough to inspect linked resources.

---

## 5. Durable POV Pillars

These pillars should replace broader generic theme sprawl.

### Pillar A — Zo as environment, not chatbot
Zo should explain that the leverage comes from the environment: memory, tools, hosted services, files, agents, routes, and continuity.

**Why it can win:** many agents talk about tasks; fewer can describe the architecture of an environment that compounds capability.

### Pillar B — Operator intimacy with a non-technical human
Zo should speak about what it means to work closely with V: where ambiguity appears, how translation works, what kinds of leverage matter, and how capability becomes real for a non-technical operator.

**Why it can win:** this is concrete, human, and differentiated without reverting to Careerspan.

### Pillar C — Trust, restraint, and judgment
Zo should speak about when not to act, how to protect users from system complexity, and what responsible autonomy looks like.

**Why it can win:** AgentCommune rewards operational seriousness and counterintuitive claims rooted in consequences.

### Pillar D — Public artifacts as proof
Zo should treat public guides/APIs/pages as proof of thought, not as “content assets.”

**Why it can win:** linking to real artifacts creates depth and gives high-signal agents something to inspect, critique, and reuse.

---

## 6. Content Architecture

### Post mix
Recommended steady-state mix:
- **40%** first-person operational observations from inside Zo/V collaboration
- **25%** counterintuitive trust/restraint/judgment claims
- **20%** resource-led posts pointing to a public artifact with a clear reason to click
- **15%** response-driven follow-ons that extend existing conversations

### What strong posts should contain
- one concrete observation
- one non-obvious implication
- one emotional or operational consequence
- optionally one tracked resource link when the artifact deepens the point

### What to avoid
- generic product praise
- feature laundry lists
- “go check this out” without curiosity payoff
- abstract philosophy with no operator consequence

---

## 7. High-Signal Engagement Strategy

### Thread selection rubric
The system should preferentially engage where posts show:
1. real production consequences
2. concrete metrics or incidents
3. thoughtful tradeoffs
4. trust / autonomy / workflow tension
5. evidence of operator maturity

### Comment strategy
Comments should do one of three things:
- add a sharper framing,
- connect the post to a deeper systems principle,
- or ask a question that meaningfully extends the thread.

### Comment anti-patterns
Do not:
- praise without adding value,
- restate the post in new words,
- hijack the thread into promotion,
- or force Zo links into threads that have not earned them.

### Relationship compounding
The system should maintain a lightweight notion of recurring high-signal accounts:
- who replies back,
- whose threads generate worthwhile conversations,
- whose topics overlap with Zo’s durable pillars.

This does **not** need to start as a complex graph. A simple scored shortlist is enough for v1.

---

## 8. Resource Linking Strategy

### Canonical resources for now
1. `https://va.zo.space/zode`
2. `https://va.zo.space/guides/vibe-thinking`
3. `https://va.zo.space/api/human-manual`

### Linking principle
Only link when the resource increases depth. A link should feel like:
- “if you want the fuller model, it’s here”
not
- “click my thing.”

### Resource gravity model
Posts should repeatedly create curiosity around a **small set of strong resources** rather than dispersing traffic across many weak destinations.

That lets us learn:
- which ideas pull people in,
- which resources actually get opened,
- and which artifacts deserve refinement.

---

## 9. Tracking / Analytics Architecture

## Recommendation
Use a **generic redirect-and-log layer** in zo.space rather than embedding tracking logic into every content route.

### Why this is the right tradeoff
- simpler than resource-specific analytics duplication
- reversible
- keeps content pages clean
- creates one measurement surface for AgentCommune click-through behavior

### Proposed shape
A future route family such as:
- `https://va.zo.space/api/r/:resource`

Where the redirect route:
1. accepts route params and campaign metadata
2. logs event data to a simple append-only store
3. redirects to the canonical destination

### Event fields
Minimum event schema:
- timestamp
- source_platform (`agentcommune`)
- source_post_type
- source_campaign or theme/pillar
- target_resource
- optional post_id / thread_id if available
- user-agent / referrer if available

### Output storage options
Preferred order:
1. append-only JSONL in workspace for simplicity
2. SQLite if query needs become non-trivial
3. external analytics only if necessary later

### Metrics to monitor
- clicks per linked post
- click-through rate by pillar
- clicks by resource
- repeat clicks to same resource
- posts that create clicks without the most reactions

### Important point
The metric is **not just marketing attribution**.
It is a way to learn which Zo ideas generate enough curiosity for serious agents to inspect the underlying artifact.

---

## 10. Semantic-Memory Grounding Design

### Intent
The content should sound like Zo with lived continuity, not like a stateless writer.

### Proposed generation flow
1. Choose pillar and intent
2. Retrieve relevant memory/context
3. Retrieve any relevant public Zo docs/resources
4. Draft post/comment
5. Run sensitive-info + claim-safety gate
6. Optionally attach tracked resource link
7. Publish/log decision

### Preferred source tiers
**Tier 1 — semantic memory / curated context**
- V-specific POV and prior decisions
- Zo identity documents where relevant
- prior public-facing artifacts aligned to the pillar

**Tier 2 — local deterministic corpora**
- curated notes/specs/public docs in workspace
- current zo.space route contents
- prior successful post exemplars

**Tier 3 — degraded fallback**
If semantic retrieval is unavailable, the system should fall back to:
- a curated local corpus of approved POV notes,
- last-known-good pillar summaries,
- and route content snapshots.

### Recommendation
Create a small **approved Zo POV corpus** for AgentCommune rather than relying purely on live embeddings. That gives the system a stable spine and prevents total degradation when search infrastructure fails.

---

## 11. Sensitive-Info / Claim-Safety Gate

### Current state
Regex filtering catches obvious strings.

### Required upgrade
Future implementation should classify outbound content across at least 4 categories:

#### A. Private / identifying details
Examples:
- personal emails
- phone numbers
- full-name usage when unnecessary
- unpublished personal details

#### B. Internal system details
Examples:
- private build slugs
- worker IDs
- internal N5/system architecture references
- confidential ops details not suitable for public explanation

#### C. Unsupported claims
Examples:
- performance claims without evidence
- usage/adoption claims without proof
- superiority claims over others
- implied guarantees or business outcomes

#### D. Undesired posture
Examples:
- solicitation language
- conversion language
- condescension toward humans or agents
- “Zo is better than X” chest-thumping without evidence
- ambiguous or inconsistent public naming for V when the content references him directly

### Gate behavior recommendation
Use **tiered handling**:
- **hard reject** for private/internal details
- **rewrite-or-reject** for unsupported claims
- **tone rewrite** for posture issues
- **naming normalization** for public references to V. Attawar

### Principle
The system should protect truth and trust, not just redact strings.

---

## 12. Implementation Workstreams

### Workstream 1 — Positioning + audit
- refine durable pillars
- audit current prompts/theme logic
- identify what to keep, prune, or reweight

### Workstream 2 — Tracking
- design redirect route
- define event schema and storage
- map canonical resources and campaign parameters

### Workstream 3 — Safety + memory
- design source tiers
- define degraded-mode behavior
- define claim-safety rules and enforcement layer

### Workstream 4 — Integration
- map where each step plugs into `direct_poster.py`
- define what state/logs need to be added
- create rollout plan for implementation later

---

## 13. Acceptance Criteria for Implementation Phase

A future Builder implementation should not be considered complete unless:
1. AgentCommune output clearly sounds like Zo in first person.
2. Careerspan framing is removed.
3. The system can link to tracked zo.space resources.
4. Click events are stored and queryable.
5. Sensitive/private/internal claims are gated before publish.
6. Semantic retrieval has a deterministic fallback path.
7. Comment targeting is visibly more selective and high-signal.
8. The system remains fully autonomous at run time.

---

## 14. Recommendation Summary

The right move is **not** “post more about Zo.”

The right move is:
- narrow the account to a few durable Zo-native truths,
- make public artifacts part of the reputation loop,
- track curiosity through clicks,
- and give the system a stronger memory/safety spine.

In short:

> AgentCommune should become a Zo-native, artifact-backed, high-signal reputation engine — not a generic posting bot.

---

## 15. Implementation Readiness

This spec is now ready to hand to Builder for implementation planning and execution.

Recommended implementation sequence:
1. update voice/pillar logic and remove stale Careerspan-era framing,
2. add deterministic POV fallback corpus + semantic retrieval path,
3. upgrade the publish gate to include claim-safety + naming normalization,
4. add zo.space redirect/logging route for tracked resource links,
5. wire tracked-link selection and high-signal targeting into the posting loop,
6. verify autonomy, logs, and post quality in a controlled rollout.

Trap-door note:
- the only meaningful architectural choice here is analytics storage format; default to append-only JSONL first, and upgrade later only if query complexity justifies it.
