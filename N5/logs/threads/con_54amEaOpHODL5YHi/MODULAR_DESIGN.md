# Modular Thread Export Design v2.1

**Date:** 2025-10-12  
**Status:** Design Approved → Implementation

---

## Overview

Refactor Thread Export v2.0 to generate **5 focused markdown files + 1 index** instead of a single monolithic document. This improves context loading efficiency and allows selective access to relevant information.

---

## File Structure

### Output Directory
```
N5/logs/threads/{thread-id}/
├── INDEX.md              # Start here - explains the structure
├── RESUME.md             # Always load first - entry point
├── DECISIONS.md          # Load to understand "why"
├── TECHNICAL.md          # Reference during execution
├── TROUBLESHOOTING.md    # Load when stuck
├── LINEAGE.md            # Load for broader context
├── aar.json              # Single source of truth (existing)
└── artifacts/            # Thread artifacts (existing)
```

---

## File Mappings

### **INDEX.md**
**Purpose:** Navigation and structure explanation  
**Content:**
- What this directory contains
- How to use these files
- Quick reference table mapping files to use cases
- File size/section count metadata

---

### **RESUME.md** (Entry Point)
**Purpose:** Quick resume - "Where am I and what do I do next?"  
**Sections:**
1. Header (Thread ID, Date, Topic, Status)
2. Summary
3. Quick Start
4. What Was Completed
5. Critical Constraints
6. Integration Points & Next Steps (only "Next Steps" part)
7. Context for Resume

**Why these together:** Everything needed for fast cold-start. Read this first, always.

---

### **DECISIONS.md**
**Purpose:** Design rationale and lessons learned - "Why is it this way?"  
**Sections:**
1. Key Technical Decisions
2. Anti-Patterns / Rejected Approaches
3. Known Issues / Gotchas
4. Open Questions

**Why these together:** Understanding the reasoning prevents repeating mistakes or undoing good decisions.

---

### **TECHNICAL.md**
**Purpose:** How-to and current state reference - "How do I do X? What's the state?"  
**Sections:**
1. Code Patterns / Quick Reference
2. State Snapshot
3. Files Created/Modified
4. Testing Status
5. Assumptions & Validations

**Why these together:** Concrete technical details needed while actively working.

---

### **TROUBLESHOOTING.md**
**Purpose:** Diagnostic guide - "I'm stuck, how do I debug?"  
**Sections:**
1. If Stuck, Check These
2. System Architecture Context
3. User Preferences (V's Style)

**Why these together:** Debugging aid when things aren't working or you need system context.

---

### **LINEAGE.md**
**Purpose:** History and broader context - "How does this fit in the bigger picture?"  
**Sections:**
1. Thread Lineage & Related Work
2. Related Documentation
3. Success Criteria
4. Export Metadata

**Why these together:** Understanding relationships and history. Less frequently needed but valuable for planning.

---

## Implementation Plan

### Phase 1: Refactor Script Structure
1. Create new methods in `ThreadExporter` class:
   - `generate_index_md(aar_data) -> str`
   - `generate_resume_md(aar_data) -> str`
   - `generate_decisions_md(aar_data) -> str`
   - `generate_technical_md(aar_data) -> str`
   - `generate_troubleshooting_md(aar_data) -> str`
   - `generate_lineage_md(aar_data) -> str`

2. Each method extracts relevant sections from `aar_data` using existing logic from `generate_markdown()`

3. Keep `generate_markdown()` for backward compatibility (combines all sections)

### Phase 2: Update Export Logic
1. Modify `run()` method to write 6 markdown files instead of 1
2. Use clear filenames: `INDEX.md`, `RESUME.md`, etc.
3. Update console output to show all files created
4. Update file paths in telemetry

### Phase 3: Add Metadata Headers
Each file should start with:
```markdown
# [Filename] - [Purpose]

**Thread ID:** {thread_id}  
**Export Date:** {date}  
**Purpose:** [One-line description]  
**Also see:** [Links to other relevant files]

---
```

### Phase 4: Testing
1. Test with dry-run
2. Test with real export
3. Verify all sections appear exactly once
4. Check file sizes are reasonable
5. Test AI loading workflow

---

## Backward Compatibility

- Keep JSON export unchanged (single source of truth)
- Keep `generate_markdown()` method for single-file export if needed
- Add CLI flag `--format [single|modular]` (default: modular)
- Existing tooling can still parse JSON

---

## Success Criteria

- [x] Design approved
- [ ] 6 markdown generator methods implemented
- [ ] Export logic updated to write 6 files
- [ ] Metadata headers added to each file
- [ ] INDEX.md clearly explains structure
- [ ] Dry-run test passes
- [ ] Real export test passes
- [ ] All 23 sections appear exactly once across files
- [ ] Documentation updated

---

## AI Usage Pattern

**For an AI resuming work:**

1. **Load INDEX.md** - Understand structure
2. **Load RESUME.md** - Get context and next steps
3. **Conditionally load:**
   - DECISIONS.md - If decisions need understanding/changing
   - TECHNICAL.md - During active work
   - TROUBLESHOOTING.md - If encountering issues
   - LINEAGE.md - For planning or understanding relationships

**Benefits:**
- Faster initial context load (RESUME is ~20% of total content)
- Targeted loading based on current need
- Reduced token usage for simple resumes
- Better mental model for AI (clear file purposes)

---

## Next Steps

1. Implement Phase 1 (refactor methods)
2. Implement Phase 2 (update export logic)
3. Implement Phase 3 (add headers)
4. Run Phase 4 (testing)
5. Update format specification document
6. Update N5 documentation

---

**Ready to implement:** Yes
