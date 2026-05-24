#!/usr/bin/env python3
"""
Bootstrap optional upstream integration dependencies for a Pulse build.

The upstream source checkouts, virtual environments, runtime databases, and
generated clients are intentionally ignored by Git. This script recreates the
local evaluation/runtime surface expected by the optional Pulse adapters.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from pulse_common import PATHS


AGENT_MAIL_REPO = "https://github.com/Dicklesworthstone/mcp_agent_mail.git"
BAML_VERSION = "0.222.0"
HUMANLAYER_VERSION = "0.7.9"

BAML_PULSE_CONTRACT = '''\
class PulseDepositReview {
  drop_id string
  passed bool
  summary string
  files_touched string[]
  plan_deviations string[]
  schema_deviations string[]
  assumption_changes string[]
  scope_deviations string[]
  collision_risks string[]
  followup_required string[]
}

function ReviewPulseDeposit(deposit_text: string) -> PulseDepositReview {
  client "openai/gpt-4o-mini"

  prompt #"
    Review this Pulse worker deposit and return a structured review.

    {{ ctx.output_format }}

    Deposit:
    {{ deposit_text }}
  "#
}
'''


def run(cmd: list[str], cwd: Path | None = None, dry_run: bool = False) -> None:
    printable = " ".join(cmd)
    if cwd:
        printable = f"(cd {cwd} && {printable})"
    print(printable)
    if dry_run:
        return
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def require_uv() -> None:
    if not shutil_which("uv"):
        raise SystemExit("uv is required to bootstrap upstream Pulse integrations")


def shutil_which(name: str) -> str | None:
    from shutil import which

    return which(name)


def build_dir(slug: str) -> Path:
    root = PATHS.build(slug)
    if not root.exists():
        raise SystemExit(f"Build not found: {root}")
    return root


def bootstrap_agent_mail(slug: str, dry_run: bool = False) -> None:
    root = build_dir(slug) / "upstream" / "mcp_agent_mail"
    if not root.exists():
        run(["git", "clone", "--depth", "1", AGENT_MAIL_REPO, str(root)], dry_run=dry_run)
    run(["uv", "venv", str(root / ".venv")], dry_run=dry_run)
    run(["uv", "pip", "install", "--python", str(root / ".venv" / "bin" / "python"), "-e", str(root)], dry_run=dry_run)


def bootstrap_baml(slug: str, dry_run: bool = False) -> None:
    root = build_dir(slug) / "upstream" / "baml_eval"
    venv = root / ".venv"
    project = root / "pulse_contract_eval"
    contract = project / "baml_src" / "pulse_deposit.baml"
    run(["uv", "venv", str(venv)], dry_run=dry_run)
    run(["uv", "pip", "install", "--python", str(venv / "bin" / "python"), f"baml-py=={BAML_VERSION}"], dry_run=dry_run)
    if not dry_run:
        project.mkdir(parents=True, exist_ok=True)
    if not (project / "baml_src").exists():
        run([str(venv / "bin" / "baml"), "init", "--dest", str(project), "--client-type", "python/pydantic"], dry_run=dry_run)
    print(f"write {contract}")
    if not dry_run:
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_text(BAML_PULSE_CONTRACT, encoding="utf-8")
    run([str(venv / "bin" / "baml"), "check"], cwd=project, dry_run=dry_run)
    run([str(venv / "bin" / "baml"), "generate"], cwd=project, dry_run=dry_run)


def bootstrap_humanlayer(slug: str, dry_run: bool = False) -> None:
    root = build_dir(slug) / "upstream" / "humanlayer_eval"
    venv = root / ".venv"
    run(["uv", "venv", str(venv)], dry_run=dry_run)
    run(["uv", "pip", "install", "--python", str(venv / "bin" / "python"), f"humanlayer=={HUMANLAYER_VERSION}"], dry_run=dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap optional upstream Pulse integration dependencies")
    parser.add_argument("slug", help="Build slug under N5/builds")
    parser.add_argument(
        "--tool",
        choices=["all", "agent-mail", "baml", "humanlayer"],
        default="all",
        help="Integration dependency set to bootstrap",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    args = parser.parse_args()

    require_uv()
    if args.tool in ("all", "agent-mail"):
        bootstrap_agent_mail(args.slug, dry_run=args.dry_run)
    if args.tool in ("all", "baml"):
        bootstrap_baml(args.slug, dry_run=args.dry_run)
    if args.tool in ("all", "humanlayer"):
        bootstrap_humanlayer(args.slug, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
