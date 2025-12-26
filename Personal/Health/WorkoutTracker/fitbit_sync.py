import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, urlopen
import sqlite3
import fitbit

# Paths
BASE_DIR = Path("/home/workspace/Personal/Health/WorkoutTracker")
CONFIG_PATH = BASE_DIR / "fitbit_config.json"

AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
ACTIVITIES_DATE_URL = "https://api.fitbit.com/1/user/-/activities/date/{date}.json"
HEART_TIME_SERIES_URL = "https://api.fitbit.com/1/user/-/activities/heart/date/{start}/{end}.json"
SLEEP_DATE_RANGE_URL = "https://api.fitbit.com/1.2/user/-/sleep/date/{start}/{end}.json"
INTRADAY_ACTIVITY_URL = "https://api.fitbit.com/1/user/-/activities/{resource}/date/{date}/1d/1min.json"
HEART_INTRADAY_URL = "https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"
HRV_DATE_URL = "https://api.fitbit.com/1/user/-/hrv/date/{date}.json"
SPO2_DATE_URL = "https://api.fitbit.com/1/user/-/spo2/date/{date}.json"
SKIN_TEMP_DATE_URL = "https://api.fitbit.com/1/user/-/temp/skin/date/{date}.json"
WEIGHT_DATE_RANGE_URL = "https://api.fitbit.com/1/user/-/body/log/weight/date/{start}/{end}.json"
VO2_MAX_DATE_URL = "https://api.fitbit.com/1/user/-/cardioscore/date/{date}.json"
STRESS_SCORE_DATE_URL = "https://api.fitbit.com/1/user/-/stress/stress-score/date/{date}.json"


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Config file not found: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: Dict[str, Any]) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, sort_keys=True)


def get_client_secret(cfg: Dict[str, Any]) -> str:
    env_name = cfg.get("client_secret_env") or "FITBIT_APP_CLIENTSECRET"
    value = os.environ.get(env_name)
    if not value:
        raise SystemExit(
            f"Environment variable '{env_name}' is not set. Configure it in Zo Settings → Developers → Secrets."
        )
    return value


def ensure_client_id(cfg: Dict[str, Any]) -> str:
    client_id = cfg.get("client_id")
    if not client_id or client_id == "PASTE_CLIENT_ID_HERE":
        raise SystemExit(
            "fitbit_config.json is missing a valid client_id. "
            "Edit the file at Personal/Health/WorkoutTracker/fitbit_config.json and set 'client_id' "
            "to the OAuth 2.0 Client ID shown in the Fitbit developer portal."
        )
    return client_id


def build_auth_url(cfg: Dict[str, Any]) -> str:
    client_id = ensure_client_id(cfg)
    redirect_uri = cfg["redirect_uri"]
    scopes: List[str] = cfg.get("scopes") or []
    scope_str = " ".join(scopes)

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope_str,
        "prompt": "consent",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def http_post(url: str, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    body = urlencode(data).encode("utf-8")
    req = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=20) as resp:
            raw = resp.read()
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} error from {url}: {err_body}") from e

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse JSON response from {url}: {e}\nRaw: {raw!r}") from e


def exchange_code_for_tokens(cfg: Dict[str, Any], code: str) -> Dict[str, Any]:
    client_id = ensure_client_id(cfg)
    client_secret = get_client_secret(cfg)

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")

    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": cfg["redirect_uri"],
    }
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    token_data = http_post(TOKEN_URL, data, headers)

    now = int(time.time())
    expires_in = int(token_data.get("expires_in", 0))

    cfg["access_token"] = token_data.get("access_token")
    cfg["refresh_token"] = token_data.get("refresh_token")
    cfg["token_expires_at"] = now + expires_in - 60 if expires_in else None

    save_config(cfg)
    return cfg


def refresh_tokens(cfg: Dict[str, Any]) -> Dict[str, Any]:
    client_id = ensure_client_id(cfg)
    client_secret = get_client_secret(cfg)

    refresh_token = cfg.get("refresh_token")
    if not refresh_token:
        raise SystemExit("No refresh_token present in config; run start-auth / finish-auth first.")

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    token_data = http_post(TOKEN_URL, data, headers)

    now = int(time.time())
    expires_in = int(token_data.get("expires_in", 0))

    cfg["access_token"] = token_data.get("access_token")
    cfg["refresh_token"] = token_data.get("refresh_token", refresh_token)
    cfg["token_expires_at"] = now + expires_in - 60 if expires_in else None

    save_config(cfg)
    return cfg


def ensure_access_token(cfg: Dict[str, Any]) -> str:
    access_token = cfg.get("access_token")
    expires_at = cfg.get("token_expires_at")
    now = int(time.time())

    if access_token and expires_at and now < int(expires_at):
        return access_token

    # Try refresh
    cfg = refresh_tokens(cfg)
    token = cfg.get("access_token")
    if not token:
        raise SystemExit("Failed to obtain access token from Fitbit.")
    return token


def parse_auth_code_from_redirect(url: str) -> str:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    codes = qs.get("code")
    if not codes:
        raise SystemExit("No 'code' query parameter found in provided redirect URL.")
    return codes[0]


def api_get_json(url: str, access_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=20) as resp:
            raw = resp.read()
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} error from {url}: {err_body}") from e

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse JSON from {url}: {e}\nRaw: {raw!r}") from e


def sync_daily_metrics(conn, token: str, start_date, end_date, workout_tracker) -> None:
    """Sync daily resting HR, HRV, weight, and sleep summary for the given date range.

    This is best-effort: errors should not prevent activity sync from running.
    """

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # 1. Resting heart rate via activities-heart time series
    hr_url = HEART_TIME_SERIES_URL.format(start=start_str, end=end_str)
    hr_data = api_get_json(hr_url, token)
    series = hr_data.get("activities-heart", [])
    for item in series:
        day = item.get("dateTime")
        if not day:
            continue
        
        # Fetch HRV for this specific day
        hrv_value = None
        try:
            hrv_data = api_get_json(HRV_DATE_URL.format(date=day), token)
            hrv_entries = hrv_data.get("hrv", [])
            if hrv_entries:
                # Fitbit usually provides one deep-sleep HRV value per day
                hrv_value = hrv_entries[0].get("value", {}).get("dailyRmssd")
        except Exception as e:
            print(f"Warning: failed to fetch HRV for {day}: {e}", file=sys.stderr)

        value = item.get("value")
        resting_hr = None
        if isinstance(value, dict):
            resting_hr = value.get("restingHeartRate") or value.get("resting_heart_rate")
        elif isinstance(value, (int, float)):
            resting_hr = float(value)
            
        if resting_hr is not None or hrv_value is not None:
            # Fetch SpO2 and Skin Temp (best-effort)
            spo2 = None
            try:
                spo2_data = api_get_json(SPO2_DATE_URL.format(date=day), token)
                # SpO2 summary returns an object with 'value' which is avg
                spo2 = spo2_data.get("value")
            except Exception: pass

            skin_temp = None
            try:
                st_data = api_get_json(SKIN_TEMP_DATE_URL.format(date=day), token)
                # Skin temp returns a list of logs, we want the first entry's relative value
                st_logs = st_data.get("tempSkin", [])
                if st_logs:
                    skin_temp = st_logs[0].get("value")
            except Exception: pass

            # Fetch Stress Score (best-effort)
            stress_score = None
            try:
                stress_data = api_get_json(STRESS_SCORE_DATE_URL.format(date=day), token)
                # Returns a list of daily stress scores
                stress_logs = stress_data.get("stressScore", [])
                if stress_logs:
                    stress_score = stress_logs[0].get("value")
            except Exception: pass

            workout_tracker.upsert_daily_resting_hr(
                conn,
                date=day,
                resting_hr=float(resting_hr) if resting_hr else None,
                hrv=float(hrv_value) if hrv_value else None,
                spo2=float(spo2) if spo2 else None,
                skin_temp_delta=float(skin_temp) if skin_temp else None,
                stress_score=float(stress_score) if stress_score else None,
                source="fitbit",
            )

    # 2. Weight logs via body/log/weight endpoint
    try:
        weight_url = WEIGHT_DATE_RANGE_URL.format(start=start_str, end=end_str)
        weight_data = api_get_json(weight_url, token)
        weights = weight_data.get("weight", [])
        for w in weights:
            workout_tracker.upsert_daily_weight(
                conn,
                date=w.get("date"),
                weight_kg=w.get("weight"),
                bmi=w.get("bmi"),
                fat_pct=w.get("fat"),
                source="fitbit"
            )
    except Exception as e:
        print(f"Warning: failed to fetch weight data: {e}", file=sys.stderr)

    # 3. Sleep summary (score + minutes asleep/in bed) via sleep date range endpoint
    sleep_url = SLEEP_DATE_RANGE_URL.format(start=start_str, end=end_str)
    sleep_data = api_get_json(sleep_url, token)
    logs = sleep_data.get("sleep", [])

    # Aggregate to one record per date (prefer main sleep, otherwise longest minutesAsleep)
    by_date: Dict[str, Dict[str, Any]] = {}
    for log in logs:
        date_of_sleep = log.get("dateOfSleep")
        if not date_of_sleep:
            continue

        minutes_asleep = log.get("minutesAsleep")
        minutes_in_bed = log.get("timeInBed") or log.get("minutesInBed")

        score = log.get("score")
        if score is None:
            levels = log.get("levels") or {}
            summary = levels.get("summary") or {}
            if isinstance(summary, dict):
                score = summary.get("score")

        is_main = bool(log.get("isMainSleep"))

        # --- New: normalize each sleep log into sessions + stages ---
        log_id = log.get("logId")
        if log_id is not None:
            start_time_local = log.get("startTime")
            end_time_local = log.get("endTime")
            duration_min_log = None
            duration_ms = log.get("duration")
            if isinstance(duration_ms, (int, float)):
                # Fitbit duration is usually ms
                duration_min_log = float(duration_ms) / 60000.0

            efficiency = log.get("efficiency")

            levels = log.get("levels") or {}
            stages: List[Dict[str, Any]] = []
            for key in ("data", "shortData"):
                for seg in levels.get(key, []) or []:
                    stage_label = seg.get("level")
                    start_ts = seg.get("dateTime")
                    if not stage_label or not start_ts:
                        continue
                    duration_sec = seg.get("seconds")
                    stages.append(
                        {
                            "stage": stage_label,
                            "start_time_local": start_ts,
                            "duration_sec": duration_sec,
                        }
                    )

            try:
                workout_tracker.upsert_sleep_session_with_stages(
                    conn,
                    log_id=int(log_id),
                    date=date_of_sleep,
                    start_time_local=start_time_local,
                    end_time_local=end_time_local,
                    is_main_sleep=is_main,
                    duration_min=duration_min_log,
                    efficiency=efficiency,
                    stages=stages,
                    source="fitbit",
                    raw_payload=log,
                )
            except Exception as e:  # noqa: BLE001
                print(
                    f"Warning: failed to upsert sleep session/stages for log_id={log_id} on {date_of_sleep}: {e}",
                    file=sys.stderr,
                )

        existing = by_date.get(date_of_sleep)
        if existing is None:
            by_date[date_of_sleep] = {
                "score": score,
                "minutes_asleep": minutes_asleep,
                "minutes_in_bed": minutes_in_bed,
                "is_main": is_main,
                "raw": log,
            }
        else:
            # Prefer main sleep; otherwise, keep the entry with greater minutesAsleep.
            existing_main = existing.get("is_main", False)
            existing_minutes = existing.get("minutes_asleep") or 0
            candidate_minutes = minutes_asleep or 0

            if (not existing_main and is_main) or (
                existing_main == is_main and candidate_minutes > existing_minutes
            ):
                by_date[date_of_sleep] = {
                    "score": score,
                    "minutes_asleep": minutes_asleep,
                    "minutes_in_bed": minutes_in_bed,
                    "is_main": is_main,
                    "raw": log,
                }

    for day, info in by_date.items():
        workout_tracker.upsert_daily_sleep(
            conn,
            date=day,
            sleep_score=info.get("score"),
            minutes_asleep=info.get("minutes_asleep"),
            minutes_in_bed=info.get("minutes_in_bed"),
            source="fitbit",
            raw_payload=info.get("raw"),
        )


def _fetch_intraday_activity_for_date(resource: str, date_str: str, token: str) -> List[Dict[str, Any]]:
    """Fetch intraday activity timeseries for a single resource and date.

    Returns a list of points with datetime_local, value, and raw_payload.
    """

    url = INTRADAY_ACTIVITY_URL.format(resource=resource, date=date_str)
    data = api_get_json(url, token)
    key = f"activities-{resource}-intraday"
    
    if key not in data:
        print(
            f"Warning: Intraday key '{key}' missing from response for {resource} on {date_str}. "
            "Ensure Fitbit App Type is 'Personal' to access intraday data.",
            file=sys.stderr,
        )
        return []

    intraday = data.get(key) or {}
    dataset = intraday.get("dataset") or []

    points: List[Dict[str, Any]] = []
    for p in dataset:
        time_str = p.get("time")
        if not time_str:
            continue
        dt_local = f"{date_str}T{time_str}"
        value = p.get("value")
        points.append({"datetime_local": dt_local, "value": value, "raw_payload": p})
    return points


def _fetch_intraday_heart_for_date(date_str: str, token: str) -> List[Dict[str, Any]]:
    """Fetch intraday heart rate timeseries for a single date.

    For now we store bpm and timestamp; zone can be derived later if needed.
    """

    url = HEART_INTRADAY_URL.format(date=date_str)
    data = api_get_json(url, token)
    
    if "activities-heart-intraday" not in data:
        print(
            f"Warning: Intraday key 'activities-heart-intraday' missing from response for {date_str}. "
            "Ensure Fitbit App Type is 'Personal' to access intraday data.",
            file=sys.stderr,
        )
        return []

    intraday = data.get("activities-heart-intraday") or {}
    dataset = intraday.get("dataset") or []

    points: List[Dict[str, Any]] = []
    for p in dataset:
        time_str = p.get("time")
        if not time_str:
            continue
        dt_local = f"{date_str}T{time_str}"
        bpm = p.get("value")
        points.append(
            {
                "datetime_local": dt_local,
                "bpm": bpm,
                "zone": None,
                "raw_payload": p,
            }
        )
    return points


def _sync_intraday_for_date(conn, workout_tracker, token: str, date_str: str) -> None:
    """Best-effort sync of intraday activity + heart rate for a single date."""

    # Activity metrics available via intraday endpoints for regular developers
    resources = ["steps", "distance", "calories", "floors", "elevation"]

    for resource in resources:
        try:
            samples = _fetch_intraday_activity_for_date(resource, date_str, token)
        except SystemExit as e:
            # Propagate auth/HTTP info but don't kill the overall sync
            print(
                f"Warning: failed to fetch intraday {resource} for {date_str}: {e}",
                file=sys.stderr,
            )
            continue

        try:
            workout_tracker.replace_intraday_activity_for_date(
                conn,
                date=date_str,
                metric=resource,
                samples=samples,
                source="fitbit",
            )
        except Exception as e:  # noqa: BLE001
            print(
                f"Warning: failed to store intraday {resource} for {date_str}: {e}",
                file=sys.stderr,
            )

    # Intraday heart rate
    try:
        hr_samples = _fetch_intraday_heart_for_date(date_str, token)
    except SystemExit as e:
        print(
            f"Warning: failed to fetch intraday heart rate for {date_str}: {e}",
            file=sys.stderr,
        )
        hr_samples = []

    if hr_samples:
        try:
            workout_tracker.replace_intraday_hr_for_date(
                conn,
                date=date_str,
                samples=hr_samples,
                source="fitbit",
            )
        except Exception as e:  # noqa: BLE001
            print(
                f"Warning: failed to store intraday heart rate for {date_str}: {e}",
                file=sys.stderr,
            )


def sync_recent_activities(days: int) -> None:
    # Import workout tracker helpers
    sys.path.append(str(BASE_DIR))
    try:
        import workout_tracker  # type: ignore
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"Failed to import workout_tracker module: {e}") from e

    conn = workout_tracker.get_connection()
    workout_tracker.init_db(conn)

    cfg = load_config()
    token = ensure_access_token(cfg)

    today = datetime.utcnow().date()
    if days < 1:
        days = 1
    start_date = today - timedelta(days=days - 1)

    # Best-effort sync of daily metrics; don't abort if this fails.
    try:
        sync_daily_metrics(conn, token, start_date, today, workout_tracker)
    except SystemExit as e:
        print(f"Warning: failed to sync daily metrics (resting HR / sleep): {e}", file=sys.stderr)

    # 3. Intraday metrics (limited to last 48 hours to save quota)
    intraday_start = today - timedelta(days=2)
    current_date = max(start_date, intraday_start)
    while current_date <= today:
        date_str = current_date.isoformat()
        print(f"Syncing intraday vitals for {date_str}...")
        _sync_intraday_for_date(conn, workout_tracker, token, date_str)
        current_date += timedelta(days=1)

    for offset in range(days):
        day = today - timedelta(days=offset)
        date_str = day.strftime("%Y-%m-%d")
        url = ACTIVITIES_DATE_URL.format(date=date_str)

        # Fetch daily activities for this date with error handling so a 429 or other
        # HTTP error doesn't abort the entire sync.
        try:
            data = api_get_json(url, token)
        except SystemExit as e:
            print(
                f"Warning: failed to fetch daily activities for {date_str}: {e}",
                file=sys.stderr,
            )
            continue

        # --- Daily activity summary for this date ---
        summary = data.get("summary") or {}
        try:
            steps = summary.get("steps")
            floors = summary.get("floors")
            elevation = summary.get("elevation")
            calories_out = summary.get("caloriesOut")
            activity_calories = summary.get("activityCalories")
            minutes_sedentary = summary.get("sedentaryMinutes")
            minutes_lightly_active = summary.get("lightlyActiveMinutes")
            minutes_fairly_active = summary.get("fairlyActiveMinutes")
            minutes_very_active = summary.get("veryActiveMinutes")

            # Distances are typically an array of {activity, distance}
            distances = summary.get("distances") or []
            distance_km = None
            for d in distances:
                if isinstance(d, dict) and d.get("activity") == "total":
                    distance_km = d.get("distance")
                    break
            if distance_km is None and distances:
                # Fallback: sum all distance entries
                try:
                    distance_km = sum(float(d.get("distance") or 0.0) for d in distances if isinstance(d, dict))
                except (TypeError, ValueError):
                    distance_km = None

            # Heart rate zones (for active zone minutes-style summaries)
            hr_zones = summary.get("heartRateZones") or []
            azm_fat_burn = None
            azm_cardio = None
            azm_peak = None
            for z in hr_zones:
                if not isinstance(z, dict):
                    continue
                name = (z.get("name") or "").lower()
                minutes = z.get("minutes")
                if name == "fat burn":
                    azm_fat_burn = minutes
                elif name == "cardio":
                    azm_cardio = minutes
                elif name == "peak":
                    azm_peak = minutes

            azm_total = None
            zone_minutes = [m for m in (azm_fat_burn, azm_cardio, azm_peak) if isinstance(m, (int, float))]
            if zone_minutes:
                azm_total = int(sum(zone_minutes))

            workout_tracker.upsert_daily_activity_summary(
                conn,
                date=date_str,
                steps=steps,
                distance_km=distance_km,
                floors=floors,
                elevation_m=elevation,
                calories_out=calories_out,
                activity_calories=activity_calories,
                minutes_sedentary=minutes_sedentary,
                minutes_lightly_active=minutes_lightly_active,
                minutes_fairly_active=minutes_fairly_active,
                minutes_very_active=minutes_very_active,
                active_zone_minutes_total=azm_total,
                active_zone_minutes_fat_burn=azm_fat_burn,
                active_zone_minutes_cardio=azm_cardio,
                active_zone_minutes_peak=azm_peak,
                source="fitbit",
                raw_summary=summary or None,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Warning: failed to upsert daily activity summary for {date_str}: {e}", file=sys.stderr)

        # --- Intraday activity + heart rate ---
        # Skip intraday for the current UTC day (offset == 0) to avoid Fitbit
        # "time range start time cannot be in the future" errors when the local
        # Fitbit timezone is behind UTC.
        if offset > 0:
            try:
                _sync_intraday_for_date(conn, workout_tracker, token, date_str)
            except Exception as e:  # noqa: BLE001
                print(f"Warning: failed to sync intraday data for {date_str}: {e}", file=sys.stderr)

        # --- Existing behavior: import per-activity workouts ---
        activities = data.get("activities", [])
        if not activities:
            continue

        for act in activities:
            log_id = act.get("logId")
            start_time_str = act.get("startTime")  # e.g. "07:30"
            duration_ms = act.get("duration") or 0
            distance = act.get("distance")
            calories = act.get("calories")
            name = act.get("name") or act.get("activityName")

            duration_min = duration_ms / 60000.0 if duration_ms else None

            # Store start_time as ISO-like if we have time, else just date.
            if start_time_str:
                start_ts = f"{date_str}T{start_time_str}"
            else:
                start_ts = date_str

            payload = {
                "date": date_str,
                "start_time": start_ts,
                "end_time": None,
                "modality": name,
                "duration_min": duration_min,
                "distance_km": distance,
                "calories": calories,
                "avg_hr": None,
                "notes": None,
                "source": "fitbit",
                "external_id": str(log_id) if log_id is not None else None,
                "raw_payload": act,
            }

            workout_id = workout_tracker.log_manual_workout(conn, payload)
            print(f"Imported Fitbit activity logId={log_id} as workout_id={workout_id} on {date_str}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fitbit sync helper for workouts.db")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_start = subparsers.add_parser("start-auth", help="Print Fitbit authorization URL")

    p_finish = subparsers.add_parser("finish-auth", help="Exchange redirect URL for tokens")
    p_finish.add_argument("--redirect-url", required=True, help="Full redirect URL copied from browser")

    p_sync = subparsers.add_parser("sync-recent", help="Sync recent Fitbit activities into workouts.db")
    p_sync.add_argument("--days", type=int, default=7, help="Number of days back from today (UTC) to sync")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "start-auth":
        cfg = load_config()
        url = build_auth_url(cfg)
        print("Open this URL in your browser (logged into Fitbit):")
        print(url)
        print("\nAfter authorizing, copy the full redirect URL from the browser's address bar and run:")
        print("  python3 Personal/Health/WorkoutTracker/fitbit_sync.py finish-auth --redirect-url 'PASTE_URL_HERE'")

    elif args.command == "finish-auth":
        cfg = load_config()
        code = parse_auth_code_from_redirect(args.redirect_url)
        cfg = exchange_code_for_tokens(cfg, code)
        print("Stored Fitbit access and refresh tokens in fitbit_config.json")

    elif args.command == "sync-recent":
        sync_recent_activities(args.days)


if __name__ == "__main__":
    main()














