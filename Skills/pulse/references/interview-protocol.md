---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_T0QGg2ryaDjCTxVj
---

# Pulse Interview Protocol

Pre-build interview to decompose work into Streams and Drops.

## When to Use

Before any build that will use Pulse orchestration.

## The Four Questions

### 1. What are we building?
- Concrete deliverables (files, features, systems)
- Success criteria
- Out of scope

### 2. What are the independent tracks?
These become **Streams** (parallel execution).
- Can run simultaneously
- No dependencies between them
- Examples: backend vs frontend, different features

### 3. What must happen in sequence?
These become **Currents** (sequential chains within a Stream).
- A feeds into B feeds into C
- Order matters
- Examples: schema → API → tests

### 4. What are the risks?
- Technical unknowns
- External dependencies
- Potential blockers

## Output

Generate `meta.json` and Drop briefs in `N5/builds/<slug>/`.

## Decomposition Patterns

### Layer Cake (most common)
```
Stream 1: Foundation (schema, types, config)
Stream 2: Core (business logic, APIs)
Stream 3: Surface (UI, integrations)
```

### Feature Slices
```
Stream 1: Feature A (full stack)
Stream 2: Feature B (full stack)
Stream 3: Feature C (full stack)
```

### Pipeline
```
Current 1: Ingest → Transform → Validate → Store
```

## Anti-Patterns

- **Too granular**: >5 Drops per Stream = overhead exceeds value
- **False parallelism**: Drops that actually depend on each other
- **Missing dependencies**: Drop assumes artifact that doesn't exist yet
