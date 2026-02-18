---
created: 2026-01-29
last_edited: 2026-01-29
version: 1.0
provenance: con_if5c6C7gXdINkUK1
---

# Building Fundamentals (P35-P39)

Five core principles derived from deep programming concepts, adapted for N5/Zo architecture.

**Origin:** Video deep-dive + synthesis session (Jan 2026)

---

## P35: Version, Don't Overwrite

**Principle:** When data might be referenced later or by multiple processes, create new versions rather than modifying in place.

**Pattern:**
- Input artifacts are **immutable** — never modify source data
- Output artifacts are **new files** — transforms produce new artifacts, not mutations
- History is **preserved** — append-only sections, versioned filenames, or git commits

**When to Apply:**
- Processing source data (briefs, transcripts, raw files)
- Multi-stage pipelines where stages may need to re-run
- Any artifact that could be referenced by downstream processes

**Examples:**
- Careerspan decomposer: input brief → new YAML files (never modifies input)
- Meeting ingestion: transcript → recap → blocks (each stage creates new artifacts)
- SESSION_STATE.md: progress is appended, not overwritten

**Anti-Pattern:**
```
❌ Modify source_brief.md during processing
✓ Create decomposed_brief_v1.yaml from source_brief.md
```

**Benefits:**
- Bugs in processing never corrupt source data
- Any stage can be re-run from its inputs
- Debugging is easier — you can compare input vs output

---

## P36: Make State Visible

**Principle:** Hidden state causes bugs. If a system "remembers" something between runs, that memory should be visible, inspectable, and managed.

**Pattern:**
- Declare state dependencies explicitly at the top of scripts
- Validate state exists before proceeding
- Log state changes explicitly (not silently)

**When to Apply:**
- Any script that reads files it didn't create this run
- Any workflow that depends on "current" anything
- Any process that writes to locations other processes read

**Skill State Declaration Template:**
```markdown
## State Dependencies

**Reads from:**
- `path/to/file.json` (expects: field X)
- `path/to/state.md` (expects: section Y)

**Writes to:**
- `path/to/output/` (creates: new files per run)
- `path/to/log.jsonl` (appends: structured entries)

**Failure mode if state missing:** [describe]
```

**Examples:**
- SESSION_STATE.md — explicit conversation state
- meta.json in builds — explicit build progress
- n5_protect markers — explicit "don't touch" signals

**Anti-Pattern:**
```
❌ Script silently fails because expected file doesn't exist
✓ Script checks for file, reports clear error, exits gracefully
```

**Benefits:**
- Debugging is possible — you can inspect state
- Failures are clear — missing state is reported
- Systems are trustable — no "magic" hidden behavior

---

## P37: Design as Pipelines

**Principle:** Design workflows as explicit pipelines with clear input → transform → output stages. Each stage should be independently testable and recoverable.

**Pattern:**
```
Stage 1: [Input Source] → [Artifact A]
Stage 2: [Artifact A] → [Transform] → [Artifact B]
Stage 3: [Artifact B] → [Transform] → [Output]
```

**Rules:**
1. Each stage reads ONLY its declared inputs
2. Each stage writes ONLY its declared outputs
3. Intermediate artifacts are inspectable
4. Any stage can be re-run from its inputs (idempotency)
5. Stages don't "reach back" to earlier inputs

**When to Apply:**
- Multi-step data processing
- Build orchestration (Pulse streams)
- Meeting ingestion, content pipelines

**Examples:**
- Meeting pipeline: Recording → Transcript → Recap → Blocks
- Pulse builds: Brief → Drop execution → Deposit → Synthesis
- Research: Sources → Notes → Synthesis → Output

**Anti-Pattern:**
```
❌ Stage 3 directly reads original input (skipping stage 2 output)
✓ Stage 3 reads only stage 2's output
```

**Benefits:**
- Partial failures are recoverable — re-run just the failed stage
- Testing is isolated — each stage can be tested independently
- Debugging is localized — issues are contained to specific stages

---

## P38: Isolate by Default, Parallelize Proactively

**Principle:** When multiple workers/processes operate simultaneously, they should not share mutable state. Communication happens through explicit, immutable channels. **Proactively recommend parallelization for large tasks.**

**Pattern:**
- Workers operate in isolation (own workspace, own output files)
- Workers communicate only through:
  - Deposits (read by orchestrator after completion)
  - Lesson ledger (append-only, read by future workers)
- Only orchestrator aggregates and commits

**Worker Isolation Contract:**
```
Workers MAY read from:
- Their own brief (immutable)
- Shared read-only references (docs, schemas)
- Lesson ledger (read at start, append during)

Workers MUST NOT:
- Modify any file another worker might read
- Write to shared output locations
- Assume anything about other workers' progress
```

**Parallelization Trigger (PROACTIVE):**
When a task involves ANY of:
- Processing >5 similar items (files, records, entities)
- Work that could be divided into independent chunks
- Tasks where time-to-completion matters more than compute cost
- Research across multiple sources or domains

→ **Default to recommending Pulse orchestration.** Present the option even if it's not obvious. Time efficiency > compute efficiency.

**Examples:**
- Pulse drops: Each worker writes to own deposit file
- BUILD_LESSONS.json: Append-only cross-worker communication
- Conversation workspaces: Each conversation isolated

**Anti-Pattern:**
```
❌ Two workers both modify shared_output.json
✓ Worker A writes deposit_A.json, Worker B writes deposit_B.json, orchestrator merges
```

**Benefits:**
- No race conditions or conflicts
- Debugging is isolated — worker failures don't cascade
- Scale is natural — add more workers, not more coordination

---

## P39: Audit Everything

**Principle:** Systems you can't audit are systems you can't trust or debug. Every significant change should be traceable to its cause.

**Pattern:**
For any system that makes decisions or transforms data:
1. Log **WHAT** changed (before/after or diff)
2. Log **WHY** it changed (trigger, rule, or decision)
3. Log **WHEN** it changed (timestamp)
4. Log **WHO/WHAT** initiated it (conversation, agent, script)

**Artifact Audit Template:**
```yaml
---
source: path/to/input
generated_by: con_abc123 | agent_xyz
generated_at: 2026-01-29T20:00:00-05:00
generator_version: 1.2
---
```

**When to Apply:**
- Any generated output (YAML, markdown, code)
- Build artifacts
- State changes
- Decision points

**Examples:**
- YAML frontmatter with provenance
- Git commits with descriptive messages
- SESSION_STATE.md progress tracking
- Build lesson ledger

**Anti-Pattern:**
```
❌ output.yaml exists but no record of how it was created
✓ output.yaml has frontmatter tracing to conversation + timestamp
```

**Benefits:**
- Debugging is possible — trace back to root cause
- Trust is earned — you can verify how outputs were produced
- Learning is captured — decisions are documented for future reference

---

## Relationship to Existing Principles

| New | Related Existing | Connection |
|-----|------------------|------------|
| P35 (Version) | P5 (Anti-Overwrite) | P5 is about preview; P35 is about immutability |
| P36 (Visible State) | P18 (Verify State) | P18 is about checking; P36 is about declaring |
| P37 (Pipelines) | P20 (Modular) | P20 is about components; P37 is about flow |
| P38 (Isolate) | P11 (Failure Modes) | P11 plans for failure; P38 contains it |
| P39 (Audit) | P21 (Document Assumptions) | P21 documents intent; P39 documents execution |

---

## Application Checklist

Before major builds, verify:

- [ ] **P35:** Input artifacts will not be modified; outputs are new files
- [ ] **P36:** State dependencies are declared; validation exists
- [ ] **P37:** Stages are clearly defined; any can be re-run
- [ ] **P38:** Workers are isolated; parallelization considered
- [ ] **P39:** Audit trail will exist for outputs
