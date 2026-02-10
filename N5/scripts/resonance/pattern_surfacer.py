#!/usr/bin/env python3
"""
Pattern Surfacer: Analyze brain.db to classify ideas by resonance level.

Resonance Hierarchy:
- L0 Cornerstone: 10+ meetings (foundational beliefs)
- L1 Active Thesis: 4-9 meetings (developing ideas)
- L2 Recurring Tool: 2-3 meetings (frameworks V reaches for)
- L3 Spark: 1 meeting (novel ideas)

Schema Versions:
- 1.0: Original format (no schema_version field)
- 2.0: Adds velocity, co_occurrence, external_validations structures

Usage:
    python3 pattern_surfacer.py generate     # Generate resonance_index.json
    python3 pattern_surfacer.py report       # Human-readable summary
    python3 pattern_surfacer.py stats        # Quick stats
"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
from itertools import combinations

# Import evolution_tracker functions for Phase 3 & 4 features
import sys
sys.path.insert(0, str(Path(__file__).parent))
try:
    from evolution_tracker import (
        get_challenge_status,
        get_ideas_with_lineage,
        detect_potential_duplicates,
        build_genealogy
    )
except ImportError:
    # Graceful fallback if evolution_tracker not available
    def get_challenge_status(idea_slug=None):
        return {'total_challenges': 0, 'by_status': {'pending': 0, 'resolved': 0, 'abandoned': 0}, 'challenges': {'pending': [], 'resolved': [], 'abandoned': []}, 'stale_challenges': []}
    def get_ideas_with_lineage():
        return []
    def detect_potential_duplicates(threshold=0.7):
        return []
    def build_genealogy(idea_id):
        return {'ancestors': [], 'descendants': [], 'siblings': [], 'lineage_depth': 0}

# Paths
N5_ROOT = Path("/home/workspace/N5")
EDGES_DB = Path("/home/workspace/N5/cognition/brain.db")
RESONANCE_INDEX = N5_ROOT / "data" / "resonance_index.json"
INSIGHTS_DIR = N5_ROOT / "insights" / "resonance"

# Schema version
CURRENT_SCHEMA_VERSION = "2.0"

# Thresholds (configurable)
THRESHOLDS = {
    "cornerstone": 10,  # L0: 10+ meetings
    "active_thesis": 4,  # L1: 4-9 meetings
    "recurring_tool": 2,  # L2: 2-3 meetings
    # L3 Spark: 1 meeting (implicit)
}

# Velocity thresholds
VELOCITY_WEEKS = 8  # Look at last 8 weeks of data
RISING_THRESHOLD = 1.5  # Recent mentions > 1.5x earlier = rising
FALLING_THRESHOLD = 0.5  # Recent mentions < 0.5x earlier = falling

# Co-occurrence thresholds
MIN_SHARED_MEETINGS = 2  # Minimum meetings to count as co-occurrence
CONVERGENCE_WEEKS_EARLY = 4  # Early window: weeks 5-8 ago
CONVERGENCE_WEEKS_RECENT = 4  # Recent window: last 4 weeks


def get_db_connection():
    """Get SQLite connection."""
    return sqlite3.connect(EDGES_DB)


def get_idea_frequencies() -> Dict[str, Dict]:
    """
    Query brain.db for idea frequencies across extraction sessions.
    Returns dict of idea_slug -> {frequency, sessions, first_seen, last_seen, label, contexts}
    
    Note: context_meeting_id stores batch/session IDs (e.g., 'backfill-2026-01-05-1230'),
    which represent distinct extraction sessions. We count unique sessions as frequency.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all edges involving ideas with their session context
    cursor.execute("""
        SELECT 
            source_type, source_id, target_type, target_id,
            relation, context_meeting_id, evidence, created_at
        FROM meeting_edges
        WHERE source_type = 'idea' OR target_type = 'idea'
    """)
    
    rows = cursor.fetchall()
    
    # Also get entity labels directly
    cursor.execute("SELECT entity_id, name, created_at FROM entities WHERE entity_type = 'idea'")
    entity_rows = cursor.fetchall()
    entity_labels = {row[0]: row[1] for row in entity_rows}
    entity_dates = {row[0]: row[2] for row in entity_rows}
    
    # Process edges to build idea -> sessions mapping
    idea_sessions = defaultdict(set)
    idea_contexts = defaultdict(set)
    idea_dates = defaultdict(list)
    
    for row in rows:
        source_type, source_id, target_type, target_id, relation, session_id, evidence, created_at = row
        
        # Get the idea slug from either source or target
        idea_slug = None
        if source_type == 'idea':
            idea_slug = source_id
        elif target_type == 'idea':
            idea_slug = target_id
        
        if idea_slug:
            # Count any non-empty session_id as a unique extraction session
            if session_id:
                idea_sessions[idea_slug].add(session_id)
            if created_at:
                idea_dates[idea_slug].append(created_at)
            
            # Extract context keywords from evidence
            if evidence:
                words = evidence.lower().split()
                for word in words:
                    if len(word) > 4 and word not in ['about', 'their', 'which', 'would', 'could', 'being', 'there', 'these', 'those']:
                        idea_contexts[idea_slug].add(word[:20])
    
    conn.close()
    
    # Build frequency data
    ideas = {}
    for idea_slug, sessions in idea_sessions.items():
        dates = sorted(idea_dates.get(idea_slug, []))
        ideas[idea_slug] = {
            "idea_slug": idea_slug,
            "label": entity_labels.get(idea_slug, idea_slug.replace("-", " ").title()),
            "frequency": len(sessions),
            "sessions": sorted(list(sessions)),
            "first_seen": dates[0][:10] if dates else None,
            "last_seen": dates[-1][:10] if dates else None,
            "sample_contexts": list(idea_contexts.get(idea_slug, set()))[:5]
        }
    
    return ideas


def classify_ideas(ideas: Dict[str, Dict]) -> Dict[str, List]:
    """Classify ideas into resonance levels."""
    classified = {
        "cornerstones": [],      # L0: 10+
        "active_theses": [],     # L1: 4-9
        "recurring_tools": [],   # L2: 2-3
        "sparks": []             # L3: 1
    }
    
    for idea_slug, data in ideas.items():
        freq = data["frequency"]
        
        if freq >= THRESHOLDS["cornerstone"]:
            classified["cornerstones"].append(data)
        elif freq >= THRESHOLDS["active_thesis"]:
            classified["active_theses"].append(data)
        elif freq >= THRESHOLDS["recurring_tool"]:
            classified["recurring_tools"].append(data)
        else:
            classified["sparks"].append(data)
    
    # Sort each category by frequency descending
    for key in classified:
        classified[key] = sorted(classified[key], key=lambda x: -x["frequency"])
    
    return classified


def load_resonance_index() -> Optional[Dict]:
    """
    Load and migrate resonance_index.json to current schema version.
    
    Migration logic:
    - No file: return None
    - No schema_version field: treat as 1.0, migrate to 2.0
    - schema_version 2.0: return as-is
    
    Returns:
        Migrated index dict or None if file doesn't exist
    """
    if not RESONANCE_INDEX.exists():
        return None
    
    with open(RESONANCE_INDEX, "r") as f:
        index = json.load(f)
    
    # Detect schema version
    version = index.get("schema_version", "1.0")
    
    if version == "1.0":
        # Migrate 1.0 -> 2.0: Add empty V2 structures
        index["schema_version"] = "2.0"
        index["velocity"] = {}  # idea_slug -> {trend: rising|stable|falling, week_over_week: float}
        index["co_occurrence"] = {}  # idea_slug -> [{paired_with: str, frequency: int, contexts: list}]
        index["external_validations"] = {}  # idea_slug -> [{validator_id: str, meeting_id: str, validated_at: str}]
        
    # Future migrations would go here: elif version == "2.0": migrate to 3.0, etc.
    
    return index


def compute_weekly_mentions() -> Dict[str, Dict[str, int]]:
    """
    Compute weekly mention counts for each idea.
    
    Returns:
        Dict of idea_slug -> {iso_week_string -> count}
        where iso_week_string is 'YYYY-WNN' format
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all idea edges with timestamps
    cursor.execute("""
        SELECT 
            source_type, source_id, target_type, target_id, created_at
        FROM meeting_edges
        WHERE (source_type = 'idea' OR target_type = 'idea')
          AND created_at IS NOT NULL
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group by idea -> week
    idea_weeks = defaultdict(lambda: defaultdict(int))
    
    for row in rows:
        source_type, source_id, target_type, target_id, created_at = row
        
        # Get the idea slug
        idea_slug = source_id if source_type == 'idea' else target_id
        
        # Parse timestamp and get ISO week
        try:
            # Handle both ISO format and SQLite datetime format
            if 'T' in created_at:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(created_at[:19], '%Y-%m-%d %H:%M:%S')
            
            iso_year, iso_week, _ = dt.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            idea_weeks[idea_slug][week_key] += 1
        except (ValueError, TypeError):
            continue
    
    return dict(idea_weeks)


def compute_velocity(weekly_mentions: Dict[str, Dict[str, int]]) -> Dict[str, Dict]:
    """
    Compute velocity (trend) for each idea based on week-over-week comparison.
    
    Compares the last 4 weeks (recent) vs the 4 weeks before that (earlier).
    - Rising: recent_avg > earlier_avg * 1.5
    - Falling: recent_avg < earlier_avg * 0.5
    - Stable: otherwise
    
    Returns:
        Dict of idea_slug -> {trend: str, recent_count: int, earlier_count: int, 
                              weeks_active: int, recent_weeks: list}
    """
    # Generate the last 8 weeks as ISO week strings
    now = datetime.now(timezone.utc)
    weeks = []
    for i in range(VELOCITY_WEEKS):
        week_dt = now - timedelta(weeks=i)
        iso_year, iso_week, _ = week_dt.isocalendar()
        weeks.append(f"{iso_year}-W{iso_week:02d}")
    
    # weeks[0] = current week, weeks[7] = 8 weeks ago
    recent_weeks = weeks[:4]  # Last 4 weeks
    earlier_weeks = weeks[4:8]  # 4 weeks before that
    
    velocity = {}
    
    for idea_slug, week_counts in weekly_mentions.items():
        # Count mentions in recent vs earlier period
        recent_count = sum(week_counts.get(w, 0) for w in recent_weeks)
        earlier_count = sum(week_counts.get(w, 0) for w in earlier_weeks)
        
        # Determine which weeks this idea was active
        active_weeks = [w for w in weeks if week_counts.get(w, 0) > 0]
        weeks_active = len(active_weeks)
        
        # Compute trend
        if earlier_count == 0:
            # No earlier activity
            if recent_count > 0:
                trend = "rising"  # New idea appearing
            else:
                trend = "dormant"  # No activity in 8 weeks
        else:
            ratio = recent_count / earlier_count
            if ratio >= RISING_THRESHOLD:
                trend = "rising"
            elif ratio <= FALLING_THRESHOLD:
                trend = "falling"
            else:
                trend = "stable"
        
        velocity[idea_slug] = {
            "trend": trend,
            "recent_count": recent_count,
            "earlier_count": earlier_count,
            "weeks_active": weeks_active,
            "recent_weeks": [w for w in recent_weeks if week_counts.get(w, 0) > 0]
        }
    
    return velocity


def build_co_occurrence_matrix(min_shared_meetings: int = MIN_SHARED_MEETINGS) -> Dict[str, Dict]:
    """
    Build matrix of idea pairs that appear in the same meetings.
    
    Two ideas "co-occur" when they both have edges with the same context_meeting_id.
    Only pairs with at least min_shared_meetings shared meetings are included.
    
    Returns:
        Dict with tuple keys "(idea_a, idea_b)" -> {
            'shared_meetings': [meeting_ids],
            'shared_count': int,
            'first_co_occurrence': date,
            'recent_co_occurrence': date,
            'meeting_dates': {meeting_id: date}
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all edges with meeting context, grouped by meeting
    cursor.execute("""
        SELECT 
            context_meeting_id,
            CASE WHEN source_type='idea' THEN source_id 
                 WHEN target_type='idea' THEN target_id 
            END as idea_slug,
            created_at
        FROM meeting_edges
        WHERE context_meeting_id IS NOT NULL
          AND (source_type = 'idea' OR target_type = 'idea')
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group ideas by meeting
    meeting_ideas = defaultdict(set)
    meeting_dates = {}
    
    for meeting_id, idea_slug, created_at in rows:
        if idea_slug:
            meeting_ideas[meeting_id].add(idea_slug)
            # Track earliest date for each meeting
            if meeting_id not in meeting_dates or (created_at and created_at < meeting_dates[meeting_id]):
                meeting_dates[meeting_id] = created_at[:10] if created_at else None
    
    # Build co-occurrence pairs
    pair_meetings = defaultdict(list)
    
    for meeting_id, ideas in meeting_ideas.items():
        if len(ideas) >= 2:
            # Generate all pairs of ideas in this meeting
            for idea_a, idea_b in combinations(sorted(ideas), 2):
                pair_key = f"{idea_a}|{idea_b}"
                pair_meetings[pair_key].append(meeting_id)
    
    # Filter to pairs with minimum shared meetings
    co_occurrence = {}
    
    for pair_key, meetings in pair_meetings.items():
        if len(meetings) >= min_shared_meetings:
            # Get dates for this pair's meetings
            dates = [meeting_dates.get(m) for m in meetings if meeting_dates.get(m)]
            dates = sorted([d for d in dates if d])
            
            co_occurrence[pair_key] = {
                'shared_meetings': meetings,
                'shared_count': len(meetings),
                'first_co_occurrence': dates[0] if dates else None,
                'recent_co_occurrence': dates[-1] if dates else None,
                'meeting_dates': {m: meeting_dates.get(m) for m in meetings}
            }
    
    return co_occurrence


def detect_convergence(co_occurrence: Dict[str, Dict]) -> List[Dict]:
    """
    Detect idea pairs that were separate in earlier weeks but now co-occur.
    
    Convergence = ideas that:
    1. Did NOT co-occur in weeks 5-8 (earlier period)
    2. DO co-occur in weeks 1-4 (recent period)
    
    Returns:
        List of converging pairs: [{
            'idea_a': str,
            'idea_b': str,
            'recent_meetings': [meeting_ids],
            'convergence_date': date (first co-occurrence in recent period)
        }]
    """
    now = datetime.now(timezone.utc)
    
    # Calculate date boundaries
    recent_cutoff = (now - timedelta(weeks=CONVERGENCE_WEEKS_RECENT)).strftime('%Y-%m-%d')
    early_cutoff = (now - timedelta(weeks=CONVERGENCE_WEEKS_EARLY + CONVERGENCE_WEEKS_RECENT)).strftime('%Y-%m-%d')
    
    converging_pairs = []
    
    for pair_key, data in co_occurrence.items():
        idea_a, idea_b = pair_key.split('|')
        
        # Classify meetings by period
        early_meetings = []
        recent_meetings = []
        
        for meeting_id, date in data['meeting_dates'].items():
            if not date:
                continue
            if date >= recent_cutoff:
                recent_meetings.append((meeting_id, date))
            elif date >= early_cutoff:
                early_meetings.append((meeting_id, date))
        
        # Convergence: no early co-occurrence, but recent co-occurrence exists
        if len(early_meetings) == 0 and len(recent_meetings) >= 1:
            recent_meetings_sorted = sorted(recent_meetings, key=lambda x: x[1])
            
            converging_pairs.append({
                'idea_a': idea_a,
                'idea_b': idea_b,
                'recent_meetings': [m[0] for m in recent_meetings_sorted],
                'recent_count': len(recent_meetings),
                'convergence_date': recent_meetings_sorted[0][1] if recent_meetings_sorted else None
            })
    
    # Sort by recent_count descending (most co-occurrences first)
    converging_pairs = sorted(converging_pairs, key=lambda x: -x['recent_count'])
    
    return converging_pairs


def get_external_validations() -> Dict[str, List[Dict]]:
    """
    Get external validation signals for V's ideas.
    
    External validation = when someone OTHER than V (entity_id != 'vrijen')
    supported_by one of V's ideas. This is high-signal: smart people
    agreeing with V's thinking validates the idea's merit.
    
    v1: Just list validators - no credibility scoring yet.
    
    Returns:
        Dict of idea_slug -> list of validations:
        [{
            'validator_id': str,      # person entity_id  
            'validator_name': str,    # person display name
            'validated_at': str,      # date string
            'meeting_context': str,   # meeting ID for context
            'evidence': str           # the quote showing validation
        }]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get supported_by edges where target is a non-V person supporting an idea
    # Edge structure: idea -> supported_by -> person (idea is supported by person)
    cursor.execute("""
        SELECT 
            e.source_id as idea_slug,
            e.target_id as validator_id,
            p.name as validator_name,
            e.context_meeting_id as meeting_context,
            e.evidence,
            e.created_at
        FROM edges e
        LEFT JOIN entities p ON e.target_id = p.entity_id AND p.entity_type = 'person'
        WHERE e.relation = 'supported_by'
          AND e.source_type = 'idea'
          AND e.target_type = 'person'
          AND e.target_id != 'vrijen'
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group by idea_slug
    validations_by_idea = defaultdict(list)
    
    for row in rows:
        idea_slug, validator_id, validator_name, meeting_context, evidence, created_at = row
        
        # Parse date (extract just date portion)
        validated_at = None
        if created_at:
            validated_at = created_at[:10] if len(created_at) >= 10 else created_at
        
        validations_by_idea[idea_slug].append({
            'validator_id': validator_id,
            'validator_name': validator_name or validator_id.replace('-', ' ').title(),
            'validated_at': validated_at,
            'meeting_context': meeting_context,
            'evidence': evidence
        })
    
    # Sort each idea's validations by date (most recent first)
    for idea_slug in validations_by_idea:
        validations_by_idea[idea_slug] = sorted(
            validations_by_idea[idea_slug],
            key=lambda x: x['validated_at'] or '',
            reverse=True
        )
    
    return dict(validations_by_idea)


def generate_resonance_index() -> Dict:
    """Generate the full resonance index with V2 schema."""
    ideas = get_idea_frequencies()
    classified = classify_ideas(ideas)
    
    # Load existing index to preserve V2 computed data if available
    existing = load_resonance_index()
    
    # Compute velocity data
    weekly_mentions = compute_weekly_mentions()
    velocity = compute_velocity(weekly_mentions)
    
    # Compute co-occurrence data (Phase 2)
    co_occurrence = build_co_occurrence_matrix()
    converging = detect_convergence(co_occurrence)
    
    # Compute external validations (Phase 5)
    external_validations = get_external_validations()
    
    index = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "thresholds": THRESHOLDS,
        "total_ideas": len(ideas),
        "summary": {
            "cornerstones": len(classified["cornerstones"]),
            "active_theses": len(classified["active_theses"]),
            "recurring_tools": len(classified["recurring_tools"]),
            "sparks": len(classified["sparks"])
        },
        # V2 structures - computed fresh
        "velocity": velocity,
        "co_occurrence": co_occurrence,
        "converging_pairs": converging,
        "external_validations": external_validations,
        # Classified ideas
        **classified
    }
    
    return index


def save_index(index: Dict) -> Path:
    """Save resonance index to JSON."""
    RESONANCE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(RESONANCE_INDEX, "w") as f:
        json.dump(index, f, indent=2)
    return RESONANCE_INDEX


def generate_report(index: Dict) -> str:
    """Generate human-readable report."""
    lines = []
    lines.append("# Resonance Report")
    lines.append(f"Generated: {index['generated_at']}")
    lines.append(f"Total Ideas Tracked: {index['total_ideas']}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append(f"- **Cornerstones (L0)**: {index['summary']['cornerstones']} ideas (10+ meetings)")
    lines.append(f"- **Active Theses (L1)**: {index['summary']['active_theses']} ideas (4-9 meetings)")
    lines.append(f"- **Recurring Tools (L2)**: {index['summary']['recurring_tools']} ideas (2-3 meetings)")
    lines.append(f"- **Sparks (L3)**: {index['summary']['sparks']} ideas (1 meeting)")
    lines.append("")
    
    # Converging Ideas section - NEW (Phase 2)
    converging = index.get("converging_pairs", [])
    if converging:
        lines.append("## 🔀 Converging Ideas — Cross-Pollination Detected")
        lines.append("Idea pairs that were separate but are now appearing together in meetings.")
        lines.append("")
        
        # Get entity labels for better display
        entity_labels = {}
        for category in ["cornerstones", "active_theses", "recurring_tools", "sparks"]:
            for idea in index.get(category, []):
                entity_labels[idea["idea_slug"]] = idea["label"]
        
        for pair in converging[:10]:
            label_a = entity_labels.get(pair['idea_a'], pair['idea_a'].replace('-', ' ').title())
            label_b = entity_labels.get(pair['idea_b'], pair['idea_b'].replace('-', ' ').title())
            count = pair['recent_count']
            date = pair['convergence_date'] or 'recently'
            lines.append(f"- **{label_a}** ↔ **{label_b}** — {count} shared meeting(s) since {date}")
        lines.append("")
    
    # Rising Ideas section - NEW
    velocity = index.get("velocity", {})
    rising_ideas = []
    for idea_slug, vel_data in velocity.items():
        if vel_data.get("trend") == "rising" and vel_data.get("recent_count", 0) >= 2:
            # Find the full idea data to get label
            idea_data = None
            for category in ["cornerstones", "active_theses", "recurring_tools", "sparks"]:
                for idea in index.get(category, []):
                    if idea["idea_slug"] == idea_slug:
                        idea_data = idea
                        break
                if idea_data:
                    break
            
            if idea_data:
                rising_ideas.append({
                    **idea_data,
                    "recent_count": vel_data["recent_count"],
                    "earlier_count": vel_data["earlier_count"],
                    "recent_weeks": vel_data.get("recent_weeks", [])
                })
    
    # Sort rising ideas by recent_count descending
    rising_ideas = sorted(rising_ideas, key=lambda x: -x["recent_count"])
    
    if rising_ideas:
        lines.append("## 📈 Rising Ideas — Gaining Momentum")
        lines.append("Ideas with increasing mentions in the last 4 weeks vs. the prior 4 weeks.")
        lines.append("")
        for idea in rising_ideas[:10]:
            earlier = idea["earlier_count"]
            recent = idea["recent_count"]
            if earlier > 0:
                ratio = f"{recent/earlier:.1f}x"
            else:
                ratio = "NEW"
            weeks_str = ", ".join(idea.get("recent_weeks", [])[-3:]) or "recent"
            lines.append(f"- **{idea['label']}** — {recent} mentions (was {earlier}, {ratio}) [{weeks_str}]")
        lines.append("")
    
    # External Validation section - NEW (Phase 5)
    external_validations = index.get("external_validations", {})
    if external_validations:
        # Build entity labels lookup
        entity_labels = {}
        for category in ["cornerstones", "active_theses", "recurring_tools", "sparks"]:
            for idea in index.get(category, []):
                entity_labels[idea["idea_slug"]] = idea["label"]
        
        # Flatten validations and sort by count per idea
        ideas_with_validations = []
        for idea_slug, validations in external_validations.items():
            ideas_with_validations.append({
                'idea_slug': idea_slug,
                'label': entity_labels.get(idea_slug, idea_slug.replace('-', ' ').title()),
                'validation_count': len(validations),
                'validators': validations
            })
        
        # Sort by validation count descending
        ideas_with_validations = sorted(ideas_with_validations, key=lambda x: -x['validation_count'])
        
        if ideas_with_validations:
            lines.append("## 🏆 External Validation — Others Who Agree")
            lines.append("Ideas validated by people other than V. High-signal alignment tracking.")
            lines.append("")
            
            for idea_data in ideas_with_validations[:10]:
                lines.append(f"### {idea_data['label']} ({idea_data['validation_count']} validator(s))")
                for v in idea_data['validators'][:3]:  # Show top 3 validators per idea
                    date_str = v['validated_at'] or 'unknown date'
                    meeting_str = f" @ {v['meeting_context']}" if v['meeting_context'] else ""
                    evidence_preview = (v['evidence'][:100] + '...') if v['evidence'] and len(v['evidence']) > 100 else (v['evidence'] or 'No quote captured')
                    lines.append(f"- **{v['validator_name']}** ({date_str}{meeting_str})")
                    lines.append(f"  > \"{evidence_preview}\"")
                lines.append("")
    
    # Under Challenge section - Phase 3 (Challenge Resolution Tracking)
    challenge_status = get_challenge_status()
    pending_challenges = challenge_status.get('challenges', {}).get('pending', [])
    if pending_challenges:
        # Build entity labels lookup for ideas
        entity_labels = {}
        for category in ["cornerstones", "active_theses", "recurring_tools", "sparks"]:
            for idea in index.get(category, []):
                entity_labels[idea["idea_slug"]] = idea["label"]
        
        lines.append("## ⚔️ Under Challenge — Ideas Being Tested")
        lines.append("Ideas that have been questioned or challenged. Unresolved challenges need attention.")
        lines.append("")
        lines.append(f"**Status:** {challenge_status['by_status']['pending']} pending · {challenge_status['by_status']['resolved']} resolved · {challenge_status['by_status']['abandoned']} abandoned")
        lines.append("")
        
        # Show stale challenges first (30+ days)
        stale = challenge_status.get('stale_challenges', [])
        if stale:
            lines.append("### ⚠️ Stale Challenges (30+ days unresolved)")
            for c in stale[:5]:
                idea_label = entity_labels.get(c['entity_id'], c['entity_id'].replace('-', ' ').title())
                challenger = c.get('challenger', 'unknown').replace('-', ' ').title()
                days = c.get('days_unresolved', '?')
                lines.append(f"- **{idea_label}** ← challenged by **{challenger}** ({days} days ago)")
                if c.get('evidence'):
                    evidence_preview = (c['evidence'][:80] + '...') if len(c['evidence']) > 80 else c['evidence']
                    lines.append(f"  > _{evidence_preview}_")
            lines.append("")
        
        # Recent pending challenges
        lines.append("### Pending Challenges")
        # Filter to show non-stale challenges
        stale_ids = {c.get('edge_id') for c in stale}
        recent_pending = [c for c in pending_challenges if c.get('edge_id') not in stale_ids]
        for c in recent_pending[:8]:
            idea_label = entity_labels.get(c['entity_id'], c['entity_id'].replace('-', ' ').title())
            challenger = c.get('challenger', 'unknown').replace('-', ' ').title()
            meeting = c.get('meeting_id', '')
            lines.append(f"- **{idea_label}** ← challenged by **{challenger}**")
            if c.get('evidence'):
                evidence_preview = (c['evidence'][:80] + '...') if len(c['evidence']) > 80 else c['evidence']
                lines.append(f"  > _{evidence_preview}_")
            if meeting:
                lines.append(f"  - Meeting: {meeting}")
        if len(recent_pending) > 8:
            lines.append(f"  - _...and {len(recent_pending) - 8} more_")
        lines.append("")
    
    # Idea Lineage section - Phase 4 (Genealogy)
    ideas_with_lineage = get_ideas_with_lineage()
    potential_duplicates = detect_potential_duplicates()
    
    if ideas_with_lineage or potential_duplicates:
        # Build entity labels lookup for ideas
        entity_labels = {}
        for category in ["cornerstones", "active_theses", "recurring_tools", "sparks"]:
            for idea in index.get(category, []):
                entity_labels[idea["idea_slug"]] = idea["label"]
        
        lines.append("## 🌳 Idea Lineage — Evolution & Heritage")
        lines.append("Ideas that derive from or spawn other ideas, and potential duplicates to consolidate.")
        lines.append("")
        
        # Show ideas with lineage (derives_from relationships)
        if ideas_with_lineage:
            # Separate roots (no ancestors, have descendants) from leaves (have ancestors, no descendants)
            roots = [i for i in ideas_with_lineage if i.get('is_root')]
            leaves = [i for i in ideas_with_lineage if i.get('is_leaf')]
            
            if roots:
                lines.append("### 🌱 Root Ideas (spawned others)")
                for idea in roots[:5]:
                    idea_label = entity_labels.get(idea['idea_id'], idea['idea_id'].replace('-', ' ').title())
                    desc_count = idea.get('descendant_count', 0)
                    lines.append(f"- **{idea_label}** → spawned {desc_count} descendant(s)")
                lines.append("")
            
            if leaves:
                lines.append("### 🍃 Evolved Ideas (derived from others)")
                for idea in leaves[:5]:
                    idea_label = entity_labels.get(idea['idea_id'], idea['idea_id'].replace('-', ' ').title())
                    depth = idea.get('lineage_depth', 0)
                    lines.append(f"- **{idea_label}** — depth {depth} (has {idea.get('ancestor_count', 0)} ancestor(s))")
                lines.append("")
        
        # Show potential duplicates
        if potential_duplicates:
            lines.append("### 🔍 Potential Duplicates (to consolidate)")
            lines.append("These idea pairs have high co-occurrence and similar edge patterns.")
            lines.append("")
            for dup in potential_duplicates[:5]:
                label_a = entity_labels.get(dup['idea_a'], dup['idea_a'].replace('-', ' ').title())
                label_b = entity_labels.get(dup['idea_b'], dup['idea_b'].replace('-', ' ').title())
                confidence = int(dup.get('confidence', 0) * 100)
                shared = dup.get('shared_meetings', 0)
                lines.append(f"- **{label_a}** ≈ **{label_b}** — {confidence}% similar ({shared} shared meetings)")
            lines.append("")
    
    # Cornerstones
    if index["cornerstones"]:
        lines.append("## 🏛️ Cornerstones (L0) — Your Foundational Beliefs")
        lines.append("These are ideas you return to repeatedly. They define your intellectual identity.")
        lines.append("")
        for idea in index["cornerstones"][:15]:
            contexts = ", ".join(idea["sample_contexts"][:3]) if idea["sample_contexts"] else "various"
            lines.append(f"- **{idea['label']}** — {idea['frequency']} meetings ({idea['first_seen']} → {idea['last_seen']})")
        lines.append("")
    
    # Active Theses
    if index["active_theses"]:
        lines.append("## 🔬 Active Theses (L1) — Ideas You're Developing")
        lines.append("These are ideas gaining traction. Watch for evolution or consolidation.")
        lines.append("")
        for idea in index["active_theses"][:15]:
            lines.append(f"- **{idea['label']}** — {idea['frequency']} meetings ({idea['first_seen']} → {idea['last_seen']})")
        lines.append("")
    
    # Recurring Tools
    if index["recurring_tools"]:
        lines.append("## 🔧 Recurring Tools (L2) — Frameworks You Reach For")
        lines.append("These are mental models you apply. Note when they appear in new domains.")
        lines.append("")
        for idea in index["recurring_tools"][:15]:
            lines.append(f"- **{idea['label']}** — {idea['frequency']} meetings")
        lines.append("")
    
    # Recent Sparks (only last 20)
    if index["sparks"]:
        lines.append("## ✨ Recent Sparks (L3) — Novel Ideas")
        lines.append("These appeared once. Candidates for exploration or naturally fleeting.")
        lines.append("")
        # Sort sparks by last_seen descending to show most recent
        recent_sparks = sorted(index["sparks"], key=lambda x: x["last_seen"] or "", reverse=True)[:20]
        for idea in recent_sparks:
            lines.append(f"- **{idea['label']}** — {idea['last_seen'] or 'unknown'}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pattern Surfacer for Resonance Reservoir")
    parser.add_argument("command", choices=["generate", "report", "stats", "json"],
                       help="Command to run")
    parser.add_argument("--output", "-o", help="Output file for report")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        index = generate_resonance_index()
        path = save_index(index)
        print(json.dumps({
            "status": "generated",
            "path": str(path),
            "summary": index["summary"],
            "total_ideas": index["total_ideas"]
        }, indent=2))
        
    elif args.command == "report":
        index = generate_resonance_index()
        save_index(index)  # Also save the index
        report = generate_report(index)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(report)
            print(f"Report saved to: {output_path}")
        else:
            print(report)
            
    elif args.command == "stats":
        index = generate_resonance_index()
        print(json.dumps({
            "total_ideas": index["total_ideas"],
            **index["summary"]
        }, indent=2))
        
    elif args.command == "json":
        index = generate_resonance_index()
        print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()












