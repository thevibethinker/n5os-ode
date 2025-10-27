# Documentation Hierarchy Proposal
**Conversation:** con_BD6xkpxbTZVbVKOt  
**Date:** 2025-10-26 19:25 ET

---

## THINK: Current State Analysis

### Current Documentation Locations

You have **three overlapping documentation hierarchies**:

1. **`N5/Documentation/`** (2 files)
   - `reflection-quick-start.md`
   - `reflection-system-setup.md`

2. **`N5/System Documentation/`** (6 files)
   - `FILE_PROTECTION_GUIDE.md`
   - `MEETING_PROCESS_CHANGELOG.md`
   - `MEETING_SYSTEM_ARCHITECTURE.md`
   - `MEETING_SYSTEM_QUICK_REFERENCE.md`
   - `PROTECTION_QUICK_REFERENCE.md`
   - `RESEARCH-FUNCTIONS-GUIDE.md`

3. **`N5/docs/`** (~140 files based on earlier find)
   - Mix of implementation summaries, architecture docs, session states, guides
   - Includes both historical (`PHASE-2B-PRIORITY-3-COMPLETE.md`) and active docs

4. **`Documents/System/`** (~80+ files)
   - Similar mix: implementation docs, guides, proposals, conversation summaries
   - HOW_TO guides, personas, system analyses

### The Problem (P2: SSOT Violation)

**No clear differentiation of purpose.** All four locations contain:
- Implementation summaries
- Quick-start guides
- Architecture documentation
- System overviews

This violates **P2 (Single Source of Truth)** and creates:
- Uncertainty about which doc is current
- Duplicated effort maintaining multiple docs
- Search confusion (where do I look first?)

---

## THINK: Adjacent Possibilities (Nemawashi)

### Option A: Consolidate Everything → `Documents/System/`
**Logic:** `Documents/` is for human-readable documentation per N5 architecture

**Pros:**
- Aligns with file 'Documents/N5.md' as primary entry point
- Clear separation: `N5/` = code/config, `Documents/` = docs
- Already has most comprehensive docs

**Cons:**
- Loses proximity of docs to code (some like `N5/commands/README.md` make sense near code)
- Large consolidation effort

### Option B: Four-Tier Hierarchy by Audience
**Structure:**
```
N5/README.md              → Quick orientation (30 seconds)
N5/commands/README.md     → Per-subsystem quick refs (stay with code)
Documents/System/         → Deep dives, how-tos, architecture (living docs)
Documents/Archive/        → Historical completion reports (frozen in time)
```

**Pros:**
- Proximity principle: Quick refs near code, deep dives separate
- Clear lifecycle: Active docs vs. archived docs
- Preserves N5 README as entry point

**Cons:**
- Still has overlap potential between `N5/commands/README.md` and `Documents/System/`

### Option C: **Two-Tier + Archive (RECOMMENDED)**
**Structure:**
```
Documents/N5.md                    → PRIMARY ENTRY POINT (master index)
Documents/System/                  → All living system documentation
  ├── guides/                      → How-to guides (operational)
  ├── architecture/                → Design docs (why/what)
  ├── quick-references/            → Cheat sheets
  └── personas/                    → AI personas

N5/README.md                       → Minimal pointer to Documents/N5.md
N5/*/README.md                     → Per-directory quick context only
                                      (what's in this dir, where to learn more)

Documents/Archive/                 → Historical docs (read-only)
```

**Delete entirely:**
- `N5/Documentation/` (2 files → merge into `Documents/System/guides/`)
- `N5/System Documentation/` (6 files → merge into `Documents/System/`)
- `N5/docs/` (140 files → active to `Documents/System/`, completion reports to `Archive/`)

**Pros:**
- Clear SSOT: `Documents/System/` is the living documentation
- Proximity where it matters: `N5/*/README.md` stays with code but is minimal
- Single entry point: `Documents/N5.md`
- Clean archive policy: Historical docs off to the side

**Cons:**
- Largest initial consolidation effort
- Need to update all references to old paths

---

## PLAN: Option C Implementation

### Success Criteria
1. ✅ Zero SSOT violations: Every doc topic has one canonical location
2. ✅ Clear navigation: `Documents/N5.md` → `Documents/System/{category}/`
3. ✅ Minimal `N5/*/README.md`: Just directory context + pointer to full docs
4. ✅ Clean archive: Historical completion reports in `Documents/Archive/`
5. ✅ All cross-references updated

### Migration Strategy

**Phase 1: Create Target Structure**
```bash
Documents/System/
├── guides/                  # How-to, setup, workflows
├── architecture/            # Design decisions, principles, system design
├── quick-references/        # Cheat sheets, quick-start
└── personas/                # (already exists)
```

**Phase 2: Categorize & Move**

**From `N5/Documentation/` (2 files):**
- `reflection-*.md` → `Documents/System/guides/`

**From `N5/System Documentation/` (6 files):**
- `*_GUIDE.md`, `*_QUICK_REFERENCE.md` → `Documents/System/quick-references/`
- `*_ARCHITECTURE.md`, `*_CHANGELOG.md` → `Documents/System/architecture/`

**From `N5/docs/` (140 files) - Triage:**
- `*_COMPLETE.md`, `*_SUMMARY.md`, `SESSION_STATE.md` → `Documents/Archive/`
- `*_GUIDE.md` → `Documents/System/guides/`
- `ARCHITECTURE*.md`, `*_DESIGN.md` → `Documents/System/architecture/`
- `QUICK*.md`, `*_QUICK_REF.md` → `Documents/System/quick-references/`

**From `Documents/System/` - Reorganize:**
- Create subdirectories, move files into categories
- Keep `PERSONAS_README.md` as `personas/README.md`

**Phase 3: Simplify `N5/README.md`**
```markdown
# N5 Operating System

**For full documentation:** file 'Documents/N5.md'

**Quick orientation:**
- Commands: `N5/commands/` (workflows you can invoke)
- Scripts: `N5/scripts/` (automation)
- Config: `N5/config/` (SSOT for system settings)

**Common tasks:**
- Meeting processing: `command 'meeting-process'`
- Thread export: `command 'thread-export'`
- Add to lists: `command 'lists-add'`
```

**Phase 4: Update `Documents/N5.md`** (Master Index)
Add clear navigation to new structure:
```markdown
## Documentation Map

**Getting Started:**
- file 'Documents/System/quick-references/N5_QUICK_START.md'

**How-To Guides:**
- file 'Documents/System/guides/' (browse all)

**Architecture & Design:**
- file 'Documents/System/architecture/' (browse all)
- file 'Knowledge/architectural/architectural_principles.md'

**Reference:**
- file 'Documents/System/quick-references/' (cheat sheets)
```

**Phase 5: Update Cross-References**
- Grep for references to moved files
- Update all `file '...'` mentions
- Update command documentation that references guides

**Phase 6: Delete Empty Directories**
```bash
rm -rf N5/Documentation/
rm -rf "N5/System Documentation/"
# Archive N5/docs/ (don't delete—audit first)
```

---

## Trap Doors & Trade-offs

### Trap Door: Breaking existing workflows
**Risk:** Scripts/commands may reference old paths  
**Mitigation:** Phase 5 comprehensive grep + update

### Trade-off: Massive file moves
**Con:** Big git diff, harder to track file history  
**Pro:** One-time pain for long-term clarity  
**Decision:** Accept the trade-off. Clean structure > incremental migration

### Trade-off: Proximity to code
**Con:** `N5/System Documentation/MEETING_SYSTEM_ARCHITECTURE.md` loses proximity to `N5/commands/meeting-process.md`  
**Pro:** But `N5/commands/README.md` can point to full arch doc  
**Decision:** Favor SSOT over proximity for architecture docs

---

## Questions for V

1. **Phase 2 triage:** `N5/docs/` has ~140 files. Should I:
   - A) Auto-classify by filename pattern (risk: mis-classification)
   - B) Generate a categorization table for your review first
   - C) Move obviously historical stuff, you manually triage the rest

2. **Archive policy:** Should `Documents/Archive/` be organized by:
   - A) Date folders (2025-10-26/)
   - B) Project folders (Worker-Systems/, Refactors/)
   - C) Flat with datestamps in filename (current pattern)

3. **`N5/docs/` fate:** Should I:
   - A) Delete the directory entirely after migration
   - B) Rename to `N5/docs_archive/` and keep for reference
   - C) Move to `Documents/Archive/N5_docs_historical/`

4. **Personas:** Currently `Documents/System/PERSONAS_README.md`. Should personas be:
   - A) `Documents/System/personas/` (stays in System)
   - B) Promoted to `Documents/Personas/` (top-level)
   - C) Moved to `Knowledge/personas/` (knowledge vs. system)

5. **Implementation timing:** Should I:
   - A) Execute full migration now (30-45 min)
   - B) Do Phase 1-3 now, you review, then finish
   - C) Generate detailed file-by-file migration plan for your approval

---

## Recommendation

**Go with Option C, Phase 1-3 now, your review, then finish.**

**Rationale:**
- Biggest cleanup impact (solves the problem completely)
- SSOT compliant
- Aligns with planning prompt values (simple over easy)
- One-time consolidation pain >> ongoing confusion

**Next:** Answer the 5 questions above, and I'll execute.

---

*v1.0 | 2025-10-26 19:25 ET*
