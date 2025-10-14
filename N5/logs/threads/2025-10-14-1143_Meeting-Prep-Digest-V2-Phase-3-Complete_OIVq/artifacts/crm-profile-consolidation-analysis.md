# CRM Profile Consolidation Analysis

## Problem Identified

**Two separate profile directories exist:**
1. `Knowledge/crm/individuals/` (4 files)
2. `Knowledge/crm/profiles/` (60+ files)

**Root Cause:** Inconsistent profile creation paths across different scripts/workflows.

---

## Profile Creation Sources

### 1. Networking Event Processor
**Script:** `N5/scripts/n5_networking_event_process.py`
- **Writes to:** `Knowledge/crm/individuals/`
- **Line 31:** `CRM_INDIVIDUALS = CRM_BASE / "individuals"`
- **Line 429:** Creates profiles at `CRM_INDIVIDUALS / f"{individual_id_slug}.md"`
- **Also writes to:** SQLite database (`crm.db`)
- **Used for:** Processing networking events and creating contact profiles

### 2. CRM Query Tool
**Script:** `N5/scripts/crm_query.py`
- **Writes to:** `Knowledge/crm/profiles/`
- **Line 165:** `md_path = Path('/home/workspace') / f'Knowledge/crm/profiles/{args.name.lower().replace(" ", "-")}.md'`
- **Used for:** Manual addition of individuals via CLI

### 3. Stakeholder Profile Generator (Meeting Processor)
**Script:** `N5/scripts/blocks/stakeholder_profile_generator.py`
- **Writes to:** Meeting directories (`N5/records/meetings/*/stakeholder-profile.md`)
- **Does NOT write directly to CRM** - only updates SQLite database
- **Used for:** Generating profiles from meeting transcripts

### 4. Deprecated/Legacy Scripts
**Scripts that reference `profiles/` but are marked DEPRECATED:**
- `N5/scripts/stakeholder_manager.py`
- `N5/scripts/background_email_scanner.py`
- `N5/scripts/safe_stakeholder_updater.py`

---

## Documentation vs. Reality

### README.md Says:
```
Knowledge/crm/
├── individuals/        # Individual profiles (one per person)
```

### DATABASE_SETUP.md Says:
```
Knowledge/crm/
├── individuals/                # Markdown files (one per person)
```

### But Reality:
- `individuals/` has 4 newer profiles (recent networking events)
- `profiles/` has 60+ older profiles (from previous system)
- Both are actively referenced by different scripts

---

## Profile Format Differences

### individuals/ Format
```markdown
# Alex Caveny

**Status:** Active Advisor
**Relationship Type:** #stakeholder:advisor
**Organization:** Wisdom Partners
**Role:** Startup Advisor / Former Founder
**Location:** Bay Area (PST timezone)
**Priority:** Important

---

## Contact Information
## Relationship Context
## Background
```

### profiles/ Format
```markdown
---
name: "Alex Caveny"
email_primary: ""
organization: ""
role: "Advisor / GTM coach"
first_contact: "2025-09-08"
status: "active"
---

# Alex Caveny

## Domain Authority & Source Credibility
## Notes
## Next enrichment tasks
```

**Different schemas, different purposes.**

---

## Architectural Intent (from README)

The system is designed around `individuals/` as the canonical location:
- Individual-centric CRM structure
- Cross-referenced with events
- Integrated with SQLite database
- Used by networking event processor

---

## Recommended Solution

### Phase 1: Immediate Fix (P0)
1. **Standardize on `individuals/`** as canonical location
2. **Update `crm_query.py`** to write to `individuals/` instead of `profiles/`
3. **Verify database sync** works correctly for both paths

### Phase 2: Migration (P1)
1. **Audit existing `profiles/`** - identify which are still relevant
2. **Migrate active profiles** from `profiles/` → `individuals/`
3. **Update database records** with new paths
4. **Archive `profiles/`** directory

### Phase 3: Cleanup (P2)
1. **Remove DEPRECATED scripts** or update their paths
2. **Update all script references** to use `individuals/` consistently
3. **Document canonical path** in all relevant READMEs

---

## Scripts Requiring Updates

### High Priority (Active Scripts)
1. ✅ `N5/scripts/n5_networking_event_process.py` - Already correct
2. ❌ `N5/scripts/crm_query.py` - **Needs fix** (line 165)
3. ✅ `N5/scripts/blocks/stakeholder_profile_generator.py` - Writes to DB only (correct)

### Medium Priority (Integration Scripts)
4. ❌ `N5/scripts/sync_b08_to_crm.py` - References `profiles/` (line 21)

### Low Priority (Deprecated)
5. `N5/scripts/stakeholder_manager.py` - DEPRECATED
6. `N5/scripts/background_email_scanner.py` - DEPRECATED
7. `N5/scripts/safe_stakeholder_updater.py` - DEPRECATED

---

## Success Criteria

✅ All new profiles created in `individuals/`
✅ All scripts reference `individuals/` as canonical path
✅ Database `markdown_file_path` points to `individuals/`
✅ Old `profiles/` archived with migration notes
✅ Documentation updated to reflect single source of truth

---

## Questions for V

1. **Migration strategy for existing `profiles/`:**
   - Migrate all 60+ profiles to `individuals/`?
   - Or audit first and migrate only active contacts?

2. **Profile format:**
   - Keep current `individuals/` format?
   - Or harmonize with some fields from `profiles/` format?

3. **Backward compatibility:**
   - Keep `profiles/` as read-only archive?
   - Or fully remove after migration?

---

**Status:** Analysis Complete - Awaiting Decision on Migration Approach
**Created:** 2025-10-14 07:31 ET
