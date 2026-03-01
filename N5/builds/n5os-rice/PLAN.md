---
created: 2026-02-21
last_edited: 2026-02-21
version: 1
provenance: con_MeSXGFyaIZ55GjbZ
type: build_plan
status: complete
---
# N5OS-Rice — Master Architecture Plan

**Objective:** Define the Troika Architecture (Office → Employee → Capability), the full employee stack specification, and the capability infrastructure manifest that turns N5OS from a personal operating system into a replicable product ("Zoffice").

**Trigger:** V's insight that "the same pattern applies at every level" — the office has its version of SOUL, MEMORY, HEARTBEAT, etc., AND each individual employee gets their own version of the full stack. This is the architectural formalization of that fractal pattern.

**Key Design Principle:** This is Stream 1 (Architecture & Strategy) of a 4-stream Rice build. It produces NO code — only the architectural specifications that Streams 2-4 implement.

---

## Open Questions

All resolved during prior architecture session. Decisions carried forward here as FINAL.

---

## The Four Rice Streams

This plan governs **Stream 1 only**. The other streams have their own build workspaces:

| Stream | Slug | Purpose | Status |
|--------|------|---------|--------|
| **1. Architecture & Strategy** | `n5os-rice` (this build) | Define Troika, Employee Stack, Capability Manifest | **Active** |
| 2. Foundation & Infrastructure | `rice-core` | Zoffice/ skeleton, config schemas, office.db | Planned (depends on Stream 1) |
| 3. Capabilities | `rice-capabilities` | 8 infrastructure modules (Security, Memory, Ingestion, etc.) | Planned (depends on Stream 2) |
| 4. Staff & Integration | `rice-staff` + `rice-integration` | 3 starter employees, routing, unified installer, E2E validation | Planned (depends on Streams 2+3) |

**Dependency chain:** Stream 1 → Stream 2 → Stream 3 → Stream 4

Stream 2-4 plans already exist at their respective build workspaces with full phase breakdowns, MECE validation, and worker briefs. This plan does NOT duplicate that content — it defines the architectural foundation they all reference.

---

## Checklist

### Phase 1: Architecture Brief (Troika Definition)
- ☑ Define the 3-tier Troika model (Office → Employee → Capability)
- ☑ Map each tier to Zo primitives
- ☑ Define the "What Carries Over" table (va patterns → Zoffice equivalents)
- ☑ Define config surface for each tier
- ☑ Document the Layered Product Model (Layer 0 → Layer 1 → Layer 2)
- ☑ Artifact: `artifacts/architecture-brief.md`

### Phase 2: Employee Stack Specification
- ☑ Define the fractal stack (what every employee gets)
- ☑ Map stack components to Zo primitives and file structures
- ☑ Define the 3 starter employees and their differentiators
- ☑ Define employee lifecycle (onboarding → active → evaluation → retirement)
- ☑ Define the autonomy model (4-tier threshold system)
- ☑ Artifact: `artifacts/employee-stack-spec.md`

### Phase 3: Capability Infrastructure Manifest
- ☑ Define all 8 capability layers with office metaphors
- ☑ Map each to Zo primitives
- ☑ Audit current maturity across va and zoputer
- ☑ Identify gaps between current state and target
- ☑ Artifact: `artifacts/capability-manifest.md`

---

## Phase 1: Architecture Brief

### Affected Files
- `N5/builds/n5os-rice/artifacts/architecture-brief.md` - CREATE - Troika Architecture definition

### Changes

**1.1 Troika Architecture Definition:**
The core architectural insight: N5OS-Rice organizes everything into three nested tiers — the Office (the whole Zo instance), the Employee (a persona with its own stack), and the Capability (an infrastructure module any employee can use). This is the "office metaphor" made concrete.

**1.2 Layered Product Model:**
- **Layer 0 (n5os-bootstrap):** Raw Zo Computer with N5 prefs, scripts, and operational machinery. Already exists on va.
- **Layer 1 (Zoffice base install):** The office skeleton — directory structure, config schemas, database, starter staff, capabilities. This is what Rice builds.
- **Layer 2 (Instance customization):** Branded employees (Zozie, Zoren), custom knowledge bases, domain-specific capabilities. Per-client work.

**1.3 "What Carries Over" Mapping:**
Systematic mapping of what exists on va today and how it transforms into the Zoffice product. Not a copy — a principled adaptation.

### Unit Tests
- Architecture brief is internally consistent (no contradictions between tiers)
- Every Zo primitive referenced actually exists (personas, rules, agents, etc.)
- Layered model is clear enough to explain to a non-technical person

---

## Phase 2: Employee Stack Specification

### Affected Files
- `N5/builds/n5os-rice/artifacts/employee-stack-spec.md` - CREATE - Full employee stack spec

### Changes

**2.1 The Fractal Stack:**
V's key insight: "the office has its version, AND each employee gets their own version." This means every employee has its own SOUL (persona.yaml), MEMORY (knowledge/), HEARTBEAT (evaluation cycle), PREFS (system-prompt.md), and TOOLS (tools/manifest.yaml).

**2.2 Autonomy Model:**
The 4-tier confidence threshold system (auto_act → act_and_notify → escalate_to_parent → escalate_to_human) that governs what employees can do independently.

**2.3 Starter Employee Profiles:**
Receptionist (front door), Chief of Staff (operations), Librarian (knowledge). Generic roles, not branded personas — branding is Layer 2.

### Unit Tests
- Stack spec covers all components V mentioned
- Autonomy model is clearly defined with concrete thresholds
- Each starter employee has distinct responsibilities (no MECE overlap)

---

## Phase 3: Capability Infrastructure Manifest

### Affected Files
- `N5/builds/n5os-rice/artifacts/capability-manifest.md` - CREATE - 8 capability layers

### Changes

**3.1 The 8 Capabilities:**
Security, Memory, Ingestion, Communication, Orchestration, Zo2Zo, Publishing, HR. Each defined with office metaphor, Zo primitives, current maturity, and gaps.

**3.2 Current State Audit:**
Honest assessment of what actually exists today on va and zoputer for each capability. Not aspirational — factual. Per P16 (Accuracy Over Sophistication).

### Unit Tests
- All 8 capabilities defined
- Each has: definition, metaphor, primitives, maturity, gaps
- Maturity assessments match what I actually found in the workspace audit

---

## Success Criteria

1. `artifacts/architecture-brief.md` defines the Troika model clearly enough that Stream 2 can build from it without clarification
2. `artifacts/employee-stack-spec.md` specifies every component of the employee stack with enough detail to generate file structures
3. `artifacts/capability-manifest.md` honestly audits current maturity and identifies all gaps
4. All three documents reference each other consistently (no terminology drift)
5. Stream 2-4 plans are consistent with the architecture defined here

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Architecture brief becomes too abstract to implement | Each concept maps to concrete Zo primitives and file paths |
| Capability manifest inflates maturity (P16 violation) | Audit based on what actually exists in workspace, not what was planned |
| Employee stack spec overlaps with rice-staff PLAN.md | This spec defines the WHAT; rice-staff defines the HOW. No implementation details here. |
| Terminology drift between documents | Shared glossary in architecture brief; other docs reference it |
| Stream 2-4 plans become stale relative to this architecture | Architecture brief is the SSOT (P02); stream plans reference it |

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** minimal
**Rationale:** This is pure architecture and specification writing — no code, no infrastructure changes. The concepts are V's own insights being formalized. Minimal friction keeps momentum.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| Fractal/recursive architecture | Practitioner | System Design | Low (V designed this) |
| Office-as-software metaphor | Practitioner | Product | Low (V's original insight) |
| Layered product model (L0/L1/L2) | Familiar | Product Engineering | Medium |
| Autonomy thresholds for AI agents | Practitioner | AI Governance | Low (V designed autonomy.yaml) |
| Capability-based architecture | Exploring | Software Architecture | Medium |

### Decision Points

All major decisions were resolved in the prior architecture session. No open decision points remain for Stream 1.

### Drop Engagement Tags

This build produces 3 specification documents — no worker decomposition needed. V writes (or reviews) the architecture directly.

---

## Relationship to Existing Builds

### Builds That Feed Into Rice
- `consulting-zoffice-stack` — Early exploration of the Zoffice concept
- `zoputer-autonomy-v2` — Autonomy model development
- `dark-factory-elevation` — Scenario-based validation (adopted by rice-integration)
- `trusted-third-party-zo2zo-deploy-readiness` — Zo2Zo communication protocol

### Builds Rice Supersedes
- None. Rice is additive — it creates the Zoffice product layer ON TOP of existing N5OS.

### Builds That Depend on Rice
- Any future "client Zoffice deployment" work
- Any "Layer 2 customization" work (branded employees, custom capabilities)
