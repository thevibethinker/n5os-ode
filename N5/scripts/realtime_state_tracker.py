#!/usr/bin/env python3
"""
Real-Time State Tracker for Strategic Partner

Manages turn-by-turn state during strategic partner sessions with:
- Voice-friendly hotwords (Objective, Subject, Idea, Mark, Snapshot)
- Chronological utterance log with compression
- Running summary maintenance
- Ideas, directions, and questions tracking
- Bounded state sizes for token efficiency

Based on Real-Time Thought Partner pattern.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)


class RealTimeStateTracker:
    """
    Manages real-time state during strategic partner sessions
    
    Features:
    - Voice hotwords: Objective, Subject, Idea, Mark, Snapshot
    - Turn-by-turn chronological log
    - Automatic compression when >14 turns
    - Ideas deduplication (max 6)
    - Directions tracking (max 3)
    - Next questions queue (max 5)
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = self._init_state()
        self.turn_counter = 0
        
        logger.info(f"Real-time state tracker initialized: {session_id}")
    
    def _init_state(self) -> Dict[str, Any]:
        """Initialize empty state"""
        return {
            "session_id": self.session_id,
            "objective": None,
            "subject": {
                "type": None,  # person|concept|organization|trend|unknown
                "name": None
            },
            "chrono_log": [],  # List of {id, text, tags, timestamp}
            "archive_summary": "",  # Compressed old turns (≤80 words)
            "running_summary": "",  # Current summary (≤120 words)
            "ideas": [],  # List of {id, idea, why_now, status}
            "directions": [],  # List of {id, direction, rationale}
            "next_questions": [],  # List of {q, reason}
            "marked_turns": [],  # Turn IDs that were marked
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def parse_hotwords(self, text: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse voice hotwords from text
        
        Returns: (hotwords_dict, cleaned_text)
        
        Hotwords:
        - "Objective: <text>" or "objective: <text>"
        - "Subject: <type> <name>" or "subject: <type> <name>"
        - "Idea: <text>" or "idea: <text>"
        - "Mark" or "mark"
        - "Snapshot" or "snapshot"
        - "Clear Objective" or "clear objective"
        """
        hotwords = {
            "objective": None,
            "subject": None,
            "idea": None,
            "mark": False,
            "snapshot": False,
            "clear_objective": False
        }
        
        cleaned_lines = []
        
        for line in text.split('\n'):
            line_stripped = line.strip()
            
            # Objective
            obj_match = re.match(r'^objective:\s*(.+)$', line_stripped, re.IGNORECASE)
            if obj_match:
                hotwords["objective"] = obj_match.group(1).strip()
                continue
            
            # Subject
            subj_match = re.match(r'^subject:\s*(\w+)\s+(.+)$', line_stripped, re.IGNORECASE)
            if subj_match:
                hotwords["subject"] = {
                    "type": subj_match.group(1).lower(),
                    "name": subj_match.group(2).strip()
                }
                continue
            
            # Idea
            idea_match = re.match(r'^idea:\s*(.+)$', line_stripped, re.IGNORECASE)
            if idea_match:
                hotwords["idea"] = idea_match.group(1).strip()
                continue
            
            # Mark
            if re.match(r'^mark$', line_stripped, re.IGNORECASE):
                hotwords["mark"] = True
                continue
            
            # Snapshot
            if re.match(r'^snapshot$', line_stripped, re.IGNORECASE):
                hotwords["snapshot"] = True
                continue
            
            # Clear Objective
            if re.match(r'^clear\s+objective$', line_stripped, re.IGNORECASE):
                hotwords["clear_objective"] = True
                continue
            
            # Not a hotword, keep the line
            cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines).strip()
        
        return hotwords, cleaned_text
    
    def process_turn(self, utterance: str) -> Dict[str, Any]:
        """
        Process a turn with hotword detection and state update
        
        Steps:
        1. Parse hotwords
        2. Execute hotword commands
        3. Add utterance to chrono log
        4. Compress if needed (>14 turns)
        5. Update running summary
        6. Extract/update ideas
        7. Update directions
        8. Update next questions
        
        Returns: Update summary
        """
        # Step 1: Parse hotwords
        hotwords, cleaned_utterance = self.parse_hotwords(utterance)
        
        updates = {
            "hotwords_executed": [],
            "new_ideas": [],
            "new_directions": [],
            "new_questions": []
        }
        
        # Step 2: Execute hotwords
        if hotwords["objective"] is not None:
            self.state["objective"] = hotwords["objective"]
            updates["hotwords_executed"].append(f"Objective set: {hotwords['objective']}")
            logger.info(f"Objective set: {hotwords['objective']}")
        
        if hotwords["subject"] is not None:
            self.state["subject"] = hotwords["subject"]
            updates["hotwords_executed"].append(
                f"Subject set: {hotwords['subject']['type']} - {hotwords['subject']['name']}"
            )
            logger.info(f"Subject: {hotwords['subject']}")
        
        if hotwords["idea"]:
            idea_id = f"I{len(self.state['ideas']) + 1}"
            new_idea = {
                "id": idea_id,
                "idea": hotwords["idea"],
                "why_now": "Captured from voice",
                "status": "open",
                "turn_id": self.turn_counter + 1
            }
            self.state["ideas"].append(new_idea)
            updates["new_ideas"].append(new_idea)
            logger.info(f"Idea captured: {hotwords['idea']}")
        
        if hotwords["clear_objective"]:
            self.state["objective"] = None
            updates["hotwords_executed"].append("Objective cleared")
            logger.info("Objective cleared")
        
        # Step 3: Add to chrono log
        self.turn_counter += 1
        turn_entry = {
            "id": self.turn_counter,
            "text": cleaned_utterance,
            "tags": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if hotwords["mark"]:
            turn_entry["tags"].append("marked")
            self.state["marked_turns"].append(self.turn_counter)
            updates["hotwords_executed"].append(f"Turn #{self.turn_counter} marked")
            logger.info(f"Turn #{self.turn_counter} marked")
        
        self.state["chrono_log"].append(turn_entry)
        
        # Step 4: Compress if needed (>14 turns)
        if len(self.state["chrono_log"]) > 14:
            self._compress_chrono_log()
        
        # Step 5: Update running summary (placeholder - production would be smarter)
        self._update_running_summary()
        
        # Step 6-8: Update ideas, directions, questions (placeholder)
        # In production, would analyze cleaned_utterance for these
        
        # Update metadata
        self.state["metadata"]["last_updated"] = datetime.now().isoformat()
        
        return updates
    
    def _compress_chrono_log(self):
        """Compress old turns into archive summary"""
        # Keep last 14, move older to archive
        if len(self.state["chrono_log"]) <= 14:
            return
        
        old_turns = self.state["chrono_log"][:-14]
        
        # Simple compression: concatenate old turns (production would be smarter)
        old_text = " ".join([t["text"] for t in old_turns if t["text"]])
        
        # Update archive (keep ≤80 words)
        words = old_text.split()
        if len(words) > 80:
            compressed = " ".join(words[-80:])
            self.state["archive_summary"] = f"[...] {compressed}"
        else:
            self.state["archive_summary"] = old_text
        
        # Keep only last 14
        self.state["chrono_log"] = self.state["chrono_log"][-14:]
        
        logger.info(f"Compressed chrono log: archived {len(old_turns)} old turns")
    
    def _update_running_summary(self):
        """Update running summary (≤120 words)"""
        # Placeholder: In production, would generate smart summary
        # For now, just note that we'd generate one
        recent_turns = self.state["chrono_log"][-5:]
        recent_text = " ".join([t["text"] for t in recent_turns if t["text"]])
        
        words = recent_text.split()
        if len(words) > 120:
            self.state["running_summary"] = " ".join(words[-120:])
        else:
            self.state["running_summary"] = recent_text
    
    def deduplicate_ideas(self):
        """Deduplicate ideas by gist, keep max 6"""
        # Simple dedup: exact match (production would be smarter)
        seen = set()
        unique_ideas = []
        
        for idea in self.state["ideas"]:
            idea_text = idea["idea"].lower().strip()
            if idea_text not in seen:
                seen.add(idea_text)
                unique_ideas.append(idea)
        
        # Keep max 6, prioritize open status and recent
        unique_ideas.sort(key=lambda x: (
            x["status"] == "parked",  # Open first
            -x.get("turn_id", 0)  # Recent first
        ))
        
        self.state["ideas"] = unique_ideas[:6]
    
    def get_snapshot(self) -> str:
        """
        Get compact state snapshot
        
        Format matches Real-Time Thought Partner output
        """
        obj = self.state["objective"] or "none"
        subj = f"{self.state['subject']['type']}|{self.state['subject']['name']}" \
               if self.state['subject']['name'] else "none"
        
        # Chrono (last 10)
        chrono_lines = []
        for turn in self.state["chrono_log"][-10:]:
            tags_str = f" [{','.join(turn['tags'])}]" if turn.get('tags') else ""
            chrono_lines.append(f"- [#{turn['id']}] {turn['text']}{tags_str}")
        
        # Ideas
        ideas_lines = []
        for idea in self.state["ideas"][:5]:
            ideas_lines.append(
                f"- ({idea['id']}) {idea['idea']} — {idea['why_now']} "
                f"[status: {idea['status']}]"
            )
        
        # Directions
        directions_lines = []
        for i, direction in enumerate(self.state["directions"][:2], 1):
            directions_lines.append(
                f"- (D{i}) {direction['direction']} — {direction['rationale']}"
            )
        
        # Questions
        questions_lines = []
        for i, q in enumerate(self.state["next_questions"][:3], 1):
            questions_lines.append(f"{i}) {q['q']} — {q['reason']}")
        
        snapshot = f"""STATE-BEGIN
Objective: {obj}
Subject: {subj}
Summary: {self.state['running_summary'] or '[In progress]'}

Chrono (last 10):
{chr(10).join(chrono_lines) if chrono_lines else '- [No turns yet]'}

Ideas (new/updated):
{chr(10).join(ideas_lines) if ideas_lines else '- [No ideas yet]'}

Directions:
{chr(10).join(directions_lines) if directions_lines else '- [No directions yet]'}

Next Qs:
{chr(10).join(questions_lines) if questions_lines else '- [No questions yet]'}
STATE-END"""
        
        return snapshot
    
    def save_state(self, output_path: Path):
        """Save state to JSON file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            content = json.dumps(self.state, indent=2, ensure_ascii=False)
            output_path.write_text(content, encoding='utf-8')
            logger.info(f"✓ Real-time state saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def save_chrono_log(self, output_path: Path):
        """Save chronological log to JSONL file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                for turn in self.state["chrono_log"]:
                    f.write(json.dumps(turn) + '\n')
            logger.info(f"✓ Chrono log saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save chrono log: {e}")
    
    def get_ideas_for_synthesis(self) -> List[Dict]:
        """Get ideas in format for reflection synthesizer"""
        return [
            {
                "idea": idea["idea"],
                "context": idea["why_now"],
                "status": idea["status"],
                "captured_turn": idea.get("turn_id")
            }
            for idea in self.state["ideas"]
            if idea["status"] == "open"
        ]
    
    def get_marked_turns(self) -> List[Dict]:
        """Get turns that were marked"""
        return [
            turn for turn in self.state["chrono_log"]
            if "marked" in turn.get("tags", [])
        ]


def main():
    """CLI for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Real-Time State Tracker (testing)"
    )
    parser.add_argument('--session-id', default="test-session",
                       help='Session ID')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode')
    
    args = parser.parse_args()
    
    tracker = RealTimeStateTracker(args.session_id)
    
    if args.interactive:
        print("Real-Time State Tracker - Interactive Test")
        print("=" * 70)
        print("Enter utterances (can include hotwords)")
        print("Commands: 'snapshot', 'quit'")
        print("=" * 70)
        
        while True:
            try:
                text = input("\n> ")
                
                if text.lower() == 'quit':
                    break
                
                if text.lower() == 'snapshot':
                    print("\n" + tracker.get_snapshot())
                    continue
                
                updates = tracker.process_turn(text)
                
                if updates["hotwords_executed"]:
                    print(f"✓ {', '.join(updates['hotwords_executed'])}")
                
                if updates["new_ideas"]:
                    for idea in updates["new_ideas"]:
                        print(f"✓ Idea captured: ({idea['id']}) {idea['idea']}")
                
                print(f"✓ Turn #{tracker.turn_counter} processed")
                
            except KeyboardInterrupt:
                break
        
        print("\n\nFinal Snapshot:")
        print(tracker.get_snapshot())
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
