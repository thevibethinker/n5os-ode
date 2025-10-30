# Phase 5: Workflows - Port & Adapt Approach

**Strategy**: Aggressive port from Main → Adapt on the fly → Test & iterate

---

## Phase 5.1: Conversation End Workflow

**Port from Main:**
- `file 'n5os-core/N5/commands/conversation-end.md'` (protocol already there)
- `N5/scripts/n5_conversation_end.py` (if exists)
- `N5/scripts/n5_workspace_root_cleanup.py`
- Related cleanup utilities

**Adapt for n5os-core:**
- Remove Careerspan-specific logic (CRM, meeting ingestion)
- Simplify to core workflow: Review → Classify → Propose → Execute
- Keep AAR export (already working)
- Keep lesson extraction
- Keep placeholder detection

**Test:**
- Run on this conversation as test case
- Verify file moves work
- Check logging

---

## Phase 5.2: Knowledge Management

**Port from Main:**
- `Knowledge/architectural/ingestion_standards.md` (already there)
- SSOT enforcement patterns
- Migration utilities

**Adapt:**
- Generic knowledge organization (not V-specific)
- Portable folder structures
- Documentation patterns

---

## Phase 5.3: Integration

- Wire conversation-end into n5os-core command registry
- Test end-to-end
- Document for distribution

---

**Let's start with 5.1 now - porting conversation-end workflow.**
