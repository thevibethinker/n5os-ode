#!/usr/bin/env python3
"""
Optional Pulse adapter for upstream BAML.

This adapter is intentionally optional: Pulse must keep working when BAML is not
installed. For isolated evaluations, it can re-exec inside:

N5/builds/<slug>/upstream/baml_eval/.venv/bin/python
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


RUNTIME_DIRNAME = "baml-upstream"


def build_dir(slug: str) -> Path:
    return PATHS.build(slug)


def build_venv_python(slug: str) -> Path:
    return build_dir(slug) / "upstream" / "baml_eval" / ".venv" / "bin" / "python"


def build_venv_cli(slug: str) -> Path:
    return build_dir(slug) / "upstream" / "baml_eval" / ".venv" / "bin" / "baml"


def eval_dir(slug: str) -> Path:
    return build_dir(slug) / "upstream" / "baml_eval" / "pulse_contract_eval"


def artifact_path(slug: str, name: str) -> Path:
    path = build_dir(slug) / "artifacts" / RUNTIME_DIRNAME / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def maybe_reexec_in_build_venv(slug: str) -> None:
    if os.environ.get("PULSE_BAML_NO_REEXEC") == "1":
        return
    venv_python = build_venv_python(slug)
    if not venv_python.exists() or Path(sys.executable).resolve() == venv_python.resolve():
        return
    env = os.environ.copy()
    env["PULSE_BAML_NO_REEXEC"] = "1"
    result = subprocess.run([str(venv_python), __file__, *sys.argv[1:]], env=env)
    raise SystemExit(result.returncode)


def package_version() -> str | None:
    for name in ("baml-py", "baml_py"):
        try:
            return version(name)
        except PackageNotFoundError:
            continue
    return None


def import_baml() -> tuple[bool, str | None]:
    try:
        import baml_py  # noqa: F401
        return True, None
    except Exception as exc:
        return False, str(exc)


def check(slug: str, allow_reexec: bool = False) -> dict[str, Any]:
    if allow_reexec:
        maybe_reexec_in_build_venv(slug)
    ok, error = import_baml()
    cli = build_venv_cli(slug)
    contract = eval_dir(slug) / "baml_src" / "pulse_deposit.baml"
    generated = eval_dir(slug) / "baml_client" / "types.py"
    return {
        "ok": ok and cli.exists() and contract.exists() and generated.exists(),
        "available": ok,
        "slug": slug,
        "python": sys.executable,
        "version": package_version(),
        "venv_python": str(build_venv_python(slug)),
        "venv_exists": build_venv_python(slug).exists(),
        "cli": str(cli),
        "cli_exists": cli.exists(),
        "contract": str(contract),
        "contract_exists": contract.exists(),
        "generated_types": str(generated),
        "generated_types_exists": generated.exists(),
        "error": error,
    }


def check_cli(slug: str) -> int:
    payload = check(slug, allow_reexec=True)
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


def run_baml(slug: str, args: list[str], log_name: str) -> tuple[int, str]:
    cli = build_venv_cli(slug)
    if not cli.exists():
        return 1, f"BAML CLI not found: {cli}"
    out = artifact_path(slug, log_name)
    result = subprocess.run([str(cli), *args], cwd=str(eval_dir(slug)), text=True, capture_output=True)
    out.write_text(result.stdout + result.stderr, encoding="utf-8")
    return result.returncode, str(out)


def generate(slug: str, allow_reexec: bool = False) -> int:
    if allow_reexec:
        maybe_reexec_in_build_venv(slug)
    status = check(slug)
    if not status["available"]:
        print(json.dumps({"ok": False, "error": status["error"]}, indent=2), file=sys.stderr)
        return 1
    check_code, check_log = run_baml(slug, ["check"], "adapter_check.log")
    gen_code, gen_log = run_baml(slug, ["generate"], "adapter_generate.log")
    generated_types = eval_dir(slug) / "baml_client" / "types.py"
    generated_text = generated_types.read_text(encoding="utf-8") if generated_types.exists() else ""
    result = {
        "ok": check_code == 0 and gen_code == 0 and "class PulseDepositReview" in generated_text,
        "slug": slug,
        "version": package_version(),
        "check_log": check_log,
        "generate_log": gen_log,
        "generated_types": str(generated_types),
        "pulse_contract_generated": "class PulseDepositReview" in generated_text,
    }
    output = artifact_path(slug, "generate_result.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"ok": result["ok"], "output_path": str(output)}, indent=2))
    return 0 if result["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Optional Pulse adapter for upstream BAML")
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="Check whether upstream BAML is available")
    check_parser.add_argument("slug")
    generate_parser = sub.add_parser("generate", help="Run BAML contract check/generate test")
    generate_parser.add_argument("slug")
    args = parser.parse_args()
    if args.command == "check":
        return check_cli(args.slug)
    if args.command == "generate":
        return generate(args.slug, allow_reexec=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
