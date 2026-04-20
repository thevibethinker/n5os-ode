#!/usr/bin/env python3
"""Deterministic smoke test for inline recovery during pulse tick()."""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pulse_common import PATHS

BUILDS_DIR = PATHS.BUILDS
PULSE_SCRIPT = PATHS.SCRIPTS / "pulse.py"
TEST_SLUGS = {
    "dead_retry": "test-tick-recovery-dead",
    "spawn_retry": "test-tick-recovery-spawn",
    "healthy": "test-tick-recovery-healthy",
}


def iso_now(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).isoformat()


def reset_build_dir(slug: str) -> Path:
    build_dir = BUILDS_DIR / slug
    if build_dir.exists():
        shutil.rmtree(build_dir)
    (build_dir / "drops").mkdir(parents=True)
    (build_dir / "deposits").mkdir(parents=True)
    (build_dir / "artifacts").mkdir(parents=True)
    return build_dir


def write_brief(build_dir: Path, slug: str, drop_id: str) -> None:
    brief = f"""---
created: 2026-04-14
last_edited: 2026-04-14
version: 1.0
provenance: test-tick-recovery-wiring
---

# {drop_id}: Recovery Smoke

## Objective
Prove inline recovery wiring for {slug}.

## On Completion

- Write the deposit requested by the orchestrator.
"""
    (build_dir / "drops" / f"{drop_id}-recovery-smoke.md").write_text(brief)


def write_meta(build_dir: Path, slug: str, drop_status: dict) -> None:
    meta = {
        "slug": slug,
        "title": f"Recovery Test {slug}",
        "status": "active",
        "current_stream": 1,
        "total_streams": 1,
        "created_at": iso_now(-60),
        "started_at": iso_now(-60),
        "drops": {
            "D1.1": drop_status,
        },
    }
    (build_dir / "meta.json").write_text(json.dumps(meta, indent=2))


def run_tick(slug: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(PULSE_SCRIPT), "tick", slug],
        capture_output=True,
        text=True,
        cwd=str(PATHS.WORKSPACE),
        check=False,
    )


def read_meta(slug: str) -> dict:
    return json.loads((BUILDS_DIR / slug / "meta.json").read_text())


def read_recovery_log(slug: str) -> list[dict]:
    log_path = BUILDS_DIR / slug / "RECOVERY_LOG.jsonl"
    if not log_path.exists():
        return []
    return [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def setup_dead_retry() -> None:
    slug = TEST_SLUGS["dead_retry"]
    build_dir = reset_build_dir(slug)
    write_brief(build_dir, slug, "D1.1")
    write_meta(
        build_dir,
        slug,
        {
            "status": "dead",
            "dead_at": iso_now(-5),
            "dead_reason": "Running for 16 minutes",
            "retry_count": 0,
            "spawn_mode": "manual",
            "blocking": True,
        },
    )


def setup_spawn_retry() -> None:
    slug = TEST_SLUGS["spawn_retry"]
    build_dir = reset_build_dir(slug)
    write_brief(build_dir, slug, "D1.1")
    write_meta(
        build_dir,
        slug,
        {
            "status": "failed",
            "failure_reason": "Spawn error: spawn worker exited unexpectedly",
            "failed_at": iso_now(-5),
            "retry_count": 0,
            "spawn_mode": "manual",
            "blocking": True,
        },
    )


def setup_healthy_build() -> dict:
    slug = TEST_SLUGS["healthy"]
    build_dir = reset_build_dir(slug)
    write_brief(build_dir, slug, "D1.1")
    write_meta(
        build_dir,
        slug,
        {
            "status": "running",
            "started_at": iso_now(-30),
            "conversation_id": "test-healthy-running",
            "blocking": True,
        },
    )
    return read_meta(slug)


def verify_dead_retry(result: subprocess.CompletedProcess[str]) -> None:
    slug = TEST_SLUGS["dead_retry"]
    meta = read_meta(slug)
    drop = meta["drops"]["D1.1"]
    actions = read_recovery_log(slug)

    assert_true(result.returncode == 0, f"dead retry tick failed: {result.stderr}")
    assert_true(drop["retry_count"] == 1, f"expected retry_count=1, got {drop.get('retry_count')}")
    assert_true(drop["status"] == "awaiting_manual", f"expected awaiting_manual after inline retry, got {drop['status']}")
    assert_true(drop.get("recovery_source") == "tick_auto", f"expected tick_auto recovery source, got {drop.get('recovery_source')}")
    assert_true(actions and actions[-1]["rule"] == "R1", "expected R1 recovery action in RECOVERY_LOG")


def verify_spawn_retry(result: subprocess.CompletedProcess[str]) -> None:
    slug = TEST_SLUGS["spawn_retry"]
    meta = read_meta(slug)
    drop = meta["drops"]["D1.1"]
    actions = read_recovery_log(slug)

    assert_true(result.returncode == 0, f"spawn retry tick failed: {result.stderr}")
    assert_true(drop["retry_count"] == 1, f"expected retry_count=1, got {drop.get('retry_count')}")
    assert_true(drop["status"] == "awaiting_manual", f"expected awaiting_manual after spawn retry, got {drop['status']}")
    assert_true(drop.get("recovery_source") == "tick_auto", f"expected tick_auto recovery source, got {drop.get('recovery_source')}")
    assert_true(actions and actions[-1]["rule"] == "R2", "expected R2 recovery action in RECOVERY_LOG")


def verify_healthy_build(result: subprocess.CompletedProcess[str], before_meta: dict) -> None:
    slug = TEST_SLUGS["healthy"]
    after_meta = read_meta(slug)
    actions = read_recovery_log(slug)

    assert_true(result.returncode == 0, f"healthy tick failed: {result.stderr}")
    assert_true(after_meta == before_meta, "healthy build mutated during tick")
    assert_true(not actions, "healthy build should not record recovery actions")


def cleanup() -> None:
    for slug in TEST_SLUGS.values():
        build_dir = BUILDS_DIR / slug
        if build_dir.exists():
            shutil.rmtree(build_dir)


def main() -> int:
    try:
        setup_dead_retry()
        setup_spawn_retry()
        healthy_before = setup_healthy_build()

        dead_result = run_tick(TEST_SLUGS["dead_retry"])
        spawn_result = run_tick(TEST_SLUGS["spawn_retry"])
        healthy_result = run_tick(TEST_SLUGS["healthy"])

        verify_dead_retry(dead_result)
        verify_spawn_retry(spawn_result)
        verify_healthy_build(healthy_result, healthy_before)

        print("PASS: tick performs inline recovery for dead and spawn failures without mutating healthy builds")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    finally:
        if "--keep" not in sys.argv:
            cleanup()


if __name__ == "__main__":
    sys.exit(main())
