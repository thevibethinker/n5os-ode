# Conversation-End File Consolidation Plan

**Date:** 2025-10-27  
**Issue:** Multiple duplicate/orphaned conversation-end files causing confusion

---

## Current State (Mess)

### Active Files (Keep)
1. ✅ `N5/prefs/operations/conversation-end.md` - **SSOT workflow doc** (v2.0.0)
2. ✅ `Recipes/System/Close Conversation.md` - **Recipe invocation file**
3. ✅ `N5/scripts/n5_conversation_end.py` - **Python implementation**
4. ✅ `N5/prefs/operations/conversation-end-cleanup-protocol.md` - **Cleanup protocol**

### Legacy/Duplicate Files (Action Needed)
5. 🗑️ `N5/commands/conversation-end.md` - **OLD command format** (pre-recipe migration)
6. 🗑️ `Documents/Archive/2025-10-27-Commands-Migration/Commands/Close Conversation.md` - Archive stub (minimal content)
7. 🗑️ `Documents/Deliverables/N5_Bootstrap_v1.0.0/N5_Bootstrap_Package_Extracted/commands/conversation-end.md` - Bootstrap export
8. 🗑️ `N5/exports/N5_Bootstrap_v1.0.0/N5_Bootstrap_Package_Extracted/commands/conversation-end.md` - Duplicate bootstrap

### Thread Artifacts (Leave Alone)
- Various CONVERSATION_END_SUMMARY.md files in N5/logs/threads/* - These are historical artifacts, not definitions

---

## Target State (Clean)

### Production Files
```
N5/prefs/operations/conversation-end.md          # SSOT: Full workflow doc
N5/prefs/operations/conversation-end-cleanup-protocol.md  # Cleanup protocol
N5/scripts/n5_conversation_end.py                # Implementation
Recipes/System/Close Conversation.md             # Recipe invocation
```

### Archives (Historical Only)
```
Documents/Archive/2025-10-27-Commands-Migration/  # Keep as historical record
Documents/Deliverables/*/                         # Keep as deliverables
N5/exports/*/                                     # Keep as exports
N5/logs/threads/*/                                # Keep as thread artifacts
```

---

## Cleanup Actions

### 1. Delete Obsolete Command File
**File:** `N5/commands/conversation-end.md`  
**Reason:** Migrated to recipe system, no longer used  
**Action:** DELETE

### 2. Clean Bootstrap Duplicates
**Files:**
- `Documents/Deliverables/N5_Bootstrap_v1.0.0/N5_Bootstrap_Package_Extracted/commands/conversation-end.md`
- `N5/exports/N5_Bootstrap_v1.0.0/N5_Bootstrap_Package_Extracted/commands/conversation-end.md`

**Reason:** Bootstrap exports should not contain individual command files after recipe migration  
**Action:** DELETE (they're in deliverable/export folders which are snapshots)

### 3. Update Recipe to Reference SSOT Only
**File:** `Recipes/System/Close Conversation.md`  
**Current:** References multiple files  
**Target:** Reference only `N5/prefs/operations/conversation-end.md`  
**Action:** SIMPLIFY

---

## Verification Checklist

After cleanup:
- [ ] Recipe references only SSOT workflow doc
- [ ] No orphaned command files in N5/commands/
- [ ] SSOT workflow doc is comprehensive and current
- [ ] Implementation script still functional
- [ ] No broken file references in system

---

## Implementation

**Safe order:**
1. Verify recipe still works with current setup
2. Delete obsolete command file
3. Clean bootstrap duplicates
4. Update recipe to reference SSOT only
5. Test recipe invocation
6. Verify no broken references

