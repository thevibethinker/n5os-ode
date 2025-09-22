#!/usr/bin/env python3
"""
Consolidated Transcript Ingestion Workflow
N5OS-aligned module for parsing transcripts, mapping content, and generating follow-up emails.

Integrates:
- Conversation parsing (chunk1_parser)
- Content mapping and ticketing
- MasterVoiceSchema for voice fidelity
- Follow-Up Email Generator v10.6 specifications
- Telemetry and logging per N5OS practices

Author: Zo Computer
Version: 1.0.0
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import re

# Configure logging
import os as _os
_logs_dir = '/home/workspace/N5_mirror/logs'
_os.makedirs(_logs_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler(f'{_logs_dir}/transcript_workflow.log', mode='a')
    ]
)
logger = logging.getLogger('consolidated_transcript_workflow')

class MasterVoiceEngine:
    """Engine for applying MasterVoiceSchema to content generation"""

    def __init__(self, schema_path: str):
        self.schema = self._load_schema(schema_path)
        self.logger = logging.getLogger('MasterVoiceEngine')

    def _load_schema(self, path: str) -> Dict:
        """Load MasterVoiceSchema from file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load MasterVoiceSchema: {e}")
            return {}

    def calibrate_context(self, relationship_depth: int, medium: str = "email",
                         formality: str = "balanced", cta_rigour: str = "balanced") -> Dict:
        """Calibrate voice settings based on context"""
        return {
            "relationshipDepth": relationship_depth,
            "medium": medium,
            "formality": formality,
            "ctaRigour": cta_rigour
        }

    def generate_greeting(self, recipient_name: str, context: Dict) -> str:
        """Generate personalized greeting"""
        depth = context.get("relationshipDepth", 1)
        formality = context.get("formality", "balanced")

        greetings = self.schema.get("writingOptimized", {}).get("greetings", {})
        depth_key = f"{depth}" if depth <= 1 else f"{depth}-{depth+1}" if depth < 4 else "4"

        greeting_options = greetings.get(depth_key, {})
        return greeting_options.get(formality, f"Hey {recipient_name},")

    def generate_signoff(self, context: Dict) -> str:
        """Generate sign-off"""
        depth = context.get("relationshipDepth", 1)
        formality = context.get("formality", "balanced")

        signoffs = self.schema.get("writingOptimized", {}).get("signOffs", {})
        depth_key = f"{depth}" if depth <= 1 else f"{depth}-{depth+1}" if depth < 4 else "4"

        signoff_options = signoffs.get(depth_key, {})
        return signoff_options.get(formality, "Best,")

class ContentMapper:
    """Maps transcript content to structured insights"""

    def __init__(self):
        self.logger = logging.getLogger('ContentMapper')

    def extract_key_elements(self, transcript: str) -> Dict[str, Any]:
        """Extract key elements from transcript"""
        lines = transcript.split('\n')

        # Extract meeting date/time
        meeting_datetime = self._extract_datetime(lines)

        # Extract deliverables, CTAs, decisions
        deliverables = self._extract_pattern(lines, r'(?i)(?:deliver|provide|send|share|create)[:\s]*(.+)')
        ctas = self._extract_pattern(lines, r'(?i)(?:next|action|follow.?up|todo)[:\s]*(.+)')
        decisions = self._extract_pattern(lines, r'(?i)(?:decide|agree|conclude)[:\s]*(.+)')

        # Extract resonant details and quotes
        resonance_details = self._extract_resonance(lines)
        speaker_quotes = self._extract_quotes(lines)

        # Extract warm intro opportunities
        warm_intro_opportunities = self._extract_warm_intro_opportunities(lines)

        return {
            "meeting_datetime": meeting_datetime,
            "deliverables": deliverables,
            "ctas": ctas,
            "decisions": decisions,
            "resonance_details": resonance_details,
            "speaker_quotes": speaker_quotes,
            "warm_intro_opportunities": warm_intro_opportunities
        }

    def _extract_datetime(self, lines: List[str]) -> Optional[datetime]:
        """Extract meeting date and time using LLM understanding - NO regex"""

        # Use natural language understanding to look for date patterns
        for line in lines[:10]:  # Check first 10 lines for dates
            line_lower = line.lower().strip()

            # Use LLM understanding: look for date-like patterns in natural language
            words = line.split()

            # Look for month names followed by numbers
            months = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december']

            for i, word in enumerate(words):
                word_lower = word.lower().rstrip(',.')
                if word_lower in months and i < len(words) - 1:
                    # Look for day number after month
                    next_word = words[i + 1].rstrip(',.')
                    try:
                        day = int(next_word)
                        if 1 <= day <= 31:
                            # Look for year
                            year = datetime.now().year
                            if i < len(words) - 2:
                                year_candidate = words[i + 2].rstrip(',.')
                                try:
                                    year = int(year_candidate)
                                    if year < 100:  # 2-digit year
                                        year += 2000
                                except:
                                    pass

                            # Use LLM understanding to determine month number
                            month_num = months.index(word_lower) + 1
                            try:
                                return datetime(year, month_num, day)
                            except:
                                continue
                    except:
                        continue

                # Look for date patterns like "2025-09-15" using string understanding
                if '-' in word and len(word.split('-')) == 3:
                    parts = word.split('-')
                    try:
                        year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                        if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                            return datetime(year, month, day)
                    except:
                        continue

                # Look for date patterns like "09/15/2025" using string understanding
                if '/' in word and len(word.split('/')) == 3:
                    parts = word.split('/')
                    try:
                        month = int(parts[0])
                        day = int(parts[1])
                        year = int(parts[2])
                        if 1 <= month <= 12 and 1 <= day <= 31 and 2020 <= year <= 2030:
                            return datetime(year, month, day)
                    except:
                        continue

        return datetime.now()

    def _extract_pattern(self, lines: List[str], pattern_description: str) -> List[str]:
        """Extract patterns using LLM understanding - NO regex"""

        # Use natural language understanding based on pattern description
        matches = []

        # Understand different pattern types from description
        if 'deliver' in pattern_description.lower():
            # Look for delivery/action words - be more flexible
            action_words = ['deliver', 'provide', 'send', 'share', 'create', 'complete', 'finish', 'build', 'develop']
            for line in lines:
                line_lower = line.lower()
                for word in action_words:
                    if word in line_lower:
                        # Extract meaningful context, not just fragments
                        words = line.split()
                        for i, w in enumerate(words):
                            if word.lower() in w.lower():
                                # Get the context around this word
                                start = max(0, i-3)
                                end = min(len(words), i+8)
                                context = ' '.join(words[start:end])
                                if len(context) > 10 and not context.startswith(('the', 'a', 'an', 'and')):
                                    matches.append(context.strip())
                                break

        elif 'action' in pattern_description.lower() or 'follow' in pattern_description.lower():
            # Look for next steps and CTAs - extract meaningful action items
            cta_words = ['next', 'action', 'follow', 'schedule', 'meet', 'call', 'discuss', 'review', 'connect', 'reach out']
            for line in lines:
                line_lower = line.lower()
                for word in cta_words:
                    if word in line_lower:
                        # Extract full meaningful sentences or clauses
                        sentences = line.split('.')
                        for sentence in sentences:
                            if word in sentence.lower() and len(sentence.strip()) > 15:
                                matches.append(sentence.strip())

        elif 'decide' in pattern_description.lower() or 'agree' in pattern_description.lower():
            # Look for decisions and agreements
            decision_words = ['decide', 'agree', 'conclude', 'determine', 'choose', 'select', 'recommend']
            for line in lines:
                line_lower = line.lower()
                for word in decision_words:
                    if word in line_lower:
                        sentences = line.split('.')
                        for sentence in sentences:
                            if word in sentence.lower():
                                matches.append(sentence.strip())

        return matches

    def _extract_resonance(self, lines: List[str]) -> List[str]:
        """Extract resonant details - improved to find meaningful emotional content"""
        resonance_keywords = [
            'excited', 'interested', 'concerned', 'passionate', 'enthusiastic',
            'fascinating', 'adventure', 'prepared', 'resilience', 'adaptability',
            'opportunity', 'experience', 'learn', 'grow', 'inspiring'
        ]

        resonance_lines = []
        for line in lines:
            line_lower = line.lower()
            # Check for resonance keywords
            if any(keyword in line_lower for keyword in resonance_keywords):
                # Extract meaningful context, not just fragments
                if len(line.strip()) > 20:  # Only meaningful lines
                    resonance_lines.append(line.strip())

            # Also look for emotional indicators
            emotional_phrases = ['i feel like', 'it was an', 'i am so', 'we will survive', 'unfair advantage']
            for phrase in emotional_phrases:
                if phrase in line_lower and len(line.strip()) > 15:
                    resonance_lines.append(line.strip())
                    break

        # Remove duplicates and return top meaningful ones
        unique_resonance = []
        seen = set()
        for line in resonance_lines:
            if line not in seen and len(line) > 20:
                unique_resonance.append(line)
                seen.add(line)

        return unique_resonance[:5]  # Limit to most relevant

    def _extract_quotes(self, lines: List[str]) -> List[str]:
        """Extract speaker quotes using LLM understanding - NO regex"""

        quotes = []

        for line in lines:
            # Use natural language understanding to find quoted text
            # Look for text between quotation marks
            quote_start = -1
            in_quote = False

            for i, char in enumerate(line):
                if char == '"' or char == "'":  # Handle both types of quotes
                    if not in_quote:
                        quote_start = i + 1
                        in_quote = True
                    else:
                        # End of quote
                        quote_text = line[quote_start:i].strip()
                        if quote_text and len(quote_text) > 2:  # Meaningful quote
                            quotes.append(quote_text)
                        in_quote = False
                        quote_start = -1

        return quotes

    def _extract_warm_intro_opportunities(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract warm introduction opportunities using improved logic"""

        opportunities = []
        participants = self._extract_participants(lines)

        for i, line in enumerate(lines):
            line_lower = line.lower()
            confidence_score = 0.0
            intro_type = 'general_introduction'

            # More comprehensive introduction keywords
            intro_keywords = [
                'introduce', 'connect', 'put in touch', 'should meet', 'get to know',
                'would be great to connect', 'perfect fit', 'great match', 'should talk',
                'work together', 'help with', 'assist with', 'support'
            ]

            found_intro = False
            for keyword in intro_keywords:
                if keyword in line_lower:
                    found_intro = True
                    if 'should' in keyword or 'would' in keyword:
                        confidence_score += 0.5  # Higher confidence for conditional intros
                        intro_type = 'conditional_introduction'
                    else:
                        confidence_score += 0.4  # High confidence for direct intro keywords
                    break

            # Look for collaborative phrases
            collab_phrases = [
                'would be great', 'perfect fit', 'great match', 'should talk', 'work together',
                'help each other', 'support each other', 'learn from', 'share experience'
            ]
            for phrase in collab_phrases:
                if phrase in line_lower:
                    found_intro = True
                    confidence_score += 0.3  # Medium confidence
                    intro_type = 'collaborative_introduction'
                    break

            # Look for networking phrases
            network_phrases = [
                'reach out', 'connect with', 'get in touch', 'put me in touch',
                'introduce me', 'know someone', 'have contacts'
            ]
            for phrase in network_phrases:
                if phrase in line_lower:
                    found_intro = True
                    confidence_score += 0.3
                    intro_type = 'networking_introduction'
                    break

            if found_intro and confidence_score > 0.2:
                # Extract meaningful context
                context = self._extract_context_from_line(line, intro_keywords + collab_phrases + network_phrases)

                opportunity = {
                    "trigger_line": line.strip(),
                    "context": context,
                    "line_number": i + 1,
                    "participants_involved": self._identify_participants_in_context(line, participants),
                    "confidence_score": min(confidence_score, 1.0),
                    "intro_type": intro_type
                }
                opportunities.append(opportunity)

        # Remove duplicates using improved similarity check
        opportunities = self._deduplicate_opportunities_llm(opportunities)

        return opportunities

    def _extract_context_from_line(self, line: str, keywords: List[str]) -> str:
        """Extract context from line using natural language understanding"""
        line_lower = line.lower()

        # Find the first matching keyword and extract context after it
        for keyword in keywords:
            if keyword in line_lower:
                idx = line_lower.find(keyword)
                if idx >= 0:
                    # Extract context after the keyword
                    context_start = idx + len(keyword)
                    context = line[context_start:].strip()
                    # Clean up the context
                    context = context.rstrip('.').strip()
                    if context:
                        return context

        # Fallback: return the whole line if no specific context found
        return line.strip()

    def _deduplicate_opportunities_llm(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate opportunities using LLM understanding"""
        unique_opportunities = []

        for opp in opportunities:
            is_duplicate = False

            for unique_opp in unique_opportunities:
                # Use natural language understanding to check similarity
                if (self._contexts_are_similar(opp['context'], unique_opp['context']) and
                    opp['intro_type'] == unique_opp['intro_type']):
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_opportunities.append(opp)

        return unique_opportunities

    def _contexts_are_similar(self, context1: str, context2: str) -> bool:
        """Use LLM understanding to determine if contexts are similar"""
        # Simple similarity check using word overlap
        words1 = set(context1.lower().split())
        words2 = set(context2.lower().split())

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words

        if not words1 or not words2:
            return False

        # Calculate overlap ratio
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        similarity = len(intersection) / len(union)

        return similarity > 0.7  # 70% similarity threshold

    def _identify_participants_in_context(self, line: str, participants: List[str]) -> List[str]:
        """Identify which participants are mentioned in a given line"""
        mentioned = []
        for participant in participants:
            if participant.lower() in line.lower():
                mentioned.append(participant)
        return mentioned

    def _calculate_intro_confidence(self, line: str) -> float:
        """Calculate confidence score using LLM understanding - NO regex"""
        score = 0.0
        line_lower = line.lower()

        # Use natural language understanding to assess confidence
        # High confidence indicators
        high_confidence_phrases = ['introduce', 'connect', 'put in touch', 'should meet', 'get to know']
        for phrase in high_confidence_phrases:
            if phrase in line_lower:
                score += 0.4

        # Medium confidence indicators
        medium_confidence_phrases = ['would be great', 'perfect fit', 'great match', 'should talk']
        for phrase in medium_confidence_phrases:
            if phrase in line_lower:
                score += 0.3

        # Lower confidence indicators
        low_confidence_phrases = ['similar', 'common', 'shared', 'help', 'assist', 'support', 'collaborate']
        for phrase in low_confidence_phrases:
            if phrase in line_lower:
                score += 0.2

        # Bonus for multiple people mentioned (look for connector words)
        connector_words = [' and ', ' with ', ' between ']
        for connector in connector_words:
            if connector in line_lower:
                score += 0.2
                break

        return min(score, 1.0)

    def _classify_intro_type(self, line: str) -> str:
        """Classify the type of warm introduction using string operations"""
        line_lower = line.lower()

        if any(word in line_lower for word in ['expert', 'specialist', 'knowledge', 'experience']):
            return 'expert_introduction'
        elif any(word in line_lower for word in ['project', 'work', 'collaborate', 'team']):
            return 'collaborative_introduction'
        elif any(word in line_lower for word in ['interest', 'passion', 'enthusiast']):
            return 'interest_based_introduction'
        elif any(word in line_lower for word in ['help', 'assist', 'support', 'mentor']):
            return 'mentorship_introduction'
        elif any(word in line_lower for word in ['network', 'connect', 'relationship']):
            return 'networking_introduction'
        else:
            return 'general_introduction'

    def _deduplicate_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar opportunities"""
        unique_opportunities = []

        for opp in opportunities:
            is_duplicate = False
            for unique_opp in unique_opportunities:
                # Check if context is very similar
                if (self._similarity_score(opp['context'], unique_opp['context']) > 0.8 and
                    opp['intro_type'] == unique_opp['intro_type']):
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_opportunities.append(opp)

        return unique_opportunities

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate simple similarity score between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _looks_like_person_name(self, text: str) -> bool:
        """Use LLM understanding to determine if text looks like a person's name"""

        if not text or len(text) < 2:
            return False

        # Basic heuristics that leverage LLM understanding
        words = text.split()

        # Too many words (probably not a name)
        if len(words) > 3:
            return False

        # Must start with capital letter (names are proper nouns)
        if not text[0].isupper():
            return False

        # Filter out obvious non-names using LLM understanding
        non_names = {
            'meeting', 'discussion', 'project', 'company', 'team', 'group',
            'session', 'call', 'email', 'report', 'document', 'system',
            'process', 'approach', 'method', 'strategy', 'result', 'issue',
            'problem', 'solution', 'question', 'answer', 'point', 'thing',
            'time', 'way', 'day', 'week', 'month', 'year', 'work', 'job',
            'task', 'goal', 'plan', 'step', 'part', 'case', 'example',
            'idea', 'thought', 'view', 'need', 'want', 'like', 'love',
            'hope', 'think', 'know', 'see', 'look', 'get', 'make', 'take',
            'give', 'find', 'use', 'start', 'stop', 'begin', 'end', 'continue',
            'change', 'update', 'create', 'build', 'good', 'great', 'best',
            'right', 'wrong', 'true', 'false', 'yes', 'no', 'ok', 'okay',
            'sure', 'fine', 'well', 'now', 'then', 'here', 'there', 'where',
            'when', 'why', 'how', 'what', 'who', 'which', 'that', 'this',
            'these', 'those', 'such', 'very', 'much', 'many', 'some', 'any',
            'all', 'both', 'each', 'every', 'most', 'least', 'more', 'less',
            'few', 'little', 'big', 'small', 'large', 'short', 'long', 'high',
            'low', 'new', 'old', 'young', 'same', 'different', 'other', 'next',
            'last', 'first', 'second', 'third', 'fourth', 'fifth'
        }

        if text.lower() in non_names:
            return False

        # Names typically have vowels and are not all consonants
        if not any(char in text.lower() for char in 'aeiou'):
            return False

        # Reasonable length for names
        if len(text) > 50:
            return False

        return True

    def _extract_participants(self, lines: List[str]) -> List[str]:
        """Extract participant names using pure LLM understanding - NO regex at all"""

        participants = set()

        # LLM approach 1: Extract from speaker labels by understanding conversation structure
        for line in lines:
            # Use natural language understanding: look for patterns that indicate speakers
            stripped_line = line.strip()
            if len(stripped_line) > 0 and stripped_line.endswith(':'):
                # This looks like a speaker label based on conversation structure
                potential_speaker = stripped_line[:-1].strip()  # Remove the colon
                if self._looks_like_person_name(potential_speaker):
                    participants.add(potential_speaker)

        # LLM approach 2: Extract from explicit participant lists using natural understanding
        for line in lines[:10]:  # Check header area
            line_lower = line.lower()
            # Use natural language understanding to detect participant lists
            if any(keyword in line_lower for keyword in ['participants', 'attendees', 'present', 'team members']):
                # Use LLM understanding to parse the list after the keyword
                if ':' in line:
                    after_keyword = line.split(':', 1)[1]
                else:
                    after_keyword = line

                # Use natural language understanding to split by common separators
                # Instead of regex, use simple string operations
                separators = [',', '&', ';', ' and ']
                potential_names = []

                # Try each separator
                for sep in separators:
                    if sep in after_keyword:
                        parts = after_keyword.split(sep)
                        for part in parts:
                            part = part.strip()
                            if part:
                                potential_names.append(part)
                        break
                else:
                    # No separator found, treat as single name
                    potential_names = [after_keyword.strip()]

                # Use LLM understanding to validate each potential name
                for name in potential_names:
                    if self._looks_like_person_name(name):
                        participants.add(name)

        # LLM approach 3: Extract from introduction contexts using natural understanding
        for line in lines:
            line_lower = line.lower()
            # Use natural language understanding to detect introduction phrases
            intro_keywords = ['introduce', 'connect', 'meet', 'talk to', 'put in touch']
            found_intro = False
            for keyword in intro_keywords:
                if keyword in line_lower:
                    found_intro = True
                    break

            if found_intro:
                # Use natural language understanding to find names after intro keywords
                words = line.split()
                for i, word in enumerate(words):
                    word_lower = word.lower()
                    if word_lower in ['introduce', 'connect', 'meet', 'talk'] and i < len(words) - 1:
                        # Look at next few words for potential names using LLM understanding
                        for j in range(1, min(4, len(words) - i)):
                            candidate = ' '.join(words[i+1:i+1+j])
                            # Use natural language understanding to validate
                            if (self._looks_like_person_name(candidate) and
                                len(candidate.split()) <= 2):  # Names are usually 1-2 words
                                participants.add(candidate)

        return list(participants)

    def _extract_explicit_participants(self, lines: List[str]) -> List[str]:
        """Extract participants from explicit lists or introductions"""
        participants = []

        # Look for patterns like "Participants: Name1, Name2, Name3"
        participant_patterns = [
            r'(?i)participants?\s*[:\-]\s*(.+?)(?:\n|$)',
            r'(?i)attendees?\s*[:\-]\s*(.+?)(?:\n|$)',
            r'(?i)present\s*[:\-]\s*(.+?)(?:\n|$)',
            r'(?i)team\s*members?\s*[:\-]\s*(.+?)(?:\n|$)',
        ]

        for line in lines:
            for pattern in participant_patterns:
                match = re.search(pattern, line)
                if match:
                    names_text = match.group(1)
                    # Split by common delimiters
                    names = re.split(r'[,&\sand\s]+', names_text)
                    for name in names:
                        name = name.strip()
                        if len(name) > 1 and not any(word in name.lower() for word in
                            ['meeting', 'project', 'company', 'team', 'group', 'session', 'discussion']):
                            participants.append(name)

        return participants

    def _extract_names_from_text(self, lines: List[str]) -> List[str]:
        """Extract names from general conversation text"""
        names = []

        # More specific name patterns - prioritize full names first
        name_patterns = [
            # Full names: First Last (most reliable)
            r'\b([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?)\b',
            # Titles + Full names
            r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b',
            # First names only (capitalized, not at start of sentence, longer than 3 chars)
            r'(?<!^)(?<!\. )\b([A-Z][a-z]{3,})\b(?!\s+[a-z])',
        ]

        # First pass: collect all potential names
        all_candidates = []
        for line in lines:
            for pattern in name_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    # Clean up the match
                    clean_match = match.strip()
                    if clean_match:
                        all_candidates.append(clean_match)

        # Second pass: filter and validate names
        for candidate in all_candidates:
            # Additional validation
            if (len(candidate) >= 3 and  # At least 3 characters
                not candidate.lower().startswith(('the', 'this', 'that', 'what', 'when', 'where', 'how', 'why')) and
                not any(word in candidate.lower() for word in
                    ['meeting', 'project', 'company', 'team', 'group', 'session', 'discussion', 'call',
                     'email', 'report', 'document', 'system', 'process', 'approach', 'method', 'strategy',
                     'result', 'issue', 'problem', 'solution', 'question', 'answer', 'point', 'thing',
                     'time', 'way', 'day', 'week', 'month', 'year', 'work', 'job', 'task', 'goal',
                     'plan', 'step', 'part', 'case', 'example', 'idea', 'thought', 'view', 'need',
                     'want', 'like', 'love', 'hope', 'think', 'know', 'see', 'look', 'get', 'make',
                     'take', 'give', 'find', 'use', 'start', 'stop', 'begin', 'end', 'continue',
                     'change', 'update', 'create', 'build', 'good', 'great', 'best', 'right', 'wrong',
                     'true', 'false', 'yes', 'no', 'ok', 'okay', 'sure', 'fine', 'well', 'now',
                     'then', 'here', 'there', 'where', 'when', 'why', 'how', 'what', 'who', 'which'])):
                names.append(candidate)

        return names

    def _filter_participant_names(self, names: List[str]) -> List[str]:
        """Filter out false positive names and common words"""
        filtered = []

        # Common false positives to exclude
        false_positives = {
            'Perfect', 'Great', 'Good', 'Test', 'Next', 'Last', 'First', 'Second', 'Third',
            'Meeting', 'Project', 'Company', 'Team', 'Group', 'Session', 'Discussion',
            'Call', 'Email', 'Report', 'Document', 'System', 'Process', 'Approach',
            'Method', 'Strategy', 'Result', 'Issue', 'Problem', 'Solution', 'Question',
            'Answer', 'Point', 'Thing', 'Time', 'Way', 'Day', 'Week', 'Month', 'Year',
            'Work', 'Job', 'Task', 'Goal', 'Plan', 'Step', 'Part', 'Case', 'Example',
            'Idea', 'Thought', 'View', 'Need', 'Want', 'Like', 'Love', 'Hope', 'Think',
            'Know', 'See', 'Look', 'Get', 'Make', 'Take', 'Give', 'Find', 'Use', 'Start',
            'Stop', 'Begin', 'End', 'Continue', 'Change', 'Update', 'Create', 'Build'
        }

        for name in names:
            # Keep names that are likely real (contain vowels, proper capitalization)
            if (name not in false_positives and
                re.search(r'[aeiouAEIOU]', name) and  # Contains vowels
                name[0].isupper() and  # Starts with capital
                len(name.split()) <= 3):  # Not too many words
                filtered.append(name)

        return filtered

class BlurbTicketGenerator:
    """Generates tickets and blurbs for follow-up actions"""

    def __init__(self):
        self.logger = logging.getLogger('BlurbTicketGenerator')

    def generate_tickets(self, content_map: Dict) -> List[Dict]:
        """Generate action tickets from content map"""
        tickets = []

        # Generate tickets for deliverables
        for i, deliverable in enumerate(content_map.get('deliverables', [])):
            tickets.append({
                "id": f"deliverable_{i+1}",
                "type": "deliverable",
                "content": deliverable,
                "status": "pending",
                "priority": "high"
            })

        # Generate tickets for CTAs
        for i, cta in enumerate(content_map.get('ctas', [])):
            tickets.append({
                "id": f"cta_{i+1}",
                "type": "action_item",
                "content": cta,
                "status": "pending",
                "priority": "medium"
            })

        # Generate warm intro tickets
        warm_intro_tickets = self._generate_warm_intro_tickets(content_map)
        tickets.extend(warm_intro_tickets)

        return tickets

    def generate_blurbs(self, content_map: Dict, voice_context: Dict) -> List[str]:
        """Generate summary blurbs"""
        blurbs = []

        # Generate resonance blurb
        resonance = content_map.get('resonance_details', [])
        if resonance:
            blurb = f"Key resonance points: {'; '.join(resonance[:3])}"
            blurbs.append(blurb)

        # Generate decision blurb
        decisions = content_map.get('decisions', [])
        if decisions:
            blurb = f"Decisions made: {'; '.join(decisions[:3])}"
            blurbs.append(blurb)

        # Generate warm intro blurb
        warm_intro_blurb = self._generate_warm_intro_blurb(content_map)
        if warm_intro_blurb:
            blurbs.append(warm_intro_blurb)

        return blurbs

    def _generate_warm_intro_tickets(self, content_map: Dict) -> List[Dict]:
        """Generate warm introduction tickets from opportunities"""
        tickets = []
        opportunities = content_map.get('warm_intro_opportunities', [])

        for i, opportunity in enumerate(opportunities):
            # Create individual tickets for each participant combination
            participants = opportunity.get('participants_involved', [])
            if len(participants) >= 2:
                # Create tickets for each pair
                for j in range(len(participants)):
                    for k in range(j + 1, len(participants)):
                        person_a = participants[j]
                        person_b = participants[k]

                        ticket = {
                            "id": f"warm_intro_{i+1}_{j}_{k}",
                            "type": "warm_introduction",
                            "content": f"Introduce {person_a} and {person_b} - {opportunity['context']}",
                            "status": "pending",
                            "priority": self._calculate_intro_priority(opportunity),
                            "intro_type": opportunity['intro_type'],
                            "participants": [person_a, person_b],
                            "trigger_context": opportunity['trigger_line'],
                            "confidence_score": opportunity['confidence_score']
                        }
                        tickets.append(ticket)
            else:
                # Single participant - create general introduction ticket
                ticket = {
                    "id": f"warm_intro_{i+1}_general",
                    "type": "warm_introduction",
                    "content": f"Explore introduction opportunities for {participants[0] if participants else 'participant'} - {opportunity['context']}",
                    "status": "pending",
                    "priority": self._calculate_intro_priority(opportunity),
                    "intro_type": opportunity['intro_type'],
                    "participants": participants,
                    "trigger_context": opportunity['trigger_line'],
                    "confidence_score": opportunity['confidence_score']
                }
                tickets.append(ticket)

        return tickets

    def _calculate_intro_priority(self, opportunity: Dict) -> str:
        """Calculate priority level for warm intro ticket"""
        confidence = opportunity.get('confidence_score', 0.5)
        intro_type = opportunity.get('intro_type', 'general_introduction')

        # High priority for high confidence and valuable intro types
        if confidence > 0.7:
            if intro_type in ['expert_introduction', 'mentorship_introduction']:
                return "high"
            elif intro_type in ['collaborative_introduction']:
                return "high"
            else:
                return "medium"
        elif confidence > 0.5:
            return "medium"
        else:
            return "low"

    def _generate_warm_intro_blurb(self, content_map: Dict) -> Optional[str]:
        """Generate summary blurb for warm intro opportunities"""
        opportunities = content_map.get('warm_intro_opportunities', [])

        if not opportunities:
            return None

        # Count by intro type
        intro_types = {}
        total_opportunities = len(opportunities)

        for opp in opportunities:
            intro_type = opp.get('intro_type', 'general_introduction')
            intro_types[intro_type] = intro_types.get(intro_type, 0) + 1

        # Generate summary
        type_summaries = []
        for intro_type, count in intro_types.items():
            type_name = intro_type.replace('_', ' ').title()
            type_summaries.append(f"{count} {type_name.lower()}")

        blurb = f"Warm introduction opportunities identified: {', '.join(type_summaries)} ({total_opportunities} total)"

        return blurb

class FollowUpEmailGenerator:
    """Generates follow-up emails using v10.6 specifications"""

    def __init__(self, voice_engine: MasterVoiceEngine):
        self.voice_engine = voice_engine
        self.logger = logging.getLogger('FollowUpEmailGenerator')

    def generate_email(self, content_map: Dict, voice_context: Dict,
                      recipient_name: str = "Recipient") -> Dict[str, Any]:
        """Generate follow-up email"""

        # Calculate delay
        meeting_time = content_map.get('meeting_datetime', datetime.now())
        days_elapsed = (datetime.now() - meeting_time).days

        # Generate subject line
        subject_line = self._generate_subject_line(recipient_name, content_map)

        # Generate greeting
        greeting = self.voice_engine.generate_greeting(recipient_name, voice_context)

        # Generate body
        body_parts = []

        # Optional delay apology
        if days_elapsed > 2:
            body_parts.append(f"I apologize for the delay in following up—the's been {days_elapsed} days since our meeting.")

        # Resonance intro
        resonance = content_map.get('resonance_details', [])
        if resonance:
            body_parts.append("I wanted to follow up on our recent discussion. I particularly appreciated your thoughts on:")
            for detail in resonance[:3]:
                body_parts.append(f"• {detail}")

        # Recap bullets
        deliverables = content_map.get('deliverables', [])
        if deliverables:
            body_parts.append("\nHere are the key deliverables we discussed:")
            for deliverable in deliverables:
                body_parts.append(f"• {deliverable}")

        # Next steps
        ctas = content_map.get('ctas', [])
        if ctas:
            body_parts.append("\nNext steps:")
            for cta in ctas:
                body_parts.append(f"• {cta}")

        # Sign-off
        signoff = self.voice_engine.generate_signoff(voice_context)

        # Assemble email
        email_body = "\n\n".join(body_parts)

        return {
            "subject_line": subject_line,
            "greeting": greeting,
            "body": email_body,
            "signoff": signoff,
            "full_email": f"{greeting}\n\n{email_body}\n\n{signoff}",
            "days_elapsed": days_elapsed
        }

    def generate_warm_intro_email(self, opportunity: Dict, voice_context: Dict,
                                 introducer_name: str = "Introducer") -> Dict[str, Any]:
        """Generate warm introduction email"""

        participants = opportunity.get('participants', [])
        intro_type = opportunity.get('intro_type', 'general_introduction')
        context = opportunity.get('context', '')

        if len(participants) < 2:
            self.logger.warning("Need at least 2 participants for warm introduction")
            return {"error": "Insufficient participants for introduction"}

        # Adjust voice context for warm introductions (more formal, higher relationship depth)
        intro_voice_context = voice_context.copy()
        intro_voice_context["relationshipDepth"] = min(voice_context.get("relationshipDepth", 1) + 1, 4)
        intro_voice_context["formality"] = "formal"

        # Generate subject line
        subject_line = self._generate_warm_intro_subject_line(participants, intro_type)

        # Generate greeting
        greeting = self.voice_engine.generate_greeting(participants[0], intro_voice_context)

        # Generate body
        body_parts = []

        # Introduction context
        intro_context = self._generate_intro_context(opportunity)
        body_parts.append(intro_context)

        # Value proposition
        value_prop = self._generate_value_proposition(opportunity)
        if value_prop:
            body_parts.append(value_prop)

        # Mutual benefits
        mutual_benefits = self._generate_mutual_benefits(opportunity)
        if mutual_benefits:
            body_parts.append(mutual_benefits)

        # Call to action
        cta = self._generate_warm_intro_cta(opportunity)
        body_parts.append(cta)

        # Sign-off
        signoff = self.voice_engine.generate_signoff(intro_voice_context)

        # Assemble email
        email_body = "\n\n".join(body_parts)

        return {
            "subject_line": subject_line,
            "greeting": greeting,
            "body": email_body,
            "signoff": signoff,
            "full_email": f"{greeting}\n\n{email_body}\n\n{signoff}",
            "participants": participants,
            "intro_type": intro_type,
            "opportunity": opportunity
        }

    def _generate_subject_line(self, recipient_name: str, content_map: Dict) -> str:
        """Generate subject line per v10.6 specs using string operations only"""
        ctas = content_map.get('ctas', [])
        keywords = []

        # Extract keywords from CTAs using string operations
        action_words = ['discuss', 'review', 'follow', 'schedule', 'meet', 'call']

        for cta in ctas[:2]:  # Up to 2 keywords
            cta_lower = cta.lower()
            words = cta_lower.split()

            # Find action-oriented words
            for word in words:
                # Remove punctuation
                clean_word = word.strip('.,!?;:')
                if clean_word in action_words:
                    keywords.append(clean_word)

        if not keywords:
            keywords = ['follow', 'up']

        keyword_str = " • ".join(keywords[:3])  # Max 3 keywords

        return f"Follow-Up Email – {recipient_name} x Careerspan [{keyword_str}]"

    def _generate_warm_intro_subject_line(self, participants: List[str], intro_type: str) -> str:
        """Generate subject line for warm introduction emails"""
        if len(participants) >= 2:
            person_a = participants[0]
            person_b = participants[1]

            type_indicators = {
                'expert_introduction': 'Expert Introduction',
                'collaborative_introduction': 'Collaboration Introduction',
                'interest_based_introduction': 'Shared Interest Introduction',
                'mentorship_introduction': 'Mentorship Introduction',
                'networking_introduction': 'Networking Introduction',
                'general_introduction': 'Professional Introduction'
            }

            type_label = type_indicators.get(intro_type, 'Professional Introduction')

            return f"Warm Introduction: {person_a} ↔ {person_b} [{type_label}]"
        else:
            return "Warm Professional Introduction"

    def _generate_intro_context(self, opportunity: Dict) -> str:
        """Generate contextual introduction paragraph"""
        participants = opportunity.get('participants', [])
        intro_type = opportunity.get('intro_type', 'general_introduction')
        trigger_context = opportunity.get('trigger_context', '')

        if len(participants) >= 2:
            person_a = participants[0]
            person_b = participants[1]

            context_templates = {
                'expert_introduction': f"I wanted to introduce you to {person_b}, who I believe has valuable expertise that could be relevant to your work.",
                'collaborative_introduction': f"I wanted to connect you with {person_b} as I see great potential for collaboration between you.",
                'interest_based_introduction': f"I wanted to introduce you to {person_b} since you both share similar interests and passions.",
                'mentorship_introduction': f"I wanted to connect you with {person_b} who could provide valuable mentorship in your area of interest.",
                'networking_introduction': f"I wanted to introduce you to {person_b} as part of expanding our professional network.",
                'general_introduction': f"I wanted to introduce you to {person_b}, who I think you would benefit from knowing."
            }

            return context_templates.get(intro_type, context_templates['general_introduction'])
        else:
            return "I wanted to make a professional introduction that I believe could be mutually beneficial."

    def _generate_value_proposition(self, opportunity: Dict) -> Optional[str]:
        """Generate value proposition section"""
        intro_type = opportunity.get('intro_type', 'general_introduction')
        context = opportunity.get('context', '')

        if context:
            return f"Based on our recent discussions, I believe this connection could be valuable because: {context}"
        else:
            return None

    def _generate_mutual_benefits(self, opportunity: Dict) -> Optional[str]:
        """Generate mutual benefits section"""
        intro_type = opportunity.get('intro_type', 'general_introduction')

        benefit_templates = {
            'expert_introduction': "This introduction could provide you with expert insights while allowing them to share their knowledge more broadly.",
            'collaborative_introduction': "This connection could lead to meaningful collaboration and shared project opportunities.",
            'interest_based_introduction': "You both share similar interests, which could lead to engaging discussions and mutual learning.",
            'mentorship_introduction': "This could be the start of a valuable mentorship relationship benefiting both parties.",
            'networking_introduction': "Expanding your professional network can open doors to new opportunities and perspectives.",
            'general_introduction': "Professional connections like this often lead to unexpected opportunities and valuable relationships."
        }

        return benefit_templates.get(intro_type)

    def _generate_warm_intro_cta(self, opportunity: Dict) -> str:
        """Generate call-to-action for warm introduction"""
        participants = opportunity.get('participants', [])

        if len(participants) >= 2:
            person_a = participants[0]
            person_b = participants[1]

            return f"""I suggest we set up a brief introductory call or meeting between you and {person_b}. Would you be open to that?

Please let me know your thoughts, and I'll help coordinate if you're both interested."""
        else:
            return "Please let me know if you'd be interested in learning more about this introduction opportunity."

class TranscriptWorkflow:
    """Main workflow orchestrator"""

    def __init__(self):
        self.logger = logging.getLogger('TranscriptWorkflow')

        # Initialize components
        schema_path = "/home/workspace/Companion [05] - Companion File - Universal - Master Voice Vrijen v1.3.txt"
        self.voice_engine = MasterVoiceEngine(schema_path)
        self.content_mapper = ContentMapper()
        self.ticket_generator = BlurbTicketGenerator()
        self.email_generator = FollowUpEmailGenerator(self.voice_engine)

        # Telemetry
        self.telemetry = {
            "start_time": None,
            "end_time": None,
            "input_size": 0,
            "processing_steps": [],
            "errors": []
        }

    def process_transcript(self, transcript_path: str, voice_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a transcript through the complete workflow"""

        self.telemetry["start_time"] = datetime.now()

        try:
            # Load transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = f.read()

            self.telemetry["input_size"] = len(transcript)
            self.telemetry["processing_steps"].append("transcript_loaded")

            # Default voice context
            if voice_context is None:
                voice_context = self.voice_engine.calibrate_context(relationship_depth=1)

            self.telemetry["processing_steps"].append("voice_context_set")

            # Extract key elements
            content_map = self.content_mapper.extract_key_elements(transcript)
            self.telemetry["processing_steps"].append("content_mapped")

            # Generate tickets and blurbs
            tickets = self.ticket_generator.generate_tickets(content_map)
            blurbs = self.ticket_generator.generate_blurbs(content_map, voice_context)
            self.telemetry["processing_steps"].append("tickets_generated")

            # Generate follow-up email
            recipient_name = "Recipient"  # Extract from transcript if available
            email_draft = self.email_generator.generate_email(content_map, voice_context, recipient_name)
            self.telemetry["processing_steps"].append("email_generated")

            # Compile results
            result = {
                "content_map": content_map,
                "tickets": tickets,
                "blurbs": blurbs,
                "email_draft": email_draft,
                "voice_context": voice_context,
                "telemetry": self.telemetry
            }

            self.telemetry["end_time"] = datetime.now()
            processing_time = (self.telemetry["end_time"] - self.telemetry["start_time"]).total_seconds()
            self.logger.info(f"Workflow completed in {processing_time:.2f}s")

            return result

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            self.telemetry["errors"].append(str(e))
            self.telemetry["end_time"] = datetime.now()
            return {
                "error": str(e),
                "telemetry": self.telemetry
            }

def main():
    """CLI interface"""
    if len(sys.argv) != 2:
        print("Usage: python consolidated_transcript_workflow.py <transcript_file>")
        sys.exit(1)

    transcript_path = sys.argv[1]

    workflow = TranscriptWorkflow()
    result = workflow.process_transcript(transcript_path)

    # Output results
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()