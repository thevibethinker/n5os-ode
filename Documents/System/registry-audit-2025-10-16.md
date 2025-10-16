# Registry Integrity Audit & Fixes
**Date:** 2025-10-16  
**Status:** ✅ Complete

## Root Cause
Dual list systems with inconsistent path references:
- **Main Registry:** `/home/workspace/Lists/index.jsonl` (user-facing, used by Zo interface)
- **N5 Registry:** `/home/workspace/N5/lists/index.jsonl` (script-facing, used by CLI tools)

Many lists existed in `Lists/` but the main registry incorrectly pointed to `N5/lists/`.

## Issues Found & Fixed

### 1. Lists Index Path Mismatches (/home/workspace/Lists/index.jsonl)
**Fixed 4 incorrect path references:**
- `phase3-test`: `N5/lists/` → `Lists/`
- `ideas`: `N5/lists/` → `Lists/`
- `squawk`: `N5/lists/` → `Lists/`
- `must-contact`: `N5/lists/` → `Lists/`

**Removed obsolete `path_md` fields from 5 entries** (per user note: no longer using markdown views)

### 2. Commands Registry Corruption (/home/workspace/N5/config/commands.jsonl)
**Fixed 3 data integrity issues:**
- Line 60: Removed malformed entry starting with literal `\n`
- Lines 71, 73: Removed duplicate `unsent-followups-digest` command
- Lines 72, 74: Removed duplicate `drop-followup` command

### 3. N5 Registry Sync
**Added 5 missing lists to N5 registry** so CLI scripts can discover them:
- `phase3-test`
- `ideas`
- `squawk`
- `must-contact`
- `pending-knowledge-updates`

## Verification Results

✅ **Lists Index:** All paths now point to existing files, no `path_md` fields remain  
✅ **Commands Registry:** No duplicates or malformed entries  
✅ **N5 Scripts:** Can now discover and operate on all lists  
✅ **CRM Index:** Clean (no issues found)

## Files Modified
- `/home/workspace/Lists/index.jsonl` (path corrections, removed path_md)
- `/home/workspace/N5/config/commands.jsonl` (removed duplicates/malformed)
- `/home/workspace/N5/lists/index.jsonl` (added missing list references)

## Backups Created
All modified files backed up to:
`/home/workspace/Documents/Backups/registry-fixes-20251016/`

## Script Used
Fix script: `file '/home/.z/workspaces/con_L0DkAPUAN9FVVDqC/registry_fixes.py'`

## Prevention
**Design Pattern Identified:** When registries point to filesystem paths, enforce validation:
1. On registry write: verify target path exists
2. On registry read: log/warn on missing paths
3. Maintain single source of truth for paths (consider symlinks or path resolution layer)

**Recommendation:** Add a registry validation script to periodic maintenance tasks that checks:
- All referenced paths exist
- No duplicate entries in registries
- No malformed JSON
- Cross-registry consistency (Lists/index.jsonl ↔ N5/lists/index.jsonl)

## Future Considerations
1. **Registry consolidation:** Consider merging the two index files or establishing clear ownership
2. **Path validation:** Add pre-commit or scheduled validation
3. **Schema enforcement:** Use JSON schema validation on all registry operations
4. **Automated tests:** Add tests that verify registry integrity before/after operations
