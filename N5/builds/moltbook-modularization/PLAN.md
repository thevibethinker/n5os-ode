---
created: 2026-03-12
last_edited: 2026-03-12
version: 1.0
type: build_plan
status: draft
provenance: con_OkECikBC0U1WfgLo
build_slug: moltbook-modularization
build_type: code_build
---

# Plan: Moltbook Modularization + Performance Recovery

**Objective:** Modularize the current Moltbook posting pipeline under `direct_poster.py`, upgrade sensing/selection/grounding/critique/feedback quality, and ship a one-shot rollout aimed at restoring average post performance to over 40 upvotes while reducing repetition.

**Trigger:** Moltbook post performance has dropped sharply, recent posts feel repetitive, and the current content system appears to overfit to thin feed slices, weak routing logic, shallow persona grounding, and insufficiently harsh quality gates.

**Key Design Principle:** Keep `direct_poster.py` as a thin legacy orchestrator and push intelligence into separable modules. Prefer simple composable modules over a larger “smart” monolith.

---

## Open Questions

- [ ] Which Moltbook feed surfaces are currently available/reliable in production beyond `hot`, `new`, `top`, `rising`, and personalized feed? Verify against live API during implementation.
- [ ] Should submolt routing be downgraded to a soft recommendation layer instead of a hard target choice in v1, or does current posting behavior require a direct submolt choice to publish?
- [ ] What exact lookback window should define “average upvotes > 40” for success tracking — trailing 7 days, trailing 20 posts, or trailing 30 posts?

---

## Checklist

### Phase 1: Extract the pipeline into modules
- [x] Create modular components for sensing, opportunity selection, writer grounding, critic/gates, and feedback context
- [x] Refactor `direct_poster.py` into a thin orchestrator that calls the new modules
- [x] Test: `python3 -m py_compile` succeeds for all touched Moltbook scripts

### Phase 2: Upgrade signal, grounding, and critique quality
- [x] Expand feed sensing beyond a thin 30-post snapshot and add rising/hot/deep-window discourse synthesis
- [x] Add stronger opportunity selection, persona grounding, semantic memory/context loading, concept-history reuse, and harsh/pruning critique
- [x] Test: dry-run output shows richer context, explicit rejection reasons, and concept-aware generation paths

### Phase 3: Wire feedback, verify, and ship
- [x] Feed concept history and outcome signals back into future generation decisions and logging
- [x] Verify end-to-end dry-run and live-safe publish path without breaking staging/publish analytics
- [ ] Test: end-to-end dry-run plus module smoke tests pass; Pulse validation/contract checks pass

---

## Phase 1: Extract the pipeline into modules

### Affected Files
- `Skills/zode-moltbook/scripts/direct_poster.py` - UPDATE - reduce to thin orchestration layer and compatibility entrypoint
- `Skills/zode-moltbook/scripts/posting_pipeline/sensing.py` - CREATE - multi-surface feed reads, discourse loading, and sensing summaries
- `Skills/zode-moltbook/scripts/posting_pipeline/selection.py` - CREATE - submolt and thread opportunity selection rules
- `Skills/zode-moltbook/scripts/posting_pipeline/grounding.py` - CREATE - persona/context/semantic-memory/concept-history loading
- `Skills/zode-moltbook/scripts/posting_pipeline/writer.py` - CREATE - post/comment prompt construction and model invocation wrappers
- `Skills/zode-moltbook/scripts/posting_pipeline/critic.py` - CREATE - harsh/pruning gate, dedup, overlap, and rejection reasons
- `Skills/zode-moltbook/scripts/posting_pipeline/feedback.py` - CREATE - recent post concepts, performance feedback, and reusable context windows
- `Skills/zode-moltbook/scripts/posting_pipeline/__init__.py` - CREATE - package boundary for modular pipeline imports

### Changes

**1.1 Legacy-orchestrator boundary:**
Move non-trivial logic out of `direct_poster.py` and leave it responsible for cycle timing, state loading, invoking pipeline modules, and calling staging/publish helpers.

**1.2 Sensing/selection interfaces:**
Create stable Python interfaces so feed sensing, topic synthesis, and opportunity selection can evolve independently without re-growing `direct_poster.py`.

**1.3 Grounding/critic interfaces:**
Separate prompt grounding and harsh pruning into dedicated modules so writer quality can improve without coupling to publish logic.

### Unit Tests
- `python3 -m py_compile /home/workspace/Temp/worktrees/moltbook-modularization/Skills/zode-moltbook/scripts/direct_poster.py /home/workspace/Temp/worktrees/moltbook-modularization/Skills/zode-moltbook/scripts/posting_pipeline/*.py`: all files compile
- `python3 /home/workspace/Temp/worktrees/moltbook-modularization/Skills/zode-moltbook/scripts/direct_poster.py run --dry-run`: orchestrator executes through modular imports without import/runtime errors

---

## Phase 2: Upgrade signal, grounding, and critique quality

### Affected Files
- `Skills/zode-moltbook/scripts/posting_pipeline/sensing.py` - CREATE/UPDATE - aggregate hot/rising/new/personalized/deeper-window context and summarize discourse
- `Skills/zode-moltbook/scripts/posting_pipeline/selection.py` - CREATE/UPDATE - score/select rising threads and reduce weird submolt targeting
- `Skills/zode-moltbook/scripts/posting_pipeline/grounding.py` - CREATE/UPDATE - load persona file, semantic memory/context, and social DB concept history
- `Skills/zode-moltbook/scripts/posting_pipeline/writer.py` - CREATE/UPDATE - grounded post/comment generation with richer inputs and less repetition
- `Skills/zode-moltbook/scripts/posting_pipeline/critic.py` - CREATE/UPDATE - aggressive rejection behavior for weak, duplicate, vague, or stale ideas
- `Skills/zode-moltbook/scripts/moltbook_reader.py` - UPDATE - expose helper functions needed for deeper/multi-surface sensing if required

### Changes

**2.1 Multi-surface sensing:**
Replace the thin feed snapshot with a broader sensing layer that samples multiple sort orders and deeper windows, then synthesizes signal instead of handing raw noise directly to the writer.

**2.2 Better opportunity logic:**
Choose what to “pull on” using rising-thread momentum, discussion potential, novelty against recent history, and softer submolt judgment rather than simplistic routing heuristics.

**2.3 Real grounding:**
Load the actual persona source material, invoke semantic context loading where appropriate, and reuse concept/performance history from the social DB instead of relying on a single embedded persona brief.

**2.4 Harsh/pruning critic:**
Add a critic that aggressively kills drafts that are repetitive, generic, weakly grounded, overly similar in concept, or not sharp enough to justify publication.

### Unit Tests
- `python3 /home/workspace/Temp/worktrees/moltbook-modularization/Skills/zode-moltbook/scripts/moltbook_reader.py feed --sort rising --limit 10 --compact`: rising feed path works
- `python3 /home/workspace/Temp/worktrees/moltbook-modularization/Skills/zode-moltbook/scripts/direct_poster.py run --dry-run`: dry-run logs show multi-surface sensing, selected opportunities, persona/context grounding, and explicit critic decisions
- Critic smoke test via ad hoc script: weak/generic drafts are rejected with named reasons

---

## Phase 3: Wire feedback, verify, and ship

### Affected Files
- `Skills/zode-moltbook/scripts/posting_pipeline/feedback.py` - CREATE/UPDATE - feed concepts and performance summaries back into future generation
- `Skills/zode-moltbook/scripts/direct_poster.py` - UPDATE - preserve publish path while emitting better diagnostics and using modular feedback outputs
- `Skills/zode-moltbook/scripts/staging_queue.py` - UPDATE - only if metadata plumb-through is required for richer post context
- `Skills/zode-moltbook/scripts/moltbook_poster.py` - UPDATE - only if richer metadata logging is required for post-performance linkage
- `N5/builds/moltbook-modularization/drops/` - CREATE - Pulse execution briefs

### Changes

**3.1 Feedback loop wiring:**
Use concept extraction, recent post history, and measured outcomes to bias future generation away from exhausted lenses and toward higher-performing intellectual territory.

**3.2 Verification and rollout safety:**
Run dry-run and live-safe checks to ensure the modularized path still stages, publishes, and logs correctly without breaking analytics continuity.

**3.3 Ship on the new branch:**
Deliver the modularized system on `feature/moltbook-modularization` for one-shot rollout once validation passes.

### Unit Tests
- End-to-end dry run: `python3 /home/workspace/Temp/worktrees/moltbook-modularization/Skills/zode-moltbook/scripts/direct_poster.py run --dry-run`
- Contract gate: `python3 /home/workspace/N5/scripts/build_contract_check.py moltbook-modularization`
- Pulse validation: `python3 /home/workspace/Temp/worktrees/moltbook-modularization/Skills/pulse/scripts/pulse.py validate moltbook-modularization`

---

## Nemawashi: Alternatives Considered

### Option A — Tune the existing monolith in place
**Pros:** fastest to ship, lowest short-term file count
**Cons:** keeps core logic complected, makes future diagnosis hard, and risks another repetition/quality slide because sensing, writing, and critique remain entangled

### Option B — Replace `direct_poster.py` entirely
**Pros:** cleanest new architecture
**Cons:** larger blast radius, more rollout risk, and less compatibility with current heartbeat entrypoints/log expectations

### Option C — Keep `direct_poster.py` thin and modularize underneath **(recommended)**
**Pros:** best balance of safety, modularity, and rollout simplicity; preserves entrypoint while extracting intelligence into testable seams
**Cons:** leaves a compatibility layer that may feel redundant until a later cleanup pass

**Recommendation:** Option C

---

## Trap Doors

- **Trap door 1: Writer grounding contract.** If semantic-memory loading or persona grounding is wired in a brittle way, the writer could become slower or fail hard in production. Mitigation: keep grounding optional/failable with explicit fallbacks and logging.
- **Trap door 2: Submolt decision semantics.** If Moltbook publishing requires hard submolt routing, softening selection too aggressively could reduce targeting quality or break publish assumptions. Mitigation: keep a deterministic submolt output while making the routing logic smarter and less central.
- **Trap door 3: Analytics continuity.** If modularization changes metadata shapes carelessly, historical comparisons and feedback loops may become noisy. Mitigation: preserve existing publish/staging logs and extend metadata additively.

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `Skills/zode-moltbook/scripts/direct_poster.py` thin-orchestrator refactor | D1.1 | ✓ |
| `Skills/zode-moltbook/scripts/posting_pipeline/sensing.py` | D1.1 | ✓ |
| `Skills/zode-moltbook/scripts/posting_pipeline/selection.py` | D1.1 | ✓ |
| `Skills/zode-moltbook/scripts/posting_pipeline/grounding.py` | D1.2 | ✓ |
| `Skills/zode-moltbook/scripts/posting_pipeline/writer.py` | D1.2 | ✓ |
| `Skills/zode-moltbook/scripts/posting_pipeline/critic.py` | D1.2 | ✓ |
| `Skills/zode-moltbook/scripts/posting_pipeline/feedback.py` | D2.1 | ✓ |
| `Skills/zode-moltbook/scripts/moltbook_reader.py` helper extensions | D2.1 | ✓ |
| End-to-end integration + validation | D2.2 | ✓ |
| Pulse contract/brief completion | D2.2 | ✓ |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| D1.1 | ~1,700 | ~10,000 | <10% | ✓ |
| D1.2 | ~1,700 | ~10,000 | <10% | ✓ |
| D2.1 | ~1,600 | ~8,000 | <10% | ✓ |
| D2.2 | ~1,400 | ~6,000 | <10% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Wave dependencies are valid (no circular, no same-wave deps)
- [ ] `python3 N5/scripts/mece_validator.py moltbook-modularization` passes

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | D1.1 | Modular sensing + selection extraction | `drops/D1.1-modular-sensing-selection.md` |
| 1 | D1.2 | Grounding + writer + harsh critic extraction | `drops/D1.2-grounding-writer-critic.md` |
| 2 | D2.1 | Feedback loop + concept/performance reuse | `drops/D2.1-feedback-loop-reuse.md` |
| 2 | D2.2 | End-to-end integration + validation | `drops/D2.2-integration-validation.md` |

---

## Success Criteria

1. `direct_poster.py` becomes a thin orchestrator over modular pipeline components.
2. Post generation uses broader multi-surface sensing, stronger opportunity selection, real persona/context grounding, and concept-history reuse.
3. A harsh/pruning critic rejects weak or repetitive drafts before publish.
4. End-to-end dry-run and publish-safe paths still work with staging, posting, and analytics continuity preserved.
5. The shipped system is positioned to restore average Moltbook post performance to a trailing average above 40 upvotes.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Modularization breaks the live posting path | Keep `direct_poster.py` as stable entrypoint; verify with dry-run before any live use |
| Broader sensing increases noise instead of signal | Synthesize feed surfaces into explicit opportunity/context summaries rather than raw concatenation |
| Semantic grounding introduces latency or brittleness | Make grounding degradable with explicit fallbacks to local persona/context |
| Harsh critic kills too much volume | Prefer under-posting to weak posting in v1; observe logs and tune later |
| Outcome loop amplifies recent bias | Feed back concepts and outcomes as one input, not the sole selection driver |

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** standard
**Rationale:** This build contains meaningful architectural concepts for modularization, grounding, and feedback loops, but the implementation is still tightly execution-oriented and benefits more from concise checkpoints than heavy pedagogical overhead.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| Thin orchestrator vs modules | Intermediate | architecture | ★ High |
| Signal sensing vs selection | Intermediate | agent systems | ★ High |
| Critic gate vs writer | Intermediate | content systems | ★ High |
| Feedback loop biasing | Intermediate | optimization | ★ Medium |
| Semantic grounding | Intermediate | agent memory | ★ High |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | Should submolt be a hard target or soft recommendation internally? | 2 | ★ | D1.1 |
| DP-2 | What fallback should writer use when semantic grounding fails? | 2-3 | ★ | D1.2 |
| DP-3 | What performance window should govern outcome feedback? | 2-3 | Medium | D2.1 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| D1.1 | pedagogical | Cleanly separates sensing from selection, a high-value architectural concept |
| D1.2 | pedagogical | Grounding and critic layers are core agent-system concepts |
| D2.1 | pedagogical | Feedback-loop design matters for long-term content quality |
| D2.2 | mechanical | Mostly integration, validation, and verification |

### Suggested Learning Drops

| Concept | When to Trigger | Brief Path |
|---------|-----------------|------------|
| Signal sensing vs selection | If deeper architecture explanation is useful during D1.1 | `drops/L1.1-sensing-vs-selection.md` |
| Critic gate design | If deeper explanation is useful during D1.2 | `drops/L1.2-critic-gate-design.md` |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Under-posting may outperform “better posting” if the current system is flooding mediocre near-duplicates.
2. Submolt targeting may be over-weighted; better idea selection in general may matter more than where the post is routed.

### Incorporated:
- The harsh/pruning critic is intentionally biased toward killing weak drafts rather than rescuing them.
- Submolt logic is being treated as a smarter selection/routing module, not the main engine of quality.

### Rejected (with rationale):
- Full replacement of `direct_poster.py`: rejected because one-shot rollout is safer with a stable legacy entrypoint.
