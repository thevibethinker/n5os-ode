#!/usr/bin/env python3
"""Todoist Bridge — unidirectional task sync for your operating system.

Read tasks from Todoist for briefings and analytics.
Create new tasks from commitments and meeting action items.
Never modifies or deletes existing Todoist tasks.
"""

import argparse
import json
import os
import random
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' package is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

API_BASE = "https://api.todoist.com/api/v1"
BRIDGE_LABEL = "n5os"
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0
DEFAULT_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "state", "sync_state.json"
)
AUTO_SYNC_THRESHOLD_MINUTES = 30


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

class TodoistAPIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(f"Todoist API error {status_code}: {message}")


class TodoistClient:
    """Minimal Todoist REST client with retry and rate-limit handling."""

    def __init__(self, token: str, dry_run: bool = False, verbose: bool = False):
        self.token = token
        self.dry_run = dry_run
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    def _request(self, method: str, path: str, **kwargs):
        url = f"{API_BASE}{path}"
        if self.verbose:
            print(f"  [{method}] {url}", file=sys.stderr)

        for attempt in range(MAX_RETRIES):
            try:
                resp = self.session.request(method, url, **kwargs)
            except requests.ConnectionError as e:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                    if self.verbose:
                        print(f"  Connection error, retrying in {wait:.1f}s...", file=sys.stderr)
                    time.sleep(wait)
                    continue
                raise TodoistAPIError(0, f"Connection failed: {e}")

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", RETRY_BASE_DELAY * (2 ** attempt)))
                wait = retry_after + random.uniform(0, 1)
                if self.verbose:
                    print(f"  Rate limited, waiting {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            if resp.status_code >= 400:
                try:
                    detail = resp.json()
                except Exception:
                    detail = resp.text
                raise TodoistAPIError(resp.status_code, str(detail))

            if resp.status_code == 204:
                return None
            return resp.json()

        raise TodoistAPIError(429, "Rate limit exceeded after retries")

    def get(self, path: str, params: dict = None):
        return self._request("GET", path, params=params)

    def post(self, path: str, data: dict = None, request_id: str = None):
        headers = {}
        if request_id:
            headers["X-Request-Id"] = request_id
        return self._request("POST", path, json=data, headers=headers)

    def get_tasks(self, project_id: str = None, filter_query: str = None):
        if filter_query:
            return self.get("/tasks/filter", params={"query": filter_query})
        params = {}
        if project_id:
            params["project_id"] = project_id
        return self.get("/tasks", params=params or None)

    def create_task(self, content: str, **kwargs) -> dict:
        payload = {"content": content}
        labels = list(kwargs.pop("labels", []))
        if BRIDGE_LABEL not in labels:
            labels.append(BRIDGE_LABEL)
        payload["labels"] = labels

        for key in ("description", "project_id", "section_id", "parent_id",
                     "priority", "due_string", "due_date", "due_datetime"):
            if key in kwargs and kwargs[key] is not None:
                payload[key] = kwargs[key]

        request_id = str(uuid.uuid4())
        return self.post("/tasks", data=payload, request_id=request_id), request_id

    def get_projects(self):
        return self.get("/projects")

    def get_completed_tasks(self, since: str = None, limit: int = 50):
        params = {"limit": limit}
        if since:
            params["since"] = since
        return self.get("/tasks/completed", params=params)

    def test_auth(self):
        """Test authentication by fetching projects. Returns True on success."""
        try:
            self.get("/projects")
            return True
        except TodoistAPIError:
            return False


# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------

def load_state(state_file: str) -> dict:
    path = Path(state_file)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {
        "version": "1.0",
        "last_sync_at": None,
        "sync_count": 0,
        "api_base": API_BASE,
        "projects": {},
        "tasks": {},
        "created_tasks": [],
    }


def save_state(state: dict, state_file: str):
    path = Path(state_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def state_is_stale(state: dict, threshold_minutes: int = AUTO_SYNC_THRESHOLD_MINUTES) -> bool:
    last_sync = state.get("last_sync_at")
    if not last_sync:
        return True
    try:
        last_dt = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) - last_dt > timedelta(minutes=threshold_minutes)
    except (ValueError, TypeError):
        return True


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_sync(client: TodoistClient, state: dict, args) -> dict:
    """Pull active tasks from Todoist into local cache."""
    if client.dry_run:
        print("[DRY RUN] Would sync tasks from Todoist")
        print(f"  Project filter: {args.project or 'all'}")
        print(f"  Filter query: {args.filter or 'none'}")
        print("  No API calls made.")
        return state

    project_id = None
    if args.project:
        projects = client.get_projects()
        for p in projects:
            if p["name"].lower() == args.project.lower():
                project_id = p["id"]
                break
        if not project_id:
            print(f"Error: Project '{args.project}' not found.", file=sys.stderr)
            available = [p["name"] for p in projects]
            print(f"  Available projects: {', '.join(available)}", file=sys.stderr)
            return state

    projects_data = client.get_projects()
    state["projects"] = {
        p["id"]: {"id": p["id"], "name": p["name"], "task_count": 0}
        for p in projects_data
    }

    tasks = client.get_tasks(project_id=project_id, filter_query=args.filter)
    if isinstance(tasks, dict) and "results" in tasks:
        tasks = tasks["results"]

    now_iso = datetime.now(timezone.utc).isoformat()
    old_task_ids = set(state["tasks"].keys())
    new_task_ids = set()

    for t in tasks:
        tid = str(t["id"])
        new_task_ids.add(tid)
        due_date = None
        if t.get("due"):
            due_date = t["due"].get("date")
        state["tasks"][tid] = {
            "id": tid,
            "content": t.get("content", ""),
            "project_id": str(t.get("project_id", "")),
            "priority": t.get("priority", 1),
            "due_date": due_date,
            "labels": t.get("labels", []),
            "is_completed": t.get("is_completed", False),
            "created_at": t.get("created_at", ""),
            "synced_at": now_iso,
        }

    removed = old_task_ids - new_task_ids
    for tid in removed:
        if not args.project and not args.filter:
            del state["tasks"][tid]

    for pid_data in state["projects"].values():
        pid_data["task_count"] = sum(
            1 for t in state["tasks"].values()
            if t["project_id"] == pid_data["id"]
        )

    state["last_sync_at"] = now_iso
    state["sync_count"] = state.get("sync_count", 0) + 1

    added = new_task_ids - old_task_ids
    print(f"Synced {len(tasks)} active tasks from Todoist.")
    if added:
        print(f"  New since last sync: {len(added)}")
    if removed and not args.project and not args.filter:
        print(f"  Removed (completed/deleted): {len(removed)}")
    print(f"  Projects: {len(state['projects'])}")
    print(f"  Total sync count: {state['sync_count']}")

    return state


def cmd_push(client: TodoistClient, state: dict, args) -> dict:
    """Create a new task in Todoist."""
    content = args.content
    if not content:
        print("Error: Task content is required.", file=sys.stderr)
        sys.exit(1)

    kwargs = {}
    if args.due:
        kwargs["due_string"] = args.due
    if args.priority:
        kwargs["priority"] = args.priority
    if args.description:
        kwargs["description"] = args.description

    extra_labels = []
    if args.label:
        extra_labels = args.label
    kwargs["labels"] = extra_labels

    if args.project:
        if client.dry_run:
            kwargs["_project_name"] = args.project
        else:
            projects = client.get_projects()
            found = None
            for p in projects:
                if p["name"].lower() == args.project.lower():
                    found = p["id"]
                    break
            if not found:
                print(f"Error: Project '{args.project}' not found.", file=sys.stderr)
                return state
            kwargs["project_id"] = found

    if args.section:
        if not client.dry_run:
            print("Warning: Section lookup requires project context. "
                  "Section will be set by name if the API supports it.", file=sys.stderr)

    source_ref = args.source or ""

    if client.dry_run:
        print("[DRY RUN] Would create task in Todoist:")
        print(f"  Content:     {content}")
        print(f"  Labels:      {[BRIDGE_LABEL] + extra_labels}")
        if args.due:
            print(f"  Due:         {args.due}")
        if args.priority:
            print(f"  Priority:    {args.priority}")
        if args.project:
            print(f"  Project:     {args.project}")
        if args.description:
            print(f"  Description: {args.description}")
        if source_ref:
            print(f"  Source:      {source_ref}")
        print("  No API call made.")
        return state

    result, request_id = client.create_task(content, **kwargs)

    state["created_tasks"].append({
        "todoist_id": str(result["id"]),
        "source": source_ref,
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
    })

    print(f"Task created successfully.")
    print(f"  ID:  {result['id']}")
    print(f"  URL: {result.get('url', 'N/A')}")
    if BRIDGE_LABEL in result.get("labels", []):
        print(f"  Label: @{BRIDGE_LABEL}")

    return state


def cmd_status(client: TodoistClient, state: dict, _args) -> dict:
    """Show bridge health and sync state."""
    print("=== Todoist Bridge Status ===\n")

    if client.dry_run:
        print("[DRY RUN] Skipping API connection test.")
        auth_ok = None
    else:
        try:
            auth_ok = client.test_auth()
        except Exception:
            auth_ok = False

    if auth_ok is True:
        print("API Connection: Connected")
    elif auth_ok is False:
        print("API Connection: FAILED — check TODOIST_API_TOKEN")
    else:
        print("API Connection: skipped (dry-run)")

    last_sync = state.get("last_sync_at", "Never")
    print(f"Last Sync:      {last_sync}")
    print(f"Sync Count:     {state.get('sync_count', 0)}")

    tasks = state.get("tasks", {})
    print(f"Cached Tasks:   {len(tasks)}")

    if tasks:
        by_project = {}
        for t in tasks.values():
            pid = t.get("project_id", "unknown")
            pname = state.get("projects", {}).get(pid, {}).get("name", pid)
            by_project.setdefault(pname, 0)
            by_project[pname] += 1
        for pname, count in sorted(by_project.items()):
            print(f"  {pname}: {count}")

    bridge_tasks = [t for t in tasks.values() if BRIDGE_LABEL in t.get("labels", [])]
    print(f"Bridge-created: {len(bridge_tasks)} (cached with @{BRIDGE_LABEL})")
    print(f"Push log:       {len(state.get('created_tasks', []))} tasks created total")

    return state


def cmd_briefing(client: TodoistClient, state: dict, args) -> dict:
    """Generate a daily task briefing."""
    if state_is_stale(state) and not client.dry_run:
        print("Auto-syncing (cache is stale)...\n")
        sync_args = argparse.Namespace(project=None, filter=None)
        state = cmd_sync(client, state, sync_args)
        print()

    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    fmt = args.format or "markdown"

    tasks = state.get("tasks", {})

    due_today = []
    overdue = []
    upcoming = []
    no_date = []

    for t in tasks.values():
        if t.get("is_completed"):
            continue
        due = t.get("due_date")
        if not due:
            no_date.append(t)
        elif due == target_date:
            due_today.append(t)
        elif due < target_date:
            overdue.append(t)
        elif due <= (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d"):
            upcoming.append(t)

    for group in (due_today, overdue, upcoming, no_date):
        group.sort(key=lambda t: t.get("priority", 1), reverse=True)

    projects = state.get("projects", {})

    def project_name(pid):
        return projects.get(pid, {}).get("name", "Unknown")

    def priority_label(p):
        return {4: "URGENT", 3: "High", 2: "Medium", 1: "Normal"}.get(p, "Normal")

    if fmt == "json":
        output = {
            "date": target_date,
            "overdue": [_task_summary(t) for t in overdue],
            "due_today": [_task_summary(t) for t in due_today],
            "upcoming": [_task_summary(t) for t in upcoming],
            "no_date": [_task_summary(t) for t in no_date],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"# Task Briefing — {target_date}\n")
        if overdue:
            print(f"## Overdue ({len(overdue)})\n")
            for t in overdue:
                print(f"- [{priority_label(t['priority'])}] {t['content']} "
                      f"(due {t['due_date']}, {project_name(t['project_id'])})")
            print()
        if due_today:
            print(f"## Due Today ({len(due_today)})\n")
            for t in due_today:
                print(f"- [{priority_label(t['priority'])}] {t['content']} "
                      f"({project_name(t['project_id'])})")
            print()
        if upcoming:
            print(f"## Upcoming ({len(upcoming)})\n")
            for t in upcoming:
                print(f"- [{priority_label(t['priority'])}] {t['content']} "
                      f"(due {t['due_date']}, {project_name(t['project_id'])})")
            print()
        if no_date:
            print(f"## No Due Date ({len(no_date)})\n")
            for t in no_date:
                print(f"- [{priority_label(t['priority'])}] {t['content']} "
                      f"({project_name(t['project_id'])})")
            print()
        total = len(overdue) + len(due_today) + len(upcoming) + len(no_date)
        print(f"**Total active:** {total} tasks")

    return state


def _task_summary(t: dict) -> dict:
    return {
        "id": t["id"],
        "content": t["content"],
        "priority": t.get("priority", 1),
        "due_date": t.get("due_date"),
        "project_id": t.get("project_id"),
        "labels": t.get("labels", []),
    }


def cmd_projects(client: TodoistClient, state: dict, args) -> dict:
    """List all Todoist projects."""
    if args.refresh and not client.dry_run:
        projects = client.get_projects()
        state["projects"] = {
            p["id"]: {"id": p["id"], "name": p["name"], "task_count": 0}
            for p in projects
        }
        for pid_data in state["projects"].values():
            pid_data["task_count"] = sum(
                1 for t in state.get("tasks", {}).values()
                if t["project_id"] == pid_data["id"]
            )
    elif client.dry_run:
        print("[DRY RUN] Would refresh projects from API.")

    projects = state.get("projects", {})
    if not projects:
        print("No projects cached. Run 'sync' or 'projects --refresh' first.")
        return state

    print("=== Todoist Projects ===\n")
    for p in sorted(projects.values(), key=lambda x: x["name"]):
        count = p.get("task_count", 0)
        print(f"  {p['name']}: {count} tasks (ID: {p['id']})")

    return state


def cmd_completed(client: TodoistClient, state: dict, args) -> dict:
    """Show recently completed tasks."""
    if client.dry_run:
        print("[DRY RUN] Would fetch completed tasks from API.")
        print(f"  Since: {args.since or 'yesterday'}")
        print(f"  Limit: {args.limit}")
        return state

    since = args.since
    if not since:
        since = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    elif "T" not in since:
        since = f"{since}T00:00:00Z"

    try:
        result = client.get_completed_tasks(since=since, limit=args.limit)
    except TodoistAPIError as e:
        print(f"Error fetching completed tasks: {e}", file=sys.stderr)
        return state

    items = result if isinstance(result, list) else result.get("items", result.get("results", []))

    if not items:
        print("No completed tasks found in the given range.")
        return state

    print(f"=== Completed Tasks (since {since[:10]}) ===\n")
    for item in items:
        content = item.get("content", item.get("task", {}).get("content", "Unknown"))
        completed_at = item.get("completed_at", "")
        print(f"  - {content} (completed: {completed_at[:10] if completed_at else 'N/A'})")

    print(f"\nTotal: {len(items)}")
    return state


# ---------------------------------------------------------------------------
# CLI Setup
# ---------------------------------------------------------------------------

def get_token() -> str:
    token = os.environ.get("TODOIST_API_TOKEN", "")
    return token


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todoist_bridge.py",
        description="Todoist Bridge — unidirectional task sync for your operating system. "
                    "Reads tasks for briefings, creates new tasks from commitments. "
                    "Never modifies or deletes existing Todoist tasks.",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen without making API calls")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable detailed logging")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE,
                        help=f"Path to sync state file (default: {DEFAULT_STATE_FILE})")

    subs = parser.add_subparsers(dest="command", help="Available commands")

    # Shared --dry-run on subcommands too (so `push "x" --dry-run` works)
    dry_run_parent = argparse.ArgumentParser(add_help=False)
    dry_run_parent.add_argument("--dry-run", action="store_true", dest="sub_dry_run",
                                help="Show what would happen without making API calls")

    # sync
    p_sync = subs.add_parser("sync", parents=[dry_run_parent],
                             help="Pull active tasks from Todoist into local cache")
    p_sync.add_argument("--project", help="Only sync tasks from this project name")
    p_sync.add_argument("--filter", help="Todoist filter query (e.g., 'today | overdue')")

    # push
    p_push = subs.add_parser("push", parents=[dry_run_parent],
                             help="Create a new task in Todoist")
    p_push.add_argument("content", help="Task title/content")
    p_push.add_argument("--due", help="Due date (natural language: 'tomorrow', 'next Monday')")
    p_push.add_argument("--priority", type=int, choices=[1, 2, 3, 4],
                        help="Priority: 1=normal, 2=medium, 3=high, 4=urgent")
    p_push.add_argument("--project", help="Target project name (default: Inbox)")
    p_push.add_argument("--section", help="Target section within project")
    p_push.add_argument("--description", help="Task description/notes")
    p_push.add_argument("--label", action="append", help="Additional label (repeatable). @n5os added automatically.")
    p_push.add_argument("--source", help="Source reference (e.g., 'meeting:2026-03-15', 'B02:commitment-3')")

    # status
    subs.add_parser("status", parents=[dry_run_parent],
                    help="Show bridge health and sync state")

    # briefing
    p_briefing = subs.add_parser("briefing", parents=[dry_run_parent],
                                 help="Generate a daily task briefing")
    p_briefing.add_argument("--date", help="Briefing date YYYY-MM-DD (default: today)")
    p_briefing.add_argument("--format", choices=["text", "json", "markdown"], default="markdown",
                            help="Output format (default: markdown)")

    # projects
    p_projects = subs.add_parser("projects", parents=[dry_run_parent],
                                 help="List Todoist projects")
    p_projects.add_argument("--refresh", action="store_true", help="Force refresh from API")

    # completed
    p_completed = subs.add_parser("completed", parents=[dry_run_parent],
                                  help="Show recently completed tasks")
    p_completed.add_argument("--since", help="Start date YYYY-MM-DD (default: yesterday)")
    p_completed.add_argument("--limit", type=int, default=50, help="Max tasks to show (default: 50)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    token = get_token()
    dry_run = args.dry_run or getattr(args, "sub_dry_run", False)

    if not token and not dry_run:
        print("Error: TODOIST_API_TOKEN environment variable is not set.", file=sys.stderr)
        print("  Get your token at: https://app.todoist.com/prefs/integrations", file=sys.stderr)
        print("  Then set it: export TODOIST_API_TOKEN='your-token-here'", file=sys.stderr)
        print("  Or use --dry-run to preview without API access.", file=sys.stderr)
        sys.exit(1)

    client = TodoistClient(token=token or "dry-run-placeholder", dry_run=dry_run, verbose=args.verbose)
    state = load_state(args.state_file)

    commands = {
        "sync": cmd_sync,
        "push": cmd_push,
        "status": cmd_status,
        "briefing": cmd_briefing,
        "projects": cmd_projects,
        "completed": cmd_completed,
    }

    handler = commands.get(args.command)
    if not handler:
        parser.print_help()
        sys.exit(1)

    try:
        state = handler(client, state, args)
        save_state(state, args.state_file)
    except TodoistAPIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
