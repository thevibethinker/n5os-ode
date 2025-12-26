#!/usr/bin/env python3
"""
Spawn Worker v2 - LLM-First Design

The LLM provides all semantic context. This script handles:
1. Generate timestamp/ID
2. Write worker assignment from LLM-provided context
3. Update parent SESSION_STATE with worker reference
4. Create worker_updates/ directory

Can also fall back to SESSION_STATE parsing if no context provided.

Usage:
    # Generate IDs only (for LLM to use)
    python3 spawn_worker.py --generate-ids --parent con_XXX
    
    # Full spawn with LLM-provided context (JSON)
    python3 spawn_worker.py --parent con_XXX --context '{...}'
    
    # Legacy mode: parse SESSION_STATE (when no --context provided)
    python3 spawn_worker.py --parent con_XXX --instruction "Do X"
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
WORKSPACES_ROOT = Path("/home/.z/workspaces")
OUTPUT_DIR = WORKSPACE / "Records" / "Temporary"

VERSION = "2.0"


def generate_ids(parent_id: str) -> dict:
    """Generate worker ID and timestamp."""
    now = datetime.now(timezone.utc)
    suffix = parent_id[-4:] if len(parent_id) >= 4 else parent_id
    worker_id = f"WORKER_{suffix}_{now.strftime('%Y%m%d_%H%M%S')}"
    timestamp = now.isoformat()
    filename = f"WORKER_ASSIGNMENT_{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond:06d}_{suffix}.md"
    
    return {
        "worker_id": worker_id,
        "timestamp": timestamp,
        "filename": filename,
        "output_path": str(OUTPUT_DIR / filename),
        "parent_workspace": str(WORKSPACES_ROOT / parent_id),
        "worker_updates_dir": str(WORKSPACES_ROOT / parent_id / "worker_updates"),
    }


def update_parent_session_state(parent_id: str, worker_filename: str, timestamp: str) -> bool:
    """Add worker reference to parent's SESSION_STATE.md"""
    session_path = WORKSPACES_ROOT / parent_id / "SESSION_STATE.md"
    
    if not session_path.exists():
        logger.warning("No parent SESSION_STATE.md found")
        return False
    
    content = session_path.read_text()
    
    # Add to Spawned Workers section
    worker_entry = f"- {worker_filename} (spawned {timestamp[:16].replace('T', ' ')} UTC)"
    
    if "## Spawned Workers" in content:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("## Spawned Workers"):
                lines.insert(i + 2, worker_entry)
                break
        content = "\n".join(lines)
    else:
        content += f"\n\n## Spawned Workers\n\n{worker_entry}\n"
    
    session_path.write_text(content)
    logger.info(f"✓ Updated parent SESSION_STATE: {worker_entry}")
    return True


def create_worker_updates_dir(parent_id: str) -> Path:
    """Create worker_updates directory in parent workspace."""
    updates_dir = WORKSPACES_ROOT / parent_id / "worker_updates"
    updates_dir.mkdir(exist_ok=True)
    logger.info(f"✓ Created/verified worker_updates dir: {updates_dir}")
    return updates_dir


# === SESSION_STATE Parsing (Legacy/Fallback) ===

def _clean_value(val: str) -> str:
    """Clean markdown artifacts from extracted values."""
    val = val.strip()
    val = re.sub(r"^\*+\s*", "", val)
    val = re.sub(r"\s*\*+$", "", val)
    val = val.strip('"\'')
    return val.strip()


def _is_placeholder(val: str) -> bool:
    """Check if value is a placeholder/default."""
    if not val:
        return True
    val_lower = val.lower().strip()
    placeholders = ["tbd", "not specified", "n/a", "none", "unknown", "placeholder"]
    return val_lower in placeholders or val_lower.startswith("what ")


def _extract_field_multi(content: str, field_names: List[str]) -> str:
    """Try multiple field names, return first non-placeholder match."""
    for field in field_names:
        pattern = rf"^[-*]*\s*\*\*{re.escape(field)}:\*\*\s*(.+)$"
        for line in content.split("\n"):
            m = re.match(pattern, line.strip(), re.IGNORECASE)
            if m:
                val = _clean_value(m.group(1))
                if not _is_placeholder(val):
                    return val
    return ""


def _extract_progress(content: str) -> str:
    """Extract Progress field - often has the richest context."""
    patterns = [
        r"^[-*]*\s*\*\*Progress:\*\*\s*(.+)$",
        r"^[-*]*\s*Progress:\s*(.+)$",
    ]
    for pattern in patterns:
        for line in content.split("\n"):
            m = re.match(pattern, line.strip(), re.IGNORECASE)
            if m:
                val = _clean_value(m.group(1))
                if not _is_placeholder(val) and len(val) > 5:
                    return val
    return ""


def parse_session_state(parent_id: str) -> Dict[str, str]:
    """Parse parent SESSION_STATE.md for context (legacy/fallback mode)."""
    session_path = WORKSPACES_ROOT / parent_id / "SESSION_STATE.md"
    
    result = {
        "parent_focus": "",
        "parent_objective": "",
        "parent_status": "",
        "parent_type": "",
        "progress": "",
    }
    
    if not session_path.exists():
        return result
    
    try:
        content = session_path.read_text()
        
        # Try Progress field first - often has best info
        result["progress"] = _extract_progress(content)
        
        # Multi-source extraction
        result["parent_focus"] = _extract_field_multi(
            content, ["Focus", "Working On", "Current Focus", "Topic", "Subject"]
        )
        result["parent_objective"] = _extract_field_multi(
            content, ["Goal", "Objective", "Purpose", "Target", "Outcome"]
        )
        result["parent_status"] = _extract_field_multi(
            content, ["Status", "State", "Phase", "Current Phase"]
        )
        result["parent_type"] = _extract_field_multi(
            content, ["Type", "Primary Type", "Conversation Type", "Mode"]
        )
        
        # If focus is empty but progress has content, use progress
        if not result["parent_focus"] and result["progress"]:
            result["parent_focus"] = f"[From Progress] {result['progress']}"
        
        logger.info(f"Parsed SESSION_STATE: type={result['parent_type']}, has_progress={bool(result['progress'])}")
        
    except Exception as e:
        logger.warning(f"Error parsing SESSION_STATE: {e}")
    
    return result


def gather_recent_artifacts(parent_id: str, max_count: int = 10) -> List[Dict]:
    """Gather list of recent artifacts from parent workspace."""
    parent_ws = WORKSPACES_ROOT / parent_id
    
    if not parent_ws.exists():
        return []
    
    exclude_patterns = {"__pycache__", ".git", ".pyc", "worker_updates", "SESSION_STATE"}
    
    try:
        all_files = []
        for item in parent_ws.rglob("*"):
            if item.is_file():
                if any(excl in str(item) for excl in exclude_patterns):
                    continue
                all_files.append((item, item.stat().st_mtime))
        
        recent_files = sorted(all_files, key=lambda x: x[1], reverse=True)[:max_count]
        
        return [
            {
                "path": str(f[0].relative_to(parent_ws)),
                "size": f[0].stat().st_size,
                "modified": datetime.fromtimestamp(f[1], timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            }
            for f in recent_files
        ]
    except Exception as e:
        logger.warning(f"Could not gather artifacts: {e}")
        return []


# === Worker Assignment Generation ===

def create_worker_assignment(ids: dict, context: dict, instruction: str = None) -> str:
    """Create worker assignment markdown from context."""
    
    # Get fields from context
    parent_focus = context.get("parent_focus", "") or "_Not specified_"
    parent_objective = context.get("parent_objective", "") or "_Not specified_"
    parent_status = context.get("parent_status", "") or "_Not specified_"
    parent_type = context.get("parent_type", "") or "_Not specified_"
    
    # Build status line
    if parent_status and parent_type:
        status_line = f"{parent_status} ({parent_type})"
    else:
        status_line = parent_status or parent_type or "_Not specified_"
    
    # Get instruction
    task_instruction = instruction or context.get("instruction", "No specific instruction provided - work in parallel on related tasks")
    
    # Optional enrichments
    key_decisions = context.get("key_decisions", [])
    relevant_files = context.get("relevant_files", [])
    additional_context = context.get("additional_context", "")
    recent_artifacts = context.get("recent_artifacts", [])
    
    # Build markdown
    md = f"""# Worker Assignment - Parallel Thread

**Generated:** {ids['timestamp']}  
**Parent Conversation:** {context.get('parent_id', ids.get('parent_id', 'unknown'))}  
**Worker ID:** {ids['worker_id']}

---

## Your Mission

{task_instruction}

Focus on implementation with proper testing, error handling, and documentation.

---

## Parent Context

**What parent is working on:**  
{parent_focus}

**Parent objective:**  
{parent_objective}

**Parent status:**  
{status_line}

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

    # Recent artifacts section
    md += "\n---\n\n## Recent Activity in Parent Thread\n\n"
    
    if recent_artifacts:
        md += "**Recently generated files:**\n\n"
        for artifact in recent_artifacts[:10]:
            path = artifact.get('path', 'unknown')
            size = artifact.get('size', 0)
            modified = artifact.get('modified', '')
            
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f}KB"
            else:
                size_str = f"{size/(1024*1024):.1f}MB"
            
            md += f"- `{path}` ({size_str}, modified {modified})\n"
    else:
        md += "*No recent artifacts available*\n"

    md += f"""
---

## Instructions for This Worker Thread

1. **Initialize your own session state:**
   ```bash
   python3 /home/workspace/N5/scripts/session_state_manager.py init \\
       --convo-id <YOUR_CONVERSATION_ID> \\
       --load-system
   ```

2. **Link back to parent:**
   ```bash
   python3 /home/workspace/N5/scripts/session_state_manager.py link-parent \\
       --parent {context.get('parent_id', ids.get('parent_id', 'PARENT_ID'))}
   ```

3. **Write status updates to parent workspace:**
   - Location: `{ids['worker_updates_dir']}/WORKER_<YOUR_ID>_status.md`
   - Format: Brief status, what you're working on, blockers if any
   - Frequency: At natural checkpoints (milestones, completions, errors)

4. **Report test results:**
   - Create: `{ids['worker_updates_dir']}/WORKER_<YOUR_ID>_test_results.json`
   - Format: JSON with `{{"tests_run": N, "passed": N, "failed": N, "details": [...]}}`
   - When: Immediately after running test suite

5. **Dump completion report:**
   - Create: `{ids['worker_updates_dir']}/WORKER_<YOUR_ID>_completion.md`
   - Format: Full summary, what was built, test results, lessons learned
   - When: When work is 100% complete

6. **Store generated artifacts:**
   - Directory: `{ids['worker_updates_dir']}/WORKER_<YOUR_ID>_artifacts`
   - Structure: Organize by type (code, docs, data, etc.)
   - Include: All files you generate (scripts, configs, documents, etc.)

7. **Work independently:**
   - You're running in parallel, not sequentially
   - Parent may or may not be actively working
   - Coordinate through workspace writes, not direct communication

---

## Communication Protocol

**You → Parent:** Write status updates to parent's workspace (path above)  
**Parent → You:** Parent may update your assignment or provide input via your workspace

**Both of you know about each other** through SESSION_STATE linkage.

---

**Ready to work in parallel!**

*Generated by spawn_worker.py v{VERSION}*
"""
    
    return md


def main():
    parser = argparse.ArgumentParser(description=f"Spawn Worker v{VERSION} - LLM-First Design")
    parser.add_argument("--parent", required=True, help="Parent conversation ID (e.g., con_ABC123)")
    parser.add_argument("--generate-ids", action="store_true", help="Only generate IDs, output JSON")
    parser.add_argument("--context", help="Inline JSON context from LLM")
    parser.add_argument("--context-file", type=Path, help="Path to JSON context file")
    parser.add_argument("--instruction", help="Task instruction (legacy mode)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    args = parser.parse_args()
    
    # Generate IDs
    ids = generate_ids(args.parent)
    ids['parent_id'] = args.parent
    
    # ID-only mode
    if args.generate_ids:
        print(json.dumps(ids, indent=2))
        return 0
    
    # Get context - prefer LLM-provided, fall back to SESSION_STATE parsing
    context = {}
    
    if args.context:
        try:
            context = json.loads(args.context)
            logger.info(f"Using LLM-provided context with {len(context)} fields")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in --context: {e}")
            return 1
    elif args.context_file:
        try:
            context = json.loads(args.context_file.read_text())
            logger.info(f"Using context from file: {args.context_file}")
        except Exception as e:
            logger.error(f"Failed to read context file: {e}")
            return 1
    else:
        # Legacy mode: parse SESSION_STATE
        logger.info("No --context provided, parsing SESSION_STATE (legacy mode)")
        context = parse_session_state(args.parent)
        context['recent_artifacts'] = gather_recent_artifacts(args.parent)
    
    context['parent_id'] = args.parent
    
    # Create assignment
    assignment = create_worker_assignment(ids, context, instruction=args.instruction)
    
    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Would write to: {ids['output_path']}")
        print("--- Content Preview ---")
        print(assignment[:1500])
        print("...")
        return 0
    
    # Write file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(ids['output_path'])
    output_path.write_text(assignment)
    logger.info(f"✓ Worker assignment created: {output_path}")
    
    # Update parent SESSION_STATE
    update_parent_session_state(args.parent, ids['filename'], ids['timestamp'])
    
    # Create worker_updates directory
    create_worker_updates_dir(args.parent)
    
    # Output for LLM to use
    result = {
        "success": True,
        "worker_id": ids['worker_id'],
        "output_path": str(output_path),
        "relative_path": f"Records/Temporary/{ids['filename']}",
        "worker_updates_dir": ids['worker_updates_dir'],
    }
    print(json.dumps(result, indent=2))
    
    logger.info(f"\n✓ Worker spawned successfully!")
    logger.info(f"📄 Open this file in a new conversation: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

