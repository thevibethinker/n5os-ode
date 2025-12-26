# Auto-Sync Strategy: V's N5 → GitHub

**Goal**: Keep n5os-core GitHub repo updated as V improves his N5 OS

---

## The Challenge

**V's system** (`/home/workspace/N5/`) evolves daily
**GitHub repo** (`vrijenattawar/n5os-core`) should stay current
**But**: Can't auto-push everything (privacy, proprietary workflows)

---

## Solution: Selective Export Script

### Architecture

```
V's N5 OS (source of truth)
    ↓
Export Script (filters to core only)
    ↓
n5os-core-staging/ (local, git-tracked)
    ↓
Manual review + push to GitHub
```

### What Gets Synced (Core 30)

**Commands** (30):
- `N5/commands/*.md` (whitelist of 30 core commands)

**Scripts** (6-8):
- `session_state_manager.py`
- `conversation_registry.py`
- `n5_git_check.py`
- `n5_index_rebuild.py`
- `n5_safety.py`
- `n5_conversation_end.py`

**Prefs** (25 core):
- System prefs (not personal)
- Core operational protocols

**Schemas** (16):
- All schemas (generic)

**Docs**:
- `zero_touch_manifesto.md`
- `architectural_principles.md`
- System docs (generic)

### What NEVER Syncs

❌ Personal data (Records/, exports/)
❌ Credentials
❌ Proprietary commands (meetings, Careerspan, etc.)
❌ Your specific workflows
❌ CRM data
❌ Intelligence files

---

## Implementation Options

### Option A: Manual Periodic Sync (Recommended)

**Frequency**: Monthly or when you make core improvements

**Process**:
```bash
# 1. Run export script
python3 /home/workspace/N5/scripts/export_core_to_github.py

# 2. Review changes
cd /path/to/n5os-core-staging
git status
git diff

# 3. Commit + push if good
git add -A
git commit -m "Update core from V's N5 OS (2025-10)"
git push origin main
```

**Pros**: Full control, review before publish
**Cons**: Manual step required

### Option B: Automated with Review

**Trigger**: Weekly cron job

**Process**:
1. Script runs Friday 6pm
2. Exports core changes
3. Creates PR on GitHub
4. Sends you email: "Review n5os-core updates"
5. You approve/reject PR

**Pros**: Automated but safe
**Cons**: Requires PR review setup

### Option C: Smart Diff + Auto-Push

**Trigger**: Daily check

**Logic**:
- Only pushes if core commands/scripts changed
- Skips if only personal files changed
- Auto-generates changelog
- Pushes directly to GitHub

**Pros**: Fully automated
**Cons**: Less control, riskier

---

## Recommended: Option A (Manual Monthly)

**Why**: 
- You iterate fast on your N5
- Core changes slowly
- Monthly sync keeps repo fresh without constant churn
- Full review before publishing

**Implementation**:
```python
#!/usr/bin/env python3
# export_core_to_github.py

CORE_COMMANDS = [
    "conversation-end.md",
    "thread-export.md",
    # ... all 30
]

CORE_SCRIPTS = [
    "session_state_manager.py",
    "n5_git_check.py",
    # ... core 6-8
]

def export_core():
    """Export core N5 components to staging directory"""
    # 1. Copy core commands
    # 2. Copy core scripts
    # 3. Copy generic prefs
    # 4. Update docs
    # 5. Generate changelog
    pass
```

---

## Changelog Generation

Auto-generate from git:
```bash
# In V's N5 repo
git log --since="30 days ago" --oneline -- \
  commands/{conversation,thread,knowledge,list}*.md \
  scripts/{session,git,index}*.py
```

Becomes:
```markdown
## Updates (2025-10)
- conversation-end: Added placeholder detection
- knowledge-add: Improved tagging
- session_state_manager.py: Bug fix for timezone handling
```

---

## Security Checks

Before any sync:
```python
def safety_check(file_path):
    """Ensure no sensitive data"""
    content = read_file(file_path)
    
    # Block if contains:
    if any(x in content for x in [
        "Careerspan",
        "vrijen@",
        "/home/workspace/Records",
        "credentials",
        # ... sensitive patterns
    ]):
        raise SecurityError(f"Sensitive data in {file_path}")
```

---

## Usage

**Monthly sync**:
```bash
# 1. Export
cd /home/workspace
python3 N5/scripts/export_core_to_github.py \
  --source /home/workspace/N5 \
  --dest /home/workspace/n5os-core-staging \
  --dry-run

# 2. Review
cd /home/workspace/n5os-core-staging
git diff

# 3. Push
git add -A
git commit -m "Monthly sync from V's N5 (2025-10-27)"
git push origin main
```

---

## Next Steps

1. Create `export_core_to_github.py` script
2. Test dry-run export
3. Set monthly calendar reminder
4. Document workflow in `CONTRIBUTING.md`

---

**Status**: Design complete, ready to implement  
**Recommended**: Option A (Manual Monthly)  
**Security**: Multi-layer checks  
**Date**: 2025-10-27
