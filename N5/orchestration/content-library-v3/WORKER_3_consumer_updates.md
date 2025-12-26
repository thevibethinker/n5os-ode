---
created: 2025-12-02
last_edited: 2025-12-02
version: 1
---
# Worker 3: Consumer Script Updates

**Orchestrator:** con_jYGYNfcv76UTmolk  
**Task ID:** W3-CONSUMERS  
**Estimated Time:** 40 minutes  
**Dependencies:** Worker 2 (CLI/API must be complete)

---

## Mission

Update all N5 scripts that import from the old content library to use the new v3 API. Create `.new` versions first, then swap.

---

## Context

Multiple N5 scripts import content library functions. They need to be updated to import from the new unified v3 location.

**Old import paths:**
- `from content_library import ContentLibrary`
- `from content_library_db import ...`
- Direct imports from `N5/scripts/content_library.py`

**New import path:**
```python
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3
```

---

## Dependencies

- Worker 2 complete: `content_library_v3.py` exists and works

---

## Deliverables

Create `.new` versions of each affected script:

1. `N5/scripts/email_composer.py.new`
2. `N5/scripts/knowledge_integrator.py.new`
3. `N5/scripts/auto_populate_content.py.new`
4. `N5/scripts/voice_transformer.py.new` (if applicable)
5. `N5/scripts/email_corrections.py.new` (if applicable)
6. `N5/scripts/document_media_curator.py.new` (if applicable)
7. `N5/scripts/content_library_db.py.new` (thin wrapper)

---

## Requirements

### Pattern for Updates

For each script:

1. **Find** lines importing old content library
2. **Replace** with v3 import
3. **Update** any API calls to match v3 interface
4. **Create** `.new` file

### Import Change Pattern

**Old:**
```python
from content_library import ContentLibrary
lib = ContentLibrary()
items = lib.search(tags={"audience": ["founders"]})
```

**New:**
```python
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()
items = lib.search(tags={"audience": "founders"})  # Note: tags is now Dict[str, str] not Dict[str, List[str]]
```

### API Differences to Handle

| Old API | New API | Notes |
|---------|---------|-------|
| `ContentLibrary()` | `ContentLibraryV3()` | Class rename |
| `search(tags={"k": ["v"]})` | `search(tags={"k": "v"})` | Tags simplified |
| `get_by_id(id)` | `get(id)` | Method rename |
| `mark_used(id)` | `mark_used(id)` | Same |
| `add(item_id=..., item_type=...)` | `add(id=..., item_type=...)` | Param rename |

---

## Implementation Guide

### Step 1: Identify Files to Update

```bash
# Find all files that import content_library
grep -r --include='*.py' -l 'content_library\|ContentLibrary' /home/workspace/N5/scripts/
```

### Step 2: For Each File

```bash
# Read original
cat /home/workspace/N5/scripts/<filename>.py

# Create .new with updated imports
# (see pattern below)
```

### Step 3: Template for Update

```python
#!/usr/bin/env python3
"""
<Original docstring>
"""

# === V3 CONTENT LIBRARY IMPORT ===
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3
# === END V3 IMPORT ===

# ... rest of original code with API calls updated ...
```

### Step 4: Create Thin Wrapper for Backwards Compat

Create `N5/scripts/content_library.py.new`:

```python
#!/usr/bin/env python3
"""
content_library.py - Backwards compatibility wrapper for v3

This is a thin wrapper that provides the old ContentLibrary interface
by delegating to ContentLibraryV3.

DEPRECATED: Use ContentLibraryV3 directly from:
  /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py
"""
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3

# Alias for backwards compatibility
ContentLibrary = ContentLibraryV3

# Re-export CLI functionality
if __name__ == "__main__":
    from content_library_v3 import main
    main()
```

---

## Files to Check and Update

Run this to find all affected files:

```bash
grep -r --include='*.py' -l 'content_library\|ContentLibrary' /home/workspace/N5/scripts/ 2>/dev/null
```

Expected files (verify each):
- `email_composer.py`
- `knowledge_integrator.py`
- `auto_populate_content.py`
- `voice_transformer.py`
- `email_corrections.py`
- `document_media_curator.py`
- `content_library_db.py`
- `content_library.py` (will become wrapper)

For each file:
1. Read current content
2. Identify import lines
3. Identify API usage patterns
4. Create `.new` with updates

---

## Testing

After creating `.new` files:

```bash
# Test wrapper import
python3 -c "from N5.scripts.content_library import ContentLibrary; print('Wrapper OK')"

# Test direct v3 import
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3
lib = ContentLibraryV3()
print(f'Stats: {lib.stats()}')
"

# For each updated script, verify it can be imported without error
python3 -c "import N5.scripts.email_composer" 2>/dev/null || echo "Needs fixing"
```

---

## Report Back

When complete, report:
1. ✅ List of `.new` files created
2. ✅ For each file: what imports were changed
3. ✅ Test results (imports work)
4. ✅ Any API incompatibilities discovered
5. ✅ Ready for cutover

---

**Orchestrator Contact:** con_jYGYNfcv76UTmolk  
**Created:** 2025-12-02 22:02 ET

