import argparse
import logging
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import matplotlib

# Use non-interactive backend for headless environments
matplotlib.use("Agg")  # type: ignore
import matplotlib.pyplot as plt  # noqa: E402

DB_PATH = Path("/home/workspace/Personal/Health/workouts.db")
GRAPHS_DIR = Path("/home/workspace/Personal/Health/WorkoutTracker/graphs")


@dataclass
class Goals:
    weekly_minutes: float = 90.0
    weekly_days: int = 2


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(message)s",
    )


def get_connection() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_workouts(conn: sqlite3.Connection, since: date) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT date, duration_min, primary_modality
        FROM workouts
        WHERE date >= ?
        ORDER BY date ASC
        """,
        (since.isoformat(),),
    )
    rows = cur.fetchall()
    logging.info("Loaded %d workouts from %s onward", len(rows), since.isoformat())
    return rows


def load_resting_hr(conn: sqlite3.Connection, since: date) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT date, resting_hr
        FROM daily_resting_hr
        WHERE date >= ? AND resting_hr IS NOT NULL
        ORDER BY date ASC
        """,
        (since.isoformat(),),
    )
    rows = cur.fetchall()
    logging.info("Loaded %d resting HR points from %s onward", len(rows), since.isoformat())
    return rows


def load_sleep(conn: sqlite3.Connection, since: date) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT date, sleep_score, minutes_asleep
        FROM daily_sleep
        WHERE date >= ? AND (sleep_score IS NOT NULL OR minutes_asleep IS NOT NULL)
        ORDER BY date ASC
        """,
        (since.isoformat(),),
    )
    rows = cur.fetchall()
    logging.info("Loaded %d sleep points from %s onward", len(rows), since.isoformat())
    return rows


def _parse_date(d: str) -> date:
    # Dates are stored as YYYY-MM-DD
    return datetime.strptime(d, "%Y-%m-%d").date()


def summarize_weekly(rows: List[sqlite3.Row]) -> Tuple[List[Tuple[date, float]], List[Tuple[date, int]]]:
    """Return (weekly_minutes, weekly_active_days).

    Weeks are grouped by ISO week (year, week), represented by the Monday of that week.
    """

    minutes_by_week: Dict[Tuple[int, int], float] = defaultdict(float)
    days_by_week: Dict[Tuple[int, int], set] = defaultdict(set)

    for r in rows:
        d = _parse_date(r["date"])
        mins = r["duration_min"] or 0.0
        iso_year, iso_week, _ = d.isocalendar()
        key = (iso_year, iso_week)
        minutes_by_week[key] += float(mins)
        days_by_week[key].add(d)

    # Convert to sorted lists keyed by week start date (Monday)
    weekly_minutes: List[Tuple[date, float]] = []
    weekly_days: List[Tuple[date, int]] = []

    for (y, w) in sorted(minutes_by_week.keys()):
        week_start = date.fromisocalendar(y, w, 1)  # Monday
        weekly_minutes.append((week_start, minutes_by_week[(y, w)]))
        weekly_days.append((week_start, len(days_by_week[(y, w)])))

    return weekly_minutes, weekly_days


def _week_positions_and_labels(weeks: List[date]) -> Tuple[List[int], List[str]]:
    """Return integer x-positions and YYYY-MM-DD labels for weekly bar charts.

    This keeps the x-axis aligned 1:1 with each Monday week-start and avoids
    Matplotlib's automatic date locators picking confusing tick locations.
    """

    x = list(range(len(weeks)))
    labels = [d.strftime("%Y-%m-%d") for d in weeks]
    return x, labels


def summarize_rolling_7d(rows: List[sqlite3.Row]) -> List[Tuple[date, float]]:
    """Compute rolling 7-day total minutes for each day with any workout.

    We consider a window [d-6, d].
    """

    by_date: Dict[date, float] = defaultdict(float)
    for r in rows:
        d = _parse_date(r["date"])
        by_date[d] += float(r["duration_min"] or 0.0)

    if not by_date:
        return []

    all_dates = sorted(by_date.keys())
    start = all_dates[0]
    end = all_dates[-1]

    day = start
    result: List[Tuple[date, float]] = []
    window: List[Tuple[date, float]] = []

    while day <= end:
        # Add today's minutes (0 if none)
        today_minutes = by_date.get(day, 0.0)
        window.append((day, today_minutes))
        # Drop entries older than 6 days
        cutoff = day - timedelta(days=6)
        window = [(d, m) for (d, m) in window if d >= cutoff]
        total = sum(m for (_, m) in window)
        result.append((day, total))
        day += timedelta(days=1)

    return result


def ensure_graphs_dir() -> Path:
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    return GRAPHS_DIR


def plot_weekly_minutes(weekly_minutes: List[Tuple[date, float]], goals: Goals, outdir: Path) -> Path:
    if not weekly_minutes:
        raise SystemExit("No weekly data available to plot.")

    weeks = [d for (d, _) in weekly_minutes]
    mins = [m for (_, m) in weekly_minutes]
    x, labels = _week_positions_and_labels(weeks)

    plt.figure(figsize=(10, 5))
    bars = plt.bar(x, mins, width=0.8, label="Weekly minutes")

    # Color-code vs goal
    for bar, value in zip(bars, mins):
        if value >= goals.weekly_minutes:
            bar.set_color("#2ca02c")  # green
        else:
            bar.set_color("#d62728")  # red

    plt.axhline(goals.weekly_minutes, color="gray", linestyle="--", label=f"Goal {goals.weekly_minutes:.0f} min")
    plt.title("Weekly workout minutes")
    plt.xlabel("Week starting (Monday)")
    plt.ylabel("Minutes")
    plt.xticks(x, labels, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    outpath = outdir / "weekly_minutes.png"
    plt.savefig(outpath)
    plt.close()

    logging.info("Saved weekly minutes graph to %s", outpath)
    return outpath


def plot_weekly_days(weekly_days: List[Tuple[date, int]], goals: Goals, outdir: Path) -> Path:
    if not weekly_days:
        raise SystemExit("No weekly data available to plot.")

    weeks = [d for (d, _) in weekly_days]
    days = [c for (_, c) in weekly_days]
    x, labels = _week_positions_and_labels(weeks)

    plt.figure(figsize=(10, 5))
    bars = plt.bar(x, days, width=0.8, label="Active days")

    for bar, value in zip(bars, days):
        if value >= goals.weekly_days:
            bar.set_color("#2ca02c")
        else:
            bar.set_color("#d62728")

    plt.axhline(goals.weekly_days, color="gray", linestyle="--", label=f"Goal {goals.weekly_days} days")
    plt.title("Workout days per week")
    plt.xlabel("Week starting (Monday)")
    plt.ylabel("Days with any workout")
    plt.xticks(x, labels, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    outpath = outdir / "weekly_days.png"
    plt.savefig(outpath)
    plt.close()

    logging.info("Saved weekly days graph to %s", outpath)
    return outpath


def plot_rolling_7d(rolling: List[Tuple[date, float]], goals: Goals, outdir: Path) -> Path:
    if not rolling:
        raise SystemExit("No rolling 7-day data available to plot.")

    days = [d for (d, _) in rolling]
    totals = [m for (_, m) in rolling]

    plt.figure(figsize=(10, 5))
    plt.plot(days, totals, label="Rolling 7-day minutes", color="#1f77b4")
    plt.axhline(goals.weekly_minutes, color="gray", linestyle="--", label=f"Weekly goal {goals.weekly_minutes:.0f} min")
    plt.title("Rolling 7-day workout minutes")
    plt.xlabel("Date")
    plt.ylabel("Minutes (last 7 days)")
    plt.legend()
    plt.tight_layout()

    outpath = outdir / "rolling_7d_minutes.png"
    plt.savefig(outpath)
    plt.close()

    logging.info("Saved rolling 7-day graph to %s", outpath)
    return outpath


def plot_resting_hr_trend(rest_rows: List[sqlite3.Row], outdir: Path) -> Optional[Path]:
    if not rest_rows:
        logging.info("No resting HR data to plot; skipping resting HR graph.")
        return None

    dates = [_parse_date(r["date"]) for r in rest_rows]
    values = [float(r["resting_hr"]) for r in rest_rows]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, values, marker="o", label="Resting HR")
    plt.title("Resting heart rate (last ~60 days)")
    plt.xlabel("Date")
    plt.ylabel("BPM")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    outpath = outdir / "resting_hr_trend.png"
    plt.savefig(outpath)
    plt.close()

    logging.info("Saved resting HR trend graph to %s", outpath)
    return outpath


def plot_sleep_trends(sleep_rows: List[sqlite3.Row], outdir: Path) -> Tuple[Optional[Path], Optional[Path]]:
    if not sleep_rows:
        logging.info("No sleep data to plot; skipping sleep graphs.")
        return None, None

    dates = [_parse_date(r["date"]) for r in sleep_rows]
    scores = [r["sleep_score"] for r in sleep_rows]
    minutes_asleep = [r["minutes_asleep"] for r in sleep_rows]

    # Sleep score trend
    score_outpath: Optional[Path] = None
    if any(s is not None for s in scores):
        plt.figure(figsize=(10, 4))
        plt.plot(dates, [float(s) if s is not None else float("nan") for s in scores], marker="o", label="Sleep score")
        plt.title("Sleep score (last ~60 days)")
        plt.xlabel("Date")
        plt.ylabel("Score")
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        score_outpath = outdir / "sleep_score_trend.png"
        plt.savefig(score_outpath)
        plt.close()
        logging.info("Saved sleep score trend graph to %s", score_outpath)

    # Sleep duration trend (hours)
    dur_outpath: Optional[Path] = None
    if any(m is not None for m in minutes_asleep):
        hours = [
            (float(m) / 60.0) if m is not None else float("nan")
            for m in minutes_asleep
        ]
        plt.figure(figsize=(10, 4))
        plt.plot(dates, hours, marker="o", label="Hours asleep")
        plt.title("Sleep duration (last ~60 days)")
        plt.xlabel("Date")
        plt.ylabel("Hours asleep")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        dur_outpath = outdir / "sleep_duration_trend.png"
        plt.savefig(dur_outpath)
        plt.close()
        logging.info("Saved sleep duration trend graph to %s", dur_outpath)

    return score_outpath, dur_outpath


def build_summary(weekly_minutes: List[Tuple[date, float]], weekly_days: List[Tuple[date, int]], goals: Goals) -> str:
    if not weekly_minutes:
        return "No workout data available for the selected window."

    total_weeks = len(weekly_minutes)
    weeks_meeting_minutes = sum(1 for (_, m) in weekly_minutes if m >= goals.weekly_minutes)
    weeks_meeting_days = sum(1 for (_, dcount) in weekly_days if dcount >= goals.weekly_days)

    last_week_start, last_week_minutes = weekly_minutes[-1]
    _, last_week_days = weekly_days[-1]

    return (
        f"Weeks in window: {total_weeks}\n"
        f"Weeks meeting minutes goal ({goals.weekly_minutes:.0f}): {weeks_meeting_minutes}/{total_weeks}\n"
        f"Weeks meeting days goal ({goals.weekly_days}): {weeks_meeting_days}/{total_weeks}\n"
        f"Last week starting {last_week_start}: {last_week_minutes:.1f} minutes over {last_week_days} day(s)."
    )


def build_metrics_summary(conn: sqlite3.Connection, today: date) -> str:
    """Summarize resting HR and sleep over the last 30 days vs prior 30 days."""

    lines: List[str] = []

    # Resting HR: last 30 days vs prior 30 days
    this_start = today - timedelta(days=29)
    prev_start = this_start - timedelta(days=30)
    prev_end = this_start - timedelta(days=1)

    cur = conn.cursor()
    cur.execute(
        "SELECT AVG(resting_hr) FROM daily_resting_hr WHERE date BETWEEN ? AND ?",
        (this_start.isoformat(), today.isoformat()),
    )
    (this_avg_hr,) = cur.fetchone()

    cur.execute(
        "SELECT AVG(resting_hr) FROM daily_resting_hr WHERE date BETWEEN ? AND ?",
        (prev_start.isoformat(), prev_end.isoformat()),
    )
    (prev_avg_hr,) = cur.fetchone()

    if this_avg_hr is not None:
        line = f"Resting HR (last 30 days): {this_avg_hr:.1f} bpm"
        if prev_avg_hr is not None:
            diff = float(this_avg_hr) - float(prev_avg_hr)
            if abs(diff) >= 0.5:
                direction = "higher" if diff > 0 else "lower"
                line += f" ({abs(diff):.1f} bpm {direction} than prior 30 days)"
        lines.append(line)
    else:
        lines.append("Resting HR: no data in the last 60 days.")

    # Sleep: average score + hours asleep/night over last 30 days
    cur.execute(
        "SELECT AVG(sleep_score), AVG(minutes_asleep) FROM daily_sleep WHERE date BETWEEN ? AND ?",
        (this_start.isoformat(), today.isoformat()),
    )
    row = cur.fetchone()
    avg_score, avg_minutes_asleep = row if row is not None else (None, None)

    if avg_score is not None or avg_minutes_asleep is not None:
        parts = ["Sleep (last 30 days):"]
        if avg_score is not None:
            parts.append(f"avg score {float(avg_score):.1f}")
        if avg_minutes_asleep is not None:
            hours = float(avg_minutes_asleep) / 60.0
            parts.append(f"avg {hours:.1f} h asleep/night")
        lines.append(" ".join(parts))
    else:
        lines.append("Sleep: no data in the last 30 days.")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Workout dashboard graphs")
    parser.add_argument(
        "--weeks",
        type=int,
        default=12,
        help="Number of weeks back from today to include (default: 12)",
    )
    parser.add_argument(
        "--weekly-minutes-goal",
        type=float,
        default=90.0,
        help="Weekly minutes goal (default: 90)",
    )
    parser.add_argument(
        "--weekly-days-goal",
        type=int,
        default=2,
        help="Weekly workout days goal (default: 2)",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()

    goals = Goals(
        weekly_minutes=args.weekly_minutes_goal,
        weekly_days=args.weekly_days_goal,
    )

    window_weeks = max(1, args.weeks)
    today = date.today()
    since = today - timedelta(weeks=window_weeks)

    conn = get_connection()
    rows = load_workouts(conn, since)
    if not rows:
        print("No workouts found in the selected window.")
        return

    weekly_minutes, weekly_days = summarize_weekly(rows)
    rolling = summarize_rolling_7d(rows)

    # HR/sleep metrics: look back ~60 days so we can compare last 30 vs prior 30.
    metrics_since = today - timedelta(days=60)
    rest_rows = load_resting_hr(conn, metrics_since)
    sleep_rows = load_sleep(conn, metrics_since)

    outdir = ensure_graphs_dir()

    weekly_minutes_path = plot_weekly_minutes(weekly_minutes, goals, outdir)
    weekly_days_path = plot_weekly_days(weekly_days, goals, outdir)
    rolling_path = plot_rolling_7d(rolling, goals, outdir)

    resting_hr_path = plot_resting_hr_trend(rest_rows, outdir)
    sleep_score_path, sleep_duration_path = plot_sleep_trends(sleep_rows, outdir)

    summary = build_summary(weekly_minutes, weekly_days, goals)
    metrics_summary = build_metrics_summary(conn, today)

    print("Dashboard generated.")
    print("Graphs:")
    print(f"  Weekly minutes: {weekly_minutes_path}")
    print(f"  Weekly days:    {weekly_days_path}")
    print(f"  Rolling 7-day:  {rolling_path}")
    if resting_hr_path is not None:
        print(f"  Resting HR:      {resting_hr_path}")
    if sleep_score_path is not None:
        print(f"  Sleep score:     {sleep_score_path}")
    if sleep_duration_path is not None:
        print(f"  Sleep duration:  {sleep_duration_path}")
    print()
    print("Workout summary:")
    print(summary)
    print()
    print("HR & Sleep summary:")
    print(metrics_summary)


if __name__ == "__main__":
    main()



