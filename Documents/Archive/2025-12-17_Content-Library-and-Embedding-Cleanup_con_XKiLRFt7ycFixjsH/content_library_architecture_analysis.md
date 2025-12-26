---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_XKiLRFt7ycFixjsH
---

# Content Library Architecture Analysis

## Current State (Fragmented)

### Databases
| Location | Status | Items | Purpose |
|----------|--------|-------|---------|
| `N5/data/content_library.db` | **CANONICAL** | 121 | Links, snippets - actively used |
| `Personal/Knowledge/ContentLibrary/content-library-v3.db` | QUARANTINED | 80 | Was v3 attempt |
| `Personal/Knowledge/ContentLibrary/content-library.db` | QUARANTINED | 16 | Ancient |

### Scripts (Problematic Coupling)
| Script | Points To | Problem |
|--------|-----------|---------|
| `N5/scripts/content_library.py` | Personal/...v3.py | Wrapper to quarantined location |
| `N5/scripts/content_library_db.py` | Personal/...v3.py | Same problem |
| `Personal/.../content_library_v3.py` | v3.db (quarantined) | DB moved |
| `N5/scripts/migrate_content_library_to_db.py` | N5/data/ | Correct |

### Active Users of Content Library
Scripts that import from Personal/Knowledge/ContentLibrary/scripts:
- `auto_populate_content.py`
- `b_block_parser.py`
- `content_library.py`
- `content_library_db.py`
- `email_composer.py`
- `email_corrections.py`
- several more...

## Fix Options

### Option A: Redirect v3.py to canonical DB
- Update `Personal/.../content_library_v3.py` DB_PATH → `N5/data/content_library.db`
- Keep existing import structure
- Minimal changes, some tech debt remains

### Option B: Consolidate to N5/scripts (Clean)
- Move `content_library_v3.py` → `N5/scripts/content_library_unified.py`
- Update all imports
- Remove Personal/Knowledge/ContentLibrary entirely
- Clean architecture

### Option C: Hybrid (Recommended)
- Update `Personal/.../content_library_v3.py` to use canonical DB (quick fix)
- Create TODO for full consolidation later
- Document tech debt

## Recommendation
Option C - quick fix now, document debt for proper cleanup later.

