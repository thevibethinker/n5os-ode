#!/usr/bin/env python3
"""
Vibe Pill Hotline — Call Data Ingest Script

Accepts VAPI webhook JSON payloads and writes structured records to the
vibe-pill-calls DuckDB database. Designed to be called by the webhook
handler after each call ends.

Usage:
    python3 ingest.py --payload '{"message": {...}}' 
    python3 ingest.py --file /path/to/payload.json
    python3 ingest.py --file /path/to/payload.json --dry-run
    python3 ingest.py --upsert-member '{"phone":"+1...","name":"...","status":"member","tier":"founding-15"}'
    python3 ingest.py --log-escalation '{"call_id":"...","name":"...","contact":"...","reason":"..."}'
    python3 ingest.py --log-feedback '{"call_id":"...","caller_name":"...","satisfaction":5,"comment":"..."}'
    python3 ingest.py --log-application '{"phone":"+1...","name":"...","screening_notes":"..."}'
"""
import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import duckdb

DB_PATH = Path(__file__).parent.parent / "data.duckdb"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("vibe-pill-ingest")


def gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def connect():
    return duckdb.connect(str(DB_PATH))


def parse_vapi_payload(payload: dict) -> dict | None:
    msg = payload.get("message", payload)
    
    call = msg.get("call", msg)
    if not call.get("id"):
        log.warning("No call ID found in payload")
        return None

    started = call.get("startedAt") or call.get("createdAt")
    ended = call.get("endedAt")

    started_dt = datetime.fromisoformat(started.replace("Z", "+00:00")) if started else None
    ended_dt = datetime.fromisoformat(ended.replace("Z", "+00:00")) if ended else None

    duration = None
    if started_dt and ended_dt:
        duration = int((ended_dt - started_dt).total_seconds())

    customer = call.get("customer", {})
    phone = customer.get("number")

    analysis = call.get("analysis", {})
    summary = analysis.get("summary")

    tool_calls = msg.get("toolCalls", call.get("toolCalls", []))
    escalation_requested = False
    for tc in (tool_calls or []):
        fn = tc.get("function", {}).get("name", "")
        if "escalat" in fn.lower() or "transfer" in fn.lower():
            escalation_requested = True
            break

    return {
        "id": call["id"],
        "member_phone": phone,
        "member_name": None,
        "member_status": None,
        "started_at": started_dt,
        "ended_at": ended_dt,
        "duration_seconds": duration,
        "pathway": None,
        "outcome": None,
        "topics_discussed": None,
        "summary": summary,
        "escalation_requested": escalation_requested,
        "raw_data": json.dumps(call),
    }


def resolve_member(db, phone: str) -> dict | None:
    if not phone:
        return None
    rows = db.execute(
        "SELECT name, status FROM member_profiles WHERE phone = ?", [phone]
    ).fetchall()
    if rows:
        return {"name": rows[0][0], "status": rows[0][1]}
    return None


def update_member_call_stats(db, phone: str, call_time, pathway: str):
    if not phone:
        return
    existing = db.execute(
        "SELECT total_calls FROM member_profiles WHERE phone = ?", [phone]
    ).fetchone()
    if existing:
        db.execute("""
            UPDATE member_profiles
            SET total_calls = total_calls + 1,
                last_call_at = ?,
                last_pathway = ?
            WHERE phone = ?
        """, [call_time, pathway, phone])
    else:
        db.execute("""
            INSERT INTO member_profiles (phone, status, total_calls, first_call_at, last_call_at, last_pathway)
            VALUES (?, 'prospect', 1, ?, ?, ?)
        """, [phone, call_time, call_time, pathway])


def ingest_call(payload: dict, dry_run: bool = False) -> dict | None:
    record = parse_vapi_payload(payload)
    if not record:
        log.error("Failed to parse payload")
        return None

    if dry_run:
        log.info("[DRY RUN] Would insert call record:")
        for k, v in record.items():
            if k != "raw_data":
                log.info(f"  {k}: {v}")
        return record

    db = connect()
    try:
        member = resolve_member(db, record["member_phone"])
        if member:
            record["member_name"] = member["name"]
            record["member_status"] = member["status"]

        db.execute("""
            INSERT INTO calls (id, member_phone, member_name, member_status,
                started_at, ended_at, duration_seconds, pathway, outcome,
                topics_discussed, summary, escalation_requested, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            record["id"], record["member_phone"], record["member_name"],
            record["member_status"], record["started_at"], record["ended_at"],
            record["duration_seconds"], record["pathway"], record["outcome"],
            record["topics_discussed"], record["summary"],
            record["escalation_requested"], record["raw_data"],
        ])

        update_member_call_stats(
            db, record["member_phone"], record["started_at"], record["pathway"]
        )
        log.info(f"Ingested call {record['id']} (phone={record['member_phone']})")
        return record
    except Exception as e:
        log.error(f"Failed to ingest call: {e}")
        raise
    finally:
        db.close()


def upsert_member(data: dict, dry_run: bool = False):
    phone = data.get("phone")
    if not phone:
        log.error("Member upsert requires 'phone'")
        return

    if dry_run:
        log.info(f"[DRY RUN] Would upsert member: {phone}")
        for k, v in data.items():
            log.info(f"  {k}: {v}")
        return

    db = connect()
    try:
        existing = db.execute(
            "SELECT phone FROM member_profiles WHERE phone = ?", [phone]
        ).fetchone()

        if existing:
            updates = []
            params = []
            for field in ["name", "email", "status", "tier", "stripe_customer_id", "notes"]:
                if field in data and data[field] is not None:
                    updates.append(f"{field} = ?")
                    params.append(data[field])
            if updates:
                params.append(phone)
                db.execute(
                    f"UPDATE member_profiles SET {', '.join(updates)} WHERE phone = ?",
                    params
                )
                log.info(f"Updated member {phone}")
        else:
            now = datetime.now(timezone.utc)
            db.execute("""
                INSERT INTO member_profiles (phone, name, email, status, tier,
                    stripe_customer_id, total_calls, first_call_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
            """, [
                phone, data.get("name"), data.get("email"),
                data.get("status", "prospect"), data.get("tier"),
                data.get("stripe_customer_id"), now, data.get("notes"),
            ])
            log.info(f"Created member profile {phone}")
    finally:
        db.close()


def log_escalation(data: dict, dry_run: bool = False):
    esc_id = gen_id("esc")
    now = datetime.now(timezone.utc)

    if dry_run:
        log.info(f"[DRY RUN] Would log escalation {esc_id}: {data}")
        return

    db = connect()
    try:
        db.execute("""
            INSERT INTO escalations (id, call_id, name, contact, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [esc_id, data.get("call_id"), data.get("name"),
              data.get("contact"), data.get("reason"), now])
        log.info(f"Logged escalation {esc_id}")
    finally:
        db.close()


def log_feedback(data: dict, dry_run: bool = False):
    fb_id = gen_id("fb")
    now = datetime.now(timezone.utc)

    if dry_run:
        log.info(f"[DRY RUN] Would log feedback {fb_id}: {data}")
        return

    db = connect()
    try:
        db.execute("""
            INSERT INTO feedback (id, call_id, caller_name, satisfaction, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [fb_id, data.get("call_id"), data.get("caller_name"),
              data.get("satisfaction"), data.get("comment"), now])
        log.info(f"Logged feedback {fb_id} (satisfaction={data.get('satisfaction')})")
    finally:
        db.close()


def log_application(data: dict, dry_run: bool = False):
    app_id = gen_id("app")
    now = datetime.now(timezone.utc)

    if dry_run:
        log.info(f"[DRY RUN] Would log application {app_id}: {data}")
        return

    db = connect()
    try:
        db.execute("""
            INSERT INTO applications (id, phone, name, screening_notes, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, [app_id, data.get("phone"), data.get("name"),
              data.get("screening_notes"), now])
        log.info(f"Logged application {app_id} for {data.get('name')}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Vibe Pill call data ingest")
    parser.add_argument("--payload", help="JSON string of VAPI webhook payload")
    parser.add_argument("--file", help="Path to JSON file with VAPI webhook payload")
    parser.add_argument("--upsert-member", help="JSON string for member upsert")
    parser.add_argument("--log-escalation", help="JSON string for escalation")
    parser.add_argument("--log-feedback", help="JSON string for feedback")
    parser.add_argument("--log-application", help="JSON string for application")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without writing")
    args = parser.parse_args()

    if args.upsert_member:
        data = json.loads(args.upsert_member)
        upsert_member(data, dry_run=args.dry_run)
    elif args.log_escalation:
        data = json.loads(args.log_escalation)
        log_escalation(data, dry_run=args.dry_run)
    elif args.log_feedback:
        data = json.loads(args.log_feedback)
        log_feedback(data, dry_run=args.dry_run)
    elif args.log_application:
        data = json.loads(args.log_application)
        log_application(data, dry_run=args.dry_run)
    elif args.payload:
        payload = json.loads(args.payload)
        ingest_call(payload, dry_run=args.dry_run)
    elif args.file:
        with open(args.file) as f:
            payload = json.load(f)
        ingest_call(payload, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
