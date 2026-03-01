#!/usr/bin/env python3
"""
Dual-Sided Audit Logger - Zoffice Consultancy Stack

Tracks ALL communications between va and zoputer independently on both sides.
Creates an immutable audit trail for security and discrepancy detection.

Usage:
    python3 audit_logger.py log --type api_call --direction va-to-zoputer --payload '{...}'
    python3 audit_logger.py log --type email --direction zoputer-to-client --content "..."
    python3 audit_logger.py list --limit 10
    python3 audit_logger.py verify --cross-check-with zoputer  # Detect discrepancies
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Database path - stored in N5/config/consulting for durability
DB_PATH = Path("/home/workspace/N5/config/consulting/audit_log.db")

# Zo instance identifier - set this per instance
ZO_INSTANCE = "va"  # Change to "zoputer" on the other side


def init_db() -> None:
    """Initialize the audit database with schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            zo_instance TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            direction TEXT NOT NULL,
            correlation_id TEXT,
            payload_hash TEXT NOT NULL,
            payload TEXT NOT NULL,
            metadata TEXT,
            verified_at TEXT,
            verification_status TEXT DEFAULT 'pending'
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_entries(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_correlation ON audit_entries(correlation_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_type_direction ON audit_entries(entry_type, direction)
    """)
    
    conn.commit()
    conn.close()


def compute_hash(payload: str) -> str:
    """Compute SHA-256 hash of payload for integrity verification."""
    return hashlib.sha256(payload.encode()).hexdigest()


def log_entry(
    entry_type: str,
    direction: str,
    payload: str,
    correlation_id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> int:
    """
    Log an audit entry.
    
    Args:
        entry_type: Type of entry (api_call, email, skill_bundle, etc.)
        direction: Direction of communication (va-to-zoputer, zoputer-to-va, etc.)
        payload: The actual content/data being logged
        correlation_id: Optional ID to link related entries
        metadata: Optional dict of additional context
    
    Returns:
        The ID of the created entry
    """
    if not DB_PATH.exists():
        init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now(timezone.utc).isoformat()
    payload_hash = compute_hash(payload)
    metadata_json = json.dumps(metadata) if metadata else None
    
    cursor.execute("""
        INSERT INTO audit_entries 
        (timestamp, zo_instance, entry_type, direction, correlation_id, payload_hash, payload, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, ZO_INSTANCE, entry_type, direction, correlation_id, payload_hash, payload, metadata_json))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return entry_id


def list_entries(
    entry_type: Optional[str] = None,
    direction: Optional[str] = None,
    limit: int = 50,
    since: Optional[str] = None
) -> list:
    """List audit entries with optional filtering."""
    if not DB_PATH.exists():
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT * FROM audit_entries WHERE 1=1"
    params = []
    
    if entry_type:
        query += " AND entry_type = ?"
        params.append(entry_type)
    
    if direction:
        query += " AND direction = ?"
        params.append(direction)
    
    if since:
        query += " AND timestamp > ?"
        params.append(since)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    
    entries = []
    for row in rows:
        entry = dict(zip(columns, row))
        # Parse metadata JSON
        if entry.get('metadata'):
            try:
                entry['metadata'] = json.loads(entry['metadata'])
            except json.JSONDecodeError:
                pass
        entries.append(entry)
    
    conn.close()
    return entries


def verify_integrity(entry_id: Optional[int] = None) -> dict:
    """
    Verify the integrity of audit entries by re-computing hashes.
    
    Returns:
        dict with verification results
    """
    if not DB_PATH.exists():
        return {"error": "Database does not exist"}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if entry_id:
        cursor.execute("SELECT id, payload, payload_hash FROM audit_entries WHERE id = ?", (entry_id,))
    else:
        cursor.execute("SELECT id, payload, payload_hash FROM audit_entries")
    
    rows = cursor.fetchall()
    
    verified = 0
    failed = []
    
    for row_id, payload, stored_hash in rows:
        computed_hash = compute_hash(payload)
        if computed_hash == stored_hash:
            verified += 1
            cursor.execute(
                "UPDATE audit_entries SET verification_status = ?, verified_at = ? WHERE id = ?",
                ("verified", datetime.now(timezone.utc).isoformat(), row_id)
            )
        else:
            failed.append({
                "id": row_id,
                "stored_hash": stored_hash,
                "computed_hash": computed_hash
            })
            cursor.execute(
                "UPDATE audit_entries SET verification_status = ? WHERE id = ?",
                ("FAILED_INTEGRITY_CHECK", row_id)
            )
    
    conn.commit()
    conn.close()
    
    return {
        "total_checked": len(rows),
        "verified": verified,
        "failed": failed,
        "integrity_intact": len(failed) == 0
    }


def export_for_cross_check(output_path: Optional[str] = None) -> str:
    """
    Export audit data for cross-checking with the other Zo instance.
    
    Returns:
        Path to exported file
    """
    if not DB_PATH.exists():
        return ""
    
    entries = list_entries(limit=10000)  # Export last 10k entries
    
    # Create minimal export with just verification data
    export_data = {
        "zo_instance": ZO_INSTANCE,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "entry_count": len(entries),
        "entries": [
            {
                "id": e["id"],
                "timestamp": e["timestamp"],
                "entry_type": e["entry_type"],
                "direction": e["direction"],
                "correlation_id": e["correlation_id"],
                "payload_hash": e["payload_hash"],
            }
            for e in entries
        ]
    }
    
    if output_path:
        output_file = Path(output_path)
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"/home/workspace/N5/config/consulting/audit_export_{ZO_INSTANCE}_{timestamp}.json")
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(export_data, indent=2))
    
    return str(output_file)


def cross_check(other_instance_export: str) -> dict:
    """
    Cross-check our audit log against the other Zo instance's export.
    Detects missing entries or discrepancies.
    
    Args:
        other_instance_export: Path to the other instance's export file
    
    Returns:
        dict with discrepancy report
    """
    if not DB_PATH.exists():
        return {"error": "Local database does not exist"}
    
    other_data = json.loads(Path(other_instance_export).read_text())
    other_instance = other_data["zo_instance"]
    other_entries = {e["correlation_id"]: e for e in other_data["entries"] if e["correlation_id"]}
    
    # Get our entries that should match
    our_entries = list_entries(limit=10000)
    our_correlated = {e["correlation_id"]: e for e in our_entries if e["correlation_id"]}
    
    discrepancies = {
        "missing_from_local": [],
        "missing_from_remote": [],
        "hash_mismatch": [],
        "summary": {
            "local_entries": len(our_correlated),
            "remote_entries": len(other_entries),
        }
    }
    
    # Check for entries we're missing
    for corr_id, remote_entry in other_entries.items():
        if corr_id not in our_correlated:
            discrepancies["missing_from_local"].append(corr_id)
    
    # Check for entries they're missing
    for corr_id, local_entry in our_correlated.items():
        if corr_id not in other_entries:
            discrepancies["missing_from_remote"].append(corr_id)
        elif local_entry["payload_hash"] != other_entries[corr_id]["payload_hash"]:
            discrepancies["hash_mismatch"].append({
                "correlation_id": corr_id,
                "local_hash": local_entry["payload_hash"],
                "remote_hash": other_entries[corr_id]["payload_hash"]
            })
    
    discrepancies["summary"]["discrepancy_count"] = (
        len(discrepancies["missing_from_local"]) +
        len(discrepancies["missing_from_remote"]) +
        len(discrepancies["hash_mismatch"])
    )
    discrepancies["summary"]["in_sync"] = discrepancies["summary"]["discrepancy_count"] == 0
    
    return discrepancies


def main():
    parser = argparse.ArgumentParser(description="Dual-Sided Audit Logger")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # log command
    log_parser = subparsers.add_parser("log", help="Log an audit entry")
    log_parser.add_argument("--type", required=True, help="Entry type (api_call, email, etc.)")
    log_parser.add_argument("--direction", required=True, help="Direction (va-to-zoputer, etc.)")
    log_parser.add_argument("--payload", required=True, help="Payload content")
    log_parser.add_argument("--correlation-id", help="Correlation ID for linking entries")
    log_parser.add_argument("--metadata", help="JSON metadata")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List audit entries")
    list_parser.add_argument("--type", help="Filter by entry type")
    list_parser.add_argument("--direction", help="Filter by direction")
    list_parser.add_argument("--limit", type=int, default=50, help="Limit results")
    list_parser.add_argument("--since", help="Entries since timestamp (ISO format)")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # verify command
    verify_parser = subparsers.add_parser("verify", help="Verify integrity")
    verify_parser.add_argument("--entry-id", type=int, help="Verify specific entry")
    
    # export command
    export_parser = subparsers.add_parser("export", help="Export for cross-check")
    export_parser.add_argument("--output", help="Output file path")
    
    # cross-check command
    cross_parser = subparsers.add_parser("cross-check", help="Cross-check with other instance")
    cross_parser.add_argument("--other-export", required=True, help="Path to other instance's export")
    
    # init command
    subparsers.add_parser("init", help="Initialize database")
    
    # stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_db()
        print(f"Initialized audit database at {DB_PATH}")
    
    elif args.command == "log":
        metadata = json.loads(args.metadata) if args.metadata else None
        entry_id = log_entry(
            entry_type=args.type,
            direction=args.direction,
            payload=args.payload,
            correlation_id=args.correlation_id,
            metadata=metadata
        )
        print(f"Logged entry {entry_id}")
    
    elif args.command == "list":
        entries = list_entries(
            entry_type=args.type,
            direction=args.direction,
            limit=args.limit,
            since=args.since
        )
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            print(f"{'ID':<6} {'Time':<20} {'Type':<15} {'Direction':<20} {'Correlation':<20}")
            print("-" * 90)
            for e in entries:
                print(f"{e['id']:<6} {e['timestamp'][:19]:<20} {e['entry_type']:<15} {e['direction']:<20} {str(e['correlation_id'])[:18]:<20}")
    
    elif args.command == "verify":
        result = verify_integrity(args.entry_id)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("integrity_intact", False) else 1)
    
    elif args.command == "export":
        path = export_for_cross_check(args.output)
        print(f"Exported to: {path}")
    
    elif args.command == "cross-check":
        result = cross_check(args.other_export)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["summary"]["in_sync"] else 1)
    
    elif args.command == "stats":
        if not DB_PATH.exists():
            print("Database not initialized")
            sys.exit(1)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM audit_entries")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT entry_type, COUNT(*) FROM audit_entries GROUP BY entry_type")
        by_type = cursor.fetchall()
        
        cursor.execute("SELECT direction, COUNT(*) FROM audit_entries GROUP BY direction")
        by_direction = cursor.fetchall()
        
        conn.close()
        
        print(f"Total entries: {total}")
        print(f"\nBy type:")
        for t, c in by_type:
            print(f"  {t}: {c}")
        print(f"\nBy direction:")
        for d, c in by_direction:
            print(f"  {d}: {c}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
