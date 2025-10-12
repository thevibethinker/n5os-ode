#!/usr/bin/env python3
"""
Map Tags to V-OS Brackets
Convert N5 hashtags to Howie V-OS bracket notation

Author: Zo Computer
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('map_tags_to_vos')


def load_vos_mapping() -> Dict:
    """Load V-OS mapping configuration"""
    
    config_path = Path("/home/workspace/N5/config/tag_vos_mapping.json")
    if not config_path.exists():
        config_path = Path("/home/workspace/N5_mirror/config/tag_vos_mapping.json")
    
    if not config_path.exists():
        logger.error("V-OS mapping config not found")
        return {}
    
    return json.loads(config_path.read_text())


def is_n5_only_tag(tag: str, mapping: Dict) -> bool:
    """Check if tag is N5-only (not synced to Howie)"""
    
    n5_only = mapping.get("n5_only_tags", [])
    
    # Check exact match
    if tag in n5_only:
        return True
    
    # Check prefix match (e.g., #relationship:* matches #relationship:new)
    for n5_tag in n5_only:
        if n5_tag.endswith(":*"):
            prefix = n5_tag[:-1]  # Remove *
            if tag.startswith(prefix):
                return True
    
    return False


def map_tags_to_vos(tags: List[str]) -> Dict:
    """
    Convert hashtags to V-OS bracket notation
    
    Args:
        tags: List of hashtags from stakeholder profile
        
    Returns:
        Dict with vos_string, vos_tags list, and metadata
    """
    
    if not tags:
        return {
            "vos_string": "",
            "vos_tags": [],
            "has_vos_tags": False,
            "n5_only": True,
            "reason": "No tags provided"
        }
    
    mapping = load_vos_mapping()
    if not mapping:
        return {
            "vos_string": "",
            "vos_tags": [],
            "has_vos_tags": False,
            "error": "Failed to load V-OS mapping"
        }
    
    vos_tags = []
    n5_only_tags = []
    
    # Check if stakeholder is N5-only (e.g., advisor)
    stakeholder_tags = [t for t in tags if t.startswith("#stakeholder:")]
    has_n5_only_stakeholder = any(is_n5_only_tag(t, mapping) for t in stakeholder_tags)
    
    if has_n5_only_stakeholder:
        # If stakeholder is N5-only, no V-OS tags at all
        return {
            "vos_string": "",
            "vos_tags": [],
            "has_vos_tags": False,
            "n5_only": True,
            "n5_only_tags": tags,
            "reason": f"Stakeholder type is N5-only (e.g., advisor) - no Howie sync"
        }
    
    # Process each tag
    for tag in tags:
        # Check if N5-only
        if is_n5_only_tag(tag, mapping):
            n5_only_tags.append(tag)
            continue
        
        # Check stakeholder mappings
        if tag in mapping.get("stakeholder_mappings", {}):
            vos_tag = mapping["stakeholder_mappings"][tag]
            if vos_tag:  # Not null
                vos_tags.append(vos_tag)
        
        # Check priority mappings
        elif tag in mapping.get("priority_mappings", {}):
            vos_tag = mapping["priority_mappings"][tag]
            if vos_tag:
                vos_tags.append(vos_tag)
        
        # Check schedule mappings
        elif tag in mapping.get("schedule_mappings", {}):
            vos_tag = mapping["schedule_mappings"][tag]
            if vos_tag:
                vos_tags.append(vos_tag)
        
        # Check coordination mappings
        elif tag in mapping.get("coordination_mappings", {}):
            vos_tag = mapping["coordination_mappings"][tag]
            if vos_tag:
                vos_tags.append(vos_tag)
        
        # Check engagement mappings (activation asterisk)
        elif tag in mapping.get("engagement_mappings", {}):
            vos_tag = mapping["engagement_mappings"][tag]
            if vos_tag:
                vos_tags.append(vos_tag)
    
    # Apply auto-inheritance rules
    for tag in tags:
        if tag in mapping.get("auto_inheritance", {}):
            rules = mapping["auto_inheritance"][tag]
            
            # Add inherited V-OS tags
            if "vos_tags" in rules:
                for vos_tag in rules["vos_tags"]:
                    if vos_tag not in vos_tags:
                        vos_tags.append(vos_tag)
            
            # Add default priority if not present
            if "vos_default_priority" in rules:
                # Check if any priority tag already present
                has_priority = any(t.startswith("[A-") or t == "[!!]" for t in vos_tags)
                if not has_priority:
                    vos_tags.append(rules["vos_default_priority"])
    
    # Build final V-OS string
    if not vos_tags:
        return {
            "vos_string": "",
            "vos_tags": [],
            "has_vos_tags": False,
            "n5_only": True,
            "n5_only_tags": n5_only_tags,
            "reason": "All tags are N5-only (e.g., #stakeholder:advisor)"
        }
    
    # Sort tags by category order (stakeholder, timing, priority, coordination, followup)
    def sort_key(tag):
        if tag.startswith("[LD-"):
            return 0  # Stakeholder category first
        elif tag in ["[!!]", "[D5]", "[D5+]", "[D10]"]:
            return 1  # Timing second
        elif tag.startswith("[A-"):
            return 2  # Priority third
        elif tag in ["[LOG]", "[ILS]"]:
            return 3  # Coordination fourth
        elif tag == "*":
            return 9  # Activation asterisk last
        else:
            return 5  # Other
    
    vos_tags_sorted = sorted(set(vos_tags), key=sort_key)
    vos_string = " ".join(vos_tags_sorted)
    
    return {
        "vos_string": vos_string,
        "vos_tags": vos_tags_sorted,
        "has_vos_tags": True,
        "n5_only": False,
        "n5_only_tags": n5_only_tags,
        "input_tags": tags
    }


if __name__ == "__main__":
    # Test with Hamoon's tags
    hamoon_tags = [
        "#stakeholder:partner:collaboration",
        "#relationship:new",
        "#priority:normal",
        "#engagement:needs_followup",
        "#context:hr_tech"
    ]
    
    result = map_tags_to_vos(hamoon_tags)
    print("Hamoon (Partnership):")
    print(json.dumps(result, indent=2))
    print(f"\nV-OS String: {result['vos_string']}")
    
    # Test with Alex's tags (advisor - N5 only)
    alex_tags = [
        "#stakeholder:advisor",
        "#relationship:active",
        "#priority:high",
        "#context:enterprise",
        "#engagement:responsive"
    ]
    
    print("\n" + "="*50 + "\n")
    result2 = map_tags_to_vos(alex_tags)
    print("Alex (Advisor):")
    print(json.dumps(result2, indent=2))
    print(f"\nV-OS String: {result2['vos_string']}")
