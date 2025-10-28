# Bug Fix: Incorrect Meeting Folder Naming Convention

**Date:** 2025-10-27  
**Severity:** Medium  
**Status:** ✅ Fixed  
**Fix Time:** 15 minutes

---

## Problem

Profile enrichment system was creating meeting profile folders in the wrong format:

**Incorrect format (what was created):**
```
N5/records/meetings/2025-10-28/jake/profile.md
N5/records/meetings/2025-10-28/ray/profile.md
N5/records/meetings/2025-10-28/shivani/profile.md
N5/records/meetings/2025-10-27/lanoble/profile.md
```

**Correct format (per stakeholder_profile_manager.py):**
```
N5/records/meetings/2025-10-28-jake-fohe/profile.md
N5/records/meetings/2025-10-28-ray-fohe/profile.md
N5/records/meetings/2025-10-28-shivani-fohe/profile.md
N5/records/meetings/2025-10-27-lanoble-colby/profile.md
```

---

## Root Cause

During scheduled task execution (con_LoMl7HXO5ZzSPDtB) on 2025-10-27 at 09:09 AM ET, Zo generated **inline Python code** that created profile directories using wrong naming convention:

1. **Used `/` separators** instead of `-` hyphens
2. **Missing organization/domain** part from email address  
3. **Created date-only parent folders** (2025-10-28, 2025-10-27) that pollute meetings directory

### Evidence

From `N5/logs/meeting_monitor.log`:
```
=== Cycle started at 2025-10-27T09:09:49.422161-04:00 ===
Created profile: /home/workspace/N5/records/meetings/2025-10-27/lanoble/profile.md
  Meeting: Lisa Noble x Vrijen | Attendee: lanoble@colby.edu
  Tags: AWA
Created profile: /home/workspace/N5/records/meetings/2025-10-28/jake/profile.md
  Meeting: FOHE x Careerspan | Attendee: jake@fohe.org
  Tags: LD-COM, OFF, D5, LOG, GPT-E
...
```

The "Created profile:" message format doesn't match any existing Python script in `N5/scripts/`. This indicates **inline code generation during scheduled task execution**.

---

## Impact

1. **Folder Structure Pollution:** Date folders cluttered meetings directory
2. **Profile Discovery Failures:** Enrichment systems couldn't find profiles
3. **Convention Violations:** Broke established N5 meeting folder naming standard
4. **Duplication Risk:** Multiple profiles could be created for same meeting

---

## Fix Applied

### 1. Migrated Existing Profiles

Moved 4 mis-created profiles to correct format:

```python
# Migration executed
jake@fohe.org:     2025-10-28/jake     → 2025-10-28-jake-fohe
ray@fohe.org:      2025-10-28/ray      → 2025-10-28-ray-fohe
shivani@fohe.org:  2025-10-28/shivani  → 2025-10-28-shivani-fohe
lanoble@colby.edu: 2025-10-27/lanoble  → 2025-10-27-lanoble-colby
```

Empty date folders (2025-10-28, 2025-10-27) removed after migration.

### 2. Created Validation Script

**File:** `N5/scripts/validate_meeting_folder_names.py`

**Features:**
- Scans meetings directory for naming violations
- Detects date-only folders with subfolders
- Auto-fix capability with dry-run mode
- Extracts email/org from profile.md to construct correct names

**Usage:**
```bash
# Check for violations
python3 N5/scripts/validate_meeting_folder_names.py

# Preview fixes
python3 N5/scripts/validate_meeting_folder_names.py --fix --dry-run

# Apply fixes
python3 N5/scripts/validate_meeting_folder_names.py --fix
```

---

## Prevention Measures

### Rule for Zo

When creating meeting profile folders, **ALWAYS**:

1. Use `stakeholder_profile_manager.create_stakeholder_profile()` function
2. **Never** create profiles with inline code during scheduled tasks
3. Follow naming convention: `YYYY-MM-DD-name-organization`
   - Extract name from email: `email.split('@')[0]`
   - Extract org from domain: `email.split('@')[1].split('.')[0]`
   - Use `-` hyphens, not `/` slashes

### Correct Code Pattern

```python
from pathlib import Path

def create_meeting_profile_dir(meeting_date: str, attendee_email: str) -> Path:
    """
    Create properly-named meeting profile directory.
    
    Args:
        meeting_date: "YYYY-MM-DD" format
        attendee_email: "name@organization.com"
        
    Returns:
        Path to profile directory
    """
    name = attendee_email.split('@')[0]
    domain = attendee_email.split('@')[1]
    org = domain.split('.')[0]
    
    # CORRECT: Use hyphens, include all parts
    dir_name = f"{meeting_date}-{name}-{org}"
    
    # WRONG: dir_name = f"{meeting_date}/{name}"  # ❌ Never do this
    
    profile_dir = Path("/home/workspace/N5/records/meetings") / dir_name
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    return profile_dir
```

### Add to File Guardian

Consider adding to `N5/scripts/maintenance/daily_guardian.py`:
```python
# Validate meeting folder names
from validate_meeting_folder_names import scan_meetings_directory

valid, invalid = scan_meetings_directory()
if invalid:
    alert("Meeting folder naming violations detected", severity="medium")
```

---

## Testing

### Validation Results

```bash
$ python3 N5/scripts/validate_meeting_folder_names.py

=== Meeting Folder Name Validation ===
Scanning: /home/workspace/N5/records/meetings

✓ Valid folders: 54
✗ Invalid folders: 0

✅ All meeting folders follow correct naming convention
```

### Profile Content Verification

```bash
$ head -5 N5/records/meetings/2025-10-28-jake-fohe/profile.md
# Stakeholder Profile: jake@fohe.org

## Meeting Information
- **Event**: FOHE x Careerspan
- **Date**: October 28, 2025 at 11:00 AM ET
```

✅ Profiles preserved correctly during migration

---

## Lessons Learned

1. **Inline code generation is risky** – Prefer calling existing functions from scripts
2. **Validation scripts are valuable** – Can catch similar issues early
3. **Convention documentation matters** – stakeholder_profile_manager.py had correct pattern, but wasn't being used
4. **Log analysis is powerful** – Timestamps and log formats revealed exact cause

---

## Related Files

- `N5/scripts/validate_meeting_folder_names.py` (new)
- `N5/scripts/stakeholder_profile_manager.py` (reference implementation)
- `N5/logs/meeting_monitor.log` (evidence)
- `N5/records/meetings/` (affected directory)

---

## Recommendation

**Update "Gdrive Meeting Pull" scheduled task** to use `stakeholder_profile_manager.create_stakeholder_profile()` instead of inline profile creation code.

---

**Fixed by:** Vibe Builder (con_zqfzTLQnf2stCMv5)  
**Verified:** 2025-10-27 11:44 ET
