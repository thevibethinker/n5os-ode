---
name: codebase-graph
description: >
  Multi-layer dependency indexer for N5OS. Maps imports, subprocess calls,
  config references, prompt wiring, skill dependencies, and Pulse build
  relationships. Use it for blast-radius review before refactors, debugging
  shared behavior, and exploring codebase coupling.
compatibility: Created for Zo Computer
metadata:
  author: <YOUR_HANDLE>.zo.computer
  version: "1.0"
  created: "2026-03-15"
---

# Codebase Graph

## When To Activate

Use this skill when:
- a change touches shared code in `N5/`, `Skills/`, `Prompts/`, or `Integrations/`
- you need blast-radius analysis before a refactor
- debugging spans multiple scripts, prompts, or skills
- you want to inspect cluster/domain structure, hubs, or orphaned nodes

For trivial typo fixes, isolated note edits, or obviously local single-file changes, this skill is optional.

## Quick Start

```bash
python3 Skills/codebase-graph/scripts/query.py index
python3 Skills/codebase-graph/scripts/query.py review N5/lib/paths.py
```

`index` rebuilds the graph from canonical N5OS surfaces.
`review` is the default operational entry point for a specific target.

## Core Commands

```bash
python3 Skills/codebase-graph/scripts/query.py index
python3 Skills/codebase-graph/scripts/query.py review <node>
python3 Skills/codebase-graph/scripts/query.py rdeps <node>
python3 Skills/codebase-graph/scripts/query.py deps <node>
python3 Skills/codebase-graph/scripts/query.py info <node>
python3 Skills/codebase-graph/scripts/query.py hubs [N]
python3 Skills/codebase-graph/scripts/query.py cluster <domain>
python3 Skills/codebase-graph/scripts/query.py orphans
python3 Skills/codebase-graph/scripts/query.py path <source> <target>
python3 Skills/codebase-graph/scripts/query.py export-json
```

## Recommended Workflow

### 1. Refresh the graph

```bash
python3 Skills/codebase-graph/scripts/query.py index
```

Run this at the start of any qualifying refactor/debugging task so decisions are based on current state.

### 2. Review the target

```bash
python3 Skills/codebase-graph/scripts/query.py review N5/scripts/db_paths.py
```

This summarizes:
- direct dependents
- total reverse dependents
- immediate dependencies
- edge-type mix
- risk label (`LOW`, `MEDIUM`, `HIGH`)

### 3. Drill deeper if needed

If the target is high risk or the coupling pattern is unclear:

```bash
python3 Skills/codebase-graph/scripts/query.py rdeps N5/scripts/db_paths.py
python3 Skills/codebase-graph/scripts/query.py deps N5/scripts/db_paths.py
python3 Skills/codebase-graph/scripts/query.py info N5/scripts/db_paths.py
python3 Skills/codebase-graph/scripts/query.py cluster n5-core
```

## Visualization

Interactive graph explorer:

- https://<YOUR_HANDLE>.zo.space/n5os-graph

API endpoint:

- https://<YOUR_HANDLE>.zo.space/api/n5os-graph

Use the page for exploration and pattern-finding. Use the CLI for operational decisions before edits.

## Scope

The graph currently indexes canonical N5OS surfaces:
- Python from `N5/`, `Skills/`, and `Integrations/`
- prompts from `Prompts/`, `N5/`, `Skills/`, plus root prompt files
- `SKILL.md` files under `Skills/`
- `N5/config/*`
- Pulse build metadata and drop briefs under `N5/builds/*`

Detected edge types:
- `IMPORTS`
- `CALLS_SUBPROCESS`
- `CONFIG_REF`
- `PROMPT_REF`
- `SKILL_REF`
- `PULSE_PLANNED`

## Exclusions

The index intentionally excludes noisy mirrors and runtime surfaces such as:
- logs
- `.backups/`
- `Build Exports/`
- `Temp/`
- `node_modules/`
- `state/`
- virtualenv folders

This keeps blast-radius analysis focused on canonical sources rather than stale copies.

## Pulse Integration

For qualifying refactor Drops, graph review should be explicit in the brief.

Minimum pre-check:

```bash
python3 Skills/codebase-graph/scripts/query.py index
python3 Skills/codebase-graph/scripts/query.py review <target>
```

If review returns `HIGH`, also run:

```bash
python3 Skills/codebase-graph/scripts/query.py rdeps <target>
```

Then either:
- narrow the change scope,
- split the work into staged Drops,
- or document why a larger blast radius is acceptable.

## Interpretation

- `review` answers: should I treat this as surgery or infrastructure work?
- `rdeps` answers: what breaks if I touch this?
- `deps` answers: what does this rely on?
- `cluster` answers: what else lives in this neighborhood?

## Limitations

This is a static graph, not runtime tracing. It will miss:
- dynamic imports
- path construction assembled at runtime
- `/zo/ask` relationships that are only implied semantically
- state coupling through databases/files unless a textual reference exists

Treat it as a high-value structural map, not a complete execution trace.
