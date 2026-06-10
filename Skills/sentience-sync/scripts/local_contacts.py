#!/usr/bin/env python3
"""
Local contacts store — replaces external CRM index as the identity resolution source.

Stores people and companies in SQLite. Exports to the same JSON shape the
IdentityResolver already consumes, so no resolver changes are needed.

Seed from: existing local contact index, pipeline-approved contacts, manual adds.
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "contacts.db"
INDEX_OUTPUT = DATA_DIR / "local_contact_index.json"
LEGACY_CONTACT_SNAPSHOT = INDEX_OUTPUT


def get_db(db_path: Path | None = None) -> sqlite3.Connection:
    p = db_path or DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS people (
            id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            job_title TEXT,
            company TEXT,
            linkedin TEXT,
            source TEXT DEFAULT 'manual',
            created_at TEXT,
            updated_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_people_email ON people(email);
        CREATE INDEX IF NOT EXISTS idx_people_name ON people(first_name, last_name);

        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT,
            domain TEXT,
            description TEXT,
            source TEXT DEFAULT 'manual',
            created_at TEXT,
            updated_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain);
        CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
    """)
    conn.commit()


def seed_from_legacy_snapshot(conn: sqlite3.Connection, snapshot_path: Path | None = None) -> dict:
    path = snapshot_path or LEGACY_CONTACT_SNAPSHOT
    if not path.exists():
        return {"error": f"Snapshot not found: {path}"}

    data = json.loads(path.read_text())
    now = datetime.now(timezone.utc).isoformat()
    people_added = 0
    companies_added = 0

    for p in data.get("people", []):
        try:
            conn.execute(
                """INSERT OR IGNORE INTO people (id, first_name, last_name, email, job_title, company, linkedin, source, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'legacy_contact_seed', ?, ?)""",
                (p.get("id"), p.get("first_name"), p.get("last_name"),
                 p.get("email"), p.get("job_title"), p.get("company"),
                 p.get("linkedin"), now, now)
            )
            people_added += conn.total_changes
        except sqlite3.IntegrityError:
            pass

    for c in data.get("companies", []):
        try:
            conn.execute(
                """INSERT OR IGNORE INTO companies (id, name, domain, description, source, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 'legacy_contact_seed', ?, ?)""",
                (c.get("id"), c.get("name"), c.get("domain"),
                 c.get("description"), now, now)
            )
            companies_added += conn.total_changes
        except sqlite3.IntegrityError:
            pass

    conn.commit()

    total_people = conn.execute("SELECT count(*) FROM people").fetchone()[0]
    total_companies = conn.execute("SELECT count(*) FROM companies").fetchone()[0]

    return {
        "seeded_from": str(path),
        "people_in_snapshot": len(data.get("people", [])),
        "companies_in_snapshot": len(data.get("companies", [])),
        "total_people": total_people,
        "total_companies": total_companies,
    }


def add_person(conn: sqlite3.Connection, *, first_name: str, last_name: str = "",
               email: str = "", job_title: str = "", company: str = "",
               linkedin: str = "", source: str = "pipeline") -> str:
    import hashlib
    pid = "local_" + hashlib.sha256(
        f"{first_name}:{last_name}:{email}".encode()
    ).hexdigest()[:12]
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT OR REPLACE INTO people (id, first_name, last_name, email, job_title, company, linkedin, source, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (pid, first_name, last_name, email, job_title, company, linkedin, source, now, now)
    )
    conn.commit()
    return pid


def add_company(conn: sqlite3.Connection, *, name: str, domain: str = "",
                description: str = "", source: str = "pipeline") -> str:
    import hashlib
    cid = "local_" + hashlib.sha256(name.lower().encode()).hexdigest()[:12]
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT OR REPLACE INTO companies (id, name, domain, description, source, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (cid, name, domain, description, source, now, now)
    )
    conn.commit()
    return cid


def export_index(conn: sqlite3.Connection, output_path: Path | None = None) -> Path:
    out = output_path or INDEX_OUTPUT
    people = [dict(r) for r in conn.execute(
        "SELECT id, first_name, last_name, email, job_title, company, linkedin FROM people"
    ).fetchall()]
    companies = [dict(r) for r in conn.execute(
        "SELECT id, name, domain, description FROM companies"
    ).fetchall()]

    index = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "source": "local_contacts_store",
        "people": people,
        "companies": companies,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=2))
    return out


def stats(conn: sqlite3.Connection) -> dict:
    people_count = conn.execute("SELECT count(*) FROM people").fetchone()[0]
    companies_count = conn.execute("SELECT count(*) FROM companies").fetchone()[0]
    sources = {}
    for row in conn.execute("SELECT source, count(*) FROM people GROUP BY source"):
        sources[row[0]] = row[1]
    return {"people": people_count, "companies": companies_count, "people_by_source": sources}


def main():
    parser = argparse.ArgumentParser(description="Local contacts store")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("seed", help="Seed from local contact index")
    sub.add_parser("export", help="Export to resolver-compatible JSON index")
    sub.add_parser("stats", help="Show store stats")

    add_p = sub.add_parser("add-person", help="Add a person")
    add_p.add_argument("--first-name", required=True)
    add_p.add_argument("--last-name", default="")
    add_p.add_argument("--email", default="")
    add_p.add_argument("--company", default="")
    add_p.add_argument("--title", default="")
    add_p.add_argument("--source", default="manual")

    add_c = sub.add_parser("add-company", help="Add a company")
    add_c.add_argument("--name", required=True)
    add_c.add_argument("--domain", default="")
    add_c.add_argument("--source", default="manual")

    args = parser.parse_args()
    conn = get_db()

    if args.command == "seed":
        result = seed_from_legacy_snapshot(conn)
        print(json.dumps(result, indent=2))
    elif args.command == "export":
        out = export_index(conn)
        s = stats(conn)
        print(f"Exported {s['people']} people + {s['companies']} companies → {out}")
    elif args.command == "stats":
        print(json.dumps(stats(conn), indent=2))
    elif args.command == "add-person":
        pid = add_person(conn, first_name=args.first_name, last_name=args.last_name,
                         email=args.email, company=args.company, job_title=args.title,
                         source=args.source)
        print(f"Added: {pid}")
    elif args.command == "add-company":
        cid = add_company(conn, name=args.name, domain=args.domain, source=args.source)
        print(f"Added: {cid}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
