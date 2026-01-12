#!/usr/bin/env python3
"""
Conversation End - Tier 2 (Standard Close) v4.0

Gathers context for research, substantial discussions, and 
sessions with multiple artifacts.

SEMANTIC ANALYSIS IS OWNED BY LIBRARIAN (LLM), NOT THIS SCRIPT.

This script provides:
- File organization with move recommendations
- Git status integration
- Raw content for LLM analysis

The LLM (Librarian) then:
- Extracts decisions through semantic understanding
- Identifies open items through reasoning
- Writes meaningful summaries

Cost target: <$0.08 | Time target: <90 seconds

Usage:
    python3 conversation_end_standard.py --convo-id <id> [--dry-run]
    
Returns: Markdown formatted closure report with context for LLM
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

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

# Import Tier 1 functions
from conversation_end_quick import (
    get_convo_path,
    read_session_state,
    scan_conversation_files,
    categorize_file,
    generate_title_local,
    update_session_state
)

# File destination recommendations
DESTINATION_MAP = {
    "documentation": "Documents/",
    "script": "N5/scripts/" if "n5" in str(SCRIPT_DIR).lower() else "Scripts/",
    "data": "N5/data/",
    "image": "Images/",
    "debug": None,  # Keep in place or delete
    "session": None,  # Don't move
    "other": "Inbox/"
}


def get_git_status() -> Dict[str, Any]:
    """Get git status for user workspace."""
    result = {
        "has_changes": False,
        "file_count": 0,
        "staged": 0,
        "unstaged": 0,
        "untracked": 0,
        "summary": "Clean"
    }
    
    try:
        # Get porcelain status
        proc = subprocess.run(
            ["git", "-C", str(USER_WORKSPACE), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if proc.returncode == 0:
            lines = [l for l in proc.stdout.strip().split('\n') if l]
            result["file_count"] = len(lines)
            result["has_changes"] = len(lines) > 0
            
            for line in lines:
                if line.startswith('??'):
                    result["untracked"] += 1
                elif line[0] != ' ':
                    result["staged"] += 1
                elif line[1] != ' ':
                    result["unstaged"] += 1
            
            if result["has_changes"]:
                parts = []
                if result["staged"]:
                    parts.append(f"{result['staged']} staged")
                if result["unstaged"]:
                    parts.append(f"{result['unstaged']} modified")
                if result["untracked"]:
                    parts.append(f"{result['untracked']} untracked")
                result["summary"] = f"{result['file_count']} changes ({', '.join(parts)})"
            
    except subprocess.TimeoutExpired:
        result["summary"] = "Git status timed out"
    except Exception as e:
        result["summary"] = f"Git error: {e}"
    
    return result


def recommend_file_destinations(files: List[Dict]) -> List[Dict]:
    """Add move recommendations to files."""
    for f in files:
        category = f.get("category", "other")
        destination = DESTINATION_MAP.get(category)
        
        if destination:
            f["recommended_destination"] = destination
            f["action"] = "move"
        elif category == "debug":
            f["recommended_destination"] = None
            f["action"] = "review"  # User decides: keep or delete
        else:
            f["recommended_destination"] = None
            f["action"] = "keep"
    
    return files


def gather_conversation_content(convo_path: Path) -> Dict[str, Any]:
    """
    Gather raw conversation content for LLM analysis.
    
    NO REGEX EXTRACTION - just raw content.
    The LLM will do semantic analysis.
    """
    content_data = {
        "key_files": [],
        "total_content_size": 0,
        "raw_content_samples": {},  # filename -> content preview
    }
    
    # Scan all readable files
    for item in convo_path.iterdir():
        if item.is_file() and item.suffix in ['.md', '.txt', '.json']:
            try:
                content = item.read_text()
                content_data["total_content_size"] += len(content)
                
                # Track significant files
                if len(content) > 500:
                    content_data["key_files"].append(item.name)
                    # Store preview for LLM context (first 2000 chars)
                    content_data["raw_content_samples"][item.name] = content[:2000]
                    
            except Exception as e:
                logger.warning(f"Could not read {item}: {e}")
    
    return content_data


def format_tier2_output(
    convo_id: str,
    title: str,
    summary: str,
    files: List[Dict],
    session_state: Optional[Dict],
    git_status: Dict,
    content_data: Dict,
    duration_minutes: int = None
) -> str:
    """Format the Tier 2 closure output."""
    
    # Determine conversation type
    convo_type = "Discussion"
    if session_state and session_state.get("type"):
        type_map = {
            "build": "Build session",
            "research": "Research",
            "discussion": "Discussion",
            "planning": "Planning session",
            "debug": "Debugging"
        }
        convo_type = type_map.get(session_state["type"].lower(), "Discussion")
    
    # Duration estimate
    duration_str = f"~{duration_minutes} minutes" if duration_minutes else "Unknown"
    
    output = f"""## Conversation Closed

**Title:** {title}
**Type:** {convo_type}
**Duration:** {duration_str}

### Summary
{summary}

---

### ⚠️ SEMANTIC ANALYSIS REQUIRED (LLM Task)

Librarian must analyze SESSION_STATE.md and conversation context to:
- Extract key decisions with rationale
- Identify open items and next steps
- Write meaningful outcome summary

---

### Files Organized
"""
    
    movable_files = [f for f in files if f.get("action") == "move"]
    if movable_files:
        output += "| File | Destination | Reason |\n"
        output += "|------|-------------|--------|\n"
        for f in movable_files:
            output += f"| `{f['name']}` | `{f['recommended_destination']}` | {f['category']} |\n"
    else:
        output += "- No files to organize\n"
    
    # Key files for context
    output += "\n### Key Files (for LLM context)\n"
    if content_data["key_files"]:
        for fname in content_data["key_files"]:
            output += f"- `{fname}`\n"
    else:
        output += "- No significant content files\n"
    
    # Git status
    output += "\n### Git Status\n"
    if git_status["has_changes"]:
        output += f"⚠️ {git_status['summary']}\n"
        output += "→ Consider committing changes before closing\n"
    else:
        output += "✓ Working directory clean\n"
    
    output += "\n---\n"
    output += "\n**Next:** Invoke Librarian for semantic analysis of decisions and outcomes."
    
    return output


def run_standard_close(convo_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Execute Tier 2 standard close workflow."""
    start_time = datetime.now(timezone.utc)
    
    # Normalize convo_id
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    
    convo_path = get_convo_path(convo_id)
    
    result = {
        "convo_id": convo_id,
        "convo_path": str(convo_path),
        "tier": 2,
        "success": False,
        "title": None,
        "summary": None,
        "files": [],
        "git_status": {},
        "content_data": {},  # Raw content for LLM
        "session_state": None,
        "output": None,
        "errors": []
    }
    
    # Step 1: Read existing session state
    logger.info(f"Reading session state for {convo_id}")
    session_state = read_session_state(convo_path)
    result["session_state"] = session_state
    
    # Step 2: Scan files (same as Tier 1)
    logger.info("Scanning conversation files")
    files = scan_conversation_files(convo_path)
    
    # Step 3: Add move recommendations (Tier 2 addition)
    logger.info("Analyzing file destinations")
    files = recommend_file_destinations(files)
    result["files"] = files
    
    # Step 4: Generate title (same as Tier 1)
    logger.info("Generating title")
    title = generate_title_local(session_state, files, convo_id)
    result["title"] = title
    
    # Step 5: Gather raw content for LLM (NO REGEX EXTRACTION)
    logger.info("Gathering conversation content for LLM analysis")
    content_data = gather_conversation_content(convo_path)
    result["content_data"] = content_data
    
    # Step 6: Generate summary stub (LLM will replace)
    logger.info("Generating summary stub")
    if session_state and session_state.get("focus"):
        summary = f"Discussion about: {session_state['focus']}"
    else:
        summary = "Session completed. (LLM should write real summary)"
    result["summary"] = summary
    
    # Step 7: Check git status (Tier 2 addition)
    logger.info("Checking git status")
    git_status = get_git_status()
    result["git_status"] = git_status
    
    # Step 8: Update SESSION_STATE.md
    logger.info("Updating session state")
    update_session_state(convo_path, title, summary, dry_run)

    # Step 9: Format output
    logger.info("Formatting output")
    output = format_tier2_output(
        convo_id=convo_id,
        title=title,
        summary=summary,
        files=files,
        session_state=session_state,
        git_status=git_status,
        content_data=content_data
    )
    result["output"] = output
    
    # Calculate duration
    end_time = datetime.now(timezone.utc)
    result["duration_seconds"] = (end_time - start_time).total_seconds()
    result["success"] = True
    
    logger.info(f"Standard close complete in {result['duration_seconds']:.2f}s")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Conversation End - Tier 2 (Standard Close)"
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
    
    result = run_standard_close(args.convo_id, args.dry_run)
    
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



