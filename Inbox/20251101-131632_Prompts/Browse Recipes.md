---
description: |
  Browse, search, and discover available recipes.
  Shows recipe descriptions, tags, and usage patterns.
tags:
  - recipes
  - discovery
  - system
tool: true
---
# Browse Recipes

Discover and explore all available recipes in your N5 system.

## What This Does

Lists all recipes with their descriptions, tags, and file references. Helps you find the right workflow for your needs.

## What Happens

1. **Scan Recipes Directory**
   - Recursively find all .md files in `/home/workspace/Prompts/` including subdirectories
   - Extract frontmatter (description, tags)

2. **Parse & Organize**
   - Parse description and tags
   - Group by category (subdirectory)
   - Show recipe name, description, category, and primary tags

3. **Display**
   - Organized by category: Meetings, Knowledge, System, Tools
   - Searchable by name, tag, or description
   - Show file path for reference

## Usage

Simply invoke this recipe via `/browse-recipes` or ask "show me available recipes"

## Instructions

1. **List all recipes:**
   ```bash
   ls -1 /home/workspace/Prompts/*.md
   ```

2. **Extract frontmatter from each recipe:**
   - Use `head -n 20` to get YAML frontmatter
   - Parse description and tags
   - Show recipe name, description, and primary tags

3. **Organize by category:**
   - Group by primary tag if helpful
   - Or show alphabetically
   - Include file path for reference

4. **Display format:**
   ```
   ## Recipe Name
   **Description:** Brief description here
   **Tags:** tag1, tag2, tag3
   **Invoke:** /recipe-name
   **File:** file 'Prompts/Recipe Name.md'
   ```

5. **Offer search:** Ask if V wants to filter by tag or keyword

## Output

Comprehensive list of available recipes with metadata for easy discovery.

## Related

- Type `/` in Zo chat for native autocomplete
- `file 'Documents/N5.md'` for system overview
- `file '/home/.z/workspaces/con_uVnpAD6W1XKczbee/RECIPES_ALIGNMENT_GUIDE.md'` for architecture
