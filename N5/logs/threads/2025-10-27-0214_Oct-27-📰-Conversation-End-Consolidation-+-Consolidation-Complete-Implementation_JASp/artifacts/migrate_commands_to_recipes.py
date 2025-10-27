#!/usr/bin/env python3
"""
Migrate N5/commands/ → Recipes/

Converts command files to recipe format and organizes into categories.
"""

import argparse
import json
import logging
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Category mapping from analysis
CATEGORY_MAPPING = {
    "System": ["system", "n5", "core", "hygiene", "state-session", "file", "git", "quality", "index", "orchestrator", "grep"],
    "Knowledge": ["knowledge", "research", "digest", "lessons", "content"],
    "Meetings": ["meeting", "meetings", "transcript"],
    "Tools": ["akiflow", "howie", "linkedin", "social-media", "streaming", "communication"],
    "Business": ["careerspan", "crm", "deliverables", "jobs", "networking", "intros"],
    "Productivity": ["lists", "build", "coordination", "flow", "threads", "quick", "personal", "strategic", "docgen", "documentation", "direct"]
}

def get_recipe_category(command_category: str) -> str:
    """Map command category to recipe category."""
    for recipe_cat, command_cats in CATEGORY_MAPPING.items():
        if command_category.lower() in command_cats:
            return recipe_cat
    return "Productivity"  # Default


def extract_frontmatter(content: str) -> tuple[Optional[Dict], str]:
    """Extract YAML frontmatter and remaining content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return None, content
    
    try:
        fm = yaml.safe_load(match.group(1))
        return fm, match.group(2)
    except yaml.YAMLError as e:
        logger.warning(f"YAML parse error: {e}")
        return None, content


def extract_summary(content: str) -> Optional[str]:
    """Extract summary from content."""
    # Try to find **Summary:** line
    match = re.search(r'\*\*Summary\*\*:\s*(.+?)(?:\n|$)', content)
    if match:
        return match.group(1).strip()
    
    # Try ## Purpose section
    match = re.search(r'## Purpose\s*\n+(.+?)(?:\n\n|\n##|$)', content, re.DOTALL)
    if match:
        first_line = match.group(1).split('\n')[0].strip()
        if first_line and len(first_line) < 200:
            return first_line
    
    return None


def convert_to_recipe_format(
    filepath: Path,
    commands_metadata: Dict,
    dry_run: bool = False
) -> Optional[tuple[str, str, str]]:
    """
    Convert command file to recipe format.
    
    Returns: (recipe_content, recipe_category, recipe_name)
    """
    try:
        content = filepath.read_text()
        frontmatter, body = extract_frontmatter(content)
        
        # Get command metadata from commands.jsonl
        cmd_name = filepath.stem
        cmd_metadata = commands_metadata.get(cmd_name, {})
        
        # Determine category
        command_category = cmd_metadata.get('category', frontmatter.get('category', 'uncategorized') if frontmatter else 'uncategorized')
        recipe_category = get_recipe_category(command_category)
        
        # Extract description
        description = cmd_metadata.get('summary', '')
        if not description:
            description = extract_summary(content)
        if not description and frontmatter:
            description = frontmatter.get('summary', '')
        
        # Extract tags
        tags = []
        if frontmatter and 'tags' in frontmatter:
            tags = frontmatter['tags']
        elif cmd_metadata.get('tags'):
            tags = cmd_metadata['tags']
        
        # Build new frontmatter
        new_frontmatter = {
            'description': description or f"Command: {cmd_name}",
            'tags': tags if isinstance(tags, list) else [tags] if tags else []
        }
        
        # Build recipe content
        recipe_content = "---\n"
        recipe_content += yaml.dump(new_frontmatter, default_flow_style=False, allow_unicode=True)
        recipe_content += "---\n"
        recipe_content += body
        
        # Use Title Case for recipe name
        recipe_name = filepath.stem.replace('-', ' ').replace('_', ' ').title()
        
        return recipe_content, recipe_category, recipe_name
        
    except Exception as e:
        logger.error(f"Error converting {filepath}: {e}")
        return None


def migrate_commands(
    commands_dir: Path,
    recipes_dir: Path,
    commands_metadata: Dict,
    dry_run: bool = False
) -> tuple[int, int]:
    """Migrate all command files to recipes. Returns (success_count, total_count)."""
    md_files = [f for f in commands_dir.glob('*.md') if f.stem.lower() != 'readme']
    
    success_count = 0
    skipped = []
    
    for filepath in sorted(md_files):
        result = convert_to_recipe_format(filepath, commands_metadata, dry_run)
        
        if not result:
            logger.warning(f"Skipping {filepath.name}")
            skipped.append(filepath.name)
            continue
        
        recipe_content, recipe_category, recipe_name = result
        
        # Create target directory
        target_dir = recipes_dir / recipe_category
        target_file = target_dir / f"{recipe_name}.md"
        
        if dry_run:
            logger.info(f"[DRY RUN] {filepath.name} → {recipe_category}/{recipe_name}.md")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file.write_text(recipe_content)
            logger.info(f"✓ {filepath.name} → {recipe_category}/{recipe_name}.md")
        
        success_count += 1
    
    if skipped:
        logger.warning(f"Skipped {len(skipped)} files: {', '.join(skipped[:5])}")
    
    return success_count, len(md_files)


def main(dry_run: bool = False) -> int:
    """Main execution."""
    try:
        commands_dir = Path('/home/workspace/N5/commands')
        recipes_dir = Path('/home/workspace/Recipes')
        metadata_file = Path('/home/.z/workspaces/con_qOw8I8BPDrF3JASp/commands_metadata_staging.jsonl')
        
        # Load commands metadata
        logger.info("Loading commands metadata...")
        commands_metadata = {}
        with open(metadata_file) as f:
            for line in f:
                cmd = json.loads(line)
                commands_metadata[cmd['command']] = cmd
        
        logger.info(f"Loaded {len(commands_metadata)} command metadata entries")
        
        # Migrate
        logger.info(f"Migrating from {commands_dir} to {recipes_dir}...")
        success, total = migrate_commands(commands_dir, recipes_dir, commands_metadata, dry_run)
        
        logger.info(f"✓ Migration complete: {success}/{total} files migrated")
        
        if not dry_run:
            # Run recipe index builder
            logger.info("Building recipe index...")
            import subprocess
            result = subprocess.run(
                ['python3', '/home/workspace/N5/scripts/recipe_index_builder.py'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✓ Recipe index built successfully")
            else:
                logger.error(f"Recipe index builder failed: {result.stderr}")
                return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate commands to recipes")
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run))
