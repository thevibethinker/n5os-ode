#!/usr/bin/env python3
"""
Integrate Follow-Up Email with B25
Called during meeting processing to auto-generate tag-aware email draft

Author: Zo Computer  
Version: 1.0.0
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, Optional

# Import tag integration modules
sys.path.insert(0, str(Path(__file__).parent))
from query_stakeholder_tags import query_stakeholder_tags
from map_tags_to_dials import map_tags_to_dials
from map_tags_to_vos import map_tags_to_vos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('integrate_email_with_b25')


def extract_recipient_email(meeting_folder: Path) -> Optional[str]:
    """
    Extract external recipient email from meeting folder
    
    Checks:
    1. stakeholder_profile.md
    2. _metadata.json
    3. Meeting folder name
    """
    
    # Check stakeholder profile first
    profile_path = meeting_folder / "stakeholder_profile.md"
    if profile_path.exists():
        content = profile_path.read_text()
        email_match = re.search(r'\*\*Email\*\*:\s*([^\s\n]+@[^\s\n]+)', content)
        if email_match:
            return email_match.group(1)
    
    # Check metadata
    metadata_path = meeting_folder / "_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            if "recipient_email" in metadata:
                return metadata["recipient_email"]
        except:
            pass
    
    logger.warning(f"Could not extract recipient email from {meeting_folder}")
    return None


def generate_email_header(
    recipient_email: str,
    profile_path: Optional[str],
    tags: list,
    dial_settings: dict,
    vos_string: str
) -> str:
    """Generate email draft header with metadata"""
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
    
    tags_display = ', '.join(tags) if tags else 'None (using defaults)'
    
    header = f"""---
**DRAFT FOLLOW-UP EMAIL** (Local Generation — Not in Gmail)
**Generated:** {timestamp}
**Recipient:** {recipient_email}
**Profile:** {profile_path or 'Not found'}
**Tags Used:** {tags_display}
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
    return header


def integrate_email_generation(
    meeting_folder: str,
    recipient_email: Optional[str] = None
) -> Dict:
    """
    Main integration function for B25 email generation
    
    Args:
        meeting_folder: Path to meeting folder
        recipient_email: Optional recipient email (will auto-detect if not provided)
        
    Returns:
        Dict with generation results
    """
    
    folder_path = Path(meeting_folder)
    logger.info(f"Starting email generation for: {folder_path.name}")
    
    # Step 1: Extract recipient email
    if not recipient_email:
        recipient_email = extract_recipient_email(folder_path)
    
    if not recipient_email:
        logger.error("No recipient email found - cannot generate email")
        return {
            "success": False,
            "error": "No recipient email found",
            "meeting_folder": str(folder_path)
        }
    
    logger.info(f"Recipient: {recipient_email}")
    
    # Step 2: Query stakeholder tags
    tag_result = query_stakeholder_tags(recipient_email, str(folder_path))
    tags = tag_result.get("tags", [])
    profile_found = tag_result.get("profile_found", False)
    profile_path = tag_result.get("profile_path")
    
    if profile_found:
        logger.info(f"✓ Profile found: {len(tags)} tags loaded")
    else:
        logger.info("✗ No profile - using default dial settings")
    
    # Step 3: Map to dials
    dial_settings = map_tags_to_dials(tags)
    logger.info(f"Dial settings: depth={dial_settings.get('relationshipDepth')}, "
                f"formality={dial_settings.get('formality')}, "
                f"warmth={dial_settings.get('warmth')}, "
                f"ctaRigour={dial_settings.get('ctaRigour')}")
    
    # Step 4: Generate V-OS tags
    vos_result = map_tags_to_vos(tags)
    vos_string = vos_result.get("vos_string", "")
    
    if vos_string:
        logger.info(f"V-OS tags: {vos_string}")
    else:
        logger.info(f"No V-OS tags: {vos_result.get('reason', 'unknown')}")
    
    # Step 5: Generate header
    header = generate_email_header(
        recipient_email=recipient_email,
        profile_path=profile_path,
        tags=tags,
        dial_settings=dial_settings,
        vos_string=vos_string
    )
    
    # Step 6: Build email body placeholder
    # (v11.0 generator will be called by Zo to fill this in)
    body_placeholder = f"""**Subject:** Follow-Up Email – [FirstName] x Careerspan [keyword1 • keyword2]

Hi [FirstName],

[Email body will be generated using v11.0 follow-up-email-generator.md]

[Zo will generate the email body based on:
- Meeting transcript analysis
- Dial settings: relationshipDepth={dial_settings.get('relationshipDepth')}, formality={dial_settings.get('formality')}, warmth={dial_settings.get('warmth')}, ctaRigour={dial_settings.get('ctaRigour')}
- Resonant details from conversation
- Deliverables from B25 table
- V's distinctive phrases (max 2)
- Readability constraints (FK ≤ 10)]

Looking forward to connecting further.
"""
    
    # Step 7: Append V-OS tags
    footer = f"\n{vos_string}\n" if vos_string else "\n"
    
    # Step 8: Combine
    full_draft = header + body_placeholder + footer
    
    # Step 9: Save to B25 file
    b25_path = folder_path / "B25_DELIVERABLE_CONTENT_MAP.md"
    
    # Check if B25 already exists
    if b25_path.exists():
        # Append email section
        existing_content = b25_path.read_text()
        
        # Check if email already present
        if "DRAFT FOLLOW-UP EMAIL" in existing_content:
            logger.info("Email draft already exists in B25 - skipping")
            return {
                "success": True,
                "already_exists": True,
                "b25_path": str(b25_path)
            }
        
        # Append to existing B25
        updated_content = existing_content + "\n\n---\n\n## Follow-Up Email Draft\n\n" + full_draft
        b25_path.write_text(updated_content)
        logger.info(f"✓ Email draft appended to existing B25: {b25_path}")
    else:
        # Create new B25 with email
        b25_content = f"""# B25 - DELIVERABLE CONTENT MAP + FOLLOW-UP EMAIL

## Section 1: Deliverable Content Map

| Item | Promised By | Promised When | Status | Link/File | Send with Email |
|------|-------------|---------------|--------|-----------|-----------------|
| [Add deliverables here] | | | | | |

---

## Section 2: Follow-Up Email Draft

{full_draft}
"""
        b25_path.write_text(b25_content)
        logger.info(f"✓ Email draft saved to new B25: {b25_path}")
    
    return {
        "success": True,
        "recipient": recipient_email,
        "profile_found": profile_found,
        "tags": tags,
        "dial_settings": dial_settings,
        "vos_string": vos_string,
        "b25_path": str(b25_path),
        "meeting_folder": str(folder_path)
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 integrate_email_with_b25.py <meeting_folder> [recipient_email]")
        sys.exit(1)
    
    meeting_folder = sys.argv[1]
    recipient_email = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = integrate_email_generation(meeting_folder, recipient_email)
    
    print("\n" + "="*70)
    print("EMAIL INTEGRATION RESULT:")
    print("="*70)
    print(json.dumps(result, indent=2))
    
    if result.get("success"):
        print(f"\n✓ Email draft saved to: {result['b25_path']}")
    else:
        print(f"\n✗ Failed: {result.get('error')}")
