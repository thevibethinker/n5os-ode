#!/usr/bin/env python3
"""
Meeting to Staging Bridge

Scans processed meetings ([R] state) for B05 action items
and stages them for review.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import re

# Ensure /home/workspace is in path for cross-module imports
_workspace_root = Path(__file__).parent.parent.parent
if str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

# Import from existing modules
from N5.task_system.staging import capture_staged_task, get_staged_tasks_by_source

MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")
PROCESSED_MARKER = ".action_items_staged"


def find_unprocessed_meetings() -> List[Path]:
    """
    Find meeting folders in [R] state that haven't had
    their action items staged yet.
    
    Check for marker file: .action_items_staged
    
    Returns:
        List of meeting folder paths
    """
    unprocessed = []
    
    # Walk through all week folders
    for week_folder in MEETINGS_ROOT.iterdir():
        if not week_folder.is_dir():
            continue
        
        # Check each meeting folder
        for meeting_folder in week_folder.iterdir():
            if not meeting_folder.is_dir():
                continue
            
            # Check if folder name indicates [R] state (Ready)
            # Format: YYYY-MM-DD_Name or YYYY-MM-DD_Name-[R]
            folder_name = meeting_folder.name
            
            # State marker check: [R] in folder name
            is_ready = '[R]' in folder_name
            
            # Or check for state marker file if using that pattern
            # (alternative pattern: state files in the folder)
            
            if not is_ready:
                continue
            
            # Check if already processed
            marker_file = meeting_folder / PROCESSED_MARKER
            if marker_file.exists():
                continue
            
            # Check if B05 exists
            b05_file = meeting_folder / "B05_ACTION_ITEMS.md"
            if not b05_file.exists():
                continue
            
            unprocessed.append(meeting_folder)
    
    return unprocessed


def parse_b05_action_items(b05_content: str) -> List[Dict[str, any]]:
    """
    Parse B05 action items from markdown content.
    
    Supports two formats:
    
    1. Checkbox format:
    ```markdown
    - [ ] **Assignee**: Action item description
    - [ ] **Assignee**: Another item
    ```
    
    2. Table format:
    ```markdown
    | Owner | Task | Priority | Due Date |
    | **All** | Sign up for GiveWell philanthropy session | Medium | ASAP |
    ```
    
    Args:
        b05_content: Raw markdown content from B05_ACTION_ITEMS.md
    
    Returns:
        List of action item dicts
    """
    items = []
    lines = b05_content.split('\n')
    
    # Pattern to match: - [ ] **Assignee**: Description
    checkbox_pattern = re.compile(r'^\s*-\s*\[[ xX]\]\s*\*\*([^*]+)\*\*\s*:\s*(.+)$')
    
    # Table parsing state
    in_table = False
    headers = []
    
    def is_formatting_row(cells: list) -> bool:
        """Check if row contains only markdown table formatting (---, :---, etc.)"""
        if not cells:
            return True
        for cell in cells:
            cell_stripped = cell.strip()
            # Empty cells or cells with only dash/colon patterns are formatting
            if cell_stripped and not re.match(r'^[:\-]+$', cell_stripped):
                return False
        return True
    
    for line in lines:
        line = line.strip()
        if not line:
            # Reset table state on empty lines
            in_table = False
            headers = []
            continue
            
        # Try checkbox format first
        match = checkbox_pattern.match(line)
        if match:
            assignee = match.group(1).strip()
            description = match.group(2).strip()
            
            items.append({
                'title': description,
                'assignee': assignee,
                'raw_text': line,
                'priority_bucket': 'normal',
                'domain_name': None,
                'project_name': None,
                'estimated_minutes': None,
                'first_step': None,
                'milestones': []
            })
            continue
        
        # Table format parsing
        if '|' in line:
            # This is a table row
            if line.startswith('|') and line.endswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                
                # Skip formatting rows (|---|---|---| or |:---|:---|:---|)
                if is_formatting_row(cells):
                    in_table = True
                    continue
                
                # If we have headers but haven't started parsing rows yet
                if not in_table and len(headers) == 0 and len(cells) > 1:
                    # This is the header row
                    headers = [h.lower() for h in cells]
                    in_table = True
                    continue
                
                # If we're in a table and have headers, parse row
                if in_table and headers and len(cells) >= len(headers):
                    # Try to map cells to headers
                    row_data = dict(zip(headers, cells[:len(headers)]))
                    
                    # Look for common column names
                    owner = None
                    task = None
                    priority = 'normal'
                    due_date = None
                    
                    # Try various column name variations
                    for key in ['owner', 'assignee', 'who', 'person']:
                        if key in row_data and row_data[key]:
                            owner = row_data[key]
                            break
                    
                    for key in ['task', 'description', 'action', 'what']:
                        if key in row_data and row_data[key]:
                            task = row_data[key]
                            break
                    
                    # Map priority text to bucket
                    if 'priority' in row_data and row_data['priority']:
                        priority_text = row_data['priority'].lower()
                        if 'high' in priority_text or 'strategic' in priority_text:
                            priority_bucket = 'strategic'
                        elif 'urgent' in priority_text:
                            priority_bucket = 'urgent'
                        elif 'low' in priority_text:
                            priority_bucket = 'normal'
                        else:
                            priority_bucket = 'normal'
                    
                    for key in ['due date', 'due', 'when', 'deadline']:
                        if key in row_data and row_data[key]:
                            due_date = row_data[key]
                            break
                    
                    # Only add if we have at least a task (non-empty)
                    if task and task.strip():
                        items.append({
                            'title': task.strip(),
                            'assignee': owner.strip() if owner else 'Unassigned',
                            'raw_text': line,
                            'priority_bucket': priority_bucket,
                            'domain_name': None,
                            'project_name': None,
                            'estimated_minutes': None,
                            'first_step': None,
                            'milestones': []
                        })
    
    return items


def process_meeting_action_items(meeting_folder: Path, dry_run: bool = False) -> List[int]:
    """
    Extract action items from B05 and stage them.
    
    Args:
        meeting_folder: Path to meeting folder
        dry_run: If True, don't actually stage items, just return count
    
    Returns:
        List of staged_task IDs (or simulated IDs if dry_run)
    """
    b05_path = meeting_folder / "B05_ACTION_ITEMS.md"
    if not b05_path.exists():
        return []
    
    # Parse B05
    items = parse_b05_action_items(b05_path.read_text())
    
    if not items:
        return []
    
    staged_ids = []
    source_id = meeting_folder.name  # Use folder name as source ID
    
    for item in items:
        # Build suggestions dict for staging
        suggestions = {
            'domain': item.get('domain_name') or '',
            'project': item.get('project_name') or '',
            'priority': item.get('priority_bucket', 'normal')
        }
        
        # Add assignee to context if available
        context = item.get('raw_text', '')
        if item.get('assignee'):
            context = f"Assignee: {item['assignee']}\n{context}"
        
        if dry_run:
            # Simulate staging
            staged_id = -1 * (len(staged_ids) + 1)  # Negative IDs for dry run
            print(f"[DRY RUN] Would stage: {item['title']}")
            print(f"  From: {source_id}")
            print(f"  Context: {context[:80]}...")
        else:
            # Actually stage the task
            staged_id = capture_staged_task(
                title=item['title'],
                source_type='meeting',
                source_id=source_id,
                context=context,
                description=item.get('raw_text', ''),
                suggestions=suggestions
            )
        
        staged_ids.append(staged_id)
    
    # Mark meeting as processed (only if not dry run)
    if not dry_run and staged_ids:
        marker_file = meeting_folder / PROCESSED_MARKER
        marker_file.write_text(datetime.now().isoformat())
    
    return staged_ids


def process_all_pending_meetings(dry_run: bool = False) -> Dict[str, List[int]]:
    """
    Process all meetings with unstaged action items.
    
    Args:
        dry_run: If True, don't actually stage items
    
    Returns:
        Dict of meeting_folder_name -> staged_ids
    """
    results = {}
    unprocessed = find_unprocessed_meetings()
    
    print(f"Found {len(unprocessed)} meetings with unstaged action items")
    
    for meeting_folder in unprocessed:
        folder_name = meeting_folder.name
        print(f"\nProcessing: {folder_name}")
        
        staged_ids = process_meeting_action_items(meeting_folder, dry_run=dry_run)
        
        if staged_ids:
            results[folder_name] = staged_ids
            print(f"  -> Staged {len(staged_ids)} action items")
    
    return results


# CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Bridge meeting action items to task staging"
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate without actually staging')
    parser.add_argument('--meeting', help='Process specific meeting folder name')
    args = parser.parse_args()
    
    if args.meeting:
        # Process specific meeting
        # Try to find it
        meeting_folder = None
        for week_folder in MEETINGS_ROOT.iterdir():
            if not week_folder.is_dir():
                continue
            candidate = week_folder / args.meeting
            if candidate.exists() and candidate.is_dir():
                meeting_folder = candidate
                break
        
        if not meeting_folder:
            print(f"Error: Meeting folder '{args.meeting}' not found")
            exit(1)
        
        print(f"Processing specific meeting: {meeting_folder}")
        staged_ids = process_meeting_action_items(meeting_folder, dry_run=args.dry_run)
        print(f"\nStaged {len(staged_ids)} action items")
    else:
        # Process all pending
        results = process_all_pending_meetings(dry_run=args.dry_run)
        
        total_staged = sum(len(ids) for ids in results.values())
        print(f"\n{'='*60}")
        if args.dry_run:
            print(f"DRY RUN: Would stage {total_staged} action items")
        else:
            print(f"Staged {total_staged} action items from {len(results)} meetings")
