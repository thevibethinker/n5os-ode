---
created: 2026-03-06
last_edited: 2026-03-06
version: 1.0
provenance: con_YPjMOLNUUzDX4QqI
---

# Plan: N5 OS Architecture Meta-Build

**Objective:** Produce a comprehensive, implementation-ready architecture and migration plan for restructuring N5 into a cleaner kernel/services/zoffice/apps model while the live system remains operational.

**Trigger:** V requested a Pulse meta-build that prepares concrete implementation specs per subsystem and establishes a safe protocol for adapting the filesystem and architecture while "building the plane as we fly it."

**Mode:** commit
**Blast Radius:** large
**Build Type:** planning meta-build

---

## North Star

Restructure N5 into a durable operating substrate built atop Zo with:
- a small explicit kernel
- typed services with stable interfaces
- Zoffice as higher-order organizational framework
- domain applications separated from infrastructure
- commitment/work-object modeling as the canonical execution primitive
- safe migration patterns for a live, in-use filesystem and runtime

---

## Scope

### In Scope
- Canonical target architecture for N5 OS
- Canonical file/folder model
- Subsystem-by-subsystem implementation specs
- Migration protocol for live-system filesystem adaptation
- Typed object model and registry plan
- Safety, versioning, and rollout discipline
- Identification of which current systems map to kernel vs services vs zoffice vs apps
- Planning builds that can later be launched in separate conversations

### Out of Scope
- Performing the restructuring
- Moving production files
- Rewiring services during this build
- Deprecating live systems without explicit follow-up implementation builds

---

## Open Questions

- [ ] Should Zoffice remain branded separately from N5 in the final public/exported framing, or live as a named framework inside N5 OS?
- [ ] Which current subsystem, if any, should be explicitly excluded from the first implementation wave because maturity is too low?
- [ ] How aggressively should public/exportable `n5os-core` track the redesigned architecture versus lagging behind the private instance?

---

## Meta-Build Deliverables

1. `N5/builds/n5os-architecture-meta-build/artifacts/architecture-review.md`
2. `N5/builds/n5os-architecture-meta-build/artifacts/canonical-system-map.md`
3. `N5/builds/n5os-architecture-meta-build/artifacts/live-migration-protocol.md`
4. `N5/builds/n5os-architecture-meta-build/artifacts/object-model-and-registries.md`
5. `N5/builds/n5os-architecture-meta-build/artifacts/subsystem-builds-index.md`
6. Planning briefs for child planning builds under `drops/`
7. `meta.json` and `STATUS.md` suitable for Pulse orchestration

---

## Build Strategy

This is a **meta-build**. It does not directly restructure N5. It generates the planning substrate for later subsystem builds.

### Streams
- **Stream 1 — Architecture Core:** kernel/services/zoffice/apps target model
- **Stream 2 — Live Migration Safety:** safe protocol for filesystem and runtime adaptation
- **Stream 3 — Typed Object + Registry Model:** commitments, work objects, registries, contracts
- **Stream 4 — Subsystem Planning:** concrete child-build specs per subsystem

### Child Planning Builds to Define
- `n5-kernel-foundation`
- `n5-service-layer-refactor`
- `n5-work-object-model`
- `n5-registry-system`
- `n5-cognition-service-hardening`
- `n5-runtime-state-boundary`
- `n5-zoffice-framework-shaping`
- `n5-app-boundary-and-domain-migration`
- `n5-git-and-artifact-hygiene`

---

## Safety Doctrine for This Build

Because N5 is live and actively used, architecture change must follow these principles:

1. **Version, don’t overwrite** — new canonical paths and adapters first; old paths retired later.
2. **Dual-run where needed** — allow old and new systems to coexist behind thin compatibility layers.
3. **Source/state/runtime/records separation before moves** — classification precedes migration.
4. **Promote interfaces before internals** — stabilize entrypoints and contracts before rearranging implementations.
5. **Prefer wrappers/adapters over in-place surgery** during active use.
6. **Use planning builds to isolate risk by subsystem.**

---

## Files to Read

| File | Why Read It |
|------|-------------|
| `AGENTS.md` | Root operating contract and build governance |
| `Skills/pulse/SKILL.md` | Canonical orchestration model |
| `Skills/pulse/references/drop-brief-template.md` | Drop brief structure |
| `Skills/pulse/references/interview-protocol.md` | Stream/current/checkpoint design |
| `N5/scripts/session_state_manager.py` | Conversation state kernel primitive |
| `N5/scripts/n5_load_context.py` | Context injection primitive |
| `N5/scripts/build_contract_check.py` | Build gating mechanism |
| `N5/scripts/n5_safety.py` | Safety scanning primitive |
| `N5/scripts/agent_conflict_gate.py` | Agent governance primitive |
| `N5/scripts/port_registry.py` | Infrastructure allocation primitive |
| `N5/task_system/task_registry.py` | Current action/task substrate |
| `N5/cognition/n5_memory_client.py` | Semantic memory substrate |
| `N5/config/user_preferences.yaml` | Preference/context registry |
| `N5/config/canonical_locations.json` | Canonical placement logic |
| `N5/scripts/n5_export_core.py` | Core export boundary |

---

## Planned Phases

### Phase 1 — Current-State Architecture Extraction
- Produce system decomposition: kernel, services, zoffice, apps, state, records, artifacts
- Identify mature vs immature layers
- Enumerate key risks and migration constraints

### Phase 2 — Future-State Canonical Design
- Define target architecture
- Define object model and registry system
- Define canonical file/folder set

### Phase 3 — Live Migration Protocol
- Define safe path adaptation protocol
- Define interface stabilization, wrappers, compatibility windows, dual-run patterns
- Define sequencing and rollback strategy

### Phase 4 — Child Planning Builds
- Create implementation-ready planning briefs for each major subsystem build
- Include scenarios, checkpoints, dependencies, and expected artifacts

---

## Success Criteria

- [ ] Canonical architecture clearly separates kernel, services, zoffice, apps, state, runtime, and records
- [ ] Live migration protocol is explicit, safe, and reversible
- [ ] Typed work-object / commitment model is specified
- [ ] Registry system is specified with clear boundaries and intended consumers
- [ ] Child planning builds are concrete enough to launch in separate conversations
- [ ] All auto-spawn Drop briefs include `## Scenarios` and `spec_completeness: full`

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Planning drift into implementation | Keep all outputs in build artifacts and planning briefs only |
| Overdesign detached from current system | Ground each recommendation in observed existing subsystems |
| Unsafe future migration plan | Write a dedicated live-migration protocol with dual-run/adapters/versioning |
| Child builds overlap or leave gaps | Use subsystem build index and explicit boundary definitions |
| File-system change breaks live workflows | Recommend classification and wrappers before physical movement |

---

## Checkpoints

### C1 — Architecture Coherence Check
Validate the target architecture is internally consistent and grounded in current N5 reality before producing subsystem planning builds.

### C2 — Migration Safety Check
Validate the live migration protocol protects runtime continuity, operator clarity, and rollback ability.

---

## Notes

This build should bias toward elegance and canonicalization, but only through migration-safe design suitable for an active operating system under live use.
