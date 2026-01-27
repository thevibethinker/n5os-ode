#!/usr/bin/env python3
"""
Aggregate findings from tidying swarm Drops.

Usage:
    python3 aggregator.py <slug>
    python3 aggregator.py pulse-v2 --json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"


def load_config() -> dict:
    """Load Pulse v2 config."""
    config_path = WORKSPACE / "Skills" / "pulse" / "config" / "pulse_v2_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def get_tidying_drop_ids() -> list[str]:
    """Get the list of tidying drop types from config."""
    config = load_config()
    return config.get("tidying_swarm", {}).get("drops", [
        "integration_test", "reference_check", "stub_scan", "dedup", "cleanup"
    ])


def load_tidying_deposits(slug: str) -> dict[str, dict]:
    """Load all tidying deposits for a build."""
    deposits_dir = BUILDS_DIR / slug / "deposits"
    tidying_types = get_tidying_drop_ids()
    
    results = {}
    for deposit_file in deposits_dir.glob("*.json"):
        if deposit_file.stem.endswith("_filter") or deposit_file.stem.endswith("_validation"):
            continue
        
        drop_id = deposit_file.stem
        
        if any(t in drop_id.lower() for t in tidying_types):
            with open(deposit_file) as f:
                results[drop_id] = json.load(f)
    
    for tidying_type in tidying_types:
        pattern = f"T*.{tidying_type}*.json"
        for deposit_file in deposits_dir.glob(f"T*-{tidying_type}*.json"):
            if deposit_file.stem not in results:
                with open(deposit_file) as f:
                    results[deposit_file.stem] = json.load(f)
    
    return results


def parse_deposit_findings(deposit: dict) -> dict:
    """Extract findings from a deposit's output field."""
    findings = {
        "critical": [],
        "warning": [],
        "info": [],
        "auto_fixable": []
    }
    
    if "findings" in deposit:
        for f in deposit.get("findings", []):
            severity = f.get("severity", "info").lower()
            if severity in ["critical", "error", "high"]:
                findings["critical"].append(f)
            elif severity in ["warning", "medium"]:
                findings["warning"].append(f)
            else:
                findings["info"].append(f)
    
    for f in deposit.get("auto_fixable", []):
        findings["auto_fixable"].append(f)
    
    for f in deposit.get("requires_review", []):
        severity = f.get("severity", "warning").lower()
        if severity in ["critical", "high"]:
            findings["critical"].append(f)
        else:
            findings["warning"].append(f)
    
    output = deposit.get("output", "")
    if isinstance(output, str):
        try:
            parsed = json.loads(output)
            if isinstance(parsed, dict):
                nested = parse_deposit_findings(parsed)
                for k, v in nested.items():
                    findings[k].extend(v)
        except json.JSONDecodeError:
            pass
    
    return findings


def aggregate_findings(slug: str) -> dict:
    """
    Read all tidying deposits and aggregate.
    
    Returns:
    {
        "critical": [...],
        "warning": [...],
        "info": [...],
        "auto_fixable": [...],
        "health_score": 0.0-1.0,
        "deposits_found": int,
        "deposits_expected": int,
        "by_check": { "check_name": {...}, ... }
    }
    """
    deposits = load_tidying_deposits(slug)
    expected_count = len(get_tidying_drop_ids())
    
    aggregated = {
        "critical": [],
        "warning": [],
        "info": [],
        "auto_fixable": [],
        "deposits_found": len(deposits),
        "deposits_expected": expected_count,
        "by_check": {}
    }
    
    for drop_id, deposit in deposits.items():
        check_findings = parse_deposit_findings(deposit)
        
        for f in check_findings["critical"]:
            f["source_drop"] = drop_id
            aggregated["critical"].append(f)
        for f in check_findings["warning"]:
            f["source_drop"] = drop_id
            aggregated["warning"].append(f)
        for f in check_findings["info"]:
            f["source_drop"] = drop_id
            aggregated["info"].append(f)
        for f in check_findings["auto_fixable"]:
            f["source_drop"] = drop_id
            aggregated["auto_fixable"].append(f)
        
        aggregated["by_check"][drop_id] = {
            "critical": len(check_findings["critical"]),
            "warning": len(check_findings["warning"]),
            "info": len(check_findings["info"]),
            "auto_fixable": len(check_findings["auto_fixable"])
        }
    
    aggregated["health_score"] = compute_health_score(aggregated)
    
    return aggregated


def compute_health_score(findings: dict) -> float:
    """
    Compute build health score.
    
    - 1.0 = no issues
    - <0.5 = critical issues present
    - 0.0 = build blocked
    
    Scoring:
    - Critical: -0.2 each (capped at -0.6)
    - Warning: -0.05 each (capped at -0.25)
    - Auto-fixable don't reduce score (can be fixed)
    - Missing deposits: -0.1 per missing
    """
    score = 1.0
    
    critical_count = len(findings.get("critical", []))
    critical_penalty = min(critical_count * 0.2, 0.6)
    score -= critical_penalty
    
    warning_count = len(findings.get("warning", []))
    warning_penalty = min(warning_count * 0.05, 0.25)
    score -= warning_penalty
    
    expected = findings.get("deposits_expected", 5)
    found = findings.get("deposits_found", 0)
    missing = max(0, expected - found)
    score -= missing * 0.1
    
    return max(0.0, round(score, 2))


def print_summary(findings: dict):
    """Print human-readable summary."""
    print(f"\n{'='*60}")
    print("TIDYING SWARM SUMMARY")
    print(f"{'='*60}")
    print(f"Deposits: {findings['deposits_found']}/{findings['deposits_expected']}")
    print(f"Health Score: {findings['health_score']:.2f}")
    print()
    
    print(f"Critical Issues: {len(findings['critical'])}")
    for f in findings['critical'][:5]:
        desc = f.get('issue', f.get('error', f.get('description', 'Unknown')))[:60]
        print(f"  ⛔ {desc}")
    
    print(f"\nWarnings: {len(findings['warning'])}")
    for f in findings['warning'][:5]:
        desc = f.get('issue', f.get('error', f.get('description', 'Unknown')))[:60]
        print(f"  ⚠️  {desc}")
    
    print(f"\nAuto-Fixable: {len(findings['auto_fixable'])}")
    
    print(f"\nBy Check:")
    for check, counts in findings.get('by_check', {}).items():
        status = "✅" if counts['critical'] == 0 else "❌"
        print(f"  {status} {check}: {counts['critical']}C/{counts['warning']}W/{counts['info']}I")
    
    print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Aggregate tidying swarm findings")
    parser.add_argument("slug", help="Build slug")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()
    
    if not (BUILDS_DIR / args.slug).exists():
        print(f"Error: Build not found: {args.slug}", file=sys.stderr)
        sys.exit(1)
    
    findings = aggregate_findings(args.slug)
    
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print_summary(findings)
        print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
