import sqlite3
import unittest

from workout_tracker import init_db
from fitbit_dedupe import build_plan, apply_plan


class FitbitDedupeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_db(self.conn)

        cur = self.conn.cursor()

        # Create three workouts; two of them are duplicates for the same Fitbit external_id
        cur.execute(
            "INSERT INTO workouts (date, primary_modality, duration_min) VALUES ('2025-11-29', 'Walk', 40.0)"
        )
        self.w1 = cur.lastrowid
        cur.execute(
            "INSERT INTO workouts (date, primary_modality, duration_min) VALUES ('2025-11-29', 'Walk', 40.0)"
        )
        self.w2 = cur.lastrowid
        cur.execute(
            "INSERT INTO workouts (date, primary_modality, duration_min) VALUES ('2025-11-30', 'Run', 30.0)"
        )
        self.w3 = cur.lastrowid

        # Observations: two Fitbit obs for same external_id -> duplicates, plus one manual obs
        cur.execute(
            "INSERT INTO workout_observations (workout_id, source, external_id, duration_min) "
            "VALUES (?, 'fitbit', 'ext-1', 40.0)",
            (self.w1,),
        )
        cur.execute(
            "INSERT INTO workout_observations (workout_id, source, external_id, duration_min) "
            "VALUES (?, 'fitbit', 'ext-1', 40.0)",
            (self.w2,),
        )
        cur.execute(
            "INSERT INTO workout_observations (workout_id, source, external_id, duration_min) "
            "VALUES (?, 'manual_text', NULL, 30.0)",
            (self.w3,),
        )

        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()

    def test_build_plan_identifies_duplicate_group(self) -> None:
        plan = build_plan(self.conn)
        self.assertEqual(len(plan.groups), 1)
        group = plan.groups[0]
        self.assertEqual(group.external_id, "ext-1")
        # One canonical + one duplicate
        self.assertEqual(len(group.duplicate_obs_ids), 1)
        # Exactly one workout should be eligible for deletion (the later one)
        self.assertEqual(len(group.workouts_to_delete), 1)

    def test_apply_plan_removes_duplicates_and_orphan_workouts(self) -> None:
        plan = build_plan(self.conn)
        deleted_obs, deleted_workouts = apply_plan(self.conn, plan)

        self.assertEqual(deleted_obs, plan.total_observations_to_delete)
        self.assertEqual(deleted_workouts, plan.total_workouts_to_delete)

        cur = self.conn.cursor()
        # Fitbit external_id should now have exactly one observation
        cur.execute(
            "SELECT COUNT(*) FROM workout_observations WHERE source='fitbit' AND external_id='ext-1'"
        )
        (count_fitbit,) = cur.fetchone()
        self.assertEqual(count_fitbit, 1)

        # Manual workout should still exist
        cur.execute(
            "SELECT COUNT(*) FROM workouts WHERE id=?",
            (self.w3,),
        )
        (count_manual_workout,) = cur.fetchone()
        self.assertEqual(count_manual_workout, 1)


if __name__ == "__main__":
    unittest.main()

