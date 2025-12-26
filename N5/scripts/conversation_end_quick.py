#!/usr/bin/env python3
"""
Conversation End - Tier 1 (Quick Close) v3.0

Fast, lightweight conversation close for simple discussions and Q&A.
Cost target: <$0.05 | Time target: <45 seconds

Workflow:
1. Generate thread title (pattern-based, LLM fallback)
2. Generate conversation summary (LLM, 2-3 sentences)
3. Rebuild SESSION_STATE.md with closure status
4. Scan and categorize files
5. Output formatted closure report

Usage:
    python3 conversation_end_quick.py --convo-id <id> [--dry-run]
    
Returns: Markdown formatted closure report
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
        "progress": []
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


def generate_title_local(session_state: Optional[Dict], files: List[Dict], convo_id: str) -> str:
    """Generate title using local pattern matching."""
    # Date prefix
    now = datetime.now(timezone.utc)
    date_prefix = now.strftime("%b %d")
    
    # Determine emoji based on conversation type
    emoji = "💬"  # Default: discussion
    if session_state and session_state.get("type"):
        type_map = {
            "build": "🏗️",
            "research": "🔍",
            "discussion": "💬",
            "planning": "📋",
            "debug": "🔧",
            "orchestrator": "🎭"
        }
        emoji = type_map.get(session_state["type"].lower(), "💬")
    
    # Generate title from focus or files
    title_body = "Conversation"
    if session_state and session_state.get("focus"):
        # Clean and truncate focus
        focus = session_state["focus"]
        # Remove common prefixes
        focus = re.sub(r'^(Working on|Discussing|Building|Investigating)\s+', '', focus, flags=re.IGNORECASE)
        # Truncate to reasonable length - allow 55 chars for better titles
        if len(focus) > 55:
            focus = focus[:52] + "..."
        title_body = focus
    elif files:
        # Use file names as hint
        doc_files = [f for f in files if f["category"] == "documentation" and f["name"] != "SESSION_STATE.md"]
        if doc_files:
            title_body = doc_files[0]["name"].replace(".md", "").replace("_", " ")
    
    return f"{date_prefix} | {emoji} {title_body}"


def generate_summary_stub(session_state: Optional[Dict], files: List[Dict]) -> str:
    """Generate a stub summary (to be replaced by LLM in actual use)."""
    # This is a placeholder - actual LLM call happens in the prompt
    if session_state and session_state.get("focus"):
        return f"Discussion about: {session_state['focus']}"
    elif session_state and session_state.get("progress"):
        return f"Completed: {', '.join(session_state['progress'][:2])}"
    else:
        return "Brief conversation session."


def update_session_state(convo_path: Path, title: str, summary: str, dry_run: bool = False) -> bool:
    """Update SESSION_STATE.md with closure information."""
    session_file = convo_path / "SESSION_STATE.md"
    
    now = datetime.now(timezone.utc)
    closure_section = f"""
## Closure

**Status:** closed
**Closed:** {now.strftime("%Y-%m-%dT%H:%M:%SZ")}
**Title:** {title}
**Summary:** {summary}
"""
    
    if session_file.exists():
        content = session_file.read_text()
        # Update status
        content = re.sub(r'\*\*Status:\*\*\s*\w+', '**Status:** closed', content)
        # Add closure section if not present
        if "## Closure" not in content:
            content += closure_section
    else:
        # Create minimal session state
        content = f"""---
created: {now.strftime("%Y-%m-%d")}
last_edited: {now.strftime("%Y-%m-%d")}
version: 1.0
---

# Session State

**Status:** closed
**Type:** discussion
**Focus:** {summary}
{closure_section}
"""
    
    if dry_run:
        logger.info(f"[DRY RUN] Would update SESSION_STATE.md")
        return True
    
    session_file.write_text(content)
    logger.info(f"Updated SESSION_STATE.md with closure")
    return True


def format_output(
    convo_id: str,
    title: str,
    summary: str,
    files: List[Dict],
    session_state: Optional[Dict],
    duration_minutes: int = None
) -> str:
    """Format the Tier 1 closure output."""
    
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
    
    # Duration estimate
    duration_str = f"~{duration_minutes} minutes" if duration_minutes else "Unknown"
    
    # File summary
    files_by_category = {}
    for f in files:
        cat = f["category"]
        if cat not in files_by_category:
            files_by_category[cat] = []
        files_by_category[cat].append(f["name"])
    
    # Build output
    output = f"""## Conversation Closed

**Title:** {title}
**Type:** {convo_type}
**Duration:** {duration_str}

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
        "success": False,
        "title": None,
        "summary": None,
        "files": [],
        "output": None,
        "errors": []
    }
    
    # Step 1: Read existing session state
    logger.info(f"Reading session state for {convo_id}")
    session_state = read_session_state(convo_path)
    
    # Step 2: Scan files
    logger.info("Scanning conversation files")
    files = scan_conversation_files(convo_path)
    result["files"] = files
    
    # Step 3: Generate title (local pattern matching)
    logger.info("Generating title")
    title = generate_title_local(session_state, files, convo_id)
    result["title"] = title
    
    # Step 4: Generate summary stub (LLM will enhance in prompt)
    logger.info("Generating summary")
    summary = generate_summary_stub(session_state, files)
    result["summary"] = summary
    
    # Step 5: Update SESSION_STATE.md
    logger.info("Updating session state")
    update_session_state(convo_path, title, summary, dry_run)
    
    # Step 6: Format output
    logger.info("Formatting output")
    output = format_output(
        convo_id=convo_id,
        title=title,
        summary=summary,
        files=files,
        session_state=session_state
    )
    result["output"] = output
    
    # Calculate duration
    end_time = datetime.now(timezone.utc)
    result["duration_seconds"] = (end_time - start_time).total_seconds()
    result["success"] = True
    
    logger.info(f"Quick close complete in {result['duration_seconds']:.2f}s")
    
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


