#!/usr/bin/env python3
"""
Strategy Evolution Tracker

Quantitative tracking of strategic evolution across sessions.

Features:
- Consensus scoring (recency-weighted)
- Divergence measurement (conflict detection)
- Trajectory analysis (momentum tracking)
- Heat zone classification
- Baseline diff analysis
- Cohesion index calculation
"""

import os
import sys
import json
import logging
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
SESSIONS_DIR = WORKSPACE / "N5/sessions/strategic-partner"
EVOLUTION_DIR = WORKSPACE / "N5/strategy-evolution"
STATE_FILE = EVOLUTION_DIR / "state.json"
KNOWLEDGE_DIR = WORKSPACE / "Knowledge"

# Create directories
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
DEFAULT_DECAY_FACTOR = 0.1  # λ for exponential decay
DEFAULT_WINDOW_SESSIONS = 10
DEFAULT_WINDOW_DAYS = 30
CONSENSUS_THRESHOLD_LOCKED_IN = 0.8
CONSENSUS_THRESHOLD_SOLIDIFYING = 0.5
DIVERGENCE_THRESHOLD_LOW = 0.3
DIVERGENCE_THRESHOLD_HIGH = 0.6
TRAJECTORY_THRESHOLD_RISING = 0.15
TRAJECTORY_THRESHOLD_FALLING = -0.15


class StrategyEvolutionTracker:
    """
    Tracks strategic evolution across sessions with quantitative scoring
    """
    
    def __init__(self, 
                 window_sessions: int = DEFAULT_WINDOW_SESSIONS,
                 window_days: int = DEFAULT_WINDOW_DAYS,
                 decay_factor: float = DEFAULT_DECAY_FACTOR):
        
        self.window_sessions = window_sessions
        self.window_days = window_days
        self.decay_factor = decay_factor
        
        self.state = self._load_state()
        self.themes = {}  # theme_id -> ThemeTracker
        self.baseline_strategy = {}
        
        logger.info(f"Strategy Evolution Tracker initialized")
        logger.info(f"  Window: {window_sessions} sessions or {window_days} days")
        logger.info(f"  Decay factor: {decay_factor}")
    
    def _load_state(self) -> Dict:
        """Load persistent state"""
        if STATE_FILE.exists():
            try:
                content = STATE_FILE.read_text(encoding='utf-8')
                state = json.loads(content)
                logger.info(f"✓ Loaded state from {STATE_FILE}")
                return state
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                return self._init_state()
        else:
            return self._init_state()
    
    def _init_state(self) -> Dict:
        """Initialize empty state"""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "window": {
                "sessions": self.window_sessions,
                "days": self.window_days
            },
            "themes": {},
            "sessions_analyzed": [],
            "baseline_files": []
        }
    
    def _save_state(self):
        """Save state to disk"""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            content = json.dumps(self.state, indent=2, ensure_ascii=False)
            STATE_FILE.write_text(content, encoding='utf-8')
            logger.info(f"✓ State saved to {STATE_FILE}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def load_baseline_strategy(self, baseline_files: Optional[List[Path]] = None):
        """
        Load baseline strategy from Knowledge/ hypotheses
        
        Reads GTM/product hypotheses as baseline for diff analysis
        """
        logger.info("Loading baseline strategy...")
        
        if not baseline_files:
            # Auto-detect hypothesis files
            baseline_files = []
            hypotheses_dir = KNOWLEDGE_DIR / "hypotheses"
            if hypotheses_dir.exists():
                baseline_files = list(hypotheses_dir.glob("*.md"))
        
        baseline = {}
        
        for filepath in baseline_files:
            try:
                content = filepath.read_text(encoding='utf-8')
                
                # Extract themes from hypotheses
                # Simple extraction (production would be more sophisticated)
                themes = self._extract_themes_from_baseline(content, filepath.stem)
                baseline.update(themes)
                
                logger.info(f"✓ Loaded baseline: {filepath.name}")
            
            except Exception as e:
                logger.warning(f"Could not load {filepath}: {e}")
        
        self.baseline_strategy = baseline
        self.state["baseline_files"] = [str(f) for f in baseline_files]
        
        logger.info(f"Loaded {len(baseline)} baseline themes")
        
        return baseline
    
    def _extract_themes_from_baseline(self, content: str, source: str) -> Dict:
        """Extract themes from baseline document"""
        themes = {}
        
        # Simple keyword extraction (production would use NLP)
        # Look for headers, bullet points, key phrases
        
        lines = content.split('\n')
        current_theme = None
        
        for line in lines:
            line = line.strip()
            
            # Headers
            if line.startswith('##') and not line.startswith('###'):
                theme_text = line.lstrip('#').strip()
                theme_id = self._normalize_theme(theme_text)
                current_theme = theme_id
                themes[theme_id] = {
                    "text": theme_text,
                    "source": source,
                    "type": "baseline",
                    "content": []
                }
            
            # Bullet points
            elif line.startswith('-') or line.startswith('*'):
                if current_theme:
                    themes[current_theme]["content"].append(line.lstrip('-*').strip())
        
        return themes
    
    def _normalize_theme(self, text: str) -> str:
        """Normalize theme text to ID"""
        # Convert to lowercase, remove special chars, replace spaces with underscores
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s_]', '', text)
        text = re.sub(r'\s+', '_', text)
        return text
    
    def scan_sessions(self, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[Path]:
        """
        Scan strategic partner sessions in window
        
        Returns sessions within window (by date or count)
        """
        logger.info("Scanning sessions...")
        
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(days=self.window_days))
        
        sessions = []
        
        if not SESSIONS_DIR.exists():
            logger.warning(f"Sessions directory not found: {SESSIONS_DIR}")
            return sessions
        
        # Find all session files
        for session_file in SESSIONS_DIR.glob("*-session-*.md"):
            try:
                # Parse date
                filename = session_file.stem
                date_str = filename.split('-session-')[0]
                session_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Check if in range
                if start_date <= session_date <= end_date:
                    sessions.append((session_date, session_file))
            
            except Exception as e:
                logger.warning(f"Could not parse session file {session_file.name}: {e}")
                continue
        
        # Sort by date
        sessions.sort(key=lambda x: x[0])
        
        # Apply session limit if needed
        if len(sessions) > self.window_sessions:
            sessions = sessions[-self.window_sessions:]
        
        session_files = [s[1] for s in sessions]
        
        logger.info(f"Found {len(session_files)} sessions in window")
        
        return session_files
    
    def extract_themes_from_session(self, session_file: Path) -> List[Dict]:
        """Extract themes and mentions from session"""
        themes = []
        
        try:
            content = session_file.read_text(encoding='utf-8')
            
            # Simple theme extraction (production would be more sophisticated)
            # Look for key topics, decisions, goals
            
            # Parse date from filename
            filename = session_file.stem
            date_str = filename.split('-session-')[0]
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Extract themes (placeholder logic)
            # In production, would use NLP to extract actual themes
            
            # For MVP, look for common strategic keywords
            keywords = {
                'enterprise': ['enterprise', 'corporate', 'b2b'],
                'pricing': ['pricing', 'price', 'revenue'],
                'product': ['product', 'feature', 'roadmap'],
                'partnership': ['partnership', 'partner', 'collaboration'],
                'hiring': ['hiring', 'recruitment', 'team'],
                'gtm': ['go-to-market', 'gtm', 'sales', 'marketing']
            }
            
            content_lower = content.lower()
            
            for theme_id, kws in keywords.items():
                count = sum(content_lower.count(kw) for kw in kws)
                if count > 0:
                    # Determine sentiment (simple heuristic)
                    supportive = bool(any(word in content_lower for word in ['good', 'should', 'yes', 'proceed']))
                    cautious = bool(any(word in content_lower for word in ['concern', 'risk', 'worry', 'but']))
                    
                    themes.append({
                        'theme_id': theme_id,
                        'theme_text': theme_id.title(),
                        'session_file': str(session_file),
                        'session_date': session_date.isoformat(),
                        'count': count,
                        'supportive': supportive,
                        'cautious': cautious,
                        'sentiment': 'supportive' if supportive and not cautious else 'cautious' if cautious else 'neutral'
                    })
            
            logger.info(f"  {session_file.name}: {len(themes)} themes")
            
            return themes
        
        except Exception as e:
            logger.error(f"Failed to extract themes from {session_file}: {e}")
            return []
    
    def calculate_consensus(self, theme_mentions: List[Dict]) -> float:
        """
        Calculate consensus score with exponential decay weighting
        
        Formula: Σ(w_i) / N where w_i = exp(-λ * t_i)
        λ = decay_factor, t_i = days since mention
        """
        if not theme_mentions:
            return 0.0
        
        now = datetime.now()
        weighted_sum = 0.0
        
        for mention in theme_mentions:
            mention_date = datetime.fromisoformat(mention['session_date'])
            days_ago = (now - mention_date).days
            weight = math.exp(-self.decay_factor * days_ago)
            weighted_sum += weight
        
        # Normalize by number of sessions in window
        consensus = weighted_sum / max(len(self.state['sessions_analyzed']), 1)
        
        # Cap at 1.0
        consensus = min(consensus, 1.0)
        
        return round(consensus, 2)
    
    def calculate_divergence(self, theme_mentions: List[Dict]) -> float:
        """
        Calculate divergence score
        
        Formula: |support – conflict| ÷ total mentions
        """
        if not theme_mentions:
            return 0.0
        
        support_count = sum(1 for m in theme_mentions if m['sentiment'] == 'supportive')
        cautious_count = sum(1 for m in theme_mentions if m['sentiment'] == 'cautious')
        
        total = len(theme_mentions)
        divergence = abs(support_count - cautious_count) / total
        
        return round(divergence, 2)
    
    def calculate_trajectory(self, theme_id: str, current_consensus: float) -> float:
        """
        Calculate trajectory (change in consensus)
        
        Formula: Δ Consensus between current and previous window
        """
        # Get previous consensus from state
        if theme_id in self.state['themes']:
            previous_consensus = self.state['themes'][theme_id].get('consensus', 0.0)
            trajectory = current_consensus - previous_consensus
            return round(trajectory, 2)
        else:
            # New theme, no previous data
            return 0.0
    
    def classify_heat_zone(self, consensus: float, divergence: float, 
                          trajectory: float) -> str:
        """
        Classify theme into heat zone
        
        Zones: Emerging, Solidifying, Locked-In, At-Risk
        """
        # At-Risk: High divergence OR negative trajectory
        if divergence >= DIVERGENCE_THRESHOLD_HIGH or trajectory < TRAJECTORY_THRESHOLD_FALLING:
            return "At-Risk"
        
        # Locked-In: High consensus, stable, low divergence
        if (consensus >= CONSENSUS_THRESHOLD_LOCKED_IN and 
            divergence < DIVERGENCE_THRESHOLD_LOW and
            abs(trajectory) < abs(TRAJECTORY_THRESHOLD_FALLING)):
            return "Locked-In"
        
        # Solidifying: Moderate consensus, positive/stable trajectory
        if (CONSENSUS_THRESHOLD_SOLIDIFYING <= consensus < CONSENSUS_THRESHOLD_LOCKED_IN):
            return "Solidifying"
        
        # Emerging: Low consensus, positive trajectory
        if (consensus < CONSENSUS_THRESHOLD_SOLIDIFYING and 
            trajectory > 0.1):
            return "Emerging"
        
        # Default
        return "Emerging" if consensus < CONSENSUS_THRESHOLD_SOLIDIFYING else "Solidifying"
    
    def calculate_cohesion_index(self, themes_data: Dict) -> float:
        """
        Calculate overall strategic cohesion
        
        Formula: Harmonic mean of Consensus and (1 – Divergence)
        """
        if not themes_data:
            return 0.0
        
        cohesion_scores = []
        
        for theme_id, data in themes_data.items():
            consensus = data['consensus']
            divergence = data['divergence']
            
            # Harmonic mean of consensus and (1 - divergence)
            alignment = 1 - divergence
            if consensus + alignment > 0:
                cohesion = 2 * consensus * alignment / (consensus + alignment)
                cohesion_scores.append(cohesion)
        
        # Overall cohesion = average of theme cohesions
        if cohesion_scores:
            overall_cohesion = sum(cohesion_scores) / len(cohesion_scores)
            return round(overall_cohesion, 2)
        else:
            return 0.0
    
    def compare_to_baseline(self, theme_id: str, theme_data: Dict) -> Tuple[str, str]:
        """
        Compare theme to baseline strategy
        
        Returns: (diff_tag, magnitude)
        Tags: Amplifies, Reinforces, Deviates, New
        Magnitude: Low, Medium, High
        """
        if theme_id not in self.baseline_strategy:
            return ("New", "-")
        
        baseline_theme = self.baseline_strategy[theme_id]
        
        # Simple comparison (production would be more sophisticated)
        # Check consensus level to determine tag
        
        consensus = theme_data['consensus']
        divergence = theme_data['divergence']
        
        # Amplifies: High consensus, low divergence, matches baseline
        if consensus >= 0.8 and divergence < 0.3:
            magnitude = "High" if consensus > 0.9 else "Medium"
            return ("Amplifies", magnitude)
        
        # Reinforces: Moderate consensus, matches baseline
        if 0.5 <= consensus < 0.8:
            magnitude = "Medium" if consensus > 0.6 else "Low"
            return ("Reinforces", magnitude)
        
        # Deviates: High divergence or conflicting
        if divergence >= 0.6:
            magnitude = "High" if divergence > 0.7 else "Medium"
            return ("Deviates", magnitude)
        
        # Default: Reinforces with low magnitude
        return ("Reinforces", "Low")
    
    def analyze(self, start_date: Optional[datetime] = None,
               end_date: Optional[datetime] = None) -> Dict:
        """
        Execute complete analysis workflow
        
        Returns analysis results
        """
        logger.info("=" * 70)
        logger.info("STRATEGY EVOLUTION ANALYSIS")
        logger.info("=" * 70)
        
        # Step 1: Load baseline
        self.load_baseline_strategy()
        
        # Step 2: Scan sessions
        sessions = self.scan_sessions(start_date, end_date)
        
        if not sessions:
            logger.warning("No sessions found in window")
            return {
                "themes": {},
                "cohesion_index": 0.0,
                "sessions_count": 0
            }
        
        # Step 3: Extract themes from sessions
        all_theme_mentions = defaultdict(list)
        
        for session_file in sessions:
            themes = self.extract_themes_from_session(session_file)
            for theme in themes:
                all_theme_mentions[theme['theme_id']].append(theme)
        
        # Step 4: Calculate scores for each theme
        themes_data = {}
        
        for theme_id, mentions in all_theme_mentions.items():
            consensus = self.calculate_consensus(mentions)
            divergence = self.calculate_divergence(mentions)
            trajectory = self.calculate_trajectory(theme_id, consensus)
            heat_zone = self.classify_heat_zone(consensus, divergence, trajectory)
            
            theme_data = {
                'theme_id': theme_id,
                'theme_text': mentions[0]['theme_text'],
                'consensus': consensus,
                'divergence': divergence,
                'trajectory': trajectory,
                'heat_zone': heat_zone,
                'mentions_count': len(mentions),
                'sessions': list(set(m['session_file'] for m in mentions))
            }
            
            # Baseline comparison
            diff_tag, magnitude = self.compare_to_baseline(theme_id, theme_data)
            theme_data['baseline_diff'] = diff_tag
            theme_data['baseline_magnitude'] = magnitude
            
            themes_data[theme_id] = theme_data
        
        # Step 5: Calculate cohesion index
        cohesion_index = self.calculate_cohesion_index(themes_data)
        
        # Step 6: Update state
        self.state['themes'] = themes_data
        self.state['sessions_analyzed'] = [str(s) for s in sessions]
        self._save_state()
        
        logger.info("=" * 70)
        logger.info("✅ ANALYSIS COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Themes analyzed: {len(themes_data)}")
        logger.info(f"Cohesion index: {cohesion_index}")
        
        return {
            "themes": themes_data,
            "cohesion_index": cohesion_index,
            "sessions_count": len(sessions),
            "window": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Strategy Evolution Tracker - Quantitative analysis"
    )
    
    parser.add_argument('--period', choices=['week', 'month', 'quarter'],
                       default='week', help='Analysis period')
    parser.add_argument('--window-sessions', type=int, default=DEFAULT_WINDOW_SESSIONS,
                       help='Session window size')
    parser.add_argument('--window-days', type=int, default=DEFAULT_WINDOW_DAYS,
                       help='Day window size')
    parser.add_argument('--decay', type=float, default=DEFAULT_DECAY_FACTOR,
                       help='Decay factor (λ) for recency weighting')
    parser.add_argument('--baseline', type=Path, action='append',
                       help='Baseline strategy file (can specify multiple)')
    
    args = parser.parse_args()
    
    # Determine date range
    end_date = datetime.now()
    if args.period == 'week':
        start_date = end_date - timedelta(days=7)
    elif args.period == 'month':
        start_date = end_date - timedelta(days=30)
    elif args.period == 'quarter':
        start_date = end_date - timedelta(days=90)
    
    # Create tracker
    tracker = StrategyEvolutionTracker(
        window_sessions=args.window_sessions,
        window_days=args.window_days,
        decay_factor=args.decay
    )
    
    # Load custom baseline if provided
    if args.baseline:
        tracker.load_baseline_strategy(args.baseline)
    
    # Run analysis
    results = tracker.analyze(start_date, end_date)
    
    # Print summary
    print(f"\n{'='*70}")
    print("STRATEGY EVOLUTION SUMMARY")
    print(f"{'='*70}")
    print(f"Period: {args.period}")
    print(f"Sessions analyzed: {results['sessions_count']}")
    print(f"Themes tracked: {len(results['themes'])}")
    print(f"Cohesion Index: {results['cohesion_index']} ({'Healthy' if results['cohesion_index'] >= 0.7 else 'Moderate' if results['cohesion_index'] >= 0.5 else 'Low'})")
    
    # Group by heat zone
    heat_zones = defaultdict(list)
    for theme_id, data in results['themes'].items():
        heat_zones[data['heat_zone']].append((theme_id, data))
    
    print(f"\nHeat Map:")
    for zone in ['Locked-In', 'Solidifying', 'Emerging', 'At-Risk']:
        if zone in heat_zones:
            print(f"\n{zone}:")
            for theme_id, data in heat_zones[zone]:
                print(f"  • {data['theme_text']} (consensus: {data['consensus']}, divergence: {data['divergence']})")
    
    print(f"\n{'='*70}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
