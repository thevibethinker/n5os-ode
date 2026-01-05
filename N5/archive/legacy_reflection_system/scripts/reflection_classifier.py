#!/usr/bin/env python3
"""
Reflection Multi-Label Classifier

Classifies reflection transcripts into 1+ block types (B50-B99) with confidence scoring.
Part of reflection-v2 processing pipeline.

Usage:
    python3 reflection_classifier.py --input <transcript.jsonl> [--output <classification.json>]
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Classification categories mapped to block types
CATEGORIES = {
    "personal": ["B50"],
    "learning": ["B60"],
    "thought_leadership": ["B70"],
    "market_analysis": ["B71"],
    "product_analysis": ["B72"],
    "strategic": ["B73"],
    "social_post": ["B80"],
    "blog": ["B81"],
    "executive_memo": ["B82"],
    "compound": ["B90"],
    "meta": ["B91"]
}

# Keyword patterns for each category (from registry)
PATTERNS = {
    "personal": [
        "feeling", "personally", "struggling with", "learning about myself",
        "growth", "emotions", "mindset", "personal journey", "self-aware"
    ],
    "learning": [
        "insight from", "learned that", "discovered", "synthesis", "aha moment",
        "understanding", "connecting dots", "pattern", "realize"
    ],
    "thought_leadership": [
        "industry", "trend", "future of", "prediction", "perspective on",
        "opinion about", "controversial", "believe that", "industry needs"
    ],
    "market_analysis": [
        "competitor", "market", "landscape", "positioning", "opportunity",
        "gap in market", "player", "competitive", "market share"
    ],
    "product_analysis": [
        "feature", "roadmap", "user", "product", "functionality", "MVP",
        "iteration", "build", "design", "UX", "user experience"
    ],
    "strategic": [
        "strategy", "vision", "long-term", "positioning", "big picture",
        "strategic", "direction", "pivot", "trajectory"
    ],
    "social_post": [
        "announcement", "sharing", "excited to", "proud to", "post about",
        "social", "LinkedIn", "share on"
    ],
    "blog": [
        "deep dive", "comprehensive", "detailed analysis", "blog", "article",
        "write about", "long-form", "publish"
    ],
    "executive_memo": [
        "decision", "recommendation", "action items", "memo", "executive summary",
        "stakeholders", "brief", "report"
    ],
    "compound": [
        "pattern across", "noticed over time", "evolution of", "recurring theme",
        "meta-pattern", "longitudinal", "over the past"
    ],
    "meta": [
        "reflection process", "how I think", "my thinking", "meta",
        "process itself", "methodology", "approach to"
    ]
}

# Minimum confidence threshold
MIN_CONFIDENCE = 0.3


def load_transcript(input_path: Path) -> str:
    """Load transcript text from .jsonl file."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            
        transcript_text = data.get('text', '')
        
        if not transcript_text:
            logger.error(f"No 'text' field found in {input_path}")
            return ""
            
        logger.info(f"Loaded transcript: {len(transcript_text)} characters")
        return transcript_text
        
    except Exception as e:
        logger.error(f"Error loading transcript: {e}", exc_info=True)
        return ""


def calculate_keyword_density(text: str, keywords: List[str]) -> float:
    """
    Calculate normalized keyword density score.
    
    Returns float 0.0-1.0 representing keyword match strength.
    """
    if not text:
        return 0.0
    
    text_lower = text.lower()
    text_words = len(text_lower.split())
    
    if text_words == 0:
        return 0.0
    
    # Count keyword matches (whole word boundaries)
    matches = 0
    for keyword in keywords:
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        matches += len(re.findall(pattern, text_lower))
    
    # Normalize by text length (prevent long texts from dominating)
    # Score = (matches / text_words) * scaling_factor
    # Scaling factor chosen so ~5 keyword matches in 1000 words = 0.5 confidence
    raw_density = (matches / text_words) * 100
    
    # Apply sigmoid-like normalization to map to 0-1 range
    # This gives diminishing returns for very high keyword density
    normalized = min(1.0, raw_density / 2.0)
    
    return round(normalized, 3)


def generate_rationale(text: str, classifications: List[Dict]) -> str:
    """Generate human-readable rationale for classifications."""
    if not classifications:
        return "No strong category matches found in transcript."
    
    # Get top classification
    top = classifications[0]
    category = top['category']
    confidence = top['confidence']
    
    # Extract a relevant snippet
    text_lower = text.lower()
    keywords = PATTERNS.get(category, [])
    
    # Find first matching keyword in text
    snippet = ""
    for keyword in keywords:
        pattern = r'.{0,50}\b' + re.escape(keyword.lower()) + r'\b.{0,50}'
        match = re.search(pattern, text_lower)
        if match:
            snippet = match.group(0).strip()
            break
    
    if len(classifications) == 1:
        rationale = f"Primary classification: {category} (confidence: {confidence:.2f}). "
    else:
        categories_str = ", ".join([c['category'] for c in classifications])
        rationale = f"Multi-label classification: {categories_str}. "
    
    if snippet:
        rationale += f"Example: \"...{snippet}...\""
    
    return rationale


def classify_reflection(transcript_text: str) -> Dict:
    """
    Multi-label classification with confidence scoring.
    
    Returns:
    {
        "classifications": [
            {"category": "strategic", "blocks": ["B73"], "confidence": 0.85},
            {"category": "product_analysis", "blocks": ["B72"], "confidence": 0.72}
        ],
        "recommended_blocks": ["B73", "B72"],
        "rationale": "Strategic discussion of product roadmap..."
    }
    """
    if not transcript_text:
        return {
            "classifications": [],
            "recommended_blocks": [],
            "rationale": "Empty transcript - no classification possible"
        }
    
    # Score each category
    scores = {}
    for category, keywords in PATTERNS.items():
        score = calculate_keyword_density(transcript_text, keywords)
        if score >= MIN_CONFIDENCE:
            scores[category] = score
            logger.debug(f"Category '{category}': {score:.3f}")
    
    if not scores:
        logger.warning("No categories exceeded confidence threshold")
        return {
            "classifications": [],
            "recommended_blocks": [],
            "rationale": f"No category confidence exceeded threshold ({MIN_CONFIDENCE})"
        }
    
    # Sort by confidence (descending)
    sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Build classifications list
    classifications = []
    for category, confidence in sorted_categories:
        classifications.append({
            "category": category,
            "blocks": CATEGORIES[category],
            "confidence": confidence
        })
    
    # Extract all recommended blocks
    recommended_blocks = []
    for c in classifications:
        recommended_blocks.extend(c["blocks"])
    
    # Generate rationale
    rationale = generate_rationale(transcript_text, classifications)
    
    result = {
        "classifications": classifications,
        "recommended_blocks": list(set(recommended_blocks)),  # deduplicate
        "rationale": rationale
    }
    
    logger.info(f"Classification complete: {len(classifications)} categories, "
                f"{len(result['recommended_blocks'])} unique blocks")
    
    return result


def validate_blocks(blocks: List[str]) -> bool:
    """Verify all block IDs are valid (B50-B99)."""
    valid_blocks = set()
    for category_blocks in CATEGORIES.values():
        valid_blocks.update(category_blocks)
    
    for block in blocks:
        if block not in valid_blocks:
            logger.error(f"Invalid block ID: {block}")
            return False
    
    return True


def main(input_path: Path, output_path: Path = None, dry_run: bool = False) -> int:
    """Main classification workflow."""
    try:
        # Validate input exists
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return 1
        
        # Load transcript
        logger.info(f"Loading transcript from {input_path}")
        transcript_text = load_transcript(input_path)
        
        if not transcript_text:
            logger.error("Failed to load transcript text")
            return 1
        
        # Classify
        logger.info("Running multi-label classification...")
        result = classify_reflection(transcript_text)
        
        # Validate block IDs
        if not validate_blocks(result['recommended_blocks']):
            logger.error("Classification produced invalid block IDs")
            return 1
        
        # Determine output path
        if not output_path:
            output_path = input_path.with_suffix('.classification.json')
        
        # Write results
        if dry_run:
            logger.info("[DRY RUN] Would write classification to: %s", output_path)
            logger.info("[DRY RUN] Result: %s", json.dumps(result, indent=2))
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Classification written to: {output_path}")
        
        # Log summary
        logger.info(f"✓ Complete: {len(result['classifications'])} classifications, "
                   f"{len(result['recommended_blocks'])} recommended blocks")
        
        return 0
        
    except Exception as e:
        logger.error(f"Classification failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Multi-label classifier for reflection transcripts"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input transcript .jsonl file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output classification .json file (default: input_path.classification.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview classification without writing file"
    )
    
    args = parser.parse_args()
    exit_code = main(
        input_path=args.input,
        output_path=args.output,
        dry_run=args.dry_run
    )
    exit(exit_code)
