#!/usr/bin/env python3
"""Careerspan founder tool: manage employer scan access (safe-by-default).

---
product: careerspan
created: 2026-01-20
last_edited: 2026-01-20
version: 1.0
requires_confirm: true
audit_log: N5/logs/careerspan_audit.jsonl
---

This script calls the Careerspan founder API endpoint:
  POST /etc/manage_employer_scan_access

It is intentionally safe-by-default:
- Always prints a dry-run preview (URL + payload)
- Refuses to call the API unless --confirm is provided
- Provides --dry-run mode that never calls the API
- Writes an append-only audit log entry for every run

Examples:

  # Dry run (no API call)
  python3 N5/scripts/manage_employer_scan_access.py test@example.com \
    --enable --credits 1 \
    --dry-run

  # Real run (API call)
  export FOUNDER_AUTH_TOKEN="..."
  python3 N5/scripts/manage_employer_scan_access.py test@example.com \
    --enable --credits 1 \
    --confirm

  # Enable org-restricted scanning (by org names/IDs)
  python3 N5/scripts/manage_employer_scan_access.py test@example.com \
    --org-scanning-enabled \
    --allowed-orgs "Acme Corp" "Beta Inc" \
    --dry-run

"""

import argparse
import datetime as _dt
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


BASE_URL_DEFAULT = "https://the-apply-ai--dossier-ai-all-main-fastapi-app.modal.run"
ENDPOINT_PATH = "/etc/manage_employer_scan_access"
TIMEOUT_SECONDS = 300  # 5 minutes
AUDIT_LOG_PATH_DEFAULT = "N5/logs/careerspan_audit.jsonl"


def _utc_timestamp() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _get_founder_token() -> str:
    token = os.getenv("FOUNDER_AUTH_TOKEN")
    if not token:
        print(
            "ERROR: FOUNDER_AUTH_TOKEN environment variable is not set.\n"
            "Set it to your founder auth token before running this script.\n"
            "(Zo: Settings → Developers → Secrets)",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def _append_audit_log(entry: Dict[str, Any], audit_log_path: str) -> None:
    abs_path = os.path.join("/home/workspace", audit_log_path) if not os.path.isabs(audit_log_path) else audit_log_path
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage employer scan access via Careerspan founder API (safe-by-default).",
    )

    parser.add_argument(
        "email",
        help="Employer email to configure",
    )

    scan_group = parser.add_mutually_exclusive_group(required=False)
    scan_group.add_argument(
        "--enable",
        action="store_true",
        help="Enable scanning for the employer (scanning_enabled=true).",
    )
    scan_group.add_argument(
        "--disable",
        action="store_true",
        help="Disable scanning for the employer (scanning_enabled=false).",
    )

    parser.add_argument(
        "--credits",
        type=int,
        help="Credits to add (credits_to_add). Must be >= 0.",
    )

    org_group = parser.add_mutually_exclusive_group(required=False)
    org_group.add_argument(
        "--org-scanning-enabled",
        action="store_true",
        help="Enable org-restricted scanning (org_scanning_enabled=true).",
    )
    org_group.add_argument(
        "--org-scanning-disabled",
        action="store_true",
        help="Disable org-restricted scanning (org_scanning_enabled=false).",
    )

    parser.add_argument(
        "--allowed-orgs",
        nargs="+",
        help=(
            "Allowed organizations list (allowed_organizations). "
            "Provide one or more org IDs OR org names."
        ),
    )

    parser.add_argument(
        "--base-url",
        default=BASE_URL_DEFAULT,
        help=f"API base URL (default: {BASE_URL_DEFAULT})",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Never call the API. Still prints preview and writes audit log.",
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required to execute the API call (mutations).",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON (includes response + audit path).",
    )

    args = parser.parse_args()

    # Validation: at least one operation
    has_any_action = any(
        [
            args.enable,
            args.disable,
            args.credits is not None,
            args.org_scanning_enabled,
            args.org_scanning_disabled,
            args.allowed_orgs is not None,
        ]
    )
    if not has_any_action:
        parser.error(
            "You must specify at least one operation: "
            "--enable/--disable/--credits/--org-scanning-enabled/--org-scanning-disabled/--allowed-orgs"
        )

    if args.credits is not None and args.credits < 0:
        parser.error("--credits must be >= 0")

    if args.allowed_orgs is not None and not args.org_scanning_enabled:
        print(
            "WARNING: You provided --allowed-orgs but did not pass --org-scanning-enabled.\n"
            "This may be intentional (API may accept it), but usually you want both.",
            file=sys.stderr,
        )

    return args


def _build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"employer_email": args.email}

    if args.enable:
        payload["scanning_enabled"] = True
    elif args.disable:
        payload["scanning_enabled"] = False

    if args.credits is not None:
        payload["credits_to_add"] = args.credits

    if args.org_scanning_enabled:
        payload["org_scanning_enabled"] = True
    elif args.org_scanning_disabled:
        payload["org_scanning_enabled"] = False

    if args.allowed_orgs is not None:
        payload["allowed_organizations"] = args.allowed_orgs

    return payload


def _print_preview(url: str, payload: Dict[str, Any]) -> None:
    print("═" * 72)
    print("DRY RUN PREVIEW (no request sent yet)")
    print("URL:", url)
    print("Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("═" * 72)


def _call_api(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    token = _get_founder_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        err_body = ""
        detail: Any = None
        try:
            err_body = exc.read().decode("utf-8")
            err_data = json.loads(err_body)
            detail = err_data.get("detail", err_data)
        except Exception:
            detail = err_body or str(exc)

        if exc.code in (401, 403):
            raise RuntimeError(
                f"Authentication failed (HTTP {exc.code}). Detail: {detail}. "
                "Check that FOUNDER_AUTH_TOKEN is set correctly."
            )
        if exc.code == 404:
            raise RuntimeError(
                f"Employer not found (HTTP 404). Detail: {detail}. "
                f"Email '{payload.get('employer_email')}' may not exist as an employer."
            )
        if exc.code == 400:
            raise RuntimeError(f"Bad request (HTTP 400). Detail: {detail}.")

        raise RuntimeError(f"API error (HTTP {exc.code}). Detail: {detail}.")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc.reason}")


def _print_success_summary(response: Dict[str, Any], audit_log_path: str) -> None:
    employer_id = response.get("employer_id")
    scanning_enabled = response.get("scanning_enabled")

    prev_credits = response.get("previous_credits")
    new_credits = response.get("new_balance")
    credits_added = response.get("credits_added")

    org_scanning_enabled = response.get("org_scanning_enabled")
    allowed_orgs = response.get("allowed_organizations") or []

    print("Scan access updated successfully.")
    print(f"Employer ID: {employer_id}")
    print(f"Scanning enabled: {scanning_enabled}")

    if prev_credits is not None or new_credits is not None or credits_added is not None:
        print(f"Credits: {prev_credits} → {new_credits} (+{credits_added} added)")

    print(f"Org scanning enabled: {org_scanning_enabled}")
    print(f"Allowed organizations: {len(allowed_orgs)}")
    print(f"Audit logged to: {audit_log_path}")


def main() -> None:
    args = _parse_args()

    url = args.base_url.rstrip("/") + ENDPOINT_PATH
    payload = _build_payload(args)

    # Always show the preview first.
    _print_preview(url, payload)

    audit_entry: Dict[str, Any] = {
        "timestamp": _utc_timestamp(),
        "operation": "manage_employer_scan_access",
        "employer_email": args.email,
        "payload": payload,
        "dry_run": bool(args.dry_run),
    }

    audit_path = AUDIT_LOG_PATH_DEFAULT

    if args.dry_run:
        audit_entry.update(
            {
                "result": "success",
                "http_status": None,
                "response": None,
            }
        )
        _append_audit_log(audit_entry, audit_path)

        if args.json:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "url": url,
                        "payload": payload,
                        "audit_log_path": audit_path,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
        else:
            print("[DRY RUN] No request was sent.")
            print(f"Audit logged to: {audit_path}")
        return

    if not args.confirm:
        msg = (
            "REFUSING TO EXECUTE: This operation would mutate production state.\n"
            "Re-run with --confirm to actually call the API, or use --dry-run."
        )
        print(f"ERROR: {msg}", file=sys.stderr)
        audit_entry.update(
            {
                "dry_run": True,
                "result": "error",
                "error": "requires_confirm",
                "message": msg,
                "http_status": None,
                "response": None,
            }
        )
        _append_audit_log(audit_entry, audit_path)
        sys.exit(2)

    try:
        response = _call_api(url, payload)
        audit_entry.update(
            {
                "result": "success",
                "http_status": 200,
                "response": response,
            }
        )
        _append_audit_log(audit_entry, audit_path)

        if args.json:
            print(
                json.dumps(
                    {
                        "success": True,
                        "response": response,
                        "audit_log_path": audit_path,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
        else:
            _print_success_summary(response, audit_path)

    except Exception as exc:
        # Ensure we audit errors too.
        audit_entry.update(
            {
                "result": "error",
                "http_status": None,
                "error": str(exc),
            }
        )
        _append_audit_log(audit_entry, audit_path)
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
