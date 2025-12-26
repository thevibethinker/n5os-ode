#!/usr/bin/env python3
"""
Extract Organizations Script
Scans Knowledge/crm/individuals/*.md for 'organization' frontmatter.
Creates corresponding profiles in Knowledge/crm/organizations/ if they don't exist.
Updates organization profiles with links to individuals.
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

# Configuration
INDIVIDUALS_DIR = Path("/home/workspace/Knowledge/crm/individuals")
ORGANIZATIONS_DIR = Path("/home/workspace/Knowledge/crm/organizations")
TEMPLATE_FILE = ORGANIZATIONS_DIR / "TEMPLATE.md"

def slugify(text):
    """Convert text to kebab-case slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text.strip('-')

def load_frontmatter(file_path):
    """Extract YAML frontmatter from a markdown file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

def create_org_file(org_name, individuals_list):
    """Create a new organization file from template."""
    slug = slugify(org_name)
    file_path = ORGANIZATIONS_DIR / f"{slug}.md"
    
    if file_path.exists():
        return False, "Exists"

    today = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
name: "{org_name}"
domain: ""
industry: ""
stage: ""
status: "active"
created: "{today}"
last_updated: "{today}"
version: "1.0"
---

# {org_name}

**Domain:**   
**Industry:**   
**Stage:**   
**Status:** Active  

---

## Overview

Auto-extracted from individual profiles.

---

## Team

### Key Contacts
"""
    
    for ind in individuals_list:
        name = ind.get('name', 'Unknown')
        path = ind.get('path', '')
        role = ind.get('role', '')
        rel_path = os.path.relpath(path, start=ORGANIZATIONS_DIR)
        content += f"- [{name}]({rel_path}) - {role}\n"

    content += """
### All Associated Individuals
*Auto-generated list of individuals linking to this org*

---

## Relationships

**Type:**   
**Key Stakeholder:**   

---

## Intelligence

**Recent News:**

**Strategic Alignment:**

---

## Notes

- Auto-generated organization profile.
"""

    with open(file_path, 'w') as f:
        f.write(content)
    
    return True, file_path

def main():
    print("Scanning individuals for organizations...")
    
    org_map = {}
    
    # 1. Scan individuals
    for file_path in INDIVIDUALS_DIR.glob("*.md"):
        fm = load_frontmatter(file_path)
        if not fm:
            continue
            
        org_name = fm.get('organization')
        if not org_name:
            continue
            
        # Normalize org name (basic)
        org_key = org_name.strip()
        
        if org_key not in org_map:
            org_map[org_key] = []
            
        org_map[org_key].append({
            'name': fm.get('name', file_path.stem),
            'role': fm.get('role', ''),
            'path': str(file_path)
        })

    print(f"Found {len(org_map)} unique organizations.")
    
    # 2. Create organization files
    created_count = 0
    skipped_count = 0
    
    for org_name, individuals in org_map.items():
        if not org_name or org_name.lower() in ['unknown', 'none', 'n/a', 'to be determined']:
            continue
            
        success, result = create_org_file(org_name, individuals)
        if success:
            print(f"Created: {result}")
            created_count += 1
        else:
            skipped_count += 1
            
    print(f"\nSummary:")
    print(f"Created {created_count} new organization profiles.")
    print(f"Skipped {skipped_count} existing profiles.")

if __name__ == "__main__":
    main()

