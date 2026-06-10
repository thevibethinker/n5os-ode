---
name: pulse-interview
description: >
  Pre-build interview that decomposes a new build into Streams, Currents,
  Checkpoints, and Scenarios before Pulse planning. Use before Architect writes
  PLAN.md whenever a build needs structured decomposition.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0.0"
created: 2026-06-10
last_edited: 2026-06-10
version: 1.0
provenance: con_sQ03t9FFBWIVZTXO
---

# Pulse Interview

Pre-build interview to decompose work into Streams, Currents, Checkpoints, and Scenarios.

## When to Use

Use before any build that will use Pulse orchestration.

## The Six Questions

### 1. What are we building?
- Concrete deliverables
- Success criteria
- Out of scope

### 2. What are the independent tracks?
These become **Streams**.
- Can run simultaneously
- No dependencies between them
- Examples: backend vs frontend, different features

### 3. What must happen in sequence?
These become **Currents**.
- A feeds into B feeds into C
- Order matters
- Examples: schema → API → tests

### 4. What are the risks?
- Technical unknowns
- External dependencies
- Potential blockers

### 5. Where are the checkpoints?
These are strategic quality gates at high-risk junctures.

**Identify build type:**
- API build? Data pipeline? Frontend? Integration?
- What typically goes wrong with this type?

**Identify high-risk handoffs:**
- Where does one Drop's bad output cascade to downstream Drops?
- Where must multiple Drops' outputs stay consistent?

**Place checkpoints:**
- 1-2 checkpoints per build is typical
- Each checkpoint gets a specific verification brief

| Build Type | Common Checkpoint Placements |
|------------|------------------------------|
| API | After schema, before frontend integration |
| Data Pipeline | After ingest, after transform |
| Frontend | After components, before deploy |
| Integration | After both sides built, before E2E |

### 6. What should V learn from this build?
These inform the Learning Landscape in the plan.
- Which technical concepts are new?
- Which decisions have the highest pedagogical value?
- What level of engagement is desired?
- Are there concepts to deep dive into?

### 7. What does "working" look like?
These become **Scenarios** in each Drop brief.

For each major deliverable, extract:
- Happy path
- Edge cases
- Failure modes

**Format each scenario as:**
```text
S1: <Descriptive name>
  Given: <Initial state or precondition>
  When: <Action or trigger>
  Then: <Expected observable outcome>
  Verify: <Executable command or "LLM: <what to check>">
```

**Verify clause guidance:**
- Prefer executable checks
- When execution isn't possible, use LLM judgment
- Each scenario should be independently evaluable

**Target:** 3-5 scenarios per Drop. More for complex Drops, fewer for simple ones.

## Output

Generate in `N5/builds/<slug>/`:
- `meta.json` — build metadata with streams, drops, checkpoints
- `drops/D*.md` — Drop briefs
- `drops/C*.md` — Checkpoint briefs

## Decomposition Patterns

### Layer Cake
- Stream 1: Foundation
- Stream 2: Core
- Stream 3: Surface

### Feature Slices
- Stream 1: Feature A
- Stream 2: Feature B
- Stream 3: Feature C

### Pipeline
- Current 1: Ingest → Checkpoint → Transform → Checkpoint → Validate → Store

## Anti-Patterns

- Too granular: >5 Drops per Stream
- False parallelism
- Missing dependencies
- No checkpoints
- Over-checkpointing: >3 checkpoints
