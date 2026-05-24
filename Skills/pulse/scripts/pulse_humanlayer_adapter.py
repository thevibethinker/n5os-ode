#!/usr/bin/env python3
"""
Optional Pulse adapter for upstream HumanLayer approval semantics.

This adapter is intentionally optional: Pulse must keep working when HumanLayer
is not installed. For isolated evaluations, it can re-exec inside:

N5/builds/<slug>/upstream/humanlayer_eval/.venv/bin/python
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from pulse_common import PATHS


RUNTIME_DIRNAME = "humanlayer-upstream"


def build_dir(slug: str) -> Path:
    return PATHS.build(slug)


def build_venv_python(slug: str) -> Path:
    return build_dir(slug) / "upstream" / "humanlayer_eval" / ".venv" / "bin" / "python"


def eval_script(slug: str) -> Path:
    return build_dir(slug) / "prototype" / "humanlayer_upstream_eval.py"


def artifact_path(slug: str, name: str) -> Path:
    path = build_dir(slug) / "artifacts" / RUNTIME_DIRNAME / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def maybe_reexec_in_build_venv(slug: str) -> None:
    if os.environ.get("PULSE_HUMANLAYER_NO_REEXEC") == "1":
        return
    venv_python = build_venv_python(slug)
    if not venv_python.exists() or Path(sys.executable).resolve() == venv_python.resolve():
        return
    env = os.environ.copy()
    env["PULSE_HUMANLAYER_NO_REEXEC"] = "1"
    result = subprocess.run([str(venv_python), __file__, *sys.argv[1:]], env=env)
    raise SystemExit(result.returncode)


def package_version() -> str | None:
    try:
        return version("humanlayer")
    except PackageNotFoundError:
        return None


def import_humanlayer() -> tuple[bool, str | None]:
    try:
        import humanlayer  # noqa: F401
        return True, None
    except Exception as exc:
        return False, str(exc)


def check(slug: str, allow_reexec: bool = False) -> dict[str, Any]:
    if allow_reexec:
        maybe_reexec_in_build_venv(slug)
    ok, error = import_humanlayer()
    script = eval_script(slug)
    return {
        "ok": ok and script.exists(),
        "available": ok,
        "slug": slug,
        "python": sys.executable,
        "version": package_version(),
        "venv_python": str(build_venv_python(slug)),
        "venv_exists": build_venv_python(slug).exists(),
        "eval_script": str(script),
        "eval_script_exists": script.exists(),
        "error": error,
    }


def check_cli(slug: str) -> int:
    payload = check(slug, allow_reexec=True)
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


def smoke(slug: str, allow_reexec: bool = False) -> int:
    if allow_reexec:
        maybe_reexec_in_build_venv(slug)
    status = check(slug)
    if not status["available"]:
        print(json.dumps({"ok": False, "error": status["error"]}, indent=2), file=sys.stderr)
        return 1
    script = eval_script(slug)
    if not script.exists():
        print(json.dumps({"ok": False, "error": f"missing eval script: {script}"}, indent=2), file=sys.stderr)
        return 1
    result = subprocess.run([sys.executable, str(script)], cwd=str(PATHS.WORKSPACE), text=True, capture_output=True)
    log_path = artifact_path(slug, "adapter_smoke.log")
    log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    output = artifact_path(slug, "eval_result.json")
    payload: dict[str, Any]
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except Exception as exc:
        payload = {"ok": False, "error": f"could not read eval output: {exc}"}
    smoke_result = {
        "ok": result.returncode == 0 and bool(payload.get("ok")),
        "slug": slug,
        "version": package_version(),
        "log_path": str(log_path),
        "eval_result": str(output),
        "approval_semantics": payload.get("approval_semantics", {}),
    }
    smoke_output = artifact_path(slug, "smoke_result.json")
    smoke_output.write_text(json.dumps(smoke_result, indent=2), encoding="utf-8")
    print(json.dumps({"ok": smoke_result["ok"], "output_path": str(smoke_output)}, indent=2))
    return 0 if smoke_result["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Optional Pulse adapter for upstream HumanLayer")
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="Check whether upstream HumanLayer is available")
    check_parser.add_argument("slug")
    smoke_parser = sub.add_parser("smoke", help="Run HumanLayer approval semantics smoke test")
    smoke_parser.add_argument("slug")
    args = parser.parse_args()
    if args.command == "check":
        return check_cli(args.slug)
    if args.command == "smoke":
        return smoke(args.slug, allow_reexec=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
