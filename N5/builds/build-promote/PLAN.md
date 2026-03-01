---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
type: build_plan
status: draft
provenance: con_p5NDwdFdETChNHoz
---

# Plan: Build Promote — The Build-to-Skill Finalization Skill

**Objective:** Create a skill that transforms completed Pulse builds into first-class Skills, handling lineage analysis, artifact classification, semantic path adaptation, and state migration.

**Trigger:** The Zøde Moltbook build required a manual 8-step process to promote from `N5/builds/` to `Skills/`. This should be a repeatable, semi-automated capability.

**Key Design Principle:** The skill does the mechanical heavy lifting (scanning, classifying, moving, path-updating) but surfaces decisions to V for approval (naming, what to keep vs drop, which build version is canonical). AI handles adaptation; human retains authority.

---

## Open Questions

- [x] Should builds that don't become skills be handled? → No, they stay. Separate capability later.
- [x] Who decides the skill slug? → Skill proposes, V approves. Always ask.
- [x] Where does runtime state go? → `state/` within the skill. New standard.
- [x] Apply retroactively? → Yes, via backfill analysis mode.
- [ ] Should the skill also update the Pulse finalize command to call build-promote as a post-finalization step? (Integration point TBD — could be a follow-up build)

---

## Alternatives Considered

### Option A: Script-only (no skill)
A single Python script that does the full promotion. Simpler but no documentation, no governance, harder to extend.
**Rejected:** This is a capability V wants to invoke repeatedly. It deserves skill structure.

### Option B: Extension to Pulse
Add promotion as a phase within `pulse.py finalize`. Keeps everything in one tool.
**Rejected:** Pulse is already complex. Promotion is a distinct concern — it should compose with Pulse, not live inside it. Also, promotion applies to non-Pulse builds too.

### Option C: Standalone skill with composable scripts ← CHOSEN
A skill at `Skills/build-promote/` with focused scripts for each concern: lineage analysis, artifact classification, promotion execution, verification. Can be invoked standalone or chained after `pulse.py finalize`.

---

## Checklist

### Wave 1: Analysis Engine (parallel)
- ☐ D1.1: Build lineage analyzer — scan all builds, cluster by capability
- ☐ D1.2: Artifact classifier — classify files in a build (operational, governance, state, scaffolding, dead)

### Wave 2: Promotion Engine (parallel, depends on W1)
- ☐ D2.1: Promotion executor — move files, adapt paths, generate SKILL.md
- ☐ D2.2: Verification suite — validate promoted skill integrity

### Wave 3: Integration (sequential, depends on W2)
- ☐ D3.1: SKILL.md + end-to-end test on a real build

---

## Wave 1: Analysis Engine

### D1.1: Build Lineage Analyzer

**Purpose:** Scan all `N5/builds/*/meta.json` files and construct a lineage graph — which builds relate to each other, which supersede others, and which represent distinct capabilities.

**Affected Files:**
- `Skills/build-promote/scripts/lineage_analyzer.py` - CREATE - Main lineage analysis script

**Clustering Signals (ranked by reliability):**
1. **Explicit lineage** — `meta.json` may have `parent_build` or Pulse `lineage` fields
2. **Shared deliverable paths** — Two builds listing the same `Skills/X/scripts/Y.py` as a deliverable are working on the same capability
3. **Slug similarity** — `zo-hotline`, `zo-hotline-v4`, `zo-hotline-v5`, `zo-hotline-v6`, `zo-hotline-v7` are clearly a chain
4. **Temporal sequence** — Same-theme builds created in order
5. **Status progression** — `superseded` or `jettisoned` builds explicitly point to their successors

**Output Format:**
```json
{
  "clusters": [
    {
      "capability": "zo-hotline",
      "builds": [
        {"slug": "zo-hotline", "status": "complete", "created": "..."},
        {"slug": "zo-hotline-v4", "status": "complete", "created": "..."},
        {"slug": "zo-hotline-v7", "status": "active", "created": "..."}
      ],
      "canonical_build": "zo-hotline-v7",
      "existing_skill": "Skills/zo-hotline/",
      "promotion_status": "has_skill_but_may_have_stale_build_artifacts"
    }
  ],
  "singletons": [
    {"slug": "adhd-todo-research", "status": "complete", "type": "one-off"}
  ]
}
```

**CLI:**
```bash
python3 Skills/build-promote/scripts/lineage_analyzer.py scan          # Full analysis
python3 Skills/build-promote/scripts/lineage_analyzer.py cluster <slug> # Show cluster for a specific build
python3 Skills/build-promote/scripts/lineage_analyzer.py promotable     # List builds ready for promotion
```

**Promotability criteria:**
- Status is `complete` or `finalized`
- Not already fully promoted (no `transition_note` in meta.json)
- Has operational artifacts (scripts, state, configs) beyond just build scaffolding
- Is the canonical (latest) build in its cluster

### D1.2: Artifact Classifier

**Purpose:** Given a build folder, classify every file into categories that determine where it should go during promotion.

**Affected Files:**
- `Skills/build-promote/scripts/artifact_classifier.py` - CREATE - Classification engine

**Classification Categories:**
| Category | Description | Promotion Target |
|----------|-------------|-----------------|
| `operational_script` | Python/TS scripts that run during normal operation | `Skills/<slug>/scripts/` |
| `governance` | Persona docs, constitutions, rubrics, policies | `Skills/<slug>/assets/` |
| `runtime_state` | Databases, caches, queues, memory, analytics | `Skills/<slug>/state/` |
| `prompt` | System prompts, engagement prompts | `Skills/<slug>/prompts/` |
| `reference` | API docs, specs, external documentation | `Skills/<slug>/references/` |
| `static_asset` | Images, avatars, templates | `Skills/<slug>/assets/` |
| `build_scaffolding` | meta.json, PLAN.md, STATUS.md, BUILD.md, workers/ | Stays in build folder |
| `obsolete` | Superseded by later version, dead code, stale cache | Delete (with confirmation) |
| `intermediate` | Research, exploration, throwaway artifacts | Archive or delete |

**Classification Method:**
- File extension + directory position (heuristic layer)
- Content analysis via LLM for ambiguous files (semantic layer)
- Cross-reference with meta.json deliverables list

**For multi-build clusters:**
- Compare files across builds in the cluster
- Identify which build has the canonical (latest working) version of each file
- Flag files in earlier builds that were superseded — these are `obsolete`
- This is the "quick obsolescence pass" V requested

**CLI:**
```bash
python3 Skills/build-promote/scripts/artifact_classifier.py classify <slug>           # Classify single build
python3 Skills/build-promote/scripts/artifact_classifier.py classify-cluster <slug>    # Classify across cluster
python3 Skills/build-promote/scripts/artifact_classifier.py --dry-run <slug>           # Preview without changes
python3 Skills/build-promote/scripts/artifact_classifier.py --json <slug>              # Machine-readable output
```

---

## Wave 2: Promotion Engine

### D2.1: Promotion Executor

**Purpose:** Execute the actual promotion — move files, adapt paths, generate SKILL.md, update sandbox, expunge build residuals.

**Affected Files:**
- `Skills/build-promote/scripts/promote.py` - CREATE - Main promotion script

**Promotion Workflow:**
1. **Pre-flight** — Run lineage_analyzer + artifact_classifier, load classification
2. **Name proposal** — Generate professional skill slug, present for V's approval (interactive prompt or --name flag)
3. **Directory creation** — Create `Skills/<slug>/` with standard structure
4. **File migration** — Copy files to target locations per classification
5. **Path adaptation** — Scan all migrated scripts for hardcoded paths referencing `N5/builds/<slug>/`, replace with `Skills/<slug>/` equivalents. This is the semantic adaptation step — not just find-replace but understanding what each path reference means
6. **SKILL.md generation** — Auto-generate SKILL.md from classified artifacts: script table, directory structure, configuration section, governance section
7. **Protection markers** — Add `.n5protected` to `state/` directories
8. **Build finalization** — Update meta.json (status: complete, transition_note), expunge migrated files from build folder
9. **Verification handoff** — Call verification suite

**Path Adaptation Strategy:**
```
Old: N5/builds/<build-slug>/workspace/...  → New: Skills/<skill-slug>/state/...
Old: N5/builds/<build-slug>/artifacts/...  → New: Skills/<skill-slug>/assets/...
Old: N5/builds/<build-slug>/scripts/...    → New: Skills/<skill-slug>/scripts/...
```

**CLI:**
```bash
python3 Skills/build-promote/scripts/promote.py run <slug> [--name <skill-slug>] [--dry-run]
python3 Skills/build-promote/scripts/promote.py run <slug> --cluster  # Promote from cluster (multi-build)
```

**Interactive vs Non-interactive:**
- Default: interactive (asks for name approval, shows classification preview)
- `--yes`: skip confirmations (for automated use)
- `--dry-run`: show what would happen without doing it

### D2.2: Verification Suite

**Purpose:** Validate that a promoted skill is fully self-contained and functional.

**Affected Files:**
- `Skills/build-promote/scripts/verify.py` - CREATE - Post-promotion verification

**Checks:**
1. **Stale path grep** — No references to `N5/builds/<slug>/` in any `.py`, `.md`, `.json`, `.ts` file under `Skills/<slug>/`
2. **Script health** — Run `--help` on every `.py` script, confirm exit code 0
3. **Import health** — Check for broken `sys.path.insert` or relative imports referencing old locations
4. **SKILL.md completeness** — Verify all scripts are listed, all directories documented
5. **State accessibility** — If `state/` exists, verify scripts can read from it
6. **Protection markers** — Verify `.n5protected` exists on `state/` dirs
7. **Build residuals** — Verify build folder only contains scaffolding (no operational files left behind)
8. **Bytecode cleanup** — No `__pycache__` with stale compiled paths

**CLI:**
```bash
python3 Skills/build-promote/scripts/verify.py check <skill-slug>
python3 Skills/build-promote/scripts/verify.py check <skill-slug> --fix  # Auto-fix simple issues
```

---

## Wave 3: Integration

### D3.1: SKILL.md + End-to-End Test

**Purpose:** Write the build-promote SKILL.md itself, and validate the entire pipeline by running it on one real completed build (not Zøde — that's already done).

**Affected Files:**
- `Skills/build-promote/SKILL.md` - CREATE - Skill documentation
- Test run on a real build TBD (candidate: one of the completed hotline builds or a simpler completed build)

**SKILL.md Structure:**
- Purpose and when to invoke
- Directory structure with `state/` standard documented
- CLI reference for all 4 scripts
- Promotion workflow diagram
- Integration point with Pulse (post-finalize hook)

---

## Success Criteria

1. `lineage_analyzer.py scan` produces a complete cluster map of all 90+ builds
2. `artifact_classifier.py classify <slug>` correctly categorizes files for a test build
3. `promote.py run <slug> --dry-run` shows correct migration plan
4. `promote.py run <slug>` successfully promotes a real build to a skill
5. `verify.py check <slug>` passes all checks on the promoted skill
6. Zero stale path references after promotion
7. All promoted scripts pass `--help`

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Path adaptation misses edge cases (dynamic path construction, f-strings) | Verification suite catches these; `--dry-run` for preview |
| Multi-build cluster has conflicting versions of same file | Classifier flags conflicts; human picks canonical version |
| Build has no meta.json (67 builds lack it) | Lineage analyzer handles gracefully — uses slug/directory heuristics |
| Promoted skill breaks running services | Promote doesn't touch running services; verification confirms script health |
| SKILL.md generation produces low-quality docs | Generated as draft; V reviews before finalizing |

---

## Trap Doors (Irreversible Decisions)

1. **Deleting obsolete files from build folders** — Mitigated by `--dry-run` + explicit confirmation
2. **Choosing canonical version in multi-build clusters** — Mitigated by always asking V
3. **Skill slug naming** — Once promoted and potentially referenced by other systems, renaming is painful. Always confirm name first.
