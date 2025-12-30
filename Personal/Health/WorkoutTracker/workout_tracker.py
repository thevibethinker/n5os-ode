import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("/home/workspace/Personal/Health/workouts.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # Canonical workouts table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            primary_modality TEXT,
            duration_min REAL,
            distance_km REAL,
            calories REAL,
            avg_hr REAL,
            notes TEXT
        )
        """
    )

    # Source observations (Fitbit, manual text, photo, etc.)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_observations (
            id INTEGER PRIMARY KEY,
            workout_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            external_id TEXT,
            start_time TEXT,
            end_time TEXT,
            modality TEXT,
            duration_min REAL,
            distance_km REAL,
            calories REAL,
            avg_hr REAL,
            raw_payload_json TEXT,
            FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE
        )
        """
    )

    # Daily qualitative check-ins (wanted to work out, worked out, regretted workout)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_checkins (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL UNIQUE,
            wanted_to_work_out INTEGER NOT NULL CHECK (wanted_to_work_out IN (0, 1)),
            worked_out INTEGER NOT NULL CHECK (worked_out IN (0, 1)),
            regretted_workout INTEGER NOT NULL CHECK (regretted_workout IN (0, 1)),
            notes TEXT
        )
        """
    )

    # Daily metrics: resting heart rate
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_resting_hr (
            date TEXT PRIMARY KEY,
            resting_hr REAL,
            hrv REAL,
            spo2 REAL,
            skin_temp_delta REAL,
            source TEXT NOT NULL
        )
        """
    )

    # Daily metrics: weight (manually logged in Fitbit or scales)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_weight (
            date TEXT PRIMARY KEY,
            weight_kg REAL NOT NULL,
            bmi REAL,
            fat_pct REAL,
            source TEXT NOT NULL
        )
        """
    )

    # Daily metrics: sleep summary
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_sleep (
            date TEXT PRIMARY KEY,
            sleep_score REAL,
            minutes_asleep REAL,
            minutes_in_bed REAL,
            source TEXT NOT NULL,
            raw_payload_json TEXT
        )
        """
    )

    # Daily metrics: aggregate activity summary from Fitbit
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_activity_summary (
            date TEXT PRIMARY KEY,
            steps INTEGER,
            distance_km REAL,
            floors INTEGER,
            elevation_m REAL,
            calories_out REAL,
            activity_calories REAL,
            minutes_sedentary INTEGER,
            minutes_lightly_active INTEGER,
            minutes_fairly_active INTEGER,
            minutes_very_active INTEGER,
            active_zone_minutes_total INTEGER,
            active_zone_minutes_fat_burn INTEGER,
            active_zone_minutes_cardio INTEGER,
            active_zone_minutes_peak INTEGER,
            source TEXT NOT NULL,
            raw_summary_json TEXT
        )
        """
    )

    # Intraday activity samples (1 row per timestamp per metric)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS intraday_activity_samples (
            id INTEGER PRIMARY KEY,
            datetime_local TEXT NOT NULL,
            local_date TEXT NOT NULL,
            metric TEXT NOT NULL,
            value REAL,
            source TEXT NOT NULL,
            raw_payload_json TEXT
        )
        """
    )

    # Intraday heart rate (1 row per timestamp)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS intraday_heart_rate (
            id INTEGER PRIMARY KEY,
            datetime_local TEXT NOT NULL,
            local_date TEXT NOT NULL,
            bpm INTEGER,
            zone TEXT,
            source TEXT NOT NULL,
            raw_payload_json TEXT
        )
        """
    )

    # Normalized sleep sessions (per Fitbit sleep log)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sleep_sessions (
            log_id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            start_time_local TEXT,
            end_time_local TEXT,
            is_main_sleep INTEGER NOT NULL CHECK (is_main_sleep IN (0, 1)),
            duration_min REAL,
            efficiency REAL,
            source TEXT NOT NULL,
            raw_payload_json TEXT
        )
        """
    )

    # Normalized sleep stages/segments per sleep session
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sleep_stages (
            id INTEGER PRIMARY KEY,
            sleep_log_id INTEGER NOT NULL,
            stage TEXT NOT NULL,
            start_time_local TEXT NOT NULL,
            duration_sec INTEGER,
            source TEXT NOT NULL,
            FOREIGN KEY (sleep_log_id) REFERENCES sleep_sessions(log_id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()


def _find_fitbit_workout_for_date(conn: sqlite3.Connection, date: str) -> Optional[int]:
    """Return a candidate Fitbit workout_id for a given date, if any.

    Heuristic for v1:
      - Look for workouts on the given date that have at least one observation with
        source='fitbit'.
      - Prefer the most recently inserted workout on that date.
    """

    cur = conn.cursor()
    cur.execute(
        """
        SELECT w.id
        FROM workouts w
        JOIN workout_observations o ON o.workout_id = w.id
        WHERE w.date = ? AND o.source = 'fitbit'
        ORDER BY w.id DESC
        LIMIT 1
        """,
        (date,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return int(row["id"])


def log_manual_workout(conn: sqlite3.Connection, payload: Dict[str, Any]) -> int:
    """Insert a workout + observation.

    Expected payload keys (all optional except date):
      - date (YYYY-MM-DD)
      - start_time, end_time (ISO or HH:MM, we store as-is for now)
      - modality
      - duration_min, distance_km, calories, avg_hr
      - notes
      - source (defaults to 'manual_text')
      - external_id (optional)
      - raw_payload (dict, optional)

    Behaviour:
      - If source == 'fitbit' and an observation already exists for the same
        external_id, this is treated as an idempotent re-import and we simply
        return the existing workout_id without inserting anything.
      - If source == 'fitbit' and no such observation exists, create a new
        workouts row and a corresponding observation.
      - If source != 'fitbit': attempt to link this observation to an existing
        Fitbit-based workout on the same date. If found, attach as another
        observation and update canonical metrics where appropriate. If not found,
        create a new workouts row.
    """

    init_db(conn)

    date = payload.get("date")
    if not date:
        raise ValueError("'date' is required in payload (YYYY-MM-DD)")

    start_time = payload.get("start_time")
    end_time = payload.get("end_time")
    modality = payload.get("modality")
    duration_min = payload.get("duration_min")
    distance_km = payload.get("distance_km")
    calories = payload.get("calories")
    avg_hr = payload.get("avg_hr")
    notes = payload.get("notes")

    source = payload.get("source") or "manual_text"
    external_id = payload.get("external_id")
    raw_payload = payload.get("raw_payload")
    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    cur = conn.cursor()

    # Decide which workouts row to use (existing Fitbit-based vs new row)
    workout_id: Optional[int] = None

    if source == "fitbit":
        # Idempotency: if we've already imported this Fitbit log_id for this
        # database (identified by source + external_id), return the existing
        # workout_id without inserting duplicates.
        if external_id is not None:
            cur.execute(
                """
                SELECT workout_id
                FROM workout_observations
                WHERE source = 'fitbit' AND external_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (str(external_id),),
            )
            row = cur.fetchone()
            if row is not None:
                return int(row["workout_id"])

        # No existing observation for this Fitbit external_id: create a new
        # canonical workout and observation.
        cur.execute(
            """
            INSERT INTO workouts (
                date, start_time, end_time, primary_modality,
                duration_min, distance_km, calories, avg_hr, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date,
                start_time,
                end_time,
                modality,
                duration_min,
                distance_km,
                calories,
                avg_hr,
                notes,
            ),
        )
        workout_id = cur.lastrowid
    else:
        # Try to link to an existing Fitbit workout for this date.
        candidate_id = _find_fitbit_workout_for_date(conn, date)
        if candidate_id is not None:
            workout_id = candidate_id
            # Optionally update canonical metrics with manual/treadmill overrides
            # where provided.
            update_fields = []
            params = []
            if duration_min is not None:
                update_fields.append("duration_min = ?")
                params.append(duration_min)
            if distance_km is not None:
                update_fields.append("distance_km = ?")
                params.append(distance_km)
            if calories is not None:
                update_fields.append("calories = ?")
                params.append(calories)
            if avg_hr is not None:
                update_fields.append("avg_hr = ?")
                params.append(avg_hr)
            if modality is not None:
                update_fields.append("primary_modality = ?")
                params.append(modality)
            if notes:
                # Append notes to any existing notes for that workout.
                update_fields.append("notes = COALESCE(notes, '') || CASE WHEN notes IS NULL OR notes = '' THEN ? ELSE ' ' || ? END")
                params.extend([notes, notes])

            if update_fields:
                params.append(workout_id)
                cur.execute(
                    f"UPDATE workouts SET {', '.join(update_fields)} WHERE id = ?",
                    params,
                )
        else:
            # No Fitbit workout found; create a new canonical workout.
            cur.execute(
                """
                INSERT INTO workouts (
                    date, start_time, end_time, primary_modality,
                    duration_min, distance_km, calories, avg_hr, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    date,
                    start_time,
                    end_time,
                    modality,
                    duration_min,
                    distance_km,
                    calories,
                    avg_hr,
                    notes,
                ),
            )
            workout_id = cur.lastrowid

    # Insert observation row pointing at the selected workout_id
    cur.execute(
        """
        INSERT INTO workout_observations (
            workout_id, source, external_id,
            start_time, end_time, modality,
            duration_min, distance_km, calories, avg_hr,
            raw_payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workout_id,
            source,
            external_id,
            start_time,
            end_time,
            modality,
            duration_min,
            distance_km,
            calories,
            avg_hr,
            raw_payload_json,
        ),
    )

    conn.commit()
    return int(workout_id)


def upsert_daily_checkin(
    conn: sqlite3.Connection,
    *,
    date: str,
    wanted_to_work_out: int,
    worked_out: int,
    regretted_workout: int,
    notes: Optional[str] = None,
) -> None:
    init_db(conn)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO daily_checkins (
            date, wanted_to_work_out, worked_out, regretted_workout, notes
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            wanted_to_work_out=excluded.wanted_to_work_out,
            worked_out=excluded.worked_out,
            regretted_workout=excluded.regretted_workout,
            notes=excluded.notes
        """,
        (date, wanted_to_work_out, worked_out, regretted_workout, notes),
    )
    conn.commit()


def upsert_daily_resting_hr(
    conn: sqlite3.Connection,
    *,
    date: str,
    resting_hr: Optional[float],
    hrv: Optional[float] = None,
    spo2: Optional[float] = None,
    skin_temp_delta: Optional[float] = None,
    stress_score: Optional[float] = None,
    source: str = "fitbit",
) -> None:
    """Upsert a single day's resting heart rate and HRV value."""

    init_db(conn)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO daily_resting_hr (date, resting_hr, hrv, spo2, skin_temp_delta, stress_score, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            resting_hr = excluded.resting_hr,
            hrv = excluded.hrv,
            spo2 = excluded.spo2,
            skin_temp_delta = excluded.skin_temp_delta,
            stress_score = excluded.stress_score,
            source = excluded.source
        """,
        (date, resting_hr, hrv, spo2, skin_temp_delta, stress_score, source),
    )
    conn.commit()


def upsert_daily_weight(
    conn: sqlite3.Connection,
    *,
    date: str,
    weight_kg: float,
    bmi: Optional[float] = None,
    fat_pct: Optional[float] = None,
    source: str = "fitbit",
) -> None:
    """Upsert a single day's weight entry."""

    init_db(conn)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO daily_weight (date, weight_kg, bmi, fat_pct, source)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            weight_kg = excluded.weight_kg,
            bmi = excluded.bmi,
            fat_pct = excluded.fat_pct,
            source = excluded.source
        """,
        (date, weight_kg, bmi, fat_pct, source),
    )
    conn.commit()


def upsert_daily_activity_summary(
    conn: sqlite3.Connection,
    *,
    date: str,
    steps: Optional[int] = None,
    distance_km: Optional[float] = None,
    floors: Optional[int] = None,
    elevation_m: Optional[float] = None,
    calories_out: Optional[float] = None,
    activity_calories: Optional[float] = None,
    minutes_sedentary: Optional[int] = None,
    minutes_lightly_active: Optional[int] = None,
    minutes_fairly_active: Optional[int] = None,
    minutes_very_active: Optional[int] = None,
    active_zone_minutes_total: Optional[int] = None,
    active_zone_minutes_fat_burn: Optional[int] = None,
    active_zone_minutes_cardio: Optional[int] = None,
    active_zone_minutes_peak: Optional[int] = None,
    source: str = "fitbit",
    raw_summary: Optional[Dict[str, Any]] = None,
) -> None:
    """Upsert a single day's aggregate activity summary from Fitbit.

    All numerical fields are optional; we upsert whatever Fitbit provides and
    preserve a copy of the raw `summary` blob for future use.
    """

    init_db(conn)
    cur = conn.cursor()
    raw_summary_json = json.dumps(raw_summary) if raw_summary is not None else None

    cur.execute(
        """
        INSERT INTO daily_activity_summary (
            date,
            steps,
            distance_km,
            floors,
            elevation_m,
            calories_out,
            activity_calories,
            minutes_sedentary,
            minutes_lightly_active,
            minutes_fairly_active,
            minutes_very_active,
            active_zone_minutes_total,
            active_zone_minutes_fat_burn,
            active_zone_minutes_cardio,
            active_zone_minutes_peak,
            source,
            raw_summary_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            steps = excluded.steps,
            distance_km = excluded.distance_km,
            floors = excluded.floors,
            elevation_m = excluded.elevation_m,
            calories_out = excluded.calories_out,
            activity_calories = excluded.activity_calories,
            minutes_sedentary = excluded.minutes_sedentary,
            minutes_lightly_active = excluded.minutes_lightly_active,
            minutes_fairly_active = excluded.minutes_fairly_active,
            minutes_very_active = excluded.minutes_very_active,
            active_zone_minutes_total = excluded.active_zone_minutes_total,
            active_zone_minutes_fat_burn = excluded.active_zone_minutes_fat_burn,
            active_zone_minutes_cardio = excluded.active_zone_minutes_cardio,
            active_zone_minutes_peak = excluded.active_zone_minutes_peak,
            source = excluded.source,
            raw_summary_json = excluded.raw_summary_json
        """,
        (
            date,
            steps,
            distance_km,
            floors,
            elevation_m,
            calories_out,
            activity_calories,
            minutes_sedentary,
            minutes_lightly_active,
            minutes_fairly_active,
            minutes_very_active,
            active_zone_minutes_total,
            active_zone_minutes_fat_burn,
            active_zone_minutes_cardio,
            active_zone_minutes_peak,
            source,
            raw_summary_json,
        ),
    )
    conn.commit()


def upsert_daily_sleep(
    conn: sqlite3.Connection,
    *,
    date: str,
    sleep_score: Optional[float],
    minutes_asleep: Optional[float],
    minutes_in_bed: Optional[float],
    source: str = "fitbit",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Upsert a single day's sleep summary (score + duration)."""

    init_db(conn)
    cur = conn.cursor()
    raw_payload_json = json.dumps(raw_payload) if raw_payload is not None else None

    cur.execute(
        """
        INSERT INTO daily_sleep (date, sleep_score, minutes_asleep, minutes_in_bed, source, raw_payload_json)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            sleep_score = excluded.sleep_score,
            minutes_asleep = excluded.minutes_asleep,
            minutes_in_bed = excluded.minutes_in_bed,
            source = excluded.source,
            raw_payload_json = excluded.raw_payload_json
        """,
        (date, sleep_score, minutes_asleep, minutes_in_bed, source, raw_payload_json),
    )
    conn.commit()


def replace_intraday_activity_for_date(
    conn: sqlite3.Connection,
    *,
    date: str,
    metric: str,
    samples: List[Dict[str, Any]],
    source: str = "fitbit",
) -> None:
    """Replace intraday activity samples for a given date/metric with new data.

    `samples` should be a list of dicts with at least:
      - datetime_local: ISO-like local timestamp string (YYYY-MM-DDTHH:MM or HH:MM:SS)
      - value: numeric value
      - raw_payload: original Fitbit point (optional)
    """

    init_db(conn)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM intraday_activity_samples WHERE local_date = ? AND metric = ?",
        (date, metric),
    )

    if not samples:
        conn.commit()
        return

    rows = []
    for s in samples:
        dt = s.get("datetime_local")
        if not dt:
            continue
        value = s.get("value")
        raw_payload = s.get("raw_payload")
        raw_json = json.dumps(raw_payload) if raw_payload is not None else None
        rows.append((dt, date, metric, value, source, raw_json))

    if rows:
        cur.executemany(
            """
            INSERT INTO intraday_activity_samples (
                datetime_local, local_date, metric, value, source, raw_payload_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    conn.commit()


def replace_intraday_hr_for_date(
    conn: sqlite3.Connection,
    *,
    date: str,
    samples: List[Dict[str, Any]],
    source: str = "fitbit",
) -> None:
    """Replace intraday heart-rate samples for a given date with new data.

    `samples` should be a list of dicts with at least:
      - datetime_local: ISO-like local timestamp string
      - bpm: integer heart rate
      - zone: optional zone label
      - raw_payload: original Fitbit point (optional)
    """

    init_db(conn)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM intraday_heart_rate WHERE local_date = ?",
        (date,),
    )

    if not samples:
        conn.commit()
        return

    rows = []
    for s in samples:
        dt = s.get("datetime_local")
        if not dt:
            continue
        bpm = s.get("bpm")
        zone = s.get("zone")
        raw_payload = s.get("raw_payload")
        raw_json = json.dumps(raw_payload) if raw_payload is not None else None
        rows.append((dt, date, bpm, zone, source, raw_json))

    if rows:
        cur.executemany(
            """
            INSERT INTO intraday_heart_rate (
                datetime_local, local_date, bpm, zone, source, raw_payload_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    conn.commit()


def upsert_sleep_session_with_stages(
    conn: sqlite3.Connection,
    *,
    log_id: int,
    date: str,
    start_time_local: Optional[str],
    end_time_local: Optional[str],
    is_main_sleep: bool,
    duration_min: Optional[float],
    efficiency: Optional[float],
    stages: Optional[List[Dict[str, Any]]] = None,
    source: str = "fitbit",
    raw_payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Upsert a sleep session (one Fitbit sleep log) and replace its stages.

    `stages` items should have:
      - stage: string label (wake/light/deep/rem/etc.)
      - start_time_local: ISO-like timestamp string
      - duration_sec: integer seconds duration
    """

    init_db(conn)
    cur = conn.cursor()

    raw_json = json.dumps(raw_payload) if raw_payload is not None else None

    cur.execute(
        """
        INSERT INTO sleep_sessions (
            log_id, date, start_time_local, end_time_local,
            is_main_sleep, duration_min, efficiency, source, raw_payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(log_id) DO UPDATE SET
            date = excluded.date,
            start_time_local = excluded.start_time_local,
            end_time_local = excluded.end_time_local,
            is_main_sleep = excluded.is_main_sleep,
            duration_min = excluded.duration_min,
            efficiency = excluded.efficiency,
            source = excluded.source,
            raw_payload_json = excluded.raw_payload_json
        """,
        (
            log_id,
            date,
            start_time_local,
            end_time_local,
            1 if is_main_sleep else 0,
            duration_min,
            efficiency,
            source,
            raw_json,
        ),
    )

    # Replace stages for this session
    cur.execute("DELETE FROM sleep_stages WHERE sleep_log_id = ?", (log_id,))

    if stages:
        rows = []
        for s in stages:
            stage = s.get("stage")
            start_ts = s.get("start_time_local")
            if not stage or not start_ts:
                continue
            duration_sec = s.get("duration_sec")
            rows.append((log_id, stage, start_ts, duration_sec, source))

        if rows:
            cur.executemany(
                """
                INSERT INTO sleep_stages (
                    sleep_log_id, stage, start_time_local, duration_sec, source
                ) VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )

    conn.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Workout tracker helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # log-manual-workout from JSON
    p_log = subparsers.add_parser("log-manual-workout", help="Log a manual workout from JSON payload")
    p_log.add_argument("--json", required=True, help="JSON string with workout fields")

    # upsert daily checkin
    p_checkin = subparsers.add_parser("upsert-daily-checkin", help="Upsert daily qualitative check-in")
    p_checkin.add_argument("--date", required=True, help="Date YYYY-MM-DD")
    p_checkin.add_argument("--wanted", type=int, choices=[0, 1], required=True)
    p_checkin.add_argument("--worked", type=int, choices=[0, 1], required=True)
    p_checkin.add_argument("--regretted", type=int, choices=[0, 1], required=True)
    p_checkin.add_argument("--notes", required=False)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    conn = get_connection()

    if args.command == "log-manual-workout":
        try:
            payload = json.loads(args.json)
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON for --json: {e}")

        workout_id = log_manual_workout(conn, payload)
        print(f"Logged workout with id={workout_id} to {DB_PATH}")

    elif args.command == "upsert-daily-checkin":
        upsert_daily_checkin(
            conn,
            date=args.date,
            wanted_to_work_out=args.wanted,
            worked_out=args.worked,
            regretted_workout=args.regretted,
            notes=args.notes,
        )
        print(f"Upserted daily_checkin for {args.date} in {DB_PATH}")


if __name__ == "__main__":
    main()









