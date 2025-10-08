# N5 OS Refactor - Plan Adaptations

**Date**: 2025-10-08  
**Purpose**: Track deviations from the master plan and deferred work

---

## Adaptations Made During Execution

### 1. Knowledge/ and Lists/ Structure - DEFERRED

**Master Plan Vision**:
```
Knowledge/
├── schemas/
├── stable/          (bio.md, company.md, timeline.md)
├── evolving/        (facts.jsonl, article_reads.jsonl)
├── architectural/   (architectural_principles.md, ingestion_standards.md)
├── howie/
└── logs/
```

**Current Implementation** (Phase 3):
- Simple move: N5/knowledge → Knowledge (as-is, no restructuring)
- Simple move: N5/lists → Lists (as-is, no restructuring)
- All 20 files with path references updated

**Rationale**: 
- Conservative approach for Phase 3
- Preserve current working structure
- Reduce risk of breaking references
- Defer internal reorganization to future phase

**Deferred Work** (Future Phase 5 or 6):
- [ ] Reorganize Knowledge/ into stable/, evolving/, architectural/ subdirectories
- [ ] Move bio.md, company.md, careerspan-timeline.md → stable/
- [ ] Move facts.jsonl, article_reads.jsonl → evolving/
- [ ] Move architectural_principles.md, ingestion_standards.md, operational_principles.md → architectural/
- [ ] Create Knowledge/schemas/ and move relevant schemas
- [ ] Update all references to reflect new structure
- [ ] Create Knowledge/README.md as "Rosetta stone"
- [ ] Create Lists/schemas/ and move list schemas
- [ ] Create Lists/README.md

**Priority**: Medium (improves organization, but current structure is functional)

---

## Implementation Notes

### Phase 2: Deduplication - COMPLETE ✅
- Deleted 788 files instead of planned 588 (found more duplicates than expected)
- N5_mirror had only 4 unique files (backed up before deletion)
- Timestamped duplicates: 387 files (matched analysis)
- Result: 1,382 → 572 files (58.6% reduction)

### Phase 3: File Migration - IN PROGRESS ⏳
- Moved Knowledge/ and Lists/ to root ✅
- Updated 20 files with path references ✅
- Updated Documents/N5.md entry point ✅
- Validated critical systems still work ✅
- **Deferred**: Internal restructuring (see above)

---

## Future Work Items

### High Priority
1. [ ] Phase 4: Command Registry Population (37 commands) - ✅ COMPLETE
2. [ ] Phase 5: Pointer/Breadcrumb System Implementation - DEFERRED
3. [ ] Phase 6: Final Validation & Health Check - PENDING
4. [ ] **NEW: Implement Records/ layer for raw data storage**
5. [ ] **NEW: Define file saving conventions to prevent bloat**
6. [ ] **NEW: Clean up Documents/ folder organization**

### Medium Priority
4. [ ] Restructure Knowledge/ into ideal subdirectories
5. [ ] Restructure Lists/ with schemas/ subdirectory
6. [ ] Create comprehensive README.md files for Knowledge/ and Lists/
7. [ ] Deprecate and archive: workflows/, modules/, flows/, essential_links/

### Low Priority
8. [ ] Decide on jobs_data/ (remove or keep?)
9. [ ] Create Knowledge/POLICY.md
10. [ ] Enhance Lists/detection_rules.md

---

## New Architectural Additions (2025-10-08)

### 2. Records/ Layer - NEW REQUIREMENT

**Problem Identified**: 
- No designated location for raw inputs (meeting transcripts, emails, documents)
- These need processing before becoming Knowledge
- Currently scattered across workspace or saved to random locations

**Proposed Structure**:
```
/home/workspace/
├── Records/                [RAW DATA STAGING]
│   ├── Company/
│   │   ├── meetings/       - Meeting transcripts (pre-processing)
│   │   ├── emails/         - Important emails for review
│   │   ├── documents/      - Company docs needing ingestion
│   │   └── inbox/          - General intake queue
│   ├── Personal/
│   │   ├── notes/          - Personal notes
│   │   └── inbox/          - Personal intake
│   ├── Temporary/          - Processing queue (auto-cleanup)
│   └── README.md           - How to use Records
```

**Purpose**:
- Staging area for unprocessed data
- Clear intake point for automations
- Prevents workspace bloat
- Enables batch processing workflows

**Processing Flow**:
```
Records/Company/meetings/transcript.md
    ↓ (via command: process-transcript or automation)
Knowledge/facts.jsonl (extracted facts)
Knowledge/company.md (updated info)
Lists/must-contact.jsonl (action items)
    ↓
Records/Company/meetings/transcript.md → archived or deleted
```

**Priority**: HIGH (addresses bloat issue)

**Implementation Tasks**:
- [ ] Create Records/ directory structure
- [ ] Create Records/README.md with conventions
- [ ] Update N5.md entry point
- [ ] Create process-record command
- [ ] Define retention policy (how long records stay)
- [ ] Add Records/ to .gitignore patterns (large files)

---

### 3. File Saving Behavior - CRITICAL ISSUE

**Problem Identified**:
Zo's default behavior for saving files is weak:
- No consistent default location
- Files scattered across workspace
- Leads to bloat and disorganization
- No clear conventions for different file types

**Root Cause**: 
- Zo tools default to workspace root
- No policy enforcement in file creation
- No prompting for location confirmation

**Proposed Solution - File Saving Policy**:

1. **Default Locations by Type**:
   - Generated images → `/Images/`
   - Meeting notes → `/Meetings/`
   - Company docs → `/Careerspan/` or `/Records/Company/`
   - Articles saved → `/Articles/`
   - Scripts/code → `/Code/` or conversation workspace
   - Exports → `/Exports/`
   - Temporary → `/Records/Temporary/`
   - Records intake → `/Records/[Category]/inbox/`

2. **Enforcement Mechanisms**:
   - Update N5/prefs.md with explicit file saving rules
   - Create file-router command that suggests location
   - Prompt user before saving to workspace root
   - Add validation in n5_safety.py (warn on root saves)

3. **Conventions**:
   ```
   RULE: Never save files to workspace root unless explicitly requested
   RULE: Always suggest location based on file type
   RULE: For ambiguous files, ask user for location
   RULE: Auto-cleanup temporary files older than 7 days
   RULE: Records/ is for intake only, process then archive/delete
   ```

4. **Implementation in N5/prefs.md**:
   ```markdown
   ## File Saving Policy
   
   **Default Locations**:
   - Images: /home/workspace/Images/
   - Meeting notes: /home/workspace/Meetings/
   - Company documents: /home/workspace/Careerspan/ or /home/workspace/Records/Company/
   - Articles: /home/workspace/Articles/
   - Code/scripts: Conversation workspace (unless permanent)
   - Exports: /home/workspace/Exports/
   - Temporary: /home/workspace/Records/Temporary/ (7-day retention)
   - Records intake: /home/workspace/Records/[Category]/inbox/
   
   **Rules**:
   1. NEVER save to workspace root without explicit user confirmation
   2. ALWAYS suggest appropriate location based on file type
   3. ASK user if location is ambiguous
   4. WARN if overwriting existing file
   5. AUTO-CLEANUP temporary files after retention period
   ```

**Priority**: HIGH (prevents ongoing bloat)

**Implementation Tasks**:
- [ ] Update N5/prefs.md with file saving policy
- [ ] Add location validation to n5_safety.py
- [ ] Create file-router command
- [ ] Update relevant commands to use policy
- [ ] Test with common file creation scenarios

---

### 4. Documents/ Folder Cleanup - NEW TASK

**Problem Identified**:
- Documents/ folder is accumulating files
- Mix of user docs, system docs, refactor docs
- No clear organization

**Current Documents/**:
```
Documents/
├── N5.md                           [KEEP - Entry point]
├── N5_OS_Refactor_and_Vision.md    [ARCHIVE after refactor]
├── N5_Refactor_Execution_Log.md    [ARCHIVE after refactor]
├── N5_Refactor_Completion_Report.md [ARCHIVE after refactor]
├── N5_Refactor_Adaptations.md      [ARCHIVE after refactor]
└── [other docs...]
```

**Proposed Structure**:
```
Documents/
├── N5.md                           [System entry point]
├── System/                         [System documentation]
│   ├── Architecture.md
│   ├── Commands_Guide.md
│   └── Maintenance.md
├── Archive/                        [Historical docs]
│   └── 2025-10-08-Refactor/
│       ├── Vision.md
│       ├── Execution_Log.md
│       ├── Completion_Report.md
│       └── Adaptations.md
└── [user docs at root]
```

**Implementation Tasks**:
- [ ] Create Documents/System/ for system docs
- [ ] Create Documents/Archive/ for historical docs
- [ ] Move refactor docs to Archive/2025-10-08-Refactor/
- [ ] Create Documents/README.md explaining structure
- [ ] Update references to moved docs

**Priority**: MEDIUM (cleanup, improves organization)

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-08 | Defer Knowledge/Lists restructuring | Reduce risk in Phase 3, preserve working structure |
| 2025-10-08 | Delete N5_mirror completely | Only 4 unique files, backed up, obsolete staging area |
| 2025-10-08 | Update all 46 path references | Necessary for migration to work |
| 2025-10-08 | Add Records/ layer | Need staging area for raw data, prevent bloat |
| 2025-10-08 | Define file saving policy | Address Zo's weakness with default locations |
| 2025-10-08 | Clean up Documents/ folder | Improve organization, archive refactor docs |

---

## Open Questions

1. Should we deprecate workflows/, modules/, flows/ now or later?
2. What to do with jobs_data/ (currently empty)?
3. Should essential_links/ be merged into Lists/ or kept separate?
4. Timing for implementing the full breadcrumb/pointer system?

---

*This document tracks real-time adaptations to the master plan. Update as execution progresses.*
