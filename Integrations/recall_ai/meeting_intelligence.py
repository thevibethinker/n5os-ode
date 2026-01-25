#!/usr/bin/env python3
"""
Meeting Intelligence Layer
Determines optimal Recall config based on:
- Calendar event metadata
- Due Diligence data
- Stakeholder profiles
- Meeting patterns
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Import config
import sys
try:
    from .config import MEETING_PRESETS
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import MEETING_PRESETS

# Paths to intelligence sources
DD_PATH = Path("/home/workspace/Knowledge/market and competitor intel/due-diligence")
STAKEHOLDER_PATH = Path("/home/workspace/Personal/stakeholders")
CRM_PATH = Path("/home/workspace/Datasets/crm")


def get_stakeholder_context(email: str) -> Optional[Dict[str, Any]]:
    """
    Look up stakeholder profile by email
    
    Returns:
        Stakeholder data or None
    """
    # Check stakeholder profiles
    for profile_file in STAKEHOLDER_PATH.glob("**/profile.json"):
        try:
            with open(profile_file) as f:
                profile = json.load(f)
            if email.lower() in [e.lower() for e in profile.get("emails", [])]:
                return profile
        except Exception:
            continue
    
    return None


def get_company_dd(company_name: str) -> Optional[Dict[str, Any]]:
    """
    Look up due diligence data for a company
    
    Returns:
        DD metadata or None
    """
    # Normalize company name to slug
    slug = re.sub(r'[^a-z0-9]+', '-', company_name.lower()).strip('-')
    
    # Check DD folders
    for dd_folder in DD_PATH.glob(f"*{slug}*"):
        manifest = dd_folder / "manifest.json"
        if manifest.exists():
            try:
                with open(manifest) as f:
                    return json.load(f)
            except Exception:
                continue
    
    return None


def infer_meeting_type(event: Dict[str, Any]) -> str:
    """
    Infer meeting type from event metadata
    
    Returns:
        Meeting type: demo, interview, 1:1, panel, seminar, internal, external
    """
    title = event.get("summary", "").lower()
    description = event.get("description", "").lower()
    attendees = event.get("attendees", [])
    
    # Check explicit tags first
    combined = f"{title} {description}"
    if "[demo]" in combined:
        return "demo"
    if "[interview]" in combined:
        return "interview"
    if "[panel]" in combined:
        return "panel"
    if "[seminar]" in combined or "[webinar]" in combined:
        return "seminar"
    if "[internal]" in combined:
        return "internal"
    
    # Infer from title patterns
    demo_patterns = ["demo", "product tour", "walkthrough", "showcase", "presentation"]
    interview_patterns = ["interview", "screening", "candidate"]
    seminar_patterns = ["webinar", "seminar", "workshop", "training", "onboarding"]
    panel_patterns = ["panel", "roundtable", "discussion group"]
    
    for pattern in demo_patterns:
        if pattern in title:
            return "demo"
    
    for pattern in interview_patterns:
        if pattern in title:
            return "interview"
    
    for pattern in seminar_patterns:
        if pattern in title:
            return "seminar"
    
    for pattern in panel_patterns:
        if pattern in title:
            return "panel"
    
    # Infer from attendee count
    external_attendees = [a for a in attendees 
                         if not any(d in a.get("email", "") 
                                   for d in ["@careerspan.com", "@mycareerspan.com", "@theapply.ai"])]
    
    if len(external_attendees) == 0:
        return "internal"
    elif len(external_attendees) == 1:
        return "1:1"
    elif len(external_attendees) >= 4:
        return "panel"
    else:
        return "external"


def get_optimal_preset(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine optimal Recall config based on meeting intelligence
    
    Args:
        event: Calendar event dict
        
    Returns:
        Config overrides to merge with DEFAULT_BOT_CONFIG
    """
    config_overrides = {}
    metadata = {"intelligence_source": []}
    
    title = event.get("summary", "")
    attendees = event.get("attendees", [])
    
    # 1. Check for explicit V-OS tags (highest priority)
    for tag, preset in MEETING_PRESETS.items():
        if tag in title and preset is not None:
            logger.info(f"Applying preset from tag {tag}")
            # Merge preset (excluding internal keys)
            for key, value in preset.items():
                if not key.startswith("_"):
                    if isinstance(value, dict) and key in config_overrides:
                        config_overrides[key].update(value)
                    else:
                        config_overrides[key] = value
            metadata["intelligence_source"].append(f"tag:{tag}")
    
    # 2. Infer meeting type if no explicit tag
    if not metadata["intelligence_source"]:
        meeting_type = infer_meeting_type(event)
        metadata["inferred_meeting_type"] = meeting_type
        metadata["intelligence_source"].append(f"inferred:{meeting_type}")
        
        # Apply type-specific defaults
        type_presets = {
            "demo": {"recording_config": {"screenshare_behavior": "overlap"}},
            "interview": {"recording_config": {"video_mixed_layout": "gallery_view_v2"}},
            "panel": {"recording_config": {"video_mixed_layout": "gallery_view_v2"}},
            "seminar": {"recording_config": {"screenshare_behavior": "overlap"}},
        }
        
        if meeting_type in type_presets:
            for key, value in type_presets[meeting_type].items():
                if isinstance(value, dict) and key in config_overrides:
                    config_overrides[key].update(value)
                else:
                    config_overrides[key] = value
    
    # 3. Check stakeholder profiles for VIP handling
    for attendee in attendees:
        email = attendee.get("email", "")
        if not email:
            continue
            
        stakeholder = get_stakeholder_context(email)
        if stakeholder:
            vip_level = stakeholder.get("vip_level", 0)
            relationship = stakeholder.get("relationship_type", "")
            
            if vip_level >= 3 or relationship in ["investor", "strategic_partner", "key_customer"]:
                # VIP meetings: ensure high quality
                logger.info(f"VIP attendee detected: {email}")
                metadata["intelligence_source"].append(f"vip:{email}")
                metadata["vip_attendee"] = email
                
                # Could add VIP-specific config here
                # e.g., higher quality transcription, priority processing
    
    # 4. Check DD data for company context
    # Extract company from attendee domains
    for attendee in attendees:
        email = attendee.get("email", "")
        if "@" in email:
            domain = email.split("@")[1]
            # Skip common personal domains
            if domain not in ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]:
                company_name = domain.split(".")[0]
                dd = get_company_dd(company_name)
                if dd:
                    logger.info(f"DD data found for {company_name}")
                    metadata["intelligence_source"].append(f"dd:{company_name}")
                    metadata["dd_company"] = company_name
                    metadata["dd_stage"] = dd.get("stage", "unknown")
                    break
    
    # Store metadata for post-processing
    config_overrides["metadata"] = {
        "meeting_intelligence": metadata,
        "calendar_event_id": event.get("id"),
        "calendar_event_title": title,
    }
    
    return config_overrides


def should_record_based_on_intelligence(event: Dict[str, Any]) -> tuple[bool, str]:
    """
    Determine if meeting should be recorded based on intelligence
    
    Returns:
        (should_record, reason)
    """
    title = event.get("summary", "")
    
    # Skip markers always win
    skip_markers = ["[NR]", "[SKIP]", "[NO RECORD]", "[NORECORD]"]
    for marker in skip_markers:
        if marker in title:
            return False, f"Skip marker: {marker}"
    
    # Force record markers
    force_markers = ["[REC]", "[RECORD]"]
    for marker in force_markers:
        if marker in title:
            return True, f"Force marker: {marker}"
    
    # Check for video link
    # (Delegate to calendar_scheduler.has_video_link)
    
    return True, "default"


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with a sample event
        test_event = {
            "summary": sys.argv[1],
            "attendees": [{"email": e} for e in sys.argv[2:]] if len(sys.argv) > 2 else []
        }
        
        meeting_type = infer_meeting_type(test_event)
        print(f"Inferred meeting type: {meeting_type}")
        
        preset = get_optimal_preset(test_event)
        print(f"Optimal preset: {json.dumps(preset, indent=2)}")
    else:
        print("Usage: python meeting_intelligence.py 'Meeting Title' [attendee@email.com ...]")
