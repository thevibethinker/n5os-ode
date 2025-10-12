#!/usr/bin/env python3
"""
Generate Follow-Up Email Draft (Tag-Aware)
Orchestrates tag query, dial calibration, V-OS generation, and email creation

Author: Zo Computer
Version: 1.0.0
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import our tag integration modules
sys.path.insert(0, str(Path(__file__).parent))
from query_stakeholder_tags import query_stakeholder_tags
from map_tags_to_dials import map_tags_to_dials
from map_tags_to_vos import map_tags_to_vos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('generate_followup_email_draft')


def generate_email_draft(
    recipient_email: str,
    meeting_folder: str,
    transcript_text: Optional[str] = None
) -> Dict:
    """
    Generate follow-up email draft with tag-aware calibration
    
    Args:
        recipient_email: External stakeholder email
        meeting_folder: Path to meeting folder
        transcript_text: Optional transcript content (for email body generation)
        
    Returns:
        Dict with email draft content, dial settings, V-OS tags
    """
    
    logger.info(f"Generating email draft for {recipient_email}")
    
    # Step 1: Query stakeholder tags
    tag_result = query_stakeholder_tags(recipient_email, meeting_folder)
    
    tags = tag_result.get("tags", [])
    profile_found = tag_result.get("profile_found", False)
    
    if profile_found:
        logger.info(f"✓ Profile found: {len(tags)} tags loaded")
    else:
        logger.info("✗ No profile found - using default dial settings")
    
    # Step 2: Map tags to dial settings
    dial_settings = map_tags_to_dials(tags)
    
    logger.info(f"Dial settings: relationship={dial_settings.get('relationshipDepth')}, "
                f"formality={dial_settings.get('formality')}, "
                f"warmth={dial_settings.get('warmth')}, "
                f"ctaRigour={dial_settings.get('ctaRigour')}")
    
    # Step 3: Generate V-OS tags
    vos_result = map_tags_to_vos(tags)
    vos_string = vos_result.get("vos_string", "")
    
    if vos_string:
        logger.info(f"V-OS tags: {vos_string}")
    else:
        logger.info(f"No V-OS tags (reason: {vos_result.get('reason', 'unknown')})")
    
    # Step 4: Build email draft header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
    
    header = f"""---
**DRAFT FOLLOW-UP EMAIL** (Local Generation — Not in Gmail)
**Generated:** {timestamp}
**Recipient:** {recipient_email}
**Profile:** {tag_result.get('profile_path', 'Not found')}
**Tags Used:** {', '.join(tags) if tags else 'None (using defaults)'}
**Dial Calibration:**
  - relationshipDepth: {dial_settings.get('relationshipDepth', 'N/A')}
  - formality: {dial_settings.get('formality', 'N/A')}/10
  - warmth: {dial_settings.get('warmth', 'N/A')}/10
  - ctaRigour: {dial_settings.get('ctaRigour', 'N/A')}
**V-OS Tags:** {vos_string if vos_string else '(none - N5-only stakeholder or no tags)'}
---

📧 **REMINDER:** CC va@zo.computer when sending to enable response tracking

---
"""
    
    # Step 5: Generate email body (placeholder - will call v11.0 generator)
    # For now, return structure for manual generation
    
    email_body_placeholder = f"""**Subject:** Follow-Up Email – [FirstName] x Careerspan [keyword1 • keyword2]

Hi [FirstName],

[Email body will be generated using v11.0 spec with the dial settings above]

[This is where the actual email content goes, calibrated based on:
- Relationship depth: {dial_settings.get('relationshipDepth')} 
- Formality: {dial_settings.get('formality')}/10
- Warmth: {dial_settings.get('warmth')}/10
- CTA rigour: {dial_settings.get('ctaRigour')}]

Looking forward to [appropriate closing based on relationship depth].
"""
    
    # Step 6: Append V-OS tag string (if applicable)
    if vos_string:
        email_footer = f"\n{vos_string}\n"
    else:
        email_footer = "\n"
    
    # Combine all parts
    full_draft = header + email_body_placeholder + email_footer
    
    return {
        "draft_content": full_draft,
        "recipient": recipient_email,
        "profile_found": profile_found,
        "tags": tags,
        "dial_settings": dial_settings,
        "vos_string": vos_string,
        "vos_details": vos_result,
        "output_path": f"{meeting_folder}/follow_up_email_DRAFT.md"
    }


def save_email_draft(draft_result: Dict) -> str:
    """Save email draft to meeting folder"""
    
    output_path = Path(draft_result["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(draft_result["draft_content"])
    
    logger.info(f"✓ Email draft saved: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    # Test with Hamoon
    hamoon_folder = "/home/workspace/N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit"
    
    result = generate_email_draft(
        recipient_email="hamoon@futurefit.com",
        meeting_folder=hamoon_folder
    )
    
    print("="*70)
    print("EMAIL DRAFT PREVIEW (Hamoon):")
    print("="*70)
    print(result["draft_content"])
    print("="*70)
    
    # Save to meeting folder
    saved_path = save_email_draft(result)
    print(f"\n✓ Saved to: {saved_path}")
