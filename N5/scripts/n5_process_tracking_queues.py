#!/usr/bin/env python3
"""
Process the individuals_queue.jsonl and organizations_queue.jsonl lists and create their respective markdown files.

This script:
1. Reads entries from N5/lists/individuals_queue.jsonl and N5/lists/organizations_queue.jsonl
2. Creates a markdown file for each new individual/organization based on templates
3. Archives processed entries to N5/lists/processed_archive.jsonl
4. Logs what was created/skipped
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def slug_from_name(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    return name.lower().replace(" ", "-").replace(".", "").replace("/", "-").replace("'", "")

def get_template_content(template_path: Path, entry_name: str, today_date: str, context: str = "", source: str = "") -> str:
    """Reads a template file and populates basic fields."""
    if not template_path.exists():
        return f"""---
name: "{entry_name}"
last_updated: "{today_date}"
---

# {entry_name}

## Context

{context}
{f'**Added from:** {source}' if source else ''}

## Notes

_[Add your notes here]_

## Recent Activity

_[DD findings will be appended here]_
"""
    
    content = template_path.read_text()
    # Replace placeholders
    content = content.replace('name: ""', f'name: "{entry_name}"')
    content = content.replace('last_updated: ""', f'last_updated: "{today_date}"')
    content = content.replace('ENTITY_NAME', entry_name)
    
    # Build context section
    context_text = ""
    if context:
        context_text += context
    if source:
        if context_text:
            context_text += "\n\n"
        context_text += f"**Added from:** {source}"
    
    if not context_text:
        context_text = "_[Add context here]_"
    
    content = content.replace('CONTEXT_PLACEHOLDER', context_text)
    return content

def process_queue(
    queue_path: Path, 
    target_base_dir: Path, 
    template_map: Dict[str, Path], 
    archive_path: Path, 
    today_date: str,
    entity_type: str
) -> int:
    """Generic function to process a queue file."""
    if not queue_path.exists():
        return 0
    
    entries = []
    with open(queue_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    
    if not entries:
        return 0
    
    processed_count = 0
    new_archive_entries = []

    for entry in entries:
        name = entry.get("name", "").strip()
        category = entry.get("category", "unknown").strip()
        type_str = entry.get("type", "unknown").strip()
        context = entry.get("context", "")
        source = entry.get("source", "")
        
        if not name:
            print(f"Skipping entry with no name in {queue_path}: {entry}")
            continue

        target_dir = target_base_dir
        template_file = None

        if entity_type == "individual":
            target_dir = target_base_dir / "Key Figures"
            template_file = template_map.get("key_figure")
        elif entity_type == "organization":
            if category == "startup":
                target_dir = target_base_dir / "Startups"
                template_file = template_map.get("startup")
            elif category == "company":
                target_dir = target_base_dir / "Companies"
                template_file = template_map.get("company")
            elif category == "community":
                target_dir = target_base_dir / "Communities"
                template_file = template_map.get("community")
            elif category == "investor":
                target_dir = target_base_dir / "Investors"
                template_file = template_map.get("investor")
            elif category == "channel_partner":
                target_dir = target_base_dir / "Channel Partners"
                template_file = template_map.get("channel_partner")
            else:
                print(f"Skipping organization '{name}' due to unknown category: {category}")
                continue
        
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            
        slug = slug_from_name(name)
        filepath = target_dir / f"{slug}.md"
        
        if filepath.exists():
            print(f"File already exists for '{name}' ({entity_type}): {filepath}")
            print("  → Skipping (use DD script to update existing entities)")
        else:
            template_content = get_template_content(template_file, name, today_date, context, source)
            
            # Populate type for Key Figures in frontmatter
            if entity_type == "individual":
                old_type = 'type: "unknown"'
                new_type = f'type: "{type_str}"'
                template_content = template_content.replace(old_type, new_type)
            elif entity_type == "organization":
                # For organizations, templates already have correct types
                pass

            with open(filepath, "w") as f:
                f.write(template_content)
            
            print(f"✓ Created: {filepath}")
            processed_count += 1
        
        new_archive_entries.append(entry)

    # Archive processed entries
    if new_archive_entries:
        with open(archive_path, "a") as f:
            for entry in new_archive_entries:
                entry["processed_date"] = today_date
                f.write(json.dumps(entry) + "\n")
        
        # Clear the queue file
        with open(queue_path, "w") as f:
            f.write("")
        
        print(f"\n✓ Archived {len(new_archive_entries)} processed {entity_type} entries from {queue_path} to {archive_path}")
        print(f"✓ Cleared {entity_type} queue: {queue_path}")
    
    return processed_count

def main():
    base_dir = Path("/home/workspace")
    lists_dir = base_dir / "N5/lists"
    si_dir = base_dir / "Startup Intelligence"
    archive_path = lists_dir / "processed_archive.jsonl"
    today = datetime.now().strftime("%Y-%m-%d")

    # Define template paths
    template_map = {
        "key_figure": si_dir / "Key Figures/_TEMPLATE.md",
        "startup": si_dir / "Startups/_TEMPLATE.md",
        "company": si_dir / "Companies/_TEMPLATE.md",
        "community": si_dir / "Communities/_TEMPLATE.md",
        "investor": si_dir / "Investors/_TEMPLATE.md",
        "channel_partner": si_dir / "Channel Partners/_TEMPLATE.md",
    }

    print("Processing individuals queue...")
    process_queue(
        queue_path=lists_dir / "individuals_queue.jsonl",
        target_base_dir=si_dir,
        template_map=template_map,
        archive_path=archive_path,
        today_date=today,
        entity_type="individual"
    )

    print("\nProcessing organizations queue...")
    process_queue(
        queue_path=lists_dir / "organizations_queue.jsonl",
        target_base_dir=si_dir,
        template_map=template_map,
        archive_path=archive_path,
        today_date=today,
        entity_type="organization"
    )

if __name__ == "__main__":
    main()
