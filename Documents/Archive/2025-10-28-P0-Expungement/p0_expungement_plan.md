# P0 Rule-of-Two Expungement Plan

## Status: COMPLETED - Core System Files Updated

**Completed:** 2025-10-28 01:28 ET  
**Files Updated:** 9 core system files  
**Archives Preserved:** All historical records intact

### Summary of Changes
- ✅ Removed P0 from architectural principles index
- ✅ Updated all active vibe builder persona files
- ✅ Cleaned protocol files (persona-management, style-guide)
- ✅ Updated Build Review recipe
- ✅ Cleaned planning prompt references
- ✅ Updated distributed build patterns
- ✅ Fixed task_deconstructor.py script comments
- ✅ Preserved all archives as historical record

## Philosophy
The Rule of Two was intended to prevent context overload but has become counterproductive. Modern context management should be handled through:
- Minimal Context (P8)
- Modular Design (P20)
- Dynamic judgment rather than rigid limits

## Strategy
1. **Remove entirely from active system files**
2. **Leave archives untouched** (historical record)
3. **Update all personas, protocols, and active documentation**
4. **Clean up n5os-core repo files**

---

## Files to Update (Priority Order)

### Critical System Files (Do First)
- [x] Knowledge/architectural/architectural_principles.md - Remove P0 from index
- [x] Documents/System/personas/vibe_builder_persona.md - Remove all P0 references
- [x] Knowledge/architectural/planning_prompt.md - Remove "Rule-of-Two" text
- [x] Knowledge/patterns/distributed_build_patterns.md - Remove pattern

### Protocol Files
- [x] N5/prefs/operations/persona-management-protocol.md - Update deprecation reference
- [x] N5/prefs/operations/style-guide-protocol.md - Remove P0 references

### Active Documentation
- [ ] Documents/N5.md - Remove P0 references
- [ ] Documents/System/PERSONAS_README.md - Update
- [ ] Documents/System/guides/*.md files
- [ ] Knowledge/architectural/principles/design.md - Remove reference
- [ ] Knowledge/personas/*.md files

### Recipes
- [x] Recipes/Build Review.md - Remove checklist item

### Scripts
- [x] N5/scripts/task_deconstructor.py - Remove P0 comments

### Bootstrap/Export Files
- [ ] VIBE_BUILDER_BOOTSTRAP.md - Already marked removed, clean up
- [ ] N5/exports/* - Update if not archived

---

## Files to SKIP (Archives - Historical Record)
- All files in Documents/Archive/*
- All files in N5/logs/threads/*
- All files in Inbox/*
- N5/lessons/archive/*
- Any file with date-stamped directory

---

## Verification
After updates, search for:
- "Rule-of-Two"
- "Rule of Two"  
- "P0" (in context of principles)

Should only appear in:
- Archive directories
- Log directories
- This expungement plan
