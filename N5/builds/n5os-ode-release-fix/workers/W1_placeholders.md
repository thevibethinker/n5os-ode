---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_oaJd6YmS7ETcg4UZ
worker_id: W1_placeholders
status: complete
dependencies: []
---
# Worker Assignment: W1_placeholders

**Project:** n5os-ode-release-fix  
**Component:** placeholder_fixes  
**Orchestrator:** con_oaJd6YmS7ETcg4UZ  
**Estimated time:** 30 minutes

---

## Objective

Fix all `PROJECT_REPO` placeholders in Python scripts and document the PyYAML dependency.

---

## Context

The n5os-ode export contains several Python scripts with placeholder URLs that need to be replaced with the actual GitHub repo URL. Additionally, the context loading script requires PyYAML but this isn't documented.

**Working directory:** `/home/workspace/N5/export/n5os-ode/`  
**Repo URL to use:** `https://github.com/vrijenattawar/n5os-ode`

---

## Tasks

### Task 1: Replace PROJECT_REPO Placeholders

Edit these 6 files, replacing `PROJECT_REPO` with `vrijenattawar`:

| File | Line | Current | Replace With |
|------|------|---------|--------------|
| `N5/scripts/n5_load_context.py` | ~12 | `https://github.com/PROJECT_REPO/n5os-ode` | `https://github.com/vrijenattawar/n5os-ode` |
| `N5/scripts/content_ingest.py` | ~11 | `https://github.com/PROJECT_REPO/n5os-ode` | `https://github.com/vrijenattawar/n5os-ode` |
| `N5/scripts/debug_logger.py` | ~15 | `https://github.com/PROJECT_REPO/n5os-ode` | `https://github.com/vrijenattawar/n5os-ode` |
| `N5/scripts/journal.py` | ~28 | `https://github.com/PROJECT_REPO/n5os-ode` | `https://github.com/vrijenattawar/n5os-ode` |
| `N5/scripts/n5_protect.py` | ~13 | `https://github.com/PROJECT_REPO/n5os-ode` | `https://github.com/vrijenattawar/n5os-ode` |
| `N5/scripts/session_state_manager.py` | ~19 | `https://github.com/PROJECT_REPO/n5os-ode` | `https://github.com/vrijenattawar/n5os-ode` |

**Approach:** Use `edit_file_llm` for each file to make the replacement.

### Task 2: Document PyYAML Dependency

Edit `docs/DEPENDENCIES.md` to add PyYAML under Python dependencies:

```markdown
## Python Dependencies

- **PyYAML** — Required for context loading (`pip install pyyaml`)
```

---

## Verification

Run these commands after completing tasks:

```bash
cd /home/workspace/N5/export/n5os-ode

# 1. No placeholders remain
rg "PROJECT_REPO" . && echo "FAIL" || echo "PASS: No placeholders"

# 2. Correct URL present
rg "vrijenattawar/n5os-ode" N5/scripts/ | wc -l
# Should return 6

# 3. PyYAML documented
grep -i "pyyaml" docs/DEPENDENCIES.md && echo "PASS: PyYAML documented"
```

---

## Handoff

When complete:
1. Report: "W1_placeholders complete. Replaced 6 placeholders, documented PyYAML."
2. List files modified
3. Paste verification output
4. Do NOT commit yet - W6 will handle all commits

---

## Files Reference

All paths relative to `/home/workspace/N5/export/n5os-ode/`:

**To edit:**
- `N5/scripts/n5_load_context.py`
- `N5/scripts/content_ingest.py`
- `N5/scripts/debug_logger.py`
- `N5/scripts/journal.py`
- `N5/scripts/n5_protect.py`
- `N5/scripts/session_state_manager.py`
- `docs/DEPENDENCIES.md`


