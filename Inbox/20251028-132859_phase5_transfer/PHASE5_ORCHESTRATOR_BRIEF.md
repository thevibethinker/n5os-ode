# Phase 5 Orchestrator Brief

**Phase**: 5 - Workflows  
**Component**: 5.1 - Conversation End Workflow  
**Time**: 8-10 hours  
**Dependencies**: Phases 0-4 Complete

---

## Your Mission

Build ONE unified `conversation-end` command that automatically closes conversations with:
- Intelligent file organization
- Lesson extraction
- Thread export generation
- Workspace cleanup

**Key**: Port from Main, adapt for distribution, test thoroughly.

---

## V's Requirements (MANDATORY)

✅ **Auto-confirm high confidence moves** - No prompts for obvious destinations  
✅ **Freeform markdown knowledge** - Not rigid schemas  
✅ **ONE unified command** - Not separate sub-commands  
✅ **Cleanup at END** - After organization, not before

---

## Pre-Flight Checklist

Before you start:

- [ ] Load `file 'planning_prompt.md'` (MANDATORY for system work)
- [ ] Load `file 'architectural_principles.md'` (index, reference as needed)
- [ ] Read `file 'PHASE5_DETAILED_PLAN.md'` (complete spec)
- [ ] Understand the 12-phase workflow
- [ ] Review reference implementation

---

## Phase 5.1 Build Sequence

### Phase 5.1.1: Port & Streamline (2-3h)

**Goal**: Get Main script working in n5os-core

**Steps**:
1. Copy `n5_conversation_end.py` reference to n5os-core
2. Remove V-specific integrations:
   - Timeline automation
   - CRM systems
   - V-only preferences
3. Ensure conversation_registry dependency works
4. Test basic execution: `python3 N5/scripts/n5_conversation_end.py --help`

**Success**: Script runs without errors, shows help

### Phase 5.1.2: Auto-Confirm Logic (1-2h)

**Goal**: Implement smart auto-confirmation

**Add function**:
```python
def auto_confirm_high_confidence(files_by_category):
    """Auto-confirm if all moves are obvious"""
    moves = files_by_category.get("MOVE", [])
    asks = files_by_category.get("ASK", [])
    deletes = files_by_category.get("DELETE", [])
    
    # High confidence = no ASK files + standard destinations
    if asks:
        return False
    
    standard_dests = ["Documents/Temporary", "Images", "Documents/Archive", "Exports"]
    
    for item in moves:
        dest_str = str(item.get('dest', ''))
        if not any(sd in dest_str for sd in standard_dests):
            return False
    
    return True
```

**Integrate**: Call before prompting user

**Success**: No prompts for obvious moves, still asks for ambiguous files

### Phase 5.1.3: Integration & Testing (2-3h)

**Goal**: Wire everything together

**Tasks**:
1. Test on multiple conversation types:
   - Build conversation (scripts, docs)
   - Research conversation (notes, links)
   - Discussion conversation (mostly text)
   - Empty conversation
2. Verify all 12 phases execute
3. Check file organization accuracy
4. Confirm lesson extraction works
5. Validate thread export generation

**Success**: Clean execution across all conversation types

### Phase 5.1.4: Documentation & Registration (1-2h)

**Goal**: Make it discoverable and usable

**Create**:
1. `/N5/commands/conversation-end.md` - Full documentation
2. Add to `/N5/config/commands.jsonl`:
```json
{
  "id": "conversation-end",
  "name": "Conversation End",
  "trigger": "end this conversation|conversation end|close conversation",
  "description": "Complete conversation closure workflow",
  "instruction": "Execute python3 /home/workspace/N5/scripts/n5_conversation_end.py --auto",
  "tags": ["workflow", "cleanup", "core"],
  "created": "2025-10-28T00:00:00Z",
  "enabled": true
}
```

**Success**: Command discoverable via `/` slash commands

### Phase 5.1.5: Validation & Polish (2h)

**Goal**: Production-ready quality

**Tasks**:
1. Fresh thread test (P12)
2. Write 30+ tests
3. Error handling review (P19)
4. State verification (P18)
5. Documentation completeness
6. No undocumented placeholders (P21)

**Success**: All quality gates pass

---

## The 12 Phases (What the Script Does)

1. **Phase -1**: Lesson Extraction - Extract key learnings
2. **Phase 0**: Thread Export - Generate AAR
3. **Phase 1**: File Organization - Classify and move files
4. **Phase 2**: Workspace Cleanup - Remove clutter from root
5. **Phase 3**: Placeholder Scan - Detect TODO/FIXME
6. **Phase 4**: Output Review - Check AI responses for issues
7. **Phase 5**: Archive Build Tasks - Move completed build artifacts
8. **Phase 6**: Title Generation - Propose conversation title
9. **Phase 7**: Git Status - Check for uncommitted changes
10. **Phase 8**: Timeline Update - (SKIP - V-specific)
11. **Phase 9**: Registry Closure - Mark conversation complete
12. **Phase 10**: Archive Promotion - Auto-promote significant conversations

**Your job**: Make all these work together seamlessly

---

## Critical Principles

Load from `file 'architectural_principles.md'`:

**Must Apply**:
- P0 (Rule-of-Two) - Max 2 config files in context
- P5 (Anti-Overwrite) - Protect existing files
- P7 (Dry-Run) - Always support --dry-run
- P11 (Failure Modes) - Document what can go wrong
- P15 (Complete Before Claiming) - Don't say done until verified
- P18 (Verify State) - Check files actually moved
- P19 (Error Handling) - Comprehensive try/except
- P21 (Document Assumptions) - No silent placeholders

**Load planning prompt** for:
- THINK → PLAN → EXECUTE framework
- Simple Over Easy philosophy
- Flow Over Pools principle
- Trap door identification

---

## Testing Strategy

**Unit Tests** (15+):
- Each phase executes independently
- File classification accuracy
- Auto-confirm logic
- Lesson extraction
- Registry integration

**Integration Tests** (10+):
- Full workflow execution
- Multiple conversation types
- Edge cases (empty, large, complex)
- Error recovery

**End-to-End Tests** (5+):
- Fresh conversation
- Real file organization
- Actual lesson extraction
- Complete cleanup

---

## Common Pitfalls

❌ **False API Limits** (P16) - Don't invent restrictions  
❌ **Skip Error Handling** (P19) - Every phase needs try/except  
❌ **Premature Completion** (P15) - Verify before claiming done  
❌ **Wrong Language** (P22) - Python for complex logic (not shell)  
❌ **External LLM** - You ARE the LLM, do work directly  

---

## Success Metrics

**Functional**:
- ✅ 12 phases execute successfully
- ✅ Files organized correctly
- ✅ Lessons extracted
- ✅ Thread export generated
- ✅ Workspace cleaned

**Quality**:
- ✅ 30+ tests passing
- ✅ Fresh thread works (<10 min)
- ✅ Error messages clear
- ✅ Documentation complete

**Distribution**:
- ✅ No V-specific code
- ✅ Works on any n5os-core install
- ✅ Self-documenting
- ✅ Production-ready

---

## Time Check-Ins

After each sub-phase, report:
- What you completed
- Time elapsed
- Any blockers
- Next steps

**Expected velocity**: Faster than planned (Demonstrator trend is 40-45% faster)

---

## When You're Stuck

1. STOP → Step outside
2. Ask: Missing info? Wrong order? Bad approach?
3. Load more principles if needed
4. Ask V clarifying questions

---

## Ready to Start?

Say: **"Beginning Phase 5.1.1: Port & Streamline"**

Then:
1. Load planning prompt
2. Read PHASE5_DETAILED_PLAN.md
3. Review reference implementation
4. Start THINK phase
5. Build!

---

*Built with Think→Plan→Execute*  
*Quality > Speed*  
*Simple > Easy*

---

*Prepared: 2025-10-28*  
*For: Demonstrator (vademonstrator.zo.computer)*
