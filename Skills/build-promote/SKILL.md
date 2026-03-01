---
name: build-promote
description: Transforms completed Pulse builds into first-class Skills with lineage analysis, artifact classification, semantic path adaptation, and state migration.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  created: "2026-02-21"
---

# Build Promote

Promotes completed builds from `N5/builds/` into permanent, first-class capabilities in `Skills/`. Handles the full lifecycle: lineage analysis across build versions, artifact classification, file migration with path adaptation, SKILL.md generation, and post-promotion verification.

## When to Use

- After a Pulse build reaches `complete` or `finalized` status
- When V decides a build should become a permanent capability
- To audit the build corpus for promotable candidates
- To verify an already-promoted skill is self-contained

## Directory Structure

```
Skills/build-promote/
├── SKILL.md              # This file
├── scripts/
│   ├── lineage_analyzer.py    # Scan + cluster builds
│   ├── artifact_classifier.py # Classify build files for routing
│   ├── promote.py             # Execute promotion workflow
│   └── verify.py              # Post-promotion verification
└── state/
    └── lineage.json           # Cached lineage analysis
```

## Scripts

| Script | Purpose |
|--------|---------|
| `lineage_analyzer.py` | Scans all `N5/builds/*/meta.json`, clusters related builds (e.g. v4→v5→v7), identifies canonical versions, flags promotable builds |
| `artifact_classifier.py` | Classifies every file in a build into categories (operational_script, governance, runtime_state, prompt, reference, static_asset, build_scaffolding, obsolete, intermediate) |
| `promote.py` | Executes the 9-step promotion workflow: pre-flight, naming, classification, directory creation, file migration, path adaptation, SKILL.md generation, protection markers, build finalization |
| `verify.py` | Runs 8 post-promotion checks: stale paths, script health, import health, SKILL.md completeness, state accessibility, protection markers, build residuals, bytecode cleanup |

## CLI Reference

### Lineage Analyzer

```bash
# Full scan of all 196 builds
python3 Skills/build-promote/scripts/lineage_analyzer.py scan
python3 Skills/build-promote/scripts/lineage_analyzer.py scan --save   # persist to state/lineage.json
python3 Skills/build-promote/scripts/lineage_analyzer.py scan --json   # machine-readable

# Show cluster for a specific build
python3 Skills/build-promote/scripts/lineage_analyzer.py cluster zo-hotline-v5

# List all promotable builds
python3 Skills/build-promote/scripts/lineage_analyzer.py promotable
python3 Skills/build-promote/scripts/lineage_analyzer.py promotable --json
```

### Artifact Classifier

```bash
# Classify a single build
python3 Skills/build-promote/scripts/artifact_classifier.py classify zode-moltbook
python3 Skills/build-promote/scripts/artifact_classifier.py classify zode-moltbook --json

# Classify across a build cluster (uses lineage data)
python3 Skills/build-promote/scripts/artifact_classifier.py classify-cluster zo-hotline-v5
```

### Promote

```bash
# Preview what would happen (dry-run)
python3 Skills/build-promote/scripts/promote.py preview <slug>

# Execute promotion (interactive confirmation)
python3 Skills/build-promote/scripts/promote.py run <slug>

# Execute with auto-confirm and custom skill name
python3 Skills/build-promote/scripts/promote.py run <slug> --name <skill-slug> --yes

# Promote from cluster canonical
python3 Skills/build-promote/scripts/promote.py run <slug> --cluster --yes
```

### Verify

```bash
# Run all 8 checks
python3 Skills/build-promote/scripts/verify.py check <skill-slug>

# Auto-fix simple issues (pycache, missing .n5protected)
python3 Skills/build-promote/scripts/verify.py check <skill-slug> --fix

# Verbose output + JSON
python3 Skills/build-promote/scripts/verify.py check <skill-slug> --verbose --json
```

## Promotion Workflow

1. **Lineage scan** — `lineage_analyzer.py scan --save` to identify promotable builds
2. **V approves** — V selects a build and approves the skill slug
3. **Preview** — `promote.py preview <slug>` to see the migration plan
4. **Execute** — `promote.py run <slug> --name <skill-slug> --yes`
5. **Verify** — `verify.py check <skill-slug> --fix`
6. **Review** — V reviews the generated SKILL.md and adapts as needed

## The `state/` Skill Standard

This skill establishes `state/` as a new convention for skills that maintain runtime data:

```
Skills/<slug>/
├── SKILL.md        # Documentation
├── scripts/        # Operational code
├── assets/         # Governance docs, images, templates
├── prompts/        # System prompts
├── references/     # API docs, specs
└── state/          # Runtime data (NEW)
    ├── memory/     # Semantic memory
    ├── staging/    # Queued items
    ├── analytics/  # Metrics and tracking
    └── learnings/  # Accumulated insights
```

**Why `state/`?** Skills like Zøde Moltbook maintain living data — semantic memory, staging queues, post drafts, analytics. This data is:
- **Not code** (doesn't belong in `scripts/`)
- **Not a dataset** (not tabular DuckDB like hotline call logs)
- **Not governance** (not static docs in `assets/`)
- **Living** — grows and changes with every interaction

The `state/` directory carries `.n5protected` markers for PII protection and is excluded from code-level operations like linting.

## Integration with Pulse

After `pulse_cc.py finalize <slug>`, the natural next step is promotion:

```bash
# After Pulse finalization
python3 Skills/build-promote/scripts/promote.py preview <slug>
# Review and execute
python3 Skills/build-promote/scripts/promote.py run <slug> --name <skill-slug> --yes
python3 Skills/build-promote/scripts/verify.py check <skill-slug> --fix
```

## Dependencies

- Python 3.10+
- stdlib only (no external packages)
