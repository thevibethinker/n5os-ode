#!/usr/bin/env python3
"""
Stakeholder Profile Generator
Builds comprehensive stakeholder profiles from meetings.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)


async def generate_stakeholder_profile(
    transcript: str,
    meeting_info: Dict[str, Any],
    meeting_history: List[Dict],
    meeting_types: List[str],
    output_dir: Path
) -> bool:
    """
    Generate stakeholder profile from transcript and history.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        meeting_history: Previous meetings with stakeholder
        meeting_types: Types of meeting
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Generating stakeholder profile")
        
        stakeholder = meeting_info.get('stakeholder_primary', 'Unknown')
        
        # Extract profile elements
        background = _extract_background(transcript)
        interests = _extract_interests(transcript)
        pain_points = _extract_pain_points(transcript)
        opportunities = _extract_opportunities(transcript)
        quotes = _extract_key_quotes(transcript)
        
        # Build relationship context
        relationship = _build_relationship_context(meeting_history, meeting_types)
        
        # Generate markdown
        markdown = _generate_markdown(
            stakeholder, background, interests, pain_points,
            opportunities, quotes, relationship, meeting_info
        )
        
        # Write output
        output_path = output_dir / "stakeholder-profile.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info("Generated stakeholder profile")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate stakeholder profile: {e}", exc_info=True)
        return False


def _extract_background(transcript: str) -> List[str]:
    """Extract background information about stakeholder."""
    background = []
    
    indicators = [
        "i work at", "i'm at", "my role", "i've been",
        "my background", "i used to", "former", "previously"
    ]
    
    lines = transcript.lower().split('\n')
    for line in lines:
        for indicator in indicators:
            if indicator in line and len(line) > 20:
                # Extract the sentence
                background.append(line.strip())
                break
    
    return background[:5]


def _extract_interests(transcript: str) -> List[str]:
    """Extract interests and focus areas."""
    interests = []
    
    indicators = [
        "interested in", "focusing on", "care about", "excited about",
        "passionate about", "working on", "thinking about"
    ]
    
    lines = transcript.lower().split('\n')
    for line in lines:
        for indicator in indicators:
            if indicator in line and len(line) > 20:
                interests.append(line.strip())
                break
    
    return interests[:5]


def _extract_pain_points(transcript: str) -> List[str]:
    """Extract pain points and challenges."""
    pain_points = []
    
    indicators = [
        "challenge", "problem", "difficult", "struggle", "hard to",
        "pain point", "issue", "concern", "worried", "frustrated"
    ]
    
    lines = transcript.lower().split('\n')
    for line in lines:
        for indicator in indicators:
            if indicator in line and len(line) > 20:
                pain_points.append(line.strip())
                break
    
    return pain_points[:5]


def _extract_opportunities(transcript: str) -> List[str]:
    """Extract opportunities mentioned."""
    opportunities = []
    
    indicators = [
        "opportunity", "could help", "looking for", "need", "want to",
        "hoping to", "would be great", "interested in"
    ]
    
    lines = transcript.lower().split('\n')
    for line in lines:
        for indicator in indicators:
            if indicator in line and len(line) > 20:
                opportunities.append(line.strip())
                break
    
    return opportunities[:5]


def _extract_key_quotes(transcript: str) -> List[str]:
    """Extract notable quotes from stakeholder."""
    quotes = []
    
    # Look for substantive statements (longer lines)
    lines = transcript.split('\n')
    for line in lines:
        if len(line) > 100 and len(line) < 300:
            # Skip if it's likely a speaker name
            if not _is_speaker_name(line):
                quotes.append(line.strip())
                if len(quotes) >= 3:
                    break
    
    return quotes


def _is_speaker_name(text: str) -> bool:
    """Check if text is likely a speaker name."""
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', text.strip()):
        return True
    if re.match(r'^[A-Z][a-z]+$', text.strip()) and len(text.strip()) < 20:
        return True
    return False


def _build_relationship_context(meeting_history: List[Dict], meeting_types: List[str]) -> Dict:
    """Build relationship context from history."""
    return {
        "previous_meetings": len(meeting_history),
        "relationship_stage": _determine_relationship_stage(meeting_history),
        "meeting_types": meeting_types
    }


def _determine_relationship_stage(meeting_history: List[Dict]) -> str:
    """Determine relationship stage from meeting count."""
    count = len(meeting_history)
    if count == 0:
        return "New"
    elif count <= 2:
        return "Developing"
    else:
        return "Established"


def _generate_markdown(
    stakeholder: str,
    background: List[str],
    interests: List[str],
    pain_points: List[str],
    opportunities: List[str],
    quotes: List[str],
    relationship: Dict,
    meeting_info: Dict
) -> str:
    """Generate markdown output for profile."""
    md = f"# Stakeholder Profile: {stakeholder}\n\n"
    md += f"**Date Updated**: {meeting_info.get('date', 'Unknown')}\n"
    md += f"**Meeting Type**: {', '.join(relationship.get('meeting_types', []))}\n\n"
    md += "---\n\n"
    
    # Background
    if background:
        md += "## Background\n\n"
        for item in background:
            md += f"- {item}\n"
        md += "\n"
    
    # Interests
    if interests:
        md += "## Interests & Focus Areas\n\n"
        for item in interests:
            md += f"- {item}\n"
        md += "\n"
    
    # Pain Points
    if pain_points:
        md += "## Pain Points & Challenges\n\n"
        for item in pain_points:
            md += f"- {item}\n"
        md += "\n"
    
    # Opportunities
    if opportunities:
        md += "## Opportunities & Needs\n\n"
        for item in opportunities:
            md += f"- {item}\n"
        md += "\n"
    
    # Relationship Context
    md += "## Relationship Context\n\n"
    md += f"- **Previous Meetings**: {relationship.get('previous_meetings', 0)}\n"
    md += f"- **Relationship Stage**: {relationship.get('relationship_stage', 'Unknown')}\n"
    md += f"- **Last Contact**: {meeting_info.get('date', 'Unknown')}\n\n"
    
    # Key Quotes
    if quotes:
        md += "## Key Quotes\n\n"
        for quote in quotes:
            md += f"> \"{quote}\"\n\n"
    
    return md
