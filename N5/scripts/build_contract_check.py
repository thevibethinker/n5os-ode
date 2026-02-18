#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required Pulse build contract artifacts.")
    parser.add_argument("slug", help="Build slug under N5/builds/")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    root = Path("/home/workspace/N5/builds") / args.slug
    plan_path = root / "PLAN.md"
    meta_path = root / "meta.json"
    drops_dir = root / "drops"

    checks = {
        "build_folder_exists": root.exists() and root.is_dir(),
        "plan_exists": plan_path.exists() and plan_path.is_file(),
        "meta_exists": meta_path.exists() and meta_path.is_file(),
        "drops_dir_exists": drops_dir.exists() and drops_dir.is_dir(),
        "drops_present": any(drops_dir.glob("*.md")) if drops_dir.exists() else False,
        "meta_has_drops": False,
        "meta_has_waves_or_currents": False,
    }

    if checks["meta_exists"]:
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            drops = meta.get("drops", {})
            checks["meta_has_drops"] = isinstance(drops, dict) and len(drops) > 0
            checks["meta_has_waves_or_currents"] = (
                (isinstance(meta.get("waves"), dict) and len(meta.get("waves", {})) > 0)
                or ("currents" in meta)
                or ("current_stream" in meta and "total_streams" in meta)
            )
        except Exception:
            checks["meta_has_drops"] = False
            checks["meta_has_waves_or_currents"] = False

    passed = all(checks.values())
    payload = {"slug": args.slug, "passed": passed, "checks": checks}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Build contract check for '{args.slug}': {'PASS' if passed else 'FAIL'}")
        for key, value in checks.items():
            print(f"- {key}: {'ok' if value else 'missing'}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
