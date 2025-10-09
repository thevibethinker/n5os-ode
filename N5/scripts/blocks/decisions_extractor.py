#!/usr/bin/env python3
"""
Decisions Extractor (LLM-powered)
Extracts decisions made during meetings using LLM.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from blocks.llm_client import get_client

logger = logging.getLogger(__name__)


async def generate_decisions(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract decisions from transcript using LLM and generate decisions.md.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting decisions from transcript using LLM")
        
        llm = get_client()
        
        system_prompt = """You are an expert meeting analyst specializing in decision extraction.

Identify concrete decisions made during meetings. A decision is:
- A clear choice or determination made
- Agreement on a specific course of action
- Explicit rejection of an option
- Resource allocation or commitment

For each decision, extract:
1. The decision statement (what was decided)
2. Rationale (why this was decided)
3. Who made or agreed to the decision
4. Category: Strategic, Product, Resource Allocation, Process, or Tactical
5. Impact (what this affects)

Return valid JSON only."""

        date = meeting_info.get('date', 'Unknown')
        participants = meeting_info.get('participants', [])
        
        user_prompt = f"""Analyze this meeting transcript and extract ALL decisions made.

Meeting Date: {date}
Participants: {', '.join(participants) if participants else 'Unknown'}

Transcript:
{transcript[:15000]}

Return a JSON object:
{{
  "decisions": [
    {{
      "decision": "Clear statement of what was decided",
      "rationale": "Why this decision was made",
      "decided_by": "Name(s) of decision maker(s)",
      "category": "Strategic|Product|Resource Allocation|Process|Tactical",
      "impact": "What areas or activities this affects"
    }}
  ]
}}

Look for decision indicators: "decided", "going with", "chose", "agreed", "will not", "won't do", "concluded", "determined"."""

        response = await llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=3000,
            temperature=0.3,
            response_format="json"
        )
        
        try:
            data = json.loads(response)
            decisions = data.get("decisions", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, attempting fallback")
            decisions = _fallback_parse(response)
        
        markdown = _generate_markdown(decisions, meeting_info)
        
        output_path = output_dir / "decisions.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info(f"Generated decisions: {len(decisions)} total decisions")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate decisions: {e}", exc_info=True)
        return False


def _fallback_parse(text: str) -> List[Dict]:
    """Fallback parser if JSON fails."""
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            try:
                data = json.loads(text[start:end].strip())
                return data.get("decisions", [])
            except:
                pass
    return []


def _generate_markdown(decisions: List[Dict], meeting_info: Dict) -> str:
    """Generate markdown output for decisions."""
    stakeholder = meeting_info.get('stakeholder_primary', 'Meeting')
    date = meeting_info.get('date', 'Unknown Date')
    
    md = f"# Decisions Made: {stakeholder}\n"
    md += f"**Date**: {date}\n\n"
    md += "---\n\n"
    
    if not decisions:
        md += "_No explicit decisions identified in this meeting._\n"
        return md
    
    # Categorize by type
    categorized = {}
    for decision in decisions:
        category = decision.get("category", "Tactical")
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(decision)
    
    # Generate sections
    for category in ["Strategic", "Product", "Resource Allocation", "Process", "Tactical"]:
        if category not in categorized:
            continue
            
        md += f"## {category} Decisions\n\n"
        
        for i, decision in enumerate(categorized[category], 1):
            md += f"### {i}. {decision['decision'][:80]}...\n\n"
            md += f"**Decision**: {decision['decision']}\n\n"
            
            if decision.get('rationale'):
                md += f"**Rationale**: {decision['rationale']}\n\n"
            
            md += f"**Decided By**: {decision.get('decided_by', 'Unknown')}\n\n"
            
            if decision.get('impact'):
                md += f"**Impact**: {decision['impact']}\n\n"
            
            md += "---\n\n"
    
    return md
