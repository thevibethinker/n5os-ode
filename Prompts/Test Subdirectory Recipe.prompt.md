---
description: Test recipe to verify subdirectory organization works with Zo's slash invocation
tool: true
tags:
  - test
  - system
---
# Test Subdirectory Recipe

This is a test recipe located in `Recipes/System/` to verify that Zo's recipe system supports subdirectory organization.

**Test Instructions:**

1. Type `/` in Zo chat
2. Search for "test subdirectory"
3. Verify this recipe appears in autocomplete
4. Invoke it and confirm it loads

**Expected Result:**  
✅ Recipe loads successfully from subdirectory

**If This Works:**  
Subdirectory organization is supported and we can proceed with categorized recipe structure.

**If This Fails:**  
Revert to flat structure by moving all recipes back to `/home/workspace/Recipes/` root.

---

**Status:** Testing  
**Created:** 2025-10-27 00:36 ET
