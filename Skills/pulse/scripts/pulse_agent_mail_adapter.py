#!/usr/bin/env python3
"""
Optional Pulse adapter for upstream MCP Agent Mail.

This adapter is intentionally optional: Pulse must keep working when the
upstream package is not installed. For isolated evaluations, the adapter can
re-exec itself inside a build-local upstream venv at:

N5/builds/<slug>/upstream/mcp_agent_mail/.venv/bin/python
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from pulse_common import PATHS


RUNTIME_DIRNAME = "pulse-agent-mail"


def sanitize_thread_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value)
    cleaned = cleaned.strip("-._") or "pulse"
    if not cleaned[0].isalnum():
        cleaned = f"pulse-{cleaned}"
    return cleaned[:128]


def to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [to_jsonable(item) for item in value]
    if hasattr(value, "model_dump"):
        return to_jsonable(value.model_dump(mode="json"))
    if hasattr(value, "dict"):
        return to_jsonable(value.dict())
    if hasattr(value, "__dict__"):
        return to_jsonable(vars(value))
    return str(value)


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: redact_sensitive(item)
            for key, item in value.items()
            if key not in {"registration_token", "token", "secret", "api_key"}
        }
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


def tool_data(result: Any) -> Any:
    return redact_sensitive(to_jsonable(getattr(result, "data", result)))


def build_dir(slug: str) -> Path:
    return PATHS.build(slug)


def build_venv_python(slug: str) -> Path:
    return build_dir(slug) / "upstream" / "mcp_agent_mail" / ".venv" / "bin" / "python"


def maybe_reexec_in_build_venv(slug: str) -> None:
    if os.environ.get("PULSE_AGENT_MAIL_NO_REEXEC") == "1":
        return
    venv_python = build_venv_python(slug)
    if not venv_python.exists() or Path(sys.executable).resolve() == venv_python.resolve():
        return
    env = os.environ.copy()
    env["PULSE_AGENT_MAIL_NO_REEXEC"] = "1"
    result = subprocess.run([str(venv_python), __file__, *sys.argv[1:]], env=env)
    raise SystemExit(result.returncode)


def import_agent_mail() -> tuple[bool, str | None]:
    try:
        global Client, build_mcp_server, clear_settings_cache, reset_database_state, clear_repo_cache
        from fastmcp import Client
        from mcp_agent_mail.app import build_mcp_server
        from mcp_agent_mail.config import clear_settings_cache
        from mcp_agent_mail.db import reset_database_state
        from mcp_agent_mail.storage import clear_repo_cache
        return True, None
    except Exception as exc:
        return False, str(exc)


def package_version() -> str | None:
    for name in ("mcp-agent-mail", "mcp_agent_mail"):
        try:
            return version(name)
        except PackageNotFoundError:
            continue
    return None


def runtime_root(slug: str, reset: bool) -> Path:
    root = build_dir(slug) / "artifacts" / RUNTIME_DIRNAME / "runtime"
    if reset and root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def configure_runtime(slug: str, reset: bool) -> Path:
    root = runtime_root(slug, reset=reset)
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{root / 'agent-mail.sqlite3'}"
    os.environ["STORAGE_ROOT"] = str(root / "storage")
    os.environ["APP_ENVIRONMENT"] = "pulse-agent-mail-adapter"
    os.environ["HTTP_HOST"] = "127.0.0.1"
    os.environ["HTTP_PORT"] = "8773"
    os.environ.setdefault("GIT_AUTHOR_NAME", "pulse-agent-mail-adapter")
    os.environ.setdefault("GIT_AUTHOR_EMAIL", "pulse-agent-mail-adapter@example.invalid")
    clear_settings_cache()
    reset_database_state()
    clear_repo_cache()
    return root


async def call_tool(client: Any, name: str, payload: dict[str, Any]) -> Any:
    result = await client.call_tool(name, payload)
    return tool_data(result)


async def smoke_async(slug: str) -> dict[str, Any]:
    root = configure_runtime(slug, reset=True)
    server = build_mcp_server()
    project_key = str(PATHS.WORKSPACE.resolve())
    target_path = f"N5/builds/{slug}/PLAN.md"
    async with Client(server) as client:
        project = await call_tool(client, "ensure_project", {"human_key": project_key})
        alpha = await call_tool(
            client,
            "register_agent",
            {
                "project_key": project_key,
                "program": "zo-pulse",
                "model": "gpt-5.5",
                "name": "pulse-alpha",
                "task_description": "Pulse Agent Mail adapter smoke sender",
            },
        )
        beta = await call_tool(
            client,
            "register_agent",
            {
                "project_key": project_key,
                "program": "zo-pulse",
                "model": "gpt-5.5",
                "name": "pulse-beta",
                "task_description": "Pulse Agent Mail adapter smoke receiver",
            },
        )
        message = await call_tool(
            client,
            "send_message",
            {
                "project_key": project_key,
                "sender_name": "pulse-alpha",
                "to": ["pulse-beta"],
                "subject": f"Pulse handoff for {slug}",
                "body_md": "Adapter smoke: message handoff works through upstream MCP Agent Mail.",
                "thread_id": sanitize_thread_id(f"pulse-agent-mail-{slug}"),
                "ack_required": True,
            },
        )
        inbox = await call_tool(
            client,
            "fetch_inbox",
            {
                "project_key": project_key,
                "agent_name": "pulse-beta",
                "include_bodies": True,
                "limit": 5,
            },
        )
        claim_alpha = await call_tool(
            client,
            "file_reservation_paths",
            {
                "project_key": project_key,
                "agent_name": "pulse-alpha",
                "paths": [target_path],
                "ttl_seconds": 3600,
                "exclusive": True,
                "reason": "Pulse adapter smoke reservation",
            },
        )
        claim_beta = await call_tool(
            client,
            "file_reservation_paths",
            {
                "project_key": project_key,
                "agent_name": "pulse-beta",
                "paths": [target_path],
                "ttl_seconds": 3600,
                "exclusive": True,
                "reason": "Pulse adapter smoke conflict",
            },
        )
        release = await call_tool(
            client,
            "release_file_reservations",
            {
                "project_key": project_key,
                "agent_name": "pulse-alpha",
                "paths": [target_path],
            },
        )
    return {
        "ok": True,
        "slug": slug,
        "version": package_version(),
        "runtime_root": str(root),
        "project_key": project_key,
        "project": project,
        "agents": {"alpha": alpha, "beta": beta},
        "message": message,
        "inbox": inbox,
        "claim_alpha": claim_alpha,
        "claim_beta_conflict": claim_beta,
        "release_alpha": release,
    }


def artifact_path(slug: str, name: str) -> Path:
    path = build_dir(slug) / "artifacts" / RUNTIME_DIRNAME / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def check(slug: str, allow_reexec: bool = False) -> dict[str, Any]:
    if allow_reexec:
        maybe_reexec_in_build_venv(slug)
    ok, error = import_agent_mail()
    return {
        "ok": ok,
        "available": ok,
        "slug": slug,
        "python": sys.executable,
        "version": package_version(),
        "venv_python": str(build_venv_python(slug)),
        "venv_exists": build_venv_python(slug).exists(),
        "error": error,
    }


def check_cli(slug: str) -> int:
    payload = check(slug, allow_reexec=True)
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


def smoke(slug: str, allow_reexec: bool = False) -> int:
    if allow_reexec:
        maybe_reexec_in_build_venv(slug)
    ok, error = import_agent_mail()
    if not ok:
        print(json.dumps({"ok": False, "error": error}, indent=2), file=sys.stderr)
        return 1
    result = asyncio.run(smoke_async(slug))
    output = artifact_path(slug, "smoke_result.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "output_path": str(output)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Optional Pulse adapter for upstream MCP Agent Mail")
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="Check whether upstream MCP Agent Mail is available")
    check_parser.add_argument("slug")
    smoke_parser = sub.add_parser("smoke", help="Run an isolated upstream MCP Agent Mail smoke test")
    smoke_parser.add_argument("slug")
    args = parser.parse_args()
    if args.command == "check":
        return check_cli(args.slug)
    if args.command == "smoke":
        return smoke(args.slug, allow_reexec=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
