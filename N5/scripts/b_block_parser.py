#!/usr/bin/env python3
"""
B-Block Parser — Extract structured blocks from meeting transcripts
Implements Phase 2 of Content Library integration

Extracts:
1. Resources explicitly/implicitly referenced in conversation
2. Eloquent lines/monologues with audience reaction signals
3. Key decisions, action items, questions
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

sys.path.insert(0, str(Path(__file__).parent))
from content_library import ContentLibrary

logger = logging.getLogger(__name__)


@dataclass
class ResourceReference:
    """A resource mentioned in the conversation"""
    content: str  # URL or description
    title: Optional[str] = None
    url: Optional[str] = None  # Explicit URL field
    mentioned_by: Optional[str] = None
    context: Optional[str] = None  # Surrounding text
    confidence: str = "explicit"  # explicit | implicit | suggested
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EloquentLine:
    """A particularly eloquent line/monologue"""
    speaker: str
    text: str
    cleaned_text: str
    context: Optional[str] = None
    audience_reaction: Optional[str] = None  # positive | neutral | none
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class BBlockParser:
    """Parse meeting transcripts into structured blocks"""
    
    def __init__(self, meeting_folder: Path):
        self.meeting_folder = Path(meeting_folder)
        self.content_library = ContentLibrary()
        self.blocks = {}  # Store loaded B-blocks
        self.confidence_order = {"explicit": 2, "implicit": 1, "suggested": 0}
        
    def _add_unique_resource(self, resources: List[ResourceReference], res: ResourceReference):
        """Add resource only if not duplicate (shared across all extraction methods)"""
        if res.content:
            content_normalized = res.content.rstrip('/').lower()
            for existing in resources:
                if existing.content and existing.content.rstrip('/').lower() == content_normalized:
                    # Upgrade confidence if this mention is more explicit
                    if self.confidence_order[res.confidence] > self.confidence_order[existing.confidence]:
                        existing.confidence = res.confidence
                    return
        resources.append(res)
    
    def parse_transcript(self, transcript_path: Path) -> Dict:
        """
        Parse transcript and extract all blocks
        Returns: {
            "resources_explicit": [ResourceReference],
            "resources_suggested": [ResourceReference],
            "eloquent_lines": [EloquentLine],
            "key_decisions": [str],
            "action_items": [str],
            "questions": [str]
        }
        """
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        return {
            "resources_explicit": self.extract_explicit_resources(transcript_text),
            "resources_suggested": self.suggest_relevant_resources(transcript_text),
            "eloquent_lines": self.extract_eloquent_lines(transcript_text),
            "key_decisions": self.extract_key_decisions(transcript_text),
            "action_items": self.extract_action_items(transcript_text),
            "questions": self.extract_questions(transcript_text)
        }
    
    def extract_explicit_resources(self, text: str) -> List[ResourceReference]:
        """
        Extract resources explicitly or implicitly mentioned in conversation
        
        Explicit: URLs, specific tool names, documents mentioned
        Implicit: References like "that article I sent", "the guide", "our demo"
        """
        resources = []
        
        # 1. Extract URLs
        url_pattern = r'https?://[^\s<>"\'\\)]+|www\.[^\s<>"\'\\)]+'
        for match in re.finditer(url_pattern, text, re.IGNORECASE):
            url = match.group(0)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            
            self._add_unique_resource(resources, ResourceReference(
                content=url,
                context=context,
                confidence="explicit"
            ))
        
        # 2. Extract specific tool/product mentions
        tool_patterns = [
            (r'\b(YC|Y\s*Combinator)\s+(founder\s+)?match(ing)?\b', "YC Founder Match"),
            (r'\bCoffee\s*Space\b', "Coffee Space"),
            (r'\bCalendly\b', "Calendly"),
            (r'\bZo\s+(Computer|referral|promo)\b', "Zo Computer"),
            (r'\bCareerspan(\+|\s+Plus)?\b', "Careerspan"),
        ]
        
        for pattern, title in tool_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                # Try to find matching resource in Content Library
                lib_items = self.content_library.search(query=title, tags={})
                if lib_items:
                    item = lib_items[0]
                    self._add_unique_resource(resources, ResourceReference(
                        content=item.content or item.url or title,
                        title=item.title,
                        context=context,
                        confidence="explicit"
                    ))
                else:
                    self._add_unique_resource(resources, ResourceReference(
                        content=title,
                        title=title,
                        context=context,
                        confidence="explicit"
                    ))
        
        # 3. Extract implicit references
        implicit_patterns = [
            r'\b(the|that|this)\s+(article|guide|doc|document|resource|link|page|site)\b',
            r'\b(our|my)\s+(demo|guide|resource|tool)\b',
            r'\bI\'ll\s+send\s+(you|over)\s+\w+\b'
        ]
        
        for pattern in implicit_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                self._add_unique_resource(resources, ResourceReference(
                    content=match.group(0),
                    context=context,
                    confidence="implicit"
                ))
        
        return resources
    
    def suggest_relevant_resources(self, text: str) -> List[ResourceReference]:
        """
        Suggest resources that would be helpful based on conversation topics
        These are NOT mentioned in conversation, but would add value
        """
        suggestions = []
        
        # Detect conversation topics
        topics = self._detect_topics(text)
        
        # Search Content Library for relevant items by topic
        for topic in topics:
            items = self.content_library.search(
                query=topic,
                tags={"purpose": ["education", "resource", "guide"]}
            )
            
            for item in items[:2]:  # Max 2 suggestions per topic
                suggestions.append(ResourceReference(
                    content=item.content or item.url or "",
                    title=item.title,
                    confidence="suggested",
                    context=f"Relevant to: {topic}"
                ))
        
        return suggestions
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect key topics in conversation for suggesting resources"""
        topics = []
        
        topic_keywords = {
            "job_search": ["job search", "career", "resume", "interview", "job hunt"],
            "co_founder": ["co-founder", "cofounder", "technical founder", "partner"],
            "fundraising": ["fundraising", "investor", "pitch", "raise"],
            "product": ["product", "build", "feature", "launch"],
            "consulting": ["consulting", "mckinsey", "consulting interview"],
            "zo_computer": ["zo", "ai system", "automation", "productivity"],
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def extract_eloquent_lines(self, text: str) -> List[EloquentLine]:
        """
        Extract particularly eloquent lines/monologues
        Focus on V or Careerspan team, especially those with positive audience reaction
        """
        eloquent_lines = []
        
        # Split into speaker turns (rough heuristic)
        # Format: "Speaker: text" or "Speaker\ntext"
        speaker_pattern = r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[:\n]\s*(.+?)(?=\n[A-Z][a-z]+\s*[:\n]|\Z)'
        
        for match in re.finditer(speaker_pattern, text, re.MULTILINE | re.DOTALL):
            speaker = match.group(1).strip()
            utterance = match.group(2).strip()
            
            # Only process V or Careerspan team (heuristic: Vrijen, V, etc.)
            if not self._is_v_or_team(speaker):
                continue
            
            # Check for eloquence signals
            eloquence_score = self._score_eloquence(utterance)
            if eloquence_score < 0.5:
                continue
            
            # Check for audience reaction signals
            reaction = self._detect_audience_reaction(text, match.end())
            
            # Clean up the line
            cleaned = self._cleanup_utterance(utterance)
            
            eloquent_lines.append(EloquentLine(
                speaker=speaker,
                text=utterance,
                cleaned_text=cleaned,
                audience_reaction=reaction,
                context=utterance[:100] + "..." if len(utterance) > 100 else utterance
            ))
        
        return eloquent_lines
    
    def _is_v_or_team(self, speaker: str) -> bool:
        """Check if speaker is V or Careerspan team"""
        team_names = ["vrijen", "v", "attawar", "careerspan"]
        return any(name in speaker.lower() for name in team_names)
    
    def _score_eloquence(self, text: str) -> float:
        """
        Score eloquence based on:
        - Length (substantial, not too short or long)
        - Metaphors/analogies
        - Clear phrasing
        - Memorable hooks
        """
        score = 0.0
        
        # Length: 20-300 words is good range
        word_count = len(text.split())
        if 20 <= word_count <= 300:
            score += 0.3
        
        # Metaphors/analogies
        metaphor_signals = ["like", "it's like", "think of it as", "imagine", "as if"]
        if any(sig in text.lower() for sig in metaphor_signals):
            score += 0.2
        
        # Clear phrasing
        clarity_signals = ["in other words", "essentially", "basically", "the key is"]
        if any(sig in text.lower() for sig in clarity_signals):
            score += 0.2
        
        # Memorable hooks
        hook_signals = ["the problem is", "here's the thing", "what's interesting", "what matters"]
        if any(sig in text.lower() for sig in hook_signals):
            score += 0.3
        
        return min(1.0, score)
    
    def _detect_audience_reaction(self, full_text: str, position: int) -> Optional[str]:
        """
        Detect audience reaction after a statement
        Look for: "that's great", "exactly", "yes", "oh wow", laughter, etc.
        """
        # Look ahead 200 chars for reaction
        snippet = full_text[position:position+200].lower()
        
        positive_signals = [
            "that's great", "that's perfect", "exactly", "yes", "yeah",
            "oh wow", "interesting", "love that", "makes sense", "totally"
        ]
        
        if any(sig in snippet for sig in positive_signals):
            return "positive"
        
        return None
    
    def _cleanup_utterance(self, text: str) -> str:
        """Clean up transcript artifacts: filler words, stutters, etc."""
        # Remove filler words
        fillers = [r'\buh\b', r'\bum\b', r'\blike\b(?! \w+ like)', r'\byou know\b', r'\bI mean\b']
        cleaned = text
        for filler in fillers:
            cleaned = re.sub(filler, '', cleaned, flags=re.IGNORECASE)
        
        # Remove stutters (e.g., "I I think" -> "I think")
        cleaned = re.sub(r'\b(\w+)\s+\1\b', r'\1', cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def extract_key_decisions(self, text: str) -> List[str]:
        """Extract key decisions made in the conversation"""
        decisions = []
        
        decision_signals = [
            r'\b(let\'s|we\'ll|we should|I\'ll|I think we should)\b.{0,200}',
            r'\b(decided to|going to|plan to)\b.{0,200}',
        ]
        
        for pattern in decision_signals:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                decisions.append(match.group(0).strip())
        
        return decisions[:5]  # Top 5
    
    def extract_action_items(self, text: str) -> List[str]:
        """Extract action items from conversation"""
        actions = []
        
        action_signals = [
            r'\b(I\'ll|I will|will)\s+(send|share|follow up|reach out|intro|connect)\b.{0,200}',
            r'\b(next step|action item|to-do|todo)\b.{0,200}',
        ]
        
        for pattern in action_signals:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                actions.append(match.group(0).strip())
        
        return actions[:5]  # Top 5
    
    def extract_questions(self, text: str) -> List[str]:
        """Extract key questions asked in conversation"""
        questions = []
        
        # Simple question extraction
        for line in text.split('\n'):
            if '?' in line:
                questions.append(line.strip())
        
        return questions[:5]  # Top 5

    def load_all_blocks(self) -> None:
        """Load all existing B-block markdown files from meeting folder"""
        logger.info(f"Loading B-blocks from {self.meeting_folder}")
        
        b_block_patterns = {
            "B01": "detailed_recap",
            "B02": "commitments",
            "B05": "questions",
            "B07": "warm_intros",
            "B13": "action_plan",
            "B21": "key_moments",
            "B26": "metadata"
        }
        
        for code, key in b_block_patterns.items():
            pattern = f"{code}_*.md"
            matching_files = list(self.meeting_folder.glob(pattern))
            if matching_files:
                file_path = matching_files[0]
                try:
                    with open(file_path, 'r') as f:
                        self.blocks[key] = f.read()
                    logger.info(f"  ✓ Loaded {code} -> {key}")
                except Exception as e:
                    logger.warning(f"  ⚠ Failed to load {code}: {e}")
                    self.blocks[key] = None
            else:
                logger.debug(f"  - No {code} block found")
                self.blocks[key] = None
    
    def extract_email_context(self) -> Dict:
        """Extract email context from loaded B-blocks"""
        logger.info("Extracting email context from B-blocks")
        
        context = {
            "resources_explicit": [],
            "resources_suggested": [],
            "eloquent_lines": [],
            "key_decisions": [],
            "action_items": [],
            "questions": []
        }
        
        # Extract resources from detailed recap and action plan
        if self.blocks.get("detailed_recap"):
            context["resources_explicit"].extend(
                self._extract_resources_from_text(self.blocks["detailed_recap"], confidence="explicit")
            )
        
        if self.blocks.get("action_plan"):
            context["resources_explicit"].extend(
                self._extract_resources_from_text(self.blocks["action_plan"], confidence="implicit")
            )
        
        # Extract eloquent lines from key moments
        if self.blocks.get("key_moments"):
            context["eloquent_lines"] = self._extract_eloquent_from_key_moments(
                self.blocks["key_moments"]
            )
        
        # Extract questions
        if self.blocks.get("questions"):
            context["questions"] = self._extract_questions_from_block(
                self.blocks["questions"]
            )
        
        # Extract action items from commitments and action plan
        if self.blocks.get("commitments"):
            context["action_items"].extend(
                self._extract_actions_from_text(self.blocks["commitments"])
            )
        
        if self.blocks.get("action_plan"):
            context["action_items"].extend(
                self._extract_actions_from_text(self.blocks["action_plan"])
            )
        
        # Suggest additional resources based on topics
        if self.blocks.get("detailed_recap"):
            topics = self._detect_topics(self.blocks["detailed_recap"])
            context["resources_suggested"] = self._suggest_resources(topics)
        
        # Deduplicate
        context["resources_explicit"] = self._deduplicate_resources(context["resources_explicit"])
        context["resources_suggested"] = self._deduplicate_resources(context["resources_suggested"])
        context["action_items"] = list(set(context["action_items"]))
        context["questions"] = list(set(context["questions"]))
        
        logger.info(f"  ✓ Extracted: {len(context['resources_explicit'])} explicit resources, "
                   f"{len(context['eloquent_lines'])} eloquent lines, "
                   f"{len(context['action_items'])} actions")
        
        return context
    
    def _extract_resources_from_text(self, text: str, confidence: str = "explicit") -> List[ResourceReference]:
        """Extract resource references from arbitrary text"""
        resources = []
        
        # URLs
        url_pattern = r'https?://[^\s<>\[\]]+[^\s<>\[\].,;:!?"\']'
        for match in re.finditer(url_pattern, text):
            url = match.group(0)
            context = self._get_context(text, match.start(), match.end())
            self._add_unique_resource(resources, ResourceReference(
                content=url,
                url=url,
                context=context,
                confidence=confidence
            ))
        
        # Tool/service names
        tool_patterns = [
            (r'\b(YC|Y\s*Combinator)\s*(founder\s+)?match(ing)?\b', "YC Founder Match"),
            (r'\bCoffee\s*Space\b', "Coffee Space"),
            (r'\bZo\s*(Computer)?\b', "Zo"),
            (r'\bCareerspan\+?\b', "Careerspan"),
        ]
        
        for pattern, name in tool_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                context = self._get_context(text, match.start(), match.end())
                
                # Try to find link from content library
                lib_items = self.content_library.search(query=name, tags={})
                lib_items = [item for item in lib_items if item.type == "link"]
                
                if lib_items:
                    self._add_unique_resource(resources, ResourceReference(
                        content=lib_items[0].content or lib_items[0].url or "",
                        url=lib_items[0].url,
                        context=context,
                        confidence="implicit"
                    ))
        
        return resources
    
    def _extract_eloquent_from_key_moments(self, key_moments_text: str) -> List[EloquentLine]:
        """Extract memorable quotes from B21_KEY_MOMENTS"""
        lines = []
        
        # Pattern: **"Quote text"** (Speaker, timestamp)
        quote_pattern = r'\*\*"([^"]+)"\*\*\s*\(([^,]+),\s*([^)]+)\)'
        
        for match in re.finditer(quote_pattern, key_moments_text):
            quote = match.group(1)
            speaker = match.group(2).strip()
            
            # Get context (look for "Context:" after the quote)
            start_pos = match.end()
            context_match = re.search(r'Context:\s*([^\n]+)', key_moments_text[start_pos:start_pos+500])
            context = context_match.group(1) if context_match else ""
            
            lines.append(EloquentLine(
                text=quote,
                cleaned_text=quote,
                speaker=speaker,
                context=context,
                audience_reaction="positive",  # Assume quotes in KEY_MOMENTS had reactions
                timestamp=None
            ))
        
        return lines
    
    def _extract_questions_from_block(self, questions_text: str) -> List[str]:
        """Extract questions from B05_OUTSTANDING_QUESTIONS"""
        questions = []
        
        # Pattern: numbered or bulleted questions
        question_patterns = [
            r'^\d+\.\s*(.+\?)',  # 1. Question?
            r'^[-*]\s*(.+\?)',    # - Question?
            r'^\*\*(.+\?)\*\*',   # **Question?**
        ]
        
        for line in questions_text.split('\n'):
            line = line.strip()
            for pattern in question_patterns:
                match = re.match(pattern, line)
                if match:
                    questions.append(match.group(1).strip())
                    break
        
        return questions
    
    def _extract_actions_from_text(self, text: str) -> List[str]:
        """Extract action items from text"""
        actions = []
        
        # Pattern: action-oriented lines
        action_patterns = [
            r'^\d+\.\s*(.+)',      # 1. Action item
            r'^[-*]\s*(.+)',        # - Action item
            r'^\s*I(?:\'ll| will)\s+(.+)',  # I'll do something
            r'^\s*(?:Need to|Must|Should|Will)\s+(.+)',  # Need to...
        ]
        
        for line in text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            for pattern in action_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    action = match.group(1).strip()
                    if len(action) > 10:  # Filter out too-short items
                        actions.append(action)
                    break
        
        return actions[:10]  # Limit to 10 actions
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for a match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _suggest_resources(self, topics: List[str]) -> List[ResourceReference]:
        """Suggest resources from content library based on topics"""
        suggestions = []
        seen_urls = set()
        
        for topic in topics:
            items = self.content_library.search(query=topic, tags={})
            items = [item for item in items if item.type == "link"]
            
            for item in items[:2]:  # Max 2 per topic
                url = item.url or item.content or ""
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    suggestions.append(ResourceReference(
                        content=url,
                        url=url,
                        title=item.title,
                        context=f"Relevant to: {topic}",
                        confidence="suggested"
                    ))
        
        return suggestions
    
    def _deduplicate_resources(self, resources: List[ResourceReference]) -> List[ResourceReference]:
        """Remove duplicate resources"""
        seen = set()
        unique = []
        
        for res in resources:
            key = (res.url or res.content).rstrip('/').lower()
            if key not in seen:
                seen.add(key)
                unique.append(res)
        
        return unique


if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Parse meeting transcript into B-blocks")
    parser.add_argument("transcript", help="Path to transcript file")
    parser.add_argument("--meeting-folder", help="Meeting folder path")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    
    args = parser.parse_args()
    
    meeting_folder = Path(args.meeting_folder) if args.meeting_folder else Path(args.transcript).parent
    parser = BBlockParser(meeting_folder)
    
    blocks = parser.parse_transcript(Path(args.transcript))
    
    # Convert to JSON-serializable
    output = {
        "resources_explicit": [r.to_dict() for r in blocks["resources_explicit"]],
        "resources_suggested": [r.to_dict() for r in blocks["resources_suggested"]],
        "eloquent_lines": [e.to_dict() for e in blocks["eloquent_lines"]],
        "key_decisions": blocks["key_decisions"],
        "action_items": blocks["action_items"],
        "questions": blocks["questions"]
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))
