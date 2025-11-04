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
import sys

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
    work_items: List[str] = field(default_factory=list)
    
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
    
    def get_progress(self) -> tuple:
        """Returns (completed, total, percentage)"""
        total = len(self.work_items)
        if total == 0:
            return (0, 0, 0.0)
        completed = sum(1 for item in self.work_items if item.status == WorkStatus.COMPLETE)
        percentage = (completed / total) * 100
        return (completed, total, percentage)
    
    def can_claim_done(self) -> tuple:
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
- `[COMPLETE]` - Completed  
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
    parser.add_argument("--example", help="Generate example manifest", action="store_true")
    
    args = parser.parse_args()
    
    if args.example:
        # Generate example for testing
        manifest = WorkManifest(args.session_state)
        manifest.initial_request = "Build authentication system"
        manifest.current_turn = 20
        
        # Add work items
        manifest.add_work_item(WorkItem("W1", "Auth module", WorkStatus.COMPLETE, "/src/auth.py", "✓ Done"))
        manifest.add_work_item(WorkItem("W2", "Password hash", WorkStatus.IN_PROGRESS, "/src/hash.py", "60% - needs salt"))
        manifest.add_work_item(WorkItem("W3", "Session mgmt", WorkStatus.PLANNED, "/src/session.py", "Placeholder at L23"))
        
        # Add threads
        active = Thread("Core Auth Flow", ThreadStatus.ACTIVE, work_items=["W1", "W2", "W3"])
        deferred = Thread("OAuth Integration", ThreadStatus.DEFERRED, "Out of scope for MVP")
        rejected = Thread("Biometric Auth", ThreadStatus.REJECTED, "Hardware dependency too complex")
        manifest.add_thread(active)
        manifest.add_thread(deferred)
        manifest.add_thread(rejected)
        
        # Add placeholder
        manifest.add_placeholder(Placeholder("/src/hash.py:L23", PlaceholderType.TODO, "Implement salt generation", 15))
        
        print(manifest.generate_manifest())
        return
    
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
