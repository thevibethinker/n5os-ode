#!/usr/bin/env python3
"""
Strategic Partner Session Manager

Handles audio/transcript processing, context loading, session state management,
and output generation for the Strategic Partner cognitive engine.

This is the PRIMARY INTERFACE for V's strategic thinking within N5 OS.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
SESSIONS_DIR = WORKSPACE / "N5/sessions/strategic-partner"
PENDING_UPDATES_DIR = SESSIONS_DIR / "pending-updates"
TOPICS_FILE = SESSIONS_DIR / "topics-to-revisit.jsonl"
INTELLIGENCE_FILE = WORKSPACE / "N5/intelligence/personal-understanding.json"
KNOWLEDGE_DIR = WORKSPACE / "Knowledge"

# Create directories
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
PENDING_UPDATES_DIR.mkdir(parents=True, exist_ok=True)
INTELLIGENCE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Careerspan priority modes
CAREERSPAN_DEFAULT_MODE = "aggressive_challenge"
CAREERSPAN_DEFAULT_DIALS = {
    "challenge": 7,
    "novel": 5,
    "structure": 4
}

# Mode descriptions for auto-suggestion
MODE_DESCRIPTIONS = {
    "aggressive": "Aggressive flaw-finding and stress testing",
    "challenge": "Challenge assumptions and identify risks",
    "synthesis": "Structure scattered thoughts into coherent strategy",
    "exploration": "Generative ideation and possibility expansion",
    "socratic": "Clarifying questions and assumption surfacing",
    "war_room": "Crisis management and rapid triage",
    "chess": "Multi-move strategy and scenario planning",
    "venture": "Investor perspective and risk/return analysis",
    "customer": "Careerspan customer lens (ICP problems)",
    "hater": "Most hostile critic perspective"
}


class StrategicPartnerSession:
    """Manages a single strategic partner session"""
    
    def __init__(self, audio_file: Optional[Path] = None, 
                 transcript_file: Optional[Path] = None,
                 mode: Optional[str] = None,
                 dials: Optional[Dict[str, int]] = None):
        
        self.audio_file = audio_file
        self.transcript_file = transcript_file
        self.mode = mode or CAREERSPAN_DEFAULT_MODE
        self.dials = dials or CAREERSPAN_DEFAULT_DIALS.copy()
        
        self.session_id = self._generate_session_id()
        self.transcript_content = None
        self.detected_topic = None
        self.loaded_context = {}
        self.session_notes = []
        
        logger.info(f"Initialized Strategic Partner session: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Count existing sessions today
        existing = list(SESSIONS_DIR.glob(f"{today}-session-*.md"))
        session_num = len(existing) + 1
        
        return f"{today}-session-{session_num}"
    
    def process_audio(self) -> bool:
        """Process audio file and generate transcript"""
        if not self.audio_file:
            return False
        
        logger.info(f"Processing audio file: {self.audio_file}")
        
        # Check file exists
        if not self.audio_file.exists():
            logger.error(f"Audio file not found: {self.audio_file}")
            return False
        
        # In real implementation, this would call Zo's transcription service
        # For now, we'll simulate/note that transcription would happen
        logger.info("Note: Audio transcription would happen here via Zo service")
        logger.info("For MVP, please provide transcript file or use --interactive mode")
        
        # Placeholder for transcription result
        self.transcript_content = "[Audio transcription would appear here]"
        
        return True
    
    def load_transcript(self) -> bool:
        """Load transcript from file"""
        if not self.transcript_file:
            return False
        
        logger.info(f"Loading transcript: {self.transcript_file}")
        
        try:
            self.transcript_content = self.transcript_file.read_text(encoding='utf-8')
            logger.info(f"Loaded transcript: {len(self.transcript_content)} characters")
            return True
        except Exception as e:
            logger.error(f"Failed to load transcript: {e}")
            return False
    
    def detect_topic(self) -> Optional[str]:
        """Detect strategic topic from transcript"""
        if not self.transcript_content:
            return None
        
        # Simple keyword-based topic detection
        # In production, this could be more sophisticated
        content_lower = self.transcript_content.lower()
        
        topics = {
            "pricing": ["pricing", "price", "cost", "revenue", "pricing strategy"],
            "product": ["product", "feature", "roadmap", "development", "user experience"],
            "partnership": ["partnership", "partner", "collaboration", "alliance"],
            "fundraising": ["fundraising", "investor", "funding", "raise", "capital"],
            "gtm": ["go-to-market", "gtm", "sales", "marketing", "customer acquisition"],
            "hiring": ["hiring", "recruitment", "team", "talent"],
            "strategy": ["strategy", "strategic", "vision", "direction"]
        }
        
        for topic, keywords in topics.items():
            if any(kw in content_lower for kw in keywords):
                self.detected_topic = topic
                logger.info(f"Detected topic: {topic}")
                return topic
        
        self.detected_topic = "general_strategy"
        return "general_strategy"
    
    def load_context(self) -> Dict[str, Any]:
        """Load relevant context from N5 knowledge base (read-only)"""
        logger.info("Loading N5 context...")
        
        context = {
            "gtm_hypotheses": [],
            "product_hypotheses": [],
            "recent_decisions": [],
            "relevant_facts": [],
            "personal_intelligence": {}
        }
        
        # Load GTM hypotheses if they exist
        gtm_file = KNOWLEDGE_DIR / "hypotheses/gtm_hypotheses.md"
        if gtm_file.exists():
            try:
                content = gtm_file.read_text(encoding='utf-8')
                # Simple extraction - in production would be more sophisticated
                context["gtm_hypotheses"] = [
                    "GTM hypotheses loaded (read-only)"
                ]
                logger.info("✓ Loaded GTM hypotheses")
            except Exception as e:
                logger.warning(f"Could not load GTM hypotheses: {e}")
        
        # Load product hypotheses if they exist
        product_file = KNOWLEDGE_DIR / "hypotheses/product_hypotheses.md"
        if product_file.exists():
            try:
                content = product_file.read_text(encoding='utf-8')
                context["product_hypotheses"] = [
                    "Product hypotheses loaded (read-only)"
                ]
                logger.info("✓ Loaded product hypotheses")
            except Exception as e:
                logger.warning(f"Could not load product hypotheses: {e}")
        
        # Load my personal intelligence
        if INTELLIGENCE_FILE.exists():
            try:
                intelligence = json.loads(INTELLIGENCE_FILE.read_text(encoding='utf-8'))
                context["personal_intelligence"] = intelligence
                logger.info("✓ Loaded personal intelligence layer")
            except Exception as e:
                logger.warning(f"Could not load personal intelligence: {e}")
        
        self.loaded_context = context
        return context
    
    def suggest_mode(self) -> str:
        """Suggest optimal mode based on topic and context"""
        if not self.detected_topic:
            return CAREERSPAN_DEFAULT_MODE
        
        # Mode suggestions based on topic
        suggestions = {
            "pricing": ["venture", "aggressive", "customer"],
            "product": ["customer", "design_thinking", "aggressive"],
            "partnership": ["chess", "war_room", "venture"],
            "fundraising": ["venture", "aggressive", "hater"],
            "gtm": ["mckinsey", "aggressive", "venture"],
            "hiring": ["socratic", "aggressive"],
            "strategy": ["chess", "mckinsey", "philosophical"]
        }
        
        topic_suggestions = suggestions.get(self.detected_topic, [CAREERSPAN_DEFAULT_MODE])
        suggested = topic_suggestions[0]
        
        logger.info(f"Suggested mode: {suggested} (based on topic: {self.detected_topic})")
        logger.info(f"Alternatives: {', '.join(topic_suggestions[1:])}")
        
        return suggested
    
    def begin_dialogue(self) -> Dict[str, Any]:
        """Begin strategic dialogue (would be interactive in real implementation)"""
        logger.info("=" * 70)
        logger.info("STRATEGIC PARTNER SESSION")
        logger.info("=" * 70)
        
        print(f"\nSession ID: {self.session_id}")
        print(f"Mode: {self.mode}")
        print(f"Dials: challenge={self.dials['challenge']}, novel={self.dials['novel']}, structure={self.dials['structure']}")
        
        if self.detected_topic:
            print(f"Topic: {self.detected_topic}")
        
        print("\nContext loaded:")
        for key, value in self.loaded_context.items():
            if value:
                print(f"  ✓ {key}")
        
        print("\n" + "=" * 70)
        print("DIALOGUE PHASE")
        print("=" * 70)
        print("\nIn production, this is where the interactive strategic dialogue occurs.")
        print("The AI would engage with you using the selected mode and dials,")
        print("applying active nuances (blind_spot_scanner, contradiction_detector, etc.)")
        print("and tracking session quality metrics.")
        print("\n[MVP: Dialog happens in main Zo conversation interface]")
        
        # Simulate session metadata
        session_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "dials": self.dials,
            "topic": self.detected_topic,
            "context_loaded": list(self.loaded_context.keys()),
            "insights_generated": 0,  # Would be tracked during dialogue
            "assumptions_surfaced": 0,
            "blindspots_identified": 0,
            "topics_for_weekly_review": []
        }
        
        return session_data
    
    def generate_synthesis(self, session_data: Dict[str, Any]) -> Path:
        """Generate session synthesis document"""
        synthesis_file = SESSIONS_DIR / f"{self.session_id}.md"
        
        content = f"""# Strategic Partner Session: {self.session_id}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}  
**Mode:** {self.mode}  
**Topic:** {self.detected_topic or 'General strategy'}

---

## Session Configuration

**Dials:**
- Challenge: {self.dials['challenge']}/10
- Novel Perspective: {self.dials['novel']}/10
- Structure: {self.dials['structure']}/10

**Context Loaded:**
{chr(10).join(f"- {k}" for k in self.loaded_context.keys() if self.loaded_context[k])}

---

## Key Insights

[In production: Insights generated during dialogue would be captured here]

1. [Insight 1]
2. [Insight 2]
3. [Insight 3]

---

## Assumptions Challenged

[In production: Assumptions surfaced and interrogated during dialogue]

1. [Assumption 1]
2. [Assumption 2]

---

## Blind Spots Identified

[In production: Unconsidered perspectives and angles]

1. [Blind spot 1]
2. [Blind spot 2]

---

## Unresolved Tensions (for Weekly Review)

[In production: Contradictions and questions needing more time]

1. [Unresolved item 1]
2. [Unresolved item 2]

---

## Recommended Next Actions

[In production: Concrete next steps from the dialogue]

1. [Action 1]
2. [Action 2]
3. [Action 3]

---

## Session Quality Metrics

- Insights generated: {session_data.get('insights_generated', 0)}
- Assumptions surfaced: {session_data.get('assumptions_surfaced', 0)}
- Blind spots identified: {session_data.get('blindspots_identified', 0)}
- Perspective shifts: {session_data.get('perspective_shifts', 0)}

---

## Notes

This session used the **{self.mode}** mode with Careerspan-optimized challenge/synthesis focus.

Pending knowledge updates staged in: `pending-updates/{self.session_id}.json`

Use `review-pending-updates` to review and approve changes to knowledge base.

---

*Session synthesis auto-generated by Strategic Partner cognitive engine*
"""
        
        synthesis_file.write_text(content, encoding='utf-8')
        logger.info(f"Session synthesis saved: {synthesis_file}")
        
        return synthesis_file
    
    def generate_pending_updates(self) -> Path:
        """Generate pending knowledge updates (staged for review)"""
        pending_file = PENDING_UPDATES_DIR / f"{self.session_id}.json"
        
        # In production, this would contain actual updates from the dialogue
        pending_updates = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "topic": self.detected_topic,
            "updates": [
                {
                    "type": "hypothesis_update",
                    "target": "gtm_hypotheses.md",
                    "field": "confidence",
                    "current_value": "medium",
                    "proposed_value": "high",
                    "reason": "Validated through strategic dialogue",
                    "requires_approval": True
                },
                {
                    "type": "new_fact",
                    "category": "strategic_decision",
                    "content": "[Decision made during session]",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "requires_approval": True
                }
            ],
            "status": "pending_review",
            "created_by": "strategic-partner",
            "auto_apply": False  # NEVER auto-apply
        }
        
        pending_file.write_text(json.dumps(pending_updates, indent=2), encoding='utf-8')
        logger.info(f"Pending updates staged: {pending_file}")
        logger.info("⚠️  Pending updates require human review - use `review-pending-updates`")
        
        return pending_file
    
    def update_topics_to_revisit(self, topics: List[Dict[str, Any]]):
        """Add unresolved topics to weekly review list"""
        if not topics:
            return
        
        # Append to JSONL file
        with open(TOPICS_FILE, 'a', encoding='utf-8') as f:
            for topic in topics:
                topic_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "session_id": self.session_id,
                    "topic": topic.get("topic", "Unnamed topic"),
                    "reason": topic.get("reason", "Unresolved during session"),
                    "priority": topic.get("priority", "medium"),
                    "status": "open"
                }
                f.write(json.dumps(topic_entry) + '\n')
        
        logger.info(f"Added {len(topics)} topics to weekly review list")
    
    def run(self) -> Dict[str, Any]:
        """Execute complete session workflow"""
        logger.info("Starting Strategic Partner session...")
        
        # Step 1: Get transcript
        if self.audio_file:
            if not self.process_audio():
                logger.error("Audio processing failed")
                return {"success": False, "error": "Audio processing failed"}
        elif self.transcript_file:
            if not self.load_transcript():
                logger.error("Transcript loading failed")
                return {"success": False, "error": "Transcript loading failed"}
        else:
            logger.error("No input provided (need audio or transcript)")
            return {"success": False, "error": "No input provided"}
        
        # Step 2: Detect topic
        self.detect_topic()
        
        # Step 3: Load context
        self.load_context()
        
        # Step 4: Suggest mode (if not specified)
        if self.mode == CAREERSPAN_DEFAULT_MODE:
            suggested = self.suggest_mode()
            print(f"\nSuggested mode: {suggested}")
            print(f"Using default: {self.mode}")
        
        # Step 5: Begin dialogue
        session_data = self.begin_dialogue()
        
        # Step 6: Generate outputs
        synthesis_file = self.generate_synthesis(session_data)
        pending_file = self.generate_pending_updates()
        
        # Step 7: Update topics for weekly review
        # In production, these would come from actual dialogue
        sample_topics = [
            {
                "topic": f"{self.detected_topic} - unresolved aspects",
                "reason": "Requires more validation",
                "priority": "high"
            }
        ]
        self.update_topics_to_revisit(sample_topics)
        
        # Summary
        print("\n" + "=" * 70)
        print("SESSION COMPLETE")
        print("=" * 70)
        print(f"\nSession ID: {self.session_id}")
        print(f"Synthesis: {synthesis_file.relative_to(WORKSPACE)}")
        print(f"Pending updates: {pending_file.relative_to(WORKSPACE)}")
        print(f"Topics added to weekly review: {len(sample_topics)}")
        print("\nNext steps:")
        print("  1. Review session synthesis")
        print("  2. Use `review-pending-updates` to approve knowledge changes")
        print("  3. Topics will resurface in weekend strategic review")
        print("\n" + "=" * 70)
        
        return {
            "success": True,
            "session_id": self.session_id,
            "synthesis_file": str(synthesis_file),
            "pending_updates_file": str(pending_file),
            "topics_added": len(sample_topics)
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Strategic Partner: Core cognitive engine for strategic thinking"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('--audio', type=Path, help='Path to audio file (.wav preferred)')
    input_group.add_argument('--transcript', type=Path, help='Path to transcript file')
    input_group.add_argument('--interactive', action='store_true', help='Interactive mode (paste transcript)')
    
    # Mode and dials
    parser.add_argument('--mode', choices=list(MODE_DESCRIPTIONS.keys()), 
                       help='Strategic mode to use')
    parser.add_argument('--challenge', type=int, choices=range(11), 
                       help='Challenge intensity (0-10)')
    parser.add_argument('--novel', type=int, choices=range(11), 
                       help='Novel perspective intensity (0-10)')
    parser.add_argument('--structure', type=int, choices=range(11), 
                       help='Structure level (0-10)')
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        print("Strategic Partner - Interactive Mode")
        print("=" * 70)
        print("Paste your transcript or thoughts (Ctrl+D when done):\n")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        transcript_content = '\n'.join(lines)
        
        if not transcript_content.strip():
            print("\n❌ No content provided")
            return 1
        
        # Save to temp file
        temp_file = SESSIONS_DIR / "temp_transcript.txt"
        temp_file.write_text(transcript_content, encoding='utf-8')
        args.transcript = temp_file
    
    # Build dials
    dials = CAREERSPAN_DEFAULT_DIALS.copy()
    if args.challenge is not None:
        dials['challenge'] = args.challenge
    if args.novel is not None:
        dials['novel'] = args.novel
    if args.structure is not None:
        dials['structure'] = args.structure
    
    # Create and run session
    session = StrategicPartnerSession(
        audio_file=args.audio,
        transcript_file=args.transcript,
        mode=args.mode,
        dials=dials
    )
    
    result = session.run()
    
    if result["success"]:
        return 0
    else:
        logger.error(f"Session failed: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
