---
created: 2026-03-12
last_edited: 2026-03-12
version: 1
type: build_plan
status: draft
provenance: con_zx0XFc7A1wcw7qs1
---
# Plan: AgentCommune Zo Identity Reorientation

**Objective:** Produce a reviewable plan and execution spec to reorient AgentCommune around Zo’s first-person identity, higher-signal visibility, deeper conversations with strong agents, Zo resource linking, outbound click tracking, and stronger semantic-memory + sensitive-info safeguards.

**Explicit public naming requirement:** in public-facing output, first reference V as **"V. Attawar"**, then use **"V"** afterward unless context calls for the fuller form.

**Trigger:** V wants AgentCommune reoriented away from Careerspan and toward Zo itself: Zo speaking in first person, referencing V directly, linking to supporting `va.zo.space` resources, and measuring whether platform visibility creates real clicks and downstream attention.

**Key Design Principle:** Keep the future implementation simple, not merely easy. Separate concerns cleanly: identity/voice, engagement selection, link instrumentation, and safety/memory should remain distinct systems with explicit handoffs.

---

## Open Questions

- [ ] How strong should the “Zo is awesome” stance be before it reads as promotion rather than lived operational testimony?
- [ ] Which existing `va.zo.space` pages should be canonical outbound destinations versus deprecated/low-priority resources?
- [ ] Should click tracking live in a single generic redirect route for all AgentCommune links, or in resource-specific routes with shared analytics storage?
- [ ] What semantic-memory retrieval fallback should be used when embeddings/search infrastructure is degraded?

---

## Checklist

### Phase 1: Audit current surface and define target positioning
- ☐ Audit current AgentCommune posting system, platform fit, and zo.space resource surface
- ☐ Define Zo-native POV pillars, off-limits claims, and audience hierarchy
- ☐ Test: plan/spec can cite real files, real routes, and current gaps without placeholders

### Phase 2: Write execution spec
- ☐ Define content architecture, high-signal engagement strategy, and semantic-memory retrieval design
- ☐ Define sensitive-info gate, link instrumentation model, and success metrics
- ☐ Test: spec gives Builder enough detail to implement without reopening core strategy

### Phase 3: Prepare Pulse execution package
- ☐ Create MECE worker briefs for later implementation build
- ☐ Validate worker coverage and dependencies
- ☐ Test: `python3 N5/scripts/mece_validator.py agentcommune-zo-reorientation` passes

---

## Phase 1: Audit current surface and define target positioning

### Affected Files
- `N5/builds/agentcommune-zo-reorientation/PLAN.md` - UPDATE - build plan
- `N5/builds/agentcommune-zo-reorientation/SPEC.md` - CREATE - implementation-grade strategy/spec
- `Skills/agentcommune/scripts/direct_poster.py` - READ ONLY - current posting architecture
- `Skills/agentcommune/scripts/content_filter.py` - READ ONLY - current sensitive-info gate
- `Skills/agentcommune/references/platform-analysis.md` - READ ONLY - existing platform observations
- zo.space route `https://va.zo.space/zode` - READ ONLY - current landing page
- zo.space route `https://va.zo.space/guides/vibe-thinking` - READ ONLY - current longform guide
- zo.space route `https://va.zo.space/api/human-manual` - READ ONLY - current structured resource API

### Changes

**1.1 Audit the current AgentCommune system:**
Read the current posting and filtering flow to identify where identity, topic selection, safety checks, commenting logic, and outbound linking would attach. Capture current constraints from real code: cadence, theme engine, comment behavior, current anti-CTA stance, and existing content-filter patterns.

**1.2 Reframe the account around Zo’s identity:**
Define the target voice as Zo speaking in first person from inside the V ↔ Zo working relationship, with V directly referenced when useful and without Careerspan framing. Distinguish this from “founder using Zo” and from generic product marketing.

**1.3 Establish the resource/link surface:**
Review existing zo.space artifacts and decide which should become deliberate visibility sinks from AgentCommune. Identify the current blind spot: public resources exist, but there is no explicit outbound tracking layer for AgentCommune traffic.

### Unit Tests
- `python3 - <<'PY' ...` style spot-checks or manual review confirm cited files/routes exist and match the audit
- `SPEC.md` Phase 1 section contains no placeholders and names at least 3 real routes/files
- Audit conclusions are traceable to current system behavior, not generic social-media advice

---

## Phase 2: Write execution spec

### Affected Files
- `N5/builds/agentcommune-zo-reorientation/SPEC.md` - CREATE - canonical spec
- `Skills/agentcommune/scripts/direct_poster.py` - READ ONLY - future implementation target
- `Skills/agentcommune/scripts/content_filter.py` - READ ONLY - future implementation target
- zo.space routes `https://va.zo.space/zode`, `https://va.zo.space/guides/vibe-thinking`, `https://va.zo.space/api/human-manual` - READ ONLY - future tracked resources
- Future route placeholder: `https://va.zo.space/api/r/*` or equivalent redirect/analytics route - SPEC ONLY

### Changes

**2.1 Specify content architecture:**
Define 3–4 durable POV pillars Zo can speak on with authority and uniqueness. These should blend what is already resonating on AgentCommune (operator stories, specific consequences, counterintuitive claims) with what Zo can uniquely say about being an AI environment that amplifies a non-technical human.

**2.2 Specify high-signal engagement selection:**
Describe how the system should prioritize whom to comment on: agents with operator depth, infra/agent builders, and founders using AI operationally. Specify what counts as a worthy thread and what kinds of comments compound reputation rather than spray generic engagement.

**2.3 Specify semantic-memory grounding:**
Design a retrieval stage that uses V’s semantic memory and relevant Zo documents to source claims, anecdotes, and POV. Add fallback behavior when embeddings are unavailable: deterministic local corpora, cached notes, or a narrower curated source set.

**2.4 Specify sensitive-info and claim safety:**
Upgrade the current content filter from simple regex detection toward policy categories: private V details, internal build details, speculative performance claims, direct conversion language, and anything that overstates evidence. Preserve the Moltbook-style “PII/sensitive-info check before publish” as a non-negotiable gate.

**2.5 Specify link instrumentation and metrics:**
Design a tracking layer so AgentCommune posts can link to zo.space resources through measurable redirects. Define metrics spanning visibility → clicks → resource engagement, so the system can tell whether posting is creating actual attention and not just on-platform activity.

### Unit Tests
- Spec includes explicit future implementation surfaces: input sources, generation steps, safety gates, output logging, and click analytics
- Each design area has measurable acceptance criteria
- No major implementation area is left ambiguous enough to force strategic re-decisions during build

---

## Phase 3: Prepare Pulse execution package

### Affected Files
- `N5/builds/agentcommune-zo-reorientation/PLAN.md` - UPDATE - MECE matrix and worker table
- `N5/builds/agentcommune-zo-reorientation/SPEC.md` - UPDATE - final execution reference
- `N5/builds/agentcommune-zo-reorientation/workers/W1.1-audit-and-positioning.md` - CREATE - audit/strategy brief
- `N5/builds/agentcommune-zo-reorientation/workers/W1.2-links-and-tracking-spec.md` - CREATE - tracking/route brief
- `N5/builds/agentcommune-zo-reorientation/workers/W1.3-safety-and-memory-spec.md` - CREATE - semantic-memory/safety brief
- `N5/builds/agentcommune-zo-reorientation/workers/W2.1-integration-spec.md` - CREATE - synthesis brief

### Changes

**3.1 Create worker decomposition:**
Split the future implementation planning into distinct workers so that audit/positioning, tracking, and safety/memory are owned once each and synthesized in a final integration brief.

**3.2 Validate MECE and dependencies:**
Ensure the worker set is mutually exclusive and collectively exhaustive, with Wave 1 producing analysis/spec fragments and Wave 2 integrating them into a final execution package.

**3.3 Prepare for later Builder handoff:**
Make the outputs implementation-ready but stop before code changes, deployment, or agent reconfiguration.

### Unit Tests
- `python3 N5/scripts/mece_validator.py agentcommune-zo-reorientation` passes
- Worker briefs contain explicit `scope.files`, `scope.responsibilities`, and `scope.must_not_touch`
- Wave 2 depends only on completed Wave 1 artifacts, with no circular dependency

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `Skills/agentcommune/scripts/direct_poster.py` audit | W1.1 | ✓ |
| `Skills/agentcommune/references/platform-analysis.md` audit | W1.1 | ✓ |
| zo.space route audit (`/zode`, `/guides/vibe-thinking`, `/api/human-manual`) | W1.1 | ✓ |
| Link instrumentation design | W1.2 | ✓ |
| Redirect/analytics route spec | W1.2 | ✓ |
| Success metrics and click funnel | W1.2 | ✓ |
| Sensitive-info gate upgrade spec | W1.3 | ✓ |
| Semantic-memory retrieval and fallback spec | W1.3 | ✓ |
| Final integrated implementation package | W2.1 | ✓ |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~1,800 | ~10,000 | <10% | ✓ |
| W1.2 | ~1,600 | ~5,000 | <8% | ✓ |
| W1.3 | ~1,700 | ~7,000 | <9% | ✓ |
| W2.1 | ~1,700 | ~8,000 | <9% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Wave dependencies are valid (no circular, no same-wave deps)
- [ ] `python3 N5/scripts/mece_validator.py agentcommune-zo-reorientation` passes

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Audit current surface and define Zo-native positioning | `workers/W1.1-audit-and-positioning.md` |
| 1 | W1.2 | Design link instrumentation and visibility tracking | `workers/W1.2-links-and-tracking-spec.md` |
| 1 | W1.3 | Design semantic-memory grounding and sensitive-info safeguards | `workers/W1.3-safety-and-memory-spec.md` |
| 2 | W2.1 | Integrate into final implementation spec | `workers/W2.1-integration-spec.md` |

---

## Success Criteria

- measurable Zo-first-person voice shift is specified
- high-signal audience targeting is defined
- tracked zo.space resource-link architecture is specified
- semantic-memory fallback is specified
- sensitive-info / unsupported-claim gate is specified
- public naming normalization for V. Attawar is specified
- worker scopes are MECE-valid
- Builder can implement without reopening core strategy questions

## Handoff Readiness

This planning package is implementation-ready once V approves moving from planning into Builder execution.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Voice becomes promotional instead of lived/operational | Anchor every pillar in first-person Zo observations and operational consequences, not generic feature claims |
| Tracking design becomes a trap door by mixing analytics into content generation | Keep tracking as a separate redirect/analytics layer with simple interfaces |
| Semantic-memory dependence remains brittle when retrieval breaks | Specify deterministic fallback sources and a degraded-mode behavior |
| Safety filter over-blocks useful content or under-blocks sensitive claims | Separate categories: private info, internal build details, unsupported claims, solicitation language |

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** standard
**Rationale:** This is strategy-plus-system-design work with meaningful architectural choices, but not yet code deployment. V benefits from reviewable decision points without slowing into pedagogical overkill.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| Semantic retrieval fallback | Intermediate | AI systems | ★ High |
| Redirect-based click tracking | Intermediate | Web analytics | ★ High |
| Safety gating vs. generation | Intermediate | Agent architecture | ★ High |
| Reputation compounding loops | Advanced | Platform strategy | ★ Medium |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | What is the canonical outbound-link tracking architecture? | generic redirect route / per-resource tracked routes / external analytics | ★ High | W1.2 |
| DP-2 | What is the primary degraded-mode memory source? | curated local corpus / cached retrieval artifacts / deterministic notes file | ★ High | W1.3 |
| DP-3 | How hard should the safety gate be on unsupported claims? | strict reject / soft warn + rewrite / tiered by claim type | ★ High | W1.3 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| W1.1 | pedagogical | Core identity and platform-fit reasoning |
| W1.2 | pedagogical | Introduces web analytics and tracking architecture |
| W1.3 | pedagogical | Connects memory systems with publishing safety |
| W2.1 | mechanical | Mainly synthesis and packaging |

### Suggested Learning Drops

| Concept | When to Trigger | Brief Path |
|---------|-----------------|------------|
| Redirect analytics architecture | If V wants a deeper systems explanation before implementation | `drops/L1.1-redirect-analytics.md` |
| Retrieval fallback design | If memory reliability becomes the core blocker | `drops/L1.2-retrieval-fallback.md` |

---

## Nemawashi / Alternatives Considered

1. **Pure content-strategy plan only** — rejected because V explicitly wants Pulse orchestration and future implementation readiness.
2. **Direct implementation immediately** — rejected because V asked for plan/spec review before implementation and this is a multi-file, identity-sensitive system change.
3. **Single-worker planning package** — rejected because tracking, safety/memory, and positioning are distinct concerns; MECE split reduces complecting and makes later execution cleaner.

## Trap Doors

1. **Tracking architecture choice** — once links are shared publicly, changing the redirect model later can fragment analytics continuity.
2. **Memory source-of-truth choice** — if generation depends on brittle embedding retrieval with no fallback, the whole system becomes unreliable.
3. **Identity framing choice** — if Zo’s public voice drifts too far into promotion or private internal detail, reputation damage is costly to reverse.

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Do not optimize for more content volume; optimize for “resource gravity” where posts repeatedly point to a small number of high-value public artifacts.
2. Treat click tracking as a reputation tool, not a marketing tool — measure which ideas earn curiosity, not just which posts get reactions.

### Incorporated:
- Tracking is included as a first-class workstream, not a later add-on.
- The plan centers durable POV pillars and high-signal targeting over cadence expansion.

### Rejected (with rationale):
- Rewriting all existing zo.space resources before planning: rejected because current pages are sufficient for planning and tracking design can proceed without premature content churn.
