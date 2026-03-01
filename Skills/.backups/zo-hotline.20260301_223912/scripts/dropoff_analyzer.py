#!/usr/bin/env python3
"""
Zo Hotline Drop-off Analyzer

Diagnoses why short calls (<60s) end using LLM semantic analysis.
All classification uses /zo/ask — NO regex heuristics for meaning extraction.

Usage:
    python3 Skills/zo-hotline/scripts/dropoff_analyzer.py analyze
    python3 Skills/zo-hotline/scripts/dropoff_analyzer.py analyze --threshold 30
    python3 Skills/zo-hotline/scripts/dropoff_analyzer.py report
    python3 Skills/zo-hotline/scripts/dropoff_analyzer.py report --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import duckdb
import requests


DB_PATH = Path(__file__).parent.parent.parent.parent / "Datasets" / "zo-hotline-calls" / "data.duckdb"
ZO_API_URL = "https://api.zo.computer/zo/ask"


def get_zo_token() -> str:
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        print("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


def zo_ask(prompt: str, token: str) -> str:
    headers = {
        "authorization": token if token.startswith("Bearer") else f"Bearer {token}",
        "content-type": "application/json",
    }
    try:
        resp = requests.post(ZO_API_URL, json={"input": prompt}, headers=headers, timeout=120)
        resp.raise_for_status()
        body = resp.json()
        return body.get("output", body.get("response", ""))
    except Exception as e:
        print(f"WARNING: /zo/ask failed: {e}", file=sys.stderr)
        return ""


def zo_ask_json(prompt: str, token: str) -> Optional[Dict]:
    raw = zo_ask(prompt, token)
    if not raw:
        return None
    text = raw.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: extract JSON object/array from surrounding text
    brace_start = text.find("{")
    bracket_start = text.find("[")
    if brace_start == -1 and bracket_start == -1:
        print(f"WARNING: No JSON structure found in /zo/ask response: {text[:300]}", file=sys.stderr)
        return None
    if bracket_start != -1 and (brace_start == -1 or bracket_start < brace_start):
        end = text.rfind("]")
        if end > bracket_start:
            try:
                return json.loads(text[bracket_start:end + 1])
            except json.JSONDecodeError:
                pass
    if brace_start != -1:
        end = text.rfind("}")
        if end > brace_start:
            try:
                return json.loads(text[brace_start:end + 1])
            except json.JSONDecodeError:
                pass
    print(f"WARNING: Could not parse JSON from /zo/ask: {text[:300]}", file=sys.stderr)
    return None


def extract_call_data(row: Tuple) -> Dict:
    call_id, started_at, ended_at, duration, raw_data_json = row

    try:
        raw_data = json.loads(raw_data_json) if raw_data_json else {}
    except json.JSONDecodeError:
        raw_data = {}

    message = raw_data.get("message", {})
    ended_reason = message.get("endedReason", "unknown")
    artifact = message.get("artifact", {})
    transcript = artifact.get("transcript", "")
    cost = message.get("cost", 0)

    return {
        "id": call_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration": duration,
        "ended_reason": ended_reason,
        "transcript": transcript,
        "transcript_preview": transcript[:300] if transcript else "",
        "has_transcript": bool(transcript and transcript.strip()),
        "cost": cost,
    }


def classify_dropoffs_llm(calls: List[Dict], token: str) -> List[Dict]:
    """
    Classify all drop-off calls using LLM semantic analysis.
    Sends calls in a single batch for efficient classification.
    """
    if not calls:
        return []

    # Build digest for LLM
    digests = []
    for c in calls:
        preview = c["transcript_preview"] or "No transcript"
        digests.append(
            f"Call {c['id'][:8]} ({c['duration']}s, ended: {c['ended_reason']}):\n{preview}"
        )

    digest_text = "\n\n---\n\n".join(digests)

    prompt = f"""You are diagnosing why callers hung up quickly on the "Vibe Thinker Hotline" — a voice AI phone line for Zo Computer users. These {len(calls)} calls lasted under 60 seconds each.

For each call, determine the most likely reason for the quick hang-up. Consider all possibilities: wrong number, test call, audio/technical issue, didn't understand what this was, lost interest after hearing the greeting, expected a human, got confused by the opening message, detected it was a bot and left, etc.

CALLS:
{digest_text}

Respond with ONLY valid JSON (no markdown fences):
{{
  "classifications": [
    {{
      "call_id": "first 8 chars of ID",
      "duration": seconds,
      "likely_reason": "one-line diagnosis in plain English",
      "category": "wrong_number|test_call|technical_issue|confused_by_greeting|expected_human|lost_interest|bot_detection|audio_issue|unknown",
      "actionable": true or false,
      "suggested_fix": "brief suggestion if actionable, null otherwise"
    }}
  ],
  "category_breakdown": {{"category_name": count}},
  "actionable_insights": ["specific changes that could reduce drop-offs"],
  "summary": "2-3 sentence pattern summary"
}}"""

    result = zo_ask_json(prompt, token)
    if not result:
        # Fallback: return unclassified
        return [
            {**c, "classification": "unknown", "likely_reason": "LLM classification unavailable",
             "actionable": False, "suggested_fix": None}
            for c in calls
        ]

    # Merge LLM classifications back into call data
    classifications = result.get("classifications", [])
    classified_calls = []

    for c in calls:
        short_id = c["id"][:8]
        match = next((cl for cl in classifications if cl.get("call_id") == short_id), None)

        if match:
            c["classification"] = match.get("category", "unknown")
            c["likely_reason"] = match.get("likely_reason", "")
            c["actionable"] = match.get("actionable", False)
            c["suggested_fix"] = match.get("suggested_fix")
        else:
            c["classification"] = "unknown"
            c["likely_reason"] = "Not matched in LLM response"
            c["actionable"] = False
            c["suggested_fix"] = None

        classified_calls.append(c)

    # Attach aggregate insights to the last call for retrieval
    if classified_calls:
        classified_calls[-1]["_aggregate"] = {
            "category_breakdown": result.get("category_breakdown", {}),
            "actionable_insights": result.get("actionable_insights", []),
            "summary": result.get("summary", ""),
        }

    return classified_calls


def analyze_dropoffs(threshold: int = 60) -> Tuple[List[Dict], Dict]:
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    query = """
    SELECT id, started_at, ended_at, duration_seconds, raw_data
    FROM calls
    WHERE duration_seconds < ?
    ORDER BY duration_seconds, started_at
    """
    rows = conn.execute(query, [threshold]).fetchall()

    total_calls = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
    conn.close()

    calls = [extract_call_data(row) for row in rows]

    # LLM-based classification
    token = get_zo_token()
    print(f"Classifying {len(calls)} drop-off calls via LLM...", file=sys.stderr)
    classified_calls = classify_dropoffs_llm(calls, token)

    # Extract aggregate from last call if present
    aggregate = {}
    if classified_calls and "_aggregate" in classified_calls[-1]:
        aggregate = classified_calls[-1].pop("_aggregate")

    # Build stats
    category_counts = {}
    hour_counts = {}
    for call in classified_calls:
        cat = call.get("classification", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1

        if call["started_at"]:
            if isinstance(call["started_at"], datetime):
                hour = call["started_at"].hour
            elif isinstance(call["started_at"], str):
                hour = datetime.fromisoformat(call["started_at"]).hour
            else:
                continue
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

    stats = {
        "total_calls": total_calls,
        "dropoff_count": len(classified_calls),
        "dropoff_percentage": (len(classified_calls) / total_calls * 100) if total_calls > 0 else 0,
        "total_wasted_cost": sum(call["cost"] for call in classified_calls),
        "by_category": category_counts,
        "by_hour": hour_counts,
        "avg_duration": sum(call["duration"] for call in classified_calls) / len(classified_calls) if classified_calls else 0,
        "actionable_insights": aggregate.get("actionable_insights", []),
        "llm_summary": aggregate.get("summary", ""),
    }

    return classified_calls, stats


def generate_report(calls: List[Dict], stats: Dict, threshold: int) -> str:
    report = f"""---
created: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
last_edited: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
version: 1.0
provenance: dropoff_analyzer
---

# Zo Hotline Drop-off Analysis

**Analysis Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Threshold:** Calls under {threshold} seconds
**Total Calls in Database:** {stats['total_calls']}
**Drop-offs Found:** {stats['dropoff_count']} ({stats['dropoff_percentage']:.1f}%)
**Total Wasted Cost:** ${stats['total_wasted_cost']:.4f}
**Average Drop-off Duration:** {stats['avg_duration']:.1f}s
**Classification Method:** LLM semantic analysis (/zo/ask)

---

"""

    if stats.get("llm_summary"):
        report += f"## Summary\n\n{stats['llm_summary']}\n\n---\n\n"

    report += "## Drop-off Categories\n\n"
    for category, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
        percentage = (count / stats["dropoff_count"] * 100) if stats["dropoff_count"] > 0 else 0
        report += f"- **{category}**: {count} calls ({percentage:.1f}%)\n"

    if stats.get("actionable_insights"):
        report += "\n## Actionable Insights\n\n"
        for insight in stats["actionable_insights"]:
            report += f"- {insight}\n"

    if stats["by_hour"]:
        report += "\n## Time-of-Day Distribution\n\n"
        for hour in sorted(stats["by_hour"].keys()):
            count = stats["by_hour"][hour]
            report += f"- **{hour:02d}:00**: {count} drop-offs\n"

    report += "\n---\n\n## Per-Call Breakdown\n\n"
    for call in calls:
        report += f"""### Call {call['id'][:8]}...

- **Duration:** {call['duration']}s
- **Started:** {call['started_at']}
- **Ended Reason:** `{call['ended_reason']}`
- **Classification:** `{call.get('classification', 'unknown')}`
- **Likely Reason:** {call.get('likely_reason', 'N/A')}
- **Actionable:** {'Yes' if call.get('actionable') else 'No'}
- **Has Transcript:** {call['has_transcript']}
- **Cost:** ${call['cost']:.4f}
"""
        if call.get("suggested_fix"):
            report += f"- **Suggested Fix:** {call['suggested_fix']}\n"

        if call['transcript_preview']:
            report += f"- **Transcript Preview:** \"{call['transcript_preview']}...\"\n"

        report += "\n"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Analyze drop-offs in Zo Hotline calls (LLM-powered classification)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze                    # Analyze calls under 60s
  %(prog)s analyze --threshold 30     # Analyze calls under 30s
  %(prog)s report                     # Generate markdown report
  %(prog)s report --threshold 90      # Report on calls under 90s
  %(prog)s report --dry-run           # Preview output without writing
        """
    )

    parser.add_argument(
        "command",
        choices=["analyze", "report"],
        help="Command to run: 'analyze' for terminal output, 'report' for markdown"
    )
    parser.add_argument("--threshold", type=int, default=60, help="Duration threshold in seconds (default: 60)")
    parser.add_argument("--dry-run", action="store_true", help="Preview output without writing files")

    args = parser.parse_args()

    calls, stats = analyze_dropoffs(args.threshold)

    if args.command == "analyze":
        print(f"\n{'='*80}")
        print(f"Zo Hotline Drop-off Analysis (LLM-classified)")
        print(f"{'='*80}\n")
        print(f"Threshold: <{args.threshold}s")
        print(f"Total Calls: {stats['total_calls']}")
        print(f"Drop-offs: {stats['dropoff_count']} ({stats['dropoff_percentage']:.1f}%)")
        print(f"Wasted Cost: ${stats['total_wasted_cost']:.4f}")
        print(f"Avg Duration: {stats['avg_duration']:.1f}s\n")

        if stats.get("llm_summary"):
            print(f"LLM Summary: {stats['llm_summary']}\n")

        print("By Category:")
        for category, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
            percentage = (count / stats["dropoff_count"] * 100) if stats["dropoff_count"] > 0 else 0
            print(f"  {category:25s}: {count:3d} ({percentage:5.1f}%)")

        if stats.get("actionable_insights"):
            print("\nActionable Insights:")
            for insight in stats["actionable_insights"]:
                print(f"  - {insight}")

        if stats["by_hour"]:
            print("\nBy Hour:")
            for hour in sorted(stats["by_hour"].keys()):
                print(f"  {hour:02d}:00: {stats['by_hour'][hour]} calls")

        # Per-call diagnoses
        print(f"\nPer-Call Diagnoses:")
        for call in calls:
            reason = call.get("likely_reason", "unknown")
            cat = call.get("classification", "unknown")
            actionable = "!" if call.get("actionable") else " "
            print(f"  [{actionable}] {call['id'][:8]} ({call['duration']:3d}s) [{cat}] {reason}")

        print(f"\n{'='*80}\n")

    elif args.command == "report":
        report = generate_report(calls, stats, args.threshold)
        if args.dry_run:
            print("[DRY RUN] Report preview:\n")
        print(report)


if __name__ == "__main__":
    main()
