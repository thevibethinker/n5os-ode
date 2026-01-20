#!/usr/bin/env python3
"""
Struggle Detector - Detect when an agent is spinning without progress

From Ralph methodology: Identify struggle patterns that indicate when to
intervene or restart with fresh context.

Usage:
    # Check conversation
    python3 struggle_detector.py --convo-id con_abc123

    # Check build
    python3 struggle_detector.py --build-slug ralph-learnings

    # JSON output
    python3 struggle_detector.py --convo-id con_abc123 --json

    # Verbose with evidence
    python3 struggle_detector.py --convo-id con_abc123 --verbose

Patterns Detected:
    1. Circular errors - Same error appears 3+ times
    2. Stalled progress - Same % for 5+ updates
    3. Revert cycles - Apply-revert-apply in git
    4. Repeated hypotheses - Same fix tried 3+ times
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Dict, Optional, Any

import yaml
sys.path.insert(0, "/home/workspace")
from N5.lib.paths import N5_CONFIG_DIR, N5_BUILDS_DIR


@dataclass
class PatternEvidence:
    """Evidence for a detected struggle pattern."""
    type: str
    count: int
    evidence: str
    severity: str
    entries: List[str] = field(default_factory=list)


@dataclass
class StruggleResult:
    """Result of struggle detection analysis."""
    status: str  # HEALTHY, STRUGGLING, STUCK
    patterns_detected: List[PatternEvidence]
    recommendation: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "patterns_detected": [asdict(p) for p in self.patterns_detected],
            "recommendation": self.recommendation,
            "context": self.context
        }


class StruggleDetector:
    """Detect agent struggle patterns."""
    
    CONFIG_PATH = N5_CONFIG_DIR / "struggle_patterns.yaml"
    BUILDS_BASE = N5_BUILDS_DIR
    
    def __init__(self, convo_id: str = None, build_slug: str = None):
        self.convo_id = convo_id
        self.build_slug = build_slug
        self.config = self._load_config()
        
        # Set up paths based on input
        if convo_id:
            self.workspace = self.WORKSPACE_BASE / convo_id
            self.debug_log = self.workspace / "DEBUG_LOG.jsonl"
            self.session_state = self.workspace / "SESSION_STATE.md"
        elif build_slug:
            self.build_dir = self.BUILDS_BASE / build_slug
            # For builds, we check the build meta and any associated conversation
            self.workspace = None
            self.debug_log = None
            self.session_state = None
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        if not self.CONFIG_PATH.exists():
            # Return sensible defaults if config missing
            return {
                "thresholds": {
                    "circular_error": {"min_repetitions": 3, "window_minutes": 30, "severity": "STRUGGLING"},
                    "stalled_progress": {"unchanged_updates": 5, "severity": "STUCK"},
                    "revert_cycles": {"min_cycles": 2, "look_back_commits": 20, "severity": "STRUGGLING"},
                    "repeated_hypothesis": {"min_repetitions": 3, "similarity_threshold": 0.7, "window_entries": 15, "severity": "STRUGGLING"}
                },
                "recommendations": {
                    "HEALTHY": "Continue",
                    "STRUGGLING": "Intervene - consider switching approach or adding context",
                    "STUCK": "Fresh start - agent likely needs reset with new context"
                }
            }
        
        with open(self.CONFIG_PATH) as f:
            return yaml.safe_load(f)
    
    def detect(self, verbose: bool = False) -> StruggleResult:
        """Run all struggle pattern detections."""
        patterns: List[PatternEvidence] = []
        context = {
            "convo_id": self.convo_id,
            "build_slug": self.build_slug,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Run detections
        if self.convo_id:
            # Conversation-based detection
            circular = self._detect_circular_errors(verbose)
            if circular:
                patterns.append(circular)
            
            stalled = self._detect_stalled_progress(verbose)
            if stalled:
                patterns.append(stalled)
            
            repeated = self._detect_repeated_hypotheses(verbose)
            if repeated:
                patterns.append(repeated)
            
            revert = self._detect_revert_cycles(verbose)
            if revert:
                patterns.append(revert)
        
        elif self.build_slug:
            # Build-based detection - check build meta and associated conversations
            revert = self._detect_revert_cycles(verbose)
            if revert:
                patterns.append(revert)
            
            # Check all worker conversations for struggles
            worker_struggles = self._check_build_workers(verbose)
            if worker_struggles:
                context["worker_struggles"] = worker_struggles
        
        # Determine overall status
        status = self._determine_status(patterns)
        recommendation = self.config.get("recommendations", {}).get(
            status, 
            "Unknown status - review manually"
        )
        
        return StruggleResult(
            status=status,
            patterns_detected=patterns,
            recommendation=recommendation,
            context=context
        )
    
    def _determine_status(self, patterns: List[PatternEvidence]) -> str:
        """Determine overall status based on detected patterns."""
        if not patterns:
            return "HEALTHY"
        
        # Check for any STUCK-severity patterns
        for p in patterns:
            if p.severity == "STUCK":
                return "STUCK"
        
        # Check pattern count
        if len(patterns) >= 3:
            return "STUCK"
        elif len(patterns) >= 1:
            return "STRUGGLING"
        
        return "HEALTHY"
    
    def _detect_circular_errors(self, verbose: bool) -> Optional[PatternEvidence]:
        """Detect same error appearing multiple times."""
        if not self.debug_log or not self.debug_log.exists():
            return None
        
        config = self.config["thresholds"]["circular_error"]
        min_reps = config["min_repetitions"]
        window_mins = config["window_minutes"]
        severity = config["severity"]
        
        # Read debug log
        entries = self._read_debug_log()
        if len(entries) < min_reps:
            return None
        
        # Filter to recent window
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_mins)
        recent = []
        for e in entries:
            try:
                ts = datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))
                if ts >= cutoff:
                    recent.append(e)
            except (KeyError, ValueError):
                recent.append(e)  # Include if can't parse timestamp
        
        if len(recent) < min_reps:
            return None
        
        # Group by similar problems (component + problem text)
        clusters = self._cluster_by_similarity(
            recent, 
            key_fields=["component", "problem"],
            threshold=0.7
        )
        
        # Find clusters meeting threshold (failures only)
        for cluster in clusters:
            failures = [e for e in cluster if e.get("outcome") != "success"]
            if len(failures) >= min_reps:
                sample = failures[0]
                entry_ids = [e.get("entry_id", "?") for e in failures]
                evidence = f"Error in {sample['component']}: '{sample['problem'][:60]}...' appeared {len(failures)} times"
                
                return PatternEvidence(
                    type="circular_error",
                    count=len(failures),
                    evidence=evidence,
                    severity=severity,
                    entries=entry_ids[:5]  # Limit to first 5
                )
        
        return None
    
    def _detect_stalled_progress(self, verbose: bool) -> Optional[PatternEvidence]:
        """Detect progress percentage stuck at same value."""
        if not self.session_state or not self.session_state.exists():
            return None
        
        config = self.config["thresholds"]["stalled_progress"]
        unchanged_threshold = config["unchanged_updates"]
        severity = config["severity"]
        
        content = self.session_state.read_text()
        
        # Extract current progress
        progress_match = re.search(r"\*\*Overall:\*\*\s*(\d+)%", content)
        if not progress_match:
            return None
        
        current_progress = int(progress_match.group(1))
        
        # Check git history of SESSION_STATE.md for progress changes
        # This is a heuristic - we look for the last_updated timestamps
        # and compare progress values
        
        # Alternative: count recent "Update" lines in Covered section
        # that don't show progress change
        covered_match = re.search(r"## Covered\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if covered_match:
            covered_lines = covered_match.group(1).strip().split("\n")
            recent_lines = [l for l in covered_lines[-10:] if l.strip().startswith("-")]
            
            # If progress is 0% and we have activity, that's a signal
            if current_progress == 0 and len(recent_lines) > unchanged_threshold:
                return PatternEvidence(
                    type="stalled_progress",
                    count=len(recent_lines),
                    evidence=f"Progress stuck at {current_progress}% despite {len(recent_lines)} logged activities",
                    severity=severity,
                    entries=[]
                )
        
        # If progress is very low and session has been updated multiple times
        last_updated_count = content.count("last_updated:")
        if current_progress < 10 and last_updated_count > unchanged_threshold:
            return PatternEvidence(
                type="stalled_progress",
                count=last_updated_count,
                evidence=f"Progress at {current_progress}% after {last_updated_count} state updates",
                severity=severity,
                entries=[]
            )
        
        return None
    
    def _detect_revert_cycles(self, verbose: bool) -> Optional[PatternEvidence]:
        """Detect apply-revert-apply patterns in git history."""
        config = self.config["thresholds"]["revert_cycles"]
        min_cycles = config["min_cycles"]
        look_back = config.get("look_back_commits", 20)
        severity = config["severity"]
        
        # Run git log to get recent commits
        try:
            result = subprocess.run(
                ["git", "log", f"-{look_back}", "--oneline", "--all"],
                capture_output=True,
                text=True,
                cwd="/home/workspace",
                timeout=10
            )
            if result.returncode != 0:
                return None
            
            commits = result.stdout.strip().split("\n")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
        
        # Look for revert patterns
        revert_pattern = re.compile(r"revert", re.IGNORECASE)
        revert_commits = [c for c in commits if revert_pattern.search(c)]
        
        if len(revert_commits) >= min_cycles:
            return PatternEvidence(
                type="revert_cycles",
                count=len(revert_commits),
                evidence=f"Found {len(revert_commits)} revert commits in last {look_back} commits",
                severity=severity,
                entries=revert_commits[:5]
            )
        
        # Also check for repeated file modifications (same file changed multiple times)
        try:
            result = subprocess.run(
                ["git", "log", f"-{look_back}", "--name-only", "--pretty=format:"],
                capture_output=True,
                text=True,
                cwd="/home/workspace",
                timeout=10
            )
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                file_counts = {}
                for f in files:
                    file_counts[f] = file_counts.get(f, 0) + 1
                
                # Flag files modified 5+ times in the window
                hot_files = [(f, c) for f, c in file_counts.items() if c >= 5]
                if hot_files:
                    # This could indicate churn, but not necessarily reverts
                    # Only flag if combined with other patterns
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def _detect_repeated_hypotheses(self, verbose: bool) -> Optional[PatternEvidence]:
        """Detect same hypothesis being tried multiple times."""
        if not self.debug_log or not self.debug_log.exists():
            return None
        
        config = self.config["thresholds"]["repeated_hypothesis"]
        min_reps = config["min_repetitions"]
        similarity = config.get("similarity_threshold", 0.7)
        window = config.get("window_entries", 15)
        severity = config["severity"]
        
        entries = self._read_debug_log()
        if len(entries) < min_reps:
            return None
        
        # Focus on recent entries
        recent = entries[-window:]
        
        # Cluster by hypothesis similarity
        clusters = self._cluster_by_similarity(
            recent,
            key_fields=["hypothesis"],
            threshold=similarity
        )
        
        for cluster in clusters:
            # Only count non-success outcomes
            failures = [e for e in cluster if e.get("outcome") != "success"]
            if len(failures) >= min_reps:
                sample = failures[0]
                entry_ids = [e.get("entry_id", "?") for e in failures]
                evidence = f"Hypothesis '{sample['hypothesis'][:50]}...' tried {len(failures)} times without success"
                
                return PatternEvidence(
                    type="repeated_hypothesis",
                    count=len(failures),
                    evidence=evidence,
                    severity=severity,
                    entries=entry_ids[:5]
                )
        
        return None
    
    def _check_build_workers(self, verbose: bool) -> List[Dict]:
        """Check all worker conversations in a build for struggles."""
        if not self.build_slug:
            return []
        
        build_dir = self.BUILDS_BASE / self.build_slug
        if not build_dir.exists():
            return []
        
        # Read build meta to find worker conversations
        meta_path = build_dir / "meta.json"
        if not meta_path.exists():
            return []
        
        try:
            with open(meta_path) as f:
                meta = json.load(f)
        except json.JSONDecodeError:
            return []
        
        worker_issues = []
        
        # Worker details is a list, not a dict
        worker_details = meta.get("worker_details", [])
        if not isinstance(worker_details, list):
            return []
        
        for worker_info in worker_details:
            if not isinstance(worker_info, dict):
                continue
            worker_id = worker_info.get("worker_id", "unknown")
            convo_id = worker_info.get("conversation_id")
            if convo_id:
                detector = StruggleDetector(convo_id=convo_id)
                result = detector.detect(verbose=False)
                if result.status != "HEALTHY":
                    worker_issues.append({
                        "worker_id": worker_id,
                        "convo_id": convo_id,
                        "status": result.status,
                        "patterns": len(result.patterns_detected)
                    })
        
        return worker_issues
    
    def _read_debug_log(self) -> List[Dict]:
        """Read entries from DEBUG_LOG.jsonl."""
        if not self.debug_log or not self.debug_log.exists():
            return []
        
        entries = []
        try:
            with open(self.debug_log) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except IOError:
            return []
        
        return entries
    
    def _cluster_by_similarity(
        self, 
        entries: List[Dict], 
        key_fields: List[str],
        threshold: float
    ) -> List[List[Dict]]:
        """Cluster entries by similarity of key fields."""
        clusters = []
        
        for entry in entries:
            # Build comparison string from key fields
            entry_text = " ".join(str(entry.get(f, "")) for f in key_fields)
            
            # Find matching cluster
            matched = False
            for cluster in clusters:
                ref = cluster[0]
                ref_text = " ".join(str(ref.get(f, "")) for f in key_fields)
                
                similarity = SequenceMatcher(None, entry_text.lower(), ref_text.lower()).ratio()
                if similarity >= threshold:
                    cluster.append(entry)
                    matched = True
                    break
            
            if not matched:
                clusters.append([entry])
        
        return clusters


def format_human_output(result: StruggleResult, verbose: bool = False) -> str:
    """Format result for human-readable output."""
    lines = []
    
    # Status header
    status_icons = {
        "HEALTHY": "✅",
        "STRUGGLING": "⚠️",
        "STUCK": "🛑"
    }
    icon = status_icons.get(result.status, "❓")
    lines.append(f"{icon} Status: {result.status}")
    lines.append("")
    
    # Patterns
    if result.patterns_detected:
        lines.append(f"Patterns detected: {len(result.patterns_detected)}")
        for p in result.patterns_detected:
            lines.append(f"  • [{p.severity}] {p.type}: {p.evidence}")
            if verbose and p.entries:
                lines.append(f"    Entries: {', '.join(p.entries)}")
        lines.append("")
    else:
        lines.append("No struggle patterns detected.")
        lines.append("")
    
    # Recommendation
    lines.append(f"Recommendation: {result.recommendation}")
    
    # Context
    if verbose and result.context:
        lines.append("")
        lines.append("Context:")
        for k, v in result.context.items():
            if k != "worker_struggles" or v:
                lines.append(f"  {k}: {v}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Detect struggle patterns in agent conversations/builds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check a conversation for struggles
    python3 struggle_detector.py --convo-id con_abc123

    # Check a build
    python3 struggle_detector.py --build-slug ralph-learnings

    # JSON output for programmatic use
    python3 struggle_detector.py --convo-id con_abc123 --json

    # Verbose output with evidence details
    python3 struggle_detector.py --convo-id con_abc123 --verbose

Patterns Detected:
    circular_error     - Same error appears 3+ times in DEBUG_LOG
    stalled_progress   - Progress % unchanged across multiple updates
    revert_cycles      - Apply-revert-apply pattern in git history
    repeated_hypothesis - Same fix hypothesis tried multiple times

Status Levels:
    HEALTHY    - No patterns detected, continue work
    STRUGGLING - 1-2 patterns, consider intervention
    STUCK      - 3+ patterns or STUCK-severity, needs fresh start
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--convo-id",
        help="Conversation ID to check (e.g., con_abc123)"
    )
    input_group.add_argument(
        "--build-slug",
        help="Build slug to check (e.g., ralph-learnings)"
    )
    
    # Output options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Include detailed evidence in output"
    )
    
    args = parser.parse_args()
    
    # Create detector
    detector = StruggleDetector(
        convo_id=args.convo_id,
        build_slug=args.build_slug
    )
    
    # Run detection
    result = detector.detect(verbose=args.verbose)
    
    # Output
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_human_output(result, verbose=args.verbose))
    
    # Exit code based on status
    exit_codes = {"HEALTHY": 0, "STRUGGLING": 1, "STUCK": 2}
    sys.exit(exit_codes.get(result.status, 3))


if __name__ == "__main__":
    main()
