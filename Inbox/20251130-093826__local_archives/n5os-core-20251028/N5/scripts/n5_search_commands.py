#!/usr/bin/env python3
"""
N5 Command Search Tool

Search the command registry (commands.jsonl) by keyword, category, or description.
Returns matching commands with their details.

Usage:
    n5_search_commands.py <keyword> [--category CATEGORY] [--dry-run]

Examples:
    n5_search_commands.py list
    n5_search_commands.py meeting --category careerspan
    n5_search_commands.py export --dry-run
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
WORKSPACE_ROOT = Path("/home/workspace")
COMMANDS_REGISTRY = WORKSPACE_ROOT / "N5/config/commands.jsonl"


def load_commands_registry() -> List[Dict]:
    """Load commands from commands.jsonl."""
    if not COMMANDS_REGISTRY.exists():
        logger.error(f"Commands registry not found: {COMMANDS_REGISTRY}")
        return []
    
    commands = []
    with open(COMMANDS_REGISTRY, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                commands.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON on line {line_num}: {e}")
    
    logger.info(f"Loaded {len(commands)} commands from registry")
    return commands


def search_commands(
    commands: List[Dict],
    keyword: str,
    category: str = None
) -> List[Dict]:
    """
    Search commands by keyword in command name, description, or file.
    Optionally filter by category.
    
    Args:
        commands: List of command dictionaries
        keyword: Search term (case-insensitive)
        category: Optional category filter
    
    Returns:
        List of matching command dictionaries
    """
    keyword_lower = keyword.lower()
    results = []
    
    for cmd in commands:
        # Category filter
        if category and cmd.get('category', '').lower() != category.lower():
            continue
        
        # Keyword search in command name, description, file
        matches = any([
            keyword_lower in cmd.get('command', '').lower(),
            keyword_lower in cmd.get('description', '').lower(),
            keyword_lower in cmd.get('file', '').lower(),
            keyword_lower in cmd.get('workflow', '').lower()
        ])
        
        if matches:
            results.append(cmd)
    
    return results


def format_results(results: List[Dict]) -> str:
    """Format search results for display."""
    if not results:
        return "No matching commands found."
    
    output = [f"\n✅ Found {len(results)} matching command(s):\n"]
    
    for i, cmd in enumerate(results, 1):
        output.append(f"{i}. {cmd.get('command', 'UNKNOWN')}")
        output.append(f"   Description: {cmd.get('description', 'N/A')}")
        output.append(f"   Category: {cmd.get('category', 'N/A')}")
        output.append(f"   File: {cmd.get('file', 'N/A')}")
        
        if cmd.get('script'):
            output.append(f"   Script: {cmd.get('script')}")
        
        if cmd.get('workflow'):
            output.append(f"   Workflow: {cmd.get('workflow')}")
        
        output.append("")  # Blank line between results
    
    return "\n".join(output)


def main(keyword: str, category: str = None, dry_run: bool = False) -> int:
    """
    Main execution function.
    
    Args:
        keyword: Search term
        category: Optional category filter
        dry_run: If True, show what would be searched without executing
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        if dry_run:
            logger.info("[DRY RUN] Would search commands with:")
            logger.info(f"  Keyword: {keyword}")
            if category:
                logger.info(f"  Category: {category}")
            logger.info(f"  Registry: {COMMANDS_REGISTRY}")
            return 0
        
        # Load commands
        commands = load_commands_registry()
        if not commands:
            logger.error("No commands loaded from registry")
            return 1
        
        # Search
        logger.info(f"Searching for: '{keyword}'" + (f" (category: {category})" if category else ""))
        results = search_commands(commands, keyword, category)
        
        # Format and print results
        output = format_results(results)
        print(output)
        
        logger.info(f"✓ Search complete: {len(results)} result(s)")
        return 0
    
    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search N5 command registry by keyword"
    )
    parser.add_argument(
        "keyword",
        help="Search term (searches command name, description, file)"
    )
    parser.add_argument(
        "--category",
        help="Filter by category (system, careerspan, core, etc.)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be searched without executing"
    )
    
    args = parser.parse_args()
    sys.exit(main(
        keyword=args.keyword,
        category=args.category,
        dry_run=args.dry_run
    ))
