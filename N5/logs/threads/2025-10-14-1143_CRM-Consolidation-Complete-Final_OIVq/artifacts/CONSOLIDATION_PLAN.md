# CRM Profile Consolidation - Ready to Execute

## Problem Summary

Two profile directories exist in your CRM:
- `Knowledge/crm/individuals/` (4 files) - **Canonical location** per documentation
- `Knowledge/crm/profiles/` (57 files) - Legacy location

This happened because different scripts write to different locations:
- ✅ **Networking event processor** → writes to `individuals/` (correct)
- ❌ **CRM query tool** → writes to `profiles/` (incorrect)
- ❌ **B08 sync script** → reads from `profiles/` (incorrect)

## Solution Ready to Deploy

**Script:** `file '/home/.z/workspaces/con_9hza8oR18GLpOIVq/consolidate_crm_profiles.py'`

### What It Will Do

**Phase 1: Update Scripts**
- Fix `N5/scripts/crm_query.py` to write to `individuals/`
- Fix `N5/scripts/sync_b08_to_crm.py` to read from `individuals/`
- Creates automatic backups before modifying

**Phase 2: Migrate Profiles**
- Copy 55 profiles from `profiles/` → `individuals/`
- Skip 2 conflicts (alex-caveny, carly-ackerman) - newer versions already in `individuals/`
- Preserves originals until Phase 4

**Phase 3: Update Database**
- Update 57 database records to point to new `individuals/` paths
- Changes `markdown_path` from `Knowledge/crm/profiles/...` → `Knowledge/crm/individuals/...`

**Phase 4: Archive Old Directory**
- Move entire `profiles/` → `.archived_profiles_20251014`
- Creates README explaining the archive

## Conflicts Detected

**2 profiles exist in both locations** (newer `individuals/` version will be kept):

1. **alex-caveny.md**
   - `profiles/`: 1,084 bytes (Oct 14, 04:56)
   - `individuals/`: 3,651 bytes (Oct 14, 11:24) ← **KEEP THIS**

2. **carly-ackerman.md**
   - `profiles/`: 1,144 bytes (Oct 14, 04:56)
   - `individuals/`: 3,271 bytes (Oct 14, 07:12) ← **KEEP THIS**

The `individuals/` versions are newer and more complete - we'll keep those.

## Safety Measures

✅ **Dry-run tested** - no surprises
✅ **Backups created** - all modified scripts backed up
✅ **Database transaction** - can be rolled back if needed
✅ **Archive not deleted** - old profiles preserved
✅ **Phased execution** - can run phases individually if needed

## How to Execute

### Option 1: Full Consolidation (Recommended)
```bash
python3 /home/.z/workspaces/con_9hza8oR18GLpOIVq/consolidate_crm_profiles.py --execute
```

### Option 2: Phase-by-Phase
```bash
# Phase 1: Update scripts
python3 /home/.z/workspaces/con_9hza8oR18GLpOIVq/consolidate_crm_profiles.py --execute --phase 1

# Phase 2: Migrate profiles
python3 /home/.z/workspaces/con_9hza8oR18GLpOIVq/consolidate_crm_profiles.py --execute --phase 2

# Phase 3: Update database
python3 /home/.z/workspaces/con_9hza8oR18GLpOIVq/consolidate_crm_profiles.py --execute --phase 3

# Phase 4: Archive old directory
python3 /home/.z/workspaces/con_9hza8oR18GLpOIVq/consolidate_crm_profiles.py --execute --phase 4
```

## Expected Results

**Before:**
```
Knowledge/crm/
├── individuals/        (4 files)
├── profiles/          (57 files)  ← MIXED STATE
└── crm.db             (points to both)
```

**After:**
```
Knowledge/crm/
├── individuals/        (59 files)  ← CANONICAL
├── .archived_profiles_20251014/  (57 files, read-only)
└── crm.db             (all point to individuals/)
```

**Scripts Updated:**
- `N5/scripts/crm_query.py` → writes to `individuals/`
- `N5/scripts/sync_b08_to_crm.py` → reads from `individuals/`

## Verification Steps

After execution:
```bash
# 1. Check file counts
ls Knowledge/crm/individuals/ | wc -l    # Should be 59

# 2. Verify database records
sqlite3 Knowledge/crm/crm.db "SELECT COUNT(*) FROM individuals WHERE markdown_path LIKE '%/profiles/%'"
# Should be 0

# 3. Verify archive
ls Knowledge/crm/.archived_profiles_20251014/ | wc -l    # Should be 57

# 4. Test CRM query tool
python3 N5/scripts/crm_query.py search "Alex"
# Should find records pointing to individuals/
```

## Rollback Plan

If something goes wrong:

1. **Scripts:** Restore from `.backup_*` files created in `N5/scripts/`
2. **Profiles:** Restore from `.archived_profiles_20251014/`
3. **Database:** Restore from `Knowledge/crm/crm_backup_*.db`

## My Recommendation

**Execute the full consolidation.** The dry-run completed successfully, all safety measures are in place, and the system architecture clearly intends `individuals/` as the canonical location.

The two conflicts are minor (newer versions already exist), and we're preserving the old `profiles/` directory as an archive.

---

**Ready to proceed?** Just say "execute consolidation" and I'll run it.

**Want to review more?** Ask about specific phases or concerns.

---

**Analysis Complete:** 2025-10-14 07:32 ET
