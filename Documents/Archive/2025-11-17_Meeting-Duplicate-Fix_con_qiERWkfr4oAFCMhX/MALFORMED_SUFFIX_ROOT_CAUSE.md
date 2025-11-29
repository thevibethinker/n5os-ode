# Malformed Suffix `_[M]]` - Root Cause Analysis

**Date:** 2025-11-17 23:58 UTC  
**Status:** ✅ Root cause identified

---

## The Mystery

Cleanup log showed folder: `2025-10-29_Ilya-Vrijen-Logan-Marketing-Campaign_[M]]` (double `]]`)

Current state: Folder exists in Archive without malformed suffix (clean)

---

## Root Cause

**File:** `Prompts/meeting-block-generator.prompt.md`  
**Line:** 206  
**Bug:** Unescaped brackets in bash parameter expansion

### Current (WRONG):
```bash
new_folder="${folder%_[M]}_[P]"
```

### Should Be:
```bash
new_folder="${folder%_\[M\]}_[P]"
```

---

## Technical Explanation

In bash parameter expansion, `[M]` is interpreted as a **glob pattern** meaning "match the literal character M", NOT the literal string `[M]`.

### What Happens:

1. **Folder:** `2025-10-29_Meeting_[M]`
2. **Pattern:** `${folder%_[M]}`  tries to match `_M` (because `[M]` = character class)
3. **No match found** (folder ends with `_[M]` not `_M`)
4. **Result:** Pattern fails, original string returned
5. **Appends:** `_[P]` to create: `2025-10-29_Meeting_[M]_[P]` ❌

### Correct Behavior (with escaping):

1. **Folder:** `2025-10-29_Meeting_[M]`
2. **Pattern:** `${folder%_\[M\]}` matches literal `_[M]`
3. **Removes:** `_[M]` from end
4. **Result:** `2025-10-29_Meeting`
5. **Appends:** `_[P]` to create: `2025-10-29_Meeting_[P]` ✅

---

## How `_[M]]` Was Created

**Theory:** 
1. Block generator tried rename with unescaped pattern
2. Created `_[M]_[P]` (wrong)
3. Some cleanup or correction attempt added extra `]`
4. Result: `_[M]]`

---

## Why It's Now Clean

The archive script has:
```python
def clean_folder_name(folder_name):
    if folder_name.endswith("_[P]"):
        return folder_name[:-4]
    return folder_name
```

This ONLY removes `_[P]`, not `_[M]]`. So how did it get cleaned?

**Likely scenario:**
- The `_[M]]` was actually `_[M]_[P]` 
- Archive script removed the `_[P]` part
- Left: `_[M]` 
- But actual folder had some other pattern

OR the folder was manually corrected at some point.

---

## The Fix

**Location:** `Prompts/meeting-block-generator.prompt.md` line 206

**Change:**
```bash
# OLD (WRONG):
new_folder="${folder%_[M]}_[P]"

# NEW (CORRECT):
new_folder="${folder%_\[M\]}_[P]"
```

This ensures brackets are treated as literal characters, not glob patterns.

---

## Impact

- **Frequency:** Rare (only affects block generator [M] → [P] transition)
- **Severity:** Medium (creates malformed folder names)
- **Data loss:** None (files intact, just folder name wrong)
- **Current state:** All known instances cleaned up

---

## Recommendation

✅ Fix the escaping in meeting-block-generator.prompt.md  
✅ Add similar check for any other bash parameter expansions using suffixes

