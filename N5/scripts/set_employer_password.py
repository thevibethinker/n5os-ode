#!/usr/bin/env python3
"""One-off employer password setup tool.

---
product: careerspan
version: 1.1
created: 2025-10-10
updated: 2026-01-20
requires_confirm: true
supports_dry_run: true
audit_log: N5/logs/careerspan_audit.jsonl
---

Usage examples:

  # Generate a random password and DO NOT call the API (dry run)
  FOUNDER_AUTH_TOKEN=dummy \
  python3 N5/scripts/set_employer_password.py davis@teamworkonline.com \
    --generate-password \
    --dry-run

  # Real run (token must be set in env)
  export FOUNDER_AUTH_TOKEN="..."
  python3 N5/scripts/set_employer_password.py davis@teamworkonline.com --password "SomePass123"

This script uses only the Python standard library (no requests needed).
"""

import argparse
import json
import os
import secrets
import string
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


BASE_URL_DEFAULT = "https://the-apply-ai--dossier-ai-all-main-fastapi-app.modal.run"
ENDPOINT_PATH = "/etc/set-employer-password"
TIMEOUT_SECONDS = 300  # 5 minutes, per API docs

AUDIT_LOG_PATH = Path("/home/workspace/N5/logs/careerspan_audit.jsonl")


def write_audit_log(
    operation: str,
    employer_email: str,
    payload: dict,
    dry_run: bool,
    result: str,
    http_status: Optional[int] = None,
    response: Optional[dict] = None,
    error_detail: Optional[str] = None,
) -> None:
    """Append an audit entry to the JSONL log."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "employer_email": employer_email,
        "payload": {k: v for k, v in payload.items() if k != "new_password"},  # Never log passwords
        "payload_has_password": "new_password" in payload,
        "dry_run": dry_run,
        "result": result,
    }
    
    if http_status is not None:
        entry["http_status"] = http_status
    if response is not None:
        entry["response"] = response
    if error_detail is not None:
        entry["error_detail"] = error_detail
    
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def generate_password(length: int = 20) -> str:
    """Generate a random password of given length (<= 30 chars)."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set initial password for an employer via the set-employer-password API.",
    )
    parser.add_argument(
        "email",
        help="Employer email to configure",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--password",
        help="Password to set (1-30 characters). If omitted, you must pass --generate-password.",
    )
    group.add_argument(
        "--generate-password",
        action="store_true",
        help="Generate a random password instead of supplying one explicitly.",
    )
    parser.add_argument(
        "--no-default-role",
        action="store_true",
        help="Do NOT provision the default lead/role (provision_default_role=false).",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL_DEFAULT,
        help=f"Base URL for the API (default: {BASE_URL_DEFAULT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be sent but do not call the remote API.",
    )

    args = parser.parse_args()

    if not args.password and not args.generate_password:
        parser.error("You must specify either --password or --generate-password.")

    return args


def get_founder_token() -> str:
    token = os.getenv("FOUNDER_AUTH_TOKEN")
    if not token:
        print(
            "ERROR: FOUNDER_AUTH_TOKEN environment variable is not set.\n"
            "Set it to your founder auth token before running this script.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def set_employer_password(
    email: str,
    password: str,
    provision_default_role: bool,
    base_url: str,
    dry_run: bool = False,
) -> Optional[dict]:
    url = base_url.rstrip("/") + ENDPOINT_PATH
    payload = {
        "employer_email": email,
        "new_password": password,
        "provision_default_role": provision_default_role,
    }

    if dry_run:
        print("[DRY RUN] Would POST to:", url)
        print("[DRY RUN] Payload:")
        print(json.dumps({k: v for k, v in payload.items() if k != "new_password"}, indent=2))
        print("[DRY RUN] (password redacted from display)")
        
        write_audit_log(
            operation="set_employer_password",
            employer_email=email,
            payload=payload,
            dry_run=True,
            result="dry_run",
        )
        return None

    token = get_founder_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
            response_data = json.loads(body)
            
            write_audit_log(
                operation="set_employer_password",
                employer_email=email,
                payload=payload,
                dry_run=False,
                result="success",
                http_status=resp.status,
                response=response_data,
            )
            return response_data
            
    except urllib.error.HTTPError as exc:
        # Read error body for details
        try:
            err_body = exc.read().decode("utf-8")
            err_data = json.loads(err_body)
            detail = err_data.get("detail", str(err_data))
        except Exception:
            detail = err_body if err_body else str(exc)
        
        write_audit_log(
            operation="set_employer_password",
            employer_email=email,
            payload=payload,
            dry_run=False,
            result="error",
            http_status=exc.code,
            error_detail=detail,
        )
        
        # Provide helpful context for common errors
        if exc.code == 401 or exc.code == 403:
            print(
                f"ERROR: Authentication failed (HTTP {exc.code}).\n"
                f"Detail: {detail}\n"
                f"Check that FOUNDER_AUTH_TOKEN is set correctly in Zo Settings → Developers → Secrets.",
                file=sys.stderr,
            )
        elif exc.code == 404:
            print(
                f"ERROR: User not found (HTTP 404).\n"
                f"Detail: {detail}\n"
                f"The email '{email}' does not exist as an employer in the system.",
                file=sys.stderr,
            )
        elif exc.code == 409:
            print(
                f"ERROR: Conflict (HTTP 409).\n"
                f"Detail: {detail}\n"
                f"This employer already has authentication configured. "
                f"This endpoint is only for FIRST-TIME password setup.",
                file=sys.stderr,
            )
        elif exc.code == 400:
            print(
                f"ERROR: Bad request (HTTP 400).\n"
                f"Detail: {detail}\n"
                f"Common causes: password too long (>30 chars), empty password, or user is not an employer.",
                file=sys.stderr,
            )
        else:
            print(
                f"ERROR: API returned status {exc.code}: {detail}",
                file=sys.stderr,
            )
        sys.exit(1)
        
    except urllib.error.URLError as exc:
        write_audit_log(
            operation="set_employer_password",
            employer_email=email,
            payload=payload,
            dry_run=False,
            result="error",
            error_detail=f"URLError: {exc.reason}",
        )
        print(f"ERROR: Request to {url} failed: {exc.reason}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as exc:
        write_audit_log(
            operation="set_employer_password",
            employer_email=email,
            payload=payload,
            dry_run=False,
            result="error",
            error_detail=f"Unexpected: {str(exc)}",
        )
        print(f"ERROR: Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    args = parse_args()

    if args.generate_password:
        password = generate_password()
    else:
        password = args.password or ""

    if not (1 <= len(password) <= 30):
        print(
            f"ERROR: Password length must be between 1 and 30 characters; got {len(password)}.",
            file=sys.stderr,
        )
        sys.exit(1)

    provision_default_role = not args.no_default_role

    result = set_employer_password(
        email=args.email,
        password=password,
        provision_default_role=provision_default_role,
        base_url=args.base_url,
        dry_run=args.dry_run,
    )

    # Summarise for the operator
    if args.generate_password:
        print(f"Generated password: {password}")

    if result is None:
        # Dry run
        print("[DRY RUN] No request was sent.")
        return

    print("Password set successfully.")
    print(f"Employer ID: {result.get('employer_id')}")
    print(f"Lead provisioned: {result.get('lead_provisioned')}")
    print(f"New lead ID: {result.get('new_lead_id')}")


if __name__ == "__main__":
    main()
