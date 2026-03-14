---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_oaJd6YmS7ETcg4UZ
worker_id: W2_init_build_script
status: complete
dependencies: []
---
# Worker Assignment: W2_init_build_script

**Project:** n5os-ode-release-fix  
**Component:** init_build_script  
**Orchestrator:** con_oaJd6YmS7ETcg4UZ  
**Estimated time:** 30 minutes

---

## Objective

Create the `init_build.py` script that the Build Capability prompt references but doesn't exist.

---

## Context

The `Prompts/Build Capability.prompt.md` in n5os-ode references `N5/scripts/init_build.py` to initialize build workspaces. This script needs to be created with minimal, functional implementation.

**Working directory:** `/home/workspace/N5/export/n5os-ode/`

---

## Task: Create init_build.py

Create `/home/workspace/N5/export/n5os-ode/N5/scripts/init_build.py` with these requirements:

### CLI Interface
```
python3 N5/scripts/init_build.py <slug> --title "<Title>"
```

### Functionality
1. Accept positional `slug` argument (e.g., `my-feature`)
2. Accept `--title` optional argument (defaults to slug if not provided)
3. Create directory structure at `N5/builds/<slug>/`:
   ```
   N5/builds/<slug>/
   ├── PLAN.md          # Build plan template
   ├── STATUS.md        # Progress tracker  
   └── artifacts/       # Output directory
   ```
4. Print confirmation message with path

### PLAN.md Template
```markdown
---
created: {date}
last_edited: {date}
version: 1
---
# {title}

## Objective

[Describe the build objective]

## Tasks

- [ ] Task 1
- [ ] Task 2

## Success Criteria

- [ ] Criterion 1
```

### STATUS.md Template
```markdown
---
created: {date}
last_edited: {date}
---
# {title} - Status

**Status:** In Progress  
**Started:** {date}

## Progress

| Task | Status | Notes |
|------|--------|-------|
| - | - | - |

## Blockers

None

## Next Steps

1. Define tasks in PLAN.md
```

### Script Requirements
- Use `argparse` for CLI
- Use `pathlib` for paths
- Handle existing directory (warn, don't overwrite)
- Exit codes: 0 success, 1 error
- No external dependencies beyond stdlib

---

## Reference Implementation

Here's the expected structure (you write the actual implementation):

```python
#!/usr/bin/env python3
"""Initialize a build workspace for N5OS-Ode.

Usage:
    python3 N5/scripts/init_build.py <slug> --title "Build Title"
    
Creates:
    N5/builds/<slug>/
    ├── PLAN.md
    ├── STATUS.md
    └── artifacts/
"""
import argparse
from datetime import datetime
from pathlib import Path
import sys

# Script info
__version__ = "1.0.0"
REPO_URL = "https://github.com/vrijenattawar/n5os-ode"

def main():
    # Your implementation here
    pass

if __name__ == "__main__":
    main()
```

---

## Verification

After creating the script:

```bash
cd /home/workspace/N5/export/n5os-ode

# 1. Script is executable Python
python3 -m py_compile N5/scripts/init_build.py && echo "PASS: Compiles"

# 2. Help works
python3 N5/scripts/init_build.py --help

# 3. Creates structure correctly
python3 N5/scripts/init_build.py verify-test --title "Verification Test"
ls -la N5/builds/verify-test/

# 4. PLAN.md exists with content
cat N5/builds/verify-test/PLAN.md

# 5. STATUS.md exists with content  
cat N5/builds/verify-test/STATUS.md

# 6. artifacts/ directory exists
test -d N5/builds/verify-test/artifacts && echo "PASS: artifacts dir exists"

# 7. Cleanup test directory
rm -rf N5/builds/verify-test
```

---

## Handoff

When complete:
1. Report: "W2_init_build_script complete. Created N5/scripts/init_build.py"
2. Paste the full script content
3. Show verification output
4. Do NOT commit yet - W6 will handle all commits

---

## Files Reference

**To create:**
- `/home/workspace/N5/export/n5os-ode/N5/scripts/init_build.py`

**May need to create directory:**
- `/home/workspace/N5/export/n5os-ode/N5/builds/` (if doesn't exist)


