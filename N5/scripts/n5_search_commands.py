#!/usr/bin/env python3
"""
N5 Command Search Tool

Search the command registry (executables.db) by keyword, category, or description.
Returns matching commands with their details.

Usage:
    n5_search_commands.py <keyword> [--category CATEGORY] [--type TYPE] [--dry-run]

Examples:
    n5_search_commands.py list
    n5_search_commands.py meeting --category careerspan
    n5_search_commands.py export --type script
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

# Add N5/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from executable_manager import search_executables, list_executables, Executable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def filter_by_criteria(
    executables: List[Executable],
    category: str = None,
    exec_type: str = None
) -> List[Executable]:
    """
    Filter executables by category and/or type.
    
    Args:
        executables: List of Executable objects
        category: Optional category filter
        exec_type: Optional type filter (prompt, script, tool)
    
    Returns:
        Filtered list of Executable objects
    """
    results = executables
    
    if category:
        results = [e for e in results if e.category and category.lower() in e.category.lower()]
    
    if exec_type:
        results = [e for e in results if e.type and exec_type.lower() == e.type.lower()]
    
    return results


def format_results(results: List[Executable]) -> str:
    """Format search results for display."""
    if not results:
        return "No matching commands found."
    
    output = [f"\n✅ Found {len(results)} matching executable(s):\n"]
    
    for i, exe in enumerate(results, 1):
        output.append(f"{i}. {exe.name}")
        output.append(f"   ID: {exe.id}")
        output.append(f"   Type: {exe.type}")
        output.append(f"   Description: {exe.description or 'N/A'}")
        output.append(f"   Category: {exe.category or 'N/A'}")
        output.append(f"   File: {exe.file_path}")
        output.append(f"   Version: {exe.version}")
        
        if exe.tags:
            output.append(f"   Tags: {', '.join(exe.tags)}")
        
        output.append("")  # Blank line between results
    
    return "\n".join(output)


def main(keyword: str, category: str = None, exec_type: str = None, dry_run: bool = False) -> int:
    """
    Main execution function.
    
    Args:
        keyword: Search term
        category: Optional category filter
        exec_type: Optional type filter (prompt, script, tool)
        dry_run: If True, show what would be searched without executing
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        if dry_run:
            logger.info("[DRY RUN] Would search executables with:")
            logger.info(f"  Keyword: {keyword}")
            if category:
                logger.info(f"  Category: {category}")
            if exec_type:
                logger.info(f"  Type: {exec_type}")
            return 0
        
        # Search using full-text search from executable_manager
        logger.info(f"Searching for: '{keyword}'" + 
                   (f" (category: {category})" if category else "") +
                   (f" (type: {exec_type})" if exec_type else ""))
        
        results = search_executables(keyword)
        
        # Apply additional filters if specified
        if category or exec_type:
            results = filter_by_criteria(results, category, exec_type)
        
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
        description="Search N5 executable registry by keyword"
    )
    parser.add_argument(
        "keyword",
        help="Search term (searches name, description, tags using FTS)"
    )
    parser.add_argument(
        "--category",
        help="Filter by category (system, careerspan, core, etc.)"
    )
    parser.add_argument(
        "--type",
        dest="exec_type",
        help="Filter by type (prompt, script, tool)"
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
        exec_type=args.exec_type,
        dry_run=args.dry_run
    ))
