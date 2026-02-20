---
created: 2026-02-18
last_edited: 2026-02-18
version: "1.0.0"
provenance: n5os-ode-v2-upgrade
---

# Building Fundamentals (P35–P39)

A higher-level conceptual bundle referenced by Builder and Architect personas. These five principles govern how artifacts are created, tracked, and composed during builds.

> **Note:** These P35–P39 building fundamentals are a conceptual bundle distinct from the individual principle YAML files that share some of these numbers (e.g., P35\_data\_format\_selection.yaml, P36\_orchestration\_pattern.yaml, P37\_refactor\_pattern.yaml). The YAML files capture the individual operational principles; this document captures the integrated philosophy for build-time work.

---

## P35: Version, Don't Overwrite

**Core idea:** Input artifacts are immutable. Transforms create new files.

Never modify source inputs in place. Every processing step should read from an input and write to a new output. This ensures you can always trace back to the original, re-run any step, and recover from errors without data loss.

**In practice:**
- Raw inputs live in a `source/` or `inputs/` directory and are never modified
- Each transform stage writes to a new location (e.g., `processed/`, `output/`)
- Versioned filenames or directories when multiple iterations exist
- If you need to "update" an input, create a new version alongside the original

**Why it matters:** When inputs are mutable, a failed transform can corrupt the source, making recovery impossible. Immutable inputs mean every stage is independently re-runnable.

---

## P36: Make State Visible

**Core idea:** Hidden state causes bugs. Declare dependencies and validate state before proceeding.

Every component should explicitly declare what it needs and what it produces. No implicit dependencies, no side-channel communication, no "it works because X happened to run first."

**In practice:**
- Scripts declare their inputs and outputs (via CLI args, config files, or frontmatter)
- State files (SESSION\_STATE.md, meta.json) are readable artifacts, not hidden memory
- Validate preconditions at the start of each step: are the required files present? Is the state what we expect?
- When state is wrong, fail loudly rather than producing incorrect output

**Why it matters:** Hidden state is the #1 cause of "works on my machine" and "worked yesterday" bugs. Visible state is debuggable state.

---

## P37: Design as Pipelines

**Core idea:** Input → Transform → Output. Each stage is independently testable and re-runnable.

Structure work as a sequence of discrete stages, each with clear inputs and outputs. Any stage can be re-run in isolation without re-running the entire pipeline.

**In practice:**
- Each stage reads from a well-defined input location and writes to a well-defined output location
- Stages are connected by their file system contracts, not by shared memory or global state
- A failed stage can be fixed and re-run without starting over
- Pipeline stages can be parallelized when they have no dependencies on each other

**Why it matters:** Monolithic scripts that do everything in one pass are fragile — a failure at step 47 means re-running steps 1–46. Pipelines localize failures and enable incremental progress.

---

## P38: Isolate by Default, Parallelize Proactively

**Core idea:** Workers don't share mutable state. When a task has >5 independent items requiring non-trivial work, recommend parallel orchestration.

Independence is the prerequisite for parallelism. If workers share state, parallelism creates race conditions. If workers are isolated, parallelism is safe and fast.

**In practice:**
- Each worker (drop, script invocation, parallel task) operates on its own input and writes its own output
- No shared mutable files, no locks, no coordination during execution
- Orchestrator assembles results after all workers complete
- Default recommendation: >5 independent non-trivial items → parallel execution
- Simple file operations (rename, move) don't need parallelization — only substantive per-item work does

**Why it matters:** Sequential processing of independent items wastes time. Parallel processing with shared state wastes correctness. Isolated parallel processing gets both right.

---

## P39: Audit Everything

**Core idea:** Every output must be traceable — provenance frontmatter, logs, and commits.

When you look at any artifact in the system, you should be able to answer: Who created this? When? From what inputs? As part of what process? This traceability is not overhead — it is the mechanism that makes complex systems debuggable.

**In practice:**
- Every generated file includes provenance frontmatter (`created`, `provenance`, `version`, `source`)
- Build processes log their actions (what was processed, what was skipped, what failed)
- Commits reference the build or task that produced them
- Outputs link back to their inputs so the full chain is reconstructable

**Why it matters:** Without audit trails, you cannot debug failures, verify correctness, or understand evolution. With them, any problem is traceable to its source.

---

## Summary Table

| # | Principle | One-Liner |
|---|-----------|-----------|
| P35 | Version, Don't Overwrite | Inputs immutable; transforms create new files |
| P36 | Make State Visible | Declare dependencies; validate before proceeding |
| P37 | Design as Pipelines | Input → Transform → Output; each stage re-runnable |
| P38 | Isolate & Parallelize | Workers don't share state; Pulse for >5 items |
| P39 | Audit Everything | Every output traceable via provenance, logs, commits |
