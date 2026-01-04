#!/usr/bin/env python3
"""
start_lab_session.py - Creates exploration folder ON DEMAND when entering Lab.

Usage:
  python3 start_lab_session.py <idea_id>              # Start new session from ideas.jsonl
  python3 start_lab_session.py --from-triage <idea_id> # Start from triage list
  python3 start_lab_session.py --log <folder> --modality <mod> --duration <min> --insights "<text>" --next "<text>"
  python3 start_lab_session.py --archive <folder> --synthesis "<text>"

The folder is only created when V actually starts exploring, not at triage time.
"""

import os
import json
import argparse
import re
from datetime import datetime
from pathlib import Path

LAB_ROOT = Path("/home/workspace/Personal/Knowledge/Lab")
EXPLORATIONS_DIR = LAB_ROOT / "Explorations"
IDEAS_LIST = Path("/home/workspace/Lists/ideas.jsonl")
TRIAGE_LIST = Path("/home/workspace/Lists/idea-triage.jsonl")

def slugify(text: str, max_len: int = 50) -> str:
    """Create URL-safe slug from text."""
    slug = re.sub(r'[^a-z0-9]+', '_', text.lower())
    slug = re.sub(r'_+', '_', slug).strip('_')
    return slug[:max_len]

def find_idea(idea_id: str, from_triage: bool = False) -> dict | None:
    """Find idea by ID in ideas.jsonl or idea-triage.jsonl."""
    source = TRIAGE_LIST if from_triage else IDEAS_LIST
    if not source.exists():
        return None
    for line in source.read_text().strip().split('\n'):
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get('id') == idea_id:
            return obj
    return None

def create_exploration_folder(idea: dict) -> Path:
    """Create the exploration folder structure."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(idea.get('title', 'untitled'))
    folder_name = f"{date_str}_{slug}"
    folder_path = EXPLORATIONS_DIR / folder_name
    
    # Handle collision
    counter = 1
    while folder_path.exists():
        folder_path = EXPLORATIONS_DIR / f"{folder_name}_{counter}"
        counter += 1
    
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Create exploration README with session log
    readme_content = f"""---
created: {date_str}
last_edited: {date_str}
version: 1.0
provenance: idea_lab_session
status: active
---

# Exploration: {idea.get('title', 'Untitled')}

## Origin
- **Source Idea ID:** {idea.get('id')}
- **Original Body:** {idea.get('body', 'N/A')}
- **Tags:** {', '.join(idea.get('tags', []))}

## Session Log
<!-- Each session appended here with timestamp -->

### Session 1 — {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Modality:** [To be filled]
- **Duration:** [To be filled]
- **Key Insights:** [To be filled]
- **Next Action:** [To be filled]

## Synthesis
<!-- Final crystallized learnings when archived -->

## Status History
- {date_str}: Created (active)
"""
    
    (folder_path / "README.md").write_text(readme_content)
    
    # Update Lab README table
    update_lab_readme(folder_path, idea.get('title', 'Untitled'))
    
    return folder_path

def update_lab_readme(folder_path: Path, title: str):
    """Add entry to Lab README table."""
    lab_readme = LAB_ROOT / "README.md"
    if not lab_readme.exists():
        return
    
    content = lab_readme.read_text()
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_row = f"| {date_str} | `file '{folder_path.relative_to(Path('/home/workspace'))}/README.md'` | Active | Explore |"
    
    # Insert before the last row or at end of table
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('| :---'):
            # Insert after header separator
            lines.insert(i + 1, new_row)
            break
    
    lab_readme.write_text('\n'.join(lines))

def log_session(folder_path: Path, modality: str, duration: int, insights: str, next_action: str):
    """Append a session log entry to exploration README."""
    readme = folder_path / "README.md"
    if not readme.exists():
        print(f"Error: README not found at {readme}")
        return
    
    content = readme.read_text()
    now = datetime.now()
    
    # Count existing sessions
    session_count = content.count("### Session")
    new_session_num = session_count + 1
    
    session_entry = f"""
### Session {new_session_num} — {now.strftime("%Y-%m-%d %H:%M")}
- **Modality:** {modality}
- **Duration:** {duration} minutes
- **Key Insights:** {insights}
- **Next Action:** {next_action}
"""
    
    # Insert before "## Synthesis" section
    if "## Synthesis" in content:
        content = content.replace("## Synthesis", session_entry + "\n## Synthesis")
    else:
        content += session_entry
    
    # Update last_edited in frontmatter
    content = re.sub(r'last_edited: \d{4}-\d{2}-\d{2}', 
                     f'last_edited: {now.strftime("%Y-%m-%d")}', content)
    
    readme.write_text(content)
    print(f"✓ Session {new_session_num} logged to {readme}")

def archive_exploration(folder_path: Path, synthesis: str):
    """Mark exploration as archived with final synthesis."""
    readme = folder_path / "README.md"
    if not readme.exists():
        print(f"Error: README not found at {readme}")
        return
    
    content = readme.read_text()
    now = datetime.now()
    
    # Update status to archived
    content = re.sub(r'status: \w+', 'status: archived', content)
    content = re.sub(r'last_edited: \d{4}-\d{2}-\d{2}', 
                     f'last_edited: {now.strftime("%Y-%m-%d")}', content)
    
    # Add synthesis content
    if "## Synthesis" in content:
        content = content.replace("## Synthesis\n<!-- Final crystallized learnings when archived -->",
                                  f"## Synthesis\n{synthesis}")
    
    # Add to status history
    archive_entry = f"- {now.strftime('%Y-%m-%d')}: Archived (exploration complete)"
    content = content.replace("## Status History", f"## Status History\n{archive_entry}")
    
    readme.write_text(content)
    
    # Update Lab README table status
    update_lab_readme_status(folder_path, "Archived")
    
    print(f"✓ Exploration archived: {folder_path}")
    print(f"  Synthesis saved. Status: archived")

def update_lab_readme_status(folder_path: Path, new_status: str):
    """Update status in Lab README table."""
    lab_readme = LAB_ROOT / "README.md"
    if not lab_readme.exists():
        return
    
    content = lab_readme.read_text()
    rel_path = str(folder_path.relative_to(Path('/home/workspace')))
    
    # Find and update the row
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if rel_path in line:
            # Replace "Active" with new status
            lines[i] = re.sub(r'\| Active \|', f'| {new_status} |', line)
            break
    
    lab_readme.write_text('\n'.join(lines))

def start_session(idea_id: str, from_triage: bool = False):
    """Main entry point: find idea and create folder."""
    idea = find_idea(idea_id, from_triage)
    if not idea:
        source = "triage" if from_triage else "ideas"
        print(f"Error: Idea ID {idea_id} not found in {source} list.")
        return
    
    folder = create_exploration_folder(idea)
    print(f"✓ Lab session started: {folder}")
    print(f"  README: {folder / 'README.md'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a Lab exploration session")
    parser.add_argument("idea_id", nargs='?', help="The UUID of the idea to explore")
    parser.add_argument("--from-triage", action="store_true", 
                        help="Look in idea-triage.jsonl instead of ideas.jsonl")
    parser.add_argument("--log", metavar="FOLDER", help="Log a session to existing exploration folder")
    parser.add_argument("--modality", help="Modality used (for --log)")
    parser.add_argument("--duration", type=int, help="Duration in minutes (for --log)")
    parser.add_argument("--insights", help="Key insights (for --log)")
    parser.add_argument("--next", dest="next_action", help="Next action (for --log)")
    parser.add_argument("--archive", metavar="FOLDER", help="Archive an exploration")
    parser.add_argument("--synthesis", help="Final synthesis (for --archive)")
    
    args = parser.parse_args()
    
    if args.log:
        folder = Path(args.log)
        if not folder.is_absolute():
            folder = EXPLORATIONS_DIR / args.log
        log_session(folder, args.modality or "Unknown", args.duration or 0, 
                   args.insights or "", args.next_action or "")
    elif args.archive:
        folder = Path(args.archive)
        if not folder.is_absolute():
            folder = EXPLORATIONS_DIR / args.archive
        archive_exploration(folder, args.synthesis or "")
    elif args.idea_id:
        start_session(args.idea_id, args.from_triage)
    else:
        parser.print_help()


