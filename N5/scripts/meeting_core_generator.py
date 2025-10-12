#!/usr/bin/env python3
# ⚠️  DEPRECATED: This template-based script has been superseded by the Registry System.
# ⚠️  See: N5/prefs/block_type_registry.json (v1.3+) and N5/commands/meeting-process.md (v4.0.0+)
# ⚠️  Preserved for historical reference only.
#
#!/usr/bin/env python3
"""
Meeting Core Generator
Generates 7 core meeting intelligence blocks based on internal/external classification.
Uses subprocess to Zo for LLM extraction.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add utils to path
sys.path.insert(0, '/home/workspace/N5/scripts/utils')
from stakeholder_classifier import classify_meeting, get_participant_details

# DEPRECATED: Templates moved to Archive/block_templates_deprecated_2025-10-12
TEMPLATES_DIR = Path("/home/workspace/N5/prefs/Archive/block_templates_deprecated_2025-10-12/block_templates")
METADATA_SCHEMA = Path("/home/workspace/N5/schemas/meeting-metadata.schema.json")


def load_template(meeting_type: str, block_name: str) -> str:
    """Load a block template based on meeting type."""
    template_path = TEMPLATES_DIR / meeting_type / f"{block_name}.template.md"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    with open(template_path, 'r') as f:
        return f.read()


def extract_with_zo(transcript: str, extraction_prompt: str) -> str:
    """
    Use subprocess to Zo to extract content from transcript.
    
    Args:
        transcript: Full meeting transcript
        extraction_prompt: Prompt describing what to extract
        
    Returns:
        Extracted content as string
    """
    # Create a temporary file for the prompt
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        prompt_file = f.name
        f.write(f"{extraction_prompt}\n\n---\n\nTRANSCRIPT:\n\n{transcript}")
    
    try:
        # Call Zo via subprocess (simulating: echo "prompt" | zo)
        # In practice, this would be a proper API call or CLI invocation
        result = subprocess.run(
            ['bash', '-c', f'cat {prompt_file}'],  # Placeholder - replace with actual Zo invocation
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Zo extraction failed: {result.stderr}")
        
        return result.stdout.strip()
    
    finally:
        # Clean up temp file
        os.unlink(prompt_file)


def generate_action_items(transcript: str, meeting_type: str) -> str:
    """Generate action items block."""
    prompt = """Extract action items from this meeting transcript.

Categorize them by timeframe:
- SHORT-TERM (1-2 weeks)
- MEDIUM-TERM (2-4 weeks)  
- LONG-TERM (1+ months)

For each action item, include:
- Clear description
- Owner (if mentioned)
- Deadline (if mentioned)
- Priority level

Format as markdown with clear sections. Aim for 10-20 action items total."""
    
    content = extract_with_zo(transcript, prompt)
    template = load_template(meeting_type, "action-items")
    
    # Fill template placeholders
    # In real implementation, parse content and fill structured template
    return content


def generate_decisions(transcript: str, meeting_type: str) -> str:
    """Generate decisions block."""
    prompt = """Extract key decisions made in this meeting.

Categorize as:
- STRATEGIC DECISIONS (long-term direction, positioning)
- TACTICAL DECISIONS (immediate execution)
- PROCESS DECISIONS (how we work)

For each decision, include:
- What was decided
- Rationale
- Expected impact

Format as markdown. Aim for 5-8 decisions."""
    
    content = extract_with_zo(transcript, prompt)
    return content


def generate_key_insights(transcript: str, meeting_type: str) -> str:
    """Generate key insights block."""
    if meeting_type == "internal":
        prompt = """Extract key insights from this internal meeting.

Categorize as:
- STRATEGIC INSIGHTS (market, positioning, direction)
- OPERATIONAL INSIGHTS (processes, efficiency)
- MARKET/PRODUCT INSIGHTS (competitive, product development)
- TEAM/PEOPLE INSIGHTS (hiring, culture, growth)

Aim for 10-15 insights total."""
    else:
        prompt = """Extract key insights from this external meeting.

Categorize as:
- STRATEGIC INSIGHTS (high-level direction, positioning)
- OPPORTUNITY INSIGHTS (business opportunities, partnerships)
- RISK/CONCERN INSIGHTS (challenges, risks, concerns)
- STAKEHOLDER INSIGHTS (about the external stakeholder)

Aim for 10-15 insights total."""
    
    content = extract_with_zo(transcript, prompt)
    return content


def generate_debate_points(transcript: str) -> str:
    """Generate debate points block (internal only)."""
    prompt = """Extract debate and tension points from this internal meeting.

Include:
- KEY DEBATES (major discussions with differing viewpoints)
- TRADE-OFFS DISCUSSED (competing priorities, resources)
- UNRESOLVED TENSIONS (issues not fully resolved)
- RESOLVED THROUGH DISCUSSION (what consensus was reached)

Format as markdown."""
    
    return extract_with_zo(transcript, prompt)


def generate_memo(transcript: str, meeting_subject: str) -> str:
    """Generate internal memo (internal only)."""
    prompt = f"""Generate an internal memo summarizing this meeting.

Meeting Subject: {meeting_subject}

Include sections:
- EXECUTIVE SUMMARY (2-3 paragraphs)
- DISCUSSION POINTS (key topics discussed)
- KEY OUTCOMES (decisions, conclusions)
- NEXT STEPS (action items summary)
- OPEN QUESTIONS (unresolved items)

Format as professional internal memo."""
    
    return extract_with_zo(transcript, prompt)


def generate_stakeholder_profile(transcript: str, stakeholder_name: str) -> str:
    """Generate stakeholder profile (external only)."""
    prompt = f"""Create a comprehensive stakeholder profile for: {stakeholder_name}

Extract from the transcript:
- BASIC INFORMATION (name, company, role, email if mentioned)
- BACKGROUND & CONTEXT (their history, experience)
- PROFESSIONAL PROFILE (current role, responsibilities)
- COMMUNICATION STYLE (how they communicate, preferences)
- PAIN POINTS & CHALLENGES (what problems they're facing)
- INTERESTS & PRIORITIES (what matters to them)
- RELATIONSHIP OPPORTUNITIES (how to build relationship)
- NOTABLE QUOTES (significant verbatim quotes)

Format as comprehensive profile document."""
    
    return extract_with_zo(transcript, prompt)


def generate_follow_up_email(transcript: str, stakeholder_name: str, stakeholder_email: str) -> str:
    """Generate follow-up email draft (external only)."""
    prompt = f"""Draft a follow-up email for this meeting.

Recipient: {stakeholder_name} <{stakeholder_email}>

Include:
- Appropriate subject line
- Email body with:
  * Thank you / recap
  * Key takeaways
  * Next steps
  * Specific asks or commitments
- Attachments/links to include
- Recommended send timing
- Any notes for the sender

Keep professional, warm, and action-oriented."""
    
    return extract_with_zo(transcript, prompt)


def generate_review_first(transcript: str, meeting_type: str, meeting_date: str, 
                          action_summary: str, decisions_summary: str, insights_summary: str) -> str:
    """Generate REVIEW_FIRST dashboard."""
    if meeting_type == "internal":
        prompt = f"""Create an executive dashboard for this internal meeting (date: {meeting_date}).

Include:
- Quick stats (meeting type, participant count, date)
- Participants list
- Action items summary (top 5)
- Key decisions summary (top 3)
- Top insights summary (top 5)
- Key debates (if any)
- Next steps

Format as executive-friendly dashboard."""
    else:
        prompt = f"""Create an executive dashboard for this external meeting (date: {meeting_date}).

Include:
- Quick stats (meeting type, stakeholder, company, date)
- Participants list
- Action items summary (top 5)
- Key decisions summary (top 3)
- Top insights summary (top 5)
- Relationship next steps
- Follow-up required

Format as executive-friendly dashboard."""
    
    return extract_with_zo(transcript, prompt)


def generate_metadata(meeting_info: dict) -> dict:
    """Generate _metadata.json content."""
    return {
        "meeting_id": meeting_info.get("meeting_id"),
        "date": meeting_info.get("date"),
        "stakeholder_classification": meeting_info.get("meeting_type"),
        "participants": meeting_info.get("participants", []),
        "processing": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "generator": "meeting_core_generator.py",
            "version": "1.0"
        },
        "blocks_generated": meeting_info.get("blocks_generated", [])
    }


def generate_core_blocks(transcript_path: str, output_dir: str, meeting_info: dict = None):
    """
    Generate all 7 core blocks for a meeting.
    
    Args:
        transcript_path: Path to transcript file
        output_dir: Directory to save blocks
        meeting_info: Optional dict with meeting metadata (date, participants, etc.)
    """
    # Read transcript
    with open(transcript_path, 'r') as f:
        transcript = f.read()
    
    # Classify meeting
    participants = meeting_info.get("participants", "") if meeting_info else ""
    meeting_type = classify_meeting(participants, transcript)
    
    print(f"📊 Meeting classified as: {meeting_type.upper()}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get meeting date
    meeting_date = meeting_info.get("date", datetime.now().strftime("%Y-%m-%d")) if meeting_info else datetime.now().strftime("%Y-%m-%d")
    
    blocks_generated = []
    
    print("\n🔄 Generating core blocks...")
    
    # 1. Action Items (both types)
    print("  ✓ action-items.md")
    action_items = generate_action_items(transcript, meeting_type)
    with open(os.path.join(output_dir, "action-items.md"), 'w') as f:
        f.write(action_items)
    blocks_generated.append("action-items.md")
    
    # 2. Decisions (both types)
    print("  ✓ decisions.md")
    decisions = generate_decisions(transcript, meeting_type)
    with open(os.path.join(output_dir, "decisions.md"), 'w') as f:
        f.write(decisions)
    blocks_generated.append("decisions.md")
    
    # 3. Key Insights (both types)
    print("  ✓ key-insights.md")
    insights = generate_key_insights(transcript, meeting_type)
    with open(os.path.join(output_dir, "key-insights.md"), 'w') as f:
        f.write(insights)
    blocks_generated.append("key-insights.md")
    
    # Type-specific blocks
    if meeting_type == "internal":
        # 4. Debate Points
        print("  ✓ debate-points.md")
        debate = generate_debate_points(transcript)
        with open(os.path.join(output_dir, "debate-points.md"), 'w') as f:
            f.write(debate)
        blocks_generated.append("debate-points.md")
        
        # 5. Memo
        print("  ✓ memo.md")
        meeting_subject = meeting_info.get("subject", "Team Meeting") if meeting_info else "Team Meeting"
        memo = generate_memo(transcript, meeting_subject)
        with open(os.path.join(output_dir, "memo.md"), 'w') as f:
            f.write(memo)
        blocks_generated.append("memo.md")
        
    else:  # external
        # 4. Stakeholder Profile
        print("  ✓ stakeholder-profile.md")
        stakeholder_name = meeting_info.get("stakeholder_name", "External Stakeholder") if meeting_info else "External Stakeholder"
        profile = generate_stakeholder_profile(transcript, stakeholder_name)
        with open(os.path.join(output_dir, "stakeholder-profile.md"), 'w') as f:
            f.write(profile)
        blocks_generated.append("stakeholder-profile.md")
        
        # 5. Follow-up Email
        print("  ✓ follow-up-email.md")
        stakeholder_email = meeting_info.get("stakeholder_email", "email@example.com") if meeting_info else "email@example.com"
        followup = generate_follow_up_email(transcript, stakeholder_name, stakeholder_email)
        with open(os.path.join(output_dir, "follow-up-email.md"), 'w') as f:
            f.write(followup)
        blocks_generated.append("follow-up-email.md")
    
    # 6. REVIEW_FIRST (both types)
    print("  ✓ REVIEW_FIRST.md")
    review = generate_review_first(transcript, meeting_type, meeting_date, 
                                   action_items, decisions, insights)
    with open(os.path.join(output_dir, "REVIEW_FIRST.md"), 'w') as f:
        f.write(review)
    blocks_generated.append("REVIEW_FIRST.md")
    
    # 7. Transcript copy (both types)
    print("  ✓ transcript.txt")
    with open(os.path.join(output_dir, "transcript.txt"), 'w') as f:
        f.write(transcript)
    blocks_generated.append("transcript.txt")
    
    # 8. Metadata
    print("  ✓ _metadata.json")
    if meeting_info:
        meeting_info["meeting_type"] = meeting_type
        meeting_info["blocks_generated"] = blocks_generated
    else:
        meeting_info = {
            "meeting_type": meeting_type,
            "blocks_generated": blocks_generated
        }
    
    metadata = generate_metadata(meeting_info)
    with open(os.path.join(output_dir, "_metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Generated {len(blocks_generated)} core blocks + metadata")
    print(f"📁 Output: {output_dir}")
    
    return {
        "meeting_type": meeting_type,
        "blocks_generated": blocks_generated,
        "output_dir": output_dir
    }


def main():
    parser = argparse.ArgumentParser(description="Generate core meeting intelligence blocks")
    parser.add_argument("--transcript", required=True, help="Path to transcript file")
    parser.add_argument("--output-dir", required=True, help="Output directory for blocks")
    parser.add_argument("--date", help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--participants", help="Participant emails (comma-separated)")
    parser.add_argument("--stakeholder-name", help="Primary stakeholder name (for external meetings)")
    parser.add_argument("--stakeholder-email", help="Primary stakeholder email (for external meetings)")
    parser.add_argument("--meeting-id", help="Unique meeting ID")
    
    args = parser.parse_args()
    
    # Build meeting info
    meeting_info = {}
    if args.date:
        meeting_info["date"] = args.date
    if args.participants:
        meeting_info["participants"] = args.participants
    if args.stakeholder_name:
        meeting_info["stakeholder_name"] = args.stakeholder_name
    if args.stakeholder_email:
        meeting_info["stakeholder_email"] = args.stakeholder_email
    if args.meeting_id:
        meeting_info["meeting_id"] = args.meeting_id
    
    # Generate blocks
    result = generate_core_blocks(args.transcript, args.output_dir, meeting_info)
    
    print(f"\n✨ Meeting type: {result['meeting_type'].upper()}")
    print(f"✨ Blocks generated: {len(result['blocks_generated'])}")


if __name__ == "__main__":
    main()
