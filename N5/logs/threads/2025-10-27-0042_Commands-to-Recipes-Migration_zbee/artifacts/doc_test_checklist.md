# Recipes Subdirectory Testing Checklist
**Date:** 2025-10-27 00:37 ET  
**Status:** Ready for Testing

---

## New Structure

```
Recipes/
├── Meetings/
│   ├── Analyze Meeting.md
│   ├── Export Thread.md
│   └── Session Review.md
├── Knowledge/
│   ├── Process to Knowledge.md
│   └── Quick Classify.md
├── System/
│   ├── Build Review.md
│   ├── Safety Check.md
│   ├── Resume.md
│   ├── Browse Recipes.md
│   ├── Close Conversation.md
│   ├── Emoji Legend.md
│   └── Test Subdirectory Recipe.md ← TEST RECIPE
└── Tools/
    ├── Create Tally Survey.md
    └── Spawn Worker.md
```

**Total:** 14 recipes across 4 categories

---

## Test Protocol

### Phase 1: Basic Discovery ✅ (Do First)

**Test 1.1:** Slash Invocation
```
Action: Type "/" in Zo chat
Expected: Recipe autocomplete menu appears
Pass/Fail: [ ]
```

**Test 1.2:** Autocomplete Shows All Recipes
```
Action: Scroll through autocomplete list
Expected: All 14 recipes visible regardless of subdirectory
Pass/Fail: [ ]
```

**Test 1.3:** Search Filtering
```
Action: Type "/test" 
Expected: "Test Subdirectory Recipe" appears
Pass/Fail: [ ]
```

---

### Phase 2: Recipe Loading ✅ (After Phase 1)

**Test 2.1:** Load from Subdirectory
```
Action: Invoke "/test-subdirectory-recipe"
Expected: Recipe loads successfully from System/
Pass/Fail: [ ]
```

**Test 2.2:** Load Multiple Categories
```
Action: Invoke one recipe from each category:
  - /analyze-meeting (Meetings/)
  - /quick-classify (Knowledge/)
  - /safety-check (System/)
  - /spawn-worker (Tools/)
Expected: All load correctly
Pass/Fail: [ ]
```

**Test 2.3:** Updated Recipes Work
```
Action: Invoke "/resume" and "/close-conversation"
Expected: Updated descriptions show correctly
Pass/Fail: [ ]
```

---

### Phase 3: Functionality ✅ (After Phase 2)

**Test 3.1:** Recipe Execution
```
Action: Fully execute 2-3 recipes
Expected: Recipes work as before migration
Pass/Fail: [ ]
```

**Test 3.2:** File References Resolve
```
Action: Invoke recipe with file references (e.g., Analyze Meeting)
Expected: AI loads referenced files correctly
Pass/Fail: [ ]
```

---

## Decision Matrix

### ✅ If All Tests Pass
**Action:** Keep subdirectory structure
**Update:** Browse Recipes.md to scan subdirectories
**Document:** Add to N5.md and system docs

### ⚠️ If Phase 1 Fails (Discovery Issues)
**Symptom:** Recipes don't appear in autocomplete
**Action:** Move all recipes back to flat structure
**Command:**
```bash
cd /home/workspace/Recipes
mv */*.md .
rmdir Meetings Knowledge System Tools
```

### ⚠️ If Phase 2 Fails (Loading Issues)
**Symptom:** Recipes appear but won't load
**Action:** Same as Phase 1 failure - revert to flat

### ⚠️ If Phase 3 Fails (Execution Issues)
**Symptom:** Recipes load but don't work correctly
**Action:** Check file path references, update if needed
**May need:** Update relative paths in recipe content

---

## Rollback Command (If Needed)

```bash
# Revert to flat structure
cd /home/workspace/Recipes
find . -name "*.md" -mindepth 2 -exec mv {} . \;
rm -rf Meetings Knowledge System Tools
echo "✓ Reverted to flat structure"
```

---

## What to Tell Me After Testing

**Format:**
```
✅ Phase 1: [PASS/FAIL]
✅ Phase 2: [PASS/FAIL]  
✅ Phase 3: [PASS/FAIL]

Notes: [Any observations]
Decision: [Keep subdirs / Revert to flat]
```

---

## Additional Notes

- **Test recipe** can be deleted after verification
- **Flat structure** is safer but less organized
- **Subdirectory structure** is cleaner but depends on Zo support
- Can always **revert later** if issues emerge

---

**Status:** Ready for V to test  
**Next:** V tests in Zo UI, reports results  
**Then:** Keep or revert based on results

---

**Created:** 2025-10-27 00:37 ET
