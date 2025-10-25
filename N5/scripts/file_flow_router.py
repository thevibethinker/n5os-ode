#!/usr/bin/env python3
"""
File Flow Router - Zero-Doc AIR Pattern Orchestrator
Assesses files → routes with confidence → queues for review if uncertain

Usage:
    python3 file_flow_router.py --scan /home/workspace
    python3 file_flow_router.py --process /home/workspace/somefile.pdf
    python3 file_flow_router.py --dry-run --scan /home/workspace
"""

import argparse
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WS = Path("/home/workspace")
PATTERNS = WS / "N5/data/learned_patterns.json"
THRESHOLDS = WS / "N5/config/confidence_thresholds.json"
ANCHORS = WS / "N5/config/anchors.json"
REVIEW_QUEUE = WS / "N5/data/review_queue.jsonl"
CORRECTIONS = WS / "N5/data/corrections.jsonl"


def load_json(path: Path) -> Dict:
    """Load JSON file."""
    try:
        if not path.exists():
            return {}
        return json.loads(path.read_text())
    except Exception as e:
        logger.error(f"Error loading {path}: {e}")
        return {}


def append_jsonl(path: Path, entry: Dict, dry_run: bool = False) -> bool:
    """Append entry to JSONL file."""
    if dry_run:
        logger.info(f"[DRY RUN] Would append to {path}: {entry}")
        return True
    
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as f:
            f.write(json.dumps(entry) + '\n')
        return True
    except Exception as e:
        logger.error(f"Error appending to {path}: {e}")
        return False


def classify_file(filepath: Path, patterns: Dict) -> Tuple[str, float, str]:
    """
    Classify file type and predict destination.
    Returns: (file_type, confidence, destination)
    """
    name = filepath.name.lower()
    ext = filepath.suffix.lower()
    
    # Resume detection
    if 'resume' in name or 'cv' in name or ext in ['.pdf', '.docx']:
        if any(kw in name for kw in ['resume', 'cv']):
            return ('resume', 0.95, 'Documents/Resumes')
    
    # Log detection
    if ext == '.log':
        return ('log', 0.98, 'N5/logs')
    
    # Session state (should never move)
    if 'session_state' in name:
        return ('system_artifact', 1.0, 'DO_NOT_MOVE')
    
    # Meeting notes (needs content analysis - for now, low confidence)
    if any(kw in name for kw in ['meeting', 'notes', 'transcript']):
        # Check learned patterns for entity hints
        # TODO: implement content-based classification
        return ('meeting_note', 0.60, 'Personal/Meetings')
    
    # Export/backup
    if 'export' in name or 'backup' in name:
        return ('export', 0.85, 'N5/exports')
    
    # Default: unknown
    return ('unknown', 0.30, 'REVIEW_NEEDED')


def assess_with_learned_patterns(filepath: Path, file_type: str, patterns: Dict) -> float:
    """Boost confidence based on learned patterns."""
    base_confidence = 0.5
    
    # Check if filename matches learned patterns
    name = filepath.name.lower()
    
    if file_type == 'resume':
        resume_patterns = patterns.get('resume_name_patterns', {})
        if resume_patterns.get('accuracy', 0) > 0.90:
            base_confidence = 0.95
    
    # Check for learned entities (meeting notes)
    if file_type == 'meeting_note':
        # TODO: scan file content for entities
        # For now, keep low confidence to queue for review
        base_confidence = 0.65
    
    return base_confidence


def route_file(filepath: Path, dry_run: bool = False) -> Dict:
    """
    Route a single file through AIR pattern.
    Returns routing decision dict.
    """
    patterns = load_json(PATTERNS)
    thresholds = load_json(THRESHOLDS)
    
    # Assess
    file_type, confidence, destination = classify_file(filepath, patterns)
    
    # Apply learned patterns
    confidence = assess_with_learned_patterns(filepath, file_type, patterns)
    
    # Get threshold for this type
    threshold = thresholds.get('thresholds', {}).get(file_type, 0.85)
    
    decision = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'filepath': str(filepath),
        'filename': filepath.name,
        'file_type': file_type,
        'predicted_destination': destination,
        'confidence': confidence,
        'threshold': threshold,
        'action': 'auto_route' if confidence >= threshold else 'queue_for_review'
    }
    
    # Intervene: auto-route or queue
    if confidence >= threshold and destination != 'REVIEW_NEEDED':
        # Auto-route
        dest_path = WS / destination / filepath.name
        if dry_run:
            logger.info(f"[DRY RUN] Would move {filepath} → {dest_path}")
            decision['action'] = 'would_move_auto'
        else:
            try:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                filepath.rename(dest_path)
                logger.info(f"✓ Auto-routed {filepath.name} → {destination}")
                decision['action'] = 'moved_auto'
                decision['actual_destination'] = str(dest_path)
            except Exception as e:
                logger.error(f"Error moving {filepath}: {e}")
                decision['action'] = 'error'
                decision['error'] = str(e)
    else:
        # Queue for review
        logger.info(f"⏸ Queued for review: {filepath.name} (confidence {confidence:.2f} < {threshold:.2f})")
        append_jsonl(REVIEW_QUEUE, decision, dry_run)
        decision['action'] = 'queued'
    
    return decision


def scan_directory(dirpath: Path, dry_run: bool = False) -> List[Dict]:
    """Scan directory for files needing routing."""
    results = []
    
    # Only scan root level (depth 1)
    for item in dirpath.iterdir():
        if not item.is_file():
            continue
        
        # Skip system files
        if item.name in ['.gitignore', '.DS_Store']:
            continue
        
        # Route the file
        decision = route_file(item, dry_run)
        results.append(decision)
    
    return results


def generate_review_digest() -> str:
    """Generate daily review digest for V."""
    if not REVIEW_QUEUE.exists():
        return "# Daily Review Digest\n\nNo files queued for review."
    
    queued = []
    with REVIEW_QUEUE.open() as f:
        for line in f:
            try:
                queued.append(json.loads(line.strip()))
            except:
                pass
    
    if not queued:
        return "# Daily Review Digest\n\nNo files queued for review."
    
    digest = ["# Daily Review Digest", ""]
    digest.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    digest.append(f"Total queued: {len(queued)}")
    digest.append("")
    
    for idx, item in enumerate(queued, 1):
        digest.append(f"## {idx}. {item['filename']}")
        digest.append(f"- Type: {item['file_type']}")
        digest.append(f"- Predicted: {item['predicted_destination']}")
        digest.append(f"- Confidence: {item['confidence']:.2f} (threshold: {item['threshold']:.2f})")
        digest.append(f"- Path: `{item['filepath']}`")
        digest.append("")
        digest.append("**Action**: Reply with destination or 'correct'")
        digest.append("")
    
    return "\n".join(digest)


def main(
    scan: Optional[str] = None,
    process: Optional[str] = None,
    digest: bool = False,
    dry_run: bool = False
) -> int:
    """Main entry point."""
    try:
        if digest:
            print(generate_review_digest())
            return 0
        
        if scan:
            scan_path = Path(scan)
            if not scan_path.exists():
                logger.error(f"Path not found: {scan}")
                return 1
            
            logger.info(f"Scanning {scan_path}...")
            results = scan_directory(scan_path, dry_run)
            
            # Summary
            auto_routed = sum(1 for r in results if r['action'] == 'moved_auto')
            queued = sum(1 for r in results if r['action'] == 'queued')
            logger.info(f"✓ Scan complete: {auto_routed} auto-routed, {queued} queued for review")
            return 0
        
        if process:
            process_path = Path(process)
            if not process_path.exists():
                logger.error(f"File not found: {process}")
                return 1
            
            decision = route_file(process_path, dry_run)
            print(json.dumps(decision, indent=2))
            return 0
        
        logger.error("Must specify --scan, --process, or --digest")
        return 1
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File flow router")
    parser.add_argument("--scan", help="Scan directory for files to route")
    parser.add_argument("--process", help="Process a single file")
    parser.add_argument("--digest", action="store_true", help="Generate review digest")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no moves)")
    
    args = parser.parse_args()
    exit(main(
        scan=args.scan,
        process=args.process,
        digest=args.digest,
        dry_run=args.dry_run
    ))
