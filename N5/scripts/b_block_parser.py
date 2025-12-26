#!/usr/bin/env python3
"""
B-Block Parser — Extract structured blocks from meeting transcripts
Implements Phase 2 of Content Library integration

Extracts:
1. Resources explicitly/implicitly referenced in conversation
2. Eloquent lines/monologues with audience reaction signals
3. Key decisions, action items, questions

v2.0: Now uses LLM extraction for flexible reasoning instead of hardcoded regex patterns.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# Ensure sibling scripts are importable when running as a standalone script
sys.path.insert(0, str(Path(__file__).parent))

# === LLM EXTRACTOR IMPORT ===
from llm_extractor import LLMExtractor
# === END LLM EXTRACTOR IMPORT ===

# === V3 CONTENT LIBRARY IMPORT ===
from content_library_v3 import ContentLibraryV3
# === END V3 IMPORT ===


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
        self.content_library = ContentLibraryV3()
        self.llm_extractor = LLMExtractor()  # LLM extraction service
        self.blocks = {}  # Store loaded B-blocks
        self.confidence_order = {"explicit": 2, "implicit": 1, "suggested": 0}
        self.unmatched_commitments = []  # Commitments without Content Library match
        
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
    
    def parse_transcript(self, transcript_path: Path = None) -> Dict:
        """
        Parse transcript and extract all blocks
        
        Args:
            transcript_path: Path to transcript file. If None, searches meeting folder.
            
        Returns: {
            "resources_explicit": [ResourceReference],
            "resources_suggested": [ResourceReference],
            "eloquent_lines": [EloquentLine],
            "key_decisions": [str],
            "action_items": {"v_actions": [], "other_actions": [], "all_actions": []},
            "questions": [str],
            "topics": {...},
            "quotes": [...]
        }
        """
        # Find transcript if not provided
        if transcript_path is None:
            # Try multiple transcript file patterns
            transcript_files = list(self.meeting_folder.glob("*.transcript.jsonl"))
            if not transcript_files:
                transcript_files = list(self.meeting_folder.glob("transcript.jsonl"))
            if transcript_files:
                # Read JSONL transcript
                import json
                with open(transcript_files[0], 'r', encoding='utf-8') as f:
                    data = json.loads(f.readline())
                    transcript_text = data.get("text", "")
            else:
                # Try plain text
                txt_files = list(self.meeting_folder.glob("*.txt"))
                if txt_files:
                    with open(txt_files[0], 'r', encoding='utf-8') as f:
                        transcript_text = f.read()
                else:
                    logger.warning("No transcript found in meeting folder")
                    transcript_text = ""
        else:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
        
        # Use LLM-based extraction
        return {
            "resources_explicit": self.extract_explicit_resources(transcript_text),
            "resources_suggested": self.suggest_relevant_resources(transcript_text),
            "eloquent_lines": self.extract_eloquent_lines(transcript_text),
            "key_decisions": self.extract_key_decisions(transcript_text),
            "action_items": self.extract_action_items(transcript_text),
            "questions": self.extract_questions(transcript_text),
            "topics": self.detect_topics(transcript_text),
            "quotes": self.extract_quotes(transcript_text),
            "unmatched_commitments": self.unmatched_commitments,
        }
    
    def extract_explicit_resources(self, text: str) -> List[ResourceReference]:
        """
        Extract resources explicitly or implicitly mentioned in conversation
        
        Explicit: URLs, specific tool names, documents mentioned
        Implicit: References like "that article I sent", "the guide", "our demo"
        """
        resources: List[ResourceReference] = []
        
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
                
                # Try to find matching resource in Content Library v3
                lib_items = self.content_library.search(
                    query=title,
                    item_type="link",
                )
                if lib_items:
                    item = lib_items[0]
                    item_url = item.get("url") or ""
                    item_content = item.get("content") or ""
                    self._add_unique_resource(
                        resources,
                        ResourceReference(
                            content=item_url or item_content or title,
                            title=item.get("title") or title,
                            url=item_url or None,
                            context=context,
                            confidence="explicit",
                        ),
                    )
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
        Extract resources V committed to sending using LLM reasoning.
        
        Uses LLMExtractor to understand context and match against Content Library.
        Falls back to regex-based detection on API errors.
        """
        suggestions: List[ResourceReference] = []
        
        # Get library items for LLM context
        library_items = self.content_library.search(query=None, limit=200)
        simplified_items = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "url": item.get("url"),
                "type": item.get("item_type"),
            }
            for item in library_items
            if item.get("id")
        ]
        
        # Use LLM extraction
        result = self.llm_extractor.extract_resources(text, simplified_items)
        
        # Convert LLM output to ResourceReference objects
        for r in result.get("resources", []):
            suggestions.append(ResourceReference(
                content=r.get("matched_item_url") or r.get("intent", ""),
                title=r.get("matched_item_title") or r.get("intent"),
                url=r.get("matched_item_url"),
                context=r.get("commitment_text"),
                confidence=self._map_confidence(r.get("confidence", "medium")),
            ))
        
        # Capture unmatched commitments for V to review
        self.unmatched_commitments = result.get("unmatched_commitments", [])
        
        # Fallback: if LLM returned nothing, use topic-based suggestions
        if not suggestions:
            suggestions = self._suggest_by_topics_fallback(text)
        
        return suggestions
    
    def _suggest_by_topics_fallback(self, text: str) -> List[ResourceReference]:
        """Fallback: suggest resources based on detected topics (old regex method)"""
        suggestions: List[ResourceReference] = []
        topics = self._detect_topics_regex(text)
        
        for topic in topics:
            items = self.content_library.search(query=topic)
            for item in items[:2]:
                content = item.get("url") or item.get("content") or ""
                title = item.get("title") or content or topic
                suggestions.append(ResourceReference(
                    content=content,
                    title=title,
                    confidence="suggested",
                    context=f"Relevant to: {topic}"
                ))
        
        return suggestions
    
    def _map_confidence(self, llm_confidence: str) -> str:
        """Map LLM confidence levels to our internal levels"""
        mapping = {
            "high": "explicit",
            "medium": "implicit",
            "low": "suggested",
        }
        return mapping.get(llm_confidence.lower(), "implicit")
    
    def detect_topics(self, text: str) -> Dict[str, Any]:
        """
        Detect conversation topics using LLM reasoning.
        
        Returns rich topic data including primary topic, breakdown, and meeting type.
        """
        result = self.llm_extractor.extract_topics(text)
        
        # If LLM failed, use fallback
        if not result.get("topics"):
            topics = self._detect_topics_regex(text)
            return {
                "topics": topics,
                "primary_topic": topics[0] if topics else None,
                "secondary_topics": topics[1:] if len(topics) > 1 else [],
                "topic_breakdown": [],
                "meeting_type_inference": "unknown",
            }
        
        return result
    
    def _detect_topics_regex(self, text: str) -> List[str]:
        """Fallback: Detect topics using regex patterns"""
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
    
    # Keep _detect_topics as alias for backward compatibility
    def _detect_topics(self, text: str) -> List[str]:
        """Backward compatibility: returns just topic list"""
        result = self.detect_topics(text)
        return result.get("topics", [])
    
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
        """Extract key decisions using LLM extraction"""
        result = self.llm_extractor.extract_decisions(text)
        
        decisions = []
        for d in result.get("decisions", []):
            if isinstance(d, dict):
                decisions.append(d.get("decision", str(d)))
            else:
                decisions.append(str(d))
        
        # Fallback to regex if LLM returned nothing
        if not decisions:
            decisions = self._extract_decisions_regex(text)
        
        return decisions[:5]
    
    def _extract_decisions_regex(self, text: str) -> List[str]:
        """Fallback: regex-based decision extraction"""
        decisions = []
        decision_signals = [
            r'\b(let\'s|we\'ll|we should|I\'ll|I think we should)\b.{0,200}',
            r'\b(decided to|going to|plan to)\b.{0,200}',
        ]
        
        for pattern in decision_signals:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                decisions.append(match.group(0).strip())
        
        return decisions
    
    def extract_action_items(self, text: str) -> Dict[str, List]:
        """
        Extract action items using LLM reasoning.
        
        Returns structured dict with v_actions, other_actions, and all actions.
        """
        result = self.llm_extractor.extract_action_items(text)
        
        # Handle both dict and list returns from LLM
        v_actions = result.get("v_actions", [])
        other_actions = result.get("other_actions", [])
        all_actions = result.get("action_items", [])
        
        # Convert action dicts to strings if needed
        def normalize_action(a):
            if isinstance(a, dict):
                return a.get("action", str(a))
            return str(a)
        
        v_actions = [normalize_action(a) for a in v_actions]
        other_actions = [normalize_action(a) for a in other_actions]
        all_actions = [normalize_action(a) for a in all_actions]
        
        # Fallback if LLM returned nothing
        if not all_actions and not v_actions:
            all_actions = self._extract_actions_regex(text)
        
        return {
            "v_actions": v_actions,
            "other_actions": other_actions,
            "all_actions": all_actions,
            "follow_up_needed": result.get("follow_up_needed", []),
        }
    
    def _extract_actions_regex(self, text: str) -> List[str]:
        """Fallback: regex-based action extraction"""
        actions = []
        action_signals = [
            r'\b(I\'ll|I will|will)\s+(send|share|follow up|reach out|intro|connect)\b.{0,200}',
            r'\b(next step|action item|to-do|todo)\b.{0,200}',
        ]
        
        for pattern in action_signals:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                actions.append(match.group(0).strip())
        
        return actions[:5]
    
    def extract_quotes(self, text: str) -> List[Dict]:
        """
        Extract quotable moments using LLM reasoning.
        
        Returns list of quote dicts with speaker, text, category, and quotability score.
        """
        result = self.llm_extractor.extract_quotable_moments(text)
        return result.get("quotes", [])
    
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
        resources: List[ResourceReference] = []
        
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
                
                # Try to find link from content library v3
                lib_items = self.content_library.search(
                    query=name,
                    item_type="link",
                )
                
                if lib_items:
                    item = lib_items[0]
                    url = item.get("url") or ""
                    content_val = item.get("content") or url
                    self._add_unique_resource(resources, ResourceReference(
                        content=content_val,
                        url=url or None,
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
        suggestions: List[ResourceReference] = []
        seen_urls = set()
        
        for topic in topics:
            items = self.content_library.search(
                query=topic,
                item_type="link",
            )
            
            for item in items[:2]:  # Max 2 per topic
                url = item.get("url") or item.get("content") or ""
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    suggestions.append(ResourceReference(
                        content=url,
                        url=url,
                        title=item.get("title"),
                        context=f"Relevant to: {topic}",
                        confidence="suggested",
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
    # action_items is now a dict with v_actions, other_actions, all_actions
    action_items = blocks["action_items"]
    if isinstance(action_items, dict):
        # Flatten for backward compatibility with email_composer
        action_items_list = action_items.get("v_actions", []) + action_items.get("other_actions", [])
        if not action_items_list:
            action_items_list = action_items.get("all_actions", [])
    else:
        action_items_list = action_items
    
    output = {
        "resources_explicit": [r.to_dict() for r in blocks["resources_explicit"]],
        "resources_suggested": [r.to_dict() for r in blocks["resources_suggested"]],
        "eloquent_lines": [e.to_dict() for e in blocks["eloquent_lines"]],
        "key_decisions": blocks["key_decisions"],
        "action_items": action_items_list,  # List for backward compat
        "action_items_structured": blocks["action_items"],  # Full dict for new consumers
        "questions": blocks["questions"],
        "topics": blocks.get("topics", {}),
        "quotes": blocks.get("quotes", []),
        "unmatched_commitments": blocks.get("unmatched_commitments", []),
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))




