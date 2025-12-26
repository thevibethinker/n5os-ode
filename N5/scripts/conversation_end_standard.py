#!/usr/bin/env python3
"""
Conversation End - Tier 2 (Standard Close) v3.0

Standard conversation close for research, substantial discussions, and 
sessions with multiple artifacts. Includes decision extraction and git check.

Cost target: <$0.08 | Time target: <90 seconds

Builds on Tier 1, adding:
- Detailed file organization with move recommendations
- Decision/outcome extraction patterns
- Open items detection
- Git status integration

Usage:
    python3 conversation_end_standard.py --convo-id <id> [--dry-run]
    
Returns: Markdown formatted closure report with decisions and outcomes
"""

import argparse
import json
import logging
import os
import re
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

# Decision patterns to detect
DECISION_PATTERNS = [
    r"(?:decided|decision|chose|choosing|picked|selected|went with|going with)\s+(?:to\s+)?(.{10,100})",
    r"(?:will|going to|plan to|agreed to)\s+(.{10,80})",
    r"(?:confirmed|confirmed that|established)\s+(.{10,80})",
]

# Open item patterns
OPEN_ITEM_PATTERNS = [
    r"(?:TODO|FIXME|NEXT|LATER|PENDING):\s*(.{5,100})",
    r"(?:need to|should|must|have to)\s+(.{10,80})(?:\.|$)",
    r"(?:follow up|followup|follow-up)\s+(?:on|with|about)?\s*(.{5,80})",
]

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


def extract_decisions_from_text(text: str) -> List[str]:
    """Extract decision statements from text."""
    decisions = []
    
    for pattern in DECISION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean up the match
            decision = match.strip().rstrip('.,;:')
            
            # Filter out noise
            if len(decision) < 10:
                continue
            if decision in decisions:
                continue
            # Skip markdown table artifacts
            if '│' in decision or '|' in decision:
                continue
            # Skip code-like content
            if decision.startswith('`') or decision.startswith('('):
                continue
            # Skip very short words only
            if len(decision.split()) < 3:
                continue
                
            decisions.append(decision)
    
    # Deduplicate similar decisions
    unique_decisions = []
    for d in decisions:
        is_duplicate = False
        for existing in unique_decisions:
            if d.lower() in existing.lower() or existing.lower() in d.lower():
                is_duplicate = True
                break
        if not is_duplicate:
            unique_decisions.append(d)
    
    return unique_decisions[:5]  # Limit to top 5


def extract_open_items(text: str) -> List[str]:
    """Extract open items / todos from text."""
    items = []
    
    for pattern in OPEN_ITEM_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            item = match.strip().rstrip('.,;:')
            if len(item) > 5 and item not in items:
                items.append(item)
    
    return items[:5]  # Limit to top 5


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


def analyze_conversation_content(convo_path: Path) -> Dict[str, Any]:
    """Analyze conversation workspace content for patterns."""
    analysis = {
        "decisions": [],
        "open_items": [],
        "key_files": [],
        "total_content_size": 0
    }
    
    # Scan all readable files
    for item in convo_path.iterdir():
        if item.is_file() and item.suffix in ['.md', '.txt', '.json']:
            try:
                content = item.read_text()
                analysis["total_content_size"] += len(content)
                
                # Extract decisions
                decisions = extract_decisions_from_text(content)
                analysis["decisions"].extend(decisions)
                
                # Extract open items
                open_items = extract_open_items(content)
                analysis["open_items"].extend(open_items)
                
                # Track significant files
                if len(content) > 500:
                    analysis["key_files"].append(item.name)
                    
            except Exception as e:
                logger.warning(f"Could not read {item}: {e}")
    
    # Deduplicate
    analysis["decisions"] = list(set(analysis["decisions"]))[:5]
    analysis["open_items"] = list(set(analysis["open_items"]))[:5]
    
    return analysis


def format_tier2_output(
    convo_id: str,
    title: str,
    summary: str,
    files: List[Dict],
    session_state: Optional[Dict],
    git_status: Dict,
    content_analysis: Dict,
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

### Key Outcomes
"""
    
    # Add outcomes from progress or decisions
    if session_state and session_state.get("progress"):
        for item in session_state["progress"][:3]:
            output += f"- {item}\n"
    elif content_analysis["decisions"]:
        output += "- " + "\n- ".join(content_analysis["decisions"][:3]) + "\n"
    else:
        output += "- Session completed\n"
    
    # Decisions section
    output += "\n### Decisions Made\n"
    if content_analysis["decisions"]:
        for decision in content_analysis["decisions"][:3]:
            output += f"- {decision}\n"
    else:
        output += "- No major decisions recorded\n"
    
    # Files section
    output += "\n### Files Organized\n"
    movable_files = [f for f in files if f.get("action") == "move"]
    if movable_files:
        output += "| File | Destination | Reason |\n"
        output += "|------|-------------|--------|\n"
        for f in movable_files:
            output += f"| `{f['name']}` | `{f['recommended_destination']}` | {f['category']} |\n"
    else:
        output += "- No files to organize\n"
    
    # Open items
    output += "\n### Open Items\n"
    if content_analysis["open_items"]:
        for item in content_analysis["open_items"][:3]:
            output += f"- [ ] {item}\n"
    else:
        output += "- None identified\n"
    
    # Git status
    output += "\n### Git Status\n"
    if git_status["has_changes"]:
        output += f"⚠️ {git_status['summary']}\n"
        output += "→ Consider committing changes before closing\n"
    else:
        output += "✓ Working directory clean\n"
    
    output += "\n✅ Workspace organized"
    
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
        "content_analysis": {},
        "output": None,
        "errors": []
    }
    
    # Step 1: Read existing session state
    logger.info(f"Reading session state for {convo_id}")
    session_state = read_session_state(convo_path)
    
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
    
    # Step 5: Analyze conversation content (Tier 2 addition)
    logger.info("Analyzing conversation content")
    content_analysis = analyze_conversation_content(convo_path)
    result["content_analysis"] = content_analysis
    
    # Step 6: Generate summary stub
    logger.info("Generating summary")
    if session_state and session_state.get("focus"):
        summary = f"Discussion about: {session_state['focus']}"
    elif content_analysis["decisions"]:
        summary = f"Session with {len(content_analysis['decisions'])} decisions made."
    else:
        summary = "Standard conversation session."
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
        content_analysis=content_analysis
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


