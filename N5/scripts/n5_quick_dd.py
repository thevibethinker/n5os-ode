#!/usr/bin/env python3
"""
Quick Due Diligence (DD) script for Key Figures and Organizations.

Usage: python3 n5_quick_dd.py "Name of Entity" [category]

Category options for organizations: startup, company, community, investor, channel_partner
If no category is provided, it defaults to "key_figure".

This script follows the DD protocol:
1. Review website and LinkedIn/relevant platforms
2. Check recent news (last 6 months)
3. Identify key social media presence/relevant online activity
4. Verify we're looking at the right entity
5. Flag conflicts for manual review

This script is meant to be called by the AI assistant, not run directly.
The AI will perform the actual web searches and analysis.
"""

import sys
from pathlib import Path

def slug_from_name(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    return name.lower().replace(" ", "-").replace(".", "").replace("/", "-").replace("'", "")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 n5_quick_dd.py 'Name of Entity' [category]")
        print("Category options for organizations: startup, company, community, investor, channel_partner")
        sys.exit(1)
    
    name = sys.argv[1]
    category_arg = "key_figure"
    if len(sys.argv) > 2:
        category_arg = sys.argv[2].lower()

    base_dir = Path("/home/workspace")
    slug = slug_from_name(name)
    target_dir = None
    
    if category_arg == "key_figure":
        target_dir = base_dir / "Startup Intelligence/Key Figures"
    elif category_arg == "startup":
        target_dir = base_dir / "Startup Intelligence/Startups"
    elif category_arg == "company":
        target_dir = base_dir / "Startup Intelligence/Companies"
    elif category_arg == "community":
        target_dir = base_dir / "Startup Intelligence/Communities"
    elif category_arg == "investor":
        target_dir = base_dir / "Startup Intelligence/Investors"
    elif category_arg == "channel_partner":
        target_dir = base_dir / "Startup Intelligence/Channel Partners"
    else:
        print(f"Error: Unknown category '{category_arg}'. Valid categories are key_figure, startup, company, community, investor, channel_partner.")
        sys.exit(1)

    filepath = target_dir / f"{slug}.md"
    
    if not filepath.exists():
        print(f"No file found for '{name}' (category: {category_arg}) at {filepath}")
        print("Please create the entity file first or check the name/category.")
        sys.exit(1)
    
    print(f"Found file: {filepath}")
    print(f"Ready for DD on: {name} (Category: {category_arg})")
    print("\nDD Protocol:")
    print("1. Review website and LinkedIn/relevant platforms")
    print("2. Check recent news (last 6 months)")
    print("3. Identify key social media presence/relevant online activity")
    print("4. Verify correct entity")
    print("5. Flag any conflicts")
    print("\nAI: Please proceed with the DD protocol and update the file.")

if __name__ == "__main__":
    main()
