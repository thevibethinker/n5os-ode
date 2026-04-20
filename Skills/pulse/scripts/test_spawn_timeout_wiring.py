#!/usr/bin/env python3
"""Deterministic smoke test for stuck spawning timeout recovery."""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pulse_common import PATHS

BUILDS_DIR = PATHS.BUILDS
PULSE_SCRIPT = PATHS.SCRIPTS / "pulse.py"
TEST_SLUG = "test-spawn-timeout-wiring"


def iso_now(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).isoformat()


def reset_build_dir() -> Path:
    build_dir = BUILDS_DIR / TEST_SLUG
    if build_dir.exists():
        shutil.rmtree(build_dir)
    (build_dir / "drops").mkdir(parents=True)
    (build_dir / "deposits").mkdir(parents=True)
    (build_dir / "artifacts").mkdir(parents=True)
    return build_dir


def write_brief(build_dir: Path) -> None:
    brief = f"""---
created: 2026-04-19
last_edited: 2026-04-19
version: 1.0
provenance: test-spawn-timeout-wiring
drop_id: D1.1
build_slug: {TEST_SLUG}
drop_type: code
stream: 1
depends_on: []
spawn_mode: manual
spec_completeness: full
quality_contract:
  cwd: .
  check_cmd: "python3 Skills/pulse/scripts/test_spawn_timeout_wiring.py"
  required:
    - check_cmd
---

# D1.1: Spawn Timeout Smoke

## Objective
Prove that a stuck spawn handshake is converted into a retryable failure during tick.

## Scenarios

S1: Spawning timeout is recovered
  Given: A Drop is stuck in spawning longer than the timeout threshold
  When: Pulse tick runs
  Then: The Drop should fail with a spawn-timeout reason and immediately auto-retry
  Verify: Run this smoke test
"""
    (build_dir / "drops" / "D1.1-spawn-timeout-smoke.md").write_text(brief)


def write_meta(build_dir: Path, worker_pid: int) -> None:
    meta = {
        "slug": TEST_SLUG,
        "title": "Spawn Timeout Wiring Test",
        "status": "active",
        "current_stream": 1,
        "total_streams": 1,
        "created_at": iso_now(-60),
        "started_at": iso_now(-60),
        "drops": {
            "D1.1": {
                "status": "spawning",
                "spawn_requested_at": iso_now(-400),
                "spawn_worker_pid": worker_pid,
                "retry_count": 0,
                "spawn_mode": "manual",
                "blocking": True,
            }
        },
    }
    (build_dir / "meta.json").write_text(json.dumps(meta, indent=2))


def run_tick() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(PULSE_SCRIPT), "tick", TEST_SLUG],
        capture_output=True,
        text=True,
        cwd=str(PATHS.WORKSPACE),
        check=False,
    )


def read_meta() -> dict:
    return json.loads((BUILDS_DIR / TEST_SLUG / "meta.json").read_text())


def read_recovery_log() -> list[dict]:
    log_path = BUILDS_DIR / TEST_SLUG / "RECOVERY_LOG.jsonl"
    if not log_path.exists():
        return []
    return [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def cleanup(worker: subprocess.Popen[str] | None = None) -> None:
    if worker is not None and worker.poll() is None:
        worker.terminate()
        try:
            worker.wait(timeout=2)
        except subprocess.TimeoutExpired:
            worker.kill()
            worker.wait(timeout=2)

    build_dir = BUILDS_DIR / TEST_SLUG
    if build_dir.exists():
        shutil.rmtree(build_dir)


def main() -> int:
    worker = None
    try:
        build_dir = reset_build_dir()
        write_brief(build_dir)
        worker = subprocess.Popen(["sleep", "30"], text=True)
        write_meta(build_dir, worker.pid)

        result = run_tick()
        meta = read_meta()
        drop = meta["drops"]["D1.1"]
        actions = read_recovery_log()

        assert_true(result.returncode == 0, f"tick failed: {result.stderr}")
        assert_true(drop["status"] == "awaiting_manual", f"expected awaiting_manual, got {drop['status']}")
        assert_true(drop["retry_count"] == 1, f"expected retry_count=1, got {drop.get('retry_count')}")
        assert_true(
            drop.get("auto_retry_reason", "").startswith("Spawn error"),
            f"expected spawn auto-retry reason, got {drop.get('auto_retry_reason')}",
        )
        assert_true(drop.get("recovery_source") == "tick_auto", f"expected tick_auto, got {drop.get('recovery_source')}")
        assert_true(actions and actions[-1]["rule"] == "R2", "expected R2 recovery action in RECOVERY_LOG")
        assert_true(worker.poll() is not None, "expected stuck spawn worker to be terminated")

        print("PASS: stuck spawning drops time out, terminate the worker, and auto-retry")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    finally:
        if "--keep" not in sys.argv:
            cleanup(worker)


if __name__ == "__main__":
    sys.exit(main())
