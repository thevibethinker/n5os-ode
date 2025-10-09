#!/usr/bin/env python3
"""
Key Insights Extractor
Extracts key insights, learnings, and advice from meetings.
"""
import logging
import re
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def generate_key_insights(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract key insights from transcript and generate detailed-notes.md.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting key insights from transcript")
        
        # Parse transcript
        statements = _parse_transcript(transcript)
        
        # Extract different types of insights
        insights = _extract_insights(statements)
        advice = _extract_advice(statements)
        realizations = _extract_realizations(statements)
        
        # Generate markdown
        markdown = _generate_markdown(insights, advice, realizations, meeting_info)
        
        # Write output
        output_path = output_dir / "detailed-notes.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        total = len(insights) + len(advice) + len(realizations)
        logger.info(f"Generated key insights: {total} total items")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate key insights: {e}", exc_info=True)
        return False


def _parse_transcript(transcript: str) -> List[Dict[str, Any]]:
    """Parse transcript into speaker-attributed statements."""
    statements = []
    lines = transcript.strip().split('\n')
    
    current_speaker = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if _is_likely_speaker(line):
            if current_speaker and current_content:
                statements.append({
                    "speaker": current_speaker,
                    "content": " ".join(current_content)
                })
            current_speaker = line
            current_content = []
        else:
            current_content.append(line)
    
    if current_speaker and current_content:
        statements.append({
            "speaker": current_speaker,
            "content": " ".join(current_content)
        })
    
    return statements


def _is_likely_speaker(text: str) -> bool:
    """Check if text line is likely a speaker name."""
    if len(text) > 50:
        return False
    if any(word in text.lower() for word in ["think", "should", "would", "realized"]):
        return False
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', text):
        return True
    if re.match(r'^[A-Z][a-z]+$', text) and len(text) < 20:
        return True
    return False


def _extract_insights(statements: List[Dict]) -> List[Dict]:
    """Extract key insights from statements."""
    insights = []
    
    insight_indicators = [
        "key insight", "important to note", "realize", "realized",
        "learned", "learning", "discovered", "insight",
        "interesting", "notable", "significant"
    ]
    
    for stmt in statements:
        content = stmt["content"]
        content_lower = content.lower()
        
        # High-value content (longer, substantive statements)
        if len(content) > 100:
            for indicator in insight_indicators:
                if indicator in content_lower:
                    insight = {
                        "content": content,
                        "speaker": stmt["speaker"],
                        "type": "insight",
                        "category": _categorize_insight(content)
                    }
                    insights.append(insight)
                    break
    
    return insights


def _extract_advice(statements: List[Dict]) -> List[Dict]:
    """Extract advice given during meeting."""
    advice_items = []
    
    advice_indicators = [
        "you should", "i'd recommend", "i recommend", "advice",
        "suggest", "my suggestion", "what i'd do", "i think you should",
        "try", "consider", "might want to"
    ]
    
    for stmt in statements:
        content = stmt["content"]
        content_lower = content.lower()
        
        for indicator in advice_indicators:
            if indicator in content_lower:
                advice = {
                    "content": content,
                    "speaker": stmt["speaker"],
                    "type": "advice",
                    "category": _categorize_insight(content)
                }
                advice_items.append(advice)
                break
    
    return advice_items


def _extract_realizations(statements: List[Dict]) -> List[Dict]:
    """Extract realizations and aha moments."""
    realizations = []
    
    realization_indicators = [
        "aha", "oh", "i see", "that makes sense", "good point",
        "you're right", "exactly", "that's it", "now i understand"
    ]
    
    for stmt in statements:
        content = stmt["content"]
        content_lower = content.lower()
        
        for indicator in realization_indicators:
            if indicator in content_lower and len(content) > 50:
                realization = {
                    "content": content,
                    "speaker": stmt["speaker"],
                    "type": "realization"
                }
                realizations.append(realization)
                break
    
    return realizations


def _categorize_insight(content: str) -> str:
    """Categorize insight by topic."""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ["product", "feature", "ui", "ux", "design"]):
        return "Product"
    if any(word in content_lower for word in ["market", "customer", "user", "buyer"]):
        return "Market"
    if any(word in content_lower for word in ["strategy", "approach", "direction", "positioning"]):
        return "Strategy"
    if any(word in content_lower for word in ["process", "workflow", "operation", "execution"]):
        return "Operations"
    if any(word in content_lower for word in ["hire", "team", "people", "culture"]):
        return "People"
    
    return "General"


def _generate_markdown(
    insights: List[Dict],
    advice: List[Dict],
    realizations: List[Dict],
    meeting_info: Dict
) -> str:
    """Generate markdown output for insights."""
    title = f"Key Insights & Detailed Notes: {meeting_info.get('stakeholder_primary', 'Meeting')}"
    date = meeting_info.get('date', 'Unknown Date')
    
    md = f"# {title}\n"
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
        
        for category, items in by_category.items():
            md += f"### {category}\n\n"
            for item in items:
                md += f"**{item['speaker']}**: {item['content']}\n\n"
    
    # Advice Section
    if advice:
        md += "## 🎓 Advice & Recommendations\n\n"
        
        by_category = {}
        for item in advice:
            category = item.get("category", "General")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)
        
        for category, items in by_category.items():
            md += f"### {category}\n\n"
            for item in items:
                md += f"**{item['speaker']}**: {item['content']}\n\n"
    
    # Realizations Section
    if realizations:
        md += "## ✨ Realizations & Aha Moments\n\n"
        for item in realizations:
            md += f"**{item['speaker']}**: {item['content']}\n\n"
    
    if not (insights or advice or realizations):
        md += "_No explicit insights or advice extracted from this meeting._\n"
    
    return md
