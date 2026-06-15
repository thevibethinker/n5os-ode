---
created: 2026-05-07
last_edited: 2026-05-07
version: 1.0
provenance: con_JVVJDhMs2CMqchJq
---

# Building Fundamentals

The P35-P39 building fundamentals are the operating baseline for N5OS implementation work. They turn broad architectural principles into concrete build behavior: preserve inputs, expose state, structure work as pipelines, parallelize only across clean boundaries, and leave an audit trail.

## P35: Version, Don't Overwrite

Preserve original inputs and create explicit new versions for transformed outputs.

Use this when:
- Editing generated artifacts, drafts, exports, or reports.
- Transforming user data into a new form.
- Creating a repair path where rollback matters.

Operational standard:
- Do not overwrite source material unless the user explicitly asked for an in-place edit.
- Prefer named versions, dated artifacts, or git-tracked diffs.
- Keep enough context to reconstruct what changed and why.

## P36: Make State Visible

Declare the current state before acting, then update it as work changes.

Use this when:
- Running multi-step work.
- Coordinating across personas, workers, or scripts.
- Making progress claims.

Operational standard:
- Name the objective, assumptions, unknowns, and current lane.
- Keep `SESSION_STATE.md`, build `STATUS.md`, or another workflow-specific state file current when required.
- Report quantitative progress for multi-step work.

## P37: Design as Pipelines

Break complex work into explicit stages that can be inspected, rerun, or replaced.

Use this when:
- Building scripts or workflows.
- Processing multiple files, meetings, records, or research sources.
- Combining deterministic scripts with semantic AI judgment.

Operational standard:
- Define inputs, transformations, outputs, and validation gates.
- Keep scripts responsible for mechanics and AI responsible for semantic judgment.
- Make each stage independently testable where practical.

## P38: Isolate and Parallelize

Parallelize work only when units are cleanly separable and do not share mutable state.

Use this when:
- Processing more than five non-trivial items.
- Running Pulse drops or worker-style execution.
- Comparing competing hypotheses or research streams.

Operational standard:
- Give each worker a bounded brief, output path, and success criteria.
- Avoid shared write targets unless a coordinator owns merging.
- Prefer Pulse orchestration for decomposable multi-source or multi-item work.

## P39: Audit Everything

Every durable output should explain where it came from, what changed, and how it was checked.

Use this when:
- Creating markdown, code, exports, or handoff artifacts.
- Closing builds or reporting completion.
- Patching public-facing packages.

Operational standard:
- Include YAML frontmatter in markdown files.
- Record provenance through conversation IDs, build IDs, deposits, changelogs, or git commits.
- Capture validation commands and outcomes before claiming completion.

## Quick Checklist

- [ ] Inputs preserved or versioned.
- [ ] State and assumptions declared.
- [ ] Work broken into inspectable stages.
- [ ] Parallel work isolated by clear boundaries.
- [ ] Outputs include provenance and validation evidence.
