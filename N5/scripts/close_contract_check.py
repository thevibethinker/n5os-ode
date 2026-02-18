#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


REQUIRED_KEYS = [
    "title_generated",
    "artifacts_itemized",
    "build_folder_closed",
    "close_artifact_written",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required close contract checklist fields.")
    parser.add_argument(
        "--checklist",
        required=True,
        help="Path to close checklist JSON with required boolean keys.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    checklist_path = Path(args.checklist)
    checks = {
        "checklist_exists": checklist_path.exists() and checklist_path.is_file(),
        "json_parseable": False,
    }
    values = {}

    if checks["checklist_exists"]:
        try:
            values = json.loads(checklist_path.read_text(encoding="utf-8"))
            checks["json_parseable"] = isinstance(values, dict)
        except Exception:
            checks["json_parseable"] = False

    for key in REQUIRED_KEYS:
        checks[key] = bool(values.get(key, False)) if checks["json_parseable"] else False

    passed = all(checks.values())
    payload = {
        "checklist": str(checklist_path),
        "passed": passed,
        "checks": checks,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Close contract check: {'PASS' if passed else 'FAIL'}")
        for key, value in checks.items():
            print(f"- {key}: {'ok' if value else 'missing'}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
