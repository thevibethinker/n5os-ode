#!/usr/bin/env python3
"""
Inbox Analyzer Script
Analyzes files in Inbox/ and generates routing suggestions using LLM
"""
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import mimetypes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
INBOX_PATH = WORKSPACE_ROOT / "Inbox"
CONFIG_PATH = WORKSPACE_ROOT / "N5/config/routing_config.json"
ANALYSIS_LOG_PATH = WORKSPACE_ROOT / "N5/logs/.inbox_analysis.jsonl"

SYSTEM_FILES = {"POLICY.md", "QUICKSTART.md", "REVIEW.md", "VERIFICATION_CHECKLIST.md"}


def load_config() -> dict:
    """Load routing configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_file_preview(filepath: Path, max_chars: int = 500) -> str:
    """Get preview of file content (first N chars)."""
    try:
        if filepath.suffix in [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".zip", ".tar", ".gz"]:
            return f"[Binary file: {filepath.suffix}]"
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
            return content if len(content) < max_chars else content + "..."
    except Exception as e:
        return f"[Error reading file: {e}]"


def get_file_metadata(filepath: Path) -> dict:
    """Extract file metadata."""
    stat = filepath.stat()
    mime_type, _ = mimetypes.guess_type(str(filepath))
    
    return {
        "filename": filepath.name,
        "size": stat.st_size,
        "file_type": mime_type or filepath.suffix or "unknown",
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


def analyze_file_llm(filepath: Path, config: dict) -> dict:
    """
    Analyze file using LLM to determine destination.
    
    NOTE: This is a placeholder for actual LLM integration.
    In real implementation, this would call the Zo LLM with the analysis prompt.
    For now, returns a structured response based on heuristics.
    """
    metadata = get_file_metadata(filepath)
    preview = get_file_preview(filepath)
    
    # Build destination descriptions string
    dest_desc = "\n".join([
        f"- {path}: {desc}"
        for path, desc in config["destination_descriptions"].items()
    ])
    
    # Format prompt
    prompt = config["analysis_prompt_template"].format(
        filename=metadata["filename"],
        size=metadata["size"],
        file_type=metadata["file_type"],
        preview=preview,
        destination_descriptions=dest_desc
    )
    
    # TODO: Replace with actual LLM call
    # For now, use simple heuristics as placeholder
    destination, confidence, reasoning = classify_by_heuristics(filepath, metadata, config)
    
    return {
        "destination": destination,
        "confidence": confidence,
        "reasoning": reasoning,
        "prompt": prompt  # Include for debugging
    }


def classify_by_heuristics(filepath: Path, metadata: dict, config: dict) -> tuple:
    """
    Simple heuristic classifier (placeholder for LLM).
    Returns (destination, confidence, reasoning)
    """
    name = filepath.name.lower()
    ext = filepath.suffix.lower()
    
    # Meeting notes
    if "meeting" in name or "notes" in name:
        if "careerspan" in name or "company" in name:
            return ("Careerspan/Meetings/", 0.75, "Filename suggests company meeting notes")
        return ("Personal/Meetings/", 0.70, "Filename suggests personal meeting notes")
    
    # Images
    if ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
        return ("Images/", 0.90, "Image file type")
    
    # Documents
    if ext in [".md", ".txt", ".doc", ".docx"]:
        if "project" in name:
            return ("projects/", 0.65, "Document with 'project' in name")
        return ("Documents/", 0.60, "Generic document, unclear classification")
    
    # Code/Projects
    if ext in [".py", ".js", ".html", ".css", ".json"]:
        return ("projects/", 0.80, "Code file likely belongs to a project")
    
    # PDFs
    if ext == ".pdf":
        if "article" in name or "paper" in name:
            return ("Articles/", 0.75, "PDF likely an article")
        return ("Documents/", 0.55, "PDF document, unclear classification")
    
    # Default: Temporary
    return ("Records/Temporary/", 0.40, "Unable to classify, defaulting to temporary storage")


def determine_action(confidence: float, config: dict) -> str:
    """Determine routing action based on confidence thresholds."""
    thresholds = config["confidence_thresholds"]
    
    if confidence >= thresholds["auto_route"]:
        return "auto_route"
    elif confidence >= thresholds["suggest"]:
        return "suggest"
    else:
        return "manual_only"


def log_analysis(analysis: dict) -> None:
    """Append analysis to log."""
    ANALYSIS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ANALYSIS_LOG_PATH, "a") as f:
        f.write(json.dumps(analysis) + "\n")


def analyze_inbox(dry_run: bool = False) -> dict:
    """Analyze all files in Inbox and log routing suggestions."""
    config = load_config()
    
    items = [f for f in INBOX_PATH.iterdir() if f.is_file() and f.name not in SYSTEM_FILES]
    
    stats = {
        "analyzed": 0,
        "auto_route": 0,
        "suggest": 0,
        "manual_only": 0,
        "errors": 0
    }
    
    for item in items:
        try:
            logger.info(f"Analyzing: {item.name}")
            
            metadata = get_file_metadata(item)
            llm_result = analyze_file_llm(item, config)
            
            action = determine_action(llm_result["confidence"], config)
            
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "file_path": str(item),
                "filename": metadata["filename"],
                "size_bytes": metadata["size"],
                "file_type": metadata["file_type"],
                "destination": llm_result["destination"],
                "confidence": llm_result["confidence"],
                "reasoning": llm_result["reasoning"],
                "action": action,
                "routed": False,
                "model_used": config["analysis_model"]
            }
            
            if not dry_run:
                log_analysis(analysis)
            
            stats["analyzed"] += 1
            stats[action] += 1
            
            logger.info(f"  → {llm_result['destination']} (confidence: {llm_result['confidence']:.2f}, action: {action})")
            
        except Exception as e:
            logger.error(f"✗ Failed to analyze {item.name}: {e}", exc_info=True)
            stats["errors"] += 1
    
    return stats


def main(dry_run: bool = False) -> int:
    """Main execution."""
    try:
        logger.info("=" * 60)
        logger.info("INBOX ANALYZER - Starting")
        logger.info("=" * 60)
        
        if not CONFIG_PATH.exists():
            logger.error(f"Config not found: {CONFIG_PATH}")
            return 1
        
        stats = analyze_inbox(dry_run=dry_run)
        
        logger.info("=" * 60)
        logger.info("INBOX ANALYZER - Complete")
        logger.info(f"  Analyzed: {stats['analyzed']}")
        logger.info(f"  Auto-route candidates: {stats['auto_route']}")
        logger.info(f"  Suggest for review: {stats['suggest']}")
        logger.info(f"  Manual only: {stats['manual_only']}")
        logger.info(f"  Errors: {stats['errors']}")
        logger.info("=" * 60)
        
        return 0 if stats["errors"] == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Inbox files")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without logging")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
