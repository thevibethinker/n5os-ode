#!/usr/bin/env python3
"""
Enhanced Contradiction Detection

Semantic analysis of contradictions across strategic partner sessions.

Features:
- Cross-session contradiction matching
- Logical inconsistency detection
- Resolution tracking
- Integration with weekly review
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
SESSIONS_DIR = WORKSPACE / "N5/sessions/strategic-partner"
CONTRADICTIONS_DIR = SESSIONS_DIR / "contradictions"
CONTRADICTIONS_DB = CONTRADICTIONS_DIR / "contradictions.jsonl"

# Create directories
CONTRADICTIONS_DIR.mkdir(parents=True, exist_ok=True)


class ContradictionDetector:
    """
    Detects and tracks contradictions across strategic sessions
    """
    
    def __init__(self):
        self.contradictions = []
        self.contradiction_patterns = self._init_patterns()
        
        logger.info("Contradiction Detector initialized")
    
    def _init_patterns(self) -> List[Dict]:
        """
        Initialize contradiction detection patterns
        
        Common logical contradictions to detect
        """
        return [
            {
                'pattern_id': 'goal_mismatch',
                'description': 'Stated goal conflicts with stated approach',
                'keywords': [
                    (['enterprise', 'corporate', 'b2b'], ['smb', 'small business', 'b2c']),
                    (['speed', 'fast', 'quick'], ['quality', 'thorough', 'deep']),
                    (['growth', 'scale', 'expand'], ['focus', 'niche', 'specialized'])
                ]
            },
            {
                'pattern_id': 'resource_mismatch',
                'description': 'Resource constraints conflict with ambition',
                'keywords': [
                    (['team of 4', 'small team', 'limited'], ['enterprise', 'multiple products', 'expand']),
                    (['3 months', 'short timeline'], ['major pivot', 'rebuild', 'significant change'])
                ]
            },
            {
                'pattern_id': 'priority_conflict',
                'description': 'Multiple stated priorities that compete for same resources',
                'keywords': [
                    (['priority', 'urgent', 'critical'], ['also priority', 'equally important'])
                ]
            },
            {
                'pattern_id': 'value_prop_tension',
                'description': 'Value proposition elements that conflict',
                'keywords': [
                    (['trust', 'credibility', 'verification'], ['speed', 'efficiency', 'fast']),
                    (['customization', 'personalized'], ['scalable', 'automated', 'standardized'])
                ]
            }
        ]
    
    def extract_statements_from_session(self, session_file: Path) -> List[Dict]:
        """Extract key statements from session for contradiction analysis"""
        statements = []
        
        try:
            content = session_file.read_text(encoding='utf-8')
            
            # Parse session date
            filename = session_file.stem
            date_str = filename.split('-session-')[0]
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Extract statements (simple approach for MVP)
            # Look for key phrases: "should", "need to", "priority is", "goal is"
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for assertion patterns
                if any(phrase in line.lower() for phrase in [
                    'should', 'need to', 'priority', 'goal', 'must',
                    'focus on', 'important', 'critical'
                ]):
                    statements.append({
                        'text': line,
                        'session_file': str(session_file),
                        'session_date': session_date.isoformat(),
                        'line_number': i + 1
                    })
            
            logger.info(f"  {session_file.name}: {len(statements)} statements")
            
            return statements
        
        except Exception as e:
            logger.error(f"Failed to extract statements from {session_file}: {e}")
            return []
    
    def detect_pattern_contradictions(self, 
                                     statements: List[Dict]) -> List[Dict]:
        """
        Detect pattern-based contradictions
        
        Checks for known contradiction patterns across statements
        """
        contradictions = []
        
        # Check each pattern
        for pattern in self.contradiction_patterns:
            for keyword_pair in pattern['keywords']:
                if len(keyword_pair) != 2:
                    continue
                
                keywords_a, keywords_b = keyword_pair
                
                # Find statements with keywords A
                statements_a = [
                    s for s in statements
                    if any(kw in s['text'].lower() for kw in keywords_a)
                ]
                
                # Find statements with keywords B
                statements_b = [
                    s for s in statements
                    if any(kw in s['text'].lower() for kw in keywords_b)
                ]
                
                # If both exist, potential contradiction
                if statements_a and statements_b:
                    # Check if from different sessions (cross-session)
                    sessions_a = set(s['session_date'] for s in statements_a)
                    sessions_b = set(s['session_date'] for s in statements_b)
                    
                    if sessions_a != sessions_b or len(statements_a) + len(statements_b) > 2:
                        contradiction = {
                            'pattern_id': pattern['pattern_id'],
                            'description': pattern['description'],
                            'keywords_a': keywords_a,
                            'keywords_b': keywords_b,
                            'statements_a': statements_a[:2],  # Sample
                            'statements_b': statements_b[:2],  # Sample
                            'sessions_involved': list(sessions_a | sessions_b),
                            'detected_date': datetime.now().isoformat(),
                            'status': 'open',
                            'priority': self._assess_priority(len(sessions_a | sessions_b), len(statements_a) + len(statements_b))
                        }
                        contradictions.append(contradiction)
        
        logger.info(f"Detected {len(contradictions)} pattern contradictions")
        
        return contradictions
    
    def detect_direct_contradictions(self, statements: List[Dict]) -> List[Dict]:
        """
        Detect direct logical contradictions
        
        Looks for opposing statements about same topic
        """
        contradictions = []
        
        # Group statements by topic (simple keyword clustering)
        topic_statements = defaultdict(list)
        
        for stmt in statements:
            # Extract topic keywords (simple approach)
            text_lower = stmt['text'].lower()
            
            # Check for common topics
            topics = []
            if 'pricing' in text_lower or 'price' in text_lower:
                topics.append('pricing')
            if 'enterprise' in text_lower or 'corporate' in text_lower:
                topics.append('enterprise')
            if 'product' in text_lower or 'feature' in text_lower:
                topics.append('product')
            if 'partnership' in text_lower or 'partner' in text_lower:
                topics.append('partnership')
            
            for topic in topics:
                topic_statements[topic].append(stmt)
        
        # Check for opposing sentiments within same topic
        for topic, stmts in topic_statements.items():
            if len(stmts) >= 2:
                # Simple sentiment check (production would be more sophisticated)
                positive = [s for s in stmts if any(w in s['text'].lower() for w in ['should', 'yes', 'good', 'proceed'])]
                negative = [s for s in stmts if any(w in s['text'].lower() for w in ['concern', 'risk', 'but', 'however'])]
                
                if positive and negative:
                    contradiction = {
                        'type': 'direct',
                        'topic': topic,
                        'positive_statements': positive[:2],
                        'negative_statements': negative[:2],
                        'sessions_involved': list(set([s['session_date'] for s in stmts])),
                        'detected_date': datetime.now().isoformat(),
                        'status': 'open',
                        'priority': 'high' if len(set([s['session_date'] for s in stmts])) > 2 else 'medium'
                    }
                    contradictions.append(contradiction)
        
        logger.info(f"Detected {len(contradictions)} direct contradictions")
        
        return contradictions
    
    def _assess_priority(self, session_count: int, statement_count: int) -> str:
        """Assess contradiction priority"""
        if session_count >= 3 or statement_count >= 8:
            return 'high'
        elif session_count >= 2 or statement_count >= 4:
            return 'medium'
        else:
            return 'low'
    
    def load_existing_contradictions(self) -> List[Dict]:
        """Load previously detected contradictions"""
        contradictions = []
        
        if not CONTRADICTIONS_DB.exists():
            return contradictions
        
        try:
            with open(CONTRADICTIONS_DB, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        contradictions.append(json.loads(line))
            
            logger.info(f"Loaded {len(contradictions)} existing contradictions")
            return contradictions
        
        except Exception as e:
            logger.error(f"Failed to load contradictions: {e}")
            return []
    
    def save_contradictions(self, contradictions: List[Dict]):
        """Save detected contradictions"""
        try:
            with open(CONTRADICTIONS_DB, 'w', encoding='utf-8') as f:
                for contradiction in contradictions:
                    f.write(json.dumps(contradiction) + '\n')
            
            logger.info(f"✓ Saved {len(contradictions)} contradictions to {CONTRADICTIONS_DB}")
        
        except Exception as e:
            logger.error(f"Failed to save contradictions: {e}")
    
    def analyze_sessions(self, session_files: List[Path]) -> Dict:
        """
        Analyze sessions for contradictions
        
        Returns detected contradictions
        """
        logger.info("=" * 70)
        logger.info("CONTRADICTION DETECTION")
        logger.info("=" * 70)
        
        # Extract statements from all sessions
        all_statements = []
        for session_file in session_files:
            statements = self.extract_statements_from_session(session_file)
            all_statements.extend(statements)
        
        logger.info(f"Extracted {len(all_statements)} statements from {len(session_files)} sessions")
        
        # Detect pattern-based contradictions
        pattern_contradictions = self.detect_pattern_contradictions(all_statements)
        
        # Detect direct contradictions
        direct_contradictions = self.detect_direct_contradictions(all_statements)
        
        # Combine and deduplicate
        all_contradictions = pattern_contradictions + direct_contradictions
        
        # Load existing and merge
        existing = self.load_existing_contradictions()
        
        # Simple deduplication (production would be smarter)
        # For MVP, just append new ones
        for contradiction in all_contradictions:
            contradiction['id'] = f"C{len(existing) + 1}"
            existing.append(contradiction)
        
        # Save
        self.save_contradictions(existing)
        
        logger.info("=" * 70)
        logger.info("✅ CONTRADICTION DETECTION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"New contradictions: {len(all_contradictions)}")
        logger.info(f"Total tracked: {len(existing)}")
        
        return {
            'new_contradictions': all_contradictions,
            'total_contradictions': existing,
            'count_new': len(all_contradictions),
            'count_total': len(existing)
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Contradiction Detector - Enhanced semantic analysis"
    )
    
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days to analyze (default: 7)')
    parser.add_argument('--show-all', action='store_true',
                       help='Show all contradictions (not just new)')
    
    args = parser.parse_args()
    
    # Find sessions in window
    from datetime import timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    sessions = []
    if SESSIONS_DIR.exists():
        for session_file in SESSIONS_DIR.glob("*-session-*.md"):
            try:
                filename = session_file.stem
                date_str = filename.split('-session-')[0]
                session_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if start_date <= session_date <= end_date:
                    sessions.append(session_file)
            except:
                continue
    
    logger.info(f"Analyzing {len(sessions)} sessions from past {args.days} days")
    
    # Run detection
    detector = ContradictionDetector()
    results = detector.analyze_sessions(sessions)
    
    # Print results
    print(f"\n{'='*70}")
    print("CONTRADICTION DETECTION RESULTS")
    print(f"{'='*70}")
    print(f"New contradictions: {results['count_new']}")
    print(f"Total tracked: {results['count_total']}")
    
    contradictions_to_show = results['total_contradictions'] if args.show_all else results['new_contradictions']
    
    if contradictions_to_show:
        print(f"\nContradictions (showing {len(contradictions_to_show)}):")
        
        for contradiction in contradictions_to_show:
            print(f"\n[{contradiction.get('id', 'NEW')}] {contradiction.get('description', contradiction.get('topic', 'Contradiction'))}")
            print(f"  Priority: {contradiction.get('priority', 'unknown').upper()}")
            print(f"  Status: {contradiction.get('status', 'open')}")
            print(f"  Sessions: {len(contradiction.get('sessions_involved', []))}")
            
            if 'positive_statements' in contradiction:
                print(f"  Positive stance: {contradiction['positive_statements'][0]['text'][:80]}...")
            if 'negative_statements' in contradiction:
                print(f"  Negative stance: {contradiction['negative_statements'][0]['text'][:80]}...")
    
    print(f"\n{'='*70}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
