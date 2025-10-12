# N5 Preferences Archive

**Purpose:** Historical documentation of preference system evolution

---

## Archived Documents

### MIGRATION_GUIDE.md
**Date:** 2025-10-09  
**Purpose:** v1 → v2 migration documentation (monolithic to modular)  
**Why Archived:** Migration completed; kept for historical reference  
**Key Content:**
- Old vs new structure comparison
- Content migration mapping
- Rollback procedures
- Validation checklist

### OPTIMIZATION_SUMMARY.md
**Date:** 2025-10-10  
**Purpose:** v2 → v3 optimization summary  
**Why Archived:** Optimization completed; kept for historical reference  
**Key Content:**
- File size reduction analysis
- New module creation summary
- Context-aware loading implementation
- Benefits documentation

---

## Preference System Evolution Timeline

### v1 (Pre-2025-10-09)
- **Structure:** Single monolithic `prefs.md` (~650 lines)
- **Approach:** Load everything always
- **Token Cost:** ~5-6K tokens per load

### v2 (2025-10-09)
- **Structure:** Modular with `index.md` as entry point
- **Approach:** Selective module loading
- **Changes:** Split into system/, operations/, communication/, integration/, knowledge/
- **Token Cost:** ~1-2K base + selective modules

### v3 (2025-10-10)
- **Structure:** Streamlined index as `prefs.md` (removed separate index.md)
- **Approach:** Enhanced context-aware loading guide
- **Changes:** 
  - Consolidated index.md → prefs.md
  - Created focused sub-modules (executive-snapshot, nuances, compatibility, etc.)
  - Added Careerspan organization identity module
- **Token Cost:** ~1-2K base + selective modules (improved organization)

### Cleanup (2025-10-12)
- **Actions:**
  - Removed 4 backup files (prefs.md.old, v1_backup, v2_monolithic_backup, index.md.deprecated)
  - Recovered empty engagement_definitions.md from Git history
  - Archived migration and optimization documentation
  - Created this Archive/ directory

---

## Current Active Documentation

For current preferences documentation, see:
- `file '../prefs.md'` — Main preferences index
- `file '../README.md'` — System documentation and quick start
- Module-specific files in system/, operations/, communication/, integration/, knowledge/

---

## Recovery Instructions

If you need to reference old structures or rollback:

### View Old Monolithic Structure
```bash
# v1 backup (if still in git history)
git show 6972e45:N5/prefs/prefs.md

# v2 backup (if still in git history)  
git show <commit>:N5/prefs/prefs.md.v2_monolithic_backup
```

### Extract Specific Content
All content from old versions exists in current modular structure. Use the MIGRATION_GUIDE.md in this folder to map old sections to new modules.
