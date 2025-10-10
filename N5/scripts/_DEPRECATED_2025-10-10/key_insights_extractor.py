#!/usr/bin/env python3
"""
Key Insights Extractor (Direct Parsing)
Extracts key insights, learnings, and advice from meetings using direct text analysis.
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
    Extract key insights from transcript using direct parsing.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting key insights from transcript using direct parsing")
        
        # Extract insights, advice, and realizations
        insights, advice, realizations = extract_insights_from_text(transcript, meeting_info)
        
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


def extract_insights_from_text(transcript: str, meeting_info: Dict[str, Any]) -> tuple:
    """
    Extract insights, advice, and realizations from transcript.
    Returns: (insights, advice, realizations)
    """
    insights = []
    advice = []
    realizations = []
    
    lines = transcript.split('\n')
    participants = meeting_info.get('participants', [])
    
    # Insight patterns
    insight_patterns = [
        r"\b(?:key point|important|key|critical|crucial|significant)\s+(?:is|was|thing)?\s*[:–-]?\s*(.+)",
        r"\b(?:realized|realize|discovery|discovered|learned|found out)\s+(?:that)?\s*(.+)",
        r"\b(?:interesting|notable|worth noting|note that)\s+(.+)",
        r"\b(?:the thing is|what's important|what matters)\s+(.+)",
        r"\b(?:insight|observation|takeaway)[:–-]\s*(.+)",
    ]
    
    # Advice patterns
    advice_patterns = [
        r"\b(?:should|would recommend|would suggest|advice|recommend)\s+(.+)",
        r"\b(?:best practice|best way|better to|good idea)\s+(?:is|would be)?\s*(?:to)?\s*(.+)",
        r"\b(?:tip|pro tip|suggestion)[:–-]\s*(.+)",
        r"\b(?:make sure|be sure|don't forget)\s+(?:to)?\s*(.+)",
        r"\b(?:my advice|my recommendation)\s+(?:is|would be)?\s*(?:to)?\s*(.+)",
    ]
    
    # Realization patterns
    realization_patterns = [
        r"\b(?:aha|eureka|got it|I see|oh wow|interesting)\b",
        r"\b(?:makes sense|clicked|connected|understand now)\s+(.+)",
        r"\b(?:breakthrough|revelation|realization)[:–-]\s*(.+)",
    ]
    
    # Quote patterns - look for impactful statements
    quote_patterns = [
        r'"([^"]+)"',  # Quoted text
        r"'([^']+)'",  # Single quoted
    ]
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 20:
            continue
        
        # Extract speaker
        speaker = "Unknown"
        text = line_stripped
        
        speaker_match = re.match(r'^([A-Z][a-zA-Z\s]+?)(?::|$)', line_stripped)
        if speaker_match:
            potential_speaker = speaker_match.group(1).strip()
            if any(potential_speaker in p for p in participants):
                speaker = potential_speaker
                text = line_stripped[len(potential_speaker):].lstrip(':').strip()
        
        # Check for insights
        for pattern in insight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.groups():
                insight_text = match.group(1).strip()
                insight_text = re.sub(r'[.!?]+\s*$', '', insight_text)
                
                if len(insight_text) >= 20:
                    # Truncate at sentence end if too long
                    if len(insight_text) > 200:
                        sentence_end = re.search(r'[.!?]', insight_text[150:])
                        if sentence_end:
                            insight_text = insight_text[:150 + sentence_end.start() + 1]
                    
                    category = _categorize_content(insight_text, meeting_info)
                    implication = _infer_implication(insight_text, text)
                    
                    insights.append({
                        "content": insight_text,
                        "speaker": speaker,
                        "category": category,
                        "implication": implication
                    })
        
        # Check for advice
        for pattern in advice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.groups():
                advice_text = match.group(1).strip()
                advice_text = re.sub(r'[.!?]+\s*$', '', advice_text)
                
                if len(advice_text) >= 15:
                    if len(advice_text) > 200:
                        sentence_end = re.search(r'[.!?]', advice_text[150:])
                        if sentence_end:
                            advice_text = advice_text[:150 + sentence_end.start() + 1]
                    
                    category = _categorize_content(advice_text, meeting_info)
                    
                    advice.append({
                        "content": advice_text,
                        "speaker": speaker,
                        "category": category
                    })
        
        # Check for realizations
        for pattern in realization_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the full context of the realization
                realization_text = text if len(text) > 30 else f"{text} | {lines[i+1] if i+1 < len(lines) else ''}"
                realization_text = re.sub(r'[.!?]+\s*$', '', realization_text.strip())
                
                if len(realization_text) >= 20:
                    realizations.append({
                        "content": realization_text[:200],
                        "speaker": speaker
                    })
        
        # Extract impactful quotes
        for pattern in quote_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                quote_text = match.group(1).strip()
                if len(quote_text) >= 30:  # Substantial quote
                    category = _categorize_content(quote_text, meeting_info)
                    implication = _infer_implication(quote_text, text)
                    
                    insights.append({
                        "content": f'"{quote_text}"',
                        "speaker": speaker,
                        "category": category,
                        "implication": implication
                    })
    
    # Deduplicate
    insights = _deduplicate_items(insights)
    advice = _deduplicate_items(advice)
    realizations = _deduplicate_items(realizations)
    
    return insights, advice, realizations


def _categorize_content(text: str, meeting_info: Dict) -> str:
    """Categorize the insight/advice."""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['product', 'feature', 'build', 'design', 'ux', 'ui']):
        return "Product"
    elif any(word in text_lower for word in ['market', 'customer', 'user', 'demand', 'competition']):
        return "Market"
    elif any(word in text_lower for word in ['strategy', 'approach', 'direction', 'vision', 'goal']):
        return "Strategy"
    elif any(word in text_lower for word in ['process', 'workflow', 'system', 'operation']):
        return "Operations"
    elif any(word in text_lower for word in ['team', 'people', 'hire', 'culture', 'talent']):
        return "People"
    elif any(word in text_lower for word in ['career', 'growth', 'learn', 'skill', 'development']):
        return "Personal"
    else:
        return "General"


def _infer_implication(content: str, full_text: str) -> str:
    """Infer why the insight matters."""
    content_lower = content.lower()
    
    # Look for implication patterns
    implication_patterns = [
        r"(?:means|implies|suggests|indicates)\s+(?:that)?\s*(.+?)(?:[.!?]|$)",
        r"(?:because|since)\s+(.+?)(?:[.!?]|$)",
        r"(?:so|therefore|thus)\s+(.+?)(?:[.!?]|$)",
    ]
    
    for pattern in implication_patterns:
        match = re.search(pattern, content_lower)
        if match:
            return match.group(1).strip()
    
    # Infer based on keywords
    if any(word in content_lower for word in ['opportunity', 'potential', 'could', 'can']):
        return "Presents potential opportunity"
    elif any(word in content_lower for word in ['risk', 'concern', 'problem', 'issue']):
        return "Highlights potential risk or concern"
    elif any(word in content_lower for word in ['validated', 'confirmed', 'proven']):
        return "Validates existing hypothesis or approach"
    
    return "Important context for strategy"


def _deduplicate_items(items: List[Dict]) -> List[Dict]:
    """Remove duplicate items."""
    if not items:
        return []
    
    unique_items = []
    seen_content = set()
    
    for item in items:
        content = item['content'].lower()
        key = re.sub(r'[^\w\s]', '', content[:60])
        
        if key not in seen_content:
            seen_content.add(key)
            unique_items.append(item)
    
    return unique_items


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
