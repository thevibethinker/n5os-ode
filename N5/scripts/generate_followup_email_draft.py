#!/usr/bin/env python3
"""
Generate Follow-Up Email Draft (Tag-Aware + v11.0 Body Generation)
Orchestrates tag query, dial calibration, V-OS generation, and complete email creation

Author: Zo Computer
Version: 2.0.0 (with v11.0 body generation)
"""

import argparse
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
from email_body_generator import (
    load_transcript,
    load_stakeholder_profile,
    extract_resonant_details,
    extract_language_patterns,
    select_confident_links,
    generate_email_body,
    apply_compression_pass,
    validate_readability
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('generate_followup_email_draft')


def generate_email_draft(
    recipient_email: str,
    meeting_folder: str,
    transcript_text: Optional[str] = None,
    generate_body: bool = True
) -> Dict:
    """
    Generate follow-up email draft with tag-aware calibration and v11.0 body generation
    
    Args:
        recipient_email: External stakeholder email
        meeting_folder: Path to meeting folder
        transcript_text: Optional transcript content
        generate_body: If True, generate full email body; if False, placeholder only
        
    Returns:
        Dict with email draft content, dial settings, V-OS tags, readability metrics
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
    
    # NEW: Step 4: Generate email body (v11.0)
    email_body = None
    readability_metrics = None
    
    if generate_body:
        logger.info("Generating email body (v11.0 spec)")
        
        # Load context
        transcript = load_transcript(meeting_folder) if not transcript_text else transcript_text
        profile = load_stakeholder_profile(meeting_folder)
        
        # Extract features
        resonance = extract_resonant_details(transcript, profile)
        language_patterns = extract_language_patterns(transcript)
        links = select_confident_links(profile, meeting_folder)
        
        # Extract recipient first name
        recipient_name = extract_first_name(recipient_email, profile)
        
        # Generate body
        context = {
            "dial_settings": dial_settings,
            "resonance": resonance,
            "language_patterns": language_patterns,
            "links": links,
            "stakeholder_profile": profile,
            "recipient_name": recipient_name
        }
        
        email_body = generate_email_body(context)
        email_body = apply_compression_pass(email_body, target_words=300)
        readability_metrics = validate_readability(email_body)
        
        logger.info(f"✓ Email body generated: {readability_metrics['word_count']} words")
    
    # Step 5: Assemble email with generated or placeholder body
    if email_body:
        recipient_name = extract_first_name(recipient_email, load_stakeholder_profile(meeting_folder))
        email_content = "**Subject:** Follow-Up Email – {} x Careerspan\n\n{}".format(recipient_name, email_body)
    else:
        email_content = f"""**Subject:** Follow-Up Email – [FirstName] x Careerspan [keyword1 • keyword2]

Hi [FirstName],

[Email body will be generated using v11.0 spec with the dial settings above]

[This is where the actual email content goes, calibrated based on:
- Relationship depth: {dial_settings.get('relationshipDepth')} 
- Formality: {dial_settings.get('formality')}/10
- Warmth: {dial_settings.get('warmth')}/10
- CTA rigour: {dial_settings.get('ctaRigour')}]

Looking forward to [appropriate closing based on relationship depth].
"""
    
    # Step 6: Add readability metrics (if body was generated)
    if readability_metrics:
        metrics_section = f"""\n**Readability Metrics:**
  - Word count: {readability_metrics['word_count']}
  - Avg sentence length: {readability_metrics['avg_sentence_length']} words
  - Flesch-Kincaid grade: {readability_metrics['flesch_kincaid_grade']}
  - Validation: {'✓ PASSED' if readability_metrics['validation_passed'] else '⚠ REVIEW NEEDED'}\n"""
        header = header + metrics_section
    
    # Step 7: Append V-OS tag string (if applicable)
    if vos_string:
        email_footer = f"\n{vos_string}\n"
    else:
        email_footer = "\n"
    
    # Combine all parts
    full_draft = header + email_content + email_footer
    
    return {
        "draft_content": full_draft,
        "recipient": recipient_email,
        "profile_found": profile_found,
        "tags": tags,
        "dial_settings": dial_settings,
        "vos_string": vos_string,
        "vos_details": vos_result,
        "readability_metrics": readability_metrics,
        "body_generated": email_body is not None,
        "output_path": f"{meeting_folder}/follow_up_email_DRAFT.md"
    }


def extract_first_name(email: str, profile: Optional[Dict]) -> str:
    """Extract first name from email or profile."""
    # Try profile first
    if profile and "raw_text" in profile:
        # Look for "STAKEHOLDER_PROFILE: FirstName LastName"
        import re
        match = re.search(r'STAKEHOLDER_PROFILE:\s+(\w+)', profile["raw_text"])
        if match:
            return match.group(1)
    
    # Fallback: use email prefix
    name = email.split('@')[0].split('.')[0]
    return name.capitalize()


def save_email_draft(draft_result: Dict) -> str:
    """Save email draft to meeting folder"""
    
    output_path = Path(draft_result["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(draft_result["draft_content"])
    
    logger.info(f"✓ Email draft saved: {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate follow-up email draft with v11.0 body generation")
    parser.add_argument("--email", help="Recipient email (default: hamoon@futurefit.ai)", 
                       default="hamoon@futurefit.ai")
    parser.add_argument("--meeting-folder", help="Meeting folder path",
                       default="/home/workspace/N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing file")
    parser.add_argument("--no-body", action="store_true", help="Skip body generation (header only)")
    
    args = parser.parse_args()
    
    result = generate_email_draft(
        recipient_email=args.email,
        meeting_folder=args.meeting_folder,
        generate_body=not args.no_body
    )
    
    if not args.dry_run:
        output_path = save_email_draft(result, args.meeting_folder)
        logger.info(f"✓ Saved to: {output_path}")
    else:
        logger.info("[DRY RUN] Preview only, no file written")
    
    print("="*70)
    print("EMAIL DRAFT PREVIEW (Hamoon):")
    print("="*70)
    print(result["draft_content"])
    print("="*70)


if __name__ == "__main__":
    main()
