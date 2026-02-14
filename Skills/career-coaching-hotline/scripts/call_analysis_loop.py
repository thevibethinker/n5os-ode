#!/usr/bin/env python3
"""
call_analysis_loop.py — Career Coaching Hotline daily analysis loop.

Ported from Skills/zo-hotline/scripts/call_analysis_loop.py, adapted for career coaching:
  - Career stage distribution analysis (5 stages from career-stages.md)
  - Careerspan conversion tracking (escalations → booked sessions)
  - Topic analysis: resume, interview, networking, outreach, career change, etc.
  - Drop-off classification adapted for career context

Runs daily (scheduled agent). Analyzes the previous day's calls:
  1. Substantive calls (>2min): Extract patterns, career stage signals, what resonated
  2. Drop-off calls (<1min): LLM-based diagnosis of why people hung up
  3. Satisfaction trends from feedback data
  4. Career stage distribution and Careerspan conversion rate
  5. Generates ranked improvement suggestions
  6. Stores results in DuckDB (daily_analysis table)

All semantic analysis uses /zo/ask — NO regex for meaning extraction.

Usage:
    python3 Skills/career-coaching-hotline/scripts/call_analysis_loop.py
    python3 Skills/career-coaching-hotline/scripts/call_analysis_loop.py --date 2026-02-14
    python3 Skills/career-coaching-hotline/scripts/call_analysis_loop.py --days 7
    python3 Skills/career-coaching-hotline/scripts/call_analysis_loop.py --dry-run
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import duckdb
import requests

DB_PATH = Path("/home/workspace/Datasets/career-coaching-calls/data.duckdb")
ANALYSIS_DIR = Path("/home/workspace/Skills/career-coaching-hotline/analysis")
ZO_API_URL = "https://api.zo.computer/zo/ask"

SUBSTANTIVE_THRESHOLD = 120  # seconds
DROPOFF_THRESHOLD = 60       # seconds

CAREER_STAGES = [
    "Groundwork (Pre-Search)",
    "Materials (Active Preparation)",
    "Outreach (Active Search)",
    "Performance (Interview & Conversion)",
    "Transition (Career Change or Crisis)",
]

TOPIC_CATEGORIES = [
    "self-reflection", "groundwork", "anecdote-development",
    "resume-customization", "aiss-bullets", "ats-optimization",
    "cover-letters", "master-resume", "materials-prep",
    "networking", "cold-outreach", "linkedin-strategy",
    "systematic-job-hunting", "four-levers",
    "interview-prep", "art-of-the-brag", "start-format",
    "career-change", "reframing-experience", "layoff-recovery",
    "career-decision", "salary-negotiation",
    "escalation", "general",
]


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", file=sys.stderr)


def get_zo_token() -> str:
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        log("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set")
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
    except requests.RequestException as e:
        log(f"WARNING: /zo/ask failed: {e}")
        return ""


def zo_ask_json(prompt: str, token: str) -> Optional[dict]:
    raw = zo_ask(prompt, token)
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    brace_start = text.find("{")
    bracket_start = text.find("[")
    if brace_start == -1 and bracket_start == -1:
        log(f"WARNING: No JSON found in response: {text[:200]}")
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
    log(f"WARNING: Could not parse JSON: {text[:200]}")
    return None


def query_calls(conn: duckdb.DuckDBPyConnection, start: str, end: str) -> list[dict]:
    rows = conn.execute("""
        SELECT id, started_at, ended_at, duration_seconds, caller_phone,
               caller_profile_id, topics_discussed, career_stage_assessed,
               escalation_requested, raw_data
        FROM calls
        WHERE started_at >= ? AND started_at < ?
        ORDER BY started_at
    """, [start, end]).fetchall()

    calls = []
    for r in rows:
        raw = json.loads(r[9]) if r[9] else {}
        calls.append({
            "id": r[0],
            "started_at": str(r[1]),
            "ended_at": str(r[2]),
            "duration_seconds": r[3] or 0,
            "caller_phone": r[4],
            "caller_profile_id": r[5],
            "topics_discussed": r[6],
            "career_stage_assessed": r[7],
            "escalation_requested": r[8],
            "raw_data": raw,
        })
    return calls


def query_feedback(conn: duckdb.DuckDBPyConnection, start: str, end: str) -> list[dict]:
    rows = conn.execute("""
        SELECT id, call_id, caller_name, satisfaction, comment, created_at
        FROM feedback
        WHERE created_at >= ? AND created_at < ?
        ORDER BY created_at
    """, [start, end]).fetchall()
    return [
        {"id": r[0], "call_id": r[1], "caller_name": r[2],
         "satisfaction": r[3], "comment": r[4], "created_at": str(r[5])}
        for r in rows
    ]


def query_escalations(conn: duckdb.DuckDBPyConnection, start: str, end: str) -> list[dict]:
    rows = conn.execute("""
        SELECT id, call_id, name, career_stage, reason, booking_link_sent, created_at
        FROM escalations
        WHERE created_at >= ? AND created_at < ?
        ORDER BY created_at
    """, [start, end]).fetchall()
    return [
        {"id": r[0], "call_id": r[1], "name": r[2], "career_stage": r[3],
         "reason": r[4], "booking_link_sent": r[5], "created_at": str(r[6])}
        for r in rows
    ]


def extract_transcript(raw_data: dict) -> str:
    try:
        return (
            raw_data.get("message", {}).get("artifact", {}).get("transcript", "")
            or raw_data.get("message", {}).get("transcript", "")
            or ""
        )
    except (KeyError, AttributeError):
        return ""


def extract_summary(raw_data: dict) -> str:
    try:
        return raw_data.get("message", {}).get("analysis", {}).get("summary", "")
    except (KeyError, AttributeError):
        return ""


def extract_ended_reason(raw_data: dict) -> str:
    try:
        return raw_data.get("message", {}).get("endedReason", "unknown")
    except (KeyError, AttributeError):
        return "unknown"


# ---------------------------------------------------------------------------
# Analysis functions — all semantic work via /zo/ask
# ---------------------------------------------------------------------------

def analyze_substantive_calls(calls: list[dict], token: str) -> dict:
    substantive = [c for c in calls if c["duration_seconds"] >= SUBSTANTIVE_THRESHOLD]
    if not substantive:
        return {"count": 0, "patterns": [], "summary": "No substantive calls in this period."}

    call_digests = []
    for c in substantive:
        transcript = extract_transcript(c["raw_data"])
        summary = extract_summary(c["raw_data"])
        content = summary or (transcript[:2000] if transcript else "No transcript available")
        stage = c.get("career_stage_assessed") or "not assessed"
        call_digests.append(
            f"Call {c['id'][:8]} ({c['duration_seconds']}s, stage: {stage}, "
            f"ended: {extract_ended_reason(c['raw_data'])}):\n{content}"
        )

    digest_text = "\n\n---\n\n".join(call_digests)
    stages_list = "\n".join(f"  - {s}" for s in CAREER_STAGES)

    prompt = f"""You are analyzing phone calls from a Career Coaching Hotline — a voice AI career advisor powered by V's decade of coaching experience. Analyze these {len(substantive)} substantive calls (each >2 minutes) and extract actionable patterns.

The hotline uses these career stages:
{stages_list}

CALLS:
{digest_text}

Respond with ONLY valid JSON (no markdown fences):
{{
  "common_questions": ["recurring questions callers ask"],
  "topics_that_engaged": ["topics where callers stayed engaged"],
  "confusion_points": ["things that confused callers"],
  "what_worked_well": ["responses or approaches that seemed effective"],
  "what_fell_flat": ["responses that didn't land"],
  "career_stage_distribution": {{"stage_name": count}},
  "top_pain_points": ["most common pain points expressed by callers"],
  "careerspan_triggers": ["what specifically led callers to want a Careerspan session"],
  "caller_sophistication": "early-career|mixed|mid-career|senior",
  "summary": "2-3 sentence overall pattern summary"
}}"""

    result = zo_ask_json(prompt, token) or {
        "common_questions": [], "topics_that_engaged": [], "confusion_points": [],
        "what_worked_well": [], "what_fell_flat": [], "career_stage_distribution": {},
        "top_pain_points": [], "careerspan_triggers": [], "caller_sophistication": "unknown",
        "summary": "Analysis failed — no response from LLM.",
    }
    result["count"] = len(substantive)
    return result


def analyze_dropoffs(calls: list[dict], token: str) -> dict:
    dropoffs = [c for c in calls if c["duration_seconds"] < DROPOFF_THRESHOLD]
    if not dropoffs:
        return {"count": 0, "diagnoses": [], "summary": "No drop-off calls in this period."}

    dropoff_digests = []
    for c in dropoffs:
        transcript = extract_transcript(c["raw_data"])
        ended_reason = extract_ended_reason(c["raw_data"])
        preview = transcript[:500] if transcript else "No transcript"
        dropoff_digests.append(
            f"Call {c['id'][:8]} ({c['duration_seconds']}s, ended: {ended_reason}):\n{preview}"
        )

    digest_text = "\n\n---\n\n".join(dropoff_digests)

    prompt = f"""You are diagnosing why callers hung up quickly on a Career Coaching Hotline — a voice AI advisor for job seekers and career changers. These {len(dropoffs)} calls lasted under 60 seconds.

For each call, determine the most likely reason. Consider: wrong number, test call, audio issue, didn't understand what this was, expected a human career coach, lost interest after greeting, got confused, looking for something else entirely, etc.

CALLS:
{digest_text}

Respond with ONLY valid JSON:
{{
  "diagnoses": [
    {{
      "call_id": "first 8 chars",
      "duration": seconds,
      "likely_reason": "one-line diagnosis",
      "category": "wrong_number|test_call|technical_issue|confused_by_greeting|expected_human|lost_interest|bot_detection|looking_for_different_service|unknown",
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


def analyze_satisfaction(feedback_entries: list[dict], token: str) -> dict:
    if not feedback_entries:
        return {"count": 0, "avg_satisfaction": None, "trend": "no_data", "insights": []}

    scores = [f["satisfaction"] for f in feedback_entries if f["satisfaction"] is not None]
    comments = [f["comment"] for f in feedback_entries if f["comment"]]

    avg_sat = sum(scores) / len(scores) if scores else None

    result: dict[str, Any] = {
        "count": len(feedback_entries),
        "avg_satisfaction": round(avg_sat, 2) if avg_sat else None,
        "score_distribution": {str(i): scores.count(i) for i in range(1, 6) if scores.count(i) > 0},
        "comments": comments,
        "insights": [],
    }

    if comments:
        prompt = f"""Analyze these {len(comments)} feedback comments from callers of a Career Coaching Hotline:

{json.dumps(comments, indent=2)}

Average satisfaction: {avg_sat or 'N/A'}/5

Respond with ONLY valid JSON:
{{
  "positive_signals": ["what callers liked"],
  "negative_signals": ["what callers disliked or wanted differently"],
  "suggestions": ["specific improvements based on feedback"],
  "coaching_quality_notes": ["anything about the quality of career advice given"]
}}"""
        insights = zo_ask_json(prompt, token)
        if insights:
            result["insights"] = insights

    return result


def generate_improvements(
    patterns: dict, dropoffs: dict, satisfaction: dict,
    escalations: list[dict], token: str
) -> list[dict]:
    prompt = f"""Based on this daily analysis of a Career Coaching Hotline, generate ranked improvement suggestions.

CALL PATTERNS:
{json.dumps(patterns, indent=2, default=str)}

DROP-OFF ANALYSIS:
{json.dumps(dropoffs, indent=2, default=str)}

SATISFACTION:
{json.dumps(satisfaction, indent=2, default=str)}

ESCALATIONS TO CAREERSPAN: {len(escalations)} requests

Respond with ONLY valid JSON — an array of improvements ranked by impact:
[
  {{
    "rank": 1,
    "title": "Short title",
    "description": "What to change and why",
    "evidence": "What data supports this",
    "category": "greeting|diagnostic|knowledge|escalation|tone|follow_up|other",
    "effort": "low|medium|high",
    "impact": "low|medium|high"
  }}
]"""

    result = zo_ask_json(prompt, token)
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and "improvements" in result:
        return result["improvements"]
    return []


# ---------------------------------------------------------------------------
# Caller insights management
# ---------------------------------------------------------------------------

def update_caller_insights(
    conn: duckdb.DuckDBPyConnection,
    feedback_entries: list[dict],
    calls: list[dict],
) -> None:
    call_lookup = {c["id"]: c for c in calls}

    for f in feedback_entries:
        name = f.get("caller_name")
        if not name:
            continue

        name_lower = name.strip().lower()
        existing = conn.execute(
            "SELECT id, total_calls, avg_satisfaction, topics_discussed, career_stage "
            "FROM caller_insights WHERE LOWER(first_name) = ?",
            [name_lower],
        ).fetchone()

        now = f.get("created_at", datetime.now(timezone.utc).isoformat())
        satisfaction = f.get("satisfaction")
        call_id = f.get("call_id")
        call_topics = None
        call_stage = None
        if call_id and call_id in call_lookup:
            matched = call_lookup[call_id]
            call_topics = matched.get("topics_discussed")
            call_stage = matched.get("career_stage_assessed")

        if existing:
            cid, cnt, prev_avg, prev_topics, prev_stage = existing
            new_count = cnt + 1
            if satisfaction is not None and prev_avg is not None:
                new_avg = ((prev_avg * cnt) + satisfaction) / new_count
            elif satisfaction is not None:
                new_avg = float(satisfaction)
            else:
                new_avg = prev_avg

            new_topics = prev_topics
            if call_topics:
                old_set = set((prev_topics or "").split(", ")) if prev_topics else set()
                new_set = set(t.strip() for t in call_topics.split(",") if t.strip())
                merged = old_set | new_set
                merged.discard("")
                new_topics = ", ".join(sorted(merged)) if merged else prev_topics

            new_stage = call_stage or prev_stage

            conn.execute("""
                UPDATE caller_insights
                SET total_calls = ?, last_call_at = ?, avg_satisfaction = ?,
                    topics_discussed = ?, career_stage = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, [new_count, now, new_avg, new_topics, new_stage, cid])
        else:
            conn.execute("""
                INSERT INTO caller_insights
                (id, first_name, phone, topics_discussed, career_stage,
                 total_calls, avg_satisfaction, first_call_at, last_call_at)
                VALUES (?, ?, NULL, ?, ?, 1, ?, ?, ?)
            """, [str(uuid.uuid4()), name.strip(), call_topics, call_stage,
                  float(satisfaction) if satisfaction else None, now, now])


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    analysis_date: str, period_start: str, period_end: str,
    all_calls: list[dict], patterns: dict, dropoffs: dict,
    satisfaction: dict, improvements: list[dict],
    escalations: list[dict],
) -> str:
    total = len(all_calls)
    sub_count = patterns.get("count", 0)
    drop_count = dropoffs.get("count", 0)
    mid_count = total - sub_count - drop_count
    avg_dur = sum(c["duration_seconds"] for c in all_calls) / total if total else 0
    esc_count = len(escalations)

    lines = [
        "---",
        f"created: {analysis_date}",
        f"last_edited: {analysis_date}",
        "version: 1.0",
        "provenance: call_analysis_loop",
        "---",
        "",
        f"# Career Coaching Hotline — Daily Analysis ({analysis_date})",
        "",
        f"**Period:** {period_start} → {period_end}",
        f"**Total Calls:** {total}",
        f"**Substantive (>2min):** {sub_count}",
        f"**Mid-range:** {mid_count}",
        f"**Drop-offs (<1min):** {drop_count}",
        f"**Avg Duration:** {avg_dur:.0f}s",
        f"**Careerspan Escalations:** {esc_count}",
        "",
        "---",
        "",
    ]

    # Career stage distribution
    stage_dist = patterns.get("career_stage_distribution", {})
    if stage_dist:
        lines.append("## Career Stage Distribution")
        lines.append("")
        lines.append("| Stage | Count |")
        lines.append("|-------|-------|")
        for stage, count in sorted(stage_dist.items(), key=lambda x: -x[1]):
            lines.append(f"| {stage} | {count} |")
        lines.append("")

    # Patterns
    lines.append("## Call Patterns")
    lines.append("")
    if patterns.get("summary"):
        lines.append(f"**Summary:** {patterns['summary']}")
        lines.append("")

    for field in ["common_questions", "topics_that_engaged", "confusion_points",
                  "what_worked_well", "what_fell_flat", "top_pain_points", "careerspan_triggers"]:
        items = patterns.get(field, [])
        if items:
            lines.append(f"### {field.replace('_', ' ').title()}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    # Drop-offs
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

    # Satisfaction
    lines.append("## Satisfaction")
    lines.append("")
    if satisfaction.get("avg_satisfaction") is not None:
        lines.append(f"**Average:** {satisfaction['avg_satisfaction']}/5 ({satisfaction['count']} responses)")
    else:
        lines.append("No feedback data for this period.")
    lines.append("")

    # Improvements
    if improvements:
        lines.append("## Recommended Improvements")
        lines.append("")
        for imp in improvements:
            rank = imp.get("rank", "?")
            title = imp.get("title", "Untitled")
            desc = imp.get("description", "")
            effort = imp.get("effort", "?")
            impact = imp.get("impact", "?")
            cat = imp.get("category", "other")
            lines.append(f"### #{rank}: {title}")
            lines.append(f"**Category:** {cat} | **Effort:** {effort} | **Impact:** {impact}")
            lines.append("")
            lines.append(desc)
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_analysis(analysis_date: str, period_start: str, period_end: str, dry_run: bool = False) -> Optional[str]:
    token = get_zo_token()

    log(f"Analyzing calls from {period_start} to {period_end}")

    if not DB_PATH.exists():
        log(f"ERROR: Database not found at {DB_PATH}")
        return None

    conn = duckdb.connect(str(DB_PATH), read_only=True)
    all_calls = query_calls(conn, period_start, period_end)
    feedback = query_feedback(conn, period_start, period_end)
    escalations = query_escalations(conn, period_start, period_end)
    conn.close()

    log(f"  Found {len(all_calls)} calls, {len(feedback)} feedback, {len(escalations)} escalations")

    if not all_calls:
        log("  No calls in this period. Skipping analysis.")
        return None

    log("  Analyzing substantive calls...")
    patterns = analyze_substantive_calls(all_calls, token)

    log("  Analyzing drop-offs...")
    dropoff_insights = analyze_dropoffs(all_calls, token)

    log("  Analyzing satisfaction...")
    satisfaction = analyze_satisfaction(feedback, token)

    log("  Generating improvements...")
    improvements = generate_improvements(patterns, dropoff_insights, satisfaction, escalations, token)

    report = generate_report(
        analysis_date, period_start, period_end,
        all_calls, patterns, dropoff_insights, satisfaction, improvements, escalations,
    )

    if dry_run:
        log("[DRY RUN] Would write report and DB record. Report preview:")
        print(report)
        return report

    conn = duckdb.connect(str(DB_PATH))

    if feedback:
        log("  Updating caller insights from feedback...")
        update_caller_insights(conn, feedback, all_calls)

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = ANALYSIS_DIR / f"{analysis_date}_daily_analysis.md"
    report_path.write_text(report)
    log(f"  Report written to {report_path}")

    record_id = str(uuid.uuid4())
    avg_dur = sum(c["duration_seconds"] for c in all_calls) / len(all_calls)
    avg_sat = satisfaction.get("avg_satisfaction")
    stage_dist = patterns.get("career_stage_distribution", {})
    topic_freq: dict[str, int] = {}
    for c in all_calls:
        if c.get("topics_discussed"):
            for t in c["topics_discussed"].split(","):
                t = t.strip()
                if t:
                    topic_freq[t] = topic_freq.get(t, 0) + 1

    conn.execute("""
        INSERT INTO daily_analysis
        (id, analysis_date, period_start, period_end, total_calls, substantive_calls,
         dropoff_calls, avg_duration, avg_satisfaction, career_stages_json, topics_json,
         careerspan_conversions, patterns_json, improvements_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        record_id, analysis_date, period_start, period_end,
        len(all_calls), patterns.get("count", 0), dropoff_insights.get("count", 0),
        avg_dur, avg_sat,
        json.dumps(stage_dist, default=str),
        json.dumps(topic_freq, default=str),
        len(escalations),
        json.dumps(patterns, default=str),
        json.dumps(improvements, default=str),
        datetime.now(timezone.utc).isoformat(),
    ])
    log(f"  Analysis stored in daily_analysis table (id: {record_id[:8]})")

    conn.close()

    log(f"  Summary:")
    log(f"    Total calls: {len(all_calls)}")
    log(f"    Substantive (>2min): {patterns.get('count', 0)}")
    log(f"    Drop-offs (<1min): {dropoff_insights.get('count', 0)}")
    log(f"    Feedback entries: {len(feedback)}")
    log(f"    Careerspan escalations: {len(escalations)}")
    log(f"    Improvements generated: {len(improvements)}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Career Coaching Hotline daily call analysis loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Analyze yesterday's calls
  %(prog)s --date 2026-02-14        # Analyze a specific date
  %(prog)s --days 7                 # Analyze last 7 days
  %(prog)s --dry-run                # Preview without writing
""",
    )
    parser.add_argument("--date", help="Specific date to analyze (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=1, help="Number of days to analyze (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB or files")

    args = parser.parse_args()

    if args.date:
        analysis_date = args.date
        period_start = f"{analysis_date} 00:00:00"
        period_end = f"{analysis_date} 23:59:59"
        run_analysis(analysis_date, period_start, period_end, dry_run=args.dry_run)
    else:
        today = datetime.now(timezone.utc).date()
        for i in range(args.days, 0, -1):
            target = today - timedelta(days=i)
            analysis_date = target.isoformat()
            period_start = f"{analysis_date} 00:00:00"
            period_end = f"{analysis_date} 23:59:59"
            run_analysis(analysis_date, period_start, period_end, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
