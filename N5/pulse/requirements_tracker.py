#!/usr/bin/env python3
"""
Track requirements, preferences, and decisions during builds.
Captures V's statements and exports to REQUIREMENTS.md.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

WORKSPACE = Path("/home/workspace")
PULSE_DIR = WORKSPACE / "N5" / "pulse"
BUILDS_DIR = WORKSPACE / "N5" / "builds"

# Patterns for auto-detection
PATTERNS = {
    "requirement": [
        r"I want (.+)",
        r"I need (.+)",
        r"I'd like (.+)",
        r"I would like (.+)",
        r"We need (.+)",
        r"We want (.+)",
        r"Make sure (.+)",
        r"Ensure (.+)",
        r"Required:?\s*(.+)",
        r"Must (.+)"
    ],
    "preference": [
        r"Always (.+)",
        r"Never (.+)",
        r"I prefer (.+)",
        r"I'd prefer (.+)",
        r"I would prefer (.+)",
        r"Preference:?\s*(.+)",
        r"Prefer (.+)",
        r"Use (.+)\s+instead",
        r"Don't (.+)"
    ],
    "decision": [
        r"Let's go with (.+)",
        r"Let's go for (.+)",
        r"Let's use (.+)",
        r"Decision:?\s*(.+)",
        r"Decided to (.+)",
        r"Going with (.+)",
        r"Going to (.+)",
        r"Going for (.+)",
        r"Selected (.+)",
        r"Choose (.+)",
        r"Chose (.+)"
    ]
}


def get_requirements_path(build_slug: str) -> Path:
    """Get the path to a build's requirements.jsonl file."""
    return BUILDS_DIR / build_slug / "requirements.jsonl"


def get_meta_path(build_slug: str) -> Path:
    """Get the path to a build's meta.json file."""
    return BUILDS_DIR / build_slug / "meta.json"


def capture(
    text: str,
    req_type: str,  # requirement, preference, decision
    build_slug: str = None,
    conversation_id: str = None,
    persona_name: str = None,
    drop_id: str = None
) -> dict:
    """
    Capture a requirement/preference/decision statement.
    
    Args:
        text: The raw text statement
        req_type: Type: requirement, preference, or decision
        build_slug: Build identifier
        conversation_id: Conversation ID
        persona_name: Who made this statement
        drop_id: Which Drop this relates to (if applicable)
    
    Returns:
        Dict of captured requirement
    """
    requirement = {
        "id": f"req-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "type": req_type,
        "text": text,
        "text_normalized": text.strip().lower(),
        "build_slug": build_slug,
        "conversation_id": conversation_id,
        "persona_name": persona_name,
        "drop_id": drop_id,
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "active",  # active, superseded, completed, deprecated
        "applied": False
    }
    
    # Write to JSONL
    if build_slug:
        path = get_requirements_path(build_slug)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(requirement) + "\n")
    
    return requirement


def auto_detect_and_capture(
    text: str,
    build_slug: str = None,
    conversation_id: str = None,
    persona_name: str = None,
    drop_id: str = None
) -> List[dict]:
    """
    Auto-detect requirements/preferences/decisions from text.
    
    Args:
        text: Text to analyze
        build_slug: Build identifier
        conversation_id: Conversation ID
        persona_name: Who made this statement
        drop_id: Which Drop this relates to
    
    Returns:
        List of captured items
    """
    captured = []
    text_lower = text.lower()
    
    # Check each pattern type
    for req_type, patterns in PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract the captured group
                extracted = match.group(1).strip()
                
                # Clean up trailing punctuation
                extracted = re.sub(r'[.!?,;]*$', '', extracted)
                
                # Capture it
                item = capture(
                    text=match.group(0),
                    req_type=req_type,
                    build_slug=build_slug,
                    conversation_id=conversation_id,
                    persona_name=persona_name,
                    drop_id=drop_id
                )
                captured.append(item)
    
    return captured


def load_requirements(build_slug: str) -> List[dict]:
    """
    Load all requirements for a build.
    
    Args:
        build_slug: Build identifier
    
    Returns:
        List of requirement dicts
    """
    path = get_requirements_path(build_slug)
    if not path.exists():
        return []
    
    requirements = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                requirements.append(json.loads(line))
            except:
                continue
    
    # Sort by captured time
    requirements.sort(key=lambda x: x.get("captured_at", ""))
    return requirements


def mark_applied(build_slug: str, req_id: str) -> bool:
    """
    Mark a requirement as applied.
    
    Args:
        build_slug: Build identifier
        req_id: Requirement ID
    
    Returns:
        True if found and updated
    """
    path = get_requirements_path(build_slug)
    if not path.exists():
        return False
    
    requirements = []
    found = False
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                if req.get("id") == req_id:
                    req["applied"] = True
                    req["applied_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    found = True
                requirements.append(req)
            except:
                requirements.append(json.loads(line))
    
    if not found:
        return False
    
    # Rewrite file
    with open(path, "w") as f:
        for req in requirements:
            f.write(json.dumps(req) + "\n")
    
    return True


def supersede(build_slug: str, old_req_id: str, new_text: str) -> bool:
    """
    Mark a requirement as superseded by a new one.
    
    Args:
        build_slug: Build identifier
        old_req_id: ID of requirement to supersede
        new_text: Text of new requirement
    
    Returns:
        True if successful
    """
    path = get_requirements_path(build_slug)
    if not path.exists():
        return False
    
    requirements = []
    old_req = None
    found = False
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                if req.get("id") == old_req_id:
                    old_req = req
                    req["status"] = "superseded"
                    req["superseded_by"] = f"req-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
                    req["superseded_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    found = True
                requirements.append(req)
            except:
                continue
    
    if not found or not old_req:
        return False
    
    # Create new requirement
    new_req = capture(
        text=new_text,
        req_type=old_req["type"],
        build_slug=build_slug,
        conversation_id=old_req.get("conversation_id"),
        persona_name=old_req.get("persona_name"),
        drop_id=old_req.get("drop_id")
    )
    
    # Append to requirements list
    requirements.append(new_req)
    
    # Rewrite file
    with open(path, "w") as f:
        for req in requirements:
            f.write(json.dumps(req) + "\n")
    
    return True


def export_to_md(build_slug: str) -> str:
    """
    Generate REQUIREMENTS.md from captured items.
    
    Args:
        build_slug: Build identifier
    
    Returns:
        Path to generated file
    """
    requirements = load_requirements(build_slug)
    meta_path = get_meta_path(build_slug)
    
    # Load meta for title
    title = build_slug
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            title = meta.get("title", build_slug)
        except:
            pass
    
    # Group by type
    by_type = {
        "requirement": [],
        "preference": [],
        "decision": []
    }
    
    for req in requirements:
        rtype = req.get("type", "requirement")
        if rtype in by_type:
            by_type[rtype].append(req)
    
    # Generate markdown
    md = f"""---
created: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
last_edited: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
version: 1.0
provenance: {Path(__file__).name}
---

# Requirements: {title}

**Build:** {build_slug}
**Total Items:** {len(requirements)}
**Last Updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## Requirements ({len(by_type['requirement'])})

"""
    
    for req in by_type["requirement"]:
        status = req.get("status", "active")
        applied = "✓" if req.get("applied") else "○"
        
        md += f"### {applied} {req['id']}\n\n"
        md += f"> {req['text']}\n\n"
        md += f"- **Status:** {status}\n"
        md += f"- **Source:** {req.get('persona_name', 'Unknown')}"
        if req.get("drop_id"):
            md += f" (via {req.get('drop_id')})"
        md += "\n"
        md += f"- **Captured:** {req.get('captured_at', 'N/A')[:19].replace('T', ' ')}\n"
        md += "\n"
    
    md += f"---\n\n## Preferences ({len(by_type['preference'])})\n\n"
    
    for req in by_type["preference"]:
        status = req.get("status", "active")
        
        md += f"### {req['id']}\n\n"
        md += f"> {req['text']}\n\n"
        md += f"- **Status:** {status}\n"
        md += f"- **Source:** {req.get('persona_name', 'Unknown')}"
        if req.get("drop_id"):
            md += f" (via {req.get('drop_id')})"
        md += "\n"
        md += f"- **Captured:** {req.get('captured_at', 'N/A')[:19].replace('T', ' ')}\n"
        md += "\n"
    
    md += f"---\n\n## Decisions ({len(by_type['decision'])})\n\n"
    
    for req in by_type["decision"]:
        status = req.get("status", "active")
        
        md += f"### {req['id']}\n\n"
        md += f"> {req['text']}\n\n"
        md += f"- **Status:** {status}\n"
        md += f"- **Source:** {req.get('persona_name', 'Unknown')}"
        if req.get("drop_id"):
            md += f" (via {req.get('drop_id')})"
        md += "\n"
        md += f"- **Captured:** {req.get('captured_at', 'N/A')[:19].replace('T', ' ')}\n"
        md += "\n"
    
    # Write to build dir
    output_path = BUILDS_DIR / build_slug / "REQUIREMENTS.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md)
    
    return str(output_path)


def list_unapplied(build_slug: str) -> List[dict]:
    """
    List all unapplied requirements for a build.
    
    Args:
        build_slug: Build identifier
    
    Returns:
        List of unapplied requirements
    """
    requirements = load_requirements(build_slug)
    return [r for r in requirements if not r.get("applied") and r.get("status") == "active"]


def main():
    parser = argparse.ArgumentParser(
        description="Pulse Requirements Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture a requirement
  python3 N5/pulse/requirements_tracker.py capture \\
    "I want all plans to be reviewed before building" \\
    --type requirement --build-slug my-build

  # Auto-detect from text
  python3 N5/pulse/requirements_tracker.py detect \\
    "I want a fast API. Always use TypeScript. Let's go with Bun." \\
    --build-slug my-build --persona-name V

  # List all requirements
  python3 N5/pulse/requirements_tracker.py list my-build

  # List unapplied requirements
  python3 N5/pulse/requirements_tracker.py list-unapplied my-build

  # Mark as applied
  python3 N5/pulse/requirements_tracker.py apply my-build req-20250124123456

  # Export to markdown
  python3 N5/pulse/requirements_tracker.py export my-build

  # Supersede a requirement
  python3 N5/pulse/requirements_tracker.py supersede my-build req-20250124123456 \\
    "I want all plans AND code to be reviewed before building"
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # capture
    capture_parser = subparsers.add_parser("capture", help="Capture a requirement")
    capture_parser.add_argument("text", help="Requirement text")
    capture_parser.add_argument("--type", required=True, choices=["requirement", "preference", "decision"])
    capture_parser.add_argument("--build-slug", help="Build slug")
    capture_parser.add_argument("--conversation-id", help="Conversation ID")
    capture_parser.add_argument("--persona-name", help="Who made this statement")
    capture_parser.add_argument("--drop-id", help="Drop ID")
    
    # detect
    detect_parser = subparsers.add_parser("detect", help="Auto-detect requirements from text")
    detect_parser.add_argument("text", help="Text to analyze")
    detect_parser.add_argument("--build-slug", help="Build slug")
    detect_parser.add_argument("--conversation-id", help="Conversation ID")
    detect_parser.add_argument("--persona-name", help="Who made this statement")
    detect_parser.add_argument("--drop-id", help="Drop ID")
    
    # list
    list_parser = subparsers.add_parser("list", help="List all requirements")
    list_parser.add_argument("build_slug", help="Build slug")
    list_parser.add_argument("--type", choices=["requirement", "preference", "decision"], help="Filter by type")
    
    # list-unapplied
    unapplied_parser = subparsers.add_parser("list-unapplied", help="List unapplied requirements")
    unapplied_parser.add_argument("build_slug", help="Build slug")
    
    # apply
    apply_parser = subparsers.add_parser("apply", help="Mark requirement as applied")
    apply_parser.add_argument("build_slug", help="Build slug")
    apply_parser.add_argument("req_id", help="Requirement ID")
    
    # export
    export_parser = subparsers.add_parser("export", help="Export to REQUIREMENTS.md")
    export_parser.add_argument("build_slug", help="Build slug")
    
    # supersede
    supersede_parser = subparsers.add_parser("supersede", help="Supersede a requirement")
    supersede_parser.add_argument("build_slug", help="Build slug")
    supersede_parser.add_argument("old_req_id", help="Old requirement ID")
    supersede_parser.add_argument("new_text", help="New requirement text")
    
    args = parser.parse_args()
    
    if args.command == "capture":
        req = capture(
            text=args.text,
            req_type=args.type,
            build_slug=args.build_slug,
            conversation_id=args.conversation_id,
            persona_name=args.persona_name,
            drop_id=args.drop_id
        )
        print(f"Captured {req['type']}: {req['id']}")
        print(f"Text: {req['text']}")
        if args.build_slug:
            print(f"Build: {args.build_slug}")
    
    elif args.command == "detect":
        captured = auto_detect_and_capture(
            text=args.text,
            build_slug=args.build_slug,
            conversation_id=args.conversation_id,
            persona_name=args.persona_name,
            drop_id=args.drop_id
        )
        print(f"Detected {len(captured)} items:")
        for item in captured:
            print(f"  [{item['type']}] {item['text']}")
        if args.build_slug:
            print(f"Saved to: {get_requirements_path(args.build_slug)}")
    
    elif args.command == "list":
        requirements = load_requirements(args.build_slug)
        if args.type:
            requirements = [r for r in requirements if r.get("type") == args.type]
        
        if not requirements:
            print(f"No requirements found for {args.build_slug}")
        else:
            print(f"\nRequirements for {args.build_slug} ({len(requirements)} total):\n")
            for req in requirements:
                applied = "✓" if req.get("applied") else " "
                status = req.get("status", "active")
                print(f"{applied} [{req['type']}] {req['id']}")
                print(f"  {req['text']}")
                print(f"  Status: {status} | Source: {req.get('persona_name', 'Unknown')}")
                if req.get("drop_id"):
                    print(f"  Drop: {req.get('drop_id')}")
                print()
    
    elif args.command == "list-unapplied":
        unapplied = list_unapplied(args.build_slug)
        
        if not unapplied:
            print(f"All requirements applied for {args.build_slug}")
        else:
            print(f"\nUnapplied requirements for {args.build_slug} ({len(unapplied)}):\n")
            for req in unapplied:
                print(f"[{req['type']}] {req['id']}")
                print(f"  {req['text']}")
                print()
    
    elif args.command == "apply":
        success = mark_applied(args.build_slug, args.req_id)
        if success:
            print(f"Marked {args.req_id} as applied")
        else:
            print(f"Requirement {args.req_id} not found")
    
    elif args.command == "export":
        path = export_to_md(args.build_slug)
        print(f"Exported to: {path}")
    
    elif args.command == "supersede":
        success = supersede(args.build_slug, args.old_req_id, args.new_text)
        if success:
            print(f"Superseded {args.old_req_id} with new requirement")
        else:
            print(f"Requirement {args.old_req_id} not found")


if __name__ == "__main__":
    main()
