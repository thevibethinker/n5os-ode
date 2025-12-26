import tempfile
from datetime import date
from pathlib import Path
import unittest

from workout_dashboard import Goals, _week_positions_and_labels, plot_weekly_minutes, plot_weekly_days


class WeeklyAxisHelperTests(unittest.TestCase):
    def test_week_positions_and_labels_match_weeks(self) -> None:
        weeks = [
            date(2025, 11, 3),
            date(2025, 11, 10),
            date(2025, 11, 17),
        ]
        x, labels = _week_positions_and_labels(weeks)

        self.assertEqual(x, [0, 1, 2])
        self.assertEqual(labels, ["2025-11-03", "2025-11-10", "2025-11-17"])


class WeeklyPlotsSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.outdir = Path(self.tmpdir.name)
        self.goals = Goals(weekly_minutes=90.0, weekly_days=2)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_plot_weekly_minutes_creates_png(self) -> None:
        weekly_minutes = [
            (date(2025, 11, 3), 100.0),
            (date(2025, 11, 10), 80.0),
        ]
        path = plot_weekly_minutes(weekly_minutes, self.goals, self.outdir)
        self.assertTrue(path.is_file())

    def test_plot_weekly_days_creates_png(self) -> None:
        weekly_days = [
            (date(2025, 11, 3), 3),
            (date(2025, 11, 10), 1),
        ]
        path = plot_weekly_days(weekly_days, self.goals, self.outdir)
        self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()

