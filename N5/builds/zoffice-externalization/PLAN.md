---
created: 2026-03-13
last_edited: 2026-03-13
version: 1.0
provenance: con_hs2l0mnC3kX6g5tx
type: build_plan
status: draft
---
# Plan: Zoffice Externalization

**Objective:** Produce a reviewable, versioned external Zoffice release folder that is ready for validation before transfer to Zoputer, using `Zoffice/` as the canonical product surface and integrating substrate/zo2zo transfer capability into the exported package without installing Zoffice into this live Zo.

**Trigger:** V clarified that the goal is not local integration into va’s Zo, but externalization: this computer should act as the factory for a portable Zoffice product. The older consultancy/substrate pathway is being deprecated as the main architecture, while its transfer capabilities should survive and be integrated into the outward-facing Zoffice package.

**Architectural decision:**
- Canonical product: `Zoffice/`
- Local safety posture: do **not** install Zoffice into this live Zo
- Export posture: the outward package must include substrate/zo2zo transfer capability
- Deprecation posture: older consultancy/substrate docs and assets remain as references, but no longer define the primary deployment story
- **Supersession posture:** this build is the convergence build. Its output should supersede prior partial or previously complete Zoffice/Rice/substrate deployment stories **except** for the core functionality of this live device (`N5/`, device-specific operating machinery, and other local system internals not intended for export).

---

## Supersession Goal

This build exists to collapse a scattered architecture into one canonical external product surface.

### What this version should supersede
- The older **consultancy-stack deployment story** in `N5/builds/consulting-zoffice-stack/`
- The fragmented **Rice stream plans as deployment entrypoints** (`n5os-rice`, `rice-core`, `rice-capabilities`, `rice-staff`, `rice-integration`) while preserving them as provenance and architectural source material
- The idea that `zoputer-substrate/` is the main product shell for deployment

### What this version should NOT supersede
- The core functionality of this device and its operating substrate (`N5/`, local automations, personal workspace structures, and other live-system machinery not meant to ship as Zoffice)
- Local factory/reference tooling that exists solely to help produce or transfer the exported package

### Supersession rule
After this build, a future builder answering “what do I deploy?” should be able to answer:
**Deploy the versioned release produced from `Zoffice/`. Use older Rice and substrate artifacts only as reference, provenance, or local factory support.**

---

## Open Questions

All blocking questions resolved in chat for this build:
- [x] Build slug: `zoffice-externalization`
- [x] Stop point: versioned release folder, not transfer/deployment
- [x] Exported package includes substrate transfer capability
- [ ] Exact version tag for the next release folder (derive from current RC state during execution)
- [ ] Final validation checklist wording for human review gate

---

## Checklist

### Phase 0: Supersession framing
- ☐ Define exactly which prior artifacts are superseded, absorbed, retained-as-reference, or excluded
- ☐ Record the non-goal boundary around this device’s core functionality
- ☐ Produce canonical supersession artifact
- ☐ Test: a future builder could identify one deployable source of truth without reading older build plans first

### Phase 1: Audit and reconciliation
- ☐ Audit existing Rice/Zoffice/substrate artifacts and reconcile them into one canonical external deployment story
- ☐ Identify which substrate assets must be absorbed into exported Zoffice versus left as local-only references
- ☐ Produce architecture reconciliation artifact
- ☐ Test: no contradiction remains between `Zoffice/`, Rice build summaries, and substrate transfer docs

### Phase 2: Product hardening and packaging path
- ☐ Close packaging gaps in `Zoffice/` for external release readiness
- ☐ Ensure zo2zo/substrate transfer capability is represented inside exported Zoffice
- ☐ Produce or update packaging/release scripts and manifests as needed
- ☐ Test: release creation runs cleanly to a new versioned folder without mutating prior releases

### Phase 3: Validation and release folder creation
- ☐ Run health/smoke validation against the externalized package surface
- ☐ Create a new versioned release folder under `Zoffice/releases/`
- ☐ Produce a review artifact describing contents, deltas from prior RCs, and validation results
- ☐ Stop before transfer to Zoputer

---

## Existing Build Context (must be referenced, not reinvented)

### Canonical prior architecture builds

| Build | Contribution | Status | Post-build disposition |
|------|--------------|--------|------------------------|
| `n5os-rice` | Defined Troika/fractal architecture and Layer 0/1/2 product model | complete | provenance / architectural reference |
| `rice-core` | Created `Zoffice/` skeleton, configs, database, release machinery direction | complete | superseded as standalone entrypoint; absorbed into canonical product |
| `rice-capabilities` | Implemented 8 capabilities including `zo2zo` inside `Zoffice/capabilities/` | complete | superseded as standalone entrypoint; absorbed into canonical product |
| `rice-staff` | Created file-based starter staff definitions | complete | superseded as standalone entrypoint; absorbed into canonical product |
| `rice-integration` | Wired routing/config to make Layer 1 coherent | complete | superseded as standalone entrypoint; absorbed into canonical product |
| `consulting-zoffice-stack` | Earlier consultancy/substrate architecture | legacy/reference | explicitly deprecated as deployment story |

### Key current product surfaces
- `Zoffice/` — canonical external product source
- `Zoffice/releases/v2.0.0-rc1/` and `Zoffice/releases/v2.0.0-rc2/` — previous release artifacts
- `Zoffice/scripts/create_release_bundle.py` — existing release bundle script
- `Zoffice/capabilities/zo2zo/` — existing internal zo2zo capability surface
- `zoputer-substrate/` — legacy/supporting substrate source containing transferable relay/sanitizer/bootstrap patterns

---

## Phase 1: Audit and reconciliation

### Affected Files
- `N5/builds/zoffice-externalization/PLAN.md` - UPDATE - canonical build plan
- `N5/builds/zoffice-externalization/artifacts/supersession-plan.md` - CREATE - canonical supersession and legacy-disposition plan
- `N5/builds/zoffice-externalization/artifacts/architecture-reconciliation.md` - CREATE - canonical story tying Rice + Zoffice + substrate together
- `N5/builds/zoffice-externalization/artifacts/substrate-absorption-map.md` - CREATE - what gets absorbed vs retained as local reference
- `Zoffice/` - READ ONLY during audit
- `zoputer-substrate/` - READ ONLY during audit
- `N5/builds/n5os-rice/PLAN.md` - READ ONLY
- `N5/builds/rice-core/PLAN.md` - READ ONLY
- `N5/builds/rice-capabilities/PLAN.md` - READ ONLY
- `N5/builds/rice-staff/PLAN.md` - READ ONLY
- `N5/builds/rice-integration/PLAN.md` - READ ONLY
- `N5/builds/consulting-zoffice-stack/PLAN.md` - READ ONLY

### Changes

**1.0 Define supersession boundary:**
Document the precise relationship between the new release and prior work. Distinguish four dispositions for every major legacy artifact family:
- **absorbed** into canonical `Zoffice/`
- **superseded** as a standalone build/deployment path
- **retained as reference/provenance**
- **excluded** because it belongs to this live device rather than the exportable office product

**1.1 Reconcile the deployment narrative:**
Document clearly that the old consultancy/substrate pathway was an exploratory predecessor, while the Rice builds established `Zoffice/` as the actual Layer 1 product. Clarify how substrate survives: not as the main product shell, but as the transfer/export capability already conceptually represented by `zo2zo`, with select assets folded into the exported release story.

**1.2 Build the substrate absorption map:**
Inventory substrate assets into three buckets:
- absorb into exported Zoffice now
- leave as local factory/reference tooling
- deprecate from deployment story

**1.3 Define local-vs-export boundary:**
This machine remains the build factory. The exported release must be self-describing and portable. No step in this build should require system-level persona installation or mutation of va’s live Zo configuration.

### Unit Tests
- Reconciliation artifact cites concrete prior builds and concrete current paths
- Every substrate component referenced lands in exactly one disposition bucket
- Narrative is internally consistent with V’s stated goal of external deployment first
- Supersession artifact explicitly excludes this device’s core operating functionality from deprecation/absorption scope

---

## Phase 2: Product hardening and packaging path

### Affected Files
- `Zoffice/scripts/create_release_bundle.py` - UPDATE if needed - release creation path
- `Zoffice/BOOTLOADER.md` - UPDATE if needed - external deployment story
- `Zoffice/MANIFEST.json` - UPDATE if needed - release/package metadata
- `Zoffice/capabilities/zo2zo/**` - UPDATE if needed - integrated transfer capability docs/code/config
- `Zoffice/releases/<next-version>/` - CREATE in Phase 3 only
- `N5/builds/zoffice-externalization/artifacts/package-readiness-checklist.md` - CREATE

### Changes

**2.1 Harden the package story:**
Ensure the package can be understood as an external release without requiring the older substrate docs to explain it.

**2.2 Integrate substrate transfer capability into exported Zoffice:**
Use the existing `zo2zo` capability as the canonical in-package home for transfer behavior. Where substrate contains still-useful relay/sanitizer/bootstrap elements, either copy/adapt them into `Zoffice/` or explicitly document why the current `zo2zo` capability already supersedes them.

**2.3 Version without overwrite (P35):**
Any release output must go to a new versioned folder. Prior RC folders remain immutable.

### Unit Tests
- Release script can dry-run the next version cleanly
- Package readiness checklist can be answered from current artifacts, not guesswork
- Bootloader/manifest do not depend on legacy-only terminology to explain deployment

---

## Phase 3: Validation and release folder creation

### Affected Files
- `Zoffice/scripts/healthcheck.py` - READ/RUN
- `Zoffice/scripts/layer2_smoke_test.py` - READ/RUN if applicable
- `Zoffice/releases/<next-version>/` - CREATE - final reviewable release folder
- `N5/builds/zoffice-externalization/artifacts/release-review.md` - CREATE - validation + review summary
- `N5/builds/zoffice-externalization/STATUS.md` - CREATE/UPDATE - build progress

### Changes

**3.1 Validate before packaging:**
Run the relevant product-level checks against the externalized surface. Focus on release readiness, not live installation into va.

**3.2 Create release folder:**
Generate the next versioned release folder under `Zoffice/releases/` and stop there.

**3.3 Prepare review gate:**
Summarize contents, known caveats, what changed since prior RCs, and the exact next step for human validation before transfer to Zoputer.

### Unit Tests
- New release folder exists and is distinct from rc1/rc2
- Release folder includes manifest/checksum/bundle output expected by release machinery
- Release review artifact accurately reflects what was created
- No transfer/deployment actions executed beyond local release creation

---

## Success Criteria

1. The build produces a single coherent answer to “what is the deployable Zoffice product?”
2. `Zoffice/` is confirmed and documented as the canonical external product source
3. Substrate transfer capability is either absorbed into exported Zoffice or explicitly superseded by integrated `zo2zo` capability with no ambiguity
4. A new versioned release folder is created under `Zoffice/releases/`
5. A human can review the release folder and validation artifacts without needing to inspect older consultancy build plans
6. No system-level installation into va’s live Zo occurs during this build
7. The build explicitly supersedes prior partial/legacy deployment stories without claiming to replace the core operating functionality of this device

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Reintroducing the old consultancy architecture by accident | Reconciliation artifact explicitly demotes legacy pathway to reference status |
| Package depends on undocumented substrate pieces | Absorption map and package readiness checklist make dependency visibility explicit |
| Release output overwrites prior RC artifacts | New version folder only; no in-place edits to rc1/rc2 |
| Validation implies install-safety on va rather than export-readiness | Keep tests scoped to package/release surface, not live-system install |

## Learning Landscape

### Build Friction Recommendation
**Recommended:** standard-to-high
**Rationale:** This is a consequential packaging and architecture-convergence build. The main failure mode is not coding difficulty but shipping an ambiguous product boundary.

### Decision Points
- DP-1: Which substrate assets must be physically absorbed into `Zoffice/` now vs merely documented as superseded?
- DP-2: What is the correct next release tag after `v2.0.0-rc2`?
- DP-3: Which validation steps are sufficient to declare “review-ready external package” without doing transfer/deployment?
