#!/usr/bin/env python3
"""Zoffice control-plane helper for shadow -> cutover migration."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path("/home/workspace/Zoffice")
CONFIG_PATH = ROOT / "config" / "controller.yaml"
CONTRACT_PATH = ROOT / "contracts" / "mutual-acceptance-v2.0.0-rc1.json"
REPORTS_DIR = ROOT / "data" / "conversations"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> dict:
    with path.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML mapping: {path}")
    return data


def save_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def save_contract(contract: dict) -> None:
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2), encoding="utf-8")


def write_report(name: str, payload: dict) -> Path:
    out = REPORTS_DIR / name
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def status() -> int:
    cfg = load_yaml(CONFIG_PATH)
    contract = load_contract()
    summary = {
        "mode": cfg["controller"]["mode"],
        "legacy_disable_at_cutover": cfg["controller"]["legacy_policy"]["disable_at_cutover"],
        "legacy_disable_completed": cfg["controller"]["legacy_policy"]["disable_completed"],
        "parity_progress": {
            "required": cfg["controller"]["shadow"]["parity_samples_required"],
            "passed": cfg["controller"]["shadow"]["parity_samples_passed"],
        },
        "acceptance": {
            "producer_signed": contract["status"]["producer_signed"],
            "consumer_signed": contract["status"]["consumer_signed"],
            "mutually_accepted": contract["status"]["mutually_accepted"],
            "effective": contract["status"]["effective"],
        },
    }
    print(json.dumps(summary, indent=2))
    return 0


def record_shadow_sample(passed: bool) -> int:
    cfg = load_yaml(CONFIG_PATH)
    shadow = cfg["controller"]["shadow"]
    if shadow["status"] != "running":
        return 1
    if passed:
        shadow["parity_samples_passed"] += 1
    shadow["last_sample_at_utc"] = now_utc()
    if shadow["parity_samples_passed"] >= shadow["parity_samples_required"]:
        shadow["status"] = "ready_for_cutover"
    cfg["controller"]["mode"] = "shadow"
    save_yaml(CONFIG_PATH, cfg)
    report = {
        "event": "shadow_sample",
        "passed": passed,
        "parity_samples_passed": shadow["parity_samples_passed"],
        "parity_samples_required": shadow["parity_samples_required"],
        "shadow_status": shadow["status"],
        "recorded_at_utc": now_utc(),
    }
    write_report("zoffice-shadow-latest.json", report)
    print(json.dumps(report, indent=2))
    return 0


def promote_cutover(integrity_rebuild_percent: int) -> int:
    cfg = load_yaml(CONFIG_PATH)
    contract = load_contract()

    shadow = cfg["controller"]["shadow"]
    required = cfg["controller"]["gates"]["require_integrity_rebuild_percent"]
    if shadow["status"] != "ready_for_cutover":
        print("ERROR: shadow mode not ready_for_cutover")
        return 1
    if integrity_rebuild_percent < required:
        print(f"ERROR: integrity_rebuild_percent {integrity_rebuild_percent} < required {required}")
        return 1

    cfg["controller"]["mode"] = "cutover"
    cfg["controller"]["legacy_policy"]["disable_completed"] = True
    cfg["controller"]["acceptance"]["integrity_rebuild_percent"] = integrity_rebuild_percent
    cfg["controller"]["acceptance"]["consumer_signed"] = True
    cfg["controller"]["cutover_at_utc"] = now_utc()
    save_yaml(CONFIG_PATH, cfg)

    contract["status"]["consumer_signed"] = True
    contract["status"]["mutually_accepted"] = True
    contract["status"]["effective"] = True
    contract["required_evidence"]["actual_integrity_rebuild_percent"] = integrity_rebuild_percent
    contract["consumer_signature"]["signed_at_utc"] = now_utc()
    contract["consumer_signature"]["payload_hash"] = contract["producer_signature"]["payload_hash"]
    contract["consumer_signature"]["signature"] = (
        f"attested-by-zoputer-{integrity_rebuild_percent}-percent"
    )
    save_contract(contract)

    report = {
        "event": "cutover",
        "mode": "cutover",
        "legacy_disabled": True,
        "integrity_rebuild_percent": integrity_rebuild_percent,
        "mutually_accepted": True,
        "effective": True,
        "completed_at_utc": now_utc(),
    }
    out = write_report("zoffice-cutover-latest.json", report)
    print(json.dumps({"status": "ok", "report": str(out)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Zoffice control-plane helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")

    sh = sub.add_parser("shadow-sample")
    sh.add_argument("--passed", action="store_true")

    cut = sub.add_parser("cutover")
    cut.add_argument("--integrity-rebuild-percent", type=int, required=True)

    args = parser.parse_args()
    if args.command == "status":
        return status()
    if args.command == "shadow-sample":
        return record_shadow_sample(passed=args.passed)
    if args.command == "cutover":
        return promote_cutover(args.integrity_rebuild_percent)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
