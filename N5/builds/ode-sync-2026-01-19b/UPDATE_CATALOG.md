---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_bU6QDWx22wZGHG1Z
---

# Update Catalog: main N5 → N5OS Ode

**Purpose:** Maximum-detail, executable catalog of updates needed to sync Ode with your current N5 in the three scoped domains:
1) Blocks, 2) Build system/orchestrator, 3) Content Library.

> Source of truth for deltas: `N5/builds/ode-sync-2026-01-19b/inventory/`

---

## A. Blocks (Prompts/Blocks)

### A1. Blocks missing in Ode (add)
**Destination dir:** `N5/export/n5os-ode/Prompts/Blocks/`

Add these from `Prompts/Blocks/`:
- `Generate_B07.prompt.md`
- `Generate_B08.prompt.md`
- `Generate_B09.prompt.md`
- `Generate_B10.prompt.md`
- `Generate_B12.prompt.md`
- `Generate_B13.prompt.md`
- `Generate_B14.prompt.md`
- `Generate_B15.prompt.md`
- `Generate_B16.prompt.md`
- `Generate_B17.prompt.md`
- `Generate_B20.prompt.md`
- `Generate_B21.prompt.md`
- `Generate_B22.prompt.md`
- `Generate_B23.prompt.md`
- `Generate_B24.prompt.md`
- `Generate_B25.prompt.md`
- `Generate_B26.prompt.md`
- `Generate_B27.prompt.md`
- `Generate_B31.prompt.md`
- `Generate_B32.prompt.md`
- `Generate_B33.prompt.md`
- `Generate_B35.prompt.md`

**Action:** ADD (copy file as-is, then sanitize pass).

**Sanitize checklist:**
- Remove/rename any hard-coded company references or internal-only directory paths
- Ensure “file mention” syntax uses backticks consistently

**Verification:**
```bash
cd /home/workspace/N5/export/n5os-ode
for f in $(cat /home/workspace/N5/builds/ode-sync-2026-01-19b/inventory/blocks_missing_names.txt); do test -f "Prompts/Blocks/$f" && echo OK:$f || echo MISSING:$f; done
```

---

## B. Reflection Blocks (Prompts/Blocks/Reflection)

### B1. Reflection blocks missing in Ode (add)
**Destination dir:** `N5/export/n5os-ode/Prompts/Blocks/Reflection/`

Add these from `Prompts/Blocks/Reflection/`:
- `R00_Emergent.prompt.md`
- `R03_Strategic.prompt.md`
- `R04_Market.prompt.md`
- `R05_Product.prompt.md`
- `R07_Prediction.prompt.md`
- `R08_Venture.prompt.md`
- `R09_Content.prompt.md`
- `RIX_Integration.prompt.md`

**Action:** ADD + sanitize pass.

**Verification:**
```bash
cd /home/workspace/N5/export/n5os-ode
for f in $(cat /home/workspace/N5/builds/ode-sync-2026-01-19b/inventory/reflections_missing_names.txt); do test -f "Prompts/Blocks/Reflection/$f" && echo OK:$f || echo MISSING:$f; done
```

---

## C. Build System / Orchestration

### C1. Script deltas (update)
**Destination dir:** `N5/export/n5os-ode/N5/scripts/`

Update these scripts to match current main N5 behavior (per diff files in `inventory/diffs/`):
- `build_orchestrator_v2.py` (UPDATE)
- `init_build.py` (UPDATE)

**New scripts to add (present in main, not guaranteed in Ode):**
- `build_status.py` (ADD)
- `build_worker_complete.py` (ADD)

**Verification:**
- `python3 -m py_compile` passes for all added/updated scripts
- Running `python3 N5/scripts/init_build.py --help` prints the expected v2 orchestration options

### C2. `.gitignore` trap-door fix (update)
**File:** `N5/export/n5os-ode/.gitignore`

Problem: pattern `build/` ignores *any* `build/` directory, including `templates/build/`.

**Action:** UPDATE
- Change `build/` → `/build/`

**Verification:**
```bash
cd /home/workspace/N5/export/n5os-ode
git check-ignore -v templates/build/plan_template.md || true
```
Expected: no output.

---

## D. Content Library

### D1. Script deltas (update/add)
**Destination dir:** `N5/export/n5os-ode/N5/scripts/`

Update/add to match main N5 content library behavior:
- `content_ingest.py` (UPDATE) — big diff (~688 lines)
- `content_library.py` (ADD or UPDATE, depending if already shipped)
- `content_query.py` (ADD or UPDATE)

**Verification:**
- `python3 -m py_compile N5/scripts/content_*.py`
- `python3 N5/scripts/content_ingest.py --help` works

---

## E. Bootloader + Docs Alignment

### E1. Context manifest location consistency
Ensure bootloader + docs refer to the same canonical file path.

**Action:** either
- Create `N5/config/context_manifest.yaml` in repo (preferred), OR
- Update bootloader to create and use the existing path consistently.

**Verification:**
`grep -R "context_manifest" -n BOOTLOADER.prompt.md docs/ N5/ | sort`

---

## F. Validation Harness (non-negotiable before release)

Run:
```bash
cd /home/workspace/N5/export/n5os-ode
python3 scripts/validate_repo.py
python3 -m py_compile $(find N5 -name "*.py" -type f)

grep -R "TO BE FILLED\|\[TODAY\]\|con_XXXXX\|\[ORCHESTRATOR CONVERSATION ID\]" -n . || true
```

---

## Release Gate
No push to GitHub until you explicitly confirm.
