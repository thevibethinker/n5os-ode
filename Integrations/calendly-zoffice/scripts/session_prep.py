#!/usr/bin/env python3

import argparse
import hashlib
import hmac
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

sys.path.insert(0, '/home/workspace/Skills/audit-system/scripts')
from audit_logger import log_entry

STATE_DIR = Path('/home/workspace/N5/config/consulting/calendly_zoffice')
SESSIONS_FILE = STATE_DIR / 'sessions.json'
JOBS_FILE = STATE_DIR / 'jobs.json'
NOTIFICATIONS_FILE = STATE_DIR / 'notifications.jsonl'
HOLD_FILE = STATE_DIR / 'hold.json'

DEFAULT_MANIFEST_PATH = Path('/home/workspace/N5/config/consulting/CONSULTING_MANIFEST.md')

ZO_WORKER_SCRIPT = Path('/home/workspace/N5/scripts/zoffice_worker.py')


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return default


def _save_json(path: Path, data: Any) -> None:
    _ensure_state_dir()
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _append_jsonl(path: Path, obj: dict) -> None:
    _ensure_state_dir()
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def _get_nested(obj: dict, dotted: str) -> Optional[Any]:
    cur: Any = obj
    for part in dotted.split('.'):
        if not isinstance(cur, dict):
            return None
        if part not in cur:
            return None
        cur = cur[part]
    return cur


def _first_present(obj: dict, keys: list[str]) -> Optional[Any]:
    for k in keys:
        v = _get_nested(obj, k)
        if v is not None and v != '':
            return v
    return None


def _parse_dt(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _load_event_type_config(event_type_name: str) -> dict:
    cfg_path = Path('/home/workspace/Integrations/calendly-zoffice/config/event_types.json')
    try:
        cfg = json.loads(cfg_path.read_text())
    except Exception:
        cfg = {"default": {"activation_offset_minutes": 15, "deactivate_offset_minutes": 30, "default_duration_minutes": 60}}

    base = cfg.get('default', {})
    by_name = cfg.get('by_event_type_name', {})
    specific = by_name.get(event_type_name, {}) if isinstance(by_name, dict) else {}

    merged = dict(base)
    merged.update(specific)
    return merged


def _manifest_path() -> Path:
    p = (os.environ.get('CONSULTING_MANIFEST_PATH') or '').strip()
    return Path(p) if p else DEFAULT_MANIFEST_PATH


def _ensure_manifest_exists(path: Path) -> None:
    if path.exists():
        # Best-effort frontmatter last_edited update
        try:
            lines = path.read_text().splitlines()
            if len(lines) >= 4 and lines[0].strip() == '---':
                for i, line in enumerate(lines[:30]):
                    if line.startswith('last_edited:'):
                        lines[i] = f"last_edited: {_utc_now().date().isoformat()}"
                        path.write_text('\n'.join(lines) + '\n')
                        return
        except Exception:
            pass
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"created: {_utc_now().date().isoformat()}\n"
        f"last_edited: {_utc_now().date().isoformat()}\n"
        "version: 1.0\n"
        "provenance: calendly-zoffice\n"
        "---\n\n"
        "# Consulting Manifest\n\n"
        "Log of consulting sessions created from Calendly webhooks.\n\n"
        "## Sessions\n"
    )


def _append_manifest_session(path: Path, session: dict) -> None:
    _ensure_manifest_exists(path)
    start = session.get('start_time_utc')
    client = session.get('client_name') or 'Unknown'
    email = session.get('client_email') or 'unknown'
    etype = session.get('event_type') or 'Meeting'
    status = session.get('status')
    sid = session.get('session_id')

    line = f"- {start} | {client} ({email}) | {etype} | status={status} | session_id={sid}\n"
    with path.open('a', encoding='utf-8') as f:
        f.write(line)


def is_hold_enabled() -> bool:
    hold = _load_json(HOLD_FILE, {"hold": False})
    return bool(hold.get('hold', False))


def set_hold(enabled: bool, reason: str = "") -> None:
    _save_json(HOLD_FILE, {"hold": enabled, "reason": reason, "updated_at": _utc_now().isoformat()})


def _job_id(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()[:16]


def upsert_session_and_jobs(session: dict) -> Tuple[str, str]:
    """Returns (activation_job_id, deactivation_job_id)."""
    _ensure_state_dir()

    sessions = _load_json(SESSIONS_FILE, {})
    jobs = _load_json(JOBS_FILE, {})

    session_id = session['session_id']
    sessions[session_id] = session

    # Jobs
    activation_job_id = _job_id(f"{session_id}:activate:{session['activation_time_utc']}")
    deactivation_job_id = _job_id(f"{session_id}:deactivate:{session['deactivation_time_utc']}")

    def put_job(job_id: str, run_at: str, action: str):
        jobs[job_id] = {
            "job_id": job_id,
            "session_id": session_id,
            "run_at_utc": run_at,
            "action": action,
            "status": "scheduled",
            "created_at_utc": _utc_now().isoformat(),
            "last_error": None,
        }

    put_job(activation_job_id, session['activation_time_utc'], 'activate_consultant')
    put_job(deactivation_job_id, session['deactivation_time_utc'], 'deactivate_consultant')

    _save_json(SESSIONS_FILE, sessions)
    _save_json(JOBS_FILE, jobs)

    return activation_job_id, deactivation_job_id


def cancel_session(session_id: str, reason: str) -> dict:
    sessions = _load_json(SESSIONS_FILE, {})
    jobs = _load_json(JOBS_FILE, {})

    s = sessions.get(session_id)
    if not s:
        return {"status": "not_found", "session_id": session_id}

    s['status'] = 'canceled'
    s['canceled_at_utc'] = _utc_now().isoformat()
    s['cancel_reason'] = reason

    for job in jobs.values():
        if job.get('session_id') == session_id and job.get('status') == 'scheduled':
            job['status'] = 'canceled'
            job['canceled_at_utc'] = _utc_now().isoformat()
            job['cancel_reason'] = reason

    _save_json(SESSIONS_FILE, sessions)
    _save_json(JOBS_FILE, jobs)

    return {"status": "canceled", "session_id": session_id}


def _emit_notifications(session: dict) -> None:
    client_name = session.get('client_name') or 'Unknown'
    client_email = session.get('client_email') or ''
    event_type = session.get('event_type') or 'Meeting'

    subject = f"[Zoffice] Consulting session scheduled - {client_name}"
    body = (
        "Session Details:\n"
        f"- Client: {client_name} ({client_email})\n"
        f"- Time (UTC): {session.get('start_time_utc')}\n"
        f"- Type: {event_type}\n\n"
        f"Zoputer will activate Consultant persona at {session.get('activation_time_utc')} UTC.\n"
        "You'll receive a briefing closer to the session.\n"
    )

    sms = f"[Zoffice] Session with {client_name} in 15 min. Consultant active soon."

    _append_jsonl(NOTIFICATIONS_FILE, {
        "created_at_utc": _utc_now().isoformat(),
        "type": "email",
        "subject": subject,
        "body": body,
        "session_id": session['session_id'],
    })

    _append_jsonl(NOTIFICATIONS_FILE, {
        "created_at_utc": _utc_now().isoformat(),
        "type": "sms",
        "message": sms,
        "session_id": session['session_id'],
    })


def build_session_from_calendly_event(event: dict) -> Optional[dict]:
    # Supports both Calendly native payloads and legacy placeholder payloads.

    # New format
    event_type = event.get('event') or event.get('event_type')
    payload = event.get('payload') if isinstance(event.get('payload'), dict) else event

    client_name = _first_present(payload, ['name', 'invitee.name', 'invitee.first_name'])
    client_email = _first_present(payload, ['email', 'invitee.email'])

    event_type_name = _first_present(payload, ['event_type.name', 'event_type_name']) or 'Meeting'
    scheduled_event_uri = _first_present(payload, ['scheduled_event.uri', 'scheduled_event_uri'])

    start_time_raw = _first_present(payload, ['scheduled_event.start_time', 'start_time'])
    end_time_raw = _first_present(payload, ['scheduled_event.end_time', 'end_time'])

    start_dt = _parse_dt(str(start_time_raw or ''))
    end_dt = _parse_dt(str(end_time_raw or ''))

    if start_dt is None:
        return None

    cfg = _load_event_type_config(str(event_type_name))
    activation_offset = int(cfg.get('activation_offset_minutes', 15))
    deactivate_offset = int(cfg.get('deactivate_offset_minutes', 30))
    default_duration = int(cfg.get('default_duration_minutes', 60))

    if end_dt is None:
        end_dt = start_dt + timedelta(minutes=default_duration)

    activation_dt = start_dt - timedelta(minutes=activation_offset)
    deactivation_dt = end_dt + timedelta(minutes=deactivate_offset)

    # Session ID strategy: stable across retries
    session_id = scheduled_event_uri or _job_id(f"{client_email}:{start_dt.isoformat()}:{event_type_name}")

    session = {
        "session_id": session_id,
        "source": "calendly",
        "calendly_event": event_type,
        "client_name": client_name,
        "client_email": client_email,
        "event_type": event_type_name,
        "scheduled_event_uri": scheduled_event_uri,
        "start_time_utc": start_dt.isoformat(),
        "end_time_utc": end_dt.isoformat(),
        "activation_time_utc": activation_dt.isoformat(),
        "deactivation_time_utc": deactivation_dt.isoformat(),
        "status": "scheduled",
        "created_at_utc": _utc_now().isoformat(),
    }

    return session


def handle_invitee_created(event: dict) -> dict:
    session = build_session_from_calendly_event(event)
    if not session:
        return {"status": "error", "error": "Could not parse start_time"}

    activation_job_id, deactivation_job_id = upsert_session_and_jobs(session)
    _append_manifest_session(_manifest_path(), session)
    _emit_notifications(session)

    log_entry(
        entry_type='calendly_invitee_created',
        direction='calendly-to-zoputer',
        payload=json.dumps({"session": session, "activation_job_id": activation_job_id, "deactivation_job_id": deactivation_job_id}),
        metadata={"session_id": session['session_id']}
    )

    return {
        "status": "scheduled",
        "session_id": session['session_id'],
        "activation_job_id": activation_job_id,
        "deactivation_job_id": deactivation_job_id,
    }


def handle_invitee_canceled(event: dict) -> dict:
    payload = event.get('payload') if isinstance(event.get('payload'), dict) else event
    scheduled_event_uri = _first_present(payload, ['scheduled_event.uri', 'scheduled_event_uri'])

    # Fallback: try reconstruct if no URI
    if scheduled_event_uri:
        session_id = scheduled_event_uri
    else:
        sess = build_session_from_calendly_event(event)
        if not sess:
            return {"status": "error", "error": "Could not identify session"}
        session_id = sess['session_id']

    result = cancel_session(session_id, reason='invitee.canceled')

    log_entry(
        entry_type='calendly_invitee_canceled',
        direction='calendly-to-zoputer',
        payload=json.dumps({"session_id": session_id, "result": result}),
        metadata={"session_id": session_id}
    )

    return result


def _run_worker_cmd(args: list[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def tick(now: Optional[datetime] = None, execute: bool = True) -> dict:
    if now is None:
        now = _utc_now()

    jobs = _load_json(JOBS_FILE, {})
    sessions = _load_json(SESSIONS_FILE, {})

    if is_hold_enabled():
        return {"status": "hold", "message": "Hold enabled; skipping execution", "checked_at_utc": now.isoformat()}

    ran = []
    for job_id, job in jobs.items():
        if job.get('status') != 'scheduled':
            continue

        run_at = _parse_dt(job.get('run_at_utc', ''))
        if not run_at or run_at > now:
            continue

        session = sessions.get(job.get('session_id'))
        if session and session.get('status') == 'canceled':
            job['status'] = 'skipped_canceled_session'
            continue

        action = job.get('action')
        cmd = None

        if action == 'activate_consultant':
            cmd = ['python3', str(ZO_WORKER_SCRIPT), 'activate', 'consultant']
        elif action == 'deactivate_consultant':
            cmd = ['python3', str(ZO_WORKER_SCRIPT), 'deactivate', 'consultant']
        else:
            job['status'] = 'failed'
            job['last_error'] = f"Unknown action: {action}"
            continue

        if execute:
            rc, out, err = _run_worker_cmd(cmd)
        else:
            rc, out, err = 0, '[dry-run]', ''

        if rc == 0:
            job['status'] = 'executed'
            job['executed_at_utc'] = now.isoformat()
            ran.append({"job_id": job_id, "action": action, "stdout": out})
            log_entry(
                entry_type='consultant_job_executed',
                direction='zoputer-internal',
                payload=json.dumps({"job": job, "stdout": out}),
                metadata={"job_id": job_id, "action": action}
            )
        else:
            job['status'] = 'failed'
            job['last_error'] = err or out or f"rc={rc}"
            log_entry(
                entry_type='consultant_job_failed',
                direction='zoputer-internal',
                payload=json.dumps({"job": job, "stdout": out, "stderr": err, "rc": rc}),
                metadata={"job_id": job_id, "action": action}
            )

    _save_json(JOBS_FILE, jobs)

    return {"status": "ok", "ran": ran, "checked_at_utc": now.isoformat()}


def main():
    parser = argparse.ArgumentParser(description='Calendly → Zoffice session preparation + job runner')
    sub = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('tick', help='Execute any due activation/deactivation jobs')

    hold_p = sub.add_parser('hold', help='Pause auto-activation')
    hold_p.add_argument('--reason', default='')

    sub.add_parser('resume', help='Resume auto-activation')

    args = parser.parse_args()

    if args.cmd == 'tick':
        result = tick()
        print(json.dumps(result, indent=2))
    elif args.cmd == 'hold':
        set_hold(True, reason=args.reason)
        print(json.dumps({"status": "ok", "hold": True, "reason": args.reason}, indent=2))
    elif args.cmd == 'resume':
        set_hold(False, reason='')
        print(json.dumps({"status": "ok", "hold": False}, indent=2))


if __name__ == '__main__':
    main()
