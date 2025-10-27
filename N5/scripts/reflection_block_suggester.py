#!/usr/bin/env python3
"""
Reflection Block Suggester

Analyzes recent reflections to identify patterns and suggest new block types.
Focuses on low-confidence classifications and recurring themes.

Usage:
    python3 reflection_block_suggester.py --days 30 --min-frequency 3 --dry-run
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
INCOMING_DIR = WORKSPACE / "N5/records/reflections/incoming"
OUTPUTS_DIR = WORKSPACE / "N5/records/reflections/outputs"
SUGGESTIONS_DIR = WORKSPACE / "N5/records/reflections/suggestions"
SUGGESTIONS_FILE = SUGGESTIONS_DIR / "block_suggestions.jsonl"
STATE_FILE = SUGGESTIONS_DIR / ".state.json"


def load_recent_reflections(days: int = 30) -> List[Dict]:
    """
    Load reflections from the last N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of reflection dictionaries with metadata
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    reflections = []
    
    # Load from incoming directory
    if INCOMING_DIR.exists():
        for file_path in INCOMING_DIR.glob("*.transcript.jsonl"):
            try:
                # Extract date from filename (YYYY-MM-DD format)
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})', file_path.stem)
                if date_match:
                    file_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                    if file_date >= cutoff_date:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            reflections.append({
                                "path": str(file_path),
                                "date": file_date.isoformat(),
                                "text": data.get("text", ""),
                                "classification": None
                            })
                            
                # Check for classification file
                classification_file = file_path.with_suffix(file_path.suffix + ".classification.json")
                if classification_file.exists() and reflections:
                    with open(classification_file, 'r') as f:
                        classification = json.load(f)
                        reflections[-1]["classification"] = classification
                        
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
                continue
    
    logger.info(f"✓ Loaded {len(reflections)} reflections from last {days} days")
    return reflections


def identify_low_confidence_classifications(
    reflections: List[Dict],
    min_confidence: float = 0.6
) -> List[Dict]:
    """
    Filter reflections with low classification confidence.
    
    Args:
        reflections: List of reflection dictionaries
        min_confidence: Minimum confidence threshold
        
    Returns:
        List of low-confidence reflections
    """
    low_confidence = []
    
    for reflection in reflections:
        classification = reflection.get("classification")
        if classification:
            confidence = classification.get("confidence", 0.0)
            if confidence < min_confidence:
                low_confidence.append(reflection)
    
    logger.info(f"✓ Identified {len(low_confidence)} low-confidence classifications (< {min_confidence})")
    return low_confidence


def extract_keywords(text: str, min_length: int = 4) -> List[str]:
    """
    Extract keywords from text using simple tokenization.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    # Simple tokenization: lowercase, remove punctuation, filter by length
    words = re.findall(r'\b[a-z]+\b', text.lower())
    keywords = [w for w in words if len(w) >= min_length]
    
    # Remove common stop words - expanded list
    stop_words = {
        'that', 'this', 'with', 'from', 'have', 'been', 'were', 'they',
        'their', 'what', 'when', 'where', 'which', 'about', 'would', 'there',
        'could', 'should', 'just', 'very', 'more', 'some', 'than', 'into',
        'through', 'over', 'also', 'such', 'only', 'other', 'then', 'them',
        # Common filler words
        'want', 'like', 'able', 'easy', 'time', 'right', 'sort', 'point',
        'your', 'actually', 'think', 'those', 'yeah', 'know', 'going', 'these',
        'least', 'okay', 'things', 'thing', 'really', 'kind', 'probably', 'maybe',
        'still', 'well', 'much', 'need', 'make', 'take', 'give', 'look',
        'something', 'anything', 'everything', 'nothing', 'everyone', 'anyone',
        'someone', 'here', 'there', 'where', 'were', 'does', 'dont', 'didnt',
        'isnt', 'arent', 'wasnt', 'werent', 'havent', 'hasnt', 'hadnt', 'wont',
        'wouldnt', 'shouldnt', 'couldnt', 'cant', 'cannot'
    }
    keywords = [k for k in keywords if k not in stop_words]
    
    return keywords


def extract_recurring_themes(reflections: List[Dict]) -> List[Dict]:
    """
    Extract recurring themes from reflections using keyword clustering.
    
    Args:
        reflections: List of reflection dictionaries
        
    Returns:
        List of theme dictionaries with keywords and examples
    """
    # Extract keywords from all reflections
    all_keywords = []
    for reflection in reflections:
        text = reflection.get("text", "")
        keywords = extract_keywords(text)
        all_keywords.extend(keywords)
    
    # Count keyword frequency
    keyword_counts = Counter(all_keywords)
    
    # Find high-frequency keywords (appear in at least 20% of reflections)
    min_appearances = max(2, len(reflections) // 5)
    frequent_keywords = {k: v for k, v in keyword_counts.items() if v >= min_appearances}
    
    # Group reflections by dominant keywords
    themes = {}
    for keyword, count in frequent_keywords.items():
        matching_reflections = []
        for reflection in reflections:
            text = reflection.get("text", "").lower()
            if keyword in text:
                matching_reflections.append(reflection["path"])
        
        if len(matching_reflections) >= 3:  # Need at least 3 examples
            themes[keyword] = {
                "keyword": keyword,
                "frequency": count,
                "examples": matching_reflections[:5]  # Limit to 5 examples
            }
    
    logger.info(f"✓ Extracted {len(themes)} recurring themes")
    return list(themes.values())


def generate_block_suggestions(
    themes: List[Dict],
    reflections: List[Dict]
) -> List[Dict]:
    """
    Generate block type suggestions from themes.
    
    Args:
        themes: List of theme dictionaries
        reflections: Original reflections for context
        
    Returns:
        List of suggestion dictionaries
    """
    suggestions = []
    
    # Get next available block ID
    next_id = get_next_block_id()
    
    for i, theme in enumerate(themes):
        keyword = theme["keyword"]
        
        # Generate suggestion
        suggestion = {
            "suggested_at_iso": datetime.now().isoformat(),
            "suggested_block_id": f"B{next_id + i}",
            "suggested_block_name": keyword.title(),
            "description": f"Reflections about {keyword}",
            "frequency": theme["frequency"],
            "example_reflections": theme["examples"],
            "recommended_domain": "internal",
            "recommended_voice_profile": "N5/prefs/communication/voice.md",
            "confidence": min(0.95, 0.5 + (theme["frequency"] / len(reflections))),
            "status": "pending_review",
            "keywords": [keyword]
        }
        suggestions.append(suggestion)
    
    logger.info(f"✓ Generated {len(suggestions)} block suggestions")
    return suggestions


def get_next_block_id() -> int:
    """
    Get the next available block ID.
    
    Returns:
        Next block ID number
    """
    # Start at B74 (after existing blocks)
    # In production, would read from block registry
    return 74


def check_duplicate_suggestions(suggestion: Dict, history: List[Dict]) -> bool:
    """
    Check if suggestion already exists in history.
    
    Args:
        suggestion: New suggestion to check
        history: List of historical suggestions
        
    Returns:
        True if duplicate exists
    """
    keyword = suggestion["keywords"][0]
    
    for hist in history:
        if keyword in hist.get("keywords", []):
            return True
    
    return False


def load_suggestion_history() -> List[Dict]:
    """
    Load historical suggestions.
    
    Returns:
        List of historical suggestion dictionaries
    """
    if not SUGGESTIONS_FILE.exists():
        return []
    
    history = []
    with open(SUGGESTIONS_FILE, 'r') as f:
        for line in f:
            try:
                history.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    return history


def save_suggestions(suggestions: List[Dict], output_path: Path, dry_run: bool = False):
    """
    Save suggestions to output file.
    
    Args:
        suggestions: List of suggestion dictionaries
        output_path: Path to save suggestions
        dry_run: If True, don't actually write
    """
    if dry_run:
        logger.info("[DRY RUN] Would save suggestions to: %s", output_path)
        for suggestion in suggestions:
            logger.info("[DRY RUN] Suggestion: %s (%s)", 
                       suggestion["suggested_block_name"],
                       suggestion["suggested_block_id"])
        return
    
    # Create directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Append to JSONL file
    with open(output_path, 'a') as f:
        for suggestion in suggestions:
            f.write(json.dumps(suggestion) + "\n")
    
    logger.info(f"✓ Saved {len(suggestions)} suggestions to {output_path}")


def main(
    days: int = 30,
    min_frequency: int = 3,
    min_confidence_threshold: float = 0.6,
    output: Path = SUGGESTIONS_FILE,
    dry_run: bool = False
) -> int:
    """
    Main execution function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting reflection block suggester")
        logger.info(f"Parameters: days={days}, min_frequency={min_frequency}, "
                   f"min_confidence={min_confidence_threshold}")
        
        # Load reflections
        reflections = load_recent_reflections(days=days)
        if not reflections:
            logger.warning("No reflections found")
            return 0
        
        # Identify low-confidence classifications
        low_confidence = identify_low_confidence_classifications(
            reflections,
            min_confidence=min_confidence_threshold
        )
        
        if not low_confidence:
            logger.info("No low-confidence classifications found")
            # Still analyze all reflections for patterns
            low_confidence = reflections
        
        # Extract recurring themes
        themes = extract_recurring_themes(low_confidence)
        if not themes:
            logger.info("No recurring themes found")
            return 0
        
        # Filter themes by minimum frequency
        themes = [t for t in themes if t["frequency"] >= min_frequency]
        logger.info(f"✓ Filtered to {len(themes)} themes (frequency >= {min_frequency})")
        
        if not themes:
            logger.info("No themes meet minimum frequency threshold")
            return 0
        
        # Generate suggestions
        suggestions = generate_block_suggestions(themes, low_confidence)
        
        # Load history and check for duplicates
        history = load_suggestion_history()
        new_suggestions = [s for s in suggestions if not check_duplicate_suggestions(s, history)]
        
        if len(new_suggestions) < len(suggestions):
            logger.info(f"Filtered out {len(suggestions) - len(new_suggestions)} duplicate suggestions")
        
        if not new_suggestions:
            logger.info("No new suggestions (all duplicates)")
            return 0
        
        # Save suggestions
        save_suggestions(new_suggestions, output, dry_run=dry_run)
        
        logger.info("✓ Block suggester complete")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reflection Block Suggester")
    parser.add_argument("--days", type=int, default=30,
                       help="Number of days to look back (default: 30)")
    parser.add_argument("--min-frequency", type=int, default=3,
                       help="Minimum keyword frequency (default: 3)")
    parser.add_argument("--min-confidence-threshold", type=float, default=0.6,
                       help="Minimum confidence threshold (default: 0.6)")
    parser.add_argument("--output", type=Path, default=SUGGESTIONS_FILE,
                       help="Output file path")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview without writing")
    
    args = parser.parse_args()
    exit(main(
        days=args.days,
        min_frequency=args.min_frequency,
        min_confidence_threshold=args.min_confidence_threshold,
        output=args.output,
        dry_run=args.dry_run
    ))
