#!/usr/bin/env python3
"""
Decisions Extractor (Direct Parsing)
Extracts decisions made during meetings using direct text analysis.
"""
import logging
import re
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def generate_decisions(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract decisions from transcript using direct parsing.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting decisions from transcript using direct parsing")
        
        # Extract decisions
        decisions = extract_decisions_from_text(transcript, meeting_info)
        
        # Generate markdown
        markdown = _generate_markdown(decisions, meeting_info)
        
        # Write output
        output_path = output_dir / "decisions.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info(f"Generated decisions: {len(decisions)} total decisions")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate decisions: {e}", exc_info=True)
        return False


def extract_decisions_from_text(transcript: str, meeting_info: Dict[str, Any]) -> List[Dict]:
    """
    Extract decisions by parsing transcript for decision-oriented language.
    """
    decisions = []
    lines = transcript.split('\n')
    
    # Decision patterns
    decision_patterns = [
        r"\b(?:decided|decision|decide)\s+(?:to|that|on)\s+(.+)",
        r"\b(?:agreed|agreement|agree)\s+(?:to|that|on)?\s*(.+)",
        r"\b(?:going with|went with|go with)\s+(.+)",
        r"\b(?:chose|chosen|choose)\s+(.+)",
        r"\b(?:will not|won't|not going to|aren't going to)\s+(.+)",
        r"\b(?:confirmed|confirm)\s+(?:that)?\s*(.+)",
        r"\b(?:approved|approve)\s+(.+)",
        r"(?:that works|sounds good|let's do it|let's do that|let's go with)",
        r"\b(?:final decision|consensus|concluded that)\s+(.+)",
        r"\b(?:move forward with|moving forward with|proceed with)\s+(.+)",
    ]
    
    # Rejection/negative decision patterns
    rejection_patterns = [
        r"\b(?:decided not to|won't|will not|not going to)\s+(.+)",
        r"\b(?:rejected|reject|ruled out)\s+(.+)",
        r"\b(?:no longer|not anymore)\s+(.+)",
    ]
    
    participants = meeting_info.get('participants', [])
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 15:
            continue
        
        # Try to extract speaker
        speaker = "Unknown"
        text = line_stripped
        
        speaker_match = re.match(r'^([A-Z][a-zA-Z\s]+?)(?::|$)', line_stripped)
        if speaker_match:
            potential_speaker = speaker_match.group(1).strip()
            if any(potential_speaker in p for p in participants):
                speaker = potential_speaker
                text = line_stripped[len(potential_speaker):].lstrip(':').strip()
        
        # Check for decision patterns
        decision_found = False
        is_rejection = False
        decision_text = None
        
        for pattern in decision_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if match.groups():
                    decision_text = match.group(1).strip()
                else:
                    # Pattern matched but no capture group (e.g., "that works")
                    # Use surrounding context
                    context_start = max(0, i-2)
                    decision_text = " ".join(lines[context_start:i+1])
                decision_found = True
                break
        
        # Check for rejection patterns
        if not decision_found:
            for pattern in rejection_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    decision_text = match.group(1).strip() if match.groups() else text
                    decision_found = True
                    is_rejection = True
                    break
        
        if decision_found and decision_text:
            # Clean up decision text
            decision_text = re.sub(r'[.!?]+\s*$', '', decision_text)
            
            # Skip if too short
            if len(decision_text) < 10:
                continue
            
            # Truncate long decisions at sentence boundary
            if len(decision_text) > 250:
                sentence_end = re.search(r'[.!?]', decision_text[150:])
                if sentence_end:
                    decision_text = decision_text[:150 + sentence_end.start() + 1]
                else:
                    decision_text = decision_text[:250] + "..."
            
            # Build context from surrounding lines
            context_lines = []
            for j in range(max(0, i-2), min(len(lines), i+3)):
                if j != i and lines[j].strip():
                    context_lines.append(lines[j].strip()[:100])
            context = " | ".join(context_lines[:3]) if context_lines else ""
            
            # Infer rationale from context
            rationale = _infer_rationale(decision_text, context, text)
            
            # Categorize decision
            category = _categorize_decision(decision_text, meeting_info)
            
            # Assess impact
            impact = _assess_impact(decision_text, category)
            
            decisions.append({
                "decision": decision_text,
                "rationale": rationale,
                "decided_by": speaker,
                "category": category,
                "impact": impact,
                "is_rejection": is_rejection
            })
    
    # Deduplicate
    decisions = _deduplicate_decisions(decisions)
    
    return decisions


def _infer_rationale(decision_text: str, context: str, line_text: str) -> str:
    """Infer why a decision was made from context."""
    # Look for "because", "since", "to", "for" clauses
    rationale_patterns = [
        r"(?:because|since|as)\s+(.+?)(?:[.!?]|$)",
        r"(?:to|in order to)\s+(.+?)(?:[.!?]|$)",
        r"(?:for|given)\s+(.+?)(?:[.!?]|$)",
    ]
    
    # Check decision text first
    for pattern in rationale_patterns:
        match = re.search(pattern, decision_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Check context
    for pattern in rationale_patterns:
        match = re.search(pattern, context, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Based on meeting discussion"


def _categorize_decision(decision_text: str, meeting_info: Dict) -> str:
    """Categorize the decision type."""
    text_lower = decision_text.lower()
    
    meeting_types = meeting_info.get('meeting_types', [])
    
    # Strategic indicators
    if any(word in text_lower for word in ['partner', 'strategy', 'approach', 'direction', 'vision', 'goal']):
        return "Strategic"
    
    # Product indicators
    if any(word in text_lower for word in ['feature', 'product', 'build', 'develop', 'design', 'functionality']):
        return "Product"
    
    # Resource allocation indicators
    if any(word in text_lower for word in ['hire', 'budget', 'spend', 'invest', 'resource', 'allocate', 'cost']):
        return "Resource Allocation"
    
    # Process indicators
    if any(word in text_lower for word in ['process', 'workflow', 'procedure', 'system', 'how we']):
        return "Process"
    
    # Default based on meeting type
    if 'sales' in meeting_types:
        return "Tactical"
    
    return "Tactical"


def _assess_impact(decision_text: str, category: str) -> str:
    """Assess the impact of the decision."""
    text_lower = decision_text.lower()
    
    # High impact indicators
    if category in ["Strategic", "Resource Allocation"]:
        return "High - affects overall direction and resources"
    
    # Check for scope indicators
    if any(word in text_lower for word in ['all', 'every', 'entire', 'company', 'organization']):
        return "High - affects multiple areas"
    
    if any(word in text_lower for word in ['team', 'group', 'department']):
        return "Medium - affects specific team/area"
    
    if any(word in text_lower for word in ['pilot', 'test', 'trial', 'experiment']):
        return "Low - limited scope, experimental"
    
    return "Medium - affects ongoing work"


def _deduplicate_decisions(decisions: List[Dict]) -> List[Dict]:
    """Remove duplicate or very similar decisions."""
    if not decisions:
        return []
    
    unique_decisions = []
    seen_texts = set()
    
    for item in decisions:
        decision_text = item['decision'].lower()
        
        # Create normalized key
        key = re.sub(r'[^\w\s]', '', decision_text[:60])
        
        if key not in seen_texts:
            seen_texts.add(key)
            unique_decisions.append(item)
    
    return unique_decisions


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
            # Show first 80 chars as title
            title = decision['decision'][:80]
            if len(decision['decision']) > 80:
                title += "..."
            
            md += f"### {i}. {title}\n\n"
            md += f"**Decision**: {decision['decision']}\n\n"
            
            if decision.get('rationale'):
                md += f"**Rationale**: {decision['rationale']}\n\n"
            
            md += f"**Decided By**: {decision.get('decided_by', 'Unknown')}\n\n"
            
            if decision.get('impact'):
                md += f"**Impact**: {decision['impact']}\n\n"
            
            if decision.get('is_rejection'):
                md += "_Note: This is a decision NOT to do something_\n\n"
            
            md += "---\n\n"
    
    return md
