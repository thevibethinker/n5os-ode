#!/usr/bin/env python3
"""
Survey Dashboard Generator using Plotly

Generates interactive HTML dashboards for survey analysis with:
- Response timeline
- Distribution charts
- Scale visualizations
- Key metrics cards
- Level Upper insights section

Usage:
    python3 generate_dashboard.py <formId> [--output path/to/dashboard.html]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import plotly.graph_objects as go


def load_analysis(form_id: str, analysis_path: Optional[str] = None) -> Dict[str, Any]:
    """Load quantitative analysis data."""
    if analysis_path:
        path = Path(analysis_path)
    else:
        # Default to survey-analyses data.json
        path = Path(f"/home/workspace/Datasets/survey-analyses/{form_id}/data.json")

    if not path.exists():
        print(f"Error: Analysis data not found at {path}")
        sys.exit(1)

    return json.loads(path.read_text(encoding="utf-8"))


def create_distribution_chart(q_data: Dict[str, Any], q_id: str) -> go.Figure:
    """Create bar chart for categorical question distribution."""
    distribution = q_data.get("distribution", {})
    percentages = q_data.get("percentage", {})
    question_text = q_data.get("question_text", q_id)

    if not distribution:
        fig = go.Figure()
        fig.add_annotation(
            text="No responses",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        return fig

    labels = list(distribution.keys())
    values = list(distribution.values())
    percs = list(percentages.values())

    # Use bar chart for better readability with many options
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        text=[f"{v} ({p}%)" for v, p in zip(values, percs)],
        textposition="outside",
        marker_color="#3b82f6"
    ))

    fig.update_layout(
        title=question_text[:80] + "..." if len(question_text) > 80 else question_text,
        xaxis_title="Count",
        yaxis_title="",
        showlegend=False,
        template="plotly_white",
        height=max(200, len(labels) * 35 + 100)
    )

    return fig


def create_level_upper_section(lu_data: Dict[str, Any]) -> go.Figure:
    """Create highlighted section for Level Upper insights."""
    perspectives = lu_data.get("novel_perspectives", [])
    challenged = lu_data.get("challenged_assumptions", [])

    fig = go.Figure()

    # Build HTML content
    html_content = """
    <div style="background-color: #fef3c7; padding: 20px; border-radius: 10px; border-left: 5px solid #f59e0b;">
        <h3 style="color: #92400e; margin-top: 0;">🔮 Level Upper Insights</h3>
    """

    if perspectives:
        html_content += "<h4 style='color: #b45309;'>Novel Perspectives:</h4><ul>"
        for p in perspectives:
            insight = p.get("insight", "")
            confidence = p.get("confidence", "")
            html_content += f"<li><strong>{insight}</strong><br/><small>Confidence: {confidence}</small></li>"
        html_content += "</ul>"

    if challenged:
        html_content += "<h4 style='color: #b45309;'>Challenged Assumptions:</h4><ul>"
        for c in challenged:
            assumption = c.get("assumption", "")
            challenge = c.get("challenge", "")
            html_content += f"<li><em>{assumption}</em><br/>Challenge: {challenge}</li>"
        html_content += "</ul>"

    html_content += "</div>"

    fig.add_annotation(
        text=html_content,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        align="left"
          )

    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=max(200, len(perspectives) * 60 + len(challenged) * 50 + 150),
        paper_bgcolor="#fffbeb"
    )

    return fig


def generate_dashboard(form_id: str, analysis_data: Dict[str, Any]) -> str:
    """Generate full dashboard HTML string."""

    # Extract nested data structures
    d1_2 = analysis_data.get("d1_2", {})
    d1_3 = analysis_data.get("d1_3", {})
    
    # Get quantitative analysis from d1_2
    qa = d1_2.get("quantitative_analysis", {})
    qa_analysis = qa if isinstance(qa, dict) else {}
    
    # Get form info
    form_title = qa.get("form_title", analysis_data.get("form_name", "Survey Analysis"))
    total_submissions = qa.get("total_submissions", 0)
    filtered_submissions = qa.get("filtered_submissions", 0)
    analysis_timestamp = qa.get("analysis_timestamp", "Unknown")
    
    # Get summaries
    summaries = qa_analysis.get("question_summaries", {})
    
    # Get Level Upper data
    lu_data = None
    if isinstance(d1_3, dict):
        lu_data = d1_3.get("level_upper_analysis", {})

    # Create metrics cards
    metrics_cards = []
    
    # Total Responses
    fig0 = go.Figure()
    fig0.add_annotation(
        text=f"<b>Total Responses</b><br><span style='font-size:32px; color:#2563eb'>{total_submissions}</span>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e5e7eb",
        borderwidth=2,
        borderpad=10
    )
    fig0.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="#f9fafb",
        height=100,
        plot_bgcolor="#f9fafb"
    )
    metrics_cards.append(fig0)
    
    # Eligible Responses
    fig1 = go.Figure()
    fig1.add_annotation(
        text=f"<b>Eligible Responses</b><br><span style='font-size:32px; color:#16a34a'>{filtered_submissions}</span>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e5e7eb",
        borderwidth=2,
        borderpad=10
    )
    fig1.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="#f9fafb",
        height=100,
        plot_bgcolor="#f9fafb"
    )
    metrics_cards.append(fig1)

    # Build HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        f"    <title>{form_title}</title>",
        "    <script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>",
        "    <style>",
        "        body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f8fafc; }",
        "        .header { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }",
        "        .metrics-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }",
        "        .chart-container { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }",
        "        .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }",
        "        h1 { margin: 0 0 10px 0; color: #1e293b; }",
        "        h2 { margin: 0 0 15px 0; color: #334155; font-size: 1.2rem; }",
        "        .timestamp { color: #64748b; font-size: 0.9rem; }",
        "    </style>",
        "</head>",
        "<body>",
        f"    <div class='header'>",
        f"        <h1>{form_title}</h1>",
        f"        <p class='timestamp'>Form ID: {form_id} | Analysis: {analysis_timestamp}</p>",
        f"        <p><strong>{total_submissions}</strong> total responses, <strong>{filtered_submissions}</strong> eligible</p>",
        f"    </div>",
        "    <div class='metrics-row'>",
    ]

    # Add metrics cards divs
    for i in range(len(metrics_cards)):
        html_parts.append(f"        <div id='metric-{i}'></div>")

    html_parts.extend([
        "    </div>",
        "",
    ])

    # Add distribution charts
    charts = []
    for q_id, q_data in summaries.items():
        q_type = q_data.get("question_type", "")
        if q_type in ["multiple_choice", "checkboxes"]:
            fig = create_distribution_chart(q_data, q_id)
            if fig:
                charts.append((q_id, fig))

    # Add charts grid
    if charts:
        html_parts.extend([
            "    <div class='chart-grid'>",
        ])

        for q_id, chart_fig in charts:
            chart_title = chart_fig.layout.title.text if hasattr(chart_fig.layout, 'title') else q_id
            html_parts.extend([
                f"        <div class='chart-container'>",
                f"            <h3>{chart_title}</h3>",
                f"            <div id='chart-{q_id}'></div>",
                f"        </div>",
            ])

        html_parts.extend([
            "    </div>",
            "",
        ])

    # Add Level Upper section
    if lu_data:
        lu_fig = create_level_upper_section(lu_data)
        html_parts.extend([
            "    <div class='chart-container'>",
            "        <h2>🔮 Level Upper Insights</h2>",
            "        <div id='level-upper'></div>",
            "    </div>",
            "",
        ])

    # Add scripts section
    html_parts.extend([
        "    <script>",
    ])

    # Add Plotly renders
    for i, card_fig in enumerate(metrics_cards):
        html_parts.append(f"        Plotly.newPlot('metric-{i}', {card_fig.to_json()});")

    for q_id, chart_fig in charts:
        html_parts.append(f"        Plotly.newPlot('chart-{q_id}', {chart_fig.to_json()});")

    if lu_data:
        html_parts.append(f"        Plotly.newPlot('level-upper', {lu_fig.to_json()});")

    html_parts.extend([
        "    </script>",
        "</body>",
        "</html>",
    ])

    return "\n".join(html_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive survey analysis dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "form_id",
        help="Fillout form ID"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output HTML path (default: Datasets/survey-analyses/<form_id>/dashboard.html)"
    )
    parser.add_argument(
        "--analysis",
        default=None,
        help="Path to analysis JSON (default: Datasets/survey-analyses/<form_id>/data.json)"
    )
    parser.add_argument(
        "--level-upper",
        default=None,
        help="Path to (default: Datasets/survey-analyses/<form_id>/data.json)"
    )

    args = parser.parse_args()

    # Load analysis data
    analysis_data = load_analysis(args.form_id, args.analysis)

    # Generate dashboard
    html = generate_dashboard(args.form_id, analysis_data)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(f"/home/workspace/Datasets/survey-analyses/{args.form_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "dashboard.html"

    # Write output
    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard generated: {output_path}")


if __name__ == "__main__":
    main()
