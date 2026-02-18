#!/usr/bin/env python3
"""
call_analysis_loop.py — Self-improving hotline analysis loop.

Runs daily (6pm ET via scheduled agent). Analyzes the previous day's calls:
  1. Substantive calls (>2min): Extract patterns, what worked, what confused callers
  2. Drop-off calls (<1min): LLM-based diagnosis of why people hung up
  3. Satisfaction trends from feedback data
  4. Generates ranked improvement suggestions by comparing findings to current system prompt
  5. Stores everything in DuckDB (daily_analysis table) and writes markdown reports

All semantic analysis uses /zo/ask — NO regex for meaning extraction.

Usage:
    python3 Skills/zo-hotline/scripts/call_analysis_loop.py              # Analyze yesterday
    python3 Skills/zo-hotline/scripts/call_analysis_loop.py --date 2026-02-13
    python3 Skills/zo-hotline/scripts/call_analysis_loop.py --days 7     # Last 7 days
    python3 Skills/zo-hotline/scripts/call_analysis_loop.py --dry-run    # Preview without writing
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb
import requests

DB_PATH = Path("/home/workspace/Datasets/zo-hotline-calls/data.duckdb")
ANALYSIS_DIR = Path("/home/workspace/Skills/zo-hotline/analysis")
SYSTEM_PROMPT_PATH = Path("/home/workspace/Skills/zo-hotline/prompts/zoseph-system-prompt.md")
ZO_API_URL = "https://api.zo.computer/zo/ask"

# Thresholds
SUBSTANTIVE_THRESHOLD = 120  # seconds — calls worth studying for patterns
DROPOFF_THRESHOLD = 60       # seconds — calls to diagnose for drop-off reasons


def get_zo_token() -> str:
    """Get Zo API token from environment."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        print("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


def zo_ask(prompt: str, token: str) -> str:
    """Call /zo/ask and return the text response. All semantic work goes through here."""
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
    """Call /zo/ask expecting JSON back. Returns parsed dict or None."""
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


def query_calls(conn: duckdb.DuckDBPyConnection, start: str, end: str) -> List[Dict]:
    """Query calls in a date range."""
    rows = conn.execute("""
        SELECT id, started_at, ended_at, duration_seconds, topics_discussed,
               level_assessed, escalation_requested, raw_data
        FROM calls
        WHERE started_at >= ? AND started_at < ?
        ORDER BY started_at
    """, [start, end]).fetchall()

    calls = []
    for r in rows:
        raw = json.loads(r[7]) if r[7] else {}
        calls.append({
            "id": r[0],
            "started_at": str(r[1]),
            "ended_at": str(r[2]),
            "duration_seconds": r[3] or 0,
            "topics_discussed": r[4],
            "level_assessed": r[5],
            "escalation_requested": r[6],
            "raw_data": raw,
        })
    return calls


def query_feedback(conn: duckdb.DuckDBPyConnection, start: str, end: str) -> List[Dict]:
    """Query feedback entries in a date range."""
    rows = conn.execute("""
        SELECT id, call_id, caller_name, satisfaction, comment, created_at
        FROM feedback
        WHERE created_at >= ? AND created_at < ?
        ORDER BY created_at
    """, [start, end]).fetchall()

    return [
        {
            "id": r[0], "call_id": r[1], "caller_name": r[2],
            "satisfaction": r[3], "comment": r[4], "created_at": str(r[5]),
        }
        for r in rows
    ]


def extract_transcript(raw_data: Dict) -> str:
    """Extract transcript from raw call data."""
    try:
        return (
            raw_data.get("message", {}).get("artifact", {}).get("transcript", "")
            or raw_data.get("message", {}).get("transcript", "")
            or ""
        )
    except (KeyError, AttributeError):
        return ""


def extract_summary(raw_data: Dict) -> str:
    """Extract Vapi-generated summary."""
    try:
        return raw_data.get("message", {}).get("analysis", {}).get("summary", "")
    except (KeyError, AttributeError):
        return ""


def extract_ended_reason(raw_data: Dict) -> str:
    """Extract call end reason."""
    try:
        return raw_data.get("message", {}).get("endedReason", "unknown")
    except (KeyError, AttributeError):
        return "unknown"


def extract_cost(raw_data: Dict) -> float:
    """Extract call cost."""
    try:
        return float(raw_data.get("message", {}).get("cost", 0) or 0)
    except (ValueError, KeyError, AttributeError):
        return 0.0


# ---------------------------------------------------------------------------
# Analysis functions — all semantic work via /zo/ask
# ---------------------------------------------------------------------------

def analyze_substantive_calls(calls: List[Dict], token: str) -> Dict:
    """
    Analyze calls >2min using LLM to extract patterns.
    Returns structured insights about what's working and what needs improvement.
    """
    substantive = [c for c in calls if c["duration_seconds"] >= SUBSTANTIVE_THRESHOLD]
    if not substantive:
        return {"count": 0, "patterns": [], "summary": "No substantive calls in this period."}

    # Build a digest of all substantive call transcripts/summaries
    call_digests = []
    for c in substantive:
        transcript = extract_transcript(c["raw_data"])
        summary = extract_summary(c["raw_data"])
        content = summary or (transcript[:2000] if transcript else "No transcript available")
        call_digests.append(
            f"Call {c['id'][:8]} ({c['duration_seconds']}s, ended: {extract_ended_reason(c['raw_data'])}):\n{content}"
        )

    digest_text = "\n\n---\n\n".join(call_digests)

    prompt = f"""You are analyzing phone calls from the "Vibe Thinker Hotline" — a voice AI advisor for Zo Computer users. Analyze these {len(substantive)} substantive calls (each >2 minutes) and extract actionable patterns.

CALLS:
{digest_text}

Respond with ONLY valid JSON (no markdown fences, no explanation):
{{
  "common_questions": ["list of recurring questions callers ask"],
  "topics_that_engaged": ["topics where callers stayed engaged and asked follow-ups"],
  "confusion_points": ["things that confused callers or led to misunderstanding"],
  "what_worked_well": ["specific responses or approaches that seemed effective"],
  "what_fell_flat": ["responses that didn't land or led to silence/topic change"],
  "caller_sophistication": "beginner|mixed|intermediate|advanced",
  "escalation_triggers": ["what specifically led callers to want human help"],
  "summary": "2-3 sentence overall pattern summary"
}}"""

    result = zo_ask_json(prompt, token) or {
        "common_questions": [], "topics_that_engaged": [], "confusion_points": [],
        "what_worked_well": [], "what_fell_flat": [], "caller_sophistication": "unknown",
        "escalation_triggers": [], "summary": "Analysis failed — no response from LLM.",
    }
    result["count"] = len(substantive)
    return result


def analyze_dropoffs(calls: List[Dict], token: str) -> Dict:
    """
    Analyze calls <1min using LLM to diagnose WHY people hung up.
    No regex classification — pure LLM semantic understanding.
    """
    dropoffs = [c for c in calls if c["duration_seconds"] < DROPOFF_THRESHOLD]
    if not dropoffs:
        return {"count": 0, "diagnoses": [], "summary": "No drop-off calls in this period."}

    # Build digest of drop-off call data
    dropoff_digests = []
    for c in dropoffs:
        transcript = extract_transcript(c["raw_data"])
        ended_reason = extract_ended_reason(c["raw_data"])
        preview = transcript[:500] if transcript else "No transcript"
        dropoff_digests.append(
            f"Call {c['id'][:8]} ({c['duration_seconds']}s, ended: {ended_reason}):\n{preview}"
        )

    digest_text = "\n\n---\n\n".join(dropoff_digests)

    prompt = f"""You are diagnosing why callers hung up quickly on the "Vibe Thinker Hotline" — a voice AI phone line for Zo Computer users. These {len(dropoffs)} calls lasted under 60 seconds.

For each call, determine the most likely reason for the quick hang-up. Consider: wrong number, test call, audio/technical issue, didn't understand what this was, lost interest after hearing the greeting, expected a human, got confused by the opening message, etc.

CALLS:
{digest_text}

Respond with ONLY valid JSON:
{{
  "diagnoses": [
    {{
      "call_id": "first 8 chars of ID",
      "duration": seconds,
      "likely_reason": "one-line diagnosis",
      "category": "wrong_number|test_call|technical_issue|confused_by_greeting|expected_human|lost_interest|bot_detection|unknown",
      "actionable": true/false
    }}
  ],
  "category_breakdown": {{"category_name": count}},
  "actionable_insights": ["specific changes that could reduce drop-offs"],
  "summary": "2-3 sentence pattern summary"
}}"""

    result = zo_ask_json(prompt, token) or {
        "diagnoses": [], "category_breakdown": {},
        "actionable_insights": [], "summary": "Analysis failed.",
    }
    result["count"] = len(dropoffs)
    return result


def analyze_satisfaction(feedback_entries: List[Dict], token: str) -> Dict:
    """Analyze feedback/satisfaction trends using LLM."""
    if not feedback_entries:
        return {"count": 0, "avg_satisfaction": None, "trend": "no_data", "insights": []}

    scores = [f["satisfaction"] for f in feedback_entries if f["satisfaction"] is not None]
    comments = [f["comment"] for f in feedback_entries if f["comment"]]
    names = [f["caller_name"] for f in feedback_entries if f["caller_name"]]

    avg_sat = sum(scores) / len(scores) if scores else None

    result = {
        "count": len(feedback_entries),
        "avg_satisfaction": round(avg_sat, 2) if avg_sat else None,
        "score_distribution": {str(i): scores.count(i) for i in range(1, 6) if scores.count(i) > 0},
        "unique_callers": len(set(names)),
        "comments": comments,
        "insights": [],
    }

    # If we have comments, use LLM to extract themes
    if comments:
        prompt = f"""These are feedback comments from callers to the Vibe Thinker Hotline:

{chr(10).join(f'- "{c}"' for c in comments)}

Average satisfaction: {avg_sat:.1f}/5 across {len(scores)} ratings.

Extract themes and actionable insights. Respond with ONLY valid JSON:
{{
  "themes": ["recurring theme 1", "recurring theme 2"],
  "positive_signals": ["what callers liked"],
  "negative_signals": ["what callers didn't like"],
  "suggestions": ["specific improvements based on this feedback"]
}}"""
        analysis = zo_ask_json(prompt, token)
        if analysis:
            result["insights"] = analysis

    return result


def generate_improvements(
    patterns: Dict, dropoffs: Dict, satisfaction: Dict,
    system_prompt: str, token: str
) -> List[Dict]:
    """
    Compare analysis findings against the current system prompt
    and generate ranked improvement suggestions.
    """
    prompt = f"""You are a voice AI optimization specialist. Based on the following analysis of the Vibe Thinker Hotline's recent performance, generate specific, actionable improvement suggestions.

## Current System Prompt (abbreviated, first 1500 chars):
{system_prompt[:1500]}

## Substantive Call Patterns:
{json.dumps(patterns, indent=2, default=str)[:2000]}

## Drop-off Analysis:
{json.dumps(dropoffs, indent=2, default=str)[:2000]}

## Satisfaction Data:
{json.dumps(satisfaction, indent=2, default=str)[:1000]}

Generate ranked improvements. Each should be specific enough to implement. Respond with ONLY valid JSON:
[
  {{
    "rank": 1,
    "category": "system_prompt|voice_config|tool_behavior|greeting|escalation|knowledge_base|other",
    "title": "Short descriptive title",
    "description": "What to change and why",
    "evidence": "Which data points support this change",
    "effort": "low|medium|high",
    "impact": "low|medium|high"
  }}
]

Limit to top 5 improvements. Prioritize high-impact, low-effort changes."""

    result = zo_ask_json(prompt, token)
    if isinstance(result, list):
        return result
    return []


def generate_executive_summary(
    analysis_date: str, total_calls: int,
    patterns: Dict, dropoffs: Dict, satisfaction: Dict,
    improvements: List[Dict], token: str
) -> Dict:
    """
    Generate a Zo team executive summary with sections for Product, GTM, and Founders.
    This is the daily briefing V requested — insights Zo's teams would want to hear.
    """
    if total_calls == 0:
        return {"product": "", "gtm": "", "founders": "", "headline": "No calls today."}

    prompt = f"""You are analyzing today's data from the Vibe Thinker Hotline — a voice AI advisory line for Zo Computer users. Zo Computer is a personal AI computer product. The hotline helps users learn to get the most out of Zo.

Today's date: {analysis_date}
Total calls: {total_calls}

## Call Pattern Analysis:
{json.dumps(patterns, indent=2, default=str)[:2500]}

## Drop-off Analysis:
{json.dumps(dropoffs, indent=2, default=str)[:1500]}

## Satisfaction:
{json.dumps(satisfaction, indent=2, default=str)[:1000]}

## Recommended Improvements:
{json.dumps(improvements, indent=2, default=str)[:1500]}

Write an executive summary for THREE audiences at Zo Computer. Be specific and cite data points. No fluff.

Respond with ONLY valid JSON:
{{
  "headline": "One-sentence summary of today's hotline activity",
  "product": "2-4 bullet points for Zo's PRODUCT team: What features are users struggling with? What capabilities are most requested? What UX friction was revealed? What should product prioritize?",
  "gtm": "2-4 bullet points for Zo's GO-TO-MARKET team: What use cases are resonating? What language do callers use to describe Zo? What objections or misconceptions came up? What marketing angles emerged?",
  "founders": "2-4 bullet points for Zo's FOUNDERS: Big-picture signals about product-market fit, user sophistication trends, whether the hotline is driving activation, and any strategic insights about how people engage with Zo as a product category."
}}"""

    result = zo_ask_json(prompt, token)
    if not result:
        return {
            "headline": f"{total_calls} calls analyzed — executive summary generation failed.",
            "product": "", "gtm": "", "founders": ""
        }
    return result


def build_caller_profiles(calls: List[Dict], token: str) -> List[Dict]:
    """
    Extract caller profile signals from call transcripts.
    Goes beyond feedback-only profiles by analyzing what callers said during calls.
    Returns profile entries that can be merged into caller_insights.
    """
    calls_with_transcripts = []
    for c in calls:
        transcript = extract_transcript(c["raw_data"])
        if transcript and len(transcript) > 100 and c["duration_seconds"] >= 60:
            calls_with_transcripts.append({
                "id": c["id"],
                "duration": c["duration_seconds"],
                "topics": c.get("topics_discussed", ""),
                "level": c.get("level_assessed"),
                "transcript_preview": transcript[:1500],
            })

    if not calls_with_transcripts:
        return []

    digests = []
    for c in calls_with_transcripts:
        digests.append(f"Call {c['id'][:8]} ({c['duration']}s, topics: {c['topics'] or 'none'}):\n{c['transcript_preview']}")

    digest_text = "\n\n---\n\n".join(digests[:10])  # Cap at 10 calls to stay within context

    prompt = f"""Analyze these {len(calls_with_transcripts)} phone call transcripts from the Vibe Thinker Hotline. For each call, extract any caller identity signals you can find.

CALLS:
{digest_text}

For each call where you can identify the caller (by name, role, company, or distinguishing details), extract a profile. If a caller doesn't identify themselves, skip that call.

Respond with ONLY valid JSON:
{{
  "profiles": [
    {{
      "call_id": "first 8 chars",
      "name": "caller's first name if mentioned, null otherwise",
      "role_or_context": "any role, company, or context they shared about themselves",
      "experience_level": "beginner|intermediate|advanced based on their questions and vocabulary",
      "interests": ["specific Zo features or use cases they were interested in"],
      "notable": "any notable quote or insight from this caller"
    }}
  ]
}}"""

    result = zo_ask_json(prompt, token)
    if not result:
        return []
    return result.get("profiles", [])


# ---------------------------------------------------------------------------
# Caller insights management
# ---------------------------------------------------------------------------

def update_caller_insights(conn: duckdb.DuckDBPyConnection, feedback_entries: List[Dict], calls: Optional[List[Dict]] = None):
    """Update caller_insights table from feedback data and call topics."""
    # Build a lookup of call data by approximate time for topic matching
    call_lookup = {}
    if calls:
        for c in calls:
            call_lookup[c["id"]] = c

    for f in feedback_entries:
        name = f.get("caller_name")
        if not name:
            continue

        name_lower = name.strip().lower()

        # Check if this caller already exists (case-insensitive match)
        existing = conn.execute(
            "SELECT id, call_count, avg_satisfaction, topics_history, level_assessed FROM caller_insights WHERE LOWER(first_name) = ?",
            [name_lower]
        ).fetchone()

        now = f.get("created_at", datetime.now(timezone.utc).isoformat())
        satisfaction = f.get("satisfaction")

        # Try to find associated call for topic/level data
        call_topics = None
        call_level = None
        call_id = f.get("call_id")
        if call_id and call_id in call_lookup:
            matched_call = call_lookup[call_id]
            call_topics = matched_call.get("topics_discussed")
            call_level = matched_call.get("level_assessed")

        if existing:
            caller_id, call_count, prev_avg, topics_hist, prev_level = existing
            new_count = call_count + 1

            if satisfaction is not None and prev_avg is not None:
                new_avg = ((prev_avg * call_count) + satisfaction) / new_count
            elif satisfaction is not None:
                new_avg = float(satisfaction)
            else:
                new_avg = prev_avg

            # Merge topics
            new_topics_hist = topics_hist
            if call_topics:
                existing_topics = set((topics_hist or "").split(", ")) if topics_hist else set()
                new_topic_set = set(t.strip() for t in call_topics.split(",") if t.strip())
                merged = existing_topics | new_topic_set
                merged.discard("")
                new_topics_hist = ", ".join(sorted(merged)) if merged else None

            # Use most recent level if available
            new_level = call_level if call_level is not None else prev_level

            conn.execute("""
                UPDATE caller_insights
                SET call_count = ?, last_seen = ?, avg_satisfaction = ?, last_satisfaction = ?,
                    topics_history = ?, level_assessed = ?
                WHERE id = ?
            """, [new_count, now, new_avg, satisfaction, new_topics_hist, new_level, caller_id])
        else:
            caller_id = str(uuid.uuid4())
            initial_topics = call_topics if call_topics else None

            conn.execute("""
                INSERT INTO caller_insights (id, first_name, call_count, first_seen, last_seen,
                                             avg_satisfaction, last_satisfaction, topics_history, level_assessed, notes)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, NULL)
            """, [caller_id, name.strip(), now, now,
                  float(satisfaction) if satisfaction else None,
                  satisfaction, initial_topics, call_level])


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    analysis_date: str, period_start: str, period_end: str,
    all_calls: List[Dict], patterns: Dict, dropoffs: Dict,
    satisfaction: Dict, improvements: List[Dict],
    executive_summary: Optional[Dict] = None
) -> str:
    """Generate a human-readable markdown report."""
    total = len(all_calls)
    substantive_count = patterns.get("count", 0)
    dropoff_count = dropoffs.get("count", 0)
    mid_count = total - substantive_count - dropoff_count
    total_cost = sum(extract_cost(c["raw_data"]) for c in all_calls)
    avg_dur = sum(c["duration_seconds"] for c in all_calls) / total if total else 0

    lines = [
        "---",
        f"created: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"last_edited: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "version: 1.0",
        "provenance: call_analysis_loop",
        "---",
        "",
        f"# Hotline Daily Analysis — {analysis_date}",
        "",
        f"**Period:** {period_start} to {period_end}",
        f"**Total Calls:** {total}",
        f"**Average Duration:** {avg_dur:.0f}s ({avg_dur/60:.1f}min)",
        f"**Total Cost:** ${total_cost:.4f}",
        "",
        f"| Segment | Count | % |",
        f"|---------|-------|---|",
        f"| Substantive (>2min) | {substantive_count} | {100*substantive_count/total if total else 0:.0f}% |",
        f"| Mid-range (1-2min) | {mid_count} | {100*mid_count/total if total else 0:.0f}% |",
        f"| Drop-off (<1min) | {dropoff_count} | {100*dropoff_count/total if total else 0:.0f}% |",
        "",
    ]

    # Executive summary for Zo team
    if executive_summary and executive_summary.get("headline"):
        lines.append("## Executive Summary for Zo Team")
        lines.append("")
        lines.append(f"**{executive_summary['headline']}**")
        lines.append("")
        for section_key, section_title in [("product", "Product Team"), ("gtm", "Go-to-Market Team"), ("founders", "Founders")]:
            section_val = executive_summary.get(section_key)
            if section_val:
                lines.append(f"### {section_title}")
                if isinstance(section_val, list):
                    for item in section_val:
                        lines.append(f"- {item}")
                else:
                    lines.append(str(section_val))
                lines.append("")
        lines.append("---")
        lines.append("")

    # Substantive patterns
    lines.append("## Substantive Call Patterns")
    lines.append("")
    if patterns.get("summary"):
        lines.append(f"**Summary:** {patterns['summary']}")
        lines.append("")

    for field, label in [
        ("common_questions", "Common Questions"),
        ("topics_that_engaged", "Engaging Topics"),
        ("confusion_points", "Confusion Points"),
        ("what_worked_well", "What Worked"),
        ("what_fell_flat", "What Fell Flat"),
        ("escalation_triggers", "Escalation Triggers"),
    ]:
        items = patterns.get(field, [])
        if items:
            lines.append(f"### {label}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    if patterns.get("caller_sophistication"):
        lines.append(f"**Caller Sophistication:** {patterns['caller_sophistication']}")
        lines.append("")

    # Drop-off analysis
    lines.append("## Drop-off Analysis")
    lines.append("")
    if dropoffs.get("summary"):
        lines.append(f"**Summary:** {dropoffs['summary']}")
        lines.append("")

    breakdown = dropoffs.get("category_breakdown", {})
    if breakdown:
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        for cat, count in sorted(breakdown.items(), key=lambda x: -x[1]):
            lines.append(f"| {cat} | {count} |")
        lines.append("")

    actionable = dropoffs.get("actionable_insights", [])
    if actionable:
        lines.append("### Actionable Insights")
        for insight in actionable:
            lines.append(f"- {insight}")
        lines.append("")

    # Satisfaction
    lines.append("## Satisfaction")
    lines.append("")
    if satisfaction.get("avg_satisfaction") is not None:
        lines.append(f"**Average:** {satisfaction['avg_satisfaction']}/5 ({satisfaction['count']} responses)")
    else:
        lines.append("No feedback data for this period.")
    lines.append("")

    dist = satisfaction.get("score_distribution", {})
    if dist:
        lines.append("| Score | Count |")
        lines.append("|-------|-------|")
        for score in sorted(dist.keys()):
            lines.append(f"| {score}/5 | {dist[score]} |")
        lines.append("")

    insights = satisfaction.get("insights", {})
    if isinstance(insights, dict):
        for field in ["positive_signals", "negative_signals", "suggestions"]:
            items = insights.get(field, [])
            if items:
                lines.append(f"### {field.replace('_', ' ').title()}")
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")

    # Improvements
    if improvements:
        lines.append("## Recommended Improvements")
        lines.append("")
        for imp in improvements:
            rank = imp.get("rank", "?")
            title = imp.get("title", "Untitled")
            desc = imp.get("description", "")
            evidence = imp.get("evidence", "")
            effort = imp.get("effort", "?")
            impact = imp.get("impact", "?")
            cat = imp.get("category", "other")

            lines.append(f"### #{rank}: {title}")
            lines.append(f"**Category:** {cat} | **Effort:** {effort} | **Impact:** {impact}")
            lines.append(f"")
            lines.append(str(desc) if not isinstance(desc, list) else "\n".join(f"- {d}" for d in desc))
            if evidence:
                lines.append("")
                evidence_str = str(evidence) if not isinstance(evidence, list) else "; ".join(str(e) for e in evidence)
                lines.append(f"**Evidence:** {evidence_str}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_analysis(analysis_date: str, period_start: str, period_end: str, dry_run: bool = False):
    """Run the full analysis loop for a given period."""
    token = get_zo_token()

    print(f"Analyzing calls from {period_start} to {period_end}", file=sys.stderr)

    # Phase 1: Read data (read-only connection — does NOT block webhook writes)
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    all_calls = query_calls(conn, period_start, period_end)
    feedback = query_feedback(conn, period_start, period_end)
    conn.close()  # Release DB immediately before LLM calls

    print(f"  Found {len(all_calls)} calls, {len(feedback)} feedback entries", file=sys.stderr)

    if not all_calls:
        print("  No calls in this period. Skipping analysis.", file=sys.stderr)
        return

    # Phase 2: LLM analysis (no DB connection held — can take minutes)
    system_prompt = ""
    if SYSTEM_PROMPT_PATH.exists():
        system_prompt = SYSTEM_PROMPT_PATH.read_text()

    print("  Analyzing substantive calls...", file=sys.stderr)
    patterns = analyze_substantive_calls(all_calls, token)

    print("  Analyzing drop-offs...", file=sys.stderr)
    dropoff_insights = analyze_dropoffs(all_calls, token)

    print("  Analyzing satisfaction...", file=sys.stderr)
    satisfaction = analyze_satisfaction(feedback, token)

    print("  Generating improvements...", file=sys.stderr)
    improvements = generate_improvements(patterns, dropoff_insights, satisfaction, system_prompt, token)

    print("  Generating executive summary for Zo team...", file=sys.stderr)
    executive_summary = generate_executive_summary(
        analysis_date, len(all_calls), patterns, dropoff_insights, satisfaction, improvements, token
    )

    print("  Building caller profiles from transcripts...", file=sys.stderr)
    caller_profiles = build_caller_profiles(all_calls, token)

    # Phase 3: Generate report (no DB needed)
    report = generate_report(
        analysis_date, period_start, period_end,
        all_calls, patterns, dropoff_insights, satisfaction, improvements,
        executive_summary=executive_summary
    )

    # Phase 4: Store results (write connection — only when NOT dry-run)
    if dry_run:
        print("\n[DRY RUN] Would write report and DB record. Report preview:\n", file=sys.stderr)
        print(report)
    else:
        # Update caller insights and store analysis
        conn = duckdb.connect(str(DB_PATH))

        if feedback:
            print("  Updating caller insights from feedback...", file=sys.stderr)
            update_caller_insights(conn, feedback, all_calls)

        if caller_profiles:
            print(f"  Merging {len(caller_profiles)} caller profiles from transcripts...", file=sys.stderr)
            for profile in caller_profiles:
                name = profile.get("name")
                if not name:
                    continue
                name_lower = name.strip().lower()
                existing = conn.execute(
                    "SELECT id, notes, topics_history FROM caller_insights WHERE LOWER(first_name) = ?",
                    [name_lower]
                ).fetchone()
                interests = ", ".join(profile.get("interests", []))
                note_parts = []
                if profile.get("role_or_context"):
                    note_parts.append(profile["role_or_context"])
                if profile.get("experience_level"):
                    note_parts.append(f"level: {profile['experience_level']}")
                if profile.get("notable"):
                    note_parts.append(f'notable: "{profile["notable"]}"')
                new_note = "; ".join(note_parts) if note_parts else None

                if existing:
                    caller_id, prev_notes, prev_topics = existing
                    merged_notes = f"{prev_notes}; {new_note}" if prev_notes and new_note else (new_note or prev_notes)
                    merged_topics = prev_topics
                    if interests:
                        existing_set = set((prev_topics or "").split(", ")) if prev_topics else set()
                        new_set = set(t.strip() for t in interests.split(",") if t.strip())
                        merged = existing_set | new_set
                        merged.discard("")
                        merged_topics = ", ".join(sorted(merged)) if merged else prev_topics
                    conn.execute(
                        "UPDATE caller_insights SET notes = ?, topics_history = ? WHERE id = ?",
                        [merged_notes, merged_topics, caller_id]
                    )
                else:
                    conn.execute("""
                        INSERT INTO caller_insights (id, first_name, call_count, first_seen, last_seen,
                                                     avg_satisfaction, last_satisfaction, topics_history, level_assessed, notes)
                        VALUES (?, ?, 1, ?, ?, NULL, NULL, ?, NULL, ?)
                    """, [str(uuid.uuid4()), name.strip(),
                          datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(),
                          interests or None, new_note])

        # Write markdown report
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = ANALYSIS_DIR / f"{analysis_date}_daily_analysis.md"
        report_path.write_text(report)
        print(f"  Report written to {report_path}", file=sys.stderr)

        # Store in DuckDB
        record_id = str(uuid.uuid4())
        substantive_count = patterns.get("count", 0)
        dropoff_count = dropoff_insights.get("count", 0)
        avg_dur = sum(c["duration_seconds"] for c in all_calls) / len(all_calls) if all_calls else 0
        avg_sat = satisfaction.get("avg_satisfaction")

        conn.execute("""
            INSERT INTO daily_analysis
            (id, analysis_date, period_start, period_end, total_calls, substantive_calls,
             dropoff_calls, avg_duration, avg_satisfaction, patterns_json, dropoff_insights_json,
             improvements_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            record_id, analysis_date, period_start, period_end,
            len(all_calls), substantive_count, dropoff_count,
            avg_dur, avg_sat,
            json.dumps(patterns, default=str),
            json.dumps(dropoff_insights, default=str),
            json.dumps(improvements, default=str),
            datetime.now(timezone.utc).isoformat(),
        ])
        print(f"  Analysis stored in daily_analysis table (id: {record_id[:8]})", file=sys.stderr)

        conn.close()

    # Print summary
    print(f"\n  Summary:", file=sys.stderr)
    print(f"    Total calls: {len(all_calls)}", file=sys.stderr)
    print(f"    Substantive (>2min): {patterns.get('count', 0)}", file=sys.stderr)
    print(f"    Drop-offs (<1min): {dropoff_insights.get('count', 0)}", file=sys.stderr)
    print(f"    Feedback entries: {len(feedback)}", file=sys.stderr)
    print(f"    Improvements generated: {len(improvements)}", file=sys.stderr)
    print(f"    Caller profiles extracted: {len(caller_profiles)}", file=sys.stderr)
    if executive_summary.get("headline"):
        print(f"    Executive headline: {executive_summary['headline']}", file=sys.stderr)

    # Return report for agent delivery
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Self-improving hotline call analysis loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Analyze yesterday's calls
  %(prog)s --date 2026-02-13        # Analyze a specific date
  %(prog)s --days 7                 # Analyze last 7 days
  %(prog)s --dry-run                # Preview without writing
  %(prog)s --days 7 --dry-run       # Preview last 7 days
""",
    )
    parser.add_argument("--date", help="Specific date to analyze (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=1, help="Number of days to analyze (default: 1 = yesterday)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB or files")

    args = parser.parse_args()

    if args.date:
        # Analyze a specific date
        analysis_date = args.date
        period_start = f"{analysis_date} 00:00:00"
        period_end = f"{analysis_date} 23:59:59"
        run_analysis(analysis_date, period_start, period_end, dry_run=args.dry_run)
    else:
        # Analyze previous N days
        today = datetime.now(timezone.utc).date()
        for i in range(args.days, 0, -1):
            target = today - timedelta(days=i)
            analysis_date = target.isoformat()
            period_start = f"{analysis_date} 00:00:00"
            period_end = f"{analysis_date} 23:59:59"
            run_analysis(analysis_date, period_start, period_end, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
