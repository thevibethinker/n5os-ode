import sqlite3
import unittest

from workout_tracker import init_db, log_manual_workout


class LogManualWorkoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_db(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_fitbit_import_is_idempotent_for_same_external_id(self) -> None:
        payload = {
            "date": "2025-12-01",
            "modality": "Run",
            "duration_min": 30.0,
            "source": "fitbit",
            "external_id": "fitbit-log-123",
            "raw_payload": {"logId": 123},
        }

        first_id = log_manual_workout(self.conn, payload)
        second_id = log_manual_workout(self.conn, payload)

        # Both calls should return the same workout_id
        self.assertEqual(first_id, second_id)

        # Only a single workouts row should exist
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM workouts")
        (workout_count,) = cur.fetchone()
        self.assertEqual(workout_count, 1)

        # Only a single observation for this external_id should exist
        cur.execute(
            "SELECT COUNT(*) FROM workout_observations WHERE source='fitbit' AND external_id=?",
            ("fitbit-log-123",),
        )
        (obs_count,) = cur.fetchone()
        self.assertEqual(obs_count, 1)

    def test_manual_source_still_creates_new_workout_when_no_fitbit_found(self) -> None:
        payload = {
            "date": "2025-12-02",
            "modality": "Walk",
            "duration_min": 20.0,
            "source": "manual_text",
            "notes": "Evening walk",
        }

        wid = log_manual_workout(self.conn, payload)
        self.assertIsInstance(wid, int)

        cur = self.conn.cursor()
        cur.execute("SELECT date, primary_modality, duration_min FROM workouts WHERE id=?", (wid,))
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["date"], "2025-12-02")
        self.assertEqual(row["primary_modality"], "Walk")
        self.assertAlmostEqual(row["duration_min"], 20.0)


if __name__ == "__main__":
    unittest.main()

