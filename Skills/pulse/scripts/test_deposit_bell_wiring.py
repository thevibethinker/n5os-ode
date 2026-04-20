#!/usr/bin/env python3
"""Deterministic smoke test for deposit bell wiring."""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BUILDS_DIR = Path("/home/workspace/N5/builds")
PULSE_SCRIPT = Path("/home/workspace/Skills/pulse/scripts/pulse.py")
TEST_SLUG = "test-deposit-bell"
MISSING_SLUG = "test-deposit-bell-missing"


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


def write_brief(build_dir: Path, slug: str, drop_id: str, drop_type: str = "code") -> None:
    brief = f"""---
created: 2026-04-19
last_edited: 2026-04-19
version: 1.0
provenance: test-deposit-bell-wiring
drop_id: {drop_id}
build_slug: {slug}
drop_type: {drop_type}
stream: 1
depends_on: []
spawn_mode: manual
spec_completeness: full
quality_contract:
  cwd: /home/workspace
  check_cmd: "python3 Skills/pulse/scripts/test_deposit_bell_wiring.py"
  required:
    - check_cmd
---

# {drop_id}: Deposit Bell Smoke

## Objective
Prove the deposit bell wiring for {slug}.

## Scenarios

S1: Deposit bell fires
  Given: A deposit exists for {drop_id}
  When: Pulse bell is rung
  Then: Tick should consume the deposit and move orchestration forward
  Verify: Run the regression test
"""
    (build_dir / "drops" / f"{drop_id}-deposit-bell-smoke.md").write_text(brief)


def write_meta(build_dir: Path, slug: str) -> None:
    meta = {
        "schema_version": 3,
        "slug": slug,
        "title": f"Deposit Bell Test {slug}",
        "status": "active",
        "build_mode": "standard",
        "created_at": iso_now(-60),
        "started_at": iso_now(-60),
        "last_progress_at": iso_now(-60),
        "waves": {
            "W1": ["D1.1"],
            "W2": ["D2.1"],
        },
        "active_wave": "W1",
        "drops": {
            "D1.1": {
                "name": "Producer",
                "stream": 1,
                "order": 1,
                "depends_on": [],
                "spawn_mode": "manual",
                "blocking": True,
                "status": "running",
                "started_at": iso_now(-30),
                "conversation_id": f"{slug}-producer",
            },
            "D2.1": {
                "name": "Consumer",
                "stream": 2,
                "order": 1,
                "depends_on": ["D1.1"],
                "spawn_mode": "manual",
                "blocking": True,
                "status": "pending",
            },
        },
    }
    (build_dir / "meta.json").write_text(json.dumps(meta, indent=2))


def write_valid_artifact(build_dir: Path) -> None:
    artifact = """def add(a: int, b: int) -> int:
    return a + b
"""
    (build_dir / "artifacts" / "ok.py").write_text(artifact)


def write_deposit(build_dir: Path, slug: str, drop_id: str) -> None:
    deposit = {
        "drop_id": drop_id,
        "status": "complete",
        "timestamp": iso_now(),
        "summary": "Producer completed and wrote a valid artifact.",
        "artifacts": [f"N5/builds/{slug}/artifacts/ok.py"],
    }
    (build_dir / "deposits" / f"{drop_id}.json").write_text(json.dumps(deposit, indent=2))


def run_ring(slug: str, drop_id: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(PULSE_SCRIPT), "ring", slug, drop_id],
        capture_output=True,
        text=True,
        cwd="/home/workspace",
        check=False,
    )


def read_meta(slug: str) -> dict:
    return json.loads((BUILDS_DIR / slug / "meta.json").read_text())


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def setup_positive_case() -> None:
    build_dir = reset_build_dir(TEST_SLUG)
    write_brief(build_dir, TEST_SLUG, "D1.1")
    write_brief(build_dir, TEST_SLUG, "D2.1")
    write_meta(build_dir, TEST_SLUG)
    write_valid_artifact(build_dir)
    write_deposit(build_dir, TEST_SLUG, "D1.1")


def setup_missing_deposit_case() -> None:
    build_dir = reset_build_dir(MISSING_SLUG)
    write_brief(build_dir, MISSING_SLUG, "D1.1")
    write_meta(build_dir, MISSING_SLUG)


def verify_positive_case(result: subprocess.CompletedProcess[str]) -> None:
    meta = read_meta(TEST_SLUG)
    producer = meta["drops"]["D1.1"]
    consumer = meta["drops"]["D2.1"]
    last_request = meta.get("last_tick_request", {})

    assert_true(result.returncode == 0, f"ring command failed: {result.stderr}")
    assert_true(producer["status"] == "complete", f"expected D1.1 complete, got {producer['status']}")
    assert_true(meta.get("active_wave") == "W2", f"expected active_wave=W2, got {meta.get('active_wave')}")
    assert_true(
        consumer["status"] == "awaiting_manual",
        f"expected D2.1 awaiting_manual, got {consumer['status']}",
    )
    assert_true(last_request.get("source") == "deposit_bell", "expected deposit_bell tick request")
    assert_true(last_request.get("drop_id") == "D1.1", f"unexpected drop_id in tick request: {last_request}")


def verify_missing_deposit_case(result: subprocess.CompletedProcess[str]) -> None:
    meta = read_meta(MISSING_SLUG)
    producer = meta["drops"]["D1.1"]

    assert_true(result.returncode != 0, "ring should fail when deposit is missing")
    assert_true(producer["status"] == "running", f"expected D1.1 to remain running, got {producer['status']}")
    assert_true("last_tick_request" not in meta, "missing-deposit case should not record tick request")


def cleanup() -> None:
    for slug in (TEST_SLUG, MISSING_SLUG):
        build_dir = BUILDS_DIR / slug
        if build_dir.exists():
            shutil.rmtree(build_dir)


def main() -> int:
    try:
        setup_positive_case()
        setup_missing_deposit_case()

        positive = run_ring(TEST_SLUG, "D1.1")
        missing = run_ring(MISSING_SLUG, "D1.1")

        verify_positive_case(positive)
        verify_missing_deposit_case(missing)

        print("PASS: deposit bell advances orchestration immediately and rejects missing deposits")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    finally:
        if "--keep" not in sys.argv:
            cleanup()


if __name__ == "__main__":
    sys.exit(main())
