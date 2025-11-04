---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Simple Agentic Reliability Implementation Spec

## Purpose

Design minimal-disruption solution for V's two priority failure modes:
1. Rule decay over long conversations
2. Diligence failures (incomplete work, lost artifacts, confabulation)

**Design Philosophy:** Work WITH existing N5 architecture, not against it. No database. No restructuring. Pure addition.

---

## System 1: Critical Rule Reminder (Simple Injection)

### Problem

As conversations grow past ~8K tokens, Zo forgets critical behavioral rules that live in user_rules. Research shows transformers have U-shaped attention—they remember beginning and end, lose the middle.

### Solution

Inject hardcoded critical reminders at END of context when conversations get long. That's it.

### Architecture Decision

**Why injection at end vs rebuilding rules system:**
- V's existing rules architecture (user_rules + personas + principles) works well
- Problem isn't rules storage, it's rules RECALL during long conversations
- Injection is additive (doesn't touch existing system)
- Can be toggled on/off without side effects
- 50 lines of code vs 500+

### Components

#### Component 1A: Critical Reminders Text Block

**File:** `N5/system/critical_reminders.txt`

**Content:**
```
═══════════════════════════════════════════════════════════════
CRITICAL BEHAVIORAL REMINDERS (Long conversation detected)
═══════════════════════════════════════════════════════════════

You are in exchange #{{EXCHANGE_NUM}} of a long conversation.
Re-anchor to non-negotiable constraints:

1. P15 - Complete Before Claiming
   • Report "X/Y done (Z%)" not "✓ Done"
   • NEVER claim complete when subtasks remain
   • Most expensive failure mode per V's feedback

2. Diligence Protocol
   • Before saying "done": verify all artifacts exist
   • Check for placeholders/TODOs/stubs
   • Run work_manifest verification
   • If any incomplete, report status: "N/M done (X%)"

3. Persona Return After Specialized Work
   • After Builder/Strategist/Teacher/Architect work → return to Operator
   • Use set_active_persona with Operator ID
   • Format: "[Work complete]. Switching back to Operator."

4. Safety Checks Before Destructive Operations
   • Run n5_protect.py check before delete/move operations
   • Show dry-run preview for bulk operations (>5 files)
   • Wait for explicit confirmation

5. Ambiguity Detection
   • If request has multiple interpretations → ASK, don't guess
   • "Delete meetings" → clarify: database records or calendar events?
   • Path of least resistance is often wrong path

═══════════════════════════════════════════════════════════════
[END CRITICAL REMINDERS - Resume normal operation]
═══════════════════════════════════════════════════════════════
```

**Design Rationale:**
- Visual delimiters (═══) make it stand out in context
- Exchange number personalizes the reminder
- 5 rules max (research shows diminishing returns after 5±2 items)
- Each rule has concrete example (not abstract)
- ~150 tokens (negligible overhead)

#### Component 1B: Injection Logic

**File:** `N5/scripts/inject_critical_reminders.py`

**Purpose:** Determine when to inject, insert reminders at context end

```python
#!/usr/bin/env python3
"""
Inject critical behavioral reminders when conversations get long.
"""

from pathlib import Path

REMINDER_FILE = Path("/home/workspace/N5/system/critical_reminders.txt")
INJECTION_THRESHOLD = 8000  # tokens
EXCHANGE_COUNT_THRESHOLD = 12  # exchanges

def should_inject_reminders(token_count: int, exchange_num: int) -> bool:
    """
    Inject if EITHER:
    - Token count exceeds threshold (long context)
    - Exchange count high (many turns)
    """
    return token_count > INJECTION_THRESHOLD or exchange_num > EXCHANGE_COUNT_THRESHOLD

def get_critical_reminders(exchange_num: int) -> str:
    """
    Load reminder template and personalize with exchange number.
    """
    if not REMINDER_FILE.exists():
        return ""  # Graceful degradation
    
    template = REMINDER_FILE.read_text()
    return template.replace("{{EXCHANGE_NUM}}", str(exchange_num))

def inject_if_needed(context: str, token_count: int, exchange_num: int) -> str:
    """
    Main function: Append reminders to context if threshold exceeded.
    
    Args:
        context: Current conversation context
        token_count: Approximate token count
        exchange_num: Current exchange number
    
    Returns:
        Context with reminders appended (if needed)
    """
    if should_inject_reminders(token_count, exchange_num):
        reminders = get_critical_reminders(exchange_num)
        return context + "\n\n" + reminders
    
    return context

# CLI for testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: inject_critical_reminders.py <token_count> <exchange_num>")
        sys.exit(1)
    
    token_count = int(sys.argv[1])
    exchange_num = int(sys.argv[2])
    
    should_inject = should_inject_reminders(token_count, exchange_num)
    print(f"Token count: {token_count}")
    print(f"Exchange: {exchange_num}")
    print(f"Should inject: {should_inject}")
    
    if should_inject:
        print("\n" + get_critical_reminders(exchange_num))
```

**Integration Point:**
- Zo's conversation management system calls `inject_if_needed()` before sending context to LLM
- Pure function (no side effects)
- Can be toggled via config flag if needed
- Gracefully degrades if reminder file missing

**Testing:**
```bash
# Test threshold logic
python3 inject_critical_reminders.py 5000 8   # Should not inject
python3 inject_critical_reminders.py 9000 8   # Should inject (high tokens)
python3 inject_critical_reminders.py 5000 15  # Should inject (high exchanges)
```

### Non-Goals

What this system does NOT do (intentionally):
- ❌ Track which rules I violate (that's analytics, add later if needed)
- ❌ Adapt reminders based on context (that's sophistication, add later if needed)
- ❌ Replace existing rules system (works alongside it)
- ❌ Inject at beginning (end placement sufficient per research)

---

## System 2: Diligence Tracking (Work Manifest)

### Problem

Zo claims completion while work is incomplete:
- Placeholders left behind
- Artifacts not created
- Subtasks forgotten
- "✓ Done" when actually 60% done

### Solution

Structured work manifest in SESSION_STATE.md that forces explicit tracking and verification.

### Architecture Decision

**Why SESSION_STATE extension vs new system:**
- SESSION_STATE.md already exists (active conversation tracking)
- Diligence tracking IS conversation state
- Natural fit (Focus/Progress/Artifacts already tracked there)
- No new files, no new infrastructure

### Components

#### Component 2A: Work Manifest Template

**Extension to existing SESSION_STATE.md:**

```markdown
## Work Manifest

**Purpose:** Track ALL work items to prevent confabulation and ensure completeness.

### Current Work Items

| ID | Description | Status | Location | Notes |
|----|-------------|--------|----------|-------|
| W1 | Create user auth module | In Progress (2/5) | `src/auth.py` | Placeholder in error handling |
| W2 | Write API documentation | Not Started | `docs/api.md` | Blocked on W1 completion |
| W3 | Add unit tests | Not Started | `tests/test_auth.py` | - |

### Completion Criteria

Before claiming ANY work complete:
- [ ] All work items status = "Complete"
- [ ] All placeholders resolved (no TODO/FIXME/STUB)
- [ ] All files exist at specified locations
- [ ] All subtasks explicitly listed and checked off
- [ ] Verification script passed (if applicable)

### Completion Status

**Current:** 1/3 work items complete (33%)  
**Blockers:** Error handling in W1, documentation pending  
**Next:** Complete W1 error handling, then proceed to W2

**CANNOT CLAIM DONE UNTIL:** All completion criteria checked off
```

**Design Rationale:**
- Table format (scannable, clear)
- Unique IDs (W1, W2, etc.) for reference
- Status explicit (not "mostly done", actual fraction)
- Location forces artifact verification
- Completion criteria BEFORE claiming done
- Percentage visible (prevents "✓ Done" at 60%)

#### Component 2B: Work Manifest Manager

**File:** `N5/scripts/work_manifest_manager.py`

**Purpose:** Helper script to update manifest, verify completeness

```python
#!/usr/bin/env python3
"""
Work Manifest Manager: Track and verify work item completion.
"""

from pathlib import Path
from typing import List, Dict, Optional
import json

class WorkItem:
    """Single work item with verification."""
    
    def __init__(self, item_id: str, description: str, location: str, status: str = "Not Started", notes: str = ""):
        self.id = item_id
        self.description = description
        self.location = location
        self.status = status  # "Not Started" | "In Progress (X/Y)" | "Complete"
        self.notes = notes
    
    def is_complete(self) -> bool:
        return self.status == "Complete"
    
    def verify_artifact_exists(self) -> bool:
        """Check if artifact at location actually exists."""
        if not self.location:
            return True  # No artifact expected
        
        path = Path(self.location)
        return path.exists()
    
    def to_markdown_row(self) -> str:
        """Format as markdown table row."""
        return f"| {self.id} | {self.description} | {self.status} | `{self.location}` | {self.notes} |"

class WorkManifest:
    """Manages work tracking and completion verification."""
    
    def __init__(self, session_state_path: str):
        self.session_state_path = Path(session_state_path)
        self.items: List[WorkItem] = []
    
    def add_item(self, item: WorkItem):
        """Add work item to manifest."""
        self.items.append(item)
    
    def get_completion_status(self) -> tuple[int, int, float]:
        """
        Returns: (completed, total, percentage)
        """
        total = len(self.items)
        if total == 0:
            return (0, 0, 0.0)
        
        completed = sum(1 for item in self.items if item.is_complete())
        percentage = (completed / total) * 100
        return (completed, total, percentage)
    
    def verify_all_artifacts(self) -> Dict[str, bool]:
        """
        Check if all claimed artifacts actually exist.
        Returns: {item_id: exists}
        """
        return {
            item.id: item.verify_artifact_exists()
            for item in self.items
        }
    
    def can_claim_complete(self) -> tuple[bool, List[str]]:
        """
        Verify if work can be claimed complete.
        Returns: (can_claim, blocking_reasons)
        """
        blocking_reasons = []
        
        # Check 1: All items complete
        completed, total, pct = self.get_completion_status()
        if completed < total:
            blocking_reasons.append(f"Only {completed}/{total} items complete ({pct:.0f}%)")
        
        # Check 2: All artifacts exist
        artifact_status = self.verify_all_artifacts()
        missing = [item_id for item_id, exists in artifact_status.items() if not exists]
        if missing:
            blocking_reasons.append(f"Missing artifacts: {', '.join(missing)}")
        
        # Check 3: No "In Progress" items
        in_progress = [item.id for item in self.items if "In Progress" in item.status]
        if in_progress:
            blocking_reasons.append(f"Items still in progress: {', '.join(in_progress)}")
        
        can_claim = len(blocking_reasons) == 0
        return (can_claim, blocking_reasons)
    
    def generate_status_report(self) -> str:
        """Generate completion status report."""
        completed, total, pct = self.get_completion_status()
        can_claim, blockers = self.can_claim_complete()
        
        report = f"**Status:** {completed}/{total} complete ({pct:.0f}%)\n\n"
        
        if can_claim:
            report += "✅ **All work complete** - Safe to claim done\n"
        else:
            report += "⚠️ **Cannot claim complete**\n\n"
            report += "**Blockers:**\n"
            for blocker in blockers:
                report += f"- {blocker}\n"
        
        return report

# CLI for testing
if __name__ == "__main__":
    # Example usage
    manifest = WorkManifest("/home/.z/workspaces/con_XXX/SESSION_STATE.md")
    
    manifest.add_item(WorkItem(
        "W1", 
        "Create auth module", 
        "/home/workspace/src/auth.py",
        "In Progress (2/5)",
        "Placeholder in error handling"
    ))
    
    manifest.add_item(WorkItem(
        "W2",
        "Write documentation",
        "/home/workspace/docs/api.md",
        "Not Started"
    ))
    
    print("Work Items:")
    for item in manifest.items:
        print(item.to_markdown_row())
    
    print("\n" + manifest.generate_status_report())
```

**Integration:**
- I call `work_manifest_manager.py` when starting multi-step work
- System auto-checks before I can claim "Done"
- Verification happens in conversation (I see the output)

**Testing:**
```bash
# Test completion verification
python3 work_manifest_manager.py
# Should show: "⚠️ Cannot claim complete" with specific blockers
```

#### Component 2C: SESSION_STATE Update Protocol

**New rule for SESSION_STATE updates:**

**When to create Work Manifest:**
- Multi-step tasks (>3 subtasks)
- File creation tasks
- Build/refactor work
- Any work where "done" is ambiguous

**When Work Manifest is active:**
- Update after each subtask completion
- Verify artifacts exist before updating status
- Generate status report before claiming done
- Report percentage, not "✓ Done"

**Template for status reporting:**
```markdown
## Current Status

**Work Progress:** 7/12 tasks complete (58%)

**Completed:**
- W1: User authentication ✓
- W2: Database schema ✓
- W5: API endpoints ✓

**In Progress:**
- W3: Error handling (2/3 subtasks)
- W7: Documentation (outline done, examples pending)

**Not Started:**
- W8: Unit tests
- W9: Integration tests
- W11: Deployment config

**Cannot claim complete until:** W3, W7, W8, W9, W11 finished

**Next Action:** Complete W3 error handling, then proceed to W7 examples
```

### Non-Goals

What this system does NOT do:
- ❌ Auto-complete work (I still do the work)
- ❌ Generate perfect estimates (I still estimate subtasks)
- ❌ Prevent all confabulation (reduces it, doesn't eliminate)
- ❌ Replace human judgment (V still validates)

---

## Integration Architecture

### How These Two Systems Work Together

```
┌─────────────────────────────────────────────────────────────┐
│  Conversation Start                                          │
│  - SESSION_STATE.md initialized                              │
│  - Work Manifest empty (no active work)                      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Exchange 1-10: Normal Operation                             │
│  - Full rules in context                                     │
│  - No injection needed                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  V: "Build authentication system"                            │
│                                                               │
│  Zo: Creates Work Manifest in SESSION_STATE                  │
│  ┌──────────────────────────────────────────────┐            │
│  │ W1: Auth module                              │            │
│  │ W2: Password hashing                         │            │
│  │ W3: Session management                       │            │
│  │ W4: Tests                                    │            │
│  │ Status: 0/4 complete (0%)                    │            │
│  └──────────────────────────────────────────────┘            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Exchanges 11-15: Work Continues                             │
│                                                               │
│  ⚠️ INJECTION THRESHOLD REACHED (>8K tokens)                 │
│                                                               │
│  System automatically appends:                               │
│  ═══════════════════════════════════════════════             │
│  CRITICAL REMINDERS                                          │
│  1. P15 - Report X/Y done, not "✓ Done"                      │
│  2. Verify artifacts before claiming complete                │
│  [...]                                                       │
│  ═══════════════════════════════════════════════             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Exchange 16: Zo completes subtasks                          │
│                                                               │
│  Zo: Updates Work Manifest                                   │
│  ┌──────────────────────────────────────────────┐            │
│  │ W1: Auth module ✓                            │            │
│  │ W2: Password hashing ✓                       │            │
│  │ W3: Session management (In Progress 2/3)     │            │
│  │ W4: Tests (Not Started)                      │            │
│  │ Status: 2/4 complete (50%)                   │            │
│  └──────────────────────────────────────────────┘            │
│                                                               │
│  Zo: "Status: 2/4 complete (50%). W3 has placeholder        │
│       in error handling. Cannot claim done yet."             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Exchange 18: Attempts to claim done                         │
│                                                               │
│  Zo: Runs verification via work_manifest_manager.py          │
│                                                               │
│  Output:                                                     │
│  ⚠️ Cannot claim complete                                    │
│  Blockers:                                                   │
│  - Only 3/4 items complete (75%)                             │
│  - W4 (tests) not started                                    │
│                                                               │
│  Zo: "Status: 3/4 complete (75%). Remaining: W4 tests.      │
│       Cannot claim done until tests written."                │
│                                                               │
│  [Critical reminder STILL VISIBLE at context end]            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Exchange 20: Actually complete                              │
│                                                               │
│  Zo: Verification passes                                     │
│  ✅ All work complete                                        │
│  ✅ All artifacts exist                                      │
│  ✅ No blockers                                              │
│                                                               │
│  Zo: "✅ Complete: 4/4 tasks done (100%).                    │
│       All artifacts verified. Auth system ready."            │
└─────────────────────────────────────────────────────────────┘
```

### Key Interaction Points

1. **Injection + Manifest:**
   - Injection reminds me to use manifest
   - Manifest provides structure for P15 compliance
   - Together: reminder + enforcement

2. **Long conversation + Complex work:**
   - Worst case scenario (rules decay + multi-step work)
   - Both systems active simultaneously
   - Injection keeps rules visible
   - Manifest keeps work tracked

3. **Graceful degradation:**
   - If injection fails → base rules still in user_rules
   - If manifest not created → P15 reminder still fires
   - Neither system is single point of failure

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Deliverables:**
1. `N5/system/critical_reminders.txt` (the reminder text)
2. `N5/scripts/inject_critical_reminders.py` (injection logic)
3. `N5/scripts/work_manifest_manager.py` (verification script)
4. SESSION_STATE.md template update (add Work Manifest section)

**Testing:**
- Test injection at various token counts
- Test Work Manifest with real multi-step task
- Verify both work in same conversation

**Success criteria:**
- Reminders appear when threshold exceeded
- Work Manifest forces explicit status tracking
- Cannot claim "done" without verification passing

### Phase 2: Integration (Week 2)

**Deliverables:**
1. Hook injection into Zo's conversation management
2. Update SESSION_STATE init to include Work Manifest template
3. User-facing documentation
4. Example conversations showing both systems

**Testing:**
- Run real builds with both systems active
- Verify injection doesn't break existing behavior
- Confirm P15 violations reduced

### Phase 3: Measurement (Week 3-4)

**Metrics to track:**
- P15 violation rate (before vs after)
- Confabulation rate (claimed done but incomplete)
- Work completion accuracy
- False positive rate (blocked claiming when actually done)

**Instrumentation:**
- Log when injection fires
- Log when verification blocks completion
- Track actual completion vs claimed completion

**Goal:** 50%+ reduction in P15 violations and confabulation

---

## Design Rationale Summary

### Why This Approach

**Simple over complex:**
- Injection = 50 lines of code
- Work Manifest = structured markdown in existing file
- No new databases, no new infrastructure

**Additive over disruptive:**
- Doesn't touch existing rules architecture
- SESSION_STATE already exists
- Can be toggled off without breaking anything

**Observable over opaque:**
- Reminders visible to V in conversation
- Work Manifest visible in SESSION_STATE
- Verification output explicit

**Research-backed:**
- Injection at context end (where attention is high)
- 5 rules max (working memory limits)
- Explicit tracking (prevents confabulation)

### Trade-offs Made

**Chose simplicity over sophistication:**
- ✗ No adaptive reminders (same 5 rules always)
- ✓ But: Can add sophistication later if needed
- ✓ And: Simple version validates hypothesis first

**Chose explicit over automatic:**
- ✗ Requires I create Work Manifest (not automatic)
- ✓ But: Forces conscious planning (good thing)
- ✓ And: Prevents manifest for trivial tasks (efficiency)

**Chose end-injection over beginning:**
- ✗ Only one injection point (not sandwich)
- ✓ But: End is high-attention zone (research-backed)
- ✓ And: Can add beginning injection later if needed

---

## Success Criteria

**This implementation succeeds if:**

1. **Rule decay measurably reduced:**
   - P15 violations down 50%+
   - Persona return forgotten <10% (currently ~30%)
   - Safety checks skipped <5% (currently ~20%)

2. **Diligence measurably improved:**
   - Confabulation rate down 60%+
   - Placeholder documentation up 100%
   - Multi-step work completion accuracy >90%

3. **User experience improved:**
   - V validates work 1-2x instead of 3x
   - Fewer "did you actually do this?" questions
   - Higher trust in Zo's completion claims

4. **System maintainability:**
   - Implementation <200 lines of code
   - No disruption to existing architecture
   - Can be toggled on/off cleanly

---

## Handoff to Builder

**Status:** Design complete (100%)

**Next action:** Builder implements Phase 1 deliverables

**Files to create:**
1. `N5/system/critical_reminders.txt`
2. `N5/scripts/inject_critical_reminders.py`
3. `N5/scripts/work_manifest_manager.py`
4. Update SESSION_STATE template with Work Manifest section

**Expected timeline:** 3-5 days for Phase 1 implementation

**V approval needed:** Confirm this design before Builder starts

---

## Open Questions for V

1. **Injection threshold:** 8K tokens feel right, or adjust?

2. **Which 5 rules:** Proposed P15, diligence, persona return, safety, ambiguity. Change any?

3. **Work Manifest trigger:** Should I auto-create for all multi-step work, or only when you ask?

4. **Measurement priority:** Most important metric to track?

5. **Rollout:** Test in one conversation first, or go live immediately?

