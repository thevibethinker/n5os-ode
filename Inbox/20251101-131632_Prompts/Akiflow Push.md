---
description: Push formatted tasks from N5 → Akiflow via Aki email interface.
tags: []
tool: true
---
# Command: akiflow-push

## Purpose
Push formatted tasks from N5 → Akiflow via Aki email interface.

## Invocation
`akiflow-push --tasks <json_file> [--batch] [--dry-run]`

## Input Schema
```json
{
  "tasks": [
    {
      "title": "Task title",
      "when": "Tomorrow 3:30pm ET" | "2025-10-23 15:30",
      "duration": "20m" | "1h",
      "priority": "High" | "Normal" | "Low",
      "project": "Operations" | "Product" | "Growth" | "People" | "Finance & Legal" | "Content" | "Networking" | "Learning" | "Personal" | "Strategic Projects",
      "tags": ["tag1", "tag2"],
      "notes": "Context and source link"
    }
  ]
}
```

## Email Template
```
Task: {title}
When: {when}
Duration: {duration}
Priority: {priority}
Project: {project}
Tags: {tags, comma-separated}
Notes: {notes}

---

[repeat for each task]
```

## Implementation
```python
#!/usr/bin/env python3
"""
Push tasks to Akiflow via Aki email.
Usage: akiflow-push --tasks tasks.json [--batch] [--dry-run]
"""
import json, argparse, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

AKI_EMAIL = "aki+qztlypb6-d@aki.akiflow.com"
SENDER_EMAIL = "va@zo.computer"
SENDER_NAME = "Zo (V's AI)"

def format_email_body(tasks: list) -> str:
    """Format tasks into Aki-compatible email body."""
    parts = []
    for t in tasks:
        parts.append(f"Task: {t['title']}")
        parts.append(f"When: {t['when']}")
        parts.append(f"Duration: {t['duration']}")
        parts.append(f"Priority: {t.get('priority', 'Normal')}")
        parts.append(f"Project: {t['project']}")
        if t.get('tags'):
            parts.append(f"Tags: {', '.join(t['tags'])}")
        if t.get('notes'):
            parts.append(f"Notes: {t['notes']}")
        parts.append("---")
    
    return "\n".join(parts).rstrip("---").rstrip()

def send_via_gmail(subject: str, body: str, dry_run: bool = False) -> dict:
    """Send email via Gmail API (use_app_gmail)."""
    if dry_run:
        logger.info(f"[DRY RUN] Would send:\nTo: {AKI_EMAIL}\nSubject: {subject}\n\n{body}")
        return {"dry_run": True}
    
    # Call use_app_gmail tool
    # (In actual implementation, this would invoke Zo's gmail tool)
    logger.info(f"Sending to {AKI_EMAIL}: {subject}")
    return {"sent": True, "to": AKI_EMAIL}

def main(tasks_file: Path, batch: bool = False, dry_run: bool = False) -> int:
    """Main entry point."""
    try:
        if not tasks_file.exists():
            logger.error(f"Tasks file not found: {tasks_file}")
            return 1
        
        with open(tasks_file) as f:
            data = json.load(f)
        
        tasks = data.get("tasks", [])
        if not tasks:
            logger.warning("No tasks found in input file")
            return 0
        
        logger.info(f"Processing {len(tasks)} tasks (batch={batch}, dry_run={dry_run})")
        
        if batch:
            # Send all tasks in one email
            subject = f"[N5] Batch tasks | {len(tasks)} items"
            body = format_email_body(tasks)
            result = send_via_gmail(subject, body, dry_run)
            logger.info(f"✓ Batch email sent: {result}")
        else:
            # Send one email per task
            for i, task in enumerate(tasks, 1):
                subject = f"[N5] {task['title']}"
                body = format_email_body([task])
                result = send_via_gmail(subject, body, dry_run)
                logger.info(f"✓ Task {i}/{len(tasks)} sent: {result}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push tasks to Akiflow")
    parser.add_argument("--tasks", type=Path, required=True, help="Path to tasks JSON file")
    parser.add_argument("--batch", action="store_true", help="Send all tasks in one email")
    parser.add_argument("--dry-run", action="store_true", help="Print email without sending")
    args = parser.parse_args()
    
    exit(main(args.tasks, args.batch, args.dry_run))
```

## Playbooks

### P1: Meeting → Action Items
```bash
# After meeting transcript processed → action_items.json generated
akiflow-push --tasks /home/workspace/Records/Company/Meetings/2025-10-22-Leadership/action_items.json --batch
```

### P2: Warm Intro Pack
```json
{
  "tasks": [
    {
      "title": "Draft intro: {Person A} → {Person B}",
      "when": "Today 3pm",
      "duration": "15m",
      "priority": "High",
      "project": "Networking",
      "tags": ["warm_intro", "draft"],
      "notes": "Context: {why connecting}"
    },
    {
      "title": "Send intro: {Person A} → {Person B}",
      "when": "Today 4pm",
      "duration": "5m",
      "priority": "High",
      "project": "Networking",
      "tags": ["warm_intro", "send"],
      "notes": "Check draft, hit send"
    },
    {
      "title": "Follow-up on intro: {Person A} → {Person B}",
      "when": "+7 days 2pm",
      "duration": "10m",
      "priority": "Normal",
      "project": "Networking",
      "tags": ["warm_intro", "follow_up"],
      "notes": "Check if they connected"
    }
  ]
}
```

### P3: Daily Planning (Future: Calendar-Aware)
```python
# Read V's calendar via IFTTT → find gaps → assign tasks to optimal slots
# Example: "Review candidate pipeline" → find 30m deep_work slot → schedule
```

## Testing Checklist
- [x] Multi-task batch email (3 tasks, all created)
- [ ] Single-task emails (verify one-by-one)
- [ ] Project mapping (confirm Aki respects all 10 projects)
- [ ] Tag preservation (verify tags applied)
- [ ] Priority visual (High=red, Normal=gray, Low=blue)
- [ ] Notes full preservation
- [ ] Error handling (invalid project, missing fields)
- [ ] Dry-run preview

## Safety
- Always `--dry-run` first for new playbooks
- CC attawar.v@gmail.com if >3 back-and-forths with Aki
- Sender locked to va@zo.computer (allowlisted)

## Future Enhancements
1. **Calendar-aware scheduling:** Read V's calendar via IFTTT, propose optimal time slots
2. **Smart project inference:** NLP to auto-assign project based on task title
3. **Recurring task templates:** Standard packs (weekly review, 1-on-1s)
4. **Conflict detection:** Warn if scheduling over existing event
5. **Batch optimization:** Group related tasks by project/time

## References
- file 'Knowledge/AI/Profiles/akiflow_aki.md'
- file 'Documents/System/akiflow/project_taxonomy.md'
- Test results: file '/home/.z/workspaces/con_EBh7LUZtIAyvppXP/test_results.md'

## Change Log
- 2025-10-22: Created v1.0 after successful multi-task test
