#!/usr/bin/env python3
"""
Recipe Index Builder
Scans Recipes/ directory and generates recipes.jsonl index

Usage:
    python3 recipe_index_builder.py [--dry-run] [--recipes-dir PATH] [--output PATH]

Features:
    - Parses YAML frontmatter from recipe markdown files
    - Generates machine-readable JSONL index
    - Validates required fields
    - Detects duplicates
    - Dry-run mode for safety
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def extract_frontmatter(content: str) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown content."""
    # Match YAML frontmatter between --- delimiters
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None
    
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error: {e}")
        return None


def extract_recipe_name(filepath: Path, frontmatter: Dict) -> str:
    """Extract or derive recipe name."""
    # Try frontmatter 'name' field first
    if frontmatter and 'name' in frontmatter:
        return frontmatter['name']
    
    # Fall back to filename (without .md extension)
    return filepath.stem


def process_recipe_file(filepath: Path, recipes_root: Path) -> Optional[Dict]:
    """Process a single recipe file and extract metadata."""
    try:
        content = filepath.read_text()
        frontmatter = extract_frontmatter(content)
        
        if not frontmatter:
            logger.warning(f"No frontmatter in {filepath.relative_to(recipes_root)}")
            frontmatter = {}
        
        # Extract name
        name = extract_recipe_name(filepath, frontmatter)
        
        # Build recipe entry
        recipe = {
            "name": name,
            "file": str(filepath.relative_to(recipes_root.parent)),  # Relative to workspace root
            "description": frontmatter.get('description', '').strip(),
            "tags": frontmatter.get('tags', []),
            "category": filepath.parent.name.lower(),  # e.g., "system", "knowledge"
        }
        
        # Optional fields
        if 'priority' in frontmatter:
            recipe['priority'] = frontmatter['priority']
        
        return recipe
        
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return None


def scan_recipes(recipes_dir: Path) -> List[Dict]:
    """Scan all recipe files and extract metadata."""
    recipes = []
    recipe_names = set()
    
    # Find all .md files (excluding README files)
    md_files = []
    for pattern in ['**/*.md', '*.md']:
        md_files.extend(recipes_dir.glob(pattern))
    
    md_files = [f for f in md_files if f.stem.lower() not in ['readme', 'index']]
    
    logger.info(f"Found {len(md_files)} recipe files")
    
    for filepath in sorted(md_files):
        recipe = process_recipe_file(filepath, recipes_dir)
        
        if recipe:
            # Check for duplicates
            if recipe['name'] in recipe_names:
                logger.warning(f"Duplicate recipe name: {recipe['name']}")
            
            recipe_names.add(recipe['name'])
            recipes.append(recipe)
    
    return recipes


def validate_recipes(recipes: List[Dict]) -> bool:
    """Validate recipe entries."""
    valid = True
    
    for recipe in recipes:
        # Check required fields
        if not recipe.get('name'):
            logger.error(f"Missing 'name' field in {recipe.get('file', 'unknown')}")
            valid = False
        
        if not recipe.get('file'):
            logger.error(f"Missing 'file' field for recipe {recipe.get('name', 'unknown')}")
            valid = False
        
        # Warn about missing descriptions
        if not recipe.get('description'):
            logger.warning(f"No description for recipe: {recipe['name']}")
    
    return valid


def write_index(recipes: List[Dict], output_path: Path, dry_run: bool = False) -> bool:
    """Write recipes to JSONL index file."""
    if dry_run:
        logger.info("[DRY RUN] Would write index to: %s", output_path)
        logger.info("[DRY RUN] Sample entries:")
        for recipe in recipes[:3]:
            logger.info("[DRY RUN]   %s", json.dumps(recipe, indent=2))
        return True
    
    try:
        with open(output_path, 'w') as f:
            for recipe in recipes:
                f.write(json.dumps(recipe) + '\n')
        
        logger.info(f"✓ Wrote {len(recipes)} recipes to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing index: {e}")
        return False


def verify_output(output_path: Path, expected_count: int) -> bool:
    """Verify the output file was created correctly."""
    if not output_path.exists():
        logger.error(f"Output file not created: {output_path}")
        return False
    
    try:
        with open(output_path) as f:
            actual_count = sum(1 for _ in f)
        
        if actual_count != expected_count:
            logger.error(f"Count mismatch: expected {expected_count}, got {actual_count}")
            return False
        
        logger.info(f"✓ Verified: {actual_count} recipes in index")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying output: {e}")
        return False


def main(
    recipes_dir: Path,
    output_path: Path,
    dry_run: bool = False
) -> int:
    """Main execution."""
    try:
        logger.info(f"Scanning recipes in: {recipes_dir}")
        
        if not recipes_dir.exists():
            logger.error(f"Recipes directory not found: {recipes_dir}")
            return 1
        
        # Scan and process recipes
        recipes = scan_recipes(recipes_dir)
        
        if not recipes:
            logger.warning("No recipes found")
            return 1
        
        # Validate
        if not validate_recipes(recipes):
            logger.error("Validation failed")
            return 1
        
        # Write index
        if not write_index(recipes, output_path, dry_run=dry_run):
            return 1
        
        # Verify (if not dry-run)
        if not dry_run:
            if not verify_output(output_path, len(recipes)):
                return 1
        
        logger.info(f"✓ Recipe index build complete: {len(recipes)} recipes")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build recipe index from Recipes/ directory")
    parser.add_argument(
        '--recipes-dir',
        type=Path,
        default=Path('/home/workspace/Recipes'),
        help='Path to Recipes directory (default: /home/workspace/Recipes)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('/home/workspace/Recipes/recipes.jsonl'),
        help='Output path for recipes.jsonl (default: /home/workspace/Recipes/recipes.jsonl)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without writing files'
    )
    
    args = parser.parse_args()
    
    sys.exit(main(
        recipes_dir=args.recipes_dir,
        output_path=args.output,
        dry_run=args.dry_run
    ))
