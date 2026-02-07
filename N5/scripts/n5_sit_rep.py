#!/usr/bin/env python3
"""
N5 Sit Rep: System-wide status report for all Zo operations.

Surfaces:
- Active Pulse builds (progress, drops, health)
- Headless worker conversations (running, stuck, complete)
- Scheduled agents (active count, next runs)
- Stale/zombie detection

Usage:
  python3 N5/scripts/n5_sit_rep.py          # Full report
  python3 N5/scripts/n5_sit_rep.py --brief  # SMS-friendly brief
  python3 N5/scripts/n5_sit_rep.py --json   # Machine-readable
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
CONVERSATIONS_DB = WORKSPACE / "N5" / "data" / "conversations.db"
PULSE_CONTROL = WORKSPACE / "N5" / "config" / "pulse_control.json"

STALE_THRESHOLD_HOURS = 2  # Mark "running" conversations as stale after this


def get_pulse_builds() -> list[dict]:
    """Get status of all active/recent Pulse builds."""
    builds = []
    if not BUILDS_DIR.exists():
        return builds
    
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue
        meta_path = build_dir / "meta.json"
        if not meta_path.exists():
            continue
        
        try:
            with open(meta_path) as f:
                meta = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue
        
        status = meta.get("status", "unknown")
        # Only show active, partial, or recently completed
        if status not in ["active", "partial", "stopped"]:
            completed_at = meta.get("completed_at")
            if completed_at:
                try:
                    completed_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    if datetime.now(timezone.utc) - completed_dt > timedelta(hours=24):
                        continue
                except:
                    continue
            else:
                continue
        
        drops = meta.get("drops", {})
        complete = sum(1 for d in drops.values() if d.get("status") == "complete")
        running = sum(1 for d in drops.values() if d.get("status") == "running")
        awaiting = sum(1 for d in drops.values() if d.get("status") == "awaiting_manual")
        pending = sum(1 for d in drops.values() if d.get("status") == "pending")
        dead = sum(1 for d in drops.values() if d.get("status") == "dead")
        failed = sum(1 for d in drops.values() if d.get("status") == "failed")
        total = len(drops)
        
        # Check for stale running drops
        stale_drops = []
        for drop_id, info in drops.items():
            if info.get("status") == "running":
                started_at = info.get("started_at")
                if started_at:
                    try:
                        started_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                        elapsed = datetime.now(timezone.utc) - started_dt
                        if elapsed > timedelta(hours=STALE_THRESHOLD_HOURS):
                            stale_drops.append({
                                "drop_id": drop_id,
                                "elapsed_minutes": int(elapsed.total_seconds() / 60)
                            })
                    except:
                        pass
        
        builds.append({
            "slug": build_dir.name,
            "status": status,
            "wave": meta.get("active_wave"),
            "progress": {
                "complete": complete,
                "running": running,
                "awaiting_manual": awaiting,
                "pending": pending,
                "dead": dead,
                "failed": failed,
                "total": total,
                "pct": int(complete / total * 100) if total > 0 else 0
            },
            "stale_drops": stale_drops,
            "gate": meta.get("gate")
        })
    
    return builds


def get_headless_conversations() -> dict:
    """Get status of headless worker conversations."""
    result = {
        "running": 0,
        "complete": 0,
        "stale": [],
        "recent_complete": []
    }
    
    if not CONVERSATIONS_DB.exists():
        return result
    
    try:
        conn = sqlite3.connect(CONVERSATIONS_DB)
        cursor = conn.cursor()
        
        # Check if headless_worker type exists
        cursor.execute("""
            SELECT id, status, build_slug, drop_id, created_at, updated_at 
            FROM conversations 
            WHERE type = 'headless_worker'
        """)
        
        rows = cursor.fetchall()
        now = datetime.now(timezone.utc)
        
        for row in rows:
            conv_id, status, build_slug, drop_id, created_at, updated_at = row
            
            if status == "complete":
                result["complete"] += 1
                # Track recently completed (last 24h)
                try:
                    updated_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    if now - updated_dt < timedelta(hours=24):
                        result["recent_complete"].append({
                            "id": conv_id,
                            "build": build_slug,
                            "drop": drop_id
                        })
                except:
                    pass
            elif status == "running":
                result["running"] += 1
                # Check if stale
                try:
                    updated_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    elapsed = now - updated_dt
                    if elapsed > timedelta(hours=STALE_THRESHOLD_HOURS):
                        result["stale"].append({
                            "id": conv_id,
                            "build": build_slug,
                            "drop": drop_id,
                            "elapsed_hours": round(elapsed.total_seconds() / 3600, 1)
                        })
                except:
                    pass
        
        conn.close()
    except Exception as e:
        result["error"] = str(e)
    
    return result


def get_scheduled_agents_summary() -> dict:
    """Get summary of scheduled agents (requires API or list_agents output)."""
    # This would need to call the Zo API, but for now we'll return a placeholder
    # that can be filled in by the calling context
    return {
        "note": "Call list_agents separately for full agent status"
    }


def get_pulse_control() -> dict:
    """Get Pulse control state."""
    if PULSE_CONTROL.exists():
        try:
            with open(PULSE_CONTROL) as f:
                return json.load(f)
        except:
            pass
    return {"state": "unknown"}


def generate_report() -> dict:
    """Generate full sit rep report."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pulse": {
            "control": get_pulse_control(),
            "builds": get_pulse_builds()
        },
        "headless": get_headless_conversations(),
        "agents": get_scheduled_agents_summary()
    }


def format_brief(report: dict) -> str:
    """Format report as SMS-friendly brief."""
    lines = []
    
    # Pulse builds
    builds = report["pulse"]["builds"]
    if builds:
        active = [b for b in builds if b["status"] == "active"]
        if active:
            for b in active:
                p = b["progress"]
                stale = len(b.get("stale_drops", []))
                status_emoji = "🔴" if stale else "🟢"
                lines.append(f"{status_emoji} {b['slug']}: {p['complete']}/{p['total']} ({p['pct']}%)")
                if stale:
                    lines.append(f"   ⚠️ {stale} stale drops")
        else:
            lines.append("No active builds")
    else:
        lines.append("No builds")
    
    # Headless workers
    h = report["headless"]
    stale_count = len(h.get("stale", []))
    if h["running"] > 0 or stale_count > 0:
        lines.append(f"Workers: {h['running']} running, {stale_count} stale")
    
    return "\n".join(lines)


def format_full(report: dict) -> str:
    """Format report as full readable text."""
    lines = ["=" * 50, "N5 SIT REP", f"Generated: {report['timestamp']}", "=" * 50, ""]
    
    # Pulse section
    lines.append("## PULSE BUILDS")
    pulse_control = report["pulse"]["control"]
    lines.append(f"Control State: {pulse_control.get('state', 'unknown')}")
    lines.append("")
    
    builds = report["pulse"]["builds"]
    if builds:
        for b in builds:
            p = b["progress"]
            lines.append(f"### {b['slug']} [{b['status'].upper()}]")
            lines.append(f"Progress: {p['complete']}/{p['total']} ({p['pct']}%)")
            if b.get("wave"):
                lines.append(f"Wave: {b['wave']}")
            lines.append(f"  Running: {p['running']}, Pending: {p['pending']}")
            lines.append(f"  Awaiting Manual: {p['awaiting_manual']}")
            lines.append(f"  Dead: {p['dead']}, Failed: {p['failed']}")
            
            if b.get("stale_drops"):
                lines.append("  ⚠️ STALE DROPS:")
                for sd in b["stale_drops"]:
                    lines.append(f"    - {sd['drop_id']}: {sd['elapsed_minutes']} min")
            
            if b.get("gate"):
                lines.append(f"  GATE: {b['gate'].get('reason', 'Unknown')}")
            lines.append("")
    else:
        lines.append("No active or recent builds")
        lines.append("")
    
    # Headless workers section
    lines.append("## HEADLESS WORKERS")
    h = report["headless"]
    lines.append(f"Running: {h['running']}")
    lines.append(f"Complete: {h['complete']}")
    
    if h.get("stale"):
        lines.append(f"\n⚠️ STALE ({len(h['stale'])}):")
        for s in h["stale"][:5]:  # Limit to 5
            lines.append(f"  - {s['build']}/{s['drop']}: {s['elapsed_hours']}h")
        if len(h["stale"]) > 5:
            lines.append(f"  ... and {len(h['stale']) - 5} more")
    
    if h.get("recent_complete"):
        lines.append(f"\nRecent completions: {len(h['recent_complete'])}")
    
    lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="N5 Sit Rep - System Status Report")
    parser.add_argument("--brief", action="store_true", help="SMS-friendly brief output")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    
    report = generate_report()
    
    if args.json:
        print(json.dumps(report, indent=2))
    elif args.brief:
        print(format_brief(report))
    else:
        print(format_full(report))


if __name__ == "__main__":
    main()
