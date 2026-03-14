---
created: 2026-03-12
last_edited: 2026-03-12
version: 1.0
type: build_plan
status: draft
provenance: con_LHsClQAZRekh7CWf
---

# Plan: Semantic Memory Google Migration

**Objective:** Migrate N5 semantic memory to a Google-only embeddings architecture using Gemini API, make `brain.db` the canonical successor database, remove split retrieval ambiguity, and execute the migration safely from a dedicated worktree.

**Trigger:** V approved a full migration build with Gemini API, Google-only provider strategy, `GEMINI_API_KEY` already configured, Pulse orchestration, and a new worktree/feature branch.

**Key Design Principle:** Keep the system simple: one canonical memory database, one active embedding provider, one retrieval contract. Preserve graph/relationship capabilities in `brain.db`, and treat embeddings/indexes as rebuildable derivatives of canonical blocks/resources.

---

## Open Questions

- [ ] Should legacy `vectors_v2.db` remain as an archived fallback artifact after cutover, or be marked deprecated but retained untouched?
- [ ] What dimension should be the production default for Gemini embeddings: 3072 for max recall parity, or 1536/768 if evals show near-equal quality with better speed/storage?
- [ ] Should the initial migration preserve BM25 + reranker behavior exactly, or allow reranker tuning as long as retrieval quality improves?

---

## Checklist

### Phase 1: Canonicalize the substrate and add Gemini provider support
- ☐ Define the new canonical memory contract around `brain.db`
- ☐ Implement Gemini embedding provider and configuration plumbing
- ☐ Test: provider can generate embeddings through `GEMINI_API_KEY` and memory client initializes without ambiguity

### Phase 2: Migrate indexing and retrieval to the canonical path
- ☐ Update indexing/rebuild scripts to target `brain.db`
- ☐ Remove automatic preference for `vectors_v2.db` in active retrieval paths
- ☐ Test: end-to-end indexing + ANN rebuild + retrieval works against `brain.db`

### Phase 3: Build migration/eval tooling and cutover validation
- ☐ Add migration script(s) and evaluation harness for corpus-level comparison
- ☐ Validate retrieval quality, speed, and state consistency after migration
- ☐ Test: migration can be dry-run/repeatable and produces measurable before/after evidence

### Phase 4: Pulse execution packaging and activation readiness
- ☐ Create MECE drop briefs and validate build contract
- ☐ Start Pulse once validation gates pass and conflict gate is clear
- ☐ Test: `build_contract_check`, `pulse validate`, and `mece_validator` pass

---

## Phase 1: Canonicalize the substrate and add Gemini provider support

### Affected Files
- `N5/builds/semantic-memory-google-migration/PLAN.md` - UPDATE - executable build plan
- `N5/builds/semantic-memory-google-migration/meta.json` - UPDATE - Pulse drop/wave contract
- `N5/builds/semantic-memory-google-migration/drops/D1.1-canonical-memory-contract.md` - CREATE - substrate contract brief
- `N5/builds/semantic-memory-google-migration/drops/D1.2-gemini-provider-adapter.md` - CREATE - provider implementation brief
- `N5/cognition/n5_memory_client.py` - UPDATE - canonical DB selection + Gemini embedding provider support
- `N5/lib/paths.py` - UPDATE - clarify canonical memory paths and deprecation notes if needed
- `N5/cognition/BASELINE.md` - UPDATE - document new canonical architecture

### Changes

**1.1 Canonical memory contract:**
Make `brain.db` the canonical active semantic-memory DB. Preserve graph/entity/relationship tables there. Remove active-path ambiguity where runtime retrieval silently prefers `vectors_v2.db` when present.

**1.2 Gemini provider adapter:**
Add a Gemini embedding provider path in `n5_memory_client.py` using `GEMINI_API_KEY`, explicit model naming, dimension handling, and provider selection via config/env. Ensure initialization is deterministic and no longer auto-switches based on legacy OpenAI vector dimensions.

**1.3 Config + docs alignment:**
Update paths/docs so the intended architecture is obvious: canonical blocks/resources/vectors in `brain.db`; ANN index derived from `brain.db`; legacy DB retained only as migration input or archive.

### Unit Tests
- Instantiate memory client with Gemini provider and confirm embeddings are produced successfully
- Confirm default active DB path resolves to `brain.db` rather than `vectors_v2.db`
- Confirm docs/configs no longer describe an ambiguous dual-active-store setup

---

## Phase 2: Migrate indexing and retrieval to the canonical path

### Affected Files
- `N5/cognition/n5_memory_client.py` - UPDATE - retrieval/indexing behavior
- `N5/scripts/n5_index_embeddings.py` - UPDATE - target canonical DB and Gemini dimensions
- `N5/scripts/n5_rebuild_ann_index.py` - UPDATE - rebuild against canonical DB
- `N5/scripts/migrate_embeddings.py` - UPDATE - migration flow if reusable
- `N5/scripts/run_full_reindex.py` - UPDATE - canonical execution path if used
- `N5/capabilities/internal/hybrid-rag-layer-v1.md` - UPDATE - retrieval architecture doc
- `N5/capabilities/internal/ann-indexed-semantic-search.md` - UPDATE - ANN contract doc

### Changes

**2.1 Retrieval path cleanup:**
Eliminate split-brain active retrieval behavior. The active search path should read vectors from `brain.db`, query embeddings from Gemini, and rebuild ANN from the same canonical source.

**2.2 Script alignment:**
Update indexing scripts so they no longer assume OpenAI 3072 as the only large-model path. Add explicit dimension/model/provider config and make rebuild/reindex flows deterministic.

**2.3 Compatibility discipline:**
Where helpful, preserve script entrypoints but change internals so existing workflows still function while using the new canonical substrate.

### Unit Tests
- Index a small canonical corpus into `brain.db` with Gemini embeddings
- Rebuild ANN index successfully from canonical vectors
- Run semantic search and profile search successfully against `brain.db`
- Verify no active-path code still auto-prefers `vectors_v2.db`

---

## Phase 3: Build migration/eval tooling and cutover validation

### Affected Files
- `N5/builds/semantic-memory-google-migration/drops/D2.1-migration-tooling.md` - CREATE - migration tooling brief
- `N5/builds/semantic-memory-google-migration/drops/D2.2-eval-and-cutover-validation.md` - CREATE - eval/cutover brief
- `N5/scripts/semantic_memory_reindex.py` - UPDATE or CREATE - full migration runner if canonical candidate
- `N5/scripts/semantic_memory_eval.py` - CREATE - retrieval quality/speed eval harness
- `N5/cognition/BASELINE.md` - UPDATE - before/after measurements and operating notes
- `N5/data/reindex_state.json` - READ/UPDATE if needed by migration flow
- `N5/data/reindex_complete.json` - READ/UPDATE if needed by migration flow

### Changes

**3.1 Migration runner:**
Create or adapt a deterministic migration runner that can re-embed canonical resources into `brain.db`, support dry-run where possible, and log progress/state explicitly.

**3.2 Eval harness:**
Add a corpus-level evaluation flow that measures retrieval quality first, then speed: handpicked semantic queries, profile-scoped retrieval, latency snapshots, ANN behavior, and index consistency.

**3.3 Cutover evidence:**
Produce concrete evidence that the new substrate works and is better/acceptable before deprecating the old path operationally.

### Unit Tests
- Dry-run migration reports expected scope without mutating data
- Real migration can resume/re-run safely without duplicating corrupted state
- Eval harness outputs measurable metrics for recall-quality proxies and latency
- Post-migration checks confirm resources/blocks/vectors are internally consistent

---

## Phase 4: Pulse execution packaging and activation readiness

### Affected Files
- `N5/builds/semantic-memory-google-migration/PLAN.md` - UPDATE - final MECE matrix
- `N5/builds/semantic-memory-google-migration/meta.json` - UPDATE - active Pulse contract
- `N5/builds/semantic-memory-google-migration/drops/D1.1-canonical-memory-contract.md` - CREATE - Wave 1 brief
- `N5/builds/semantic-memory-google-migration/drops/D1.2-gemini-provider-adapter.md` - CREATE - Wave 1 brief
- `N5/builds/semantic-memory-google-migration/drops/D2.1-migration-tooling.md` - CREATE - Wave 2 brief
- `N5/builds/semantic-memory-google-migration/drops/D2.2-eval-and-cutover-validation.md` - CREATE - Wave 2 brief
- `N5/builds/semantic-memory-google-migration/STATUS.md` - UPDATE - progress visibility

### Changes

**4.1 MECE drop decomposition:**
Split work into substrate contract, provider adapter, migration tooling, and validation/cutover. Keep ownership non-overlapping and collectively exhaustive.

**4.2 Validation gates:**
Run contract check, Pulse validate, and MECE validation before start. Pulse start should only happen once the build package passes all local gates and the agent conflict gate is clear.

**4.3 Worktree execution readiness:**
Ensure implementation will be done from `Temp/worktrees/semantic-memory-google-migration` on `feature/semantic-memory-google-migration`, not on the currently busy workspace branch.

### Unit Tests
- `python3 N5/scripts/build_contract_check.py semantic-memory-google-migration`
- `python3 Skills/pulse/scripts/pulse.py validate semantic-memory-google-migration`
- `python3 N5/scripts/mece_validator.py semantic-memory-google-migration`
- `git -C /home/workspace/Temp/worktrees/semantic-memory-google-migration status --short --branch`

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `N5/cognition/n5_memory_client.py` canonical DB contract | D1.1 | ✓ |
| `N5/lib/paths.py` canonical/deprecation path cleanup | D1.1 | ✓ |
| `N5/cognition/BASELINE.md` architecture documentation | D1.1 | ✓ |
| Gemini embedding provider implementation | D1.2 | ✓ |
| Indexing/rebuild script provider alignment | D1.2 | ✓ |
| Migration runner / reindex flow | D2.1 | ✓ |
| Reindex state + resumability handling | D2.1 | ✓ |
| Eval harness and cutover validation | D2.2 | ✓ |
| Retrieval architecture docs updates | D2.2 | ✓ |
| Build contract / Pulse readiness | Orchestrator | ✓ |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| D1.1 | ~1,800 | ~9,000 | <10% | ✓ |
| D1.2 | ~1,900 | ~10,000 | <10% | ✓ |
| D2.1 | ~1,800 | ~8,000 | <9% | ✓ |
| D2.2 | ~1,800 | ~7,000 | <9% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Wave dependencies are valid (no circular, no same-wave deps)
- [ ] `python3 N5/scripts/mece_validator.py semantic-memory-google-migration` passes

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | D1.1 | Canonical memory contract on `brain.db` | `drops/D1.1-canonical-memory-contract.md` |
| 1 | D1.2 | Gemini provider adapter + indexing alignment | `drops/D1.2-gemini-provider-adapter.md` |
| 2 | D2.1 | Migration tooling + reindex orchestration | `drops/D2.1-migration-tooling.md` |
| 2 | D2.2 | Eval harness + cutover validation | `drops/D2.2-eval-and-cutover-validation.md` |

---

## Success Criteria

1. `brain.db` is the single canonical active semantic-memory database for resources, blocks, vectors, and graph relationships.
2. The runtime memory client uses Gemini embeddings via `GEMINI_API_KEY` and no longer silently prefers `vectors_v2.db`.
3. Indexing, ANN rebuild, and retrieval flows operate against the canonical substrate and can be re-run deterministically.
4. A migration/eval path exists that proves acceptable or improved memory quality and reports speed/consistency metrics.
5. Pulse build contract is valid and execution can proceed from the dedicated worktree without touching the already-busy root branch.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Gemini embedding dimensions break compatibility with existing ANN/vector assumptions | Make dimension explicit in provider/config and rebuild ANN from canonical vectors rather than trying to reuse old indexes |
| Canonicalizing onto `brain.db` damages graph/relationship features | Preserve graph tables in-place and constrain migration work to semantic-memory tables/paths only |
| Full migration creates unrecoverable state drift | Keep old DBs untouched, run migration as additive/rebuild flow where possible, and validate counts/consistency before cutover |
| Pulse start is blocked by agent conflict or transient Zo API issues | Complete local planning + validation first, then re-run the conflict gate and only start when clear |

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** standard
**Rationale:** This is a deep systems migration with architectural significance, but the user already made the main trap-door decisions. Standard friction keeps execution moving while preserving visibility into decisions that matter.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| Canonical DB vs derived index | Intermediate | System architecture | ★ High |
| Embeddings as rebuildable derivatives | Intermediate | AI systems | ★ High |
| ANN index rebuild discipline | Intermediate | Retrieval systems | ★ High |
| Provider adapter / abstraction boundary | Intermediate | Software architecture | ★ Medium |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | Default Gemini output dimension | 3072 / 1536 / 768 | ★ High | D1.2 |
| DP-2 | Fate of `vectors_v2.db` after cutover | archive / deprecated-retained / remove later | ★ Medium | D2.1 |
| DP-3 | Keep existing reranker behavior or tune during migration | preserve / tune | ★ Medium | D2.2 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| D1.1 | pedagogical | Core architectural clarification about canonical vs derived layers |
| D1.2 | pedagogical | Introduces provider abstraction and embedding dimensions |
| D2.1 | mechanical | Mostly deterministic migration/state tooling |
| D2.2 | pedagogical | Teaches how to judge retrieval quality vs speed |

### Suggested Learning Drops

| Concept | When to Trigger | Brief Path |
|---------|-----------------|------------|
| Canonical DB vs rebuildable index | If V wants a deeper systems explanation during D1.1 | `drops/L1.1-canonical-vs-derived.md` |
| ANN quality vs latency tradeoff | If dimension/performance tradeoffs become central during D2.2 | `drops/L1.2-ann-tradeoffs.md` |

---

## Nemawashi / Alternatives Considered

1. **Leave `brain.db` for graph only and create a third canonical vector DB** — rejected because it preserves conceptual sprawl and prolongs ambiguity.
2. **Keep `vectors_v2.db` as active semantic store and add Gemini there** — rejected because V explicitly wants `brain.db` as the successor DB and one canonical active substrate.
3. **Dual-provider migration with OpenAI fallback** — rejected because V explicitly chose Google-only and a full migration build.

## Trap Doors

1. **Canonical DB choice (`brain.db`)** — accepted by V; reversing later would require another full migration.
2. **Google-only provider strategy** — accepted by V; simplifies the system but reduces fallback diversity.
3. **Embedding dimension default** — affects storage, ANN rebuild cost, and retrieval behavior across the corpus.

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Treat embeddings and ANN indexes as compiled artifacts, not the canonical memory itself.
2. Solve split-brain retrieval before chasing model-card benchmark gains.

### Incorporated:
- The plan centers on canonical substrate unification first, then provider migration, then evaluation.

### Rejected (with rationale):
- Multi-provider fallback in the first cut: rejected because it adds ambiguity back into the system and V explicitly chose Google-only.
