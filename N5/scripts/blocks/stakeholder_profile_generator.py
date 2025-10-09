#!/usr/bin/env python3
"""
Stakeholder Profile Generator (LLM-powered)
Builds comprehensive stakeholder profiles using LLM.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
from blocks.llm_client import get_client

logger = logging.getLogger(__name__)


async def generate_stakeholder_profile(
    transcript: str,
    meeting_info: Dict[str, Any],
    meeting_history: List[Dict],
    meeting_types: List[str],
    output_dir: Path
) -> bool:
    """
    Generate stakeholder profile using LLM.
    
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
        logger.info("Generating stakeholder profile using LLM")
        
        llm = get_client()
        
        stakeholder = meeting_info.get('stakeholder_primary', 'Unknown')
        
        system_prompt = """You are an expert at building comprehensive stakeholder profiles from meeting transcripts.

Extract and organize:
1. **Background**: Current role, company, professional background, relevant experience
2. **Interests & Focus Areas**: What they care about, what they're working on
3. **Pain Points & Challenges**: Problems they're facing, obstacles mentioned
4. **Opportunities & Needs**: What they're looking for, gaps they want to fill
5. **Key Quotes**: Notable or revealing statements (select 2-3 most meaningful)
6. **Relationship Notes**: Communication style, preferences, connection points

Be specific and factual. Quote directly when appropriate."""

        date = meeting_info.get('date', 'Unknown')
        relationship_stage = "New" if len(meeting_history) == 0 else \
                           "Developing" if len(meeting_history) <= 2 else "Established"
        
        user_prompt = f"""Build a comprehensive profile for this stakeholder from the meeting transcript.

Stakeholder: {stakeholder}
Meeting Date: {date}
Meeting Type: {', '.join(meeting_types) if meeting_types else 'General'}
Previous Meetings: {len(meeting_history)}
Relationship Stage: {relationship_stage}

Transcript:
{transcript[:15000]}

Create a structured profile with:
- Background & Current Role
- Interests & Focus Areas  
- Pain Points & Challenges
- Opportunities & Needs
- Key Quotes (2-3 most meaningful)
- Relationship Context

Return in markdown format with clear sections and bullet points."""

        response = await llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=3000,
            temperature=0.5
        )
        
        # Format the response
        markdown = _format_profile_markdown(
            response, stakeholder, date, relationship_stage, meeting_history
        )
        
        # Write output
        output_path = output_dir / "stakeholder-profile.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info("Generated stakeholder profile")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate stakeholder profile: {e}", exc_info=True)
        return False


def _format_profile_markdown(
    content: str,
    stakeholder: str,
    date: str,
    relationship_stage: str,
    meeting_history: List[Dict]
) -> str:
    """Format profile content as structured markdown."""
    md = f"# Stakeholder Profile: {stakeholder}\n\n"
    md += f"**Last Updated**: {date}\n"
    md += f"**Relationship Stage**: {relationship_stage}\n"
    md += f"**Total Meetings**: {len(meeting_history) + 1}\n\n"
    md += "---\n\n"
    md += content
    return md
