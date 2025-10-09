#!/usr/bin/env python3
"""
Key Insights Extractor (LLM-powered)
Extracts key insights, learnings, and advice from meetings using LLM.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from blocks.llm_client import get_client

logger = logging.getLogger(__name__)


async def generate_key_insights(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract key insights from transcript using LLM and generate detailed-notes.md.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting key insights from transcript using LLM")
        
        llm = get_client()
        
        system_prompt = """You are an expert meeting analyst specializing in insight extraction.

Extract three types of valuable content:
1. **Key Insights**: Important realizations, validations, new perspectives, strategic observations
2. **Advice & Recommendations**: Guidance, suggestions, best practices shared
3. **Realizations & Aha Moments**: Breakthroughs, connections made, problem clarifications

For each item, identify:
- The content/statement
- Who said it
- Category: Product, Market, Strategy, Operations, People, Personal, or General
- Why it matters (implication)

Prioritize high-value, actionable, or transformative content.

Return valid JSON only."""

        date = meeting_info.get('date', 'Unknown')
        participants = meeting_info.get('participants', [])
        
        user_prompt = f"""Analyze this meeting transcript and extract key insights, advice, and realizations.

Meeting Date: {date}
Participants: {', '.join(participants) if participants else 'Unknown'}

Transcript:
{transcript[:15000]}

Return a JSON object:
{{
  "insights": [
    {{
      "content": "The insight statement",
      "speaker": "Who said it",
      "category": "Product|Market|Strategy|Operations|People|Personal|General",
      "implication": "Why this matters or what it means"
    }}
  ],
  "advice": [
    {{
      "content": "The advice or recommendation",
      "speaker": "Who gave it",
      "category": "Product|Market|Strategy|Operations|People|Personal|General"
    }}
  ],
  "realizations": [
    {{
      "content": "The realization or aha moment",
      "speaker": "Who had it"
    }}
  ]
}}

Focus on substantive, meaningful content that provides value."""

        response = await llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=4000,
            temperature=0.4,
            response_format="json"
        )
        
        try:
            data = json.loads(response)
            insights = data.get("insights", [])
            advice = data.get("advice", [])
            realizations = data.get("realizations", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, attempting fallback")
            data = _fallback_parse(response)
            insights = data.get("insights", [])
            advice = data.get("advice", [])
            realizations = data.get("realizations", [])
        
        markdown = _generate_markdown(insights, advice, realizations, meeting_info)
        
        output_path = output_dir / "detailed-notes.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        total = len(insights) + len(advice) + len(realizations)
        logger.info(f"Generated key insights: {total} total items")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate key insights: {e}", exc_info=True)
        return False


def _fallback_parse(text: str) -> Dict:
    """Fallback parser if JSON fails."""
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            try:
                return json.loads(text[start:end].strip())
            except:
                pass
    return {"insights": [], "advice": [], "realizations": []}


def _generate_markdown(
    insights: List[Dict],
    advice: List[Dict],
    realizations: List[Dict],
    meeting_info: Dict
) -> str:
    """Generate markdown output for insights."""
    stakeholder = meeting_info.get('stakeholder_primary', 'Meeting')
    date = meeting_info.get('date', 'Unknown Date')
    
    md = f"# Key Insights & Detailed Notes: {stakeholder}\n"
    md += f"**Date**: {date}\n\n"
    md += "---\n\n"
    
    # Key Insights Section
    if insights:
        md += "## 💡 Key Insights\n\n"
        
        # Group by category
        by_category = {}
        for insight in insights:
            category = insight.get("category", "General")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(insight)
        
        for category, items in sorted(by_category.items()):
            md += f"### {category}\n\n"
            for item in items:
                md += f"**{item.get('speaker', 'Unknown')}**: {item['content']}\n\n"
                if item.get('implication'):
                    md += f"_Implication: {item['implication']}_\n\n"
    
    # Advice Section
    if advice:
        md += "## 🎓 Advice & Recommendations\n\n"
        
        by_category = {}
        for item in advice:
            category = item.get("category", "General")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)
        
        for category, items in sorted(by_category.items()):
            md += f"### {category}\n\n"
            for item in items:
                md += f"**{item.get('speaker', 'Unknown')}**: {item['content']}\n\n"
    
    # Realizations Section
    if realizations:
        md += "## ✨ Realizations & Aha Moments\n\n"
        for item in realizations:
            md += f"**{item.get('speaker', 'Unknown')}**: {item['content']}\n\n"
    
    if not (insights or advice or realizations):
        md += "_No explicit insights or advice extracted from this meeting._\n"
    
    return md
