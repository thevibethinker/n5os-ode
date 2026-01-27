---
created: 2026-01-25
last_edited: 2026-01-25
version: 2.0
provenance: con_WxPUSXG566miX5VX
---

# PLAN: Pulse Jettison & Lineage System

## Summary

Add jettison launch mode to Pulse — a way to spawn connected-but-independent builds from the current context. Includes lineage tracking to visualize the DAG of build relationships.

## Open Questions

*None remaining — all clarified in conversation.*

## Checklist

### Phase 1: Core Jettison
- [ ] D1.1: Jettison command implementation (`pulse jettison`)
- [ ] D1.2: Lineage schema + folder scaffolding

### Phase 2: Visualization & Docs
- [ ] D2.1: Lineage visualization command (`pulse lineage`)
- [ ] D2.2: Update SKILL.md documentation

## Success Criteria

1. `pulse jettison "task description"` creates `N5/builds/j-<slug>/` with proper structure
2. Running from a build context auto-populates lineage from parent
3. Output is a copy-pasteable launch prompt with file path
4. `pulse lineage` shows DAG of all builds with parent relationships
5. `pulse lineage <slug>` shows ancestry/descendants of specific build
6. Jettison deposits go to their own build folder (self-contained)

---

## Phase 1: Core Jettison

### D1.1: Jettison Command

**Affected Files:**
- `Skills/pulse/scripts/pulse.py` (add `jettison` subcommand)

**Changes:**
1. Add `jettison` subcommand to argparse
2. Implement context capture:
   - Accept task description
   - Optional `--from <slug>` for explicit parent build
   - Optional `--type <type>` for explicit build type (else auto-detect)
   - Optional `--moment "<description>"` for explicit moment capture
3. Auto-detect build type from task description keywords:
   - "fix", "bug", "debug", "error" → code_build
   - "research", "explore", "investigate" → research
   - "draft", "write", "content" → content
   - "plan", "design", "architect" → planning
   - Default: code_build
4. Generate slug: `j-<short-task-slug>-<timestamp>`
5. Create build folder via D1.2's scaffolding
6. Write drop brief to `drops/D1.1-jettison-task.md`
7. Output launch prompt:
   ```
   Jettison created: N5/builds/j-<slug>/
   
   Launch prompt (copy to new thread):
   ---
   Load and execute: file 'N5/builds/j-<slug>/drops/D1.1-jettison-task.md'
   ---
   ```

**Unit Tests:**
- Test type auto-detection from various task descriptions
- Test slug generation
- Test output format

### D1.2: Lineage Schema & Scaffolding

**Affected Files:**
- `Skills/pulse/scripts/pulse.py` (add scaffolding helper)
- Schema definition (inline in code)

**Changes:**
1. Define lineage schema for meta.json:
   ```json
   {
     "lineage": {
       "parent_type": "build|conversation|jettison|null",
       "parent_ref": "<slug or convo_id>",
       "parent_conversation": "<convo_id where jettison was triggered>",
       "moment": "<description of what triggered this>",
       "branched_at": "<ISO timestamp>"
     }
   }
   ```
2. Create `scaffold_jettison_build()` function:
   - Create `N5/builds/j-<slug>/` directory
   - Create meta.json with:
     - `build_type`: detected or specified
     - `launch_mode`: "jettison"
     - `lineage`: populated from context
     - `status`: "pending"
   - Create empty `drops/`, `deposits/`, `artifacts/` directories
   - Create STATUS.md template
3. Inherit learnings from parent:
   - If parent build exists, read its BUILD_LESSONS.json
   - Copy relevant learnings to jettison's BUILD_LESSONS.json
   - Add note: "Inherited from <parent>"

**Unit Tests:**
- Test folder structure creation
- Test lineage population from build context
- Test lineage population from conversation context
- Test learnings inheritance

---

## Phase 2: Visualization & Docs

### D2.1: Lineage Visualization

**Affected Files:**
- `Skills/pulse/scripts/pulse.py` (add `lineage` subcommand)

**Changes:**
1. Add `lineage` subcommand:
   - `pulse lineage` — show full DAG of all builds
   - `pulse lineage <slug>` — show ancestry + descendants of specific build
   - `--format tree|json` — output format (default: tree)
2. Scan all `N5/builds/*/meta.json` for lineage data
3. Build adjacency graph (parent → children)
4. Render as ASCII tree:
   ```
   Build Lineage
   
   adhd-todo-research [research] ✓
   ├── j-ratelimit-debug [code_build] ●
   │   └── j-api-redesign [planning] ○
   └── j-gamification-tangent [research] ✓
   
   standalone-build [code_build] ○
   
   Legend: ✓ complete  ● running  ○ pending  ✗ failed
   ```
5. For `--format json`, output machine-readable structure

**Unit Tests:**
- Test graph building from meta.json files
- Test tree rendering
- Test filtering by slug

### D2.2: Documentation Update

**Affected Files:**
- `Skills/pulse/SKILL.md`

**Changes:**
1. Add "Jettison Launch Mode" section:
   - When to use (tangent off-ramp, debugging, idea exploration)
   - Command syntax and options
   - Example workflow
2. Add "Lineage Tracking" section:
   - How lineage is recorded
   - Visualization commands
   - DAG structure explanation
3. Update terminology table with:
   - Jettison: Connected-but-independent build spawned as tangent
   - Lineage: Parent-child relationship graph between builds

**Unit Tests:**
- N/A (documentation)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Old builds lack lineage field | Make lineage optional; null = standalone build |
| Type auto-detection guesses wrong | Allow explicit `--type` override; ask clarifying questions |
| DAG visualization slow with many builds | Cache graph; lazy-load meta.json |

## Alternatives Considered

1. **Jettisons as sub-folder of parent** — Rejected: breaks self-containment, complicates deposits
2. **Separate jettisons directory** — Rejected: they ARE builds, should live with builds
3. **Complex branching/merging like git** — Deferred: one-way branches sufficient for now

## Trap Doors

- **Lineage schema**: Once builds have lineage, changing schema requires migration
  - Mitigation: Keep schema minimal and extensible
