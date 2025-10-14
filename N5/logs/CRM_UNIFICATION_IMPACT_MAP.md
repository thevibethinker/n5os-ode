# CRM Unification Impact Map

**Last Updated:** 2025-10-14 00:39 ET  
**Status:** Phase 3 Complete (Phases 1-3 executed)

---

## Executive Summary

**Objective:** Unify N5/stakeholders/ and Knowledge/crm/ into single CRM system  
**Current Phase:** 3 of 9 (Profile Migration Complete)  
**Risk Level:** 🟡 Medium (workflows currently broken, expected)

### Progress
- ✅ Phase 1: Backup & Structure (git: 9cf28bd)
- ✅ Phase 2: Directory Restructure (git: 9817418)
- ✅ Phase 3: Profile Migration (git: 5d2033d)
- ⏳ Phase 4: Index Rebuild (pending)
- ⏳ Phase 5: Documentation (pending)
- ⏳ Phase 6: Code Updates (pending)
- ⏳ Phase 7: Verification (pending)
- ⏳ Phase 8: Cleanup (pending)
- ⏳ Phase 9: Organizations Setup (pending)

---

## System State

### Directory Structure (Current)
```
Knowledge/crm/
├── .backups/              (copied from N5/stakeholders)
├── .pending_updates/      (copied from N5/stakeholders)
├── profiles/              (renamed from individuals/, 51→58 profiles)
│   ├── _template.md       (copied from N5/stakeholders)
│   ├── [51 original CRM profiles]
│   └── [6 migrated stakeholder profiles]
├── organizations/         (NEW, empty)
├── interactions/          (NEW, empty)
├── events/
├── follow-ups/
├── crm.db                 (SQLite database)
├── index.jsonl            (6 migrated entries)
└── [docs: DATABASE_SETUP, PROFILE_TEMPLATE, README]

N5/stakeholders/           (unchanged, 6 profiles still present)
├── .backups/
├── .pending_updates/
├── [6 profile .md files]
├── index.jsonl            (6 entries)
└── [docs: README, PROFILE-UPDATES, _template]
```

### Profile Counts
- **Before:** 51 CRM + 6 stakeholders = 57 total
- **After Phase 3:** 58 in Knowledge/crm/profiles/ (52 + 6 migrated)
- **Duplicates Detected:** 0
- **Migration Success:** 100% (6/6)

---

## Dependencies & Impact Analysis

### Phase 3 Dependencies (Closed)

#### ✅ D1: Profile Migration
**Type:** Data Movement  
**Status:** CLOSED  
**Resolution:** 6 profiles migrated successfully (michael-maher-cornell, fei-ma-nira, elaine-pak, kat-de-haen-fourth-effect, jake-fohe, hei-yue-pang-yuu)

#### ✅ D2: Duplicate Detection
**Type:** Data Integrity  
**Status:** CLOSED  
**Resolution:** Email-based and filename-based duplicate detection implemented. No duplicates found.

#### ✅ D3: Index Update
**Type:** Data Integrity  
**Status:** CLOSED  
**Resolution:** CRM index.jsonl updated with 6 new entries including migration metadata

---

### Detected Dependencies (Open)

#### 🔴 D4: Path References (HIGH PRIORITY)
**Type:** Code Breakage  
**Status:** OPEN  
**Impact:** Scripts/commands referencing `Knowledge/crm/individuals/` will fail  
**Affected Components:**
- Unknown count of scripts in `N5/scripts/`
- Unknown count of commands in `N5/commands/`
- Potential references in workflow docs

**Detection Method:** Grep search needed  
**Resolution Plan:** Phase 6 (Code Updates)

#### 🔴 D5: Index Schema Inconsistency (HIGH PRIORITY)
**Type:** Data Model  
**Status:** OPEN  
**Impact:** CRM index has 6 entries (migrated), but 58 profiles exist  
**Gap:** 52 legacy profiles not indexed  
**Resolution Plan:** Phase 4 (Index Rebuild) - scan all profiles/, generate complete index

#### 🟡 D6: N5/stakeholders/ Cleanup (MEDIUM PRIORITY)
**Type:** Data Duplication  
**Status:** OPEN  
**Impact:** Source profiles still exist in N5/stakeholders/ after migration  
**Decision:** Keep until Phase 8 (Cleanup) for safety  
**Resolution Plan:** Phase 8 - archive or delete N5/stakeholders/ after verification

#### 🟡 D7: Template Duplication (LOW PRIORITY)
**Type:** Maintenance  
**Status:** OPEN  
**Impact:** _template.md exists in both locations  
**Resolution Plan:** Phase 8 - remove N5/stakeholders/_template.md, establish SSOT in Knowledge/crm/profiles/

#### 🟢 D8: Organizations Structure (PLANNED)
**Type:** Feature Addition  
**Status:** OPEN (by design)  
**Impact:** organizations/ directory created but empty  
**Priority:** Top of system upgrades list (per user request)  
**Resolution Plan:** Phase 9 (Organizations Setup) - design schema, populate from existing profiles

---

## Breaking Changes (Expected)

### Currently Broken (Will Fix in Phase 6)
1. **Path References:** Any code using `Knowledge/crm/individuals/` → 404
2. **Index Lookups:** Scripts expecting complete index will miss 52 profiles
3. **Stakeholder Workflows:** May still reference N5/stakeholders/ paths

### Mitigation Strategy
- User confirmed: "breaking these workflows is fine"
- All changes backed up (commit 9cf28bd)
- Rollback script available: `.migration_backups/crm_unification_2025-10-14/ROLLBACK.sh`

---

## Next Actions (Phase 4)

### Phase 4: Index Rebuild
**Objective:** Generate complete CRM index covering all 58 profiles

**Tasks:**
1. Scan all profiles in `Knowledge/crm/profiles/`
2. Extract metadata (name, email, organization, slug)
3. Rebuild `index.jsonl` with complete dataset
4. Validate: 58 entries, no missing profiles
5. Git commit

**Dependencies Closed by Phase 4:**
- D5: Index Schema Inconsistency

---

## Rollback Information

### Quick Rollback
```bash
cd /home/workspace
git reset --hard 9cf28bd  # Pre-migration checkpoint
```

### Full Rollback (if git issues)
```bash
/home/workspace/.migration_backups/crm_unification_2025-10-14/ROLLBACK.sh
```

### Backup Location
```
/home/workspace/.migration_backups/crm_unification_2025-10-14/
├── N5_stakeholders_backup.tar.gz (16 KB)
├── Knowledge_crm_backup.tar.gz (23 KB)
├── crm_backup.sql (144 lines)
├── stakeholders_index.jsonl (1.4 KB)
├── crm_index.jsonl (0 bytes)
├── checksums.txt (MD5 hashes)
└── ROLLBACK.sh (executable)
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data loss during migration | Low | Critical | ✅ Backups + git checkpoints |
| Scripts fail after path change | High | Medium | ⏳ Phase 6 updates + testing |
| Duplicate profiles created | Low | Medium | ✅ Duplicate detection implemented |
| Index corruption | Low | High | ✅ Append-only writes + backups |
| User workflow disruption | Medium | Low | ✅ User confirmed acceptable |

---

## Metrics

### Migration Efficiency
- **Profiles Migrated:** 6/6 (100%)
- **Duplicates Avoided:** 0
- **Errors:** 0
- **Time:** ~15 minutes (Phases 1-3)

### Code Impact (Estimated)
- **Affected Scripts:** TBD (Phase 6 detection)
- **Affected Commands:** TBD (Phase 6 detection)
- **Affected Docs:** TBD (Phase 5 detection)

---

## Change Log

### 2025-10-14 00:39 ET
- ✅ Executed Phase 1: Backup & Structure
- ✅ Executed Phase 2: Directory Restructure
- ✅ Executed Phase 3: Profile Migration
- 🔍 Detected 8 dependencies (4 closed, 4 open)
- 📝 Created impact map

---

*Next: Phase 4 (Index Rebuild) - Detected dependency D5 must be resolved*
