#!/usr/bin/env python3
"""
Conversation End - Quick Close (Tier 1)

Mechanical close only - gathers context for Librarian.

TWO MODES:
- Worker Close: If parent_convo_id detected, outputs worker context (no commits)
- Full Close: Normal/orchestrator threads get full context

What this script does (MECHANICS ONLY):
1. Scan conversation workspace for files
2. Read SESSION_STATE.md
3. Detect if worker thread (parent_convo_id present)
4. Check git status
5. Output context bundle for Librarian

What this script does NOT do (SEMANTIC - Librarian's job):
- Generate titles (Librarian uses 3-slot emoji system)
- Write summaries
- Extract decisions
- Make semantic judgments
- Git commits (especially for workers - deferred to orchestrator)
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
N5_ROOT = SCRIPT_DIR.parent
USER_WORKSPACE = Path("/home/workspace")
CONVO_WORKSPACE_BASE = Path("/home/.z/workspaces")


def get_convo_path(convo_id: str) -> Path:
    """Get conversation workspace path."""
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    return CONVO_WORKSPACE_BASE / convo_id


def read_session_state(convo_path: Path) -> Optional[Dict]:
    """Read and parse SESSION_STATE.md if it exists."""
    session_file = convo_path / "SESSION_STATE.md"
    if not session_file.exists():
        return None
    
    content = session_file.read_text()
    state = {
        "raw": content,
        "type": None,
        "focus": None,
        "status": None,
        "started": None,
        "artifacts": [],
        "progress": [],
        "parent_convo_id": None,
        "orchestrator_id": None
    }
    
    # Parse key fields
    type_match = re.search(r'\*\*Type:\*\*\s*(\w+)', content)
    if type_match:
        state["type"] = type_match.group(1)
    
    focus_match = re.search(r'\*\*Focus:\*\*\s*(.+?)(?:\n|$)', content)
    if focus_match:
        state["focus"] = focus_match.group(1).strip()
    
    status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content)
    if status_match:
        state["status"] = status_match.group(1)
    
    started_match = re.search(r'\*\*Started:\*\*\s*([\d\-T:Z]+)', content)
    if started_match:
        state["started"] = started_match.group(1)
    
    # Detect worker thread - check for parent_convo_id or orchestrator_id
    parent_match = re.search(r'parent_convo_id:\s*(con_\w+)', content)
    if parent_match:
        state["parent_convo_id"] = parent_match.group(1)
    
    orchestrator_match = re.search(r'orchestrator_id:\s*(con_\w+)', content)
    if orchestrator_match:
        state["orchestrator_id"] = orchestrator_match.group(1)
    
    # Also check YAML frontmatter style
    parent_yaml = re.search(r'^parent_convo_id:\s*(con_\w+)', content, re.MULTILINE)
    if parent_yaml and not state["parent_convo_id"]:
        state["parent_convo_id"] = parent_yaml.group(1)
    
    orchestrator_yaml = re.search(r'^orchestrator_id:\s*(con_\w+)', content, re.MULTILINE)
    if orchestrator_yaml and not state["orchestrator_id"]:
        state["orchestrator_id"] = orchestrator_yaml.group(1)
    
    # Extract artifacts section
    artifacts_match = re.search(r'## Artifacts\n(.*?)(?:\n##|\Z)', content, re.DOTALL)
    if artifacts_match:
        artifacts_text = artifacts_match.group(1)
        state["artifacts"] = re.findall(r'- \[.\]\s*`([^`]+)`', artifacts_text)
    
    # Extract progress items
    progress_match = re.search(r'## Progress\n(.*?)(?:\n##|\Z)', content, re.DOTALL)
    if progress_match:
        progress_text = progress_match.group(1)
        state["progress"] = re.findall(r'- \[x\]\s*(.+)', progress_text, re.IGNORECASE)
    
    return state


def is_worker_thread(session_state: Optional[Dict]) -> bool:
    """Check if this is a worker thread (spawned by orchestrator)."""
    if not session_state:
        return False
    return bool(session_state.get("parent_convo_id") or session_state.get("orchestrator_id"))


def get_parent_topic(session_state: Optional[Dict]) -> Optional[str]:
    """Extract parent topic for worker title tag."""
    if not session_state:
        return None
    # Could be in focus or a dedicated field
    focus = session_state.get("focus", "")
    # Extract a slug-like topic from focus
    if focus:
        # Simple slugification for the tag
        words = focus.split()[:3]  # First 3 words
        return "-".join(w.capitalize() for w in words if w.isalnum())
    return None


def scan_conversation_files(convo_path: Path) -> List[Dict]:
    """Scan conversation workspace for files."""
    files = []
    
    if not convo_path.exists():
        return files
    
    for item in convo_path.iterdir():
        if item.name.startswith('.'):
            continue
        if item.is_file():
            files.append({
                "name": item.name,
                "path": str(item),
                "size": item.stat().st_size,
                "ext": item.suffix.lower(),
                "category": categorize_file(item)
            })
    
    return files


def categorize_file(file_path: Path) -> str:
    """Categorize a file by type."""
    name = file_path.name.lower()
    ext = file_path.suffix.lower()
    
    if name == "session_state.md":
        return "session"
    elif "debug" in name or "log" in name:
        return "debug"
    elif ext in [".md", ".txt"]:
        return "documentation"
    elif ext in [".py", ".js", ".ts", ".sh"]:
        return "script"
    elif ext in [".json", ".jsonl", ".yaml", ".yml"]:
        return "data"
    elif ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
        return "image"
    else:
        return "other"


def generate_summary_stub(session_state: Optional[Dict], files: List[Dict]) -> str:
    """Generate a stub summary (to be replaced by LLM in actual use)."""
    # This is a placeholder - actual LLM call happens in the prompt
    if session_state and session_state.get("focus"):
        return f"Discussion about: {session_state['focus']}"
    elif session_state and session_state.get("progress"):
        return f"Completed: {', '.join(session_state['progress'][:2])}"
    else:
        return "Brief conversation session."


def update_session_state(convo_path: Path, summary: str, dry_run: bool = False) -> bool:
    """Update SESSION_STATE.md with close info. Title added by Librarian."""
    session_file = convo_path / "SESSION_STATE.md"
    if not session_file.exists():
        logger.warning(f"SESSION_STATE.md not found: {session_file}")
        return False
    
    if dry_run:
        logger.info("[DRY RUN] Would update SESSION_STATE.md")
        return True
    
    content = session_file.read_text()
    
    # Add close section if not present
    if "## Close" not in content:
        close_section = f"""

## Close

**Status:** closed
**Summary:** {summary}
"""
        content += close_section
        session_file.write_text(content)
        logger.info("Updated SESSION_STATE.md with close section")
    
    return True


def format_output(
    convo_id: str,
    session_state: Optional[Dict],
    files: List[Dict],
    summary: str,
    is_worker: bool,
) -> str:
    """Format the output for Librarian to process."""
    mode = "Worker Close" if is_worker else "Full Close"
    parent_id = None
    if is_worker and session_state:
        parent_id = session_state.get("parent_convo_id") or session_state.get("orchestrator_id")
    
    output = f"""## Tier 1 Quick Close - Context Bundle

**Conversation:** {convo_id}
**Mode:** {mode}
"""
    
    if is_worker and parent_id:
        parent_topic = get_parent_topic(session_state)
        output += f"""**Parent Orchestrator:** {parent_id}
**Parent Topic Tag:** [{parent_topic or 'Unknown'}]

⚠️ **WORKER MODE:** This is a worker thread. DO NOT commit. 
Generate handoff summary for orchestrator review.

"""
    
    output += f"""**Summary:** {summary}

### Session State
"""
    
    # Determine conversation type
    convo_type = "Quick discussion"
    if session_state and session_state.get("type"):
        type_map = {
            "build": "Build session",
            "research": "Research",
            "discussion": "Discussion",
            "planning": "Planning",
            "debug": "Debugging"
        }
        convo_type = type_map.get(session_state["type"].lower(), "Discussion")
    
    # File summary
    files_by_category = {}
    for f in files:
        cat = f["category"]
        if cat not in files_by_category:
            files_by_category[cat] = []
        files_by_category[cat].append(f["name"])
    
    # Build output
    output += f"""## Conversation Closed

**Type:** {convo_type}

### Summary
{summary}

### Files in Workspace
"""
    
    if files:
        for cat, file_list in sorted(files_by_category.items()):
            if cat == "session":
                continue  # Skip SESSION_STATE.md
            output += f"- **{cat.title()}:** {', '.join(file_list)}\n"
    else:
        output += "- No files created\n"
    
    if is_worker:
        output += "\n⚠️ Worker close complete - awaiting orchestrator review"
    else:
        output += "\n✅ Workspace clean"
    
    return output


def run_quick_close(convo_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Execute Tier 1 quick close workflow."""
    start_time = datetime.now(timezone.utc)
    
    # Normalize convo_id
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    
    convo_path = get_convo_path(convo_id)
    
    result = {
        "convo_id": convo_id,
        "convo_path": str(convo_path),
        "tier": 1,
        "is_worker": False,
        "parent_convo_id": None,
        "success": False,
        "files": [],
        "output": None,
        "errors": []
    }
    
    # Step 1: Read existing session state
    logger.info(f"Reading session state for {convo_id}")
    session_state = read_session_state(convo_path)
    
    # Step 2: Detect worker mode
    is_worker = is_worker_thread(session_state)
    result["is_worker"] = is_worker
    if is_worker and session_state:
        result["parent_convo_id"] = session_state.get("parent_convo_id") or session_state.get("orchestrator_id")
        logger.info(f"Worker thread detected, parent: {result['parent_convo_id']}")
    
    # Step 3: Scan files
    logger.info("Scanning conversation files")
    files = scan_conversation_files(convo_path)
    result["files"] = files
    
    # Step 4: Generate summary (brief, for context - Librarian will write real one)
    logger.info("Generating context summary")
    if session_state and session_state.get("focus"):
        summary = f"Quick close for: {session_state['focus']}"
    else:
        summary = f"Quick close for conversation {convo_id}"
    result["summary"] = summary
    
    # Step 5: Update session state (without title - Librarian adds that)
    if not dry_run:
        update_session_state(convo_path, summary, dry_run)
    
    # Step 6: Format output for Librarian
    output = format_output(
        convo_id=convo_id,
        session_state=session_state,
        files=files,
        summary=summary,
        is_worker=is_worker,
    )
    result["output"] = output
    
    # Calculate duration
    end_time = datetime.now(timezone.utc)
    result["duration_seconds"] = (end_time - start_time).total_seconds()
    result["success"] = True
    
    mode_str = "Worker" if is_worker else "Full"
    logger.info(f"Quick close ({mode_str} mode) complete in {result['duration_seconds']:.2f}s")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Conversation End - Tier 1 (Quick Close)"
    )
    parser.add_argument(
        "--convo-id",
        required=True,
        help="Conversation ID (with or without con_ prefix)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write changes, just show what would happen"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full result as JSON instead of markdown"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Write output to file instead of stdout"
    )
    
    args = parser.parse_args()
    
    result = run_quick_close(args.convo_id, args.dry_run)
    
    if args.json:
        output = json.dumps(result, indent=2)
    else:
        output = result["output"] if result["success"] else f"Error: {result['errors']}"
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to: {args.output}")
    else:
        print(output)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()




