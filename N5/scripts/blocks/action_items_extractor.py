#!/usr/bin/env python3
"""
Action Items Extractor (LLM-powered)
Extracts action items from meeting transcripts using LLM.
"""
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from blocks.llm_client import get_client

logger = logging.getLogger(__name__)


async def generate_action_items(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract action items from transcript using LLM and generate action-items.md.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting action items from transcript using LLM")
        
        # Get LLM client
        llm = get_client()
        
        # Prepare prompt
        system_prompt = """You are an expert meeting analyst. Extract action items from transcripts with precision.

For each action item, identify:
1. Clear, concise action description
2. Owner (who will do it)
3. Deadline or timeframe
4. Context (why it matters)
5. Priority level

Categorize actions by timeframe:
- Immediate: 0-2 days
- Short-term: 3-14 days  
- Medium-term: 15-30 days
- Long-term: 30+ days

Return valid JSON only."""

        meeting_date = meeting_info.get('date', datetime.now().strftime('%Y-%m-%d'))
        participants = meeting_info.get('participants', [])
        
        user_prompt = f"""Analyze this meeting transcript and extract ALL action items, commitments, and tasks mentioned.

Meeting Date: {meeting_date}
Participants: {', '.join(participants) if participants else 'Unknown'}

Transcript:
{transcript[:15000]}  # Limit for token constraints

Return a JSON object with this structure:
{{
  "action_items": [
    {{
      "action": "Clear description of the action",
      "owner": "Person's name",
      "deadline": "YYYY-MM-DD",
      "timeframe": "immediate|short_term|medium_term|long_term",
      "priority": "high|medium|normal",
      "context": "Why this matters or additional context"
    }}
  ]
}}

Extract concrete commitments, stated intentions ("I'll...", "I will...", "going to...", "need to..."), and agreed next steps."""

        # Call LLM
        response = await llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=4000,
            temperature=0.3,  # Lower for structured extraction
            response_format="json"
        )
        
        # Parse response
        try:
            data = json.loads(response)
            action_items = data.get("action_items", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, attempting extraction from text")
            action_items = _fallback_parse(response)
        
        # Generate markdown
        markdown = _generate_markdown(action_items, meeting_info)
        
        # Write output
        output_path = output_dir / "action-items.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info(f"Generated action items: {len(action_items)} total items")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate action items: {e}", exc_info=True)
        return False


def _fallback_parse(text: str) -> List[Dict]:
    """Fallback parser if JSON fails."""
    # Try to extract JSON from markdown code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            try:
                data = json.loads(text[start:end].strip())
                return data.get("action_items", [])
            except:
                pass
    return []


def _generate_markdown(action_items: List[Dict], meeting_info: Dict) -> str:
    """Generate markdown output for action items."""
    stakeholder = meeting_info.get('stakeholder_primary', 'Meeting')
    date = meeting_info.get('date', 'Unknown Date')
    
    md = f"# Action Items: {stakeholder}\n"
    md += f"**Date**: {date}\n\n"
    md += "---\n\n"
    
    # Categorize by timeframe
    categorized = {
        "immediate": [],
        "short_term": [],
        "medium_term": [],
        "long_term": []
    }
    
    for item in action_items:
        timeframe = item.get("timeframe", "short_term")
        if timeframe in categorized:
            categorized[timeframe].append(item)
    
    # Immediate actions
    if categorized["immediate"]:
        md += "## ⚡ Immediate (Next 24-48 Hours)\n\n"
        for item in categorized["immediate"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            if item.get('priority') == 'high':
                md += f"  - **Priority**: 🔴 HIGH\n"
            md += f"  - **Context**: {item.get('context', 'N/A')}\n\n"
    
    # Short-term actions
    if categorized["short_term"]:
        md += "## 📅 Short-Term (1-2 Weeks)\n\n"
        for item in categorized["short_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            md += f"  - **Context**: {item.get('context', 'N/A')}\n\n"
    
    # Medium-term actions
    if categorized["medium_term"]:
        md += "## 📆 Medium-Term (2-4 Weeks)\n\n"
        for item in categorized["medium_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            md += f"  - **Context**: {item.get('context', 'N/A')}\n\n"
    
    # Long-term actions
    if categorized["long_term"]:
        md += "## 🗓️ Long-Term (1+ Months)\n\n"
        for item in categorized["long_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            md += f"  - **Context**: {item.get('context', 'N/A')}\n\n"
    
    if not any(categorized.values()):
        md += "_No explicit action items identified in this meeting._\n"
    
    return md
