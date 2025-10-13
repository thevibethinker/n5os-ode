# Lists System Investigation

## Issue Summary
1. **lists-create.md corrupted** - Has `\\n` escapes instead of newlines
2. **Dual-write failing** - shopping-list.md not updated after adding item
3. **Schema violation** - 42 commands have invalid workflow "single-shot"

## Root Cause Analysis

### Issue 1: lists-create.md Corruption
**File state:**
- Created: 2025-10-13 19:59:26 (just now, by docgen)
- Content: Has `\\n` instead of newlines throughout body

**Investigation:**
- n5_docgen.py reads from commands.jsonl
- commands.jsonl has lists-create with entire markdown content in "summary" field
- The summary field contains escaped newlines: `\\n`
- n5_docgen.py writes this directly to MD file without unescaping

**Root cause:** commands.jsonl entry for lists-create is malformed
- Workflow: "single-shot" (invalid)
- Summary: Contains entire doc content with escaped newlines
- Missing: proper structured fields (inputs, outputs, side_effects)

### Issue 2: Dual-Write Failure
**Expected behavior:**
- n5_lists_add.py adds item to JSONL
- Should trigger n5_lists_docgen.py to update MD

**Actual behavior:**
- Item added to shopping-list.jsonl ✓
- shopping-list.md NOT updated ✗

**Investigation needed:**
- Does n5_lists_add.py call n5_lists_docgen.py?
- If yes, why did it fail silently?
- If no, when is MD supposed to be regenerated?

### Issue 3: Schema Violation
**State:**
- 42/49 commands have workflow="single-shot"
- Valid workflows per schema: writing, research, data, ops, knowledge, lists, index, email, media, code, misc, automation
- "single-shot" not in valid list

**Impact:**
- n5_docgen.py schema validation fails
- Cannot regenerate command docs
- System is inconsistent

## Next Steps
1. Check if n5_lists_add.py includes dual-write call
2. Fix commands.jsonl schema violations (workflow field)
3. Restore lists-create.md to proper format
4. Test dual-write functionality
5. Document the fix to prevent recurrence
