#!/usr/bin/env python3
"""
Generate teaching moments from V's descriptions.
Detects imprecise language and surfaces precise alternatives.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

GLOSSARY_PATH = Path("N5/pulse/teaching/glossary.json")

# Common imprecision patterns to detect
IMPRECISION_PATTERNS = {
    "non-overlapping": {
        "precise_term": "MECE decomposition",
        "why_it_matters": "MECE (Mutually Exclusive, Collectively Exhaustive) ensures nothing is missed and nothing overlaps—critical for complete work coverage.",
        "example": "When planning parallel tasks, make them MECE: each task covers distinct ground, together they cover everything needed."
    },
    "all at once": {
        "precise_term": "atomic operation",
        "why_it_matters": "Atomic operations either succeed completely or fail completely, preventing partial or corrupted states.",
        "example": "A file move that deletes source then creates destination is atomic—either both happen or neither does."
    },
    "run twice safely": {
        "precise_term": "idempotent operation",
        "why_it_matters": "Idempotent operations produce the same result no matter how many times they're applied, making them safe for retries and automation.",
        "example": "Setting a value to 'X' is idempotent—running it once or ten times leaves the same state."
    },
    "pause for review": {
        "precise_term": "checkpoint",
        "why_it_matters": "Checkpoints are designated points in workflows where humans validate progress before continuing—essential for quality control.",
        "example": "The plan_review checkpoint in Pulse lets you approve the plan before workers start executing."
    },
    "split into parts": {
        "precise_term": "decomposition",
        "why_it_matters": "Decomposition breaks complex problems into smaller, manageable pieces that can be solved independently.",
        "example": "Breaking 'build a website' into 'design frontend', 'build backend', 'deploy' is decomposition."
    },
    "independent tasks": {
        "precise_term": "parallelizable",
        "why_it_matters": "Parallelizable tasks can run simultaneously, reducing total execution time compared to sequential execution.",
        "example": "In Pulse Streams, drops in the same stream run sequentially, but different streams run in parallel."
    }
}


def load_glossary() -> Dict:
    """Load the glossary from disk."""
    if GLOSSARY_PATH.exists():
        return json.loads(GLOSSARY_PATH.read_text())
    return {"version": "1.0", "terms": []}


def save_glossary(glossary: Dict):
    """Save the glossary to disk."""
    GLOSSARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    GLOSSARY_PATH.write_text(json.dumps(glossary, indent=2))


def detect_imprecision(text: str) -> List[Dict]:
    """
    Detect imprecise language patterns.

    Returns list of:
    {
        "v_phrase": "like those sort of non-overlapping things",
        "precise_term": "MECE decomposition",
        "explanation": "What you're describing is called MECE..."
    }
    """
    moments = []
    text_lower = text.lower()

    # Build word mapping for flexible matching
    pattern_words_map = {
        "non-overlapping": ["non", "overlapping", "overlap", "don't", "no"],
        "all at once": ["all", "once", "complete", "completely", "fails", "all-or-nothing"],
        "run twice safely": ["run", "twice", "multiple", "times", "safely", "safe", "again"],
        "pause for review": ["pause", "stop", "review", "check", "human", "look"],
        "split into parts": ["split", "break", "parts", "pieces", "smaller", "divide"],
        "independent tasks": ["independent", "separate", "parallel", "same", "time"]
    }

    for pattern, teaching in IMPRECISION_PATTERNS.items():
        # Get key words for this pattern
        key_words = pattern_words_map.get(pattern, pattern.split())

        # Count how many key words appear in the text
        matches = sum(1 for word in key_words if word in text_lower)

        # Lower threshold to 40% (at least 2 words for most patterns)
        threshold = max(len(key_words) * 0.4, 2)
        
        if matches >= threshold:
            moments.append({
                "v_phrase": pattern,
                "precise_term": teaching["precise_term"],
                "why_it_matters": teaching["why_it_matters"],
                "example": teaching["example"]
            })

    return moments


def generate_moment(context: str, v_input: str, checkpoint: str) -> Dict:
    """
    Generate a teaching moment.

    context: What's happening (plan_review, feedback, etc.)
    v_input: V's actual words
    checkpoint: Which HITL checkpoint triggered this

    Returns:
    {
        "has_moment": true/false,
        "teaching": {
            "you_said": "...",
            "precise_term": "...",
            "why_it_matters": "...",
            "example": "..."
        },
        "glossary_update": {...} or null
    }
    """
    # Detect imprecision patterns
    detected = detect_imprecision(v_input)

    if not detected:
        return {
            "has_moment": False,
            "teaching": None,
            "glossary_update": None
        }

    # Use first detected moment (could be smarter about ranking)
    best = detected[0]

    # Build teaching moment
    teaching = {
        "you_said": f"...{best['v_phrase']}...",
        "precise_term": best["precise_term"],
        "why_it_matters": best["why_it_matters"],
        "example": best["example"]
    }

    # Check if term is already in glossary
    glossary = load_glossary()
    existing_term = None
    for term in glossary["terms"]:
        if term["precise_term"].lower() == best["precise_term"].lower():
            existing_term = term
            break

    glossary_update = None
    if existing_term:
        # Update usage count
        existing_term["usage_count"] = existing_term.get("usage_count", 0) + 1
        existing_term["last_seen"] = datetime.now(timezone.utc).isoformat()
        save_glossary(glossary)
    else:
        # Add new term to glossary
        new_term = {
            "term": best["precise_term"].split()[0],  # First word as term
            "definition": best["why_it_matters"],
            "v_description": f"{best['v_phrase']}",
            "precise_term": best["precise_term"],
            "context": checkpoint,
            "first_encountered": datetime.now(timezone.utc).isoformat(),
            "absorbed": False,
            "usage_count": 1,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
        glossary["terms"].append(new_term)
        save_glossary(glossary)
        glossary_update = new_term

    return {
        "has_moment": True,
        "teaching": teaching,
        "glossary_update": glossary_update
    }


def add_to_glossary(term: str, definition: str, v_description: str, context: str) -> Dict:
    """Add new term to glossary."""
    glossary = load_glossary()

    new_term = {
        "term": term,
        "definition": definition,
        "v_description": v_description,
        "precise_term": definition.split(" - ")[0] if " - " in definition else term,
        "context": context,
        "first_encountered": datetime.now(timezone.utc).isoformat(),
        "absorbed": False,
        "usage_count": 1
    }

    glossary["terms"].append(new_term)
    save_glossary(glossary)

    return new_term


def mark_absorbed(term: str) -> bool:
    """Mark term as absorbed (V demonstrated understanding)."""
    glossary = load_glossary()
    found = False

    for t in glossary["terms"]:
        if t["precise_term"].lower() == term.lower() or t["term"].lower() == term.lower():
            t["absorbed"] = True
            t["absorbed_at"] = datetime.now(timezone.utc).isoformat()
            found = True
            break

    if found:
        save_glossary(glossary)

    return found


def get_unabsorbed_terms() -> List[Dict]:
    """Get all terms that haven't been absorbed yet."""
    glossary = load_glossary()
    return [t for t in glossary["terms"] if not t.get("absorbed", False)]


def get_term_by_name(name: str) -> Optional[Dict]:
    """Get a term from the glossary by name or precise_term."""
    glossary = load_glossary()

    for term in glossary["terms"]:
        if term["precise_term"].lower() == name.lower() or term["term"].lower() == name.lower():
            return term

    return None


if __name__ == "__main__":
    # Test with some examples
    test_inputs = [
        "Make sure the workers don't overlap with each other",
        "I want to run this script multiple times safely",
        "This should be all-or-nothing - either works or fails completely"
    ]

    for text in test_inputs:
        print(f"\nInput: {text}")
        result = generate_moment("test", text, "test_checkpoint")
        if result["has_moment"]:
            print(f"  Teaching: {result['teaching']['precise_term']}")
        else:
            print("  No teaching moment detected")
