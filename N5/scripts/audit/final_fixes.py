#!/usr/bin/env python3
"""Apply final fixes to remaining command file issues."""

import json
from pathlib import Path
from datetime import datetime

COMMANDS_DIR = Path("/home/workspace/N5/commands")

def fix_missing_checksum(filepath):
    """Add missing checksum to frontmatter."""
    content = filepath.read_text()
    
    if "checksum:" in content:
        return False, "Already has checksum"
    
    # Find the end of frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "No frontmatter found"
    
    frontmatter = parts[1]
    rest = parts[2]
    
    # Generate checksum from filename
    checksum = filepath.stem.replace("-", "_") + "_v1_0_0"
    
    # Add checksum after generated_date line
    lines = frontmatter.split("\n")
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if "generated_date:" in line:
            new_lines.append(f"checksum: {checksum}")
    
    new_frontmatter = "\n".join(new_lines)
    new_content = f"---{new_frontmatter}---{rest}"
    
    filepath.write_text(new_content)
    return True, f"Added checksum: {checksum}"

def fix_missing_fields(filepath, missing_fields):
    """Add multiple missing frontmatter fields."""
    content = filepath.read_text()
    
    if not content.startswith("---"):
        return False, "No frontmatter"
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "Invalid frontmatter"
    
    frontmatter = parts[1]
    rest = parts[2]
    
    # Check which fields are actually missing
    to_add = {}
    
    if "date:" not in frontmatter and "date" in missing_fields:
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%dT%H:%M:%SZ')
        to_add["date"] = f"'{mtime}'"
    
    if "checksum:" not in frontmatter and "checksum" in missing_fields:
        checksum = filepath.stem.replace("-", "_") + "_v1_0_0"
        to_add["checksum"] = checksum
    
    if "category:" not in frontmatter and "category" in missing_fields:
        # Smart category detection
        if "list" in filepath.stem:
            to_add["category"] = "lists"
        elif "incantum" in filepath.stem:
            to_add["category"] = "productivity"
        else:
            to_add["category"] = "misc"
    
    if "priority:" not in frontmatter and "priority" in missing_fields:
        to_add["priority"] = "medium"
    
    if not to_add:
        return False, "No fields to add"
    
    # Add fields
    lines = frontmatter.split("\n")
    new_lines = []
    for line in lines:
        new_lines.append(line)
        # Add after appropriate lines
        if "generated_date:" in line and "checksum" in to_add:
            new_lines.append(f"checksum: {to_add['checksum']}")
        elif "tags:" in line and "category" in to_add:
            new_lines.append(f"category: {to_add['category']}")
        elif "category:" in line and "priority" in to_add:
            new_lines.append(f"priority: {to_add['priority']}")
    
    # Handle date at the beginning
    if "date" in to_add:
        new_lines = [f"date: {to_add['date']}"] + [l for l in new_lines if "date:" not in l or "generated_date:" in l or "last-tested:" in l]
    
    new_frontmatter = "\n".join(new_lines)
    new_content = f"---{new_frontmatter}---{rest}"
    
    filepath.write_text(new_content)
    return True, f"Added fields: {', '.join(to_add.keys())}"

def add_missing_section(filepath, section_name, default_content="(None)"):
    """Add a missing section to a command file."""
    content = filepath.read_text()
    
    if section_name in content:
        return False, f"Section {section_name} already exists"
    
    # Determine where to add the section
    if section_name == "## Inputs":
        # Add after Workflow: or Tags: line
        if "Tags:" in content:
            parts = content.split("Tags:", 1)
            # Find next section after Tags
            rest = parts[1]
            next_section_idx = rest.find("\n##")
            if next_section_idx > 0:
                insert_point = content.find("Tags:") + len("Tags:") + next_section_idx
                new_content = content[:insert_point] + f"\n\n{section_name}\n{default_content}\n" + content[insert_point:]
            else:
                new_content = content + f"\n\n{section_name}\n{default_content}\n"
        else:
            return False, "Could not find insertion point"
    
    elif section_name == "## Side Effects":
        # Add after ## Outputs or ## Inputs
        if "## Outputs" in content:
            parts = content.split("## Outputs", 1)
            rest = parts[1]
            next_section_idx = rest.find("\n##")
            if next_section_idx > 0:
                insert_point = content.find("## Outputs") + next_section_idx + len("## Outputs")
                new_content = content[:insert_point] + f"\n\n{section_name}\n{default_content}\n" + content[insert_point:]
            else:
                # Add before ## Examples or Related Components
                if "## Examples" in content:
                    new_content = content.replace("## Examples", f"{section_name}\n{default_content}\n\n## Examples")
                elif "## Related" in content:
                    new_content = content.replace("## Related", f"{section_name}\n{default_content}\n\n## Related")
                else:
                    new_content = content + f"\n\n{section_name}\n{default_content}\n"
        elif "## Inputs" in content:
            parts = content.split("## Inputs", 1)
            rest = parts[1]
            next_section_idx = rest.find("\n##")
            if next_section_idx > 0:
                insert_point = content.find("## Inputs") + next_section_idx + len("## Inputs")
                new_content = content[:insert_point] + f"\n\n{section_name}\n{default_content}\n" + content[insert_point:]
            else:
                new_content = content + f"\n\n{section_name}\n{default_content}\n"
        else:
            return False, "Could not find insertion point"
    else:
        return False, f"Unknown section: {section_name}"
    
    filepath.write_text(new_content)
    return True, f"Added section: {section_name}"

def main():
    print("=" * 80)
    print("FINAL FIXES - Addressing Remaining Issues")
    print("=" * 80)
    print()
    
    fixes = {
        "frontmatter_fixed": 0,
        "sections_added": 0,
        "errors": 0
    }
    
    # Files needing checksum only
    checksum_files = [
        "careerspan-timeline-add.md",
        "careerspan-timeline.md"
    ]
    
    # Files needing multiple frontmatter fields
    multi_field_files = {
        "incantum-quickref.md": ["date", "checksum", "category", "priority"],
        "lists-health-check.md": ["date", "checksum", "category", "priority"]
    }
    
    # Files needing sections
    section_fixes = {
        "careerspan-timeline.md": ["## Side Effects"],
        "docgen-with-schedule-wrapper.md": ["## Inputs"],
        "docgen.md": ["## Inputs"],
        "git-audit.md": ["## Inputs", "## Side Effects"],
        "git-check.md": ["## Inputs", "## Side Effects"],
        "grep-search-command-creation.md": ["## Inputs"],
        "index-rebuild.md": ["## Inputs"],
        "index-update.md": ["## Inputs"],
        "knowledge-find.md": ["## Side Effects"],
        "lists-find.md": ["## Side Effects"],
        "system-timeline.md": ["## Side Effects"]
    }
    
    # Fix checksums
    print("📝 Adding missing checksums...")
    for filename in checksum_files:
        filepath = COMMANDS_DIR / filename
        if filepath.exists():
            success, msg = fix_missing_checksum(filepath)
            if success:
                print(f"  ✅ {filename}: {msg}")
                fixes["frontmatter_fixed"] += 1
            else:
                print(f"  ⏭️  {filename}: {msg}")
    
    print()
    
    # Fix multiple fields
    print("📝 Adding multiple frontmatter fields...")
    for filename, fields in multi_field_files.items():
        filepath = COMMANDS_DIR / filename
        if filepath.exists():
            success, msg = fix_missing_fields(filepath, fields)
            if success:
                print(f"  ✅ {filename}: {msg}")
                fixes["frontmatter_fixed"] += 1
            else:
                print(f"  ⏭️  {filename}: {msg}")
    
    print()
    
    # Fix missing sections
    print("📝 Adding missing sections...")
    for filename, sections in section_fixes.items():
        filepath = COMMANDS_DIR / filename
        if filepath.exists():
            for section in sections:
                try:
                    success, msg = add_missing_section(filepath, section, "(None)")
                    if success:
                        print(f"  ✅ {filename}: {msg}")
                        fixes["sections_added"] += 1
                    else:
                        print(f"  ⏭️  {filename}: {msg}")
                except Exception as e:
                    print(f"  ❌ {filename}: Error adding {section}: {e}")
                    fixes["errors"] += 1
    
    print()
    print("=" * 80)
    print(f"✅ Frontmatter fixes: {fixes['frontmatter_fixed']}")
    print(f"✅ Sections added: {fixes['sections_added']}")
    print(f"❌ Errors: {fixes['errors']}")
    print("=" * 80)

if __name__ == "__main__":
    main()
