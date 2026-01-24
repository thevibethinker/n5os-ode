#!/usr/bin/env python3
"""Process Careerspan scan result CSVs and generate candidate briefings.

---
product: careerspan
version: 1.0
created: 2026-01-21
requires_confirm: false
---

Usage:
    python3 N5/scripts/process_scan_results.py <csv_path>
    python3 N5/scripts/process_scan_results.py <csv_path> --output-dir /path/to/output
    python3 N5/scripts/process_scan_results.py <csv_path> --json  # Machine-readable output

This script analyzes Careerspan scan result CSVs and produces:
1. A summary of candidate counts and score distributions
2. Top candidates with their key attributes
3. A markdown briefing suitable for quick review
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any


def parse_csv(csv_path: Path) -> list[dict[str, Any]]:
    """Parse CSV file into list of candidate dicts."""
    candidates = []
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize keys (lowercase, strip whitespace)
            normalized = {k.lower().strip().replace(' ', '_'): v.strip() for k, v in row.items()}
            candidates.append(normalized)
    return candidates


def extract_score(candidate: dict, score_keys: list[str]) -> float | None:
    """Try to extract a numeric score from various possible field names."""
    for key in score_keys:
        if key in candidate:
            try:
                return float(candidate[key])
            except (ValueError, TypeError):
                continue
    return None


def analyze_candidates(candidates: list[dict]) -> dict[str, Any]:
    """Analyze candidate list and return summary statistics."""
    if not candidates:
        return {"error": "No candidates found in CSV"}
    
    # Try to find score columns
    score_keys = ['score', 'overall_score', 'final_score', 'match_score', 'total_score']
    scores = []
    for c in candidates:
        score = extract_score(c, score_keys)
        if score is not None:
            scores.append(score)
    
    # Basic stats
    analysis = {
        "total_candidates": len(candidates),
        "fields_available": list(candidates[0].keys()) if candidates else [],
        "timestamp": datetime.now().isoformat(),
    }
    
    # Score statistics if available
    if scores:
        analysis["score_stats"] = {
            "min": min(scores),
            "max": max(scores),
            "mean": round(mean(scores), 2),
            "median": round(median(scores), 2),
            "stdev": round(stdev(scores), 2) if len(scores) > 1 else 0,
        }
        
        # Score distribution buckets
        buckets = {"90+": 0, "85-89": 0, "80-84": 0, "75-79": 0, "<75": 0}
        for s in scores:
            if s >= 90:
                buckets["90+"] += 1
            elif s >= 85:
                buckets["85-89"] += 1
            elif s >= 80:
                buckets["80-84"] += 1
            elif s >= 75:
                buckets["75-79"] += 1
            else:
                buckets["<75"] += 1
        analysis["score_distribution"] = buckets
    
    # Extract top candidates
    name_keys = ['name', 'candidate_name', 'full_name', 'applicant_name', 'email']
    
    def get_name(c: dict) -> str:
        for key in name_keys:
            if key in c and c[key]:
                return c[key]
        return "Unknown"
    
    # Sort by score if available
    if scores:
        scored_candidates = []
        for c in candidates:
            score = extract_score(c, score_keys)
            if score is not None:
                scored_candidates.append((score, c))
        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        
        analysis["top_candidates"] = []
        for score, c in scored_candidates[:10]:
            top_entry = {
                "name": get_name(c),
                "score": score,
            }
            # Add any other interesting fields
            for key in ['email', 'title', 'current_role', 'company', 'experience_years', 
                        'skills', 'strengths', 'summary', 'application_link']:
                if key in c and c[key]:
                    top_entry[key] = c[key]
            analysis["top_candidates"].append(top_entry)
    else:
        # No scores, just list first 10
        analysis["top_candidates"] = [
            {"name": get_name(c), **{k: v for k, v in c.items() if v}}
            for c in candidates[:10]
        ]
    
    return analysis


def generate_briefing(analysis: dict, csv_name: str) -> str:
    """Generate a markdown briefing from analysis."""
    lines = [
        f"# Scan Results Briefing: {csv_name}",
        f"",
        f"**Generated:** {analysis.get('timestamp', 'Unknown')}",
        f"**Total Candidates:** {analysis.get('total_candidates', 0)}",
        f"",
    ]
    
    # Score summary
    if "score_stats" in analysis:
        stats = analysis["score_stats"]
        lines.extend([
            "## Score Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Mean | {stats['mean']} |",
            f"| Median | {stats['median']} |",
            f"| Range | {stats['min']} - {stats['max']} |",
            f"| Std Dev | {stats['stdev']} |",
            "",
        ])
    
    # Distribution
    if "score_distribution" in analysis:
        dist = analysis["score_distribution"]
        lines.extend([
            "## Score Distribution",
            "",
            f"| Range | Count |",
            f"|-------|-------|",
        ])
        for bucket, count in dist.items():
            bar = "█" * min(count, 20)
            lines.append(f"| {bucket} | {count} {bar} |")
        lines.append("")
    
    # Top candidates
    if "top_candidates" in analysis and analysis["top_candidates"]:
        lines.extend([
            "## Top Candidates",
            "",
        ])
        for i, candidate in enumerate(analysis["top_candidates"][:10], 1):
            name = candidate.get("name", "Unknown")
            score = candidate.get("score", "N/A")
            lines.append(f"### {i}. {name} (Score: {score})")
            
            # Add available details
            details = []
            if "email" in candidate:
                details.append(f"- **Email:** {candidate['email']}")
            if "title" in candidate or "current_role" in candidate:
                role = candidate.get("title") or candidate.get("current_role")
                details.append(f"- **Current Role:** {role}")
            if "company" in candidate:
                details.append(f"- **Company:** {candidate['company']}")
            if "strengths" in candidate:
                details.append(f"- **Strengths:** {candidate['strengths']}")
            if "summary" in candidate:
                details.append(f"- **Summary:** {candidate['summary'][:200]}...")
            if "application_link" in candidate:
                details.append(f"- **Apply Link:** {candidate['application_link']}")
            
            if details:
                lines.extend(details)
            lines.append("")
    
    # Fields available (for reference)
    if "fields_available" in analysis:
        lines.extend([
            "## Available Fields",
            "",
            f"The CSV contains these columns: `{', '.join(analysis['fields_available'])}`",
            "",
        ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Process Careerspan scan result CSVs and generate candidate briefings."
    )
    parser.add_argument("csv_path", help="Path to the scan results CSV file")
    parser.add_argument("--output-dir", default=None, 
                        help="Directory to save briefing (default: same as CSV)")
    parser.add_argument("--json", action="store_true", 
                        help="Output raw analysis as JSON instead of markdown")
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse and analyze
    candidates = parse_csv(csv_path)
    analysis = analyze_candidates(candidates)
    
    if args.json:
        print(json.dumps(analysis, indent=2))
        return
    
    # Generate briefing
    briefing = generate_briefing(analysis, csv_path.name)
    
    # Save briefing
    output_dir = Path(args.output_dir) if args.output_dir else csv_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    briefing_path = output_dir / f"{csv_path.stem}_briefing.md"
    briefing_path.write_text(briefing)
    
    print(briefing)
    print(f"\n---\nBriefing saved to: {briefing_path}")


if __name__ == "__main__":
    main()
