# Root Cause Analysis: Lists System Corruption

## Issues Identified

### 1. **lists-create.md Corruption**
**Symptom:** File contains `\\n` escape sequences instead of actual newlines
**Root Cause:** `n5_docgen.py` line 143+ writes command docs by reading from `commands.jsonl`, which had ALL markdown content stuffed into the `summary` field with escape sequences

### 2. **Dual-Write Failure**
**Symptom:** Adding items to lists only updated JSONL, not MD file
**Root Cause:** `n5_lists_add.py` did not call `n5_lists_docgen.py` after writing JSONL

### 3. **commands.jsonl Schema Violations**
**Symptom:** 42 commands had `workflow: "single-shot"` (invalid value)
**Root Cause:** Historical - commands were created with non-schema-compliant values

## How It Happened

**Timeline:**
1. Someone (likely an AI instance) incorrectly updated `commands.jsonl` entries by stuffing entire markdown documents into the `summary` field instead of using structured `inputs`, `outputs`, `side_effects` fields
2. `n5_docgen.py` read these malformed entries and generated corrupted `.md` files with `\\n` escapes
3. The dual-write was never implemented in `n5_lists_add.py`, so MD files only updated when manually running docgen

## Fixes Applied

✅ **Fixed commands.jsonl** - Restored proper structure with inputs/outputs fields (already applied via backup swap)
✅ **Added dual-write** - Modified `n5_lists_add.py` to call `n5_lists_docgen.py` after JSONL write
✅ **Restored lists-create.md** - Fixed escape sequences and YAML frontmatter

## Prevention

**Going forward:**
1. Schema validation should run on `commands.jsonl` before docgen
2. Dual-write pattern should be enforced in all list-modifying scripts
3. Backups created before all modifications (P5)
4. Never stuff markdown into JSON fields - use proper structured data

## Testing Needed

- [ ] Verify all command docs render correctly
- [ ] Test lists-add → confirm MD updates automatically
- [ ] Check other list-modifying commands (lists-set, lists-move, etc.) for dual-write
