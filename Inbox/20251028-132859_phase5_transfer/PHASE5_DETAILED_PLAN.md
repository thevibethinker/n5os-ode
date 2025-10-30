# Phase 5 Detailed Plan

**Phase**: 5.1 - Conversation End Workflow  
**Time**: 8-10 hours  
**Complexity**: Medium-High

---

## Overview

Build ONE unified `conversation-end` command that executes 12 sequential phases to formally close a conversation.

---

## Phase 5.1: Conversation End Workflow

### Architecture

**Single Entry Point**: `N5/scripts/n5_conversation_end.py`

**12-Phase Sequential Execution**:
```
Phase -1: Lesson Extraction     → Extract learnings
Phase 0:  Thread Export         → Generate AAR
Phase 1:  File Organization     → Classify & move files
Phase 2:  Workspace Cleanup     → Clean root directory
Phase 3:  Placeholder Scan      → Detect TODOs
Phase 4:  Output Review         → Check AI responses
Phase 5:  Archive Build Tasks   → Move completed work
Phase 6:  Title Generation      → Propose title
Phase 7:  Git Status Check      → Uncommitted changes
Phase 8:  Timeline Update       → [SKIP - V-specific]
Phase 9:  Registry Closure      → Mark complete
Phase 10: Archive Promotion     → Auto-promote significant
```

### Component Specifications

#### Phase -1: Lesson Extraction

**Purpose**: Extract key learnings from conversation

**Logic**:
1. Scan conversation for:
   - Principle violations (P0-P22)
   - Novel solutions
   - Mistakes and corrections
   - Efficiency improvements
2. Generate freeform markdown summary
3. Save to `LESSONS_EXTRACTED.md`

**Skip Conditions**: 
- Conversation too short (<5 messages)
- Already extracted

#### Phase 0: Thread Export (AAR)

**Purpose**: Generate After Action Review

**Logic**:
1. Scan workspace for artifacts:
   - Scripts created
   - Documents written
   - Files modified
2. Classify conversation type (build/research/discussion)
3. Generate structured export:
   - INDEX.md (navigation)
   - RESUME.md (quick restart)
   - DESIGN.md (decisions)
   - IMPLEMENTATION.md (technical details)
   - VALIDATION.md (testing)
   - CONTEXT.md (background)

**Output**: Thread export directory with 6 markdown files

#### Phase 1: File Organization

**Purpose**: Classify and organize workspace files

**Classification Rules**:
```python
def classify_file(filepath):
    # Images → Images/
    if filepath.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
        return ("Images/", "move", "Image file")
    
    # Temporary docs → Documents/Temporary/
    if "temp" in filepath.name.lower() or "scratch" in filepath.name.lower():
        return ("Documents/Temporary/", "move", "Temporary document")
    
    # Exports → Exports/
    if "export" in filepath.name.lower() or filepath.suffix == '.zip':
        return ("Exports/", "move", "Export file")
    
    # Scripts → Keep in place or ask
    if filepath.suffix in ['.py', '.sh']:
        return (None, "keep", "Script file - manual review")
    
    # Unknown → ASK
    return (None, "ask", "Unknown file type")
```

**Auto-Confirm Logic**:
```python
def auto_confirm_high_confidence(files_by_category):
    # Auto-confirm if:
    # 1. No ASK files (all destinations clear)
    # 2. All moves to standard destinations
    # 3. No deletions (or only obvious temp files)
    
    asks = files_by_category.get("ASK", [])
    if asks:
        return False  # Need human decision
    
    moves = files_by_category.get("MOVE", [])
    standard_dests = [
        "Images/",
        "Documents/Temporary/",
        "Documents/Archive/",
        "Exports/"
    ]
    
    for item in moves:
        dest = str(item.get('dest', ''))
        if not any(sd in dest for sd in standard_dests):
            return False
    
    return True
```

**Output**: Files organized, summary logged

#### Phase 2: Workspace Cleanup

**Purpose**: Remove clutter from workspace root

**Logic**:
1. Scan root directory for:
   - Temporary files (*.tmp, *.temp)
   - Duplicate files (file_1.md, file_2.md)
   - Empty directories
2. Propose deletions
3. Execute if approved

**Safety**: Never delete without confirmation (unless --auto)

#### Phase 3: Placeholder Scan

**Purpose**: Detect unfinished work

**Scan for**:
- `TODO`
- `FIXME`
- `XXX`
- `HACK`
- `PLACEHOLDER`
- Undocumented functions

**Output**: Report with line numbers, prompt to fix or acknowledge

#### Phase 4: Output Review Check

**Purpose**: Verify AI responses quality

**Check for**:
- Truncated responses
- Error messages
- Incomplete code blocks
- Promise-but-not-deliver patterns

**Output**: Quality report, flag issues

#### Phase 5: Archive Build Tasks

**Purpose**: Move completed build artifacts

**Logic**:
1. Find directories matching build patterns:
   - `*-project/`
   - `build-*/`
   - `tmp-*/`
2. Check if work complete (no TODOs, has README)
3. Propose archival
4. Move to Documents/Archive/

#### Phase 6: Title Generation

**Purpose**: Suggest conversation title

**Logic**:
1. Analyze conversation focus
2. Extract key topics
3. Generate 3-5 title options
4. Save to PROPOSED_TITLE.md
5. Display prominently

**Format**: `YYYY-MM-DD_Topic-Description_ID`

#### Phase 7: Git Status Check

**Purpose**: Detect uncommitted changes

**Logic**:
1. Check if workspace is git repo
2. Run `git status --porcelain`
3. Report uncommitted files
4. Prompt to commit (if interactive)

#### Phase 8: Timeline Update

**Status**: SKIP (V-specific integration)

**Note**: Remove from distribution version

#### Phase 9: Registry Closure

**Purpose**: Mark conversation complete in database

**Logic**:
1. Get conversation ID
2. Update conversations.db:
   - status = "completed"
   - completed_at = now()
   - aar_path = thread export path
3. Log artifacts created
4. Record any issues

**Database**: SQLite at N5/data/conversations.db

#### Phase 10: Archive Promotion

**Purpose**: Auto-promote significant conversations

**Criteria for "Significant"**:
- Duration > 30 minutes
- Artifacts created > 5
- Scripts/docs generated
- Build or system work

**Action**: Move thread export to permanent archive location

---

## Command Interface

### Arguments

```bash
python3 N5/scripts/n5_conversation_end.py [OPTIONS]

OPTIONS:
  --auto                 Auto-approve all prompts (non-interactive)
  --dry-run              Show what would be done without executing
  --skip-cleanup         Skip workspace root cleanup phase
  --skip-placeholder-scan Skip placeholder detection
  --convo-id CONVO_ID    Specific conversation ID (auto-detect if omitted)
```

### Natural Language Triggers

Register in commands.jsonl:
- "end this conversation"
- "conversation end"
- "close conversation"
- "finish conversation"
- "wrap up"

### Exit Codes

- 0: Success
- 1: Error during execution
- 2: User aborted
- 3: Prerequisites not met

---

## Dependencies

### Python Packages
- pathlib (stdlib)
- sqlite3 (stdlib)
- json (stdlib)
- logging (stdlib)
- subprocess (stdlib)

### N5 Components
- conversation_registry.py (Phase 1)
- session_state_manager.py (Phase 1)
- conversations.db (Phase 1)

### External Tools
- git (optional, for Phase 7)

---

## Testing Requirements

### Unit Tests (15+)

1. File classification accuracy
2. Auto-confirm logic
3. Lesson extraction
4. Title generation
5. Registry updates
6. Each phase independently

### Integration Tests (10+)

1. Full workflow on build conversation
2. Full workflow on research conversation
3. Full workflow on discussion conversation
4. Empty conversation handling
5. Large conversation (100+ files)
6. Error recovery
7. Dry-run mode
8. Auto mode
9. Interactive mode
10. Phase skip flags

### End-to-End Tests (5+)

1. Fresh conversation close
2. Multi-artifact conversation
3. Conversation with git repo
4. Conversation with placeholders
5. Minimal conversation

---

## Error Handling

### Phase Failures

Each phase must:
1. Log specific error
2. Decide: abort or continue?
3. Report to user
4. Update registry with issue

### Recoverable Errors
- Missing git (skip Phase 7)
- No title generator (use basic title)
- Registry unavailable (log warning)

### Fatal Errors
- Workspace not found
- Permission denied
- Corrupted database

---

## Documentation Requirements

### Command Documentation

Create `N5/commands/conversation-end.md`:
```markdown
# Conversation End

ONE unified command for formal conversation closure.

## Usage

Natural language: "end this conversation"
Direct: `python3 N5/scripts/n5_conversation_end.py --auto`

## What It Does

Executes 12 phases:
1. Extract lessons
2. Generate AAR
3. Organize files
... [full description]

## Options

--auto: Non-interactive mode
--dry-run: Preview without executing
... [full options]

## Examples

... [3-5 examples]
```

### Code Documentation

Each function needs:
- Docstring
- Type hints
- Error conditions
- Return values

---

## Distribution Checklist

- [ ] No V-specific code
- [ ] No hardcoded paths (except /home/workspace)
- [ ] Clear error messages
- [ ] Comprehensive logging
- [ ] Help text complete
- [ ] Examples provided
- [ ] Tests passing
- [ ] Fresh install works
- [ ] Documentation complete
- [ ] Registered in commands.jsonl

---

## Success Criteria

**Functional**:
- ✅ All 12 phases execute
- ✅ Auto-confirm works correctly
- ✅ Files organized accurately
- ✅ Lessons extracted
- ✅ Thread export generated
- ✅ Registry updated

**Quality**:
- ✅ 30+ tests passing
- ✅ Fresh thread test (<10 min)
- ✅ Error handling comprehensive
- ✅ State verification works
- ✅ Dry-run accurate

**Distribution**:
- ✅ Works on any n5os-core
- ✅ Documentation complete
- ✅ Examples clear
- ✅ Production-ready

---

*Version: 1.0*  
*Created: 2025-10-28*  
*For: Demonstrator Build*
