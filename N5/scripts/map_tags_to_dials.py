#!/usr/bin/env python3
"""
Map Tags to Email Dial Settings
Convert stakeholder tags to email tone calibration settings

Author: Zo Computer
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('map_tags_to_dials')


def load_dial_mapping() -> Dict:
    """Load dial mapping configuration"""
    
    config_path = Path("/home/workspace/N5/config/tag_dial_mapping.json")
    if not config_path.exists():
        config_path = Path("/home/workspace/N5_mirror/config/tag_dial_mapping.json")
    
    if not config_path.exists():
        logger.error("Dial mapping config not found")
        return {}
    
    return json.loads(config_path.read_text())


def map_tags_to_dials(tags: List[str]) -> Dict:
    """
    Convert hashtags to email dial settings
    
    Args:
        tags: List of hashtags from stakeholder profile
        
    Returns:
        Dict with relationshipDepth, formality, warmth, ctaRigour
    """
    
    mapping = load_dial_mapping()
    if not mapping:
        return mapping.get("defaults", {})
    
    # Start with defaults
    dials = mapping.get("defaults", {}).copy()
    
    # Apply relationship mapping (primary driver)
    relationship_tag = None
    for tag in tags:
        if tag.startswith("#relationship:"):
            relationship_tag = tag
            break
    
    if relationship_tag and relationship_tag in mapping.get("relationship_mappings", {}):
        rel_settings = mapping["relationship_mappings"][relationship_tag]
        dials.update({
            "relationshipDepth": rel_settings["relationshipDepth"],
            "formality": rel_settings["formality"],
            "warmth": rel_settings["warmth"],
            "ctaRigour": rel_settings["ctaRigour"]
        })
        logger.info(f"Applied relationship settings: {relationship_tag}")
    
    # Apply stakeholder adjustments (formality boost)
    stakeholder_tag = None
    for tag in tags:
        if tag.startswith("#stakeholder:"):
            stakeholder_tag = tag
            break
    
    if stakeholder_tag:
        # Check for exact match
        if stakeholder_tag in mapping.get("stakeholder_adjustments", {}):
            adjustment = mapping["stakeholder_adjustments"][stakeholder_tag]
            formality_boost = adjustment.get("formality_boost", 0)
            dials["formality"] = max(1, min(10, dials.get("formality", 7) + formality_boost))
            logger.info(f"Applied stakeholder adjustment: {stakeholder_tag} (formality {formality_boost:+d})")
        
        # Check for investor (auto-adds critical priority)
        if stakeholder_tag == "#stakeholder:investor":
            dials["formality"] = min(10, dials.get("formality", 7) + 1)
    
    # Apply priority adjustments (urgency metadata)
    priority_tag = None
    for tag in tags:
        if tag.startswith("#priority:"):
            priority_tag = tag
            break
    
    if priority_tag and priority_tag in mapping.get("priority_adjustments", {}):
        dials["urgency"] = mapping["priority_adjustments"][priority_tag]["urgency"]
    
    # Ensure dials are within bounds
    dials["relationshipDepth"] = max(0, min(3, dials.get("relationshipDepth", 1)))
    dials["formality"] = max(1, min(10, dials.get("formality", 7)))
    dials["warmth"] = max(1, min(10, dials.get("warmth", 5)))
    dials["ctaRigour"] = max(1, min(4, dials.get("ctaRigour", 2)))
    
    # Add metadata
    dials["tags_used"] = tags
    dials["relationship_tag"] = relationship_tag
    dials["stakeholder_tag"] = stakeholder_tag
    dials["priority_tag"] = priority_tag
    
    return dials


if __name__ == "__main__":
    # Test with Hamoon
    hamoon_tags = [
        "#stakeholder:partner:collaboration",
        "#relationship:new",
        "#priority:normal",
        "#engagement:needs_followup",
        "#context:hr_tech"
    ]
    
    result = map_tags_to_dials(hamoon_tags)
    print("Hamoon (Partnership, New Relationship):")
    print(json.dumps(result, indent=2))
    
    # Test with Alex
    alex_tags = [
        "#stakeholder:advisor",
        "#relationship:active",
        "#priority:high",
        "#context:enterprise",
        "#engagement:responsive"
    ]
    
    print("\n" + "="*50 + "\n")
    result2 = map_tags_to_dials(alex_tags)
    print("Alex (Advisor, Active Relationship):")
    print(json.dumps(result2, indent=2))
    
    # Test with no tags (fallback)
    print("\n" + "="*50 + "\n")
    result3 = map_tags_to_dials([])
    print("No Tags (Fallback to Defaults):")
    print(json.dumps(result3, indent=2))
