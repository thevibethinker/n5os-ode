#!/usr/bin/env python3
"""
Weekly Strategic Review Script

Weekend cognitive conciliatory - resurfaces and processes week's strategic thinking.

Runs every Saturday at 12:00 PM ET (configured via scheduled task).

Features:
- Scans week's strategic partner sessions
- Identifies topics-to-revisit (from topics-to-revisit.jsonl)
- Detects emerging contradictions
- Flags critical decisions needed
- Generates weekend review agenda
- Sends proactive notification
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Import analysis modules
sys.path.insert(0, str(Path(__file__).parent))
from contradiction_detector import ContradictionDetector
from strategy_evolution_tracker import StrategyEvolutionTracker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
SESSIONS_DIR = WORKSPACE / "N5/sessions/strategic-partner"
SYNTHESES_DIR = SESSIONS_DIR / "syntheses"
TOPICS_FILE = SESSIONS_DIR / "topics-to-revisit.jsonl"
WEEKLY_REVIEWS_DIR = SESSIONS_DIR / "weekly-reviews"
INTELLIGENCE_FILE = WORKSPACE / "N5/intelligence/personal-understanding.json"

# Create directories
WEEKLY_REVIEWS_DIR.mkdir(parents=True, exist_ok=True)


class WeeklyStrategicReview:
    """
    Manages weekly strategic review process
    
    Cognitive conciliatory that:
    - Resurfaces topics from week's sessions
    - Identifies contradictions
    - Flags critical decisions
    - Synthesizes patterns
    - Facilitates deeper processing
    """
    
    def __init__(self, start_date: Optional[datetime] = None):
        # Default to last 7 days
        self.end_date = datetime.now()
        self.start_date = start_date or (self.end_date - timedelta(days=7))
        
        self.review_id = self._generate_review_id()
        
        self.sessions = []
        self.topics_to_revisit = []
        self.contradictions = []
        self.critical_decisions = []
        self.patterns = []
        self.strategy_evolution = None  # Will hold evolution analysis
        
        logger.info(f"Weekly Review initialized: {self.review_id}")
        logger.info(f"Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
    
    def _generate_review_id(self) -> str:
        """Generate review ID (ISO week format)"""
        year, week, _ = self.end_date.isocalendar()
        return f"{year}-W{week:02d}"
    
    def scan_sessions(self) -> List[Path]:
        """Scan strategic partner sessions from the week"""
        logger.info("Scanning strategic partner sessions...")
        
        sessions = []
        
        if not SESSIONS_DIR.exists():
            logger.warning(f"Sessions directory not found: {SESSIONS_DIR}")
            return sessions
        
        # Find all session files
        for session_file in SESSIONS_DIR.glob("*-session-*.md"):
            try:
                # Parse date from filename (YYYY-MM-DD-session-N.md)
                filename = session_file.stem
                date_str = filename.split('-session-')[0]
                session_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Check if in range
                if self.start_date <= session_date <= self.end_date:
                    sessions.append(session_file)
                    logger.info(f"  ✓ {session_file.name}")
            
            except Exception as e:
                logger.warning(f"Could not parse session file {session_file.name}: {e}")
                continue
        
        self.sessions = sorted(sessions)
        logger.info(f"Found {len(self.sessions)} sessions in period")
        
        return self.sessions
    
    def load_topics_to_revisit(self) -> List[Dict]:
        """Load topics from topics-to-revisit.jsonl"""
        logger.info("Loading topics to revisit...")
        
        topics = []
        
        if not TOPICS_FILE.exists():
            logger.warning(f"Topics file not found: {TOPICS_FILE}")
            return topics
        
        try:
            with open(TOPICS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('{\"_schema'):
                        continue
                    
                    topic = json.loads(line)
                    
                    # Filter for open topics in date range
                    if topic.get('status', 'open') == 'open':
                        topic_date = datetime.strptime(topic['date'], "%Y-%m-%d")
                        if topic_date >= self.start_date:
                            topics.append(topic)
            
            # Sort by priority
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            topics.sort(key=lambda t: (
                priority_order.get(t.get('priority', 'medium'), 1),
                t.get('date', '')
            ))
            
            self.topics_to_revisit = topics
            logger.info(f"Loaded {len(topics)} topics to revisit")
            
            return topics
        
        except Exception as e:
            logger.error(f"Failed to load topics: {e}")
            return []
    
    def detect_contradictions(self) -> List[Dict]:
        """Detect emerging contradictions across sessions (ENHANCED)"""
        logger.info("Detecting contradictions (enhanced)...")
        
        if not self.sessions:
            logger.warning("No sessions to analyze")
            return []
        
        # Use enhanced contradiction detector
        detector = ContradictionDetector()
        results = detector.analyze_sessions(self.sessions)
        
        # Filter for new contradictions this week
        new_contradictions = results.get('new_contradictions', [])
        
        logger.info(f"Detected {len(new_contradictions)} contradictions")
        self.contradictions = new_contradictions
        
        return new_contradictions
    
    def run_strategy_evolution(self) -> Optional[Dict]:
        """Run strategy evolution analysis"""
        logger.info("Running strategy evolution analysis...")
        
        if not self.sessions:
            logger.warning("No sessions to analyze")
            return None
        
        try:
            # Create tracker
            tracker = StrategyEvolutionTracker()
            
            # Run analysis
            evolution = tracker.analyze(self.start_date, self.end_date)
            
            self.strategy_evolution = evolution
            
            logger.info(f"✓ Strategy evolution analysis complete")
            logger.info(f"  Themes: {len(evolution.get('themes', {}))}")
            logger.info(f"  Cohesion: {evolution.get('cohesion_index', 0.0)}")
            
            return evolution
        
        except Exception as e:
            logger.error(f"Strategy evolution analysis failed: {e}")
            return None
    
    def identify_critical_decisions(self) -> List[Dict]:
        """Identify critical decisions needing resolution"""
        logger.info("Identifying critical decisions...")
        
        decisions = []
        
        # In production, would scan for decision points in sessions
        # Look for: deadline mentions, decision language, unresolved choices
        
        # For MVP, extract from topics with deadlines
        for topic in self.topics_to_revisit:
            if topic.get('priority') == 'high':
                # Check for deadline indicators
                reason = topic.get('reason', '').lower()
                if any(word in reason for word in ['deadline', 'decision', 'urgent', 'soon']):
                    decisions.append({
                        'topic': topic['topic'],
                        'reason': topic['reason'],
                        'session_id': topic.get('session_id'),
                        'priority': 'high',
                        'flagged_date': topic['date']
                    })
        
        logger.info(f"Identified {len(decisions)} critical decisions")
        self.critical_decisions = decisions
        
        return decisions
    
    def synthesize_patterns(self) -> List[Dict]:
        """Synthesize patterns across week's sessions"""
        logger.info("Synthesizing patterns...")
        
        patterns = []
        
        # In production, would analyze themes, topics, and trends
        # For MVP, simple topic clustering
        
        # Group topics by theme
        topic_themes = defaultdict(list)
        for topic in self.topics_to_revisit:
            # Simple keyword extraction (production would be smarter)
            topic_text = topic['topic'].lower()
            
            if 'pricing' in topic_text:
                topic_themes['pricing'].append(topic)
            elif any(w in topic_text for w in ['partnership', 'partner']):
                topic_themes['partnerships'].append(topic)
            elif any(w in topic_text for w in ['product', 'feature', 'roadmap']):
                topic_themes['product'].append(topic)
            elif any(w in topic_text for w in ['enterprise', 'smb', 'customer']):
                topic_themes['customer_focus'].append(topic)
            else:
                topic_themes['other'].append(topic)
        
        # Generate pattern observations
        for theme, topics in topic_themes.items():
            if len(topics) >= 2:
                patterns.append({
                    'pattern': f"Recurring theme: {theme}",
                    'frequency': len(topics),
                    'topics': [t['topic'] for t in topics],
                    'implication': f"{theme.title()} appears {len(topics)} times - may need focused session"
                })
        
        logger.info(f"Synthesized {len(patterns)} patterns")
        self.patterns = patterns
        
        return patterns
    
    def generate_review_agenda(self) -> str:
        """Generate weekend review agenda"""
        logger.info("Generating review agenda...")
        
        agenda = f"""# Weekly Strategic Review - {self.review_id}

**Period:** {self.start_date.strftime('%B %d')} - {self.end_date.strftime('%B %d, %Y')}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}

---

## 📊 Week Summary

**Strategic Partner Sessions:** {len(self.sessions)}
**Topics to Revisit:** {len(self.topics_to_revisit)}
**Contradictions Detected:** {len(self.contradictions)}
**Critical Decisions Flagged:** {len(self.critical_decisions)}
**Patterns Identified:** {len(self.patterns)}

---

## 🎯 Topics to Revisit

"""
        
        if not self.topics_to_revisit:
            agenda += "_No open topics from this week._\n\n"
        else:
            # Group by priority
            high_priority = [t for t in self.topics_to_revisit if t.get('priority') == 'high']
            medium_priority = [t for t in self.topics_to_revisit if t.get('priority') == 'medium']
            low_priority = [t for t in self.topics_to_revisit if t.get('priority') == 'low']
            
            if high_priority:
                agenda += "### High Priority\n\n"
                for i, topic in enumerate(high_priority, 1):
                    agenda += f"{i}. **{topic['topic']}**\n"
                    agenda += f"   - Reason: {topic['reason']}\n"
                    agenda += f"   - Session: {topic.get('session_id', 'N/A')}\n"
                    agenda += f"   - Date: {topic['date']}\n\n"
            
            if medium_priority:
                agenda += "### Medium Priority\n\n"
                for i, topic in enumerate(medium_priority, 1):
                    agenda += f"{i}. **{topic['topic']}**\n"
                    agenda += f"   - Reason: {topic['reason']}\n\n"
            
            if low_priority:
                agenda += "### Low Priority\n\n"
                for i, topic in enumerate(low_priority, 1):
                    agenda += f"{i}. **{topic['topic']}**\n\n"
        
        # Contradictions
        agenda += "---\n\n## ⚠️  Contradictions to Reconcile\n\n"
        
        if not self.contradictions:
            agenda += "_No contradictions detected this week._\n\n"
        else:
            for i, contradiction in enumerate(self.contradictions, 1):
                agenda += f"### Contradiction {i}: {contradiction.get('title', 'Untitled')}\n\n"
                agenda += f"**Sessions:** {', '.join(contradiction.get('sessions', []))}\n\n"
                agenda += f"**The Tension:**\n{contradiction.get('description', '')}\n\n"
                agenda += f"**Recommendation:** {contradiction.get('recommendation', 'Discuss and resolve')}\n\n"
        
        # Critical Decisions
        agenda += "---\n\n## 🚨 Critical Decisions Needed\n\n"
        
        if not self.critical_decisions:
            agenda += "_No critical decisions flagged._\n\n"
        else:
            for i, decision in enumerate(self.critical_decisions, 1):
                agenda += f"{i}. **{decision['topic']}**\n"
                agenda += f"   - Reason: {decision['reason']}\n"
                agenda += f"   - Flagged: {decision['flagged_date']}\n"
                agenda += f"   - Priority: {decision['priority'].upper()}\n\n"
        
        # Patterns
        agenda += "---\n\n## 📈 Patterns Identified\n\n"
        
        if not self.patterns:
            agenda += "_No significant patterns detected._\n\n"
        else:
            for pattern in self.patterns:
                agenda += f"**{pattern['pattern']}** (frequency: {pattern['frequency']})\n"
                agenda += f"- Topics: {', '.join(pattern['topics'][:3])}"
                if len(pattern['topics']) > 3:
                    agenda += f" +{len(pattern['topics']) - 3} more"
                agenda += f"\n- Implication: {pattern['implication']}\n\n"
        
        # Next Steps
        agenda += "---\n\n## 🎬 Recommended Focus\n\n"
        agenda += "Based on this week's review:\n\n"
        
        if self.critical_decisions:
            agenda += f"1. **Address {len(self.critical_decisions)} critical decision(s)** - High urgency\n"
        
        if self.contradictions:
            agenda += f"2. **Reconcile {len(self.contradictions)} contradiction(s)** - Alignment needed\n"
        
        if self.patterns:
            top_pattern = max(self.patterns, key=lambda p: p['frequency'])
            agenda += f"3. **Deep dive on {top_pattern['pattern'].lower()}** - Recurring theme\n"
        
        agenda += "\n---\n\n"
        agenda += "*Weekly Strategic Review generated by N5 OS Strategic Partner*\n"
        
        return agenda
    
    def generate_notification(self) -> str:
        """Generate proactive notification text"""
        
        notification = f"""📬 Weekly Strategic Review Ready

This week you had {len(self.sessions)} strategic partner session(s)"""
        
        if self.topics_to_revisit:
            high_priority_count = len([t for t in self.topics_to_revisit if t.get('priority') == 'high'])
            notification += f" with {len(self.topics_to_revisit)} topic(s) to revisit"
            if high_priority_count:
                notification += f" ({high_priority_count} high priority)"
        
        notification += ".\n\n"
        
        if self.contradictions:
            notification += f"{len(self.contradictions)} contradiction(s) detected:\n"
            for c in self.contradictions[:2]:
                notification += f"  • {c.get('title', 'Contradiction')}\n"
            if len(self.contradictions) > 2:
                notification += f"  • +{len(self.contradictions) - 2} more\n"
            notification += "\n"
        
        if self.critical_decisions:
            notification += f"{len(self.critical_decisions)} critical decision(s) flagged:\n"
            for d in self.critical_decisions[:2]:
                notification += f"  • {d['topic']}\n"
            if len(self.critical_decisions) > 2:
                notification += f"  • +{len(self.critical_decisions) - 2} more\n"
            notification += "\n"
        
        notification += f"Review agenda: N5/sessions/strategic-partner/weekly-reviews/{self.review_id}-agenda.md\n\n"
        notification += "Ready when you are: weekly-strategic-review"
        
        return notification
    
    def save_agenda(self, agenda: str) -> Path:
        """Save review agenda to file"""
        agenda_file = WEEKLY_REVIEWS_DIR / f"{self.review_id}-agenda.md"
        
        try:
            agenda_file.write_text(agenda, encoding='utf-8')
            logger.info(f"✓ Review agenda saved: {agenda_file}")
            return agenda_file
        except Exception as e:
            logger.error(f"Failed to save agenda: {e}")
            return None
    
    def trigger_personal_intelligence_update(self):
        """Trigger weekly deep update of personal intelligence"""
        logger.info("Triggering personal intelligence weekly update...")
        
        try:
            import subprocess
            intelligence_script = WORKSPACE / "N5/scripts/update_personal_intelligence.py"
            
            if intelligence_script.exists():
                result = subprocess.run(
                    [sys.executable, str(intelligence_script), '--weekly'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info("✓ Personal intelligence weekly update complete")
                else:
                    logger.warning(f"Personal intelligence update had issues: {result.stderr}")
            else:
                logger.warning("Personal intelligence script not found")
        
        except Exception as e:
            logger.error(f"Failed to trigger personal intelligence update: {e}")
    
    def run(self, notify: bool = False) -> Dict[str, Any]:
        """
        Execute complete weekly review workflow
        
        Args:
            notify: If True, generates notification (for scheduled runs)
        
        Returns:
            Review summary
        """
        logger.info("=" * 70)
        logger.info("WEEKLY STRATEGIC REVIEW")
        logger.info("=" * 70)
        
        # Step 1: Scan sessions
        self.scan_sessions()
        
        # Step 2: Load topics to revisit
        self.load_topics_to_revisit()
        
        # Step 3: Run strategy evolution analysis (NEW)
        self.run_strategy_evolution()
        
        # Step 4: Detect contradictions (ENHANCED)
        self.detect_contradictions()
        
        # Step 5: Identify critical decisions
        self.identify_critical_decisions()
        
        # Step 6: Synthesize patterns
        self.synthesize_patterns()
        
        # Step 7: Generate review agenda
        agenda = self.generate_review_agenda()
        
        # Step 8: Save agenda
        agenda_file = self.save_agenda(agenda)
        
        # Step 9: Trigger personal intelligence weekly update
        self.trigger_personal_intelligence_update()
        
        # Step 9: Generate notification if requested
        notification = None
        if notify:
            notification = self.generate_notification()
            print("\n" + "=" * 70)
            print(notification)
            print("=" * 70 + "\n")
        
        # Summary
        summary = {
            "review_id": self.review_id,
            "period": {
                "start": self.start_date.strftime("%Y-%m-%d"),
                "end": self.end_date.strftime("%Y-%m-%d")
            },
            "sessions_count": len(self.sessions),
            "topics_count": len(self.topics_to_revisit),
            "contradictions_count": len(self.contradictions),
            "decisions_count": len(self.critical_decisions),
            "patterns_count": len(self.patterns),
            "agenda_file": str(agenda_file) if agenda_file else None,
            "notification": notification
        }
        
        logger.info("=" * 70)
        logger.info("✅ WEEKLY STRATEGIC REVIEW COMPLETE")
        logger.info("=" * 70)
        
        return summary


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Weekly Strategic Review - Weekend cognitive conciliatory"
    )
    
    parser.add_argument('--notify', action='store_true',
                       help='Generate proactive notification (for scheduled runs)')
    parser.add_argument('--start-date', type=str,
                       help='Start date (YYYY-MM-DD) - defaults to 7 days ago')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days to review (default: 7)')
    
    args = parser.parse_args()
    
    # Parse start date
    start_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        start_date = datetime.now() - timedelta(days=args.days)
    
    # Run review
    review = WeeklyStrategicReview(start_date=start_date)
    summary = review.run(notify=args.notify)
    
    # Print summary
    print(f"\n{'='*70}")
    print("REVIEW SUMMARY")
    print(f"{'='*70}")
    print(f"Review ID: {summary['review_id']}")
    print(f"Period: {summary['period']['start']} to {summary['period']['end']}")
    print(f"Sessions: {summary['sessions_count']}")
    print(f"Topics to revisit: {summary['topics_count']}")
    print(f"Contradictions: {summary['contradictions_count']}")
    print(f"Critical decisions: {summary['decisions_count']}")
    print(f"Patterns: {summary['patterns_count']}")
    
    if summary['agenda_file']:
        print(f"\nAgenda: {summary['agenda_file']}")
        print(f"\nTo start review: weekly-strategic-review")
    
    print(f"{'='*70}\n")
    
    return 0 if summary['agenda_file'] else 1


if __name__ == "__main__":
    sys.exit(main())
