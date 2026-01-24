#!/usr/bin/env python3
"""
Survey Dashboard Generator for Fundamentals of AI Productivity

Reads Fillout webhook events and generates presentation-ready summaries.
Includes LLM-based semantic clustering for open-ended questions.

Usage:
    # Console output
    python3 survey_dashboard.py
    
    # HTML dashboard
    python3 survey_dashboard.py --html --save dashboard.html
    
    # With semantic clustering (requires ANTHROPIC_API_KEY)
    python3 survey_dashboard.py --cluster
    
    # JSON export for further analysis
    python3 survey_dashboard.py --json
"""

import argparse
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


EVENTS_DIR = Path("/home/workspace/N5/Integrations/fillout/events")

# Question field mappings (adjust based on actual Fillout field names)
QUESTION_MAPPINGS = {
    "biggest_challenge": ["biggest challenge", "challenge", "q1"],
    "usage_level": ["current ai usage", "usage", "q2"],
    "sentiment": ["feel about ai", "sentiment", "q3"],
    "session_value": ["valuable for you", "value", "q4"],
    "repetitive_tasks": ["repetitive tasks", "annoying tasks", "q5"],
    "time_lost": ["time per week", "time lost", "q6"],
    "tools_using": ["tools", "currently using", "q7"],
    "role": ["describe your role", "role", "q8"],
    "seniority": ["senior", "seniority", "q9"],
    "industry": ["industry", "domain", "q10"],
}


def load_all_events() -> list[dict[str, Any]]:
    """Load all submission events from JSONL files."""
    events = []
    if not EVENTS_DIR.exists():
        return events
    
    for jsonl_file in sorted(EVENTS_DIR.glob("*.jsonl")):
        with open(jsonl_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
    return events


def extract_field(submission: dict, field_keys: list[str]) -> Any:
    """Extract a field from submission by trying multiple possible keys."""
    # Handle both nested and flat structures
    questions = submission.get("questions", submission.get("payload", {}).get("questions", []))
    
    if isinstance(questions, list):
        for q in questions:
            q_name = q.get("name", "").lower()
            q_id = q.get("id", "").lower()
            for key in field_keys:
                if key.lower() in q_name or key.lower() in q_id:
                    return q.get("value")
    elif isinstance(questions, dict):
        for key in field_keys:
            for q_key, q_val in questions.items():
                if key.lower() in q_key.lower():
                    return q_val
    
    return None


def extract_submissions(events: list[dict]) -> list[dict]:
    """Extract submission data from events."""
    submissions = []
    for event in events:
        payload = event.get("payload", {})
        submission = payload.get("submission", payload)
        if submission:
            submissions.append(submission)
    return submissions


def summarize_responses(submissions: list[dict]) -> dict[str, Any]:
    """Generate summary statistics from submissions."""
    summary = {
        "total": len(submissions),
        "biggest_challenge": Counter(),
        "usage_level": Counter(),
        "sentiment_scores": [],
        "session_value": Counter(),
        "repetitive_tasks": [],
        "time_lost": Counter(),
        "tools_using": Counter(),
        "roles": [],
        "seniority": Counter(),
        "industries": [],
    }
    
    for sub in submissions:
        # Q1: Biggest challenge
        val = extract_field(sub, QUESTION_MAPPINGS["biggest_challenge"])
        if val:
            summary["biggest_challenge"][str(val)] += 1
        
        # Q2: Usage level
        val = extract_field(sub, QUESTION_MAPPINGS["usage_level"])
        if val:
            summary["usage_level"][str(val)] += 1
        
        # Q3: Sentiment (1-5)
        val = extract_field(sub, QUESTION_MAPPINGS["sentiment"])
        if val:
            try:
                summary["sentiment_scores"].append(float(val))
            except (ValueError, TypeError):
                pass
        
        # Q4: Session value (multi-select)
        val = extract_field(sub, QUESTION_MAPPINGS["session_value"])
        if val:
            if isinstance(val, list):
                for v in val:
                    summary["session_value"][str(v)] += 1
            else:
                summary["session_value"][str(val)] += 1
        
        # Q5: Repetitive tasks (open text)
        val = extract_field(sub, QUESTION_MAPPINGS["repetitive_tasks"])
        if val and str(val).strip():
            summary["repetitive_tasks"].append(str(val).strip())
        
        # Q6: Time lost
        val = extract_field(sub, QUESTION_MAPPINGS["time_lost"])
        if val:
            summary["time_lost"][str(val)] += 1
        
        # Q7: Tools using (multi-select)
        val = extract_field(sub, QUESTION_MAPPINGS["tools_using"])
        if val:
            if isinstance(val, list):
                for v in val:
                    summary["tools_using"][str(v)] += 1
            else:
                summary["tools_using"][str(val)] += 1
        
        # Q8: Role (open text)
        val = extract_field(sub, QUESTION_MAPPINGS["role"])
        if val and str(val).strip():
            summary["roles"].append(str(val).strip())
        
        # Q9: Seniority
        val = extract_field(sub, QUESTION_MAPPINGS["seniority"])
        if val:
            summary["seniority"][str(val)] += 1
        
        # Q10: Industry (open text)
        val = extract_field(sub, QUESTION_MAPPINGS["industry"])
        if val and str(val).strip():
            summary["industries"].append(str(val).strip())
    
    return summary


def cluster_with_llm(texts: list[str], category_name: str, num_clusters: int = 6) -> dict[str, int]:
    """Use LLM to cluster open-ended text responses."""
    if not texts:
        return {}
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback: return raw texts as-is
        return Counter(texts)
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""Analyze these {len(texts)} responses about "{category_name}" and cluster them into {num_clusters} or fewer thematic categories.

Responses:
{chr(10).join(f'- {t}' for t in texts)}

Return ONLY valid JSON in this exact format, no other text:
{{"clusters": [{{"name": "Category Name", "count": 5, "examples": ["example1", "example2"]}}]}}

Rules:
- Category names should be short (2-4 words)
- Each response should be counted in exactly one category
- Include an "Other" category for outliers if needed
- Total counts must equal {len(texts)}"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text
        result = json.loads(result_text)
        
        return {c["name"]: c["count"] for c in result.get("clusters", [])}
    
    except Exception as e:
        print(f"LLM clustering failed: {e}")
        # Fallback: simple word frequency
        return Counter(texts)


def format_bar(count: int, total: int, width: int = 20) -> str:
    """Format a simple text bar chart."""
    if total == 0:
        return ""
    pct = count / total
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {count} ({pct:.0%})"


def format_gauge(score: float, max_score: float = 5) -> str:
    """Format a sentiment gauge."""
    normalized = score / max_score
    width = 20
    filled = int(normalized * width)
    gauge = "▓" * filled + "░" * (width - filled)
    
    if score < 2:
        label = "😰 Anxious"
    elif score < 2.5:
        label = "🤔 Skeptical"
    elif score < 3.5:
        label = "😐 Curious"
    elif score < 4.5:
        label = "😊 Optimistic"
    else:
        label = "🚀 All-in"
    
    return f"[{gauge}] {score:.1f}/5 — {label}"


def render_console(summary: dict[str, Any], clusters: dict[str, dict] = None) -> str:
    """Render dashboard as console output."""
    if summary["total"] == 0:
        return "📊 No survey responses yet.\n"
    
    lines = []
    lines.append("=" * 60)
    lines.append("📊 FUNDAMENTALS OF AI PRODUCTIVITY")
    lines.append(f"   Pre-Session Survey • {summary['total']} responses (anonymous)")
    lines.append("=" * 60)
    lines.append("")
    
    # Who's in the room (Q8, Q9, Q10)
    lines.append("👥 WHO'S IN THE ROOM")
    lines.append("-" * 40)
    
    if summary["seniority"]:
        lines.append("  Seniority:")
        for level, count in summary["seniority"].most_common():
            lines.append(f"    {level}: {format_bar(count, summary['total'], 15)}")
    
    if clusters and "roles" in clusters:
        lines.append("  Roles (clustered):")
        for role, count in sorted(clusters["roles"].items(), key=lambda x: -x[1])[:5]:
            lines.append(f"    {role}: {format_bar(count, summary['total'], 15)}")
    elif summary["roles"]:
        lines.append(f"  Roles: {len(summary['roles'])} unique responses")
    
    if clusters and "industries" in clusters:
        lines.append("  Industries (clustered):")
        for ind, count in sorted(clusters["industries"].items(), key=lambda x: -x[1])[:5]:
            lines.append(f"    {ind}: {format_bar(count, summary['total'], 15)}")
    
    lines.append("")
    
    # Sentiment (Q3)
    lines.append("😊 ROOM SENTIMENT")
    lines.append("-" * 40)
    if summary["sentiment_scores"]:
        avg = sum(summary["sentiment_scores"]) / len(summary["sentiment_scores"])
        lines.append(f"  {format_gauge(avg)}")
    else:
        lines.append("  No sentiment data")
    lines.append("")
    
    # Biggest challenges (Q1)
    lines.append("🎯 BIGGEST CHALLENGES")
    lines.append("-" * 40)
    for challenge, count in summary["biggest_challenge"].most_common(5):
        short = challenge[:40] + "..." if len(challenge) > 40 else challenge
        lines.append(f"  {short}: {format_bar(count, summary['total'], 15)}")
    lines.append("")
    
    # Time lost (Q6)
    lines.append("⏰ TIME LOST TO REPETITIVE TASKS")
    lines.append("-" * 40)
    for time_range, count in summary["time_lost"].most_common():
        lines.append(f"  {time_range}: {format_bar(count, summary['total'], 15)}")
    lines.append("")
    
    # Tools (Q7)
    lines.append("🛠️ TOOLS YOU'RE USING")
    lines.append("-" * 40)
    for tool, count in summary["tools_using"].most_common(8):
        lines.append(f"  {tool}: {format_bar(count, summary['total'], 15)}")
    lines.append("")
    
    # Pain points (Q5)
    lines.append("💬 REPETITIVE TASK PAIN POINTS")
    lines.append("-" * 40)
    if clusters and "repetitive_tasks" in clusters:
        for theme, count in sorted(clusters["repetitive_tasks"].items(), key=lambda x: -x[1])[:6]:
            lines.append(f"  {theme}: {format_bar(count, summary['total'], 15)}")
    elif summary["repetitive_tasks"]:
        lines.append(f"  {len(summary['repetitive_tasks'])} responses (run with --cluster for themes)")
    lines.append("")
    
    # What they want (Q4)
    lines.append("📋 WHAT YOU WANT FROM TODAY")
    lines.append("-" * 40)
    total_selections = sum(summary["session_value"].values())
    for want, count in summary["session_value"].most_common():
        short = want[:35] + "..." if len(want) > 35 else want
        lines.append(f"  {short}: {format_bar(count, total_selections, 15)}")
    lines.append("")
    
    lines.append("=" * 60)
    return "\n".join(lines)


def render_html(summary: dict[str, Any], clusters: dict[str, dict] = None) -> str:
    """Render dashboard as HTML."""
    sentiment_avg = 0
    if summary["sentiment_scores"]:
        sentiment_avg = sum(summary["sentiment_scores"]) / len(summary["sentiment_scores"])
    
    # Prepare data for charts
    def to_js_data(counter: Counter) -> str:
        return json.dumps([{"label": k, "value": v} for k, v in counter.most_common()])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fundamentals of AI Productivity — Survey Results</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 2rem;
        }}
        .dashboard {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ 
            font-size: 2.5rem; 
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{ color: #888; margin-bottom: 2rem; font-size: 1.1rem; }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 1.5rem; 
        }}
        .card {{ 
            background: rgba(255,255,255,0.05); 
            border-radius: 16px; 
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h2 {{ 
            font-size: 1rem; 
            color: #888; 
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .gauge {{ 
            text-align: center; 
            padding: 2rem 0;
        }}
        .gauge-value {{ 
            font-size: 4rem; 
            font-weight: 700;
            background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .gauge-label {{ color: #888; margin-top: 0.5rem; font-size: 1.2rem; }}
        .stat-row {{ display: flex; justify-content: space-between; margin-bottom: 0.5rem; }}
        .stat-label {{ color: #aaa; }}
        .stat-bar {{ 
            height: 8px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 4px;
            overflow: hidden;
            margin-top: 4px;
        }}
        .stat-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }}
        .big-number {{ font-size: 3rem; font-weight: 700; color: #667eea; }}
        canvas {{ max-height: 250px; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📊 Fundamentals of AI Productivity</h1>
        <p class="subtitle">Pre-Session Survey • {summary['total']} responses (anonymous)</p>
        
        <div class="grid">
            <div class="card">
                <h2>😊 Room Sentiment</h2>
                <div class="gauge">
                    <div class="gauge-value">{sentiment_avg:.1f}</div>
                    <div class="gauge-label">out of 5 — {"😰 Anxious" if sentiment_avg < 2 else "🤔 Skeptical" if sentiment_avg < 2.5 else "😐 Curious" if sentiment_avg < 3.5 else "😊 Optimistic" if sentiment_avg < 4.5 else "🚀 All-in"}</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Biggest Challenges</h2>
                <canvas id="challengesChart"></canvas>
            </div>
            
            <div class="card">
                <h2>⏰ Time Lost Weekly</h2>
                <canvas id="timeLostChart"></canvas>
            </div>
            
            <div class="card">
                <h2>🛠️ Tools You're Using</h2>
                <canvas id="toolsChart"></canvas>
            </div>
            
            <div class="card">
                <h2>👥 Seniority Mix</h2>
                <canvas id="seniorityChart"></canvas>
            </div>
            
            <div class="card">
                <h2>📋 What You Want</h2>
                <canvas id="wantChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        const chartColors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'];
        
        function createPieChart(id, data) {{
            new Chart(document.getElementById(id), {{
                type: 'doughnut',
                data: {{
                    labels: data.map(d => d.label.substring(0, 30)),
                    datasets: [{{
                        data: data.map(d => d.value),
                        backgroundColor: chartColors,
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ position: 'right', labels: {{ color: '#aaa' }} }} }}
                }}
            }});
        }}
        
        function createBarChart(id, data) {{
            new Chart(document.getElementById(id), {{
                type: 'bar',
                data: {{
                    labels: data.map(d => d.label.substring(0, 25)),
                    datasets: [{{
                        data: data.map(d => d.value),
                        backgroundColor: '#667eea',
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#aaa' }}, grid: {{ color: 'rgba(255,255,255,0.1)' }} }},
                        y: {{ ticks: {{ color: '#aaa' }}, grid: {{ display: false }} }}
                    }}
                }}
            }});
        }}
        
        createPieChart('challengesChart', {to_js_data(summary['biggest_challenge'])});
        createPieChart('timeLostChart', {to_js_data(summary['time_lost'])});
        createBarChart('toolsChart', {to_js_data(summary['tools_using'])});
        createPieChart('seniorityChart', {to_js_data(summary['seniority'])});
        createBarChart('wantChart', {to_js_data(summary['session_value'])});
    </script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate survey dashboard")
    parser.add_argument("--html", action="store_true", help="Generate HTML output")
    parser.add_argument("--json", action="store_true", help="Export as JSON")
    parser.add_argument("--cluster", action="store_true", help="Use LLM to cluster open-ended responses")
    parser.add_argument("--save", type=str, help="Save output to file")
    args = parser.parse_args()
    
    events = load_all_events()
    submissions = extract_submissions(events)
    summary = summarize_responses(submissions)
    
    clusters = None
    if args.cluster and summary["total"] > 0:
        clusters = {}
        if summary["repetitive_tasks"]:
            clusters["repetitive_tasks"] = cluster_with_llm(
                summary["repetitive_tasks"], "repetitive professional tasks"
            )
        if summary["roles"]:
            clusters["roles"] = cluster_with_llm(
                summary["roles"], "professional roles/titles"
            )
        if summary["industries"]:
            clusters["industries"] = cluster_with_llm(
                summary["industries"], "industries/domains"
            )
    
    if args.json:
        output = json.dumps({"summary": summary, "clusters": clusters}, indent=2, default=str)
    elif args.html:
        output = render_html(summary, clusters)
    else:
        output = render_console(summary, clusters)
    
    if args.save:
        Path(args.save).write_text(output)
        print(f"Saved to {args.save}")
    else:
        print(output)


if __name__ == "__main__":
    main()
