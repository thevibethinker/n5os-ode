# Recipes Migration: Next Actions
**Date:** 2025-10-27 00:32 ET  
**Priority:** High → Low

---

## Immediate Actions (Do Now)

### 1. Test Recipes in Zo UI ⚡
**Why:** Verify slash invocation works correctly

**How:**
1. Open Zo chat
2. Type `/` in message input
3. Confirm recipe autocomplete menu appears
4. Test invoking 2-3 recipes
5. Verify AI loads and executes correctly

**Test These:**
- `/browse-recipes` (new)
- `/analyze-meeting` (migrated)
- `/safety-check` (migrated)

---

### 2. Archive Commands/ Folder 📦
**Why:** Clean up old structure, preserve history

**Command:**
```bash
mkdir -p /home/workspace/Documents/Archive/
mv /home/workspace/Commands /home/workspace/Documents/Archive/Commands-2025-10-27
```

**Validation:**
```bash
ls /home/workspace/Recipes/*.md | wc -l  # Should be 13
ls /home/workspace/Documents/Archive/Commands-2025-10-27/*.md | wc -l  # Should be 11
```

---

## Short-term Actions (This Week)

### 3. Fix Naming Inconsistency 🏷️
**Issue:** spawn-worker.md uses kebab-case, others use Title Case

**Fix:**
```bash
cd /home/workspace/Recipes
mv "spawn-worker.md" "Spawn Worker.md"
```

---

### 4. Fix Typo in Close Conversation 📝
**Issue:** "Wrap up converseation" → "conversation"

**Fix:** Ask me to: "Fix the typo in `file 'Recipes/Close Conversation.md'`"

---

### 5. Enhance Recipe Metadata 🎯
**Issue:** Some recipes lack tags or have minimal descriptions

**Update These:**

**Resume.md:**
```yaml
---
description: Resume operations after connection drops or errors. Provides context about previous state.
tags:
  - error-recovery
  - system
  - troubleshooting
---
```

**Close Conversation.md:**
```yaml
---
description: Wrap up conversation with proper closure protocol
tags:
  - session
  - cleanup
  - organization
---
```

---

## Medium-term Actions (Next 2 Weeks)

### 6. Test Subdirectory Organization 📂
**Question:** Does Zo support `Recipes/Category/Recipe.md`?

**Proposed Structure:**
```
Recipes/
├── Meetings/
│   ├── Analyze Meeting.md
│   └── Export Thread.md
├── Knowledge/
│   ├── Process to Knowledge.md
│   └── Quick Classify.md
├── System/
│   ├── Build Review.md
│   ├── Safety Check.md
│   ├── Resume.md
│   └── Browse Recipes.md
└── Tools/
    ├── Create Tally Survey.md
    └── Spawn Worker.md
```

**Test:** Create test subdirectory and verify slash invocation still works

---

### 7. Update N5 References to Recipes 🔗
**Search for old paths:**
```bash
grep -r "Commands/" /home/workspace/N5/ --include="*.md" --include="*.py"
```

**Update these files:**
- `file 'N5/commands/manage-drafts.md'`
- Any scripts with hardcoded paths
- Documentation references

---

### 8. Create Additional Discovery Recipes 🔍

**Search Recipes.md:**
```yaml
---
description: Search recipes by keyword, tag, or description
tags:
  - recipes
  - search
  - discovery
---
```

**Recent Recipes.md:**
```yaml
---
description: Show recently used recipes and usage patterns
tags:
  - recipes
  - analytics
  - history
---
```

---

## Long-term Actions (Next Month)

### 9. Decision: recipes.jsonl Future 🤔
**Options:**
1. **Keep as-is** - Internal registry separate from Recipes
2. **Update paths** - Point to Recipes/ instead of Commands/
3. **Deprecate** - Rely purely on Recipes/ for everything
4. **Hybrid** - System commands in jsonl, user workflows in Recipes

**Recommendation:** Option 4 (Hybrid) - keeps separation of concerns

---

### 10. Create Recipe Development Guide 📚
**Contents:**
- Recipe template
- YAML frontmatter standards
- Naming conventions
- Tag taxonomy
- Best practices
- Testing checklist

**Location:** `file 'Documents/System/RECIPE_DEVELOPMENT_GUIDE.md'`

---

### 11. Build Recipe Usage Analytics 📊
**Track:**
- Which recipes are used most
- Which recipes are never used (candidates for archiving)
- Usage patterns over time
- Success/failure rates

**Implementation:** Log to N5/data/recipe_usage.jsonl

---

## Questions for V

1. **Commands/ folder:** Archive or delete entirely?
2. **Subdirectories:** Want to test category-based organization?
3. **recipes.jsonl:** Keep, update, or deprecate?
4. **Recipe discovery:** Want more sophisticated search/analytics?
5. **Documentation:** Need recipe development guide now or later?

---

## References

- `file 'Documents/System/RECIPES_MIGRATION_COMPLETE.md'` - Full summary
- `file '/home/.z/workspaces/con_uVnpAD6W1XKczbee/RECIPES_ALIGNMENT_GUIDE.md'` - Architecture
- `file 'Recipes/'` - All recipes (13 total)
- `file 'Documents/N5.md'` - System overview

---

## Quick Commands

**List all recipes:**
```bash
ls -1 /home/workspace/Recipes/*.md | xargs -n1 basename
```

**Count recipes:**
```bash
ls /home/workspace/Recipes/*.md | wc -l
```

**Search recipe content:**
```bash
grep -h "description:" /home/workspace/Recipes/*.md
```

**Test recipe in Zo:**
Type `/recipe-name` in chat

---

**Last Updated:** 2025-10-27 00:32 ET  
**Status:** Ready for action
