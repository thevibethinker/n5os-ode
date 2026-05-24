---
created: 2026-03-15
last_edited: 2026-03-15
version: 1.0
provenance: con_oK3U6a3DWgbtQKma
---

# Dependency Graph Review Protocol

## Purpose

Make structural coupling visible before edits land.

This protocol is required for:
- multi-file refactors
- debugging shared behavior or uncertain blast radius
- Pulse Drops that modify shared scripts, prompts, skills, or libraries

This protocol is optional for:
- typo fixes
- isolated docs/notes
- clearly local single-file edits with obvious blast radius

## Required Sequence

```bash
python3 Skills/codebase-graph/scripts/query.py index
python3 Skills/codebase-graph/scripts/query.py review <target>
```

If `review` returns `HIGH`, continue with:

```bash
python3 Skills/codebase-graph/scripts/query.py rdeps <target>
python3 Skills/codebase-graph/scripts/query.py deps <target>
python3 Skills/codebase-graph/scripts/query.py info <target>
```

## Decision Rules

### Low Risk

Characteristics:
- few direct dependents
- limited reverse blast radius
- narrow edge mix

Action:
- proceed with a scoped edit
- re-run review if scope expands

### Medium Risk

Characteristics:
- several direct dependents
- mixed coupling but still understandable

Action:
- inspect direct dependents before editing
- avoid bundling unrelated cleanup
- stage the work if the target sits in a shared cluster

### High Risk

Characteristics:
- many direct or transitive dependents
- multiple edge types converge on the target
- shared infrastructure or hub-like behavior

Action:
- treat as staged work, not casual surgery
- check direct dependents with `rdeps`
- reduce scope, split phases, or Pulse-decompose the change
- document why the blast radius is acceptable if you still proceed

## Debugging Use

When root cause is unclear, run graph review on the suspected shared files before fixing symptoms.

Questions to answer:
- Is the failing file actually the source, or just a shared downstream consumer?
- What other components will I perturb if I patch this here?
- Am I about to “fix” a hub symptom instead of the upstream cause?

## Pulse Use

For qualifying Drops, include an explicit pre-check block:

```markdown
## Graph Review

Before editing:

```bash
python3 Skills/codebase-graph/scripts/query.py index
python3 Skills/codebase-graph/scripts/query.py review <target>
```

If risk is HIGH, also run:

```bash
python3 Skills/codebase-graph/scripts/query.py rdeps <target>
```

Record what the blast radius implies for scope.
```

## Interpretation Standard

- `review` is the default entry point
- `rdeps` is mandatory when risk is high or transitive impact matters
- `deps` clarifies upstream requirements
- `cluster` is for neighborhood context

## Failure Modes To Avoid

- editing a shared hub as if it were isolated
- making a “small” refactor against stale graph data
- reviewing only imports and ignoring prompts/skills/Pulse links
- treating the graph as advisory on work that qualifies as required
