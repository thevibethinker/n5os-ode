# Sandbox-First Artifact System — Quick Reference

## Core Concept

**All files created in sandbox by default. Workspace files require explicit declaration.**

---

## Quick Commands

### Declare Permanent Artifact
```bash
python3 /home/workspace/N5/scripts/session_state_manager.py declare-artifact \
  --convo-id {CURRENT_CONVO} \
  --path "path/to/file" \
  --classification permanent \
  --rationale "Why permanent"
```

### List Artifacts
```bash
# All artifacts
python3 /home/workspace/N5/scripts/session_state_manager.py list-artifacts --convo-id {CURRENT_CONVO}

# Only permanent
python3 /home/workspace/N5/scripts/session_state_manager.py list-artifacts --convo-id {CURRENT_CONVO} --classification permanent

# Only temporary
python3 /home/workspace/N5/scripts/session_state_manager.py list-artifacts --convo-id {CURRENT_CONVO} --classification temporary
```

### Update Status
```bash
python3 /home/workspace/N5/scripts/session_state_manager.py update-artifact \
  --convo-id {CURRENT_CONVO} \
  --path "path/to/file" \
  --status created
```

### Validate Path (Testing)
```bash
python3 /home/workspace/N5/scripts/sandbox_enforcer.py \
  "/home/workspace/some/file.txt" \
  --convo-id {CURRENT_CONVO}
```

---

## Decision Tree

```
Need to create a file?
├─ Iterative/scratch work? → Sandbox (no declaration)
├─ User deliverable? → Workspace (declare permanent)
├─ N5 component? → Workspace (declare permanent)
├─ Will need after conversation? → Workspace (declare permanent)
└─ Anything else? → Sandbox (default)
```

---

## Status Lifecycle

- **📋 declared** — Planned, not created yet
- **✅ created** — File successfully written
- **📦 moved** — Relocated to different path  
- **🗑️ deleted** — Removed

---

## Exception Paths (Always Allowed)

- `/home/workspace/N5/logs/`
- `/home/workspace/N5/data/`
- `/tmp/`

---

## Common Patterns

### Pattern 1: Analysis Script (Temp)
```python
# No declaration - just create in sandbox
create_or_rewrite_file(
    f"/home/.z/workspaces/{convo_id}/analyze.py",
    content=script
)
```

### Pattern 2: User Document (Permanent)
```python
# Declare
manager.declare_artifact(
    "Documents/report.md",
    "permanent",
    "User-requested analysis"
)

# Create
create_or_rewrite_file(
    "/home/workspace/Documents/report.md",
    content=report
)

# Update
manager.update_artifact_status("Documents/report.md", "created")
```

### Pattern 3: N5 Tool (Permanent)
```python
# Declare with flexible path
manager.declare_artifact(
    "N5/scripts/",  # AI picks specific name
    "permanent",
    "New utility for X workflow"
)

# Create
create_or_rewrite_file(
    "/home/workspace/N5/scripts/new_tool.py",
    content=code
)

# Update
manager.update_artifact_status("N5/scripts/new_tool.py", "created")
```

---

## What Happens If...

**Q: I forget to declare and try to create in workspace?**  
A: ⛔ SANDBOX VIOLATION error with remediation steps

**Q: I declare but never create?**  
A: Artifact stays in "declared" status, reviewable at conversation-end

**Q: I need to move a file from sandbox to workspace?**  
A: Declare it permanent, copy (don't move to preserve original), update status to "moved"

**Q: I'm not sure if file should be temp or permanent?**  
A: Default to temp (sandbox). Can always promote later.

---

## Full Documentation

- **Protocol**: `file 'N5/prefs/operations/artifact-placement.md'`
- **Enforcer**: `file 'N5/scripts/sandbox_enforcer.py'`
- **Manager**: `file 'N5/scripts/session_state_manager.py'`
- **Prefs Rule**: `file 'N5/prefs/prefs.md'` → Safety & Review section
