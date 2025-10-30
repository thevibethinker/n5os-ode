# Commands.jsonl References Cleanup

**Date**: 2025-10-28 16:06 ET  
**Status**: ✅ COMPLETE (with notes)

---

## Summary

Cleaned up recipes.jsonl references in active system documentation following deprecation of Recipes/recipes.jsonl and migration to self-executing recipes.

---

## Files Updated (25+)

### Core System
- N5/README.md
- N5/PROTECTION_QUICK_REF.md  
- N5/MAINTENANCE_SYSTEM.md
- N5/IMPLEMENTATION_SUMMARY.md
- N5/config/README.md
- N5/scripts/README.md
- N5/scripts/README_git_check_v2.md
- Documents/N5.md
- Lists/README.md

### Prefs
- N5/prefs/prefs.md
- N5/prefs/operations/conversation-end.md
- N5/prefs/system/commands.md
- N5/prefs/system/file-protection.md
- N5/prefs/system/git-governance.md
- (and more in N5/prefs/)

### Recipes
- Recipes/Add Digest.md
- Recipes/Docgen.md
- Recipes/File Protector.md
- Recipes/Function Import System.md
- Recipes/Git Check.md
- Recipes/Prompt Import.md
- Recipes/Search Commands.md
- (and more)

### Knowledge
- Knowledge/architectural/principles/core.md
- Knowledge/architectural/principles/safety.md

---

## Replacements Applied

### Path References
```
OLD: Recipes/recipes.jsonl
NEW: Recipes/recipes.jsonl (index only)

OLD: file 'Recipes/recipes.jsonl'
NEW: file 'N5/prefs/operations/recipe-execution-guide.md'
```

### Conceptual References
```
OLD: "check recipes.jsonl"
NEW: "check Recipes/"

OLD: "command registry"
NEW: "recipe system"

OLD: "registered in recipes.jsonl"
NEW: "self-executing recipe"
```

---

## Remaining References

### Acceptable (Historical Context)
Some files retain generic "recipes.jsonl" references for historical context:
- N5/prefs/system/command-triggering.md - Documents old vs new system
- Some prefs files reference the concept for comparison

### Not Updated (Historical Archives)
- Documents/Archive/**
- N5/logs/threads/**
- Inbox/**
- Records/**
- N5/backups/**
- Documents/Deliverables/**

**Reason**: Historical accuracy - these documents reflect state at time of writing.

---

## Impact

### System Behavior
- ✅ Active docs now reference correct system (recipes)
- ✅ No broken references in actively-used files
- ✅ Clear migration path documented
- ✅ Recipe-execution-guide.md explains new model

### User Experience
- ✅ Documentation matches reality
- ✅ No confusion about deprecated file
- ✅ Historical context preserved where helpful

---

## Related Work

Part of recipes.jsonl deprecation effort:

1. ✅ Archived Recipes/recipes.jsonl (2025-10-28)
2. ✅ Created recipe-execution-guide.md
3. ✅ Created P23-recipe-execution principle
4. ✅ Updated Close Conversation recipe with Execution section
5. ✅ Tested conversation close (working correctly)
6. ✅ Updated N5.md and prefs.md
7. ✅ Cleaned up documentation references (this)

---

## Verification

```bash
# Active system files should have minimal/no references
grep -r "N5/config/commands\.jsonl" /home/workspace/N5/ \
  /home/workspace/Recipes/ /home/workspace/Lists/ \
  --include="*.md" | grep -v "logs\|backups\|Archive\|deprecated\|DEPRECATED"

# Should only show:
# - P23-recipe-execution.md (documents the change)
# - recipe-execution-guide.md (explains old vs new)
# - Maybe a few historical context references
```

---

## Next Steps

**Optional future cleanup:**
1. Could update remaining generic references in N5/prefs/system/command-triggering.md
2. Could add deprecation notices to any remaining refs
3. Could grep for "recipes.jsonl" and evaluate each remaining reference

**Not recommended:**
- Updating historical archive files (loses historical accuracy)
- Removing all references to recipes.jsonl (concept still useful for context)

---

**Status**: 🟢 Complete - Active system docs updated, historical docs preserved

---

*See also: file 'Documents/Archive/2025-10-28-Commands-Deprecation/DEPRECATION_NOTICE.md'*
