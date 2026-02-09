"""SourceStack monitoring CLI.
"""
import argparse
import json
import logging
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
WATCHLIST_PATH = SCRIPT_DIR.parent / "assets" / "watchlist.yaml"
DB_PATH = SCRIPT_DIR.parent / "data" / "sourcestack.db"
API_BASE = "https://sourcestack-api.com"
LOG = logging.getLogger("sourcestack")
JOB_FIELDS = [
    "post_uuid",
    "job_name",
    "company_name",
    "company_url",
    "post_url",
    "post_apply_url",
    "post_full_text",
    "department",
    "seniority",
    "remote",
    "comp_range",
    "city",
    "country",
    "first_indexed",
    "last_indexed",
    "job_created_at",
    "job_published_at",
]


@dataclass
class JobRecord:
    post_uuid: str
    job_name: str
    company_name: str
    company_url: str
    post_url: Optional[str]
    post_apply_url: Optional[str]
    post_full_text: Optional[str]
    first_indexed: Optional[str]
    last_indexed: Optional[str]
    job_created_at: Optional[str]
    job_published_at: Optional[str]
    department: Optional[str]
    seniority: Optional[str]
    remote: Optional[bool]
    comp_range: Optional[str]
    city: Optional[str]
    country: Optional[str]


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    LOG.addHandler(handler)
    LOG.setLevel(logging.INFO)


def get_api_key() -> str:
    key = os.environ.get("SOURCESTACK_API_KEY")
    if not key:
        LOG.error("SOURCESTACK_API_KEY environment variable is missing.")
        sys.exit(1)
    return key


def ensure_paths() -> None:
    WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def connect_db() -> sqlite3.Connection:
    ensure_paths()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            post_uuid TEXT PRIMARY KEY,
            job_name TEXT,
            company_name TEXT,
            company_url TEXT,
            post_url TEXT,
            post_apply_url TEXT,
            post_full_text TEXT,
            department TEXT,
            seniority TEXT,
            remote BOOLEAN,
            comp_range TEXT,
            city TEXT,
            country TEXT,
            first_indexed TEXT,
            last_indexed TEXT,
            job_created_at TEXT,
            job_published_at TEXT,
            first_seen TEXT,
            last_seen TEXT,
            status TEXT DEFAULT 'active',
            scan_id TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            scan_type TEXT,
            timestamp TEXT,
            credits_used INTEGER,
            jobs_found INTEGER,
            jobs_new INTEGER,
            query_config TEXT
        )
        """
    )
    conn.commit()


def load_watchlist() -> Dict[str, Any]:
    if not WATCHLIST_PATH.exists():
        LOG.warning("Watchlist not found at %s. Using empty defaults.", WATCHLIST_PATH)
        return {"companies": [], "roles": [], "filters": {}}
    with WATCHLIST_PATH.open() as fh:
        data = yaml.safe_load(fh) or {}
    return {
        "companies": data.get("companies", []),
        "roles": data.get("roles", []),
        "filters": data.get("filters", {}),
    }


def save_watchlist(data: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        LOG.info("Dry-run enabled; not saving watchlist.")
        return
    with WATCHLIST_PATH.open("w") as fh:
        yaml.safe_dump(data, fh)
    LOG.info("Updated watchlist saved to %s.", WATCHLIST_PATH)


def post_to_api(path: str, payload: Dict[str, Any], api_key: str) -> Tuple[Dict[str, Any], Optional[int]]:
    url = f"{API_BASE}/{path.lstrip('/')}"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    LOG.debug("POST %s %s", url, payload)
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        LOG.error("API request failed (%s): %s", response.status_code, response.text)
        raise
    credits = response.headers.get("X-SOURCESTACK-CREDITS-REMAINING")
    if credits is not None:
        LOG.info("Credits remaining: %s", credits)
        credits_value: Optional[int]
        try:
            credits_value = int(credits)
        except ValueError:
            credits_value = None
    else:
        credits_value = None
    return response.json(), credits_value


def get_quota(api_key: str) -> Dict[str, Any]:
    url = f"{API_BASE}/quota"
    headers = {"X-API-KEY": api_key}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


def build_filters(watchlist: Dict[str, Any]) -> List[Dict[str, Any]]:
    filters = [
        {"field": "last_indexed", "operator": "GREATER_THAN", "value": "LAST_1D"}
    ]
    companies = [entry.get("url") for entry in watchlist.get("companies", []) if entry.get("url")]
    if companies:
        filters.append({"field": "company_url", "operator": "IN", "value": companies})
    roles = [role for role in watchlist.get("roles", []) if role]
    if roles:
        filters.append({"field": "job_name", "operator": "CONTAINS_ANY", "value": roles})
    filters_config = watchlist.get("filters", {})
    countries = filters_config.get("countries") or []
    if countries:
        filters.append({"field": "country", "operator": "IN", "value": countries})
    seniority = filters_config.get("seniority") or []
    if seniority:
        filters.append({"field": "seniority", "operator": "IN", "value": seniority})
    if filters_config.get("remote_only"):
        filters.append({"field": "remote", "operator": "EQUALS", "value": True})
    return filters


def normalize_job(job: Dict[str, Any]) -> JobRecord:
    return JobRecord(
        post_uuid=job.get("post_uuid"),
        job_name=job.get("job_name"),
        company_name=job.get("company_name"),
        company_url=job.get("company_url"),
        post_url=job.get("post_url"),
        post_apply_url=job.get("post_apply_url"),
        post_full_text=job.get("post_full_text"),
        first_indexed=job.get("first_indexed"),
        last_indexed=job.get("last_indexed"),
        job_created_at=job.get("job_created_at"),
        job_published_at=job.get("job_published_at"),
        department=job.get("department"),
        seniority=job.get("seniority"),
        remote=job.get("remote"),
        comp_range=job.get("comp_range"),
        city=job.get("city"),
        country=job.get("country"),
    )


def persist_jobs(
    conn: sqlite3.Connection,
    jobs: Iterable[JobRecord],
    scan_id: str,
    dry_run: bool,
) -> Dict[str, int]:
    stats = {"found": 0, "new": 0}
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    for job in jobs:
        if not job.post_uuid:
            continue
        stats["found"] += 1
        cursor.execute("SELECT post_uuid FROM jobs WHERE post_uuid = ?", (job.post_uuid,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                """
                UPDATE jobs
                SET last_seen = ?, status = 'active', scan_id = ?
                WHERE post_uuid = ?
                """,
                (now, scan_id, job.post_uuid),
            )
        else:
            stats["new"] += 1
            if not dry_run:
                cursor.execute(
                    """
                    INSERT INTO jobs(
                        post_uuid, job_name, company_name, company_url, post_url, post_apply_url,
                        post_full_text, department, seniority, remote, comp_range, city, country,
                        first_indexed, last_indexed, job_created_at, job_published_at,
                        first_seen, last_seen, scan_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job.post_uuid,
                        job.job_name,
                        job.company_name,
                        job.company_url,
                        job.post_url,
                        job.post_apply_url,
                        job.post_full_text,
                        job.department,
                        job.seniority,
                        job.remote,
                        job.comp_range,
                        job.city,
                        job.country,
                        job.first_indexed,
                        job.last_indexed,
                        job.job_created_at,
                        job.job_published_at,
                        now,
                        now,
                        scan_id,
                    ),
                )
    if not dry_run:
        conn.commit()
    return stats


def scan_watchlist(args: argparse.Namespace) -> None:
    api_key = get_api_key()
    watchlist = load_watchlist()
    filters = build_filters(watchlist)
    payload = {
        "filters": filters,
        "fields": JOB_FIELDS,
        "limit": 2000,
    }
    scan_id = f"scan-{datetime.utcnow().isoformat()}"
    LOG.info("Starting daily scan (%s).", scan_id)
    if args.dry_run:
        LOG.info("Dry-run: query will not persist results.")
    response_data, credits = post_to_api("jobs", payload, api_key)
    jobs_data = response_data.get("data") or response_data.get("results") or []
    job_records = [normalize_job(job) for job in jobs_data]
    conn = connect_db()
    stats = persist_jobs(conn, job_records, scan_id, args.dry_run)
    if not args.dry_run:
        record_scan(conn, scan_id, "daily", stats["found"], stats["new"], payload, credits)
    LOG.info("Scan complete. Found %s jobs (%s new).", stats["found"], stats["new"])


def record_scan(
    conn: sqlite3.Connection,
    scan_id: str,
    scan_type: str,
    found: int,
    new: int,
    query: Dict[str, Any],
    credits_used: Optional[int],
) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scans(scan_id, scan_type, timestamp, credits_used, jobs_found, jobs_new, query_config)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            scan_id,
            scan_type,
            datetime.utcnow().isoformat(),
            credits_used,
            found,
            new,
            json.dumps(query),
        ),
    )
    conn.commit()


def adhoc_search(args: argparse.Namespace) -> None:
    api_key = get_api_key()
    filters: List[Dict[str, Any]] = []
    if args.company_url:
        filters.append({"field": "company_url", "operator": "EQUALS", "value": args.company_url})
    if args.role:
        filters.append({"field": "job_name", "operator": "CONTAINS_ANY", "value": args.role.split(',')})
    if args.country:
        filters.append({"field": "country", "operator": "EQUALS", "value": args.country})
    payload = {
        "filters": filters,
        "fields": JOB_FIELDS,
        "limit": args.limit,
    }
    LOG.info("Running ad hoc search: %s", args)
    response_data, _ = post_to_api("jobs", payload, get_api_key())
    jobs = response_data.get("data") or response_data.get("results") or []
    for job in jobs:
        LOG.info("%s | %s | %s", job.get("company_name"), job.get("job_name"), job.get("post_url"))


def query_local_db(args: argparse.Namespace) -> None:
    conn = connect_db()
    sql = "SELECT post_uuid, company_name, job_name, post_url, status, last_seen FROM jobs"
    clauses: List[str] = []
    params: List[Any] = []
    if args.company:
        clauses.append("company_name LIKE ?")
        params.append(f"%{args.company}%")
    if args.status:
        clauses.append("status = ?")
        params.append(args.status)
    if args.text:
        clauses.append("post_full_text LIKE ?")
        params.append(f"%{args.text}%")
    if args.since_days:
        cutoff = (datetime.utcnow() - timedelta(days=args.since_days)).isoformat()
        clauses.append("last_seen >= ?")
        params.append(cutoff)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY last_seen DESC LIMIT ?"
    params.append(args.limit)
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    LOG.info("%s rows returned.", len(rows))
    for row in rows:
        LOG.info(
            "%s | %s | %s | %s | %s",
            row["company_name"],
            row["job_name"],
            row["post_url"],
            row["status"],
            row["last_seen"],
        )


def report_watchlist(args: argparse.Namespace) -> None:
    data = load_watchlist()
    if not args.add_company and not args.remove_company and not args.add_role and not args.remove_role:
        LOG.info(
            "Current watchlist:\nCompanies: %s\nRoles: %s\nFilters: %s",
            data["companies"],
            data["roles"],
            data["filters"],
        )
        return
    companies = data["companies"]
    roles = data["roles"]
    if args.add_company:
        url, label = args.add_company.split(":", 1) if ":" in args.add_company else (args.add_company, args.add_company)
        if not any(entry.get("url") == url for entry in companies):
            companies.append({"url": url, "label": label})
    if args.remove_company:
        companies = [entry for entry in companies if entry.get("url") != args.remove_company]
    if args.add_role and args.add_role not in roles:
        roles.append(args.add_role)
    if args.remove_role:
        roles = [role for role in roles if role != args.remove_role]
    data["companies"] = companies
    data["roles"] = roles
    save_watchlist(data, args.dry_run)


def delta_report(args: argparse.Namespace) -> None:
    conn = connect_db()
    cutoff = datetime.utcnow() - timedelta(days=args.since_days)
    cursor = conn.execute(
        "SELECT post_uuid, company_name, job_name, post_url, status FROM jobs WHERE last_seen >= ? ORDER BY last_seen DESC",
        (cutoff.isoformat(),),
    )
    rows = cursor.fetchall()
    LOG.info("%s jobs changed in the last %s days", len(rows), args.since_days)
    for row in rows:
        LOG.info("%s | %s | %s | %s", row["company_name"], row["job_name"], row["status"], row["post_url"])


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="SourceStack monitoring CLI")
    parser.add_argument("--dry-run", action="store_true", help="skip stateful writes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Run the automated watchlist scan")
    scan_parser.set_defaults(func=scan_watchlist)

    search_parser = subparsers.add_parser("search", help="Run an ad hoc SourceStack search")
    search_parser.add_argument("--company-url", help="company URL to filter")
    search_parser.add_argument("--role", help="role/title to filter (comma separated)")
    search_parser.add_argument("--country", help="country name")
    search_parser.add_argument("--limit", type=int, default=25)
    search_parser.set_defaults(func=adhoc_search)

    query_parser = subparsers.add_parser("query", help="Query the local SQLite cache")
    query_parser.add_argument("--company", help="partial company name")
    query_parser.add_argument("--text", help="search in job description text")
    query_parser.add_argument("--status", choices=["active", "disappeared"], help="job status")
    query_parser.add_argument("--since-days", type=int, default=7)
    query_parser.add_argument("--limit", type=int, default=25)
    query_parser.set_defaults(func=query_local_db)

    watch_parser = subparsers.add_parser("watchlist", help="Inspect or edit the watchlist")
    watch_parser.add_argument("--add-company", help="Add company in format url:Label")
    watch_parser.add_argument("--remove-company", help="Remove company by URL")
    watch_parser.add_argument("--add-role", help="Add role keyword")
    watch_parser.add_argument("--remove-role", help="Remove role keyword")
    watch_parser.set_defaults(func=report_watchlist)

    subparsers.add_parser("quota", help="Check SourceStack credit quota").set_defaults(func=lambda args: print(get_quota(get_api_key())))

    delta_parser = subparsers.add_parser("delta", help="Show recent job changes")
    delta_parser.add_argument("--since-days", type=int, default=1)
    delta_parser.set_defaults(func=delta_report)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        LOG.error("Failed to execute %s: %s", args.command, exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
