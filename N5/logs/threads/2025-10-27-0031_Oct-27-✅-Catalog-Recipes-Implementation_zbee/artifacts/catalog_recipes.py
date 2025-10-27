#!/usr/bin/env python3
import re
from pathlib import Path

recipes_dir = Path("/home/workspace/Recipes")
recipes = []

for md_file in sorted(recipes_dir.glob("*.md")):
    with open(md_file, 'r') as f:
        content = f.read()
        
    # Extract frontmatter
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    description = "No description"
    tags = []
    
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        desc_match = re.search(r'description:\s*\|?\s*(.*?)(?=\ntags:|---|\Z)', fm, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip().replace('\n', ' ')
        
        tags_match = re.search(r'tags:\s*\n((?:  - .*\n?)*)', fm)
        if tags_match:
            tags = [line.strip('- ').strip() for line in tags_match.group(1).split('\n') if line.strip()]
    
    recipes.append({
        'name': md_file.stem,
        'file': md_file.name,
        'description': description[:100] + ('...' if len(description) > 100 else ''),
        'tags': tags[:3]
    })

# Print results
print(f"# Available Recipes ({len(recipes)} total)\n")
for r in recipes:
    print(f"## {r['name']}")
    print(f"**Description:** {r['description']}")
    if r['tags']:
        print(f"**Tags:** {', '.join(r['tags'])}")
    print(f"**File:** `Recipes/{r['file']}`\n")
