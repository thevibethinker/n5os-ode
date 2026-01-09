#!/usr/bin/env python3
"""
Voice Learner - Analyze selections and refine voice configurations

Learns from:
1. Variant selection patterns (variant_preferences)
2. Refinement feedback (approval_queue.refinement_suggestion)
3. Posted tweet performance (posted_tweets)
4. V's historical voice (voice_samples from archive)
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

PROJECT_DIR = "/home/workspace/Projects/x-thought-leader"
TWEETS_DB = f"{PROJECT_DIR}/db/tweets.db"
VOICE_CONFIG = f"{PROJECT_DIR}/config/voice_variants.yaml"
LEARNING_LOG = f"{PROJECT_DIR}/config/learning_log.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("voice_learner")

VARIANTS = ['supportive', 'challenging', 'spicy', 'comedic']


def get_selection_stats(days: int = 30) -> dict:
    """Get variant selection statistics from approval history."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    stats = {
        'period_days': days,
        'total_selections': 0,
        'by_variant': {v: 0 for v in VARIANTS},
        'percentages': {v: 0.0 for v in VARIANTS},
        'feedback_count': 0,
        'feedback_samples': []
    }
    
    # Try variant_preferences table first
    try:
        rows = conn.execute("""
            SELECT selected_variant, context_category, feedback, timestamp
            FROM variant_preferences
            WHERE timestamp > ?
        """, (cutoff,)).fetchall()
        
        for row in rows:
            variant = row['selected_variant']
            feedback = row['feedback']
            
            stats['total_selections'] += 1
            if variant in stats['by_variant']:
                stats['by_variant'][variant] += 1
            
            if feedback:
                stats['feedback_count'] += 1
                stats['feedback_samples'].append({
                    'variant': variant,
                    'feedback': feedback,
                    'context': row['context_category']
                })
    except sqlite3.OperationalError:
        logger.warning("variant_preferences table not found or empty")
    
    # Also check approval_queue for selections
    try:
        rows = conn.execute("""
            SELECT selected_variant, refinement_suggestion
            FROM approval_queue
            WHERE status = 'APPROVED'
            AND approved_at > ?
        """, (cutoff,)).fetchall()
        
        for row in rows:
            variant = row['selected_variant']
            feedback = row['refinement_suggestion']
            
            if variant:
                stats['total_selections'] += 1
                if variant in stats['by_variant']:
                    stats['by_variant'][variant] += 1
                
                if feedback:
                    stats['feedback_count'] += 1
                    stats['feedback_samples'].append({
                        'variant': variant,
                        'feedback': feedback,
                        'context': 'approval_queue'
                    })
    except sqlite3.OperationalError:
        pass
    
    conn.close()
    
    # Calculate percentages
    total = stats['total_selections']
    if total > 0:
        stats['percentages'] = {
            v: round(c / total * 100, 1) 
            for v, c in stats['by_variant'].items()
        }
    
    return stats


def get_posted_performance(days: int = 30) -> dict:
    """Analyze performance of posted tweets by variant."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    stats = {
        'period_days': days,
        'total_posted': 0,
        'by_variant': {v: {'count': 0, 'total_engagement': 0, 'avg_engagement': 0} for v in VARIANTS},
        'top_performers': []
    }
    
    try:
        rows = conn.execute("""
            SELECT variant_used, engagement_metrics, our_content, position_ids, posted_at
            FROM posted_tweets
            WHERE posted_at > ?
            ORDER BY posted_at DESC
        """, (cutoff,)).fetchall()
        
        for row in rows:
            variant = row['variant_used']
            metrics = json.loads(row['engagement_metrics']) if row['engagement_metrics'] else {}
            
            # Calculate engagement score
            engagement_score = (
                metrics.get('like_count', 0) + 
                metrics.get('reply_count', 0) * 2 +
                metrics.get('retweet_count', 0) * 3
            )
            
            stats['total_posted'] += 1
            if variant in stats['by_variant']:
                stats['by_variant'][variant]['count'] += 1
                stats['by_variant'][variant]['total_engagement'] += engagement_score
            
            if engagement_score > 0:
                stats['top_performers'].append({
                    'variant': variant,
                    'engagement': engagement_score,
                    'content': row['our_content'][:80] if row['our_content'] else '',
                    'posted_at': row['posted_at']
                })
        
        # Calculate averages
        for v in VARIANTS:
            data = stats['by_variant'][v]
            if data['count'] > 0:
                data['avg_engagement'] = round(data['total_engagement'] / data['count'], 1)
        
        # Sort top performers
        stats['top_performers'].sort(key=lambda x: -x['engagement'])
        stats['top_performers'] = stats['top_performers'][:10]
        
    except sqlite3.OperationalError as e:
        logger.warning(f"Error reading posted_tweets: {e}")
    
    conn.close()
    return stats


def analyze_voice_samples() -> dict:
    """Analyze V's historical tweets for voice patterns."""
    conn = sqlite3.connect(TWEETS_DB)
    conn.row_factory = sqlite3.Row
    
    patterns = {
        'sample_count': 0,
        'high_engagement_count': 0,
        'avg_length': 0,
        'high_engagement_avg_length': 0,
        'common_openers': [],
        'common_closers': [],
        'emoji_usage': 0
    }
    
    try:
        rows = conn.execute("""
            SELECT content, engagement_metrics
            FROM voice_samples
        """).fetchall()
        
        if not rows:
            conn.close()
            return patterns
        
        patterns['sample_count'] = len(rows)
        
        # Calculate metrics
        total_length = 0
        high_engagement = []
        emoji_count = 0
        openers = defaultdict(int)
        closers = defaultdict(int)
        
        for row in rows:
            content = row['content'] or ''
            # Parse engagement from JSON metrics if available
            metrics = json.loads(row['engagement_metrics']) if row['engagement_metrics'] else {}
            score = metrics.get('like_count', 0) + metrics.get('retweet_count', 0) * 2
            
            total_length += len(content)
            
            # Count emojis (simple heuristic)
            emoji_count += sum(1 for c in content if ord(c) > 127462)
            
            if score > 0.3:
                high_engagement.append(content)
            
            # Extract openers (first 3 words)
            words = content.split()[:3]
            if words:
                openers[' '.join(words)] += 1
            
            # Extract closers (last 3 words)
            words = content.split()[-3:]
            if words:
                closers[' '.join(words)] += 1
        
        patterns['avg_length'] = round(total_length / len(rows)) if rows else 0
        patterns['high_engagement_count'] = len(high_engagement)
        patterns['high_engagement_avg_length'] = round(
            sum(len(t) for t in high_engagement) / len(high_engagement)
        ) if high_engagement else 0
        patterns['emoji_usage'] = round(emoji_count / len(rows), 2) if rows else 0
        
        # Top openers/closers
        patterns['common_openers'] = sorted(openers.items(), key=lambda x: -x[1])[:5]
        patterns['common_closers'] = sorted(closers.items(), key=lambda x: -x[1])[:5]
        
    except sqlite3.OperationalError as e:
        logger.warning(f"Error reading voice_samples: {e}")
    
    conn.close()
    return patterns


def generate_recommendations(selection_stats: dict, performance_stats: dict, voice_patterns: dict) -> list:
    """Generate actionable voice refinement recommendations."""
    recommendations = []
    
    total = selection_stats['total_selections']
    
    # Check variant balance
    if total >= 10:
        for variant, pct in selection_stats['percentages'].items():
            if pct < 10:
                recommendations.append({
                    'priority': 'medium',
                    'type': 'variant_underused',
                    'variant': variant,
                    'metric': f"{pct:.0f}%",
                    'suggestion': f"'{variant}' only selected {pct:.0f}% of time. Consider making it more distinctive or providing better examples."
                })
            elif pct > 55:
                recommendations.append({
                    'priority': 'low',
                    'type': 'variant_dominant',
                    'variant': variant,
                    'metric': f"{pct:.0f}%",
                    'suggestion': f"'{variant}' dominates at {pct:.0f}%. This may be fine if it matches your voice, or consider diversifying."
                })
    
    # Feedback pattern analysis
    feedback_by_variant = defaultdict(list)
    for sample in selection_stats.get('feedback_samples', []):
        if sample.get('feedback'):
            feedback_by_variant[sample['variant']].append(sample['feedback'].lower())
    
    common_requests = {
        'edgier': ['edgier', 'more edge', 'sharper', 'bolder', 'spicier'],
        'softer': ['softer', 'gentler', 'less aggressive', 'tone down'],
        'shorter': ['shorter', 'more concise', 'trim', 'cut'],
        'funnier': ['funnier', 'more humor', 'wittier', 'more wit']
    }
    
    for variant, feedbacks in feedback_by_variant.items():
        for request_type, keywords in common_requests.items():
            matches = sum(1 for f in feedbacks if any(k in f for k in keywords))
            if matches >= 2:
                recommendations.append({
                    'priority': 'high',
                    'type': 'feedback_pattern',
                    'variant': variant,
                    'metric': f"{matches} requests for '{request_type}'",
                    'suggestion': f"'{variant}' frequently gets '{request_type}' feedback. Update the variant prompt/examples."
                })
    
    # Performance insights
    if performance_stats['total_posted'] >= 5:
        best_variant = max(
            performance_stats['by_variant'].items(),
            key=lambda x: x[1]['avg_engagement']
        )
        if best_variant[1]['avg_engagement'] > 5:
            recommendations.append({
                'priority': 'info',
                'type': 'top_performer',
                'variant': best_variant[0],
                'metric': f"{best_variant[1]['avg_engagement']:.1f} avg engagement",
                'suggestion': f"'{best_variant[0]}' has highest engagement. Study what makes these resonate."
            })
    
    # Voice sample insights
    if voice_patterns['sample_count'] >= 20:
        if voice_patterns['high_engagement_avg_length'] > 0:
            recommendations.append({
                'priority': 'info',
                'type': 'length_insight',
                'variant': 'all',
                'metric': f"{voice_patterns['high_engagement_avg_length']} chars",
                'suggestion': f"Your high-engagement tweets average {voice_patterns['high_engagement_avg_length']} chars. Consider this when drafting."
            })
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2, 'info': 3}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))
    
    return recommendations


def log_learning_cycle(stats: dict, recommendations: list):
    """Append learning cycle to log for historical tracking."""
    Path(LEARNING_LOG).parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'total_selections': stats.get('total_selections', 0),
        'variant_distribution': stats.get('percentages', {}),
        'recommendation_count': len(recommendations),
        'top_recommendations': [r['suggestion'] for r in recommendations[:3]]
    }
    
    with open(LEARNING_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    logger.info(f"Logged learning cycle to {LEARNING_LOG}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Voice Learning & Refinement")
    parser.add_argument("command", choices=['stats', 'performance', 'analyze', 'recommend', 'report'])
    parser.add_argument("--days", type=int, default=30, help="Days to analyze")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    if args.command == 'stats':
        stats = get_selection_stats(args.days)
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"\n=== Selection Stats (last {args.days} days) ===")
            print(f"Total selections: {stats['total_selections']}")
            print(f"\nBy variant:")
            for v in VARIANTS:
                c = stats['by_variant'].get(v, 0)
                pct = stats['percentages'].get(v, 0)
                bar = '█' * int(pct / 5) if pct > 0 else ''
                print(f"  {v:12}: {c:3} ({pct:5.1f}%) {bar}")
            print(f"\nFeedback received: {stats['feedback_count']}")
            if stats['feedback_samples']:
                print("\nRecent feedback:")
                for fb in stats['feedback_samples'][:3]:
                    print(f"  [{fb['variant']}] {fb['feedback']}")
    
    elif args.command == 'performance':
        perf = get_posted_performance(args.days)
        if args.json:
            print(json.dumps(perf, indent=2))
        else:
            print(f"\n=== Posted Performance (last {args.days} days) ===")
            print(f"Total posted: {perf['total_posted']}")
            print(f"\nBy variant:")
            for v in VARIANTS:
                data = perf['by_variant'].get(v, {'count': 0, 'avg_engagement': 0})
                print(f"  {v:12}: {data['count']:3} posts, {data['avg_engagement']:5.1f} avg engagement")
            if perf['top_performers']:
                print(f"\nTop performers:")
                for tp in perf['top_performers'][:5]:
                    print(f"  [{tp['variant']}] {tp['engagement']} eng: {tp['content'][:50]}...")
    
    elif args.command == 'analyze':
        patterns = analyze_voice_samples()
        if args.json:
            print(json.dumps(patterns, indent=2, default=str))
        else:
            print(f"\n=== Voice Sample Analysis ===")
            print(f"Total samples: {patterns['sample_count']}")
            print(f"High engagement: {patterns['high_engagement_count']}")
            print(f"Avg length: {patterns['avg_length']} chars")
            print(f"High-engagement avg: {patterns['high_engagement_avg_length']} chars")
            print(f"Emoji usage: {patterns['emoji_usage']} per tweet")
            if patterns['common_openers']:
                print(f"\nCommon openers:")
                for opener, count in patterns['common_openers'][:3]:
                    print(f"  \"{opener}...\" ({count}x)")
    
    elif args.command == 'recommend':
        selection_stats = get_selection_stats(args.days)
        performance_stats = get_posted_performance(args.days)
        voice_patterns = analyze_voice_samples()
        recs = generate_recommendations(selection_stats, performance_stats, voice_patterns)
        
        if args.json:
            print(json.dumps(recs, indent=2))
        else:
            print(f"\n=== Recommendations ===")
            if not recs:
                print("No recommendations yet. Need more data (10+ selections).")
            for i, rec in enumerate(recs, 1):
                print(f"\n{i}. [{rec['priority'].upper()}] {rec['type']}")
                if rec.get('variant') != 'all':
                    print(f"   Variant: {rec.get('variant', '-')}")
                print(f"   Metric: {rec['metric']}")
                print(f"   → {rec['suggestion']}")
    
    elif args.command == 'report':
        selection_stats = get_selection_stats(args.days)
        performance_stats = get_posted_performance(args.days)
        voice_patterns = analyze_voice_samples()
        recs = generate_recommendations(selection_stats, performance_stats, voice_patterns)
        
        log_learning_cycle(selection_stats, recs)
        
        report = {
            'generated': datetime.now().isoformat(),
            'period_days': args.days,
            'selection_stats': selection_stats,
            'performance_stats': performance_stats,
            'voice_patterns': voice_patterns,
            'recommendations': recs
        }
        
        report_path = f"{PROJECT_DIR}/docs/voice_report_{datetime.now().strftime('%Y%m%d')}.json"
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report saved to: {report_path}")
        if args.json:
            print(json.dumps(report, indent=2, default=str))
        else:
            print(f"\nSummary:")
            print(f"  Selections: {selection_stats['total_selections']}")
            print(f"  Posted: {performance_stats['total_posted']}")
            print(f"  Voice samples: {voice_patterns['sample_count']}")
            print(f"  Recommendations: {len(recs)}")


if __name__ == "__main__":
    main()




