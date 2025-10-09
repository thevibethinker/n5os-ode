#!/usr/bin/env python3
"""
Follow-Up Email Generator
Generates follow-up email drafts from meeting transcripts.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


async def generate_follow_up_email(
    transcript: str,
    meeting_info: Dict[str, Any],
    email_history: Optional[List[Dict]],
    meeting_history: List[Dict],
    meeting_types: List[str],
    output_dir: Path
) -> bool:
    """
    Generate follow-up email draft from meeting.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        email_history: Previous email exchanges (optional)
        meeting_history: Previous meetings with stakeholder
        meeting_types: Types of meeting
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Generating follow-up email")
        
        # Read action items and decisions
        action_items = _read_file(output_dir / "action-items.md")
        decisions = _read_file(output_dir / "decisions.md")
        
        # Extract key points for email
        key_actions = _extract_actions_for_email(action_items, 3)
        key_decisions = _extract_decisions_for_email(decisions, 2)
        
        # Determine tone based on stakeholder
        tone = _determine_tone(meeting_types, meeting_history)
        
        # Generate email content
        email_content = _generate_email(
            meeting_info, key_actions, key_decisions, tone
        )
        
        # Write output
        output_path = output_dir / "follow-up-email.md"
        output_path.write_text(email_content, encoding='utf-8')
        
        logger.info("Generated follow-up email draft")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate follow-up email: {e}", exc_info=True)
        return False


def _read_file(path: Path) -> str:
    """Read file content, return empty string if not exists."""
    try:
        return path.read_text(encoding='utf-8')
    except:
        return ""


def _extract_actions_for_email(content: str, limit: int) -> List[str]:
    """Extract key actions for email."""
    actions = []
    lines = content.split('\n')
    
    for line in lines:
        if line.strip().startswith('- [ ] **'):
            action = line.strip()[9:]
            if '**' in action:
                action = action[:action.index('**')]
            actions.append(action)
            if len(actions) >= limit:
                break
    
    return actions


def _extract_decisions_for_email(content: str, limit: int) -> List[str]:
    """Extract key decisions for email."""
    decisions = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith('**Decision**:'):
            decision = line[13:].strip()
            decisions.append(decision)
            if len(decisions) >= limit:
                break
    
    return decisions


def _determine_tone(meeting_types: List[str], meeting_history: List[Dict]) -> str:
    """Determine appropriate email tone."""
    if "coaching" in meeting_types or "networking" in meeting_types:
        return "warm"
    elif "sales" in meeting_types or "fundraising" in meeting_types:
        return "professional"
    elif len(meeting_history) > 3:
        return "familiar"
    else:
        return "professional"


def _generate_email(
    meeting_info: Dict,
    key_actions: List[str],
    key_decisions: List[str],
    tone: str
) -> str:
    """Generate email markdown content."""
    stakeholder = meeting_info.get('stakeholder_primary', 'Unknown')
    participants = meeting_info.get('participants', [])
    date = meeting_info.get('date', 'today')
    
    # Extract external participants (not Vrijen)
    external = [p for p in participants if 'vrijen' not in p.lower()]
    
    md = "# Follow-Up Email Draft\n\n"
    md += f"**To**: {', '.join(external) if external else stakeholder}\n"
    md += f"**Subject**: Following up from our meeting on {date}\n\n"
    md += "---\n\n"
    md += "## Email Body\n\n"
    
    # Greeting
    if tone == "warm":
        md += f"Hi {stakeholder.split()[0] if ' ' in stakeholder else stakeholder},\n\n"
    elif tone == "familiar":
        md += f"Hi {stakeholder.split()[0] if ' ' in stakeholder else stakeholder},\n\n"
    else:
        md += f"Dear {stakeholder},\n\n"
    
    # Recap
    md += f"Thanks for taking the time to meet on {date}. "
    md += "I wanted to follow up on our conversation and confirm next steps.\n\n"
    
    # Key Points
    if key_decisions:
        md += "### Key Decisions\n\n"
        for decision in key_decisions:
            md += f"- {decision}\n"
        md += "\n"
    
    # Next Steps
    if key_actions:
        md += "### Next Steps\n\n"
        for action in key_actions:
            md += f"- {action}\n"
        md += "\n"
    
    # Closing
    if tone == "warm":
        md += "Looking forward to staying in touch!\n\n"
        md += "Best,\n"
    elif tone == "familiar":
        md += "Let me know if you have any questions.\n\n"
        md += "Best,\n"
    else:
        md += "Please let me know if you have any questions or need clarification on any of these points.\n\n"
        md += "Best regards,\n"
    
    md += "Vrijen\n\n"
    
    md += "---\n\n"
    md += "_Note: This is a draft. Please review and customize before sending._\n"
    
    return md
