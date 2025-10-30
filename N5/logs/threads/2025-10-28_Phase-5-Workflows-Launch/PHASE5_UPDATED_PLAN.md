# N5OS Core - Phase 5 Updated Plan

**Project**: N5 OS (Cesc v0.1)  
**Phase**: 5 - Workflows  
**Build Location**: **Demonstrator** (n5os-core)  
**Approach**: Port & Adapt aggressively from Main

---

## V's Specifications

✅ **Auto-confirm high confidence moves** - No prompts for obvious file moves  
✅ **Freeform markdown for knowledge** - No rigid schemas, natural markdown structure  
✅ **ONE unified command** - `conversation-end` as single workflow, not sub-commands  
✅ **Building on Demonstrator** - Work in `/home/workspace/n5os-core/`  

---

## Cleanup Timing Recommendation

**CLEANUP AT THE END** ✅ (V's intuition is correct)

**Why this is optimal:**
1. **Dependency order**: Process/analyze → organize → cleanup → finalize
2. **File stability**: Don't move files other phases might need
3. **Natural flow**: Cleanup is the final "close the books" step
4. **Current script structure**: Already implements this pattern

**Current workflow order** (already correct):
```
Phase -1: Lesson Extraction      [analyze]
Phase 0:  AAR Generation          [analyze]
Phase 1:  File Organization       [organize]
Phase 2:  Workspace Cleanup       [cleanup] ← Cleanup here
Phase 2.5: Placeholder Detection  [validate]
Phase 3:  Intelligence Update     [finalize]
Phase 4:  Git Status              [finalize]
Phase 5:  Registry Closure        [finalize]
Phase 6:  Archive Promotion       [finalize]
```

**Recommendation**: Keep cleanup at Phase 2, right after file organization. Perfect spot.

---

## Phase 5 Implementation: ONE Unified Command

### Design

**Command**: `conversation-end`  
**Script**: `/home/workspace/n5os-core/N5/scripts/n5_conversation_end.py` (already ported!)  
**Registry**: `/home/workspace/n5os-core/N5/config/commands.jsonl`

**NOT** building separate commands for:
- ❌ `conversation-analyze`
- ❌ `conversation-organize`  
- ❌ `conversation-cleanup`

**Instead**: ONE workflow that runs all phases sequentially.

### Current Status

**Already ported** from Main:
- ✅ `n5_conversation_end.py` (1405 lines, cleaned from 1959)
- ✅ `conversation_registry.py` (fixed logger issue)
- ✅ `n5_workspace_root_cleanup.py` (supporting script)

**What works:**
- Full workflow (Phases -1 through 6)
- Auto-confirm logic (needs minor fix)
- File classification
- AAR generation
- Registry closure
- Archive promotion

**Minor fixes needed:**
1. Fix input() EOF handling in non-interactive mode → **5 min**
2. Add auto-confirm for high-confidence moves → **10 min**
3. Test full execution (not just dry-run) → **5 min**

---

## Implementation Steps

### Step 1: Fix Auto-Confirm Logic (15 min)

**Current issue**: Script waits for input() even in non-interactive mode

**Fix**:
```python
# Step 3: Get confirmation
if dry_run:
    print("\n[DRY RUN] Skipping execution")
    confirmed = False
elif auto_confirm_high_confidence(files_by_category):  # NEW
    print("\n✓ Auto-confirming high-confidence moves")
    confirmed = True
elif "--auto" in sys.argv or "--yes" in sys.argv:
    confirmed = True
else:
    try:
        response = input("\n> ").strip().lower()
        confirmed = response in ['y', 'yes', '']
    except (EOFError, KeyboardInterrupt):
        print("\n\nSkipping due to non-interactive mode")
        confirmed = False
```

**Add auto-confirm logic**:
```python
def auto_confirm_high_confidence(files_by_category):
    """Auto-confirm if all moves are high-confidence"""
    moves = files_by_category.get("MOVE", [])
    asks = files_by_category.get("ASK", [])
    
    # High confidence: no ASK files, only obvious moves
    if not asks and len(moves) > 0:
        # Check if all moves are to standard destinations
        standard_dests = [
            "Document Inbox/Temporary",
            "Images",
            "Documents",
            "Exports"
        ]
        all_standard = all(
            any(sd in str(item['dest']) for sd in standard_dests)
            for item in moves
        )
        return all_standard
    
    return False
```

### Step 2: Register Command (5 min)

Add to `/home/workspace/n5os-core/N5/config/commands.jsonl`:

```json
{
  "name": "conversation-end",
  "description": "Close conversation with AAR, file organization, and cleanup",
  "triggers": ["end conversation", "close conversation", "wrap up", "finish conversation"],
  "script": "N5/scripts/n5_conversation_end.py",
  "args": ["--auto"],
  "category": "workflow",
  "auto_confirm": true
}
```

### Step 3: Test Full Execution (10 min)

Run on this conversation:
```bash
cd /home/workspace/n5os-core
python3 N5/scripts/n5_conversation_end.py --convo-id con_E4Qo1a8XsHzOqtGy --auto
```

Verify:
- ✅ No input() blocking
- ✅ Auto-confirms high-confidence moves
- ✅ Files moved to correct locations
- ✅ AAR generated
- ✅ Registry updated
- ✅ No errors

### Step 4: Document for Distribution (15 min)

Create `/home/workspace/n5os-core/N5/commands/conversation-end.md`:

```markdown
# Conversation End

**Command**: `conversation-end`  
**Purpose**: Close conversation with full workflow  
**Auto-confirm**: Yes (high-confidence moves)

## What It Does

1. **Extract Lessons** - Captures techniques and patterns
2. **Generate AAR** - Documents decisions and context
3. **Organize Files** - Moves files to appropriate locations
4. **Cleanup Workspace** - Removes temporary files
5. **Validate Code** - Detects placeholders and stubs
6. **Update Systems** - Registry, timeline, intelligence
7. **Archive** - Promotes significant conversations

## Usage

Natural language:
- "End this conversation"
- "Wrap up"
- "Close conversation"

Direct:
- `n5 conversation-end`

## Behavior

**Auto-confirms** when:
- All moves are to standard destinations
- No ambiguous files (ASK category empty)

**Prompts** when:
- Files need decisions
- Placeholders detected
- Git changes uncommitted

## Knowledge Structure

**Extracted knowledge** saved as freeform markdown in:
- `Knowledge/` - Reusable insights
- `Lists/` - Action items
- `Records/` - Meeting notes (if applicable)

No rigid schemas - natural markdown structure.
```

---

## Total Time Estimate

**30-45 minutes** to complete Phase 5.1:
- 15 min: Fix auto-confirm logic
- 5 min: Register command
- 10 min: Test execution
- 15 min: Documentation

**Then**: Phase 5 is COMPLETE and ready for distribution! 🎉

---

## Ready to Execute?

Say the word and I'll:
1. Fix the auto-confirm logic in `n5_conversation_end.py`
2. Test it on this conversation
3. Register the command
4. Write distribution docs

All in n5os-core (Demonstrator), ONE unified command, cleanup at the end.

**Go?**

---

*Updated: 2025-10-28 05:21 ET*
*Build Location: /home/workspace/n5os-core (Demonstrator)*
