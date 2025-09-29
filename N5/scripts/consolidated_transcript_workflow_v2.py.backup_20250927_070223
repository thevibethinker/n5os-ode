#!/usr/bin/env python3
"""
Consolidated Transcript Ingestion Workflow v2.0
Enhanced version addressing cross-contamination, commitment tracking, and output format issues.

Key improvements:
- Enhanced commitment extraction with speaker attribution (my/our/others)
- Fixed content mapping to prevent cross-contamination
- Replaced full email generation with content map + recap chunk
- Improved extraction accuracy to prevent hallucinations
- Speaker-aware parsing for accurate attribution

Author: Zo Computer
Version: 2.0.0
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
        logging.FileHandler(f'{_logs_dir}/transcript_workflow_v2.log', mode='a')
    ]
)
logger = logging.getLogger('consolidated_transcript_workflow_v2')

class SpeakerAwareParser:
    """Parse transcript with speaker attribution to prevent cross-contamination"""
    
    def __init__(self):
        self.logger = logging.getLogger('SpeakerAwareParser')
    
    def parse_transcript(self, transcript: str) -> List[Dict[str, Any]]:
        """Parse transcript into speaker-attributed statements"""
        lines = transcript.split('\n')
        statements = []
        current_speaker = None
        current_content = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a speaker label (ends with colon, looks like name)
            if ':' in line and line.count(':') == 1 and line.endswith(':'):
                potential_speaker = line[:-1].strip()
                
                # Save previous speaker's content
                if current_speaker and current_content:
                    content = ' '.join(current_content).strip()
                    if content:
                        statements.append({
                            "speaker": current_speaker,
                            "content": content,
                            "line_range": (line_num - len(current_content), line_num - 1)
                        })
                
                # Start new speaker if it looks like a name
                if self._is_likely_speaker_name(potential_speaker):
                    current_speaker = potential_speaker
                    current_content = []
                    continue
            
            # Check for inline speaker patterns like "Name: content"
            if ':' in line and not line.endswith(':'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    potential_speaker = parts[0].strip()
                    content_part = parts[1].strip()
                    
                    if self._is_likely_speaker_name(potential_speaker) and content_part:
                        # Save previous speaker's content first
                        if current_speaker and current_content:
                            content = ' '.join(current_content).strip()
                            if content:
                                statements.append({
                                    "speaker": current_speaker,
                                    "content": content,
                                    "line_range": (line_num - len(current_content), line_num - 1)
                                })
                        
                        # Add this statement
                        statements.append({
                            "speaker": potential_speaker,
                            "content": content_part,
                            "line_range": (line_num, line_num)
                        })
                        
                        # Reset for next speaker
                        current_speaker = None
                        current_content = []
                        continue
            
            # Add content to current speaker
            if current_speaker:
                current_content.append(line)
            else:
                # Handle lines before any speaker (metadata, headers, etc.)
                if any(keyword in line.lower() for keyword in ['date:', 'participants:', 'meeting', 'transcript']):
                    statements.append({
                        "speaker": "METADATA",
                        "content": line,
                        "line_range": (line_num, line_num)
                    })
        
        # Handle final speaker
        if current_speaker and current_content:
            content = ' '.join(current_content).strip()
            if content:
                statements.append({
                    "speaker": current_speaker,
                    "content": content,
                    "line_range": (len(lines) - len(current_content), len(lines))
                })
        
        return statements
    
    def _is_likely_speaker_name(self, text: str) -> bool:
        """Check if text looks like a speaker name"""
        if not text or len(text) < 2:
            return False
        
        # Must start with capital letter
        if not text[0].isupper():
            return False
        
        # Reasonable length for names (not too short or long)
        if len(text) < 2 or len(text) > 50:
            return False
        
        # Should not be common non-name words
        non_names = {
            'meeting', 'discussion', 'project', 'company', 'team', 'group',
            'session', 'call', 'email', 'transcript', 'date', 'time', 'agenda',
            'notes', 'summary', 'action', 'items', 'follow', 'up'
        }
        
        if text.lower() in non_names:
            return False
        
        # Should contain vowels (real names have vowels)
        if not any(char in text.lower() for char in 'aeiou'):
            return False
        
        # Shouldn't be all numbers or special characters
        if not any(char.isalpha() for char in text):
            return False
        
        # Must look like a name pattern (allow full names like "Vrijen Attawar")
        words = text.split()
        if len(words) > 3:  # Too many words for a name
            return False
            
        # Each word should start with capital
        for word in words:
            if not word[0].isupper():
                return False
        
        return True

class EnhancedContentMapper:
    """Enhanced content mapping with commitment tracking and cross-contamination prevention"""
    
    def __init__(self, user_name: str = "Vrijen"):
        self.logger = logging.getLogger('EnhancedContentMapper')
        self.user_name = user_name.lower()
        # Also handle full names by extracting first name
        self.user_first_name = user_name.split()[0].lower()
        self.parser = SpeakerAwareParser()
    
    def extract_content_map(self, transcript: str) -> Dict[str, Any]:
        """Extract comprehensive content map from transcript"""
        
        # Parse transcript with speaker attribution
        statements = self.parser.parse_transcript(transcript)
        
        # Extract meeting metadata
        meeting_info = self._extract_meeting_info(statements)
        
        # Extract participants
        participants = self._extract_participants(statements)
        
        # Extract commitments with speaker attribution
        commitments = self._extract_commitments(statements)
        
        # Extract decisions and agreements
        decisions = self._extract_decisions(statements)
        
        # Extract next steps and CTAs
        next_steps = self._extract_next_steps(statements)
        
        # Extract deliverables
        deliverables = self._extract_deliverables(statements)
        
        # Extract resonance and key insights
        resonance = self._extract_resonance(statements)
        
        # Extract context of the deal/agreement
        context = self._extract_deal_context(statements)
        
        return {
            "meeting_info": meeting_info,
            "participants": participants,
            "my_commitments": commitments.get("my_commitments", []),
            "our_commitments": commitments.get("our_commitments", []),
            "others_commitments": commitments.get("others_commitments", []),
            "decisions": decisions,
            "next_steps": next_steps,
            "deliverables": deliverables,
            "resonance": resonance,
            "deal_context": context,
            "raw_statements": len(statements)
        }
    
    def _extract_meeting_info(self, statements: List[Dict]) -> Dict[str, Any]:
        """Extract meeting metadata"""
        info = {
            "date": None,
            "title": None,
            "duration": None
        }
        
        # Look for date information in metadata lines
        for stmt in statements:
            if stmt["speaker"] == "METADATA":
                content_lower = stmt["content"].lower()
                
                # Extract date
                if "date:" in content_lower:
                    date_part = stmt["content"].split(":", 1)[1].strip()
                    info["date"] = date_part
                
                # Extract title/subject
                if any(keyword in content_lower for keyword in ["meeting", "discussion", "call", "transcript"]):
                    if ":" in stmt["content"]:
                        info["title"] = stmt["content"].split(":", 1)[0].strip()
                    else:
                        info["title"] = stmt["content"]
        
        return info
    
    def _extract_participants(self, statements: List[Dict]) -> List[str]:
        """Extract participant list"""
        participants = set()
        
        # Get speakers from parsed statements
        for stmt in statements:
            if stmt["speaker"] != "METADATA":
                participants.add(stmt["speaker"])
        
        # Also check for explicit participant lists in metadata
        for stmt in statements:
            if stmt["speaker"] == "METADATA":
                content_lower = stmt["content"].lower()
                if "participants:" in content_lower:
                    parts_text = stmt["content"].split(":", 1)[1].strip()
                    # Split by common delimiters
                    names = re.split(r'[,&]|\s+and\s+', parts_text)
                    for name in names:
                        name = name.strip()
                        if name:
                            participants.add(name)
        
        return sorted(list(participants))
    
    def _extract_commitments(self, statements: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract commitments with speaker attribution"""
        
        commitment_indicators = [
            "i will", "i'll", "i commit to", "i promise to", "i agree to",
            "we will", "we'll", "we commit to", "we agree to", "we promise to",
            "you will", "you'll", "you should", "you could", "you can",
            "they will", "they'll", "they should", "they agreed to",
            "i'm going to", "we're going to", "i plan to", "we plan to",
            "on my end", "i'll take care of", "i'll handle", "i'll deliver",
            "we decided", "i decided", "you decided", "they decided"
        ]
        
        my_commitments = []
        our_commitments = []
        others_commitments = []
        
        for stmt in statements:
            speaker = stmt["speaker"]
            content = stmt["content"].lower()
            original_content = stmt["content"]
            
            # Skip metadata
            if speaker == "METADATA":
                continue
            
            # Find commitment statements
            for indicator in commitment_indicators:
                if indicator in content:
                    # Extract the commitment context
                    commitment_text = self._extract_commitment_context(original_content, indicator)
                    
                    if commitment_text and len(commitment_text) > 10:  # Meaningful commitment
                        # Check if this is the user speaking (match both full name and first name)
                        is_user_speaker = (speaker.lower() == self.user_name or 
                                         speaker.lower() == self.user_first_name or
                                         self.user_first_name in speaker.lower())
                        
                        commitment_obj = {
                            "speaker": speaker,
                            "commitment": commitment_text,
                            "indicator": indicator,
                            "is_user": is_user_speaker
                        }
                        
                        # Categorize based on pronouns and speaker
                        if is_user_speaker and any(pronoun in indicator for pronoun in ["i will", "i'll", "i commit", "i agree", "on my end", "i plan"]):
                            my_commitments.append(commitment_obj)
                        elif any(pronoun in indicator for pronoun in ["we will", "we'll", "we commit", "we agree", "we plan"]):
                            our_commitments.append(commitment_obj)
                        else:
                            others_commitments.append(commitment_obj)
        
        return {
            "my_commitments": my_commitments,
            "our_commitments": our_commitments,
            "others_commitments": others_commitments
        }
    
    def _extract_commitment_context(self, content: str, indicator: str) -> str:
        """Extract meaningful context around commitment indicators"""
        content_lower = content.lower()
        indicator_pos = content_lower.find(indicator)
        
        if indicator_pos == -1:
            return ""
        
        # Get sentence containing the commitment
        sentences = content.split('.')
        for sentence in sentences:
            if indicator in sentence.lower():
                return sentence.strip()
        
        # Fallback: get context around the indicator
        start = max(0, indicator_pos - 20)
        end = min(len(content), indicator_pos + len(indicator) + 100)
        context = content[start:end].strip()
        
        return context
    
    def _extract_decisions(self, statements: List[Dict]) -> List[Dict]:
        """Extract decisions and agreements"""
        decision_indicators = [
            "we decided", "we agreed", "we determined", "we concluded",
            "it was decided", "we settled on", "the decision was",
            "we chose", "we selected", "we picked", "consensus was",
            "agreed upon", "decided on"
        ]
        
        decisions = []
        
        for stmt in statements:
            if stmt["speaker"] == "METADATA":
                continue
                
            content_lower = stmt["content"].lower()
            original_content = stmt["content"]
            
            for indicator in decision_indicators:
                if indicator in content_lower:
                    decision_text = self._extract_decision_context(original_content, indicator)
                    if decision_text and len(decision_text) > 15:
                        decisions.append({
                            "speaker": stmt["speaker"],
                            "decision": decision_text,
                            "indicator": indicator
                        })
        
        return decisions
    
    def _extract_decision_context(self, content: str, indicator: str) -> str:
        """Extract decision context"""
        sentences = content.split('.')
        for sentence in sentences:
            if indicator in sentence.lower():
                return sentence.strip()
        return ""
    
    def _extract_next_steps(self, statements: List[Dict]) -> List[Dict]:
        """Extract next steps and action items"""
        next_step_indicators = [
            "next steps", "action items", "follow up", "next meeting",
            "schedule", "coordinate", "reach out", "follow-up",
            "need to", "will need to", "next time",
            "moving forward", "going forward"
        ]
        
        next_steps = []
        seen_steps = set()  # Prevent duplicates
        
        for stmt in statements:
            if stmt["speaker"] == "METADATA":
                continue
                
            content_lower = stmt["content"].lower()
            original_content = stmt["content"]
            
            for indicator in next_step_indicators:
                if indicator in content_lower:
                    step_text = self._extract_step_context(original_content, indicator)
                    if step_text and len(step_text) > 15 and step_text not in seen_steps:
                        seen_steps.add(step_text)
                        next_steps.append({
                            "speaker": stmt["speaker"],
                            "step": step_text,
                            "indicator": indicator
                        })
        
        return next_steps
    
    def _extract_step_context(self, content: str, indicator: str) -> str:
        """Extract next step context"""
        sentences = content.split('.')
        for sentence in sentences:
            if indicator in sentence.lower():
                return sentence.strip()
        return ""
    
    def _extract_deliverables(self, statements: List[Dict]) -> List[Dict]:
        """Extract specific deliverables mentioned"""
        deliverable_indicators = [
            "deliver", "provide", "send", "share", "create", "build",
            "develop", "produce", "generate", "prepare", "draft",
            "document", "report", "analysis", "proposal", "summary"
        ]
        
        deliverables = []
        
        for stmt in statements:
            if stmt["speaker"] == "METADATA":
                continue
                
            content_lower = stmt["content"].lower()
            original_content = stmt["content"]
            
            for indicator in deliverable_indicators:
                if indicator in content_lower:
                    deliverable_text = self._extract_deliverable_context(original_content, indicator)
                    if deliverable_text and len(deliverable_text) > 10:
                        deliverables.append({
                            "speaker": stmt["speaker"],
                            "deliverable": deliverable_text,
                            "indicator": indicator
                        })
        
        return deliverables
    
    def _extract_deliverable_context(self, content: str, indicator: str) -> str:
        """Extract deliverable context"""
        sentences = content.split('.')
        for sentence in sentences:
            if indicator in sentence.lower():
                return sentence.strip()
        return ""
    
    def _extract_resonance(self, statements: List[Dict]) -> List[Dict]:
        """Extract resonant details and emotional content"""
        resonance_indicators = [
            "excited", "passionate", "interesting", "fascinating", "amazing",
            "love", "perfect", "great", "excellent", "fantastic", "wonderful",
            "adventure", "opportunity", "potential", "impact", "unfair advantage",
            "thrilled", "enthusiastic", "inspiring", "valuable", "important"
        ]
        
        resonance_items = []
        
        for stmt in statements:
            if stmt["speaker"] == "METADATA":
                continue
                
            content_lower = stmt["content"].lower()
            original_content = stmt["content"]
            
            for indicator in resonance_indicators:
                if indicator in content_lower:
                    resonance_text = self._extract_resonance_context(original_content, indicator)
                    if resonance_text and len(resonance_text) > 15:
                        resonance_items.append({
                            "speaker": stmt["speaker"],
                            "resonance": resonance_text,
                            "indicator": indicator
                        })
        
        return resonance_items
    
    def _extract_resonance_context(self, content: str, indicator: str) -> str:
        """Extract resonance context"""
        sentences = content.split('.')
        for sentence in sentences:
            if indicator in sentence.lower():
                return sentence.strip()
        return ""
    
    def _extract_deal_context(self, statements: List[Dict]) -> Dict[str, Any]:
        """Extract the context of the deal/agreement"""
        context = {
            "project_name": None,
            "main_topic": None,
            "key_decisions": [],
            "scope": None
        }
        
        # Look for project/topic indicators
        project_indicators = ["project", "initiative", "program", "effort", "work"]
        topic_indicators = ["discuss", "exploring", "focusing on", "about", "regarding"]
        
        for stmt in statements:
            content_lower = stmt["content"].lower()
            original_content = stmt["content"]
            
            # Extract project names
            for indicator in project_indicators:
                if indicator in content_lower:
                    # Look for specific project names after the indicator
                    words = original_content.split()
                    for i, word in enumerate(words):
                        if indicator in word.lower() and i < len(words) - 1:
                            # Get next few words as potential project name
                            project_candidate = ' '.join(words[i:i+4])
                            if not context["project_name"]:
                                context["project_name"] = project_candidate
            
            # Extract main topics
            if not context["main_topic"] and any(indicator in content_lower for indicator in topic_indicators):
                context["main_topic"] = original_content[:100] + "..." if len(original_content) > 100 else original_content
        
        return context

class EmailRecapGenerator:
    """Generate email recap chunks instead of full emails"""
    
    def __init__(self):
        self.logger = logging.getLogger('EmailRecapGenerator')
    
    def generate_recap_chunk(self, content_map: Dict[str, Any]) -> Dict[str, str]:
        """Generate a concise email recap chunk for copy-paste"""
        
        recap_parts = []
        
        # Meeting summary
        meeting_info = content_map.get("meeting_info", {})
        if meeting_info.get("date"):
            recap_parts.append(f"Following up on our meeting on {meeting_info['date']}.")
        else:
            recap_parts.append("Following up on our recent meeting.")
        
        # Key decisions
        decisions = content_map.get("decisions", [])
        if decisions:
            recap_parts.append("\nKey decisions made:")
            for decision in decisions[:3]:  # Top 3 decisions
                recap_parts.append(f"• {decision['decision']}")
        
        # What I committed to
        my_commitments = content_map.get("my_commitments", [])
        if my_commitments:
            recap_parts.append("\nWhat I committed to:")
            for commitment in my_commitments:
                recap_parts.append(f"• {commitment['commitment']}")
        
        # What you/others committed to
        others_commitments = content_map.get("others_commitments", [])
        if others_commitments:
            recap_parts.append("\nWhat you committed to:")
            for commitment in others_commitments:
                recap_parts.append(f"• {commitment['commitment']}")
        
        # Next steps
        next_steps = content_map.get("next_steps", [])
        if next_steps:
            recap_parts.append("\nNext steps:")
            for step in next_steps[:3]:  # Top 3 next steps
                recap_parts.append(f"• {step['step']}")
        
        # Timeline mention
        recap_parts.append("\nI'll follow up as we progress on these items.")
        
        return {
            "email_recap_chunk": "\n".join(recap_parts),
            "follow_up_trigger": "Schedule follow-up meeting based on commitment timelines"
        }

class TodoListExtractor:
    """Extract user commitments into to-do list format"""
    
    def __init__(self):
        self.logger = logging.getLogger('TodoListExtractor')
    
    def extract_user_todos(self, content_map: Dict[str, Any], user_name: str = "Vrijen") -> List[Dict[str, Any]]:
        """Extract user commitments as actionable to-do items"""
        
        todos = []
        seen_tasks = set()  # Prevent duplicates
        
        # Process my_commitments (these are the most important)
        my_commitments = content_map.get("my_commitments", [])
        for i, commitment in enumerate(my_commitments):
            task_text = commitment["commitment"].strip()
            
            # Skip duplicates
            if task_text in seen_tasks:
                continue
            seen_tasks.add(task_text)
            
            # Only add meaningful commitments (not meta statements)
            if len(task_text) > 20 and not task_text.startswith(("Now, let me", "So to", "Let me")):
                todo_item = {
                    "id": f"commitment_{len(todos)+1}",
                    "task": task_text,
                    "type": "commitment",
                    "priority": "high",
                    "status": "pending",
                    "source": "meeting_commitment",
                    "speaker": commitment["speaker"]
                }
                todos.append(todo_item)
        
        return todos

class TranscriptWorkflowV2:
    """Enhanced workflow orchestrator v2.0"""
    
    def __init__(self, user_name: str = "Vrijen"):
        self.logger = logging.getLogger('TranscriptWorkflowV2')
        self.user_name = user_name
        
        # Initialize components
        self.content_mapper = EnhancedContentMapper(user_name)
        self.recap_generator = EmailRecapGenerator()
        self.todo_extractor = TodoListExtractor()
        
        # Telemetry
        self.telemetry = {
            "start_time": None,
            "end_time": None,
            "input_size": 0,
            "processing_steps": [],
            "errors": []
        }
    
    def process_transcript(self, transcript_path: str) -> Dict[str, Any]:
        """Process transcript through enhanced workflow"""
        
        self.telemetry["start_time"] = datetime.now()
        
        try:
            # Load transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = f.read()
            
            self.telemetry["input_size"] = len(transcript)
            self.telemetry["processing_steps"].append("transcript_loaded")
            
            # Extract comprehensive content map
            content_map = self.content_mapper.extract_content_map(transcript)
            self.telemetry["processing_steps"].append("content_mapped")
            
            # Generate email recap chunk (instead of full email)
            email_recap = self.recap_generator.generate_recap_chunk(content_map)
            self.telemetry["processing_steps"].append("recap_generated")
            
            # Extract user to-do items
            user_todos = self.todo_extractor.extract_user_todos(content_map, self.user_name)
            self.telemetry["processing_steps"].append("todos_extracted")
            
            # Compile results
            result = {
                "content_map": content_map,
                "email_recap_chunk": email_recap,
                "user_todos": user_todos,
                "telemetry": self.telemetry
            }
            
            self.telemetry["end_time"] = datetime.now()
            processing_time = (self.telemetry["end_time"] - self.telemetry["start_time"]).total_seconds()
            self.logger.info(f"Enhanced workflow completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced workflow failed: {e}")
            self.telemetry["errors"].append(str(e))
            self.telemetry["end_time"] = datetime.now()
            return {
                "error": str(e),
                "telemetry": self.telemetry
            }

def main():
    """CLI interface for enhanced workflow"""
    if len(sys.argv) < 2:
        print("Usage: python consolidated_transcript_workflow_v2.py <transcript_file> [user_name]")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    user_name = sys.argv[2] if len(sys.argv) > 2 else "Vrijen"
    
    workflow = TranscriptWorkflowV2(user_name)
    result = workflow.process_transcript(transcript_path)
    
    # Output results
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()