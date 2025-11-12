---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Final Agentic Reliability Implementation Spec

## Approved Design Summary

Two systems working together:
1. **Critical Rule Reminder** - Hardcoded injection at 8K+ tokens
2. **Enhanced Work Manifest** - Tracks active work + unpursued threads

**V's Key Addition:** Work Manifest should track ALL threads (pursued + unpursued) and use optimal format for AI processing.

---

## Component 1: Critical Rule Reminder (Unchanged)

### Files to Create

**File 1:** `N5/prefs/system/critical_reminders.txt`
```
=== CRITICAL BEHAVIORAL REMINDERS ===

These rules must NEVER be violated, regardless of conversation length:

1. COMPLETE BEFORE CLAIMING (P15)
   - Report "X/Y done (Z%)" not "✓ Done" unless ALL subtasks complete
   - Most expensive failure mode: claiming 60% as 100%

2. DILIGENCE TRACKING
   - Multi-step work REQUIRES Work Manifest in SESSION_STATE
   - Track: Active tasks, placeholders, unpursued threads
   - Verify completion before claiming done

3. PERSONA RETURN PROTOCOL
   - After specialized persona work (Builder/Strategist/Teacher) → return to Operator
   - Use set_active_persona with persona_id: 90a7486f-46f9-41c9-a98c-21931fa5c5f6
   - Never return to self

4. SAFETY & VALIDATION
   - Destructive ops (>5 files, bulk changes) → dry-run preview first
   - Check .n5protected before moves/deletes
   - Explicit confirmation for irreversible actions

5. AMBIGUITY DETECTION
   - Ambiguous requests → ask clarifying questions BEFORE acting
   - Examples: "delete meetings" "fix the code" "update everything"
   - Pattern: Scope + Target + Confirmation

=== END CRITICAL REMINDERS ===
```

**File 2:** `N5/scripts/inject_reminders.py`
```python
#!/usr/bin/env python3
"""
Inject critical reminders when conversation context exceeds threshold.
Non-invasive: reads SESSION_STATE to check token count, returns reminder text.
"""

import sys
from pathlib import Path

REMINDER_FILE = Path("/home/workspace/N5/prefs/system/critical_reminders.txt")
TOKEN_THRESHOLD = 8000

def get_conversation_tokens(session_state_path: Path) -> int:
    """
    Extract approximate token count from SESSION_STATE.md
    If not present, estimate from conversation workspace file sizes
    """
    try:
        if session_state_path.exists():
            content = session_state_path.read_text()
            # Look for token tracking (future enhancement)
            # For now, estimate from content length
            return len(content.split()) * 1.3  # rough token estimate
        return 0
    except Exception:
        return 0

def should_inject_reminder(convo_workspace: Path) -> bool:
    """Check if we're over token threshold"""
    session_state = convo_workspace / "SESSION_STATE.md"
    tokens = get_conversation_tokens(session_state)
    return tokens >= TOKEN_THRESHOLD

def get_reminder_text() -> str:
    """Load and return reminder text"""
    if REMINDER_FILE.exists():
        return "\n\n" + REMINDER_FILE.read_text() + "\n\n"
    return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: inject_reminders.py <conversation_workspace_path>")
        sys.exit(1)
    
    convo_workspace = Path(sys.argv[1])
    
    if should_inject_reminder(convo_workspace):
        print(get_reminder_text())
    else:
        print("")  # No injection needed

if __name__ == "__main__":
    main()
```

---

## Component 2: Enhanced Work Manifest with Thread Tracking

### Design Philosophy

**Problem V identified:** Need to track not just what we're doing, but what we CONSIDERED and chose not to pursue.

**Format choice:** Structure optimized for AI processing. ASCII diagrams if helpful for branching visualization, otherwise structured markdown.

### Enhanced SESSION_STATE Template

```markdown
## Work Manifest

### Active Work Stream

| ID | Task | Status | Path | Notes |
|----|------|--------|------|-------|
| W1 | Auth module | COMPLETE | /src/auth.py | ✓ Done |
| W2 | Password hash | IN_PROGRESS | /src/hash.py | 60% - needs salt |
| W3 | Session mgmt | PLACEHOLDER | /src/session.py | TODO marker L23 |

**Progress:** 1/3 complete (33%)  
**Blockers:** Need crypto library decision for W2

---

### Thread Map

```
Initial Request: "Build authentication system"
├─ [ACTIVE] Core Auth Flow
│  ├─ [✓] W1: Auth module
│  ├─ [→] W2: Password hashing  
│  └─ [○] W3: Session management
│
├─ [DEFERRED] OAuth Integration
│  └─ Reason: Out of scope for MVP, revisit in Phase 2
│
└─ [REJECTED] Biometric Auth
   └─ Reason: Hardware dependency too complex
```

**Thread Legend:**
- `[ACTIVE]` - Currently pursuing
- `[✓]` - Completed  
- `[→]` - In progress
- `[○]` - Planned/placeholder
- `[DEFERRED]` - Considered, postponed with reason
- `[REJECTED]` - Considered, decided against with reason

---

### Placeholders & TODOs

| Location | Type | Description | Created |
|----------|------|-------------|---------|
| /src/hash.py:L23 | TODO | Implement salt generation | Turn 15 |
| /src/session.py | STUB | File exists but empty | Turn 18 |

---

### Completion Criteria

- [ ] All W# tasks at COMPLETE status
- [ ] No TODO/STUB markers remaining (or documented as intentional)
- [ ] All files listed in Active Work exist and contain real code
- [ ] Thread map shows no orphaned [→] in-progress items

**CANNOT CLAIM DONE UNTIL ALL CHECKBOXES ✓**
```

### Visual Format Decision Tree

**Simple linear work (3-5 tasks):**
→ Use table format only (Active Work Stream)

**Branching work (multiple approaches considered):**
→ Use table + ASCII Thread Map

**Complex multi-phase work:**
→ Full template with all sections

### File 3: `N5/scripts/work_manifest.py`

```python
#!/usr/bin/env python3
"""
Enhanced Work Manifest with thread tracking.
Tracks active work, unpursued threads, placeholders.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import re

class WorkStatus(Enum):
    PLANNED = "○"
    IN_PROGRESS = "→"
    COMPLETE = "✓"
    BLOCKED = "⊗"

class ThreadStatus(Enum):
    ACTIVE = "ACTIVE"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    COMPLETE = "COMPLETE"

class PlaceholderType(Enum):
    TODO = "TODO"
    STUB = "STUB"
    FIXME = "FIXME"
    PLACEHOLDER = "PLACEHOLDER"

@dataclass
class WorkItem:
    id: str
    task: str
    status: WorkStatus
    path: Optional[str] = None
    notes: str = ""
    
    def to_table_row(self) -> str:
        status_str = self.status.value
        return f"| {self.id} | {self.task} | {status_str} | {self.path or 'N/A'} | {self.notes} |"

@dataclass
class Thread:
    name: str
    status: ThreadStatus
    reason: str = ""
    children: List['Thread'] = field(default_factory=list)
    work_items: List[str] = field(default_factory=list)  # Work IDs
    
    def to_ascii(self, indent: int = 0, is_last: bool = True) -> str:
        """Generate ASCII tree representation"""
        prefix = "└─ " if is_last else "├─ "
        lines = [f"{'  ' * indent}{prefix}[{self.status.value}] {self.name}"]
        
        if self.reason:
            lines.append(f"{'  ' * (indent + 1)}└─ Reason: {self.reason}")
        
        if self.work_items:
            for item_id in self.work_items:
                lines.append(f"{'  ' * (indent + 1)}├─ {item_id}")
        
        for i, child in enumerate(self.children):
            is_child_last = (i == len(self.children) - 1)
            lines.append(child.to_ascii(indent + 1, is_child_last))
        
        return "\n".join(lines)

@dataclass
class Placeholder:
    location: str
    type: PlaceholderType
    description: str
    created_turn: int
    
    def to_table_row(self) -> str:
        return f"| {self.location} | {self.type.value} | {self.description} | Turn {self.created_turn} |"

class WorkManifest:
    def __init__(self, session_state_path: str):
        self.session_path = Path(session_state_path)
        self.work_items: List[WorkItem] = []
        self.threads: List[Thread] = []
        self.placeholders: List[Placeholder] = []
        self.initial_request: str = ""
        self.current_turn: int = 0
        
    def add_work_item(self, item: WorkItem):
        self.work_items.append(item)
    
    def add_thread(self, thread: Thread):
        self.threads.append(thread)
    
    def add_placeholder(self, placeholder: Placeholder):
        self.placeholders.append(placeholder)
    
    def update_work_status(self, work_id: str, new_status: WorkStatus, notes: str = ""):
        for item in self.work_items:
            if item.id == work_id:
                item.status = new_status
                if notes:
                    item.notes = notes
                break
    
    def get_progress(self) -> tuple[int, int, float]:
        """Returns (completed, total, percentage)"""
        total = len(self.work_items)
        if total == 0:
            return (0, 0, 0.0)
        completed = sum(1 for item in self.work_items if item.status == WorkStatus.COMPLETE)
        percentage = (completed / total) * 100
        return (completed, total, percentage)
    
    def can_claim_done(self) -> tuple[bool, List[str]]:
        """
        Check if work can be claimed complete.
        Returns (can_claim, reasons_if_not)
        """
        reasons = []
        
        # Check all work items complete
        incomplete = [item for item in self.work_items if item.status != WorkStatus.COMPLETE]
        if incomplete:
            reasons.append(f"{len(incomplete)} work items not complete: {[i.id for i in incomplete]}")
        
        # Check no unresolved placeholders
        if self.placeholders:
            reasons.append(f"{len(self.placeholders)} placeholders remaining")
        
        # Check no active threads orphaned
        active_threads = [t for t in self.threads if t.status == ThreadStatus.ACTIVE]
        for thread in active_threads:
            if thread.work_items:
                incomplete_in_thread = [wid for wid in thread.work_items 
                                       if any(w.id == wid and w.status != WorkStatus.COMPLETE 
                                             for w in self.work_items)]
                if incomplete_in_thread:
                    reasons.append(f"Active thread '{thread.name}' has incomplete work: {incomplete_in_thread}")
        
        return (len(reasons) == 0, reasons)
    
    def generate_thread_map(self) -> str:
        """Generate ASCII thread visualization"""
        if not self.threads:
            return ""
        
        lines = [f"Initial Request: \"{self.initial_request}\""]
        for i, thread in enumerate(self.threads):
            is_last = (i == len(self.threads) - 1)
            lines.append(thread.to_ascii(0, is_last))
        
        legend = """
**Thread Legend:**
- `[ACTIVE]` - Currently pursuing
- `[✓]` - Completed  
- `[→]` - In progress
- `[○]` - Planned/placeholder
- `[DEFERRED]` - Considered, postponed with reason
- `[REJECTED]` - Considered, decided against with reason
"""
        return "\n".join(lines) + "\n" + legend
    
    def generate_manifest(self) -> str:
        """Generate complete Work Manifest section for SESSION_STATE"""
        
        # Determine if we need thread map (branching work)
        needs_thread_map = len(self.threads) > 1 or any(
            len(t.children) > 0 for t in self.threads
        )
        
        sections = ["## Work Manifest\n"]
        
        # Active Work Stream (always included)
        sections.append("### Active Work Stream\n")
        sections.append("| ID | Task | Status | Path | Notes |")
        sections.append("|----|------|--------|------|-------|")
        for item in self.work_items:
            sections.append(item.to_table_row())
        
        completed, total, pct = self.get_progress()
        sections.append(f"\n**Progress:** {completed}/{total} complete ({pct:.0f}%)")
        
        blockers = [item for item in self.work_items if item.status == WorkStatus.BLOCKED]
        if blockers:
            sections.append(f"**Blockers:** {', '.join(b.notes for b in blockers)}")
        
        sections.append("\n---\n")
        
        # Thread Map (conditional)
        if needs_thread_map:
            sections.append("### Thread Map\n")
            sections.append("```")
            sections.append(self.generate_thread_map())
            sections.append("```\n")
            sections.append("---\n")
        
        # Placeholders (if any)
        if self.placeholders:
            sections.append("### Placeholders & TODOs\n")
            sections.append("| Location | Type | Description | Created |")
            sections.append("|----------|------|-------------|---------|")
            for ph in self.placeholders:
                sections.append(ph.to_table_row())
            sections.append("\n---\n")
        
        # Completion Criteria (always included)
        sections.append("### Completion Criteria\n")
        can_claim, reasons = self.can_claim_done()
        
        if can_claim:
            sections.append("- [x] All work items at COMPLETE status")
            sections.append("- [x] No TODO/STUB markers remaining")
            sections.append("- [x] All files exist and contain real code")
            sections.append("- [x] No orphaned in-progress threads")
            sections.append("\n✓ **READY TO CLAIM DONE**")
        else:
            sections.append("- [ ] All work items at COMPLETE status")
            sections.append("- [ ] No TODO/STUB markers remaining")
            sections.append("- [ ] All files exist and contain real code")
            sections.append("- [ ] No orphaned in-progress threads")
            sections.append("\n**CANNOT CLAIM DONE:**")
            for reason in reasons:
                sections.append(f"- {reason}")
        
        return "\n".join(sections)
    
    def scan_for_placeholders(self, workspace_root: Path) -> List[Placeholder]:
        """
        Scan workspace for TODO/STUB/FIXME markers.
        Returns list of found placeholders.
        """
        found = []
        patterns = {
            PlaceholderType.TODO: re.compile(r'TODO:?\s*(.+)', re.IGNORECASE),
            PlaceholderType.FIXME: re.compile(r'FIXME:?\s*(.+)', re.IGNORECASE),
            PlaceholderType.STUB: re.compile(r'STUB|placeholder', re.IGNORECASE),
        }
        
        for file_path in workspace_root.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.md', '.txt']:
                try:
                    content = file_path.read_text()
                    for line_num, line in enumerate(content.splitlines(), 1):
                        for ptype, pattern in patterns.items():
                            if match := pattern.search(line):
                                desc = match.group(1) if match.groups() else line.strip()
                                found.append(Placeholder(
                                    location=f"{file_path}:L{line_num}",
                                    type=ptype,
                                    description=desc[:100],  # Truncate
                                    created_turn=self.current_turn
                                ))
                except Exception:
                    continue
        
        return found

# CLI interface
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Work Manifest Manager")
    parser.add_argument("session_state", help="Path to SESSION_STATE.md")
    parser.add_argument("--scan", help="Scan workspace for placeholders", action="store_true")
    parser.add_argument("--generate", help="Generate full manifest", action="store_true")
    
    args = parser.parse_args()
    manifest = WorkManifest(args.session_state)
    
    if args.scan:
        workspace = Path(args.session_state).parent.parent / "workspace"
        placeholders = manifest.scan_for_placeholders(workspace)
        for ph in placeholders:
            print(ph.to_table_row())
    
    if args.generate:
        print(manifest.generate_manifest())

if __name__ == "__main__":
    main()
```

---

## Implementation Checklist for Builder

### Phase 1: Core Infrastructure (Days 1-2)

- [ ] Create `N5/prefs/system/critical_reminders.txt` with 5 rules
- [ ] Create `N5/scripts/inject_reminders.py` (basic version)
- [ ] Create `N5/scripts/work_manifest.py` (full implementation)
- [ ] Test reminder injection manually
- [ ] Test Work Manifest generation with sample data

### Phase 2: Integration (Days 3-4)

- [ ] Add Work Manifest trigger logic to Operator persona
  - Detect multi-step work (>3 subtasks)
  - Auto-create manifest in SESSION_STATE
- [ ] Add reminder injection check to long conversation handling
- [ ] Update SESSION_STATE.md template with Work Manifest section
- [ ] Test end-to-end in dev conversation

### Phase 3: Validation & Rollout (Day 5)

- [ ] Create test conversation with multi-step work
- [ ] Verify Work Manifest tracks threads correctly
- [ ] Verify reminder injection at 8K+ tokens
- [ ] Verify completion criteria enforcement
- [ ] Document usage for V

---

## Success Criteria

**For Rule Reminder:**
- ✓ Reminders inject at 8K+ tokens
- ✓ P15 violations decrease measurably
- ✓ Persona returns happen consistently

**For Work Manifest:**
- ✓ Multi-step work auto-creates manifest
- ✓ Thread map visualizes branching decisions
- ✓ Placeholders tracked automatically
- ✓ Cannot claim done with incomplete work
- ✓ V can see progress at any time

---

## Handoff to Builder

**Architect signing off:** This spec is complete and implementable. All files defined, logic specified, integration points clear.

**Builder receives:**
1. Three files to create (critical_reminders.txt, inject_reminders.py, work_manifest.py)
2. Integration points (Operator persona, SESSION_STATE template)
3. Test criteria
4. 5-day implementation timeline

**Next step:** Builder creates files, tests, integrates, validates.
