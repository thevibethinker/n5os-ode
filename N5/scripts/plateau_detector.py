#!/usr/bin/env python3
"""
Plateau Detector - Detect when Drops are stuck making repeated similar attempts without progress.

Part of Watts Principles: Quality gate that detects spinning/stagnation and suggests
tooling changes instead of blind retries.

Usage:
    python3 plateau_detector.py check <slug> <drop_id>
    python3 plateau_detector.py analyze <slug>
    python3 plateau_detector.py scan
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Paths
BUILDS_DIR = Path("/home/workspace/N5/builds")


class PlateauDetector:
    """Detects when a Drop is stuck in a spinning pattern without progress."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize detector with sentence transformer model."""
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get sentence embedding for text."""
        return self.model.encode(text)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        import numpy as np
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def load_drop_logs(self, slug: str, drop_id: str) -> List[str]:
        """Load log entries for a Drop from conversations.db."""
        import sqlite3
        
        convos_db = Path("/home/workspace/N5/data/conversations.db")
        if not convos_db.exists():
            return []
        
        try:
            conn = sqlite3.connect(convos_db)
            cursor = conn.cursor()
            
            # Get log entries for this drop
            cursor.execute("""
                SELECT message_content 
                FROM messages 
                WHERE conversation_id IN (
                    SELECT id FROM conversations WHERE drop_id = ? AND build_slug = ?
                )
                ORDER BY created_at DESC
                LIMIT 50
            """, (drop_id, slug))
            
            entries = [row[0] for row in cursor.fetchall() if row[0]]
            conn.close()
            return entries
        except Exception as e:
            return []
    
    def load_deposit_history(self, slug: str, drop_id: str) -> List[Dict]:
        """Load deposit attempts for a Drop."""
        deposits_dir = BUILDS_DIR / slug / "deposits"
        if not deposits_dir.exists():
            return []
        
        # Look for deposit files and any partial/resubmit versions
        deposit_files = []
        for f in deposits_dir.glob(f"{drop_id}*.json"):
            deposit_files.append(f)
        
        history = []
        for f in sorted(deposit_files):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                history.append({
                    "path": str(f),
                    "timestamp": data.get("timestamp", ""),
                    "status": data.get("status", ""),
                    "summary": data.get("summary", ""),
                    "artifacts": data.get("artifacts", [])
                })
            except:
                continue
        
        return history
    
    def analyze_log_patterns(self, logs: List[str]) -> Dict:
        """Analyze log entries for repetition patterns."""
        if len(logs) < 3:
            return {"has_repetition": False, "reason": "Not enough log entries"}
        
        # Extract task descriptions and outcomes
        task_entries = []
        for log in logs:
            # Look for patterns like "Trying X", "Attempt Y", "Doing Z"
            if any(word in log.lower() for word in ["trying", "attempt", "attempting", "testing", "checking"]):
                task_entries.append(log)
        
        if len(task_entries) < 2:
            return {"has_repetition": False, "reason": "No clear task entries found"}
        
        # Check for similarity among recent tasks
        recent_tasks = task_entries[:10]
        similarities = []
        
        for i in range(len(recent_tasks) - 1):
            sim = self.compute_similarity(recent_tasks[i], recent_tasks[i + 1])
            similarities.append(sim)
        
        # High similarity indicates spinning
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        is_spinning = avg_similarity > 0.85
        
        return {
            "has_repetition": is_spinning,
            "average_similarity": avg_similarity,
            "task_count": len(task_entries),
            "analyzed_pairs": len(similarities)
        }
    
    def analyze_deposit_progression(self, history: List[Dict]) -> Dict:
        """Analyze deposit submissions for progress or stagnation."""
        if len(history) < 2:
            return {"has_progress": True, "reason": "First submission"}
        
        # Compare consecutive deposits
        comparisons = []
        for i in range(len(history) - 1):
            current = history[i]
            next_dep = history[i + 1]
            
            # Check if summaries are very similar
            if current["summary"] and next_dep["summary"]:
                sim = self.compute_similarity(current["summary"], next_dep["summary"])
                comparisons.append(sim)
        
        if not comparisons:
            return {"has_progress": True, "reason": "Cannot compare summaries"}
        
        # High similarity = no meaningful progress
        avg_sim = sum(comparisons) / len(comparisons)
        has_progress = avg_sim < 0.90
        
        return {
            "has_progress": has_progress,
            "average_similarity": avg_sim,
            "comparisons": len(comparisons)
        }
    
    def detect_signals(self, slug: str, drop_id: str) -> List[str]:
        """Collect all plateau signals."""
        signals = []
        
        # Check logs
        logs = self.load_drop_logs(slug, drop_id)
        log_analysis = self.analyze_log_patterns(logs)
        
        if log_analysis.get("has_repetition"):
            signals.append(f"Spinning in task attempts (avg similarity: {log_analysis.get('average_similarity', 0):.2f})")
        
        # Check deposits
        history = self.load_deposit_history(slug, drop_id)
        dep_analysis = self.analyze_deposit_progression(history)
        
        if not dep_analysis.get("has_progress"):
            signals.append(f"No meaningful progress in submissions (avg similarity: {dep_analysis.get('average_similarity', 0):.2f})")
        
        # Check for error loops
        error_patterns = []
        for log in logs:
            # Look for repeated error patterns
            if any(word in log.lower() for word in ["error", "failed", "exception"]):
                # Extract error message
                error_match = re.search(r'(error|failed|exception)[:100]', log, re.IGNORECASE)
                if error_match:
                    error_patterns.append(error_match.group().lower())
        
        # Count unique errors
        unique_errors = set(error_patterns)
        if len(error_patterns) > 5 and len(unique_errors) < 3:
            signals.append(f"Error loop: {len(error_patterns)} errors, only {len(unique_errors)} unique")
        
        return signals
    
    def get_tooling_suggestions(self, signals: List[str]) -> List[str]:
        """Suggest tooling changes based on detected signals."""
        suggestions = []
        
        # Check for spinning in task attempts
        if any("spinning" in s.lower() or "similarity" in s.lower() for s in signals):
            suggestions.append("Add instrumentation/logging to identify bottleneck")
            suggestions.append("Try different algorithm or library approach")
            suggestions.append("Expand search space or adjust parameters")
        
        # Check for error loops
        if any("error loop" in s.lower() for s in signals):
            suggestions.append("Review error logs for root cause (not just symptoms)")
            suggestions.append("Try alternative library or API method")
        
        # Check for no progress
        if any("no meaningful progress" in s.lower() for s in signals):
            suggestions.append("Reframe the problem or approach")
            suggestions.append("Consider if task is achievable as specified")
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Add debug logging to understand where stuck",
                "Try a different approach to the subtask",
                "Break down task into smaller chunks"
            ]
        
        return suggestions
    
    def check_drop_plateau(self, slug: str, drop_id: str, min_signals: int = 2) -> Dict:
        """
        Check if a Drop has plateaued.
        
        Args:
            slug: Build slug
            drop_id: Drop ID
            min_signals: Minimum number of signals to consider plateaued
        
        Returns:
            {
                "is_plateau": bool,
                "signals": [...],
                "tool_suggestions": [...]
            }
        """
        signals = self.detect_signals(slug, drop_id)
        
        return {
            "is_plateau": len(signals) >= min_signals,
            "signals": signals,
            "signal_count": len(signals),
            "tool_suggestions": self.get_tooling_suggestions(signals)
        }


def check_drop_plateau(slug: str, drop_id: str) -> Dict:
    """
    Integration function: Check if a Drop has plateaued.
    
    Returns same structure as PlateauDetector.check_drop_plateau().
    """
    try:
        detector = PlateauDetector()
        return detector.check_drop_plateau(slug, drop_id)
    except Exception as e:
        return {
            "is_plateau": False,
            "signals": [],
            "error": str(e),
            "tool_suggestions": ["Error checking plateau: enable instrumentation"]
        }


def cmd_check(args):
    """Handle 'check' command."""
    result = check_drop_plateau(args.slug, args.drop_id)
    
    print("=" * 60)
    print(f"PLATEAU CHECK: {args.slug}/{args.drop_id}")
    print("=" * 60)
    print()
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return
    
    if result["is_plateau"]:
        print("🔴 PLATEAU DETECTED")
        print()
        print(f"Signals ({result['signal_count']}):")
        for signal in result["signals"]:
            print(f"  - {signal}")
        print()
        print("Suggested tooling changes:")
        for suggestion in result["tool_suggestions"]:
            print(f"  - {suggestion}")
    else:
        print("✅ No plateau detected")
        if result.get("signals"):
            print()
            print(f"Minor signals: {result['signals']}")


def cmd_analyze(args):
    """Handle 'analyze' command for entire build."""
    build_dir = BUILDS_DIR / args.slug
    meta_file = build_dir / "meta.json"
    
    if not meta_file.exists():
        print(f"Error: Build {args.slug} not found")
        sys.exit(1)
    
    with open(meta_file) as f:
        meta = json.load(f)
    
    drops = meta.get("drops", {})
    print("=" * 60)
    print(f"PLATEAU ANALYSIS: {args.slug}")
    print("=" * 60)
    print()
    
    detector = PlateauDetector()
    plateaued_drops = []
    
    for drop_id, info in drops.items():
        if info.get("status") == "running":
            result = detector.check_drop_plateau(args.slug, drop_id)
            if result["is_plateau"]:
                plateaued_drops.append((drop_id, result))
    
    if plateaued_drops:
        print(f"Found {len(plateaued_drops)} plateaued Drop(s):")
        print()
        for drop_id, result in plateaued_drops:
            print(f"  {drop_id}:")
            for signal in result["signals"][:2]:
                print(f"    - {signal}")
            print()
    else:
        print("✅ No plateaued Drops found")


def main():
    parser = argparse.ArgumentParser(
        description="Detect when Drops are stuck without progress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check watts-principles D2.1
  %(prog)s analyze watts-principles

Exit Codes:
  0: No plateau detected
  1: Plateau detected
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if a Drop has plateaued")
    check_parser.add_argument("slug", help="Build slug")
    check_parser.add_argument("drop_id", help="Drop ID")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze entire build for plateaued Drops")
    analyze_parser.add_argument("slug", help="Build slug")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "check":
        cmd_check(args)
        sys.exit(0 if not check_drop_plateau(args.slug, args.drop_id)["is_plateau"] else 1)
    elif args.command == "analyze":
        cmd_analyze(args)


if __name__ == "__main__":
    main()
