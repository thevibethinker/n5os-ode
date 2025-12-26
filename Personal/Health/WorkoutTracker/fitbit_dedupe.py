import argparse
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Tuple

from workout_tracker import get_connection, init_db


@dataclass
class DuplicateGroup:
    external_id: str
    canonical_obs_id: int
    canonical_workout_id: int
    duplicate_obs_ids: List[int]
    workouts_to_delete: List[int]


@dataclass
class DedupePlan:
    groups: List[DuplicateGroup]

    @property
    def total_observations_to_delete(self) -> int:
        return sum(len(g.duplicate_obs_ids) for g in self.groups)

    @property
    def total_workouts_to_delete(self) -> int:
        return len({wid for g in self.groups for wid in g.workouts_to_delete})


def build_plan(conn: sqlite3.Connection) -> DedupePlan:
    """Scan for duplicate Fitbit observations and produce a dedupe plan.

    A duplicate is defined as multiple workout_observations rows with
    source='fitbit' and the same non-null external_id. We keep the earliest
    observation (smallest id) as canonical and treat the rest as duplicates.

    Any workouts that are referenced *only* by duplicate observations are marked
    for deletion as well.
    """

    init_db(conn)
    cur = conn.cursor()

    # Load all Fitbit observations with an external_id so we can group in Python.
    cur.execute(
        """
        SELECT o.id AS obs_id,
               o.external_id,
               o.workout_id
        FROM workout_observations o
        WHERE o.source = 'fitbit' AND o.external_id IS NOT NULL
        ORDER BY o.external_id, o.id
        """
    )
    rows = cur.fetchall()

    # Group by external_id
    by_external: Dict[str, List[sqlite3.Row]] = {}
    for r in rows:
        ext = str(r["external_id"])
        by_external.setdefault(ext, []).append(r)

    groups: List[DuplicateGroup] = []

    # Precompute mapping from workout_id -> all observation ids that reference it
    cur.execute(
        "SELECT workout_id, id AS obs_id FROM workout_observations"
    )
    all_obs = cur.fetchall()
    obs_by_workout: Dict[int, List[int]] = {}
    for r in all_obs:
        wid = int(r["workout_id"])
        obs_by_workout.setdefault(wid, []).append(int(r["obs_id"]))

    for external_id, obs_rows in by_external.items():
        if len(obs_rows) <= 1:
            continue  # nothing to dedupe

        # Keep the earliest observation as canonical
        canonical = obs_rows[0]
        canonical_obs_id = int(canonical["obs_id"])
        canonical_workout_id = int(canonical["workout_id"])

        duplicate_obs_ids = [int(r["obs_id"]) for r in obs_rows[1:]]

        # Determine which workouts can be safely deleted: those for which *all*
        # observations are in duplicate_obs_ids.
        workouts_to_delete: List[int] = []
        for r in obs_rows[1:]:
            wid = int(r["workout_id"])
            all_obs_ids_for_workout = obs_by_workout.get(wid, [])
            if all(oid in duplicate_obs_ids for oid in all_obs_ids_for_workout):
                workouts_to_delete.append(wid)

        groups.append(
            DuplicateGroup(
                external_id=external_id,
                canonical_obs_id=canonical_obs_id,
                canonical_workout_id=canonical_workout_id,
                duplicate_obs_ids=duplicate_obs_ids,
                workouts_to_delete=sorted(set(workouts_to_delete)),
            )
        )

    return DedupePlan(groups=groups)


def apply_plan(conn: sqlite3.Connection, plan: DedupePlan) -> Tuple[int, int]:
    """Apply a dedupe plan, returning (deleted_observations, deleted_workouts)."""

    if not plan.groups:
        return 0, 0

    cur = conn.cursor()

    # Delete duplicate observations
    dup_obs_ids = [oid for g in plan.groups for oid in g.duplicate_obs_ids]
    if dup_obs_ids:
        cur.execute(
            f"DELETE FROM workout_observations WHERE id IN ({','.join('?' for _ in dup_obs_ids)})",
            dup_obs_ids,
        )

    # Delete workouts that are now orphaned (only referenced by deleted observations)
    workout_ids = sorted({wid for g in plan.groups for wid in g.workouts_to_delete})
    if workout_ids:
        cur.execute(
            f"DELETE FROM workouts WHERE id IN ({','.join('?' for _ in workout_ids)})",
            workout_ids,
        )

    conn.commit()
    return len(dup_obs_ids), len(workout_ids)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deduplicate Fitbit workouts in workouts.db")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply the dedupe instead of just printing a dry-run summary",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    conn = get_connection()

    plan = build_plan(conn)

    print(f"Found {len(plan.groups)} Fitbit external_id groups with duplicates.")
    print(f"Would delete {plan.total_observations_to_delete} duplicate observations "
          f"and {plan.total_workouts_to_delete} workouts.")

    for g in plan.groups:
        print(
            f"external_id={g.external_id}: keep obs {g.canonical_obs_id} / workout {g.canonical_workout_id}, "
            f"delete obs {g.duplicate_obs_ids} and workouts {g.workouts_to_delete}"
        )

    if not args.execute:
        print("Dry run only. Re-run with --execute to apply these deletions.")
        return

    deleted_obs, deleted_workouts = apply_plan(conn, plan)
    print(f"Deleted {deleted_obs} observations and {deleted_workouts} workouts.")


if __name__ == "__main__":
    main()

