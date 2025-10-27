#!/usr/bin/env python3
"""
Inbox Review Generator
Creates human-readable REVIEW.md from analysis results
"""
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
INBOX_PATH = WORKSPACE_ROOT / "Inbox"
CONFIG_PATH = WORKSPACE_ROOT / "N5/config/routing_config.json"
ANALYSIS_LOG_PATH = WORKSPACE_ROOT / "N5/logs/.inbox_analysis.jsonl"
REVIEW_PATH = INBOX_PATH / "REVIEW.md"


def load_config() -> dict:
    """Load routing configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_unrouted_analyses() -> list:
    """Load analyses for unrouted files."""
    if not ANALYSIS_LOG_PATH.exists():
        return []
    
    analyses = {}
    with open(ANALYSIS_LOG_PATH) as f:
        for line in f:
            entry = json.loads(line)
            filepath = entry["file_path"]
            # Keep most recent analysis per file
            if filepath not in analyses or entry["timestamp"] > analyses[filepath]["timestamp"]:
                analyses[filepath] = entry
    
    # Filter for unrouted only
    unrouted = [a for a in analyses.values() if not a.get("routed", False)]
    
    # Sort by action priority: manual_only, suggest, auto_route
    action_priority = {"manual_only": 0, "suggest": 1, "auto_route": 2}
    unrouted.sort(key=lambda a: (action_priority.get(a["action"], 3), a["timestamp"]))
    
    return unrouted


def check_ttl_exceeded(filepath: Path, ttl_days: int) -> bool:
    """Check if file has exceeded TTL in Inbox."""
    if not filepath.exists():
        return False
    
    created = datetime.fromtimestamp(filepath.stat().st_ctime)
    age_days = (datetime.now() - created).days
    return age_days > ttl_days


def format_size(bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"


def generate_review(dry_run: bool = False) -> dict:
    """Generate REVIEW.md file."""
    config = load_config()
    analyses = load_unrouted_analyses()
    
    if not analyses:
        logger.info("No unrouted files to review")
        return {"total": 0, "by_action": {}}
    
    # Group by action
    by_action = {
        "auto_route": [],
        "suggest": [],
        "manual_only": []
    }
    
    for analysis in analyses:
        action = analysis["action"]
        by_action[action].append(analysis)
    
    # Build markdown
    lines = []
    lines.append("# Inbox Review")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}")
    lines.append(f"**Total Items:** {len(analyses)}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Auto-route ready:** {len(by_action['auto_route'])} (≥85% confidence)")
    lines.append(f"- **Suggested routing:** {len(by_action['suggest'])} (60-84% confidence)")
    lines.append(f"- **Manual review needed:** {len(by_action['manual_only'])} (<60% confidence)")
    lines.append("")
    
    # TTL warnings
    ttl_exceeded = []
    for analysis in analyses:
        filepath = Path(analysis["file_path"])
        if check_ttl_exceeded(filepath, config["inbox_ttl_days"]):
            ttl_exceeded.append(filepath.name)
    
    if ttl_exceeded:
        lines.append("## ⚠️ TTL Exceeded")
        lines.append("")
        lines.append(f"The following files have been in Inbox for >{config['inbox_ttl_days']} days:")
        lines.append("")
        for filename in ttl_exceeded:
            lines.append(f"- `{filename}`")
        lines.append("")
    
    # Auto-route section
    if by_action["auto_route"]:
        lines.append("## ✅ Auto-Route Ready (High Confidence)")
        lines.append("")
        lines.append("These files will be automatically routed on next run:")
        lines.append("")
        
        for analysis in by_action["auto_route"]:
            filepath = Path(analysis["file_path"])
            lines.append(f"### `{filepath.name}`")
            lines.append(f"- **Destination:** `{analysis['destination']}`")
            lines.append(f"- **Confidence:** {analysis['confidence']:.0%}")
            lines.append(f"- **Size:** {format_size(analysis['size_bytes'])}")
            lines.append(f"- **Reasoning:** {analysis['reasoning']}")
            lines.append("")
    
    # Suggested section
    if by_action["suggest"]:
        lines.append("## 💡 Suggested Routing (Medium Confidence)")
        lines.append("")
        lines.append("Review these suggestions and manually route:")
        lines.append("")
        
        for analysis in by_action["suggest"]:
            filepath = Path(analysis["file_path"])
            lines.append(f"### `{filepath.name}`")
            lines.append(f"- **Suggested:** `{analysis['destination']}`")
            lines.append(f"- **Confidence:** {analysis['confidence']:.0%}")
            lines.append(f"- **Size:** {format_size(analysis['size_bytes'])}")
            lines.append(f"- **Reasoning:** {analysis['reasoning']}")
            lines.append("")
    
    # Manual section
    if by_action["manual_only"]:
        lines.append("## ❓ Manual Review Required (Low Confidence)")
        lines.append("")
        lines.append("These files need human classification:")
        lines.append("")
        
        for analysis in by_action["manual_only"]:
            filepath = Path(analysis["file_path"])
            lines.append(f"### `{filepath.name}`")
            lines.append(f"- **Best guess:** `{analysis['destination']}`")
            lines.append(f"- **Confidence:** {analysis['confidence']:.0%}")
            lines.append(f"- **Size:** {format_size(analysis['size_bytes'])}")
            lines.append(f"- **Reasoning:** {analysis['reasoning']}")
            lines.append("")
    
    # Instructions
    lines.append("---")
    lines.append("")
    lines.append("## How to Use This Review")
    lines.append("")
    lines.append("1. **Auto-route files:** Run `python3 N5/scripts/inbox_router.py` to move high-confidence files")
    lines.append("2. **Review suggestions:** Manually move suggested files or provide feedback")
    lines.append("3. **Classify manual items:** Move to appropriate destinations")
    lines.append("4. **Provide feedback:** Document corrections in feedback log (future feature)")
    lines.append("")
    
    content = "\n".join(lines)
    
    if not dry_run:
        REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REVIEW_PATH, "w") as f:
            f.write(content)
        logger.info(f"✓ Review generated: {REVIEW_PATH}")
    else:
        logger.info("[DRY RUN] Would generate REVIEW.md")
    
    stats = {
        "total": len(analyses),
        "by_action": {k: len(v) for k, v in by_action.items()},
        "ttl_exceeded": len(ttl_exceeded)
    }
    
    return stats


def main(dry_run: bool = False) -> int:
    """Main execution."""
    try:
        logger.info("=" * 60)
        logger.info("INBOX REVIEW GENERATOR - Starting")
        logger.info("=" * 60)
        
        if not CONFIG_PATH.exists():
            logger.error(f"Config not found: {CONFIG_PATH}")
            return 1
        
        stats = generate_review(dry_run=dry_run)
        
        logger.info("=" * 60)
        logger.info("INBOX REVIEW GENERATOR - Complete")
        logger.info(f"  Total items: {stats['total']}")
        if stats['total'] > 0:
            logger.info(f"  Auto-route: {stats['by_action']['auto_route']}")
            logger.info(f"  Suggest: {stats['by_action']['suggest']}")
            logger.info(f"  Manual: {stats['by_action']['manual_only']}")
            logger.info(f"  TTL exceeded: {stats['ttl_exceeded']}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Inbox review document")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
