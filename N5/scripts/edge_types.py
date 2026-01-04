#!/usr/bin/env python3
"""
Edge Types: Canonical vocabulary for context graph relations.

This module defines the allowed edge types and provides validation.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum

class EdgeCategory(Enum):
    PROVENANCE = "provenance"    # Who/where did this come from
    STANCE = "stance"            # Positions on ideas
    EXPECTATION = "expectation"  # Forward-looking outcomes
    CHAIN = "chain"              # Logical dependencies


@dataclass
class EdgeType:
    relation: str
    category: EdgeCategory
    description: str
    inverse: Optional[str] = None
    
    def __str__(self):
        return self.relation


# Canonical edge types
EDGE_TYPES: Dict[str, EdgeType] = {
    # Provenance
    "originated_by": EdgeType(
        relation="originated_by",
        category=EdgeCategory.PROVENANCE,
        description="Who first surfaced this idea/decision",
        inverse="originated"
    ),
    "influenced_by": EdgeType(
        relation="influenced_by",
        category=EdgeCategory.PROVENANCE,
        description="Shaped my thinking without being the origin",
        inverse="influenced"
    ),
    
    # Stance
    "supported_by": EdgeType(
        relation="supported_by",
        category=EdgeCategory.STANCE,
        description="Endorsed or validated",
        inverse="supports"
    ),
    "challenged_by": EdgeType(
        relation="challenged_by",
        category=EdgeCategory.STANCE,
        description="Pushed back or questioned",
        inverse="challenges"
    ),
    
    # Expectation
    "hoped_for": EdgeType(
        relation="hoped_for",
        category=EdgeCategory.EXPECTATION,
        description="Expected positive outcome"
    ),
    "concerned_about": EdgeType(
        relation="concerned_about",
        category=EdgeCategory.EXPECTATION,
        description="Worried about negative outcome"
    ),
    
    # Chain
    "preceded_by": EdgeType(
        relation="preceded_by",
        category=EdgeCategory.CHAIN,
        description="Earlier version or precursor",
        inverse="preceded"
    ),
    "depends_on": EdgeType(
        relation="depends_on",
        category=EdgeCategory.CHAIN,
        description="Logical prerequisite",
        inverse="enables"
    ),
    "supersedes": EdgeType(
        relation="supersedes",
        category=EdgeCategory.CHAIN,
        description="Replaces earlier decision",
        inverse="superseded_by"
    ),
    
    # Position-related (Phase 4.5)
    "crystallized_from": EdgeType(
        relation="crystallized_from",
        category=EdgeCategory.CHAIN,
        description="Position formed from accumulated evidence",
        inverse="contributed_to"
    ),
    "supports_position": EdgeType(
        relation="supports_position",
        category=EdgeCategory.STANCE,
        description="Edge evidence supports this position",
        inverse="supported_by_edge"
    ),
    "challenges_position": EdgeType(
        relation="challenges_position",
        category=EdgeCategory.STANCE,
        description="Edge evidence challenges this position",
        inverse="challenged_by_edge"
    ),
}


# Valid entity types
ENTITY_TYPES = {"person", "idea", "decision", "meeting", "position", "commitment", "outcome"}


def validate_relation(relation: str) -> bool:
    """Check if relation is in canonical vocabulary."""
    return relation in EDGE_TYPES


def validate_entity_type(entity_type: str) -> bool:
    """Check if entity type is valid."""
    return entity_type in ENTITY_TYPES


def get_edge_type(relation: str) -> Optional[EdgeType]:
    """Get EdgeType object for a relation."""
    return EDGE_TYPES.get(relation)


def get_inverse(relation: str) -> Optional[str]:
    """Get inverse relation for bidirectional queries."""
    edge_type = EDGE_TYPES.get(relation)
    return edge_type.inverse if edge_type else None


def list_relations_by_category(category: EdgeCategory) -> List[str]:
    """Get all relations in a category."""
    return [et.relation for et in EDGE_TYPES.values() if et.category == category]


def generate_slug(text: str, prefix: str = "") -> str:
    """Generate a URL-safe slug from text."""
    import re
    # Lowercase, replace spaces with hyphens, remove non-alphanumeric
    slug = text.lower().strip()
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    slug = re.sub(r'-+', '-', slug)  # Collapse multiple hyphens
    slug = slug.strip('-')
    
    # Truncate to reasonable length
    if len(slug) > 50:
        slug = slug[:50].rsplit('-', 1)[0]
    
    return f"{prefix}:{slug}" if prefix else slug


if __name__ == "__main__":
    print("=== Edge Types ===\n")
    for category in EdgeCategory:
        print(f"\n{category.value.upper()}:")
        for relation in list_relations_by_category(category):
            et = EDGE_TYPES[relation]
            inv = f" (inverse: {et.inverse})" if et.inverse else ""
            print(f"  {relation}: {et.description}{inv}")
    
    print("\n\n=== Entity Types ===")
    print(", ".join(sorted(ENTITY_TYPES)))
    
    print("\n\n=== Slug Examples ===")
    print(f"  'Context Graph System' -> {generate_slug('Context Graph System', 'idea')}")
    print(f"  'Build review queue for edges' -> {generate_slug('Build review queue for edges', 'decision')}")




