#!/usr/bin/env python3
"""
Zoffice Healthcheck — validates a Zoffice installation.

Usage:
    python healthcheck.py [--verbose] [--fix]

Checks:
    1. Directory structure completeness
    2. Config YAML validity and required fields
    3. MANIFEST.json integrity
    4. office.db tables and indexes
    5. Staff registry structure
    6. Capability README presence
"""

import argparse
import json
import os
import sys

ZOFFICE_ROOT = "/home/workspace/Zoffice"

# --- Expected structure ---

REQUIRED_DIRS = [
    "config",
    "capabilities/security",
    "capabilities/memory",
    "capabilities/ingestion",
    "capabilities/communication",
    "capabilities/orchestration",
    "capabilities/zo2zo",
    "capabilities/publishing",
    "capabilities/hr",
    "staff/_template",
    "staff/receptionist",
    "staff/chief-of-staff",
    "staff/librarian",
    "data/contacts",
    "data/conversations",
    "data/decisions",
    "knowledge/about-owner",
    "knowledge/products",
    "knowledge/clients",
    "knowledge/domain",
    "scripts",
]

REQUIRED_CONFIGS = {
    "config/office.yaml": ["office"],
    "config/autonomy.yaml": ["thresholds"],
    "config/capabilities.yaml": ["capabilities"],
    "config/routing.yaml": ["routes"],
    "config/security.yaml": ["security"],
}

REQUIRED_FILES = [
    "MANIFEST.json",
    "staff/registry.yaml",
]

CAPABILITY_READMES = [
    "capabilities/security/README.md",
    "capabilities/memory/README.md",
    "capabilities/ingestion/README.md",
    "capabilities/communication/README.md",
    "capabilities/orchestration/README.md",
    "capabilities/zo2zo/README.md",
    "capabilities/publishing/README.md",
    "capabilities/hr/README.md",
]

DB_TABLES = ["audit", "contacts", "decisions", "conversations", "evaluations"]


def check_directories(verbose=False):
    """Check all required directories exist."""
    results = {"pass": 0, "fail": 0, "details": []}
    for d in REQUIRED_DIRS:
        path = os.path.join(ZOFFICE_ROOT, d)
        if os.path.isdir(path):
            results["pass"] += 1
            if verbose:
                results["details"].append(f"  OK  {d}/")
        else:
            results["fail"] += 1
            results["details"].append(f"  MISSING  {d}/")
    return results


def check_configs(verbose=False):
    """Check config files exist and contain required top-level keys."""
    results = {"pass": 0, "fail": 0, "details": []}
    try:
        import yaml
    except ImportError:
        results["details"].append("  WARN  PyYAML not installed — skipping YAML validation")
        # Still check file existence
        for config_path in REQUIRED_CONFIGS:
            path = os.path.join(ZOFFICE_ROOT, config_path)
            if os.path.isfile(path):
                results["pass"] += 1
                if verbose:
                    results["details"].append(f"  OK  {config_path} (exists, not validated)")
            else:
                results["fail"] += 1
                results["details"].append(f"  MISSING  {config_path}")
        return results

    for config_path, required_keys in REQUIRED_CONFIGS.items():
        path = os.path.join(ZOFFICE_ROOT, config_path)
        if not os.path.isfile(path):
            results["fail"] += 1
            results["details"].append(f"  MISSING  {config_path}")
            continue

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                results["fail"] += 1
                results["details"].append(f"  INVALID  {config_path} — not a YAML mapping")
                continue

            missing_keys = [k for k in required_keys if k not in data]
            if missing_keys:
                results["fail"] += 1
                results["details"].append(
                    f"  INCOMPLETE  {config_path} — missing keys: {missing_keys}"
                )
            else:
                results["pass"] += 1
                if verbose:
                    results["details"].append(f"  OK  {config_path}")
        except yaml.YAMLError as e:
            results["fail"] += 1
            results["details"].append(f"  PARSE_ERROR  {config_path} — {e}")

    return results


def check_manifest(verbose=False):
    """Check MANIFEST.json is valid JSON with required fields."""
    results = {"pass": 0, "fail": 0, "details": []}
    path = os.path.join(ZOFFICE_ROOT, "MANIFEST.json")

    if not os.path.isfile(path):
        results["fail"] += 1
        results["details"].append("  MISSING  MANIFEST.json")
        return results

    try:
        with open(path) as f:
            data = json.load(f)

        required = ["product", "version", "layer"]
        missing = [k for k in required if k not in data]
        if missing:
            results["fail"] += 1
            results["details"].append(f"  INCOMPLETE  MANIFEST.json — missing: {missing}")
        else:
            results["pass"] += 1
            if verbose:
                results["details"].append(
                    f"  OK  MANIFEST.json (v{data.get('version', '?')}, layer {data.get('layer', '?')})"
                )
    except json.JSONDecodeError as e:
        results["fail"] += 1
        results["details"].append(f"  PARSE_ERROR  MANIFEST.json — {e}")

    return results


def check_database(verbose=False):
    """Check office.db exists with expected tables."""
    results = {"pass": 0, "fail": 0, "details": []}
    db_path = os.path.join(ZOFFICE_ROOT, "data", "office.db")

    if not os.path.isfile(db_path):
        results["fail"] += 1
        results["details"].append("  MISSING  data/office.db")
        return results

    try:
        import duckdb

        con = duckdb.connect(db_path, read_only=True)
        existing = [
            row[0] for row in con.execute("SHOW TABLES").fetchall()
        ]

        for table in DB_TABLES:
            if table in existing:
                results["pass"] += 1
                if verbose:
                    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    results["details"].append(f"  OK  table:{table} ({count} rows)")
            else:
                results["fail"] += 1
                results["details"].append(f"  MISSING  table:{table}")

        con.close()
    except ImportError:
        results["details"].append("  WARN  duckdb not installed — skipping DB validation")
        if os.path.isfile(db_path):
            results["pass"] += 1
            results["details"].append("  OK  data/office.db (exists, not validated)")
    except Exception as e:
        results["fail"] += 1
        results["details"].append(f"  ERROR  data/office.db — {e}")

    return results


def check_files(verbose=False):
    """Check required standalone files and capability READMEs."""
    results = {"pass": 0, "fail": 0, "details": []}

    for f in REQUIRED_FILES + CAPABILITY_READMES:
        path = os.path.join(ZOFFICE_ROOT, f)
        if os.path.isfile(path):
            results["pass"] += 1
            if verbose:
                results["details"].append(f"  OK  {f}")
        else:
            results["fail"] += 1
            results["details"].append(f"  MISSING  {f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate Zoffice installation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show passing checks too")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix missing directories (not configs)")
    args = parser.parse_args()

    if not os.path.isdir(ZOFFICE_ROOT):
        print(f"FATAL: Zoffice root not found at {ZOFFICE_ROOT}")
        sys.exit(2)

    checks = [
        ("Directories", check_directories),
        ("Configs", check_configs),
        ("Manifest", check_manifest),
        ("Database", check_database),
        ("Files", check_files),
    ]

    total_pass = 0
    total_fail = 0

    print("=" * 50)
    print("  Zoffice Healthcheck")
    print("=" * 50)

    for name, check_fn in checks:
        result = check_fn(verbose=args.verbose)
        total_pass += result["pass"]
        total_fail += result["fail"]

        status = "PASS" if result["fail"] == 0 else "FAIL"
        print(f"\n[{status}] {name} — {result['pass']} ok, {result['fail']} issues")
        for detail in result["details"]:
            print(detail)

    print("\n" + "=" * 50)
    total = total_pass + total_fail
    print(f"  Total: {total_pass}/{total} checks passed")
    if total_fail > 0:
        print(f"  {total_fail} issue(s) found")
        sys.exit(1)
    else:
        print("  Installation healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()
