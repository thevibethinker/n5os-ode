#!/usr/bin/env python3
"""
ZTH Spawn Worker Generator

Generates self-contained worker files from B00 Zo Take Heed entries.
These workers can be auto-executed or queued for manual processing.

NEW in v1.1: Direct execution for list/deal/CRM operations via existing N5 scripts.

Usage:
    python3 zth_spawn_worker.py --meeting-folder <path> --b00-file <path>
    python3 zth_spawn_worker.py --meeting-folder <path>  # auto-finds B00
    python3 zth_spawn_worker.py --test
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import subprocess

# Task type to title mapping
TASK_TITLES = {
    "blurb": "Blurb Generation",
    "follow_up_email": "Follow-Up Email",
    "warm_intro": "Warm Introduction",
    "research": "Research Request",
    "custom": "Custom Task",
    "directive": "Directive (Inline)",
}

# Task type to template flags
TASK_FLAGS = {
    "blurb": "is_blurb",
    "follow_up_email": "is_follow_up_email",
    "warm_intro": "is_warm_intro",
    "research": "is_research",
    "custom": "is_custom",
}

# Task types that execute directly (no worker file needed)
DIRECT_EXECUTION_TYPES = {
    "list_add",
    "deal_add",
    "deal_update",
    "crm_contact",
    "intro_lead",
}


def load_b00_entries(b00_path: Path) -> list[dict]:
    """Load B00 JSONL entries."""
    entries = []
    if not b00_path.exists():
        return entries
    
    content = b00_path.read_text().strip()
    if not content or content.startswith("#"):
        return entries
    
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    return entries


def get_meeting_info(meeting_folder: Path) -> dict:
    """Extract meeting info from manifest or folder name."""
    manifest_path = meeting_folder / "manifest.json"
    
    info = {
        "meeting_id": meeting_folder.name,
        "meeting_title": meeting_folder.name.replace("_", " ").replace("-", " "),
        "meeting_folder": str(meeting_folder),
    }
    
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            info["meeting_id"] = manifest.get("meeting_id", info["meeting_id"])
            info["meeting_title"] = manifest.get("generated_at", info["meeting_title"])
            if "attendees" in manifest:
                info["meeting_title"] = f"{manifest['attendees'][0]} Meeting" if manifest['attendees'] else info["meeting_title"]
        except (json.JSONDecodeError, KeyError):
            pass
    
    return info


def generate_worker(entry: dict, meeting_folder: Path, provenance: str = "zth_spawn_worker") -> str:
    """Generate worker markdown from B00 entry."""
    meeting_info = get_meeting_info(meeting_folder)
    now = datetime.now().strftime("%Y-%m-%d")
    
    task_type = entry.get("task_type", "custom")
    
    # Build frontmatter
    frontmatter = f"""---
created: {now}
last_edited: {now}
version: 1.0
provenance: {provenance}
type: zth_worker
zth_id: {entry.get('id', 'ZTH-000')}
task_type: {task_type}
execution_policy: {entry.get('execution_policy', 'queue')}
meeting_id: {meeting_info['meeting_id']}
meeting_folder: {meeting_info['meeting_folder']}
status: pending
---"""

    # Task title
    task_title = TASK_TITLES.get(task_type, "Unknown Task")
    
    # Build body
    body = f"""
# ZTH Worker: {task_title}

## Original Cue

> "{entry.get('raw_cue', '')}"

**Timestamp:** {entry.get('timestamp', 'unknown')}

## Meeting Context

**Meeting:** {meeting_info['meeting_title']}
**Folder:** `{meeting_info['meeting_folder']}`

{entry.get('context', 'No additional context provided.')}

## Instruction

{entry.get('instruction', 'No instruction provided.')}

## Execution
"""

    # Task-specific execution instructions
    additional_params = entry.get("additional_params", {})
    recipient_hint = additional_params.get("recipient_hint", "attendees")
    
    if task_type == "blurb":
        body += f"""
Run: `file 'Prompts/Blurb-Generator.prompt.md'`
With meeting context from: `file '{meeting_info['meeting_folder']}/B01_DETAILED_RECAP.md'`

**Voice Requirements:**
```bash
python3 N5/scripts/retrieve_voice_lessons.py --content-type linkedin_post --include-global
```
"""
    elif task_type == "follow_up_email":
        body += f"""
Run: `file 'Prompts/Follow-Up Email Generator.prompt.md'`
With meeting context from: `file '{meeting_info['meeting_folder']}/B01_DETAILED_RECAP.md'`

**Voice Requirements:**
```bash
python3 N5/scripts/retrieve_voice_lessons.py --content-type follow_up --include-global
```

**Additional Context:**
- Recipient hint: {recipient_hint}
- Apply standard follow-up voice and formatting
"""
    elif task_type == "warm_intro":
        body += f"""
Run: `file 'Prompts/Meeting Warm Intro Generation.prompt.md'`
With meeting context from: `file '{meeting_info['meeting_folder']}/B01_DETAILED_RECAP.md'`

**Voice Requirements:**
```bash
python3 N5/scripts/retrieve_voice_lessons.py --content-type intro --include-global
```

**Additional Context:**
- Target: {recipient_hint}
"""
    elif task_type == "research":
        body += f"""
**Research Request** (queued for manual execution)

Topic: {entry.get('instruction', '')}

Suggested approach:
1. Use `web_research` with appropriate category filters
2. Check existing `Knowledge/` for related content
3. Output findings to `{meeting_info['meeting_folder']}/research/{entry.get('id', 'ZTH-000')}_findings.md`
"""
    else:  # custom or directive
        body += f"""
**{task_title}** (queued for manual execution)

This task requires manual review and execution.

Instruction: {entry.get('instruction', '')}
"""

    # Output location and status
    body += f"""
## Output Location

Save output to: `{meeting_info['meeting_folder']}/zth_outputs/{entry.get('id', 'ZTH-000')}_{task_type}.md`

## Status Log

- [x] Worker generated: {now}
- [ ] Execution started: (pending)
- [ ] Execution completed: (pending)
- [ ] Output saved: (pending)
"""

    return frontmatter + body


def save_worker(content: str, meeting_folder: Path, zth_id: str, task_type: str) -> Path:
    """Save worker file to meeting folder."""
    workers_dir = meeting_folder / "workers"
    workers_dir.mkdir(exist_ok=True)
    
    filename = f"{zth_id}_{task_type}.md"
    worker_path = workers_dir / filename
    worker_path.write_text(content)
    
    return worker_path


def execute_list_add(entry: dict, meeting_folder: Path) -> dict:
    """Add item to a list in N5/lists/."""
    params = entry.get("additional_params", {})
    list_name = params.get("list_name", "ideas")
    item_summary = params.get("item_summary", entry.get("instruction", ""))
    
    # Normalize list name
    if not list_name.endswith(".jsonl"):
        list_name = f"{list_name}.jsonl"
    
    list_path = Path("/home/workspace/N5/lists") / list_name
    
    # Create list entry
    list_entry = {
        "id": f"ZTH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "added": datetime.now().isoformat(),
        "source": f"ZTH from {meeting_folder.name}",
        "summary": item_summary,
        "context": entry.get("context", ""),
        "status": "new"
    }
    
    # Append to list
    with open(list_path, "a") as f:
        f.write(json.dumps(list_entry) + "\n")
    
    return {
        "action": "executed",
        "result": f"Added to {list_name}",
        "list_path": str(list_path)
    }


def execute_deal_add(entry: dict, meeting_folder: Path) -> dict:
    """Add a new deal via deal system."""
    params = entry.get("additional_params", {})
    company = params.get("company", "Unknown")
    pipeline = params.get("pipeline", "careerspan")
    note = params.get("initial_note", entry.get("context", ""))
    
    # Call deal handler
    cmd = f'python3 /home/workspace/N5/scripts/sms_deal_handler.py --message "n5 deal add {company} {pipeline} {note}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return {
        "action": "executed",
        "result": result.stdout.strip() or "Deal add attempted",
        "company": company,
        "pipeline": pipeline
    }


def execute_deal_update(entry: dict, meeting_folder: Path) -> dict:
    """Update an existing deal."""
    params = entry.get("additional_params", {})
    company = params.get("company", "Unknown")
    update_note = params.get("update_note", entry.get("instruction", ""))
    
    cmd = f'python3 /home/workspace/N5/scripts/sms_deal_handler.py --message "n5 deal {company} {update_note}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return {
        "action": "executed",
        "result": result.stdout.strip() or "Deal update attempted",
        "company": company
    }


def execute_crm_contact(entry: dict, meeting_folder: Path) -> dict:
    """Add contact to CRM tracking."""
    params = entry.get("additional_params", {})
    person_name = params.get("person_name", "Unknown")
    role = params.get("role", "contact")
    company = params.get("company", "")
    context = params.get("context", entry.get("context", ""))
    
    # Add to must-contact list with role tag
    contact_entry = {
        "id": f"CRM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "added": datetime.now().isoformat(),
        "source": f"ZTH from {meeting_folder.name}",
        "name": person_name,
        "role": role,
        "company": company,
        "context": context,
        "status": "new"
    }
    
    list_path = Path("/home/workspace/N5/lists/must-contact.jsonl")
    with open(list_path, "a") as f:
        f.write(json.dumps(contact_entry) + "\n")
    
    return {
        "action": "executed",
        "result": f"Added {person_name} ({role}) to CRM tracking",
        "list_path": str(list_path)
    }


def execute_intro_lead(entry: dict, meeting_folder: Path) -> dict:
    """Track a warm intro opportunity via deal_proactive_sensor (database-native).
    
    DEPRECATED: No longer writes to intro-leads.jsonl.
    Routes through deal_proactive_sensor.py which:
    - Detects broker signals
    - Queues for V's approval via SMS
    - Creates deal_contacts entry on approval
    """
    params = entry.get("additional_params", {})
    source = params.get("source_person", "Unknown")
    target = params.get("target_person", "Unknown")
    target_company = params.get("target_company", "")
    target_role = params.get("target_role", "")
    context = params.get("context", entry.get("context", ""))
    
    # Construct text that deal_proactive_sensor can parse
    # Format: broker signal text that matches BROKER_PATTERNS
    signal_text = f"{source} can introduce me to {target}"
    if target_company:
        signal_text += f" at {target_company}"
    if target_role:
        signal_text += f" ({target_role})"
    if context:
        signal_text += f". Context: {context}"
    
    # Route through proactive sensor for proper DB handling + approval flow
    # Note: source is constrained to {meeting, email, sms, kondo}
    # Meeting folder name is embedded in signal_text context
    cmd = [
        "python3", "/home/workspace/N5/scripts/deal_proactive_sensor.py",
        "--text", signal_text,
        "--source", "meeting"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return {
            "action": "executed",
            "result": f"Routed to deal system: {source} → {target} at {target_company}",
            "detail": result.stdout.strip(),
            "routing": "deal_proactive_sensor"
        }
    else:
        return {
            "action": "error",
            "result": f"Failed to route intro lead: {result.stderr}",
            "fallback": "Manual review needed"
        }


def process_b00_entries(meeting_folder: Path, b00_path: Optional[str] = None, provenance: str = "zth_spawn_worker") -> list[dict]:
    """Process B00 entries and generate worker files or execute directly."""
    if b00_path is None:
        b00_path = meeting_folder / "B00_ZO_TAKE_HEED.jsonl"
    
    entries = load_b00_entries(b00_path)
    
    results = []
    for entry in entries:
        task_type = entry.get("task_type", "custom")
        exec_policy = entry.get("execution_policy", "queue")
        zth_id = entry.get("id", "ZTH-???")
        
        # Skip rejected entries
        if "REJECTED" in zth_id:
            results.append({
                "id": zth_id,
                "action": "skipped",
                "reason": entry.get("reason", "rejected")
            })
            continue
        
        # Skip directives (they're handled inline during block generation)
        if task_type == "directive":
            results.append({
                "id": zth_id,
                "task_type": task_type,
                "action": "skipped",
                "reason": "directive - handled inline"
            })
            continue
        
        # Direct execution for list/deal/CRM operations
        if task_type in DIRECT_EXECUTION_TYPES:
            try:
                if task_type == "list_add":
                    exec_result = execute_list_add(entry, meeting_folder)
                elif task_type == "deal_add":
                    exec_result = execute_deal_add(entry, meeting_folder)
                elif task_type == "deal_update":
                    exec_result = execute_deal_update(entry, meeting_folder)
                elif task_type == "crm_contact":
                    exec_result = execute_crm_contact(entry, meeting_folder)
                elif task_type == "intro_lead":
                    exec_result = execute_intro_lead(entry, meeting_folder)
                
                results.append({
                    "id": zth_id,
                    "task_type": task_type,
                    **exec_result
                })
            except Exception as e:
                results.append({
                    "id": zth_id,
                    "task_type": task_type,
                    "action": "error",
                    "error": str(e)
                })
            continue
        
        # Generate worker file for other types (blurb, follow_up_email, warm_intro, research, custom)
        # Skip directives (they're applied inline, not spawned)
        if entry.get("task_type") == "directive":
            results.append({
                "id": entry.get("id"),
                "task_type": "directive",
                "action": "skip",
                "reason": "Directives are applied inline, not spawned as workers"
            })
            continue
        
        # Generate and save worker
        content = generate_worker(entry, meeting_folder, provenance)
        worker_path = save_worker(
            content, 
            meeting_folder, 
            entry.get("id", "ZTH-000"),
            entry.get("task_type", "custom")
        )
        
        results.append({
            "id": entry.get("id"),
            "task_type": entry.get("task_type"),
            "execution_policy": entry.get("execution_policy"),
            "worker_path": str(worker_path),
            "action": "generated"
        })
    
    return results


def run_tests():
    """Run built-in tests."""
    print("Running ZTH spawn worker tests...\n")
    
    import tempfile
    import shutil
    
    # Create temp meeting folder
    tmp_dir = Path(tempfile.mkdtemp())
    meeting_folder = tmp_dir / "2026-01-19_Test-Meeting"
    meeting_folder.mkdir()
    
    # Create test B00 file
    b00_content = """{"id":"ZTH-001","timestamp":"mid","raw_cue":"Zo take heed, prep a follow-up email","instruction":"prep a follow-up email","task_type":"follow_up_email","execution_policy":"auto_execute","scope":["follow_up_email"],"context":"End of meeting"}
{"id":"ZTH-002","timestamp":"late","raw_cue":"Zo take heed, omit pricing","instruction":"omit pricing from recap","task_type":"directive","execution_policy":"inline","scope":["B01"],"context":"Pricing discussion"}
{"id":"ZTH-003","timestamp":"late","raw_cue":"Zo take heed, research their funding history","instruction":"research their funding history","task_type":"research","execution_policy":"queue","scope":["research"],"context":"Due diligence"}"""
    
    b00_path = meeting_folder / "B00_ZO_TAKE_HEED.jsonl"
    b00_path.write_text(b00_content)
    
    # Run processor
    results = process_b00_entries(meeting_folder, provenance="test")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Follow-up email worker generated
    email_result = next((r for r in results if r["id"] == "ZTH-001"), None)
    if email_result and email_result["action"] == "generated":
        worker_path = Path(email_result["worker_path"])
        if worker_path.exists() and "Follow-Up Email" in worker_path.read_text():
            print("  ✓ Follow-up email worker generated correctly")
            tests_passed += 1
        else:
            print("  ✗ Follow-up email worker content incorrect")
            tests_failed += 1
    else:
        print("  ✗ Follow-up email worker not generated")
        tests_failed += 1
    
    # Test 2: Directive skipped (not spawned)
    directive_result = next((r for r in results if r["id"] == "ZTH-002"), None)
    if directive_result and directive_result["action"] == "skipped":
        print("  ✓ Directive correctly skipped (not spawned)")
        tests_passed += 1
    else:
        print(f"  ✗ Directive should be skipped (got: {directive_result})")
        tests_failed += 1
    
    # Test 3: Research worker generated with queue policy
    research_result = next((r for r in results if r["id"] == "ZTH-003"), None)
    if research_result and research_result["action"] == "generated":
        worker_path = Path(research_result["worker_path"])
        content = worker_path.read_text()
        if "Research Request" in content and "queued for manual" in content:
            print("  ✓ Research worker generated with queue notice")
            tests_passed += 1
        else:
            print("  ✗ Research worker content incorrect")
            tests_failed += 1
    else:
        print("  ✗ Research worker not generated")
        tests_failed += 1
    
    # Test 4: Workers directory created
    workers_dir = meeting_folder / "workers"
    if workers_dir.exists() and workers_dir.is_dir():
        print("  ✓ Workers directory created")
        tests_passed += 1
    else:
        print("  ✗ Workers directory not created")
        tests_failed += 1
    
    # Cleanup
    shutil.rmtree(tmp_dir)
    
    print(f"\nResults: {tests_passed}/{tests_passed + tests_failed} tests passed")
    return tests_failed == 0


def main():
    parser = argparse.ArgumentParser(description="Generate ZTH worker files from B00 entries")
    parser.add_argument("--meeting-folder", type=Path, help="Path to meeting folder")
    parser.add_argument("--b00-file", type=Path, help="Path to B00 JSONL file (default: <meeting-folder>/B00_ZO_TAKE_HEED.jsonl)")
    parser.add_argument("--zth-id", type=str, help="Process only this ZTH ID")
    parser.add_argument("--provenance", type=str, default="zth_spawn_worker", help="Provenance string for tracking")
    parser.add_argument("--test", action="store_true", help="Run built-in tests")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    if not args.meeting_folder:
        parser.error("--meeting-folder is required")
    
    if not args.meeting_folder.exists():
        print(f"Error: Meeting folder not found: {args.meeting_folder}")
        sys.exit(1)
    
    results = process_b00_entries(
        args.meeting_folder,
        args.b00_file,
        args.zth_id,
        args.provenance
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No ZTH entries to process")
        else:
            print(f"Processed {len(results)} ZTH entries:")
            for r in results:
                if r["action"] == "generated":
                    print(f"  ✓ {r['id']}: {r['task_type']} ({r['execution_policy']}) → {r['worker_path']}")
                else:
                    print(f"  ○ {r['id']}: {r['task_type']} (skipped - {r.get('reason', 'N/A')})")


if __name__ == "__main__":
    main()
