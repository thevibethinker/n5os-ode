#!/usr/bin/env python3
"""
Flow Learner - Zero-Doc Self-Learning System
Learns routing patterns from user corrections and updates confidence thresholds.

Usage:
    python3 flow_learner.py --train
    python3 flow_learner.py --report
    python3 flow_learner.py --dry-run
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WS = Path("/home/workspace")
FLOW_LOG = WS / "N5/data/file_flow_log.jsonl"
PATTERNS = WS / "N5/data/learned_patterns.json"
THRESHOLDS = WS / "N5/config/confidence_thresholds.json"
CORRECTIONS = WS / "N5/data/corrections.jsonl"


def load_json(path: Path) -> Dict:
    """Load JSON file with error handling."""
    try:
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return {}
        return json.loads(path.read_text())
    except Exception as e:
        logger.error(f"Error loading {path}: {e}")
        return {}


def save_json(path: Path, data: Dict, dry_run: bool = False) -> bool:
    """Save JSON with atomic write."""
    if dry_run:
        logger.info(f"[DRY RUN] Would write to {path}")
        logger.info(f"[DRY RUN] Data: {json.dumps(data, indent=2)[:200]}...")
        return True
    
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(data, indent=2))
        tmp.rename(path)
        logger.info(f"✓ Saved {path}")
        return True
    except Exception as e:
        logger.error(f"Error saving {path}: {e}")
        return False


def load_corrections(since_days: int = 7) -> List[Dict]:
    """Load recent corrections from log."""
    if not CORRECTIONS.exists():
        logger.info("No corrections file yet")
        return []
    
    cutoff = datetime.utcnow() - timedelta(days=since_days)
    corrections = []
    
    with CORRECTIONS.open() as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                ts = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                if ts > cutoff:
                    corrections.append(entry)
            except Exception as e:
                logger.warning(f"Skipping malformed line: {e}")
    
    logger.info(f"Loaded {len(corrections)} corrections from last {since_days} days")
    return corrections


def analyze_corrections(corrections: List[Dict]) -> Dict[str, Any]:
    """Analyze correction patterns to learn routing rules."""
    analysis = {
        'by_type': defaultdict(lambda: {'total': 0, 'corrected': 0, 'destinations': defaultdict(int)}),
        'entity_mappings': defaultdict(lambda: defaultdict(int)),
        'filename_patterns': defaultdict(int),
        'content_keywords': defaultdict(lambda: defaultdict(int))
    }
    
    for corr in corrections:
        file_type = corr.get('predicted_type', 'unknown')
        predicted_dest = corr.get('predicted_destination', '')
        actual_dest = corr.get('actual_destination', '')
        entities = corr.get('entities', [])
        filename = corr.get('filename', '')
        
        # Track accuracy by type
        analysis['by_type'][file_type]['total'] += 1
        if predicted_dest != actual_dest:
            analysis['by_type'][file_type]['corrected'] += 1
        analysis['by_type'][file_type]['destinations'][actual_dest] += 1
        
        # Learn entity→destination mappings
        for entity in entities:
            analysis['entity_mappings'][entity][actual_dest] += 1
        
        # Learn filename patterns
        if filename:
            # Extract patterns (e.g., "Resume" in name, .log extension)
            if 'resume' in filename.lower() or 'cv' in filename.lower():
                analysis['filename_patterns']['resume_pattern'] += 1
            if filename.endswith('.log'):
                analysis['filename_patterns']['log_pattern'] += 1
        
        # Learn content keywords (from meeting notes, etc)
        keywords = corr.get('keywords', [])
        for kw in keywords:
            analysis['content_keywords'][kw][actual_dest] += 1
    
    return analysis


def update_learned_patterns(analysis: Dict, dry_run: bool = False) -> bool:
    """Update learned patterns based on analysis."""
    patterns = load_json(PATTERNS)
    
    # Update entity mappings (e.g., "ClientX" -> Meetings)
    if 'clients_careerspan' not in patterns:
        patterns['clients_careerspan'] = {'entities': [], 'confidence_boost': 0.25}
    
    for entity, dests in analysis['entity_mappings'].items():
        # If entity strongly correlates with a destination (>70%), add to patterns
        total = sum(dests.values())
        for dest, count in dests.items():
            if count / total > 0.7:
                if 'Meeting' in dest and entity not in patterns['clients_careerspan']['entities']:
                    patterns['clients_careerspan']['entities'].append(entity)
                    logger.info(f"Learned: {entity} → Meetings")
    
    # Update accuracy metrics
    for file_type, stats in analysis['by_type'].items():
        key = f"{file_type}_patterns"
        if key not in patterns:
            patterns[key] = {'accuracy': 0.0, 'examples': 0}
        
        total = stats['total']
        correct = total - stats['corrected']
        patterns[key]['accuracy'] = correct / total if total > 0 else 0.0
        patterns[key]['examples'] = total
        logger.info(f"{file_type}: {correct}/{total} correct ({patterns[key]['accuracy']:.1%})")
    
    patterns['updated'] = datetime.utcnow().isoformat() + 'Z'
    return save_json(PATTERNS, patterns, dry_run)


def update_confidence_thresholds(analysis: Dict, dry_run: bool = False) -> bool:
    """Adjust confidence thresholds based on accuracy."""
    thresholds = load_json(THRESHOLDS)
    
    for file_type, stats in analysis['by_type'].items():
        if stats['total'] < 10:
            continue  # Need more data
        
        accuracy = (stats['total'] - stats['corrected']) / stats['total']
        current_threshold = thresholds['thresholds'].get(file_type, 0.85)
        
        # Adjust threshold: high accuracy → lower threshold (be more aggressive)
        #                   low accuracy → higher threshold (be more cautious)
        if accuracy > 0.90:
            new_threshold = max(0.80, current_threshold - 0.02)
        elif accuracy < 0.70:
            new_threshold = min(0.95, current_threshold + 0.03)
        else:
            new_threshold = current_threshold
        
        if new_threshold != current_threshold:
            logger.info(f"Adjusting {file_type}: {current_threshold:.2f} → {new_threshold:.2f} (accuracy: {accuracy:.1%})")
            thresholds['thresholds'][file_type] = new_threshold
    
    thresholds['updated'] = datetime.utcnow().isoformat() + 'Z'
    return save_json(THRESHOLDS, thresholds, dry_run)


def generate_report() -> str:
    """Generate learning report."""
    patterns = load_json(PATTERNS)
    thresholds = load_json(THRESHOLDS)
    
    report = ["# Flow Learning Report", ""]
    report.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    report.append("")
    
    # Current thresholds
    report.append("## Confidence Thresholds")
    for ftype, thresh in thresholds.get('thresholds', {}).items():
        report.append(f"- {ftype}: {thresh:.2f}")
    report.append("")
    
    # Accuracy by type
    report.append("## Accuracy by Type")
    for key, data in patterns.items():
        if '_patterns' in key and 'accuracy' in data:
            ftype = key.replace('_patterns', '')
            report.append(f"- {ftype}: {data['accuracy']:.1%} ({data.get('examples', 0)} examples)")
    report.append("")
    
    # Learned entities
    report.append("## Learned Entity Mappings")
    if patterns.get('clients_careerspan', {}).get('entities'):
        report.append("Careerspan clients:")
        for ent in patterns['clients_careerspan']['entities']:
            report.append(f"  - {ent}")
    else:
        report.append("None yet (need corrections to train)")
    report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    for key, data in patterns.items():
        if '_patterns' in key and 'needs_training' in data and data['needs_training']:
            ftype = key.replace('_patterns', '')
            report.append(f"- {ftype}: Needs more training data")
    
    return "\n".join(report)


def main(train: bool = False, report: bool = False, dry_run: bool = False) -> int:
    """Main entry point."""
    try:
        if report:
            print(generate_report())
            return 0
        
        if not train:
            logger.error("Must specify --train or --report")
            return 1
        
        logger.info("Starting flow learning training...")
        
        # Load corrections from last 7 days
        corrections = load_corrections(since_days=7)
        
        if not corrections:
            logger.info("No corrections to learn from")
            return 0
        
        # Analyze patterns
        analysis = analyze_corrections(corrections)
        
        # Update learned patterns
        if not update_learned_patterns(analysis, dry_run):
            logger.error("Failed to update patterns")
            return 1
        
        # Update confidence thresholds
        if not update_confidence_thresholds(analysis, dry_run):
            logger.error("Failed to update thresholds")
            return 1
        
        logger.info(f"✓ Learning complete from {len(corrections)} corrections")
        return 0
        
    except Exception as e:
        logger.error(f"Error during learning: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flow learning system")
    parser.add_argument("--train", action="store_true", help="Train from corrections")
    parser.add_argument("--report", action="store_true", help="Generate learning report")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no writes)")
    
    args = parser.parse_args()
    exit(main(train=args.train, report=args.report, dry_run=args.dry_run))
