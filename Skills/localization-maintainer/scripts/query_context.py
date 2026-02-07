#!/usr/bin/env python3
"""
Localization Maintainer - Context Query Script

Query the current localization context for use in advisory conversations.
Provides selective revelation based on what's requested.

Runs on CLIENT Zo instances, not va.
"""

import argparse
import json
from pathlib import Path


def load_context() -> dict | None:
    """Load the context file."""
    context_file = Path("/home/workspace/N5/data/localization_context.json")
    if not context_file.exists():
        print("⚠️ No context file found. Run refresh_context.py first.")
        return None
    return json.loads(context_file.read_text())


def query_skills(context: dict, detail: bool = False) -> None:
    """Show available skills."""
    print("## Available Skills\n")
    if detail:
        for skill in context.get("skills_detail", []):
            print(f"- **{skill['name']}** (`{skill['path']}`)")
            if skill.get("scripts"):
                print(f"  Scripts: {', '.join(skill['scripts'])}")
    else:
        for name in context.get("skills", []):
            print(f"- {name}")


def query_structure(context: dict) -> None:
    """Show folder structure."""
    print("## Folder Structure\n")
    for folder, children in context.get("folder_structure", {}).items():
        print(f"- **{folder}**")
        for child in children[:5]:  # Limit display
            print(f"  - {child}")
        if len(children) > 5:
            print(f"  - ... and {len(children) - 5} more")


def query_conventions(context: dict) -> None:
    """Show naming conventions and aliases."""
    print("## Conventions\n")
    conventions = context.get("conventions", {})
    
    if conventions.get("aliases"):
        print("### Active Aliases")
        for canonical, display in conventions["aliases"].items():
            print(f"- {canonical} → {display}")
        print()
    
    if conventions.get("naming_pattern"):
        print(f"**Naming pattern:** {conventions['naming_pattern']}")


def query_summary(context: dict) -> None:
    """Show a brief summary for conversation injection."""
    print("## Client Context Summary\n")
    print(f"- **Last refresh:** {context.get('last_refresh', 'unknown')}")
    print(f"- **Localization tier:** {context.get('localization_tier', 'not set')}")
    print(f"- **Skills available:** {len(context.get('skills', []))}")
    print(f"- **System scripts:** {len(context.get('scripts', []))}")
    
    aliases = context.get("conventions", {}).get("aliases", {})
    if aliases:
        print(f"- **Active aliases:** {len(aliases)}")
        for k, v in list(aliases.items())[:3]:
            print(f"  - {k} → {v}")
    
    print("\n### Key Skills")
    for name in context.get("skills", [])[:5]:
        print(f"- {name}")


def main():
    parser = argparse.ArgumentParser(description="Query localization context")
    parser.add_argument(
        "--what",
        choices=["skills", "structure", "conventions", "summary", "all"],
        default="summary",
        help="What to query"
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON"
    )
    args = parser.parse_args()
    
    context = load_context()
    if not context:
        return
    
    if args.json:
        print(json.dumps(context, indent=2))
        return
    
    if args.what == "skills":
        query_skills(context, args.detail)
    elif args.what == "structure":
        query_structure(context)
    elif args.what == "conventions":
        query_conventions(context)
    elif args.what == "summary":
        query_summary(context)
    elif args.what == "all":
        query_summary(context)
        print("\n---\n")
        query_skills(context, args.detail)
        print("\n---\n")
        query_structure(context)
        print("\n---\n")
        query_conventions(context)


if __name__ == "__main__":
    main()
