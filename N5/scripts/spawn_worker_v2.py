#!/usr/bin/env python3
"""
Spawn Worker v2 - LLM-First Design

The LLM provides all semantic context. This script only handles:
1. Generate timestamp/ID
2. Write worker assignment from LLM-provided content
3. Update parent SESSION_STATE with worker reference
4. Create worker_updates/ directory

Usage:
    # Generate IDs only (for LLM to use)
    python3 spawn_worker_v2.py --generate-ids --parent con_XXX
    
    # Full spawn with LLM-provided context (JSON)
    python3 spawn_worker_v2.py --parent con_XXX --context-file /path/to/context.json
    
    # Full spawn with inline JSON
    python3 spawn_worker_v2.py --parent con_XXX --context '{...}'
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/workspace")
WORKSPACES_ROOT = Path("/home/.z/workspaces")
OUTPUT_DIR = WORKSPACE / "Records" / "Temporary"


def generate_ids(parent_id: str) -> dict:
    """Generate worker ID and timestamp."""
    now = datetime.now(timezone.utc)
    suffix = parent_id[-4:] if len(parent_id) >= 4 else parent_id
    worker_id = f"WORKER_{suffix}_{now.strftime('%Y%m%d_%H%M%S_%f')}"
    timestamp = now.isoformat()
    filename = f"WORKER_ASSIGNMENT_{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond:06d}_{suffix}.md"
    
    return {
        "worker_id": worker_id,
        "timestamp": timestamp,
        "filename": filename,
        "output_path": str(OUTPUT_DIR / filename),
        "parent_workspace": str(WORKSPACES_ROOT / parent_id),
    }


def update_parent_session_state(parent_id: str, worker_filename: str, timestamp: str):
    """Add worker reference to parent's SESSION_STATE.md"""
    session_path = WORKSPACES_ROOT / parent_id / "SESSION_STATE.md"
    
    if not session_path.exists():
        return False
    
    content = session_path.read_text()
    
    # Add to Spawned Workers section
    worker_entry = f"\n- {worker_filename} (spawned {timestamp[:16].replace('T', ' ')} UTC)"
    
    if "## Spawned Workers" in content:
        content = content.replace(
            "## Spawned Workers\n",
            f"## Spawned Workers\n{worker_entry}"
        )
    else:
        content += f"\n\n## Spawned Workers\n{worker_entry}\n"
    
    session_path.write_text(content)
    return True


def create_worker_updates_dir(parent_id: str) -> Path:
    """Create worker_updates directory in parent workspace."""
    updates_dir = WORKSPACES_ROOT / parent_id / "worker_updates"
    updates_dir.mkdir(exist_ok=True)
    return updates_dir


def create_worker_assignment(ids: dict, context: dict) -> str:
    """Create worker assignment markdown from LLM-provided context."""
    
    # Required fields
    instruction = context.get("instruction", "No instruction provided - define your task")
    parent_focus = context.get("parent_focus", "Not specified")
    parent_objective = context.get("parent_objective", "Not specified")
    parent_status = context.get("parent_status", "Not specified")
    parent_type = context.get("parent_type", "Not specified")
    
    # Optional enrichments
    key_decisions = context.get("key_decisions", [])
    relevant_files = context.get("relevant_files", [])
    additional_context = context.get("additional_context", "")
    
    # Build markdown
    md = f"""# Worker Assignment - Parallel Thread

**Generated:** {ids['timestamp']}  
**Parent Conversation:** {context.get('parent_id', 'unknown')}  
**Worker ID:** {ids['worker_id']}

---

## Your Mission

{instruction}

---

## Parent Context

**What parent is working on:**  
{parent_focus}

**Parent objective:**  
{parent_objective}

**Parent status:**  
{parent_status}

**Parent conversation type:**  
{parent_type}
"""

    if key_decisions:
        md += "\n**Key decisions already made:**\n"
        for decision in key_decisions:
            md += f"- {decision}\n"

    if relevant_files:
        md += "\n**Relevant files:**\n"
        for f in relevant_files:
            md += f"- `{f}`\n"

    if additional_context:
        md += f"\n**Additional context:**\n{additional_context}\n"

    md += f"""
---

## Your Workspace

**Worker updates directory:** `{ids['parent_workspace']}/worker_updates/`

When you complete work or have updates:
1. Write status to `worker_updates/{ids['worker_id']}_STATUS.md`
2. Place artifacts in the user workspace as appropriate

---

## Communication Protocol

**To update parent:**
- Write to `worker_updates/{ids['worker_id']}_STATUS.md`
- Format: Summary, artifacts created, blockers, next steps

**To request input:**
- Write to `worker_updates/{ids['worker_id']}_BLOCKED.md`
- Parent will check and respond

**On completion:**
- Write `worker_updates/{ids['worker_id']}_COMPLETE.md`
- List all artifacts and summary

---

## Important Notes

- You are a **parallel thread**, not a sub-agent
- Work independently using your best judgment
- Ask clarifying questions only if truly blocked
- Parent may or may not check updates during your work
- Optimize for async communication

---

**Ready to work in parallel!**
"""
    
    return md


def main():
    parser = argparse.ArgumentParser(description="Spawn Worker v2 - LLM-First")
    parser.add_argument("--parent", required=True, help="Parent conversation ID")
    parser.add_argument("--generate-ids", action="store_true", help="Only generate IDs, output JSON")
    parser.add_argument("--context", help="Inline JSON context from LLM")
    parser.add_argument("--context-file", help="Path to JSON context file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    args = parser.parse_args()
    
    # Generate IDs
    ids = generate_ids(args.parent)
    
    # ID-only mode
    if args.generate_ids:
        print(json.dumps(ids, indent=2))
        return 0
    
    # Get context
    if args.context:
        context = json.loads(args.context)
    elif args.context_file:
        context = json.loads(Path(args.context_file).read_text())
    else:
        # Minimal context - LLM should provide more
        context = {"instruction": "Task not specified - define your mission"}
    
    context["parent_id"] = args.parent
    
    # Create assignment
    assignment = create_worker_assignment(ids, context)
    
    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Would write to: {ids['output_path']}")
        print("--- Content ---")
        print(assignment)
        return 0
    
    # Write file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(ids['output_path'])
    output_path.write_text(assignment)
    
    # Update parent
    update_parent_session_state(args.parent, ids['filename'], ids['timestamp'])
    create_worker_updates_dir(args.parent)
    
    # Output for LLM to use
    result = {
        "success": True,
        "worker_id": ids['worker_id'],
        "output_path": str(output_path),
        "relative_path": f"Records/Temporary/{ids['filename']}",
        "worker_updates_dir": f"{ids['parent_workspace']}/worker_updates/",
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())


