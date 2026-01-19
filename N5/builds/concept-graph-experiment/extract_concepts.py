#!/usr/bin/env python3
"""
Phase 1: Concept Extraction Pipeline

Extracts concepts from positions data using:
1. Title keyword extraction (common themes)
2. Predicate patterns (relationship types hint at shared concepts)
3. Cross-domain bridging (positions spanning domains)

Output:
- data/concepts.json - List of extracted concepts with metadata
- data/thought_concept_edges.json - Edges mapping thoughts to concepts
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Any

BUILD_DIR = Path(__file__).parent
DATA_DIR = BUILD_DIR / "data"

# Source data paths
POSITIONS_EXPORT = Path("/home/workspace/N5/builds/position-system-overhaul/positions_export.json")
TRIPLES_FILE = Path("/home/workspace/N5/builds/position-viz/positions_triples.json")

# Concept extraction patterns - manually curated seed concepts
# These are themes that appear across multiple positions
SEED_CONCEPTS = {
    "signal-decay": {
        "label": "Signal Decay",
        "description": "The degradation of meaningful information in systems over time or through noise",
        "keywords": ["signal", "noise", "collapse", "decay", "obsolete", "broken", "destroyed"],
        "domains": ["hiring-market", "ai-automation"]
    },
    "friction-as-filter": {
        "label": "Friction as Filter",
        "description": "Intentional effort barriers that separate high-quality from low-quality actors",
        "keywords": ["friction", "high-effort", "high-friction", "barrier", "filter", "willingness"],
        "domains": ["hiring-market", "careerspan"]
    },
    "self-knowledge": {
        "label": "Self-Knowledge",
        "description": "The importance of deep self-understanding for professional effectiveness",
        "keywords": ["self-knowledge", "self-reflection", "self-awareness", "self-advocacy", "introspection"],
        "domains": ["careerspan", "personal-foundations", "hiring-market"]
    },
    "trust-networks": {
        "label": "Trust Networks",
        "description": "Systems of relationship-based credibility and referral",
        "keywords": ["trust", "referral", "network", "relationship", "reputation", "credibility"],
        "domains": ["hiring-market", "careerspan", "worldview"]
    },
    "ai-commoditization": {
        "label": "AI Commoditization",
        "description": "How AI reduces the cost and differentiation of previously valuable outputs",
        "keywords": ["ai", "commodit", "automat", "zero cost", "marginal cost", "generic"],
        "domains": ["ai-automation", "hiring-market"]
    },
    "narrative-identity": {
        "label": "Narrative Identity",
        "description": "Professional identity as constructed through stories rather than documents",
        "keywords": ["narrative", "story", "semantic", "identity", "meaningful"],
        "domains": ["careerspan", "worldview", "hiring-market"]
    },
    "orchestration": {
        "label": "Orchestration",
        "description": "Achieving complex outcomes through coordination of simpler components",
        "keywords": ["orchestrat", "multi-step", "sequence", "coordinate", "polyorchestrator"],
        "domains": ["ai-automation", "epistemology"]
    },
    "information-asymmetry": {
        "label": "Information Asymmetry",
        "description": "Imbalances in information access that create market advantages or failures",
        "keywords": ["asymmetr", "information", "data", "signal", "fidelity", "premium"],
        "domains": ["hiring-market", "careerspan", "worldview"]
    },
    "problem-stack": {
        "label": "Problem Stack Elevation",
        "description": "Moving humans to higher-level problems while AI handles lower levels",
        "keywords": ["problem stack", "elevat", "higher", "shift", "expert"],
        "domains": ["ai-automation"]
    },
    "adversarial-dynamics": {
        "label": "Adversarial Dynamics",
        "description": "Zero-sum competition and its alternatives in hiring/career systems",
        "keywords": ["adversarial", "non-adversarial", "zero-sum", "arms race", "mutually assured"],
        "domains": ["hiring-market"]
    },
    "moonshot-growth": {
        "label": "Moonshot Growth",
        "description": "The developmental value of high-risk, high-ambition endeavors",
        "keywords": ["moonshot", "growth", "risk", "high-variance", "developmental"],
        "domains": ["worldview", "founder"]
    },
    "assessment-validity": {
        "label": "Assessment Validity",
        "description": "What makes evaluation signals trustworthy and meaningful",
        "keywords": ["assessment", "evaluat", "valid", "measure", "score", "confidence", "quality"],
        "domains": ["hiring-market", "epistemology"]
    },
    "geometric-distance": {
        "label": "Career Mobility Distance",
        "description": "The measurable gap between current position and target role",
        "keywords": ["geometric", "distance", "mobility", "pivot", "transition", "fundab"],
        "domains": ["careerspan"]
    },
    "portable-trust": {
        "label": "Portable Trust",
        "description": "Mechanisms for transferring credibility across contexts",
        "keywords": ["portable", "trust", "transferable", "readiness", "latency"],
        "domains": ["careerspan", "hiring-market"]
    },
    "anthropomorphic-engagement": {
        "label": "Anthropomorphic Engagement",
        "description": "Human-like interfaces that drive behavior change through social dynamics",
        "keywords": ["anthropomorphic", "social", "human", "engagement", "obligation", "habit"],
        "domains": ["ai-automation", "worldview"]
    },
    "platform-shift": {
        "label": "Platform Shift",
        "description": "Transitions in how platforms create and capture value",
        "keywords": ["platform", "linkedin", "niche", "social network", "utility"],
        "domains": ["worldview"]
    },
    "bundled-tradeoffs": {
        "label": "Bundled Tradeoffs",
        "description": "Hiring as optimization across skill bundles rather than linear ranking",
        "keywords": ["bundle", "trade-off", "tradeoff", "optimization", "stack-rank", "vectorized"],
        "domains": ["hiring-market", "careerspan"]
    },
    "minimum-viable-existence": {
        "label": "Minimum Viable Existence",
        "description": "The declining accessibility of stable middle-class life",
        "keywords": ["minimum viable", "okay life", "middle-class", "dignity", "existence"],
        "domains": ["worldview"]
    },
    "scar-tissue-institutions": {
        "label": "Institutional Scar Tissue",
        "description": "How parallel institutions emerge from historical exclusion",
        "keywords": ["scar tissue", "exclusion", "parallel", "institution", "dominance"],
        "domains": ["worldview"]
    },
    "restraint-discipline": {
        "label": "Disciplined Restraint",
        "description": "Long-term growth through intentional underperformance",
        "keywords": ["restraint", "discipline", "long-term", "sabotag", "over-exertion"],
        "domains": ["worldview", "personal-foundations"]
    }
}


def load_positions() -> list[dict]:
    """Load positions from export file."""
    with open(POSITIONS_EXPORT) as f:
        return json.load(f)


def load_triples() -> list[dict]:
    """Load relationship triples."""
    with open(TRIPLES_FILE) as f:
        return json.load(f)


def normalize_id(title: str) -> str:
    """Create a slug from title."""
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:60]


def extract_concepts_for_position(position: dict, seed_concepts: dict) -> list[tuple[str, float]]:
    """
    Extract concepts for a single position based on keyword matching.
    Returns list of (concept_id, strength) tuples.
    """
    title = position.get("title", "").lower()
    insight = position.get("insight_preview", "").lower()
    domain = position.get("domain", "")
    
    combined_text = f"{title} {insight}"
    matches = []
    
    for concept_id, concept_data in seed_concepts.items():
        score = 0.0
        
        # Keyword matching
        for keyword in concept_data["keywords"]:
            if keyword.lower() in combined_text:
                # Title match is stronger than insight match
                if keyword.lower() in title:
                    score += 0.4
                else:
                    score += 0.2
        
        # Domain bonus
        if domain in concept_data.get("domains", []):
            score += 0.1
        
        # Threshold for inclusion
        if score >= 0.2:
            matches.append((concept_id, min(score, 1.0)))
    
    return matches


def build_concept_graph(positions: list[dict], seed_concepts: dict) -> tuple[list[dict], list[dict]]:
    """
    Build concepts list and thought-concept edges.
    """
    concept_thoughts = defaultdict(list)
    edges = []
    
    for pos in positions:
        thought_id = pos.get("id", normalize_id(pos.get("title", "")))
        matches = extract_concepts_for_position(pos, seed_concepts)
        
        for concept_id, strength in matches:
            concept_thoughts[concept_id].append(thought_id)
            edges.append({
                "thought_id": thought_id,
                "concept_id": concept_id,
                "strength": round(strength, 2)
            })
    
    # Build concepts with counts
    concepts = []
    for concept_id, concept_data in seed_concepts.items():
        thought_count = len(concept_thoughts[concept_id])
        if thought_count > 0:  # Only include concepts that matched something
            concepts.append({
                "id": concept_id,
                "label": concept_data["label"],
                "description": concept_data["description"],
                "thought_count": thought_count,
                "domains": concept_data["domains"]
            })
    
    # Sort by thought count
    concepts.sort(key=lambda x: -x["thought_count"])
    
    return concepts, edges


def find_orphan_thoughts(positions: list[dict], edges: list[dict]) -> list[str]:
    """Find thoughts with no concept connections."""
    connected = {e["thought_id"] for e in edges}
    orphans = []
    for pos in positions:
        thought_id = pos.get("id", normalize_id(pos.get("title", "")))
        if thought_id not in connected:
            orphans.append(thought_id)
    return orphans


def main(dry_run: bool = False):
    print("Loading positions data...")
    positions = load_positions()
    print(f"  Loaded {len(positions)} positions")
    
    print("\nExtracting concepts...")
    concepts, edges = build_concept_graph(positions, SEED_CONCEPTS)
    
    print(f"\n=== Results ===")
    print(f"Concepts extracted: {len(concepts)}")
    print(f"Thought-concept edges: {len(edges)}")
    
    # Find orphans
    orphans = find_orphan_thoughts(positions, edges)
    print(f"Orphan thoughts (no concepts): {len(orphans)}")
    
    print(f"\n=== Top 10 Concepts by Connectivity ===")
    for c in concepts[:10]:
        print(f"  {c['label']}: {c['thought_count']} thoughts")
    
    if orphans:
        print(f"\n=== Sample Orphan Thoughts (first 5) ===")
        for o in orphans[:5]:
            print(f"  - {o}")
    
    if dry_run:
        print("\n[DRY RUN] Would write to:")
        print(f"  - {DATA_DIR}/concepts.json")
        print(f"  - {DATA_DIR}/thought_concept_edges.json")
        return
    
    # Write outputs
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(DATA_DIR / "concepts.json", "w") as f:
        json.dump({"concepts": concepts}, f, indent=2)
    print(f"\nWrote {DATA_DIR}/concepts.json")
    
    with open(DATA_DIR / "thought_concept_edges.json", "w") as f:
        json.dump({"edges": edges}, f, indent=2)
    print(f"Wrote {DATA_DIR}/thought_concept_edges.json")
    
    # Summary stats
    avg_concepts_per_thought = len(edges) / len(positions) if positions else 0
    print(f"\n=== Summary Stats ===")
    print(f"Average concepts per thought: {avg_concepts_per_thought:.1f}")
    print(f"Concept coverage: {(len(positions) - len(orphans)) / len(positions) * 100:.0f}%")


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
