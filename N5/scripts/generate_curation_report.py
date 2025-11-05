#!/usr/bin/env python3
"""
Knowledge System V4 - Generate Curation Report
Aggregates pending intelligence extracts into weekly curation report for V's review.

Input: Knowledge/intelligence/extracts/*.yaml (status: pending_review)
Output: Knowledge/intelligence/WEEKLY_CURATION_REPORT_{date}.md
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

WORKSPACE = Path("/home/workspace")
INTELLIGENCE_DIR = WORKSPACE / "Knowledge" / "intelligence"
EXTRACTS_DIR = INTELLIGENCE_DIR / "extracts"


def load_pending_extracts() -> List[Dict[str, Any]]:
    """
    Load all pending YAML extracts.
    
    Returns list of dicts with 'data' (parsed YAML) and 'file' (Path).
    """
    if not EXTRACTS_DIR.exists():
        logging.warning(f"Extracts directory not found: {EXTRACTS_DIR}")
        return []
    
    extracts = []
    
    for yaml_file in EXTRACTS_DIR.glob("*.yaml"):
        try:
            with yaml_file.open() as f:
                data = yaml.safe_load(f)
            
            # Only include pending items
            if data.get("status") == "pending_review":
                extracts.append({
                    "data": data,
                    "file": yaml_file,
                })
                logging.info(f"Loaded pending extract: {yaml_file.name}")
        
        except Exception as e:
            logging.error(f"Failed to load {yaml_file}: {e}")
    
    return extracts


def sort_extracts(extracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort extracts by:
    1. Priority (high → medium → low)
    2. Confidence (high → low within each priority)
    3. Date (newest first)
    """
    priority_map = {"high": 3, "medium": 2, "low": 1}
    
    def sort_key(item):
        data = item["data"]
        tags = data.get("tags", {})
        priority = tags.get("priority", "medium")
        confidence = data.get("confidence", 0)
        captured_at = data.get("captured_at", "")
        
        return (
            -priority_map.get(priority, 2),  # Negative for descending
            -confidence,  # Negative for descending
            -ord(captured_at[0]) if captured_at else 0,  # Newest first
        )
    
    return sorted(extracts, key=sort_key)


def format_item(item: Dict[str, Any], index: int) -> str:
    """Format single intelligence item for report."""
    data = item["data"]
    content = data.get("content", {})
    tags = data.get("tags", {})
    routing = data.get("knowledge_routing", {})
    entity = data.get("entity", {})
    metadata = data.get("metadata", {})
    
    # Build item text
    lines = []
    lines.append(f"### Item {index}: {', '.join(data.get('intelligence_type', []))}")
    lines.append(f"**Source:** {data.get('source_type', 'unknown').capitalize()} - {data.get('source_id', 'unknown')}")
    lines.append(f"**Confidence:** {data.get('confidence', 0):.2f}")
    lines.append(f"**Entity:** {entity.get('type', 'concept')} - {entity.get('name', 'unknown')}")
    lines.append("")
    
    # Content
    lines.append("**Content:**")
    if content.get("quote"):
        lines.append(f"> \"{content['quote']}\"")
        lines.append("")
    
    lines.append(f"**Summary:** {content.get('summary', 'N/A')}")
    lines.append("")
    
    if content.get("details"):
        lines.append(f"**Details:** {content['details']}")
        lines.append("")
    
    if content.get("implications"):
        lines.append(f"**Implications:** {content['implications']}")
        lines.append("")
    
    # Tags
    domains = tags.get("domain", [])
    purpose = tags.get("purpose", [])
    if domains or purpose:
        lines.append(f"**Tags:**")
        if domains:
            lines.append(f"- Domain: {', '.join(domains)}")
        if purpose:
            lines.append(f"- Purpose: {', '.join(purpose)}")
        lines.append("")
    
    # Routing
    target = routing.get("target", "unknown")
    section = routing.get("section", "")
    lines.append(f"**Proposed Routing:** `{target}`")
    if section:
        lines.append(f"- Section: \"{section}\"")
    lines.append("")
    
    # Decision prompt
    lines.append("**Your Decision:**")
    lines.append("- [A] Approve - Write to proposed target")
    lines.append("- [R] Reject - Move to rejected/")
    lines.append("- [M] Modify routing - Specify new target")
    lines.append("- [S] Skip - Review next week")
    lines.append("")
    lines.append(f"**Response:** ___")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def generate_report(extracts: List[Dict[str, Any]]) -> str:
    """Generate full markdown report."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Group by priority
    high_priority = [e for e in extracts if e["data"].get("tags", {}).get("priority") == "high"]
    medium_priority = [e for e in extracts if e["data"].get("tags", {}).get("priority") == "medium"]
    low_priority = [e for e in extracts if e["data"].get("tags", {}).get("priority") == "low"]
    
    # Count sources
    source_counts = {}
    for e in extracts:
        source_type = e["data"].get("source_type", "unknown")
        source_counts[source_type] = source_counts.get(source_type, 0) + 1
    
    # Build report
    lines = []
    lines.append("---")
    lines.append(f"created: {today}")
    lines.append(f"last_edited: {today}")
    lines.append("version: 1.0")
    lines.append("---")
    lines.append("")
    lines.append(f"# Knowledge Curation Report: Week of {today}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- **Total Items:** {len(extracts)}")
    lines.append(f"- **High Priority:** {len(high_priority)}")
    lines.append(f"- **Medium Priority:** {len(medium_priority)}")
    lines.append(f"- **Low Priority:** {len(low_priority)}")
    
    source_strs = [f"{count} {source}" for source, count in source_counts.items()]
    lines.append(f"- **Sources:** {', '.join(source_strs)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # High priority items
    if high_priority:
        lines.append("## High-Priority Items (Review First)")
        lines.append("")
        for idx, item in enumerate(high_priority, start=1):
            lines.append(format_item(item, idx))
    
    # Medium priority items
    if medium_priority:
        lines.append("## Medium-Priority Items")
        lines.append("")
        start_idx = len(high_priority) + 1
        for idx, item in enumerate(medium_priority, start=start_idx):
            lines.append(format_item(item, idx))
    
    # Low priority items
    if low_priority:
        lines.append("## Low-Priority Items")
        lines.append("")
        start_idx = len(high_priority) + len(medium_priority) + 1
        for idx, item in enumerate(low_priority, start=start_idx):
            # Shorter format for low priority
            data = item["data"]
            content = data.get("content", {})
            lines.append(f"### Item {idx}: {content.get('summary', 'N/A')}")
            lines.append(f"**Source:** {data.get('source_type', 'unknown')} | **Confidence:** {data.get('confidence', 0):.2f}")
            lines.append(f"**Response:** ___")
            lines.append("")
    
    # Instructions
    lines.append("---")
    lines.append("")
    lines.append("## Instructions")
    lines.append("")
    lines.append("Reply to this report with your decisions in format:")
    lines.append("```")
    lines.append("1: A")
    lines.append("2: M Knowledge/stable/company/strategy.md")
    lines.append("3: R")
    lines.append("4: A")
    lines.append("5: S")
    lines.append("...")
    lines.append("```")
    lines.append("")
    lines.append("Or simply mark inline above and save file.")
    lines.append("Script will process your responses and execute.")
    lines.append("")
    
    return "\n".join(lines)


def main(dry_run: bool = False) -> int:
    """Main execution."""
    try:
        logging.info(f"Starting curation report generation (dry_run={dry_run})")
        
        # Load pending extracts
        extracts = load_pending_extracts()
        
        if not extracts:
            logging.warning("No pending extracts found")
            print("No pending intelligence items to curate.")
            return 0
        
        logging.info(f"Found {len(extracts)} pending extracts")
        
        # Sort extracts
        sorted_extracts = sort_extracts(extracts)
        
        # Generate report
        report_text = generate_report(sorted_extracts)
        
        # Write report
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = INTELLIGENCE_DIR / f"WEEKLY_CURATION_REPORT_{today}.md"
        
        if dry_run:
            logging.info("DRY RUN: Would write report to {report_path}")
            print("\n" + "="*80)
            print(report_text[:2000])  # Preview first 2000 chars
            print("...\n(truncated for preview)")
            print("="*80)
            return 0
        
        report_path.write_text(report_text)
        logging.info(f"✓ Report written: {report_path}")
        print(f"Curation report generated: {report_path}")
        return 0
        
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate weekly knowledge curation report")
    parser.add_argument("--dry-run", action="store_true", help="Preview but don't write report")
    
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
