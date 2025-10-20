#!/usr/bin/env python3
"""
N5 Emoji Legend Sync Script

Generates human-readable markdown documentation from the centralized
emoji-legend.json source of truth.

Usage:
    python3 n5_emoji_legend_sync.py
    python3 n5_emoji_legend_sync.py --dry-run
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
JSON_SOURCE = WORKSPACE / "N5/config/emoji-legend.json"
MD_OUTPUT = WORKSPACE / "N5/prefs/emoji-legend.md"


def load_emoji_legend() -> dict:
    """Load emoji legend JSON source."""
    try:
        with open(JSON_SOURCE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Source file not found: {JSON_SOURCE}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {JSON_SOURCE}: {e}")
        raise


def generate_markdown(data: dict) -> str:
    """Generate markdown documentation from emoji legend data."""
    lines = []
    
    # Header
    lines.append("# N5 Emoji Legend")
    lines.append("")
    lines.append(f"**Version:** {data['version']}  ")
    lines.append(f"**Last Updated:** {data['last_updated']}  ")
    lines.append(f"**Auto-generated from:** `file 'N5/config/emoji-legend.json'`")
    lines.append("")
    lines.append(f"> {data['description']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("- [Complete Emoji List](#complete-emoji-list)")
    lines.append("- [Emojis by Category](#emojis-by-category)")
    lines.append("- [Usage Contexts](#usage-contexts)")
    lines.append("- [Detection Priority](#detection-priority)")
    lines.append("- [Quick Reference](#quick-reference)")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Complete Emoji List
    lines.append("## Complete Emoji List")
    lines.append("")
    lines.append("| Emoji | Name | Category | Meaning | Contexts |")
    lines.append("|-------|------|----------|---------|----------|")
    
    for emoji in data["emojis"]:
        contexts = ", ".join(emoji["contexts"])
        lines.append(
            f"| {emoji['symbol']} | {emoji['name']} | "
            f"{emoji['category']} | {emoji['meaning']} | {contexts} |"
        )
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Detailed Descriptions
    lines.append("## Detailed Descriptions")
    lines.append("")
    
    for emoji in data["emojis"]:
        lines.append(f"### {emoji['symbol']} {emoji['name'].replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"**Category:** {emoji['category']}  ")
        lines.append(f"**Meaning:** {emoji['meaning']}  ")
        lines.append(f"**Priority:** {emoji['priority']}  ")
        lines.append(f"**Contexts:** {', '.join(emoji['contexts'])}")
        lines.append("")
        lines.append(f"**Usage Notes:**  ")
        lines.append(f"{emoji['usage_notes']}")
        lines.append("")
        lines.append(f"**Keywords:** {', '.join(emoji['keywords'])}")
        lines.append("")
        
        # Detection rules if present
        if emoji.get("detection_rules"):
            rules = emoji["detection_rules"]
            if rules.get("positive"):
                lines.append(f"**Detection (Positive):** {', '.join(rules['positive'])}")
            if rules.get("negative"):
                lines.append(f"**Detection (Negative):** {', '.join(rules['negative'])}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Emojis by Category
    lines.append("## Emojis by Category")
    lines.append("")
    
    for cat_name, cat_data in data["categories"].items():
        lines.append(f"### {cat_name.replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"{cat_data['description']}")
        lines.append("")
        
        # Find emojis in this category
        cat_emojis = [e for e in data["emojis"] if e["category"] == cat_name]
        for emoji in cat_emojis:
            lines.append(f"- {emoji['symbol']} **{emoji['name']}** - {emoji['meaning']}")
        
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Usage Contexts
    lines.append("## Usage Contexts")
    lines.append("")
    
    for ctx_name, ctx_data in data["usage_contexts"].items():
        lines.append(f"### {ctx_name.title()}")
        lines.append("")
        lines.append(f"{ctx_data['description']}")
        lines.append("")
        lines.append(f"**Priority Order:** {' → '.join(ctx_data['priority_order'])}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Detection Priority
    lines.append("## Detection Priority")
    lines.append("")
    lines.append("When auto-selecting emojis, higher priority values are checked first:")
    lines.append("")
    
    # Sort by priority (highest first)
    sorted_emojis = sorted(data["emojis"], key=lambda e: e["priority"], reverse=True)
    
    lines.append("| Priority | Emoji | Name | Category |")
    lines.append("|----------|-------|------|----------|")
    
    for emoji in sorted_emojis:
        lines.append(
            f"| {emoji['priority']} | {emoji['symbol']} | "
            f"{emoji['name']} | {emoji['category']} |"
        )
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Quick Reference
    lines.append("## Quick Reference")
    lines.append("")
    lines.append("### By Use Case")
    lines.append("")
    
    lines.append("#### Thread Status")
    status_emojis = [e for e in data["emojis"] if e["category"] == "status"]
    for emoji in status_emojis:
        lines.append(f"- {emoji['symbol']} {emoji['meaning']}")
    lines.append("")
    
    lines.append("#### Work Type")
    type_emojis = [e for e in data["emojis"] if e["category"] == "content_type"]
    for emoji in type_emojis:
        lines.append(f"- {emoji['symbol']} {emoji['meaning']}")
    lines.append("")
    
    lines.append("#### Actions")
    action_emojis = [e for e in data["emojis"] if e["category"] == "action"]
    for emoji in action_emojis:
        lines.append(f"- {emoji['symbol']} {emoji['meaning']}")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Footer
    lines.append("## Maintenance")
    lines.append("")
    lines.append("**To add/modify emojis:**")
    lines.append("1. Edit `file 'N5/config/emoji-legend.json'`")
    lines.append("2. Run `python3 N5/scripts/n5_emoji_legend_sync.py`")
    lines.append("3. This markdown file will be regenerated automatically")
    lines.append("")
    lines.append("**JSON Schema:**")
    lines.append("```json")
    lines.append("{")
    lines.append('  "symbol": "🔧",')
    lines.append('  "name": "system",')
    lines.append('  "category": "content_type",')
    lines.append('  "meaning": "System or infrastructure work",')
    lines.append('  "contexts": ["threads", "tasks"],')
    lines.append('  "keywords": ["system", "infrastructure"],')
    lines.append('  "priority": 40,')
    lines.append('  "usage_notes": "N5 system improvements",')
    lines.append('  "detection_rules": {')
    lines.append('    "positive": ["system", "N5"],')
    lines.append('    "negative": []')
    lines.append('  }')
    lines.append("}")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Auto-generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
    
    return "\n".join(lines)


def write_markdown(content: str, dry_run: bool = False) -> bool:
    """Write markdown content to output file."""
    if dry_run:
        logger.info("[DRY RUN] Would write to: %s", MD_OUTPUT)
        logger.info("[DRY RUN] Content preview (first 500 chars):")
        logger.info(content[:500])
        return True
    
    try:
        MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(MD_OUTPUT, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("✓ Wrote markdown to: %s", MD_OUTPUT)
        return True
    except Exception as e:
        logger.error(f"Failed to write markdown: {e}")
        return False


def verify_output() -> bool:
    """Verify the output file was created and is valid."""
    if not MD_OUTPUT.exists():
        logger.error("Output file does not exist: %s", MD_OUTPUT)
        return False
    
    size = MD_OUTPUT.stat().st_size
    if size == 0:
        logger.error("Output file is empty")
        return False
    
    logger.info("✓ Verified output: %s (%d bytes)", MD_OUTPUT, size)
    return True


def main(dry_run: bool = False) -> int:
    """Main execution."""
    try:
        logger.info("Loading emoji legend from: %s", JSON_SOURCE)
        data = load_emoji_legend()
        
        emoji_count = len(data["emojis"])
        logger.info("Loaded %d emojis", emoji_count)
        
        logger.info("Generating markdown documentation...")
        markdown = generate_markdown(data)
        
        logger.info("Writing markdown to: %s", MD_OUTPUT)
        if not write_markdown(markdown, dry_run=dry_run):
            return 1
        
        if not dry_run:
            if not verify_output():
                return 1
        
        logger.info("✓ Emoji legend sync complete!")
        logger.info("  Source: %s", JSON_SOURCE)
        logger.info("  Output: %s", MD_OUTPUT)
        logger.info("  Emojis: %d", emoji_count)
        
        return 0
        
    except Exception as e:
        logger.error("Error during sync: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync emoji legend JSON to markdown documentation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
