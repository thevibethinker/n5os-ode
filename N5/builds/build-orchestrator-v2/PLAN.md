---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
type: build_plan
status: active
provenance: con_cmcIm7pClVwCh5sF
---

# Plan: Build Orchestrator v2

**Objective:** Replace the broken build orchestration pattern with a human-in-the-loop distributed cognition system that uses persistent documents (not API calls) to coordinate work across threads.

**Trigger:** V identified fundamental misunderstanding — "spawn workers" was being interpreted as `/zo/ask` API calls when the actual intent is document-based worker briefs that V manually pastes into new threads.

**Key Insight:** The orchestrator is a DOCUMENT (persistent build folder), not a conversation. The conversation is just an interface to the document.

---

## Open Questions (Resolved)

- [x] Should meta.json live at build root or in a `.build/` subfolder?  
  **→ Build root.** Simpler, no hidden folders, easier for V to inspect.

- [x] Should worker briefs be separate files or sections in BUILD.md?  
  **→ Separate files in `workers/`.** Better for copy-paste ergonomics, cleaner BUILD.md.

- [x] How should "general orchestration" (non-code) differ from code builds?  
  **→ `type` field in meta.json.** Code builds get git awareness; general builds skip commit logic.

- [x] Dashboard site: static regeneration or live API?  
  **→ Static regeneration triggered by script.** Simpler, no server needed, runs on close/check-in.

- [x] Should there be a `build ls --incomplete` CLI?  
  **→ Yes.** Bake into init_build.py as pre-screen + standalone `build_status.py` command.

---

## Checklist

### Wave 1: Foundation (No Dependencies — Parallel)
- ☐ W1.1: System Documentation (`Documents/System/Build-Orchestrator-System.md`)
- ☐ W1.2: Template Updates (BUILD.md, worker brief, meta.json schema)
- ☐ W1.3: Rule Creation (correct build orchestrator rule)

### Wave 2: Core Scripts (Depends on W1.2)
- ☐ W2.1: init_build.py upgrade (v2 structure, pre-screen, meta.json)
- ☐ W2.2: update_build.py creation (worker completion, status sync)
- ☐ W2.3: Close Conversation prompt update (enhanced worker mode)

### Wave 3: Dashboard (Depends on W2.2)
- ☐ W3.1: build_status.py script (CLI for build status, JSON output)
- ☐ W3.2: Build Dashboard Site (Domino's tracker UI)

### Wave 4: Integration (Depends on All Above)
- ☐ W4.1: Operator persona update (BUILD TRIGGER section)
- ☐ W4.2: Integration test (end-to-end with this build as test case)

---

## Architecture Decision: Hybrid Upgrade

**Decision:** Upgrade existing infrastructure, don't replace.

**Rationale:**
- `N5/builds/` has 50+ historical builds — preserve folder structure
- `init_build.py` exists — extend it
- `Close Conversation.prompt.md` has worker mode — enhance it
- Templates exist — upgrade them

**What's New:**
- `workers/` and `completions/` subfolders
- `meta.json` for build state tracking
- Pre-decided worker titles
- Dashboard site
- Proper rule that reflects actual pattern

---

## Wave 1: Foundation

### W1.1: System Documentation
**Title:** `[build-orchestrator-v2] W1.1: System Documentation`  
**File:** `Documents/System/Build-Orchestrator-System.md`

Canonical reference document explaining:
- The full pattern (orchestrator = document, not conversation)
- Folder structure and file purposes
- Worker brief format
- Thread title conventions
- How close hooks work
- Code build vs general orchestration
- Dependency management and waves

### W1.2: Template Updates
**Title:** `[build-orchestrator-v2] W1.2: Template Updates`  
**Files:**
- `N5/templates/build/BUILD_template.md` (new — orchestrator doc)
- `N5/templates/build/worker_brief_template.md` (new)
- `N5/templates/build/meta_schema.json` (new — reference schema)
- Update `N5/templates/build/plan_template.md` (add worker brief section)

### W1.3: Rule Creation
**Title:** `[build-orchestrator-v2] W1.3: Rule Creation`  
**Artifact:** Zo rule via `create_rule`

Condition: `When build orchestrator pattern is invoked, or complex work needs distribution across threads`

Instruction covering:
- Creates persistent build artifacts (not API workers)
- Worker briefs are documents for manual paste
- Workers close WITHOUT commits
- Pre-screen for incomplete builds
- Pre-decide worker titles at orchestration time

---

## Wave 2: Core Scripts

### W2.1: init_build.py Upgrade
**Title:** `[build-orchestrator-v2] W2.1: init_build.py Upgrade`  
**File:** `N5/scripts/init_build.py`

Changes:
- Add `--type` flag (code_build, content, research, general)
- Create `workers/` and `completions/` subfolders
- Generate `meta.json` with initial state
- Pre-screen: check for incomplete builds with `--check-existing` or by default
- Add `--workers` flag to pre-generate worker brief stubs
- Output pre-decided titles for each worker

### W2.2: update_build.py Creation
**Title:** `[build-orchestrator-v2] W2.2: update_build.py Creation`  
**File:** `N5/scripts/update_build.py`

Commands:
- `update_build.py complete <slug> <worker-id> --status complete|partial|blocked --summary "..."`
  - Writes to `completions/<worker-id>.json`
  - Updates `meta.json` worker counts
- `update_build.py status <slug>`
  - Reads all completions, outputs current state
- `update_build.py close <slug>`
  - Marks build complete in meta.json
  - Archives if configured

### W2.3: Close Conversation Prompt Update
**Title:** `[build-orchestrator-v2] W2.3: Close Conversation Update`  
**File:** `Prompts/Close Conversation.prompt.md`

Enhancements to Worker Close mode:
- Read pre-decided title from SESSION_STATE (if set by worker brief)
- Write structured completion to `completions/` via update_build.py
- Include learnings, pitfalls, concerns in completion
- Flag if dependent workers need brief updates

---

## Wave 3: Dashboard

### W3.1: build_status.py Script
**Title:** `[build-orchestrator-v2] W3.1: Build Status Script`  
**File:** `N5/scripts/build_status.py`

Commands:
- `build_status.py list` — All builds with status (active/complete)
- `build_status.py list --incomplete` — Only incomplete builds
- `build_status.py <slug>` — Detailed status for one build
- `build_status.py --json` — JSON output for dashboard site
- `build_status.py regenerate` — Update dashboard site HTML

### W3.2: Build Dashboard Site
**Title:** `[build-orchestrator-v2] W3.2: Build Dashboard Site`  
**Location:** `Sites/build-tracker/`

Features:
- List all active builds with progress bars
- Show worker completion status per build
- Color-coded: green (complete), yellow (in-progress), red (blocked)
- Link to build folder
- Stale build indicator (no activity in X days)
- Auto-regenerates on build close/check-in

---

## Wave 4: Integration

### W4.1: Operator Persona Update
**Title:** `[build-orchestrator-v2] W4.1: Operator Persona Update`  
**Artifact:** Update via `edit_persona`

Update BUILD TRIGGER section to reflect correct flow:
1. Run init_build.py to scaffold
2. Route to Architect for planning
3. Architect generates BUILD.md + worker briefs
4. V manually launches workers (copy-paste briefs)
5. Workers close → write to completions/
6. V returns to orchestrator for next wave
7. Repeat until complete
8. Orchestrator commits (if code build)

### W4.2: Integration Test
**Title:** `[build-orchestrator-v2] W4.2: Integration Test`  
**Method:** Use this build as the test case

Verify:
- init_build.py creates correct structure
- Worker briefs are self-contained and paste-ready
- Worker close writes to completions/
- Orchestrator can read completions and adapt
- Dashboard shows correct status
- Final close commits atomically

---

## Success Criteria

1. **V can start a build** with `init_build.py` that creates full v2 structure
2. **Worker briefs are self-contained** and include pre-decided titles
3. **Workers close cleanly** without commits, writing to completions/
4. **Orchestrator reads completions** and can adapt remaining briefs
5. **Dashboard shows all active builds** with accurate progress
6. **Pre-screen catches** attempts to create duplicate builds
7. **This build itself** completes successfully using the new pattern

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backward compat with existing builds | Medium | Keep old templates, detect version in scripts |
| Worker forgets to use worker brief title | Low | Close Conversation reads from SESSION_STATE |
| meta.json gets out of sync | Medium | update_build.py is single source of truth |
| Dashboard site stales | Low | Regenerate on every build close |

---

## Trap Doors (Irreversible Decisions)

1. **meta.json schema** — Once workers start writing to it, schema changes require migration
   - **Mitigation:** Include `schema_version` field; keep schema minimal initially

2. **Worker brief format** — Workers will rely on consistent structure
   - **Mitigation:** Define in template with clear sections; version the template

3. **Thread title format** — Will be in conversation history forever
   - **Mitigation:** The proposed format `[slug] W#.#: Task` is flexible enough

---

## Worker Briefs

Individual worker briefs are in `workers/` folder. V opens new thread, pastes brief, worker executes.

**File naming:** `WX.Y-task-slug.md` (e.g., `W1.1-system-documentation.md`)
