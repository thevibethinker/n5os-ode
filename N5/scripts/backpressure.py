#!/usr/bin/env python3
"""
Backpressure Validation Script
Unified validation layer for builds and code paths.

Implements the "Ralph Wiggum" backpressure concept: automated validation
that rejects invalid work before human review.

Backpressure = tests + lints + type checks + custom validators

Usage:
    python3 backpressure.py <build_slug>
    python3 backpressure.py --path /path/to/code
    python3 backpressure.py <build_slug> --json
    python3 backpressure.py --help
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml

sys.path.insert(0, "/home/workspace")
from N5.lib.paths import N5_CONFIG_DIR, N5_BUILDS_DIR


# Exit codes
EXIT_PASS = 0
EXIT_WARN = 1
EXIT_FAIL = 2


@dataclass
class ValidatorResult:
    """Result from a single validator run."""
    name: str
    status: str  # PASS, WARN, FAIL, SKIP
    details: str
    exit_code: int = 0
    duration_ms: int = 0


@dataclass
class BackpressureReport:
    """Aggregated backpressure validation results."""
    status: str  # PASS, WARN, FAIL
    validators: List[ValidatorResult] = field(default_factory=list)
    summary: str = ""
    target: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "validators": [asdict(v) for v in self.validators],
            "summary": self.summary,
            "target": self.target,
            "timestamp": self.timestamp
        }


def load_config(config_path: Optional[Path], build_path: Optional[Path]) -> Dict[str, Any]:
    """Load backpressure config with fallback chain."""
    default_config = N5_CONFIG_DIR / "backpressure_rules.yaml"
    
    # Priority: explicit config > build-local > global default
    paths_to_try = []
    
    if config_path:
        paths_to_try.append(config_path)
    
    if build_path:
        local_config = build_path / "backpressure.yaml"
        paths_to_try.append(local_config)
    
    paths_to_try.append(default_config)
    
    for path in paths_to_try:
        if path.exists():
            with open(path) as f:
                config = yaml.safe_load(f) or {}
            return config.get("defaults", config)
    
    # Fallback defaults if no config found
    return {
        "pytest": {"enabled": True, "args": ["-q", "--tb=short"], "fail_on": "error"},
        "ruff": {"enabled": True, "args": ["check", "."], "fail_on": "error"},
        "mypy": {"enabled": False, "args": ["--ignore-missing-imports"], "fail_on": "warning"},
        "custom": []
    }


def run_validator(name: str, command: List[str], cwd: Path, fail_on: str) -> ValidatorResult:
    """Run a single validator and capture results."""
    import time
    
    start = time.time()
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        duration_ms = int((time.time() - start) * 1000)
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output = stdout or stderr or "(no output)"
        
        # Truncate long output
        if len(output) > 500:
            output = output[:500] + "... (truncated)"
        
        if result.returncode == 0:
            return ValidatorResult(
                name=name,
                status="PASS",
                details=output if output != "(no output)" else "All checks passed",
                exit_code=result.returncode,
                duration_ms=duration_ms
            )
        else:
            # Determine status based on fail_on
            if fail_on == "error":
                status = "FAIL"
            elif fail_on == "warning":
                status = "WARN"
            else:  # never
                status = "WARN"
            
            return ValidatorResult(
                name=name,
                status=status,
                details=output,
                exit_code=result.returncode,
                duration_ms=duration_ms
            )
    
    except subprocess.TimeoutExpired:
        return ValidatorResult(
            name=name,
            status="FAIL",
            details="Timeout after 300 seconds",
            exit_code=-1,
            duration_ms=300000
        )
    except Exception as e:
        return ValidatorResult(
            name=name,
            status="SKIP",
            details=f"Error: {str(e)}",
            exit_code=-1,
            duration_ms=0
        )


def check_validator_exists(name: str) -> bool:
    """Check if a validator command is available."""
    try:
        subprocess.run(
            ["which", name],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_pytest(config: Dict[str, Any], target_path: Path) -> ValidatorResult:
    """Run pytest validator."""
    cfg = config.get("pytest", {})
    
    if not cfg.get("enabled", True):
        return ValidatorResult(name="pytest", status="SKIP", details="Disabled in config")
    
    if not check_validator_exists("pytest"):
        return ValidatorResult(name="pytest", status="SKIP", details="pytest not installed")
    
    # Check for test files
    test_files = list(target_path.rglob("test_*.py")) + list(target_path.rglob("*_test.py"))
    if not test_files:
        return ValidatorResult(name="pytest", status="SKIP", details="No test files found")
    
    args = cfg.get("args", ["-q", "--tb=short"])
    command = ["pytest"] + args + [str(target_path)]
    
    return run_validator("pytest", command, target_path, cfg.get("fail_on", "error"))


def run_ruff(config: Dict[str, Any], target_path: Path) -> ValidatorResult:
    """Run ruff linter."""
    cfg = config.get("ruff", {})
    
    if not cfg.get("enabled", True):
        return ValidatorResult(name="ruff", status="SKIP", details="Disabled in config")
    
    if not check_validator_exists("ruff"):
        # Fallback to flake8
        if check_validator_exists("flake8"):
            command = ["flake8", str(target_path)]
            result = run_validator("flake8", command, target_path, cfg.get("fail_on", "error"))
            result.name = "ruff (flake8 fallback)"
            return result
        return ValidatorResult(name="ruff", status="SKIP", details="Neither ruff nor flake8 installed")
    
    # Check for Python files
    py_files = list(target_path.rglob("*.py"))
    if not py_files:
        return ValidatorResult(name="ruff", status="SKIP", details="No Python files found")
    
    args = cfg.get("args", ["check", "."])
    command = ["ruff"] + args
    
    return run_validator("ruff", command, target_path, cfg.get("fail_on", "error"))


def run_mypy(config: Dict[str, Any], target_path: Path) -> ValidatorResult:
    """Run mypy type checker."""
    cfg = config.get("mypy", {})
    
    if not cfg.get("enabled", False):  # opt-in by default
        return ValidatorResult(name="mypy", status="SKIP", details="Disabled in config (opt-in)")
    
    if not check_validator_exists("mypy"):
        return ValidatorResult(name="mypy", status="SKIP", details="mypy not installed")
    
    # Check for Python files
    py_files = list(target_path.rglob("*.py"))
    if not py_files:
        return ValidatorResult(name="mypy", status="SKIP", details="No Python files found")
    
    args = cfg.get("args", ["--ignore-missing-imports"])
    command = ["mypy"] + args + [str(target_path)]
    
    return run_validator("mypy", command, target_path, cfg.get("fail_on", "warning"))


def run_custom_validators(config: Dict[str, Any], target_path: Path) -> List[ValidatorResult]:
    """Run custom validators defined in config."""
    results = []
    custom_validators = config.get("custom", [])
    
    for validator in custom_validators:
        name = validator.get("name", "custom")
        command = validator.get("command", "").split()
        fail_on = validator.get("fail_on", "error")
        
        if not command:
            results.append(ValidatorResult(
                name=name,
                status="SKIP",
                details="No command specified"
            ))
            continue
        
        results.append(run_validator(name, command, target_path, fail_on))
    
    return results


def resolve_target(build_slug: Optional[str], path: Optional[str]) -> Path:
    """Resolve the target path for validation."""
    if path:
        return Path(path).resolve()
    
    if build_slug:
        build_path = N5_BUILDS_DIR / build_slug
        if build_path.exists():
            return build_path
        
        # Maybe it's a site or other project
        workspace = Path("/home/workspace")
        candidates = [
            workspace / build_slug,
            workspace / "Sites" / build_slug,
            workspace / "Skills" / build_slug,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        # Fall back to workspace root with warning
        return workspace
    
    return Path.cwd()


def run_backpressure(
    build_slug: Optional[str] = None,
    path: Optional[str] = None,
    config_path: Optional[str] = None
) -> BackpressureReport:
    """Run all backpressure validators and aggregate results."""
    
    target_path = resolve_target(build_slug, path)
    config = load_config(
        Path(config_path) if config_path else None,
        target_path if target_path.is_dir() else target_path.parent
    )
    
    report = BackpressureReport(
        status="PASS",
        target=str(target_path),
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    # Run validators
    report.validators.append(run_pytest(config, target_path))
    report.validators.append(run_ruff(config, target_path))
    report.validators.append(run_mypy(config, target_path))
    report.validators.extend(run_custom_validators(config, target_path))
    
    # Determine overall status
    statuses = [v.status for v in report.validators if v.status != "SKIP"]
    
    if "FAIL" in statuses:
        report.status = "FAIL"
    elif "WARN" in statuses:
        report.status = "WARN"
    elif not statuses:
        report.status = "WARN"  # All skipped = warning
    else:
        report.status = "PASS"
    
    # Generate summary
    passed = sum(1 for v in report.validators if v.status == "PASS")
    warned = sum(1 for v in report.validators if v.status == "WARN")
    failed = sum(1 for v in report.validators if v.status == "FAIL")
    skipped = sum(1 for v in report.validators if v.status == "SKIP")
    
    parts = []
    if passed:
        parts.append(f"{passed} passed")
    if warned:
        parts.append(f"{warned} warnings")
    if failed:
        parts.append(f"{failed} failed")
    if skipped:
        parts.append(f"{skipped} skipped")
    
    report.summary = f"Backpressure: {', '.join(parts)} | Target: {target_path.name}"
    
    return report


def print_report(report: BackpressureReport, json_output: bool = False):
    """Print the report to stdout."""
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return
    
    # Human-readable output
    status_emoji = {"PASS": "✓", "WARN": "⚠", "FAIL": "✗", "SKIP": "○"}
    
    print(f"\n{'='*60}")
    print(f"BACKPRESSURE VALIDATION")
    print(f"{'='*60}")
    print(f"Target: {report.target}")
    print(f"Status: {status_emoji.get(report.status, '?')} {report.status}")
    print(f"{'='*60}\n")
    
    for v in report.validators:
        emoji = status_emoji.get(v.status, "?")
        print(f"  {emoji} {v.name}: {v.status}")
        if v.details and v.status != "PASS":
            # Indent details
            for line in v.details.split("\n")[:5]:  # Max 5 lines
                print(f"      {line}")
        if v.duration_ms > 0:
            print(f"      ({v.duration_ms}ms)")
        print()
    
    print(f"{'='*60}")
    print(f"Summary: {report.summary}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Backpressure validation for builds and code paths.",
        epilog="""
Examples:
  python3 backpressure.py ralph-learnings          # Validate a build
  python3 backpressure.py --path N5/scripts/       # Validate specific path
  python3 backpressure.py my-build --json          # JSON output
  python3 backpressure.py my-build --config x.yaml # Custom config

Exit codes:
  0 = PASS (all validators passed)
  1 = WARN (some warnings, no failures)
  2 = FAIL (at least one validator failed)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "build_slug",
        nargs="?",
        help="Build slug to validate (e.g., 'ralph-learnings')"
    )
    parser.add_argument(
        "--path", "-p",
        help="Path to validate instead of build slug"
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to custom config file"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    if not args.build_slug and not args.path:
        parser.print_help()
        sys.exit(1)
    
    report = run_backpressure(
        build_slug=args.build_slug,
        path=args.path,
        config_path=args.config
    )
    
    print_report(report, json_output=args.json)
    
    # Exit with appropriate code
    if report.status == "PASS":
        sys.exit(EXIT_PASS)
    elif report.status == "WARN":
        sys.exit(EXIT_WARN)
    else:
        sys.exit(EXIT_FAIL)


if __name__ == "__main__":
    main()
