import logging
from datetime import date, timedelta
from pathlib import Path

from flask import Flask, send_from_directory, render_template_string

import workout_dashboard


app = Flask(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(message)s",
    )


@app.route("/")
def index() -> str:
    """Simple HTML dashboard over workouts.db.

    Reuses the same logic as workout_dashboard.py to compute summaries and
    regenerate graphs on each page load.
    """

    conn = workout_dashboard.get_connection()
    today = date.today()

    # Workout window: 12 weeks, same default as CLI
    since = today - timedelta(weeks=12)
    rows = workout_dashboard.load_workouts(conn, since)

    if not rows:
        workout_summary = "No workouts found in the selected window."
        metrics_summary = workout_dashboard.build_metrics_summary(conn, today)
        graphs = {}
    else:
        goals = workout_dashboard.Goals(weekly_minutes=90.0, weekly_days=2)
        weekly_minutes, weekly_days = workout_dashboard.summarize_weekly(rows)
        rolling = workout_dashboard.summarize_rolling_7d(rows)

        # HR/sleep metrics: last ~60 days
        metrics_since = today - timedelta(days=60)
        rest_rows = workout_dashboard.load_resting_hr(conn, metrics_since)
        sleep_rows = workout_dashboard.load_sleep(conn, metrics_since)

        outdir = workout_dashboard.ensure_graphs_dir()

        weekly_minutes_path = workout_dashboard.plot_weekly_minutes(weekly_minutes, goals, outdir)
        weekly_days_path = workout_dashboard.plot_weekly_days(weekly_days, goals, outdir)
        rolling_path = workout_dashboard.plot_rolling_7d(rolling, goals, outdir)
        resting_hr_path = workout_dashboard.plot_resting_hr_trend(rest_rows, outdir)
        sleep_score_path, sleep_duration_path = workout_dashboard.plot_sleep_trends(sleep_rows, outdir)

        workout_summary = workout_dashboard.build_summary(weekly_minutes, weekly_days, goals)
        metrics_summary = workout_dashboard.build_metrics_summary(conn, today)

        graphs = {
            "weekly_minutes": Path(weekly_minutes_path).name,
            "weekly_days": Path(weekly_days_path).name,
            "rolling_7d": Path(rolling_path).name,
            "resting_hr": Path(resting_hr_path).name if resting_hr_path is not None else None,
            "sleep_score": Path(sleep_score_path).name if sleep_score_path is not None else None,
            "sleep_duration": Path(sleep_duration_path).name if sleep_duration_path is not None else None,
        }

    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Health Dashboard</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; }
    h1, h2 { margin-bottom: 0.5rem; }
    pre { background: #f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; }
    .graphs { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1.5rem; margin-top: 1.5rem; }
    .graph-card { border: 1px solid #ddd; border-radius: 6px; padding: 1rem; }
    .graph-card h3 { margin-top: 0; margin-bottom: 0.5rem; }
    img { max-width: 100%; height: auto; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Health Dashboard</h1>

  <h2>Workout summary</h2>
  <pre>{{ workout_summary }}</pre>

  <h2>HR & Sleep summary</h2>
  <pre>{{ metrics_summary }}</pre>

  <div class="graphs">
    {% if graphs.weekly_minutes %}
    <div class="graph-card">
      <h3>Weekly minutes</h3>
      <img src="/graphs/{{ graphs.weekly_minutes }}" alt="Weekly minutes graph">
    </div>
    {% endif %}

    {% if graphs.weekly_days %}
    <div class="graph-card">
      <h3>Workout days per week</h3>
      <img src="/graphs/{{ graphs.weekly_days }}" alt="Weekly days graph">
    </div>
    {% endif %}

    {% if graphs.rolling_7d %}
    <div class="graph-card">
      <h3>Rolling 7-day minutes</h3>
      <img src="/graphs/{{ graphs.rolling_7d }}" alt="Rolling 7-day graph">
    </div>
    {% endif %}

    {% if graphs.resting_hr %}
    <div class="graph-card">
      <h3>Resting heart rate</h3>
      <img src="/graphs/{{ graphs.resting_hr }}" alt="Resting HR graph">
    </div>
    {% endif %}

    {% if graphs.sleep_score %}
    <div class="graph-card">
      <h3>Sleep score</h3>
      <img src="/graphs/{{ graphs.sleep_score }}" alt="Sleep score graph">
    </div>
    {% endif %}

    {% if graphs.sleep_duration %}
    <div class="graph-card">
      <h3>Sleep duration</h3>
      <img src="/graphs/{{ graphs.sleep_duration }}" alt="Sleep duration graph">
    </div>
    {% endif %}
  </div>
</body>
</html>
"""

    return render_template_string(
        template,
        workout_summary=workout_summary,
        metrics_summary=metrics_summary,
        graphs=type("G", (), graphs)(),  # simple attribute-style access
    )


@app.route("/graphs/<path:filename>")
def graphs(filename: str):
    """Serve generated graph PNGs from the shared graphs directory."""

    graphs_dir = workout_dashboard.GRAPHS_DIR
    return send_from_directory(graphs_dir, filename)


if __name__ == "__main__":
    setup_logging()
    app.run(host="0.0.0.0", port=8010)

