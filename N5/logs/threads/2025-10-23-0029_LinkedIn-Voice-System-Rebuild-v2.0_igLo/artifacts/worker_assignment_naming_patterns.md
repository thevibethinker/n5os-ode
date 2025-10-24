# Worker Assignment - File Naming & Storage Patterns

**Generated:** 2025-10-22T21:21:30+00:00  
**Parent Conversation:** con_f7Xbld76jdowigLo  
**Requested By:** V  
**Worker Status:** PENDING_ASSIGNMENT

---

## Your Mission

Develop a consistent, reliable pattern for naming files and folders + storing/locating files in the right place according to its role in the data ecosystem.

---

## Context

The N5 system has:
- Existing emoji legend for file categorization (`file 'N5/config/emoji-legend.json'`)
- Naming conventions document (`file 'N5/prefs/naming-conventions.md'`)
- Architectural principles (`file 'Knowledge/architectural/architectural_principles.md'`)

The goal is to create a unified, principle-driven system that:
1. Makes file purpose immediately clear
2. Enables fast location/retrieval based on role in data flow
3. Integrates with existing N5 patterns (Records → Process → Knowledge/Lists → Archive)
4. Provides automated classification and placement guidance

---

## Objectives

1. **Audit Current State**
   - Map current file/folder patterns across workspace
   - Identify inconsistencies and ambiguities
   - Document implicit rules being followed

2. **Design Pattern System**
   - Extend/refine naming conventions for clarity
   - Define role-based storage taxonomy (raw data, processed, knowledge, archived)
   - Create decision tree for "where does this file go?"
   - Define emoji indicators for file roles (if not already covered)

3. **Build Automation**
   - Create classification script/command
   - Build file placement helper
   - Integrate with existing N5 commands (conversation-end, knowledge-ingest, etc.)

4. **Documentation**
   - Update `file 'N5/prefs/naming-conventions.md'` with patterns
   - Create quick reference guide
   - Add examples for common scenarios

---

## Success Criteria

- [ ] Comprehensive file role taxonomy documented
- [ ] Clear naming patterns for each file role
- [ ] Automated classification tool working
- [ ] Integration with conversation-end workflow
- [ ] Quick reference guide created
- [ ] Examples tested across common scenarios

---

## Architectural Principles to Follow

Reference: `file 'Knowledge/architectural/architectural_principles.md'`

Key principles:
- P0: Rule-of-Two (max 2 config files in context)
- P1: Human-Readable First
- P2: Single Source of Truth
- P8: Minimal Context
- P20: Modular Design

---

## Constraints

- Must integrate with existing N5 emoji system
- Must respect current folder structure (Knowledge/, Records/, Lists/, Documents/)
- Must not break existing workflows
- Should be backwards compatible where possible

---

## Deliverables

1. **Pattern Documentation** - Updated naming conventions with role-based patterns
2. **Classification Script** - `n5_file_classifier.py` or similar
3. **Command Integration** - Update relevant commands to use new patterns
4. **Quick Reference** - One-page guide for file placement decisions
5. **Examples Collection** - Real-world examples of classification

---

## Instructions for Worker Thread

1. Initialize your session with system files
2. Load architectural principles
3. Ask 3+ clarifying questions if needed
4. Create implementation plan with phases
5. Build modularly following P20
6. Test with real workspace files
7. Update status regularly in `worker_updates/` directory
8. Document all architectural decisions

---

## Communication Protocol

**You → Parent:** Write status updates to parent's workspace:  
`/home/.z/workspaces/con_f7Xbld76jdowigLo/worker_updates/WORKER_{your_convo_id}_status.md`

**Parent → You:** Parent may update this assignment or provide input via messages

---

**Ready for assignment to new worker thread!**
