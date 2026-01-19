---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_bU6QDWx22wZGHG1Z
---

# Plan: Ode sync hardening (blocks/build/content library)

## Open Questions (must answer before execution)
1. **Scope boundary:** Are we syncing *only* the three domains you named (Blocks, Build Orchestrator/build system, Content Library), or should we also include any *required* transitive dependencies they reference (new scripts, new templates, new docs)?
2. **Public repo hygiene:** For anything that is potentially V-specific (Careerspan, private workflows), do we (A) exclude entirely, (B) include but sanitize, or (C) include behind an explicit "optional" flag in docs?
3. **Release flow:** After changes land locally, do you want (A) a PR workflow (branch → PR → merge) or (B) direct commits to `main`? (Default recommendation: PR, even if you merge immediately.)
4. **Compatibility target:** Should Ode continue to work on a totally fresh Zo with *no pip installs* (graceful degradation), or is it acceptable that some capabilities require `pip install ...` as an explicit post-step?

---

## Nemawashi (2–3 alternatives)

### Option A (Recommended): Deterministic "sync-pack" with explicit allowlist
**Idea:** Create an allowlist of files to sync from your main N5 into Ode, copy/update them deterministically, and run a validation harness.
- Pros: Lowest drift, reproducible, reviewable diff
- Cons: Needs ongoing allowlist maintenance

### Option B: Manual/curated cherry-pick
**Idea:** Human-curated file-by-file copy and ad-hoc edits.
- Pros: Fast for one-off
- Cons: High risk of inconsistency; hard to repeat; misses transitive deps

### Option C: "Mirror" module subtrees
**Idea:** Treat subtrees (e.g., `N5/scripts/`, `Prompts/Blocks/`) as mirrored packages.
- Pros: Lower effort long-term
- Cons: Highest trap-door risk: can accidentally import private/V-specific things into Ode

**Recommendation:** Option A.

---

## Trap Doors (flagged)
1. **`.gitignore` pattern `build/`** currently ignores `templates/build/` (we already saw this). If we don’t fix this, templates will silently fail to ship. **Trap door:** future missing-template regressions.
2. **Path canonicalization (`N5/config/context_manifest.yaml` vs `N5/prefs/context_manifest.yaml`).** If we don’t normalize, bootloader/docs drift and users get partial setups.
3. **Copying “updated blocks” without sanitization.** Risk: leaking V-specific conventions, or pulling in prompts that assume private tooling.

---

## Checklist

### Phase 1: Inventory, Scope Lock, and Update Catalog (Architect-owned)
- ☐ Produce max-detail Update Catalog (per-file actions, source→dest)
- ☐ Normalize path decisions (context_manifest, templates)
- ☐ Decide sanitization policy for blocks + content library
- ☐ Test: “Catalog is executable” — another Zo instance could follow it without guessing

### Phase 2: Wave 1 Implementation (Workers update Ode staging branch)
- ☐ W1.1 Blocks delta sync (B07–B35 set) + quick sanity scan
- ☐ W1.2 Reflection blocks delta sync (R00, R03–R05, R07–R09, RIX)
- ☐ W1.3 Build system sync (init_build, build_status, worker_complete, build_orchestrator updates) + `.gitignore` fix
- ☐ W1.4 Content library sync (content_ingest/content_library/content_query + docs) + compatibility checks
- ☐ W1.5 Bootloader/docs alignment (ensure bootloader installs what repo contains; ensure install docs reference correct paths)
- ☐ W1.6 Validation harness (fresh clone smoke test, `python -m py_compile`, prompt reference checks)
- ☐ Test: `scripts/validate_repo.py` passes; repo has no ignored-yet-required files

### Phase 3: Integration, Review Gate, Release
- ☐ Orchestrator reviews each worker completion report + verifies artifacts exist
- ☐ Run full validation suite (commands listed below)
- ☐ Prepare PR (or merge to main) and tag a release note
- ☐ Test: Fresh Zo install path works end-to-end

---

## Phase 1: Inventory, Scope Lock, and Update Catalog

### Affected Files
- `N5/builds/ode-sync-2026-01-19b/UPDATE_CATALOG.md` - CREATE
- `N5/builds/ode-sync-2026-01-19b/PLAN.md` - UPDATE
- `N5/builds/ode-sync-2026-01-19b/workers/W1.*.md` - UPDATE
- `N5/export/n5os-ode/.gitignore` - UPDATE (fix `build/` ignore)

### Changes
1. **Create `UPDATE_CATALOG.md`** with per-file actions:
   - Source file (main N5) → destination file (Ode)
   - Action (ADD / UPDATE / DELETE / SKIP)
   - Rationale
   - Verification step
2. **Normalize context manifest location:** pick ONE canonical location used by bootloader + docs + repo.
   - Recommendation: `N5/config/context_manifest.yaml` (config belongs in config)
3. **`.gitignore` fix:** change `build/` → `/build/` to avoid ignoring `templates/build/`.

### Unit Tests / Verification
- `git check-ignore -v templates/build/plan_template.md` should return nothing
- `grep -R "N5/prefs/context_manifest"` in Ode repo should be 0 results (after normalization)

---

## Phase 2: Wave 1 Implementation (Workers)

### Affected Files (high level)
- `N5/export/n5os-ode/Prompts/Blocks/*.prompt.md`
- `N5/export/n5os-ode/Prompts/Blocks/Reflection/*.prompt.md`
- `N5/export/n5os-ode/N5/scripts/*.py`
- `N5/export/n5os-ode/N5/scripts/content_*.py`
- `N5/export/n5os-ode/N5/scripts/build_*.py`
- `N5/export/n5os-ode/BOOTLOADER.prompt.md`
- `N5/export/n5os-ode/docs/*`

### Unit Tests / Verification (per worker)
Each worker must include:
- `git diff` (summary of changes)
- A local verification command they ran
- A completion report written to `N5/builds/ode-sync-2026-01-19b/completions/<worker_id>.json`

---

## Phase 3: Integration, Review Gate, Release

### Orchestrator Verification Commands (run in Ode repo)
```bash
cd /home/workspace/N5/export/n5os-ode

git status
python3 scripts/validate_repo.py
python3 -m py_compile $(find N5 -name "*.py" -type f)

git check-ignore -v templates/build/plan_template.md || true

grep -R "TO BE FILLED\|\[TODAY\]\|con_XXXXX\|\[ORCHESTRATOR CONVERSATION ID\]" -n . || true
```

### Release Gate (requires your explicit go-ahead)
- Create branch + PR OR merge to main
- Push to GitHub

---

## Worker Briefs (Wave 1)

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Blocks delta sync | `workers/W1.1-blocks-delta-sync.md` |
| 1 | W1.2 | Reflection blocks delta sync | `workers/W1.2-reflection-blocks-delta-sync.md` |
| 1 | W1.3 | Build system sync + gitignore fix | `workers/W1.3-build-system-sync.md` |
| 1 | W1.4 | Content library sync | `workers/W1.4-content-library-sync.md` |
| 1 | W1.5 | Bootloader + docs alignment | `workers/W1.5-bootloader-docs-alignment.md` |
| 1 | W1.6 | Validation harness + smoke test | `workers/W1.6-validation-harness.md` |

---

## Success Criteria
1. Ode repo contains all updated blocks + reflections you intend to ship, with no V-specific leakage.
2. Ode repo build tooling matches current N5 build primitives (init_build/build_status/worker_complete/build_orchestrator behavior).
3. Ode repo content library scripts + docs are consistent and pass validation.
4. Fresh Zo install path works and does not silently skip required templates/files.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Drift between main N5 and Ode continues | Create a repeatable allowlist-driven sync-pack + validation harness |
| Hidden `.gitignore` exclusions | Fix ignore patterns + add `git check-ignore` to validation |
| Blocks contain V-specific assumptions | Sanitization pass + “portable-only” allowlist |
| Bootloader installs a different shape than repo | Align docs/paths, add prompt-reference checks |

---

## Level Upper Review
(TBD — invoke once Open Questions are answered.)
