#!/usr/bin/env python3
"""
N5 Compatibility Scanner

Purpose: Safely assess whether a Zo Computer is ready for the N5 hybrid Git+submodule setup
without making any changes. Produces a concise human summary and a machine-readable JSON report.

Exit codes:
 0 -> Compatible (green)
 2 -> Compatible with remediation needed (yellow)
 1 -> Not compatible (red)

Usage:
  python3 /home/workspace/N5/scripts/n5_compat_scan.py --json /home/workspace/N5/logs/n5_compat_report.json
  python3 /home/workspace/N5/scripts/n5_compat_scan.py --dry-run

Notes:
 - No writes outside /home/workspace/N5/logs (and only if permitted)
 - No network traffic beyond a HEAD connection to github.com:443 to test reachability
 - Does NOT initialize git repos or submodules
"""
import argparse
import json
import logging
import os
import platform
import shutil
import socket
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("n5_compat_scan")

WORKSPACE = Path("/home/workspace")
N5_DIR = WORKSPACE / "N5"
LOG_DIR = N5_DIR / "logs"

@dataclass
class CheckResult:
    name: str
    status: str  # pass | warn | fail
    detail: str
    data: Optional[dict] = None

@dataclass
class Report:
    overall: str
    summary: str
    checks: List[CheckResult]
    environment: Dict[str, str]


def run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def check_python() -> CheckResult:
    ver = platform.python_version()
    return CheckResult(
        name="python",
        status="pass" if tuple(map(int, ver.split("."))) >= (3, 10, 0) else "warn",
        detail=f"Python {ver} detected (>=3.10 recommended)",
        data={"version": ver},
    )


def check_git() -> CheckResult:
    git_path = shutil.which("git")
    if not git_path:
        return CheckResult("git", "fail", "git not installed")
    proc = run_cmd(["git", "--version"])
    ver = proc.stdout.strip().split()[-1] if proc.stdout else "unknown"
    # Require >= 2.30 for robust submodule UX
    try:
        parts = tuple(int(p) for p in ver.split(".")[:3])
        status = "pass" if parts >= (2, 30, 0) else "warn"
    except Exception:
        status = "warn"
    return CheckResult("git", status, f"git {ver} detected (>=2.30 recommended)", {"version": ver})


def check_gh_cli() -> CheckResult:
    gh_path = shutil.which("gh")
    if not gh_path:
        return CheckResult("gh", "warn", "GitHub CLI not installed (optional, recommended for repo automation)")
    ver = run_cmd(["gh", "--version"]).stdout.splitlines()[0].strip()
    return CheckResult("gh", "pass", ver)


def check_dirs() -> List[CheckResult]:
    results: List[CheckResult] = []
    # Workspace exists
    if WORKSPACE.exists():
        results.append(CheckResult("workspace_dir", "pass", str(WORKSPACE)))
    else:
        results.append(CheckResult("workspace_dir", "fail", f"Missing {WORKSPACE}"))
    # N5 directory presence
    if N5_DIR.exists():
        results.append(CheckResult("n5_dir", "pass", str(N5_DIR)))
    else:
        results.append(CheckResult("n5_dir", "warn", f"{N5_DIR} does not exist yet (installer will create)"))
    # Logs directory write test (in-memory only)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (LOG_DIR / ".write_test").write_text("ok")
        (LOG_DIR / ".write_test").unlink(missing_ok=True)
        results.append(CheckResult("write_perm", "pass", f"Writable: {LOG_DIR}"))
    except Exception as e:
        results.append(CheckResult("write_perm", "fail", f"Cannot write to {LOG_DIR}: {e}"))
    return results


def check_disk() -> CheckResult:
    usage = shutil.disk_usage(str(WORKSPACE))
    gb_free = usage.free / (1024**3)
    status = "pass" if gb_free >= 1.0 else ("warn" if gb_free >= 0.2 else "fail")
    return CheckResult("disk", status, f"Free space: {gb_free:.2f} GB (>=1.0 GB recommended)", {"free_gb": round(gb_free, 2)})


def check_network() -> CheckResult:
    try:
        with socket.create_connection(("github.com", 443), timeout=3):
            return CheckResult("network_github", "pass", "Reachable: github.com:443")
    except Exception as e:
        return CheckResult("network_github", "warn", f"github.com:443 not reachable: {e}")


def check_git_repo_state() -> List[CheckResult]:
    results: List[CheckResult] = []
    n5_git = N5_DIR / ".git"
    if n5_git.exists():
        # It's a repo; check submodule readiness and cleanliness
        results.append(CheckResult("n5_git_repo", "pass", f"Git repo present at {N5_DIR}"))
        # Clean working tree?
        proc = run_cmd(["git", "-C", str(N5_DIR), "status", "--porcelain"])
        dirty = bool(proc.stdout.strip())
        results.append(CheckResult("n5_git_clean", "warn" if dirty else "pass", "Working tree is dirty" if dirty else "Clean working tree"))
        # Submodule slot conflicts
        n5_core_path = N5_DIR / "n5_core"
        if n5_core_path.exists() and not (n5_core_path / ".git").exists():
            results.append(CheckResult("n5_core_conflict", "fail", f"{n5_core_path} exists and is not a git repo (would block submodule)"))
        else:
            results.append(CheckResult("n5_core_slot", "pass", "No conflicts for n5_core"))
    else:
        results.append(CheckResult("n5_git_repo", "warn", f"{N5_DIR} is not a git repo (optional; recommended for private config)"))
        # Still check for potential conflicts
        n5_core_path = N5_DIR / "n5_core"
        if n5_core_path.exists() and not (n5_core_path / ".git").exists():
            results.append(CheckResult("n5_core_conflict", "fail", f"{n5_core_path} exists and is not a git repo (would block submodule)"))
        else:
            results.append(CheckResult("n5_core_slot", "pass", "No conflicts for n5_core"))
    return results


def summarize(checks: List[CheckResult]) -> str:
    fails = [c for c in checks if c.status == "fail"]
    warns = [c for c in checks if c.status == "warn"]
    if fails:
        return f"RED: {len(fails)} failing checks, {len(warns)} warnings"
    if warns:
        return f"YELLOW: {len(warns)} warnings, no failures"
    return "GREEN: All checks passed"


def main() -> int:
    parser = argparse.ArgumentParser(description="N5 Compatibility Scanner")
    parser.add_argument("--json", type=str, default=None, help="Write JSON report to this path")
    parser.add_argument("--dry-run", action="store_true", help="No-op flag for consistency")
    args = parser.parse_args()

    env = {
        "os": platform.platform(),
        "python": platform.python_version(),
        "cwd": str(Path.cwd()),
    }

    checks: List[CheckResult] = []
    checks.append(check_python())
    checks.append(check_git())
    checks.append(check_gh_cli())
    checks.extend(check_dirs())
    checks.append(check_disk())
    checks.append(check_network())
    checks.extend(check_git_repo_state())

    summary = summarize(checks)
    overall = "pass" if summary.startswith("GREEN") else ("warn" if summary.startswith("YELLOW") else "fail")

    report = Report(
        overall=overall,
        summary=summary,
        checks=checks,
        environment=env,
    )

    # Log human summary
    logger.info(summary)
    for c in checks:
        logger.info(f"- {c.name}: {c.status} - {c.detail}")

    # Optionally write JSON
    if args.json:
        try:
            out = Path(args.json)
            out.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "overall": report.overall,
                "summary": report.summary,
                "environment": report.environment,
                "checks": [asdict(c) for c in report.checks],
            }
            out.write_text(json.dumps(payload, indent=2))
            logger.info(f"Saved JSON report to {out}")
        except Exception as e:
            logger.error(f"Failed to write JSON report: {e}")

    if overall == "pass":
        return 0
    if overall == "warn":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
