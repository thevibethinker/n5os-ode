#!/usr/bin/env python3
"""
Dispatch auto-fixes or escalate to V.

Usage:
    python3 fix_dispatcher.py <slug>
    python3 fix_dispatcher.py <slug> --dry-run
    python3 fix_dispatcher.py <slug> --escalate-only
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import aiohttp

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
SKILLS_DIR = WORKSPACE / "Skills" / "pulse"
ZO_API_URL = "https://api.zo.computer/zo/ask"


def load_config() -> dict:
    """Load Pulse v2 config."""
    config_path = SKILLS_DIR / "config" / "pulse_v2_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {"tidying_swarm": {"auto_fix_threshold": 0.9}}


def should_auto_fix(finding: dict, threshold: float) -> bool:
    """
    Determine if a finding should be auto-fixed.
    
    Conditions:
    - Finding has auto_fixable=true or is in auto_fixable list
    - Confidence >= threshold
    - Fix script/action is specified
    """
    if not finding.get("auto_fixable", False) and finding.get("confidence", 0) < threshold:
        return False
    
    if finding.get("fix_action") or finding.get("fix_script"):
        return True
    
    safe_patterns = [
        "unused import",
        "debug print",
        "console.log",
        "trailing whitespace",
        "unused variable"
    ]
    description = finding.get("description", finding.get("issue", "")).lower()
    return any(p in description for p in safe_patterns)


def categorize_findings(findings: dict, threshold: float) -> tuple[list, list]:
    """
    Categorize findings into auto-fixable and escalation.
    
    Returns: (auto_fix_list, escalate_list)
    """
    to_fix = []
    to_escalate = []
    
    for f in findings.get("auto_fixable", []):
        confidence = f.get("confidence", 1.0)
        if confidence >= threshold and should_auto_fix(f, threshold):
            to_fix.append(f)
        else:
            to_escalate.append({
                **f,
                "reason": f"Confidence {confidence:.2f} < threshold {threshold:.2f}"
            })
    
    for f in findings.get("critical", []):
        to_escalate.append({**f, "severity": "critical"})
    
    for f in findings.get("warning", []):
        if should_auto_fix(f, threshold):
            to_fix.append(f)
        else:
            to_escalate.append({**f, "severity": "warning"})
    
    return to_fix, to_escalate


def generate_fix_brief(slug: str, finding: dict) -> str:
    """Generate a Drop brief for auto-fixing a finding."""
    source = finding.get("source_drop", "unknown")
    file_path = finding.get("file_path", finding.get("path", "unknown"))
    issue = finding.get("issue", finding.get("description", "No description"))
    fix_action = finding.get("fix_action", "")
    
    return f"""---
build_slug: {slug}
drop_type: fix
source_hygiene: {source}
auto_generated: true
---

# Auto-Fix: {issue[:50]}

## Context
- **Source**: {source}
- **File**: {file_path}
- **Issue**: {issue}

## Task
Fix this issue automatically. The following action was suggested:

{fix_action if fix_action else "Apply the standard fix for this issue type."}

## Constraints
- Make minimal changes
- Do not alter business logic
- If uncertain, escalate rather than fix

## Deposit Schema
```json
{{
  "fixed": true|false,
  "file_path": "{file_path}",
  "changes_made": "description of changes",
  "escalated": true|false,
  "escalation_reason": null|"reason"
}}
```
"""


def generate_escalation_report(findings: list, slug: str) -> str:
    """Generate SMS-friendly escalation summary."""
    if not findings:
        return f"[PULSE] {slug}: Tidying complete. No escalations needed."
    
    critical = [f for f in findings if f.get("severity") == "critical"]
    warnings = [f for f in findings if f.get("severity") != "critical"]
    
    lines = [f"[PULSE] {slug} TIDYING ESCALATION"]
    
    if critical:
        lines.append(f"⛔ {len(critical)} critical:")
        for f in critical[:2]:
            issue = f.get("issue", f.get("description", "Unknown"))[:40]
            lines.append(f"  • {issue}")
    
    if warnings:
        lines.append(f"⚠️ {len(warnings)} warnings needing review")
    
    lines.append("Reply APPROVE to proceed, REVIEW to see details, or STOP.")
    
    return "\n".join(lines)


async def send_sms(message: str) -> bool:
    """Send SMS via Zo API."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print(f"[SMS-DRY] Would send: {message}")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                ZO_API_URL,
                headers={
                    "authorization": token,
                    "content-type": "application/json"
                },
                json={
                    "input": f"Send this SMS to V immediately: {message}"
                }
            ) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"[SMS ERROR] {e}")
            return False


async def spawn_fix_drop(slug: str, brief: str) -> Optional[str]:
    """Spawn a fix Drop via Zo API. Returns conversation ID or None."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print("[FIX] No API token - would spawn fix Drop")
        return None
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                ZO_API_URL,
                headers={
                    "authorization": token,
                    "content-type": "application/json"
                },
                json={"input": brief}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("conversation_id", "spawned")
                return None
        except Exception as e:
            print(f"[FIX SPAWN ERROR] {e}")
            return None


async def dispatch(slug: str, findings: dict, dry_run: bool = False) -> dict:
    """
    For each finding:
    - If auto_fixable AND confidence >= threshold: spawn fix Drop
    - Else: add to escalation report
    
    Returns dispatch results.
    """
    config = load_config()
    threshold = config.get("tidying_swarm", {}).get("auto_fix_threshold", 0.9)
    
    to_fix, to_escalate = categorize_findings(findings, threshold)
    
    result = {
        "slug": slug,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threshold": threshold,
        "to_fix": len(to_fix),
        "to_escalate": len(to_escalate),
        "fixes_spawned": [],
        "escalation_sent": False,
        "dry_run": dry_run
    }
    
    if dry_run:
        print(f"\n[DRY RUN] Would dispatch {len(to_fix)} fixes, {len(to_escalate)} escalations")
        for f in to_fix:
            print(f"  FIX: {f.get('issue', f.get('description', 'Unknown'))[:60]}")
        for f in to_escalate:
            print(f"  ESCALATE: {f.get('issue', f.get('description', 'Unknown'))[:60]}")
        return result
    
    for f in to_fix:
        brief = generate_fix_brief(slug, f)
        convo_id = await spawn_fix_drop(slug, brief)
        if convo_id:
            result["fixes_spawned"].append({
                "finding": f.get("issue", "unknown")[:50],
                "conversation_id": convo_id
            })
            print(f"[FIX SPAWNED] {f.get('issue', 'unknown')[:50]}")
    
    if to_escalate:
        report = generate_escalation_report(to_escalate, slug)
        await send_sms(report)
        result["escalation_sent"] = True
        result["escalation_report"] = report
        print(f"[ESCALATED] {len(to_escalate)} findings sent to V")
    
    dispatch_path = BUILDS_DIR / slug / "DISPATCH_RESULT.json"
    with open(dispatch_path, "w") as f:
        json.dump(result, f, indent=2)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Dispatch fixes or escalate findings")
    parser.add_argument("slug", help="Build slug")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--escalate-only", action="store_true", help="Skip auto-fixes, escalate all")
    parser.add_argument("--findings-json", help="Path to aggregated findings JSON (default: run aggregator)")
    args = parser.parse_args()
    
    if not (BUILDS_DIR / args.slug).exists():
        print(f"Error: Build not found: {args.slug}", file=sys.stderr)
        sys.exit(1)
    
    if args.findings_json:
        with open(args.findings_json) as f:
            findings = json.load(f)
    else:
        from aggregator import aggregate_findings
        findings = aggregate_findings(args.slug)
    
    if args.escalate_only:
        findings["auto_fixable"] = []
        all_findings = findings.get("critical", []) + findings.get("warning", [])
        for f in all_findings:
            f["auto_fixable"] = False
    
    result = asyncio.run(dispatch(args.slug, findings, dry_run=args.dry_run))
    
    print(f"\n[DISPATCH COMPLETE]")
    print(f"  Fixes spawned: {len(result.get('fixes_spawned', []))}")
    print(f"  Escalation sent: {result.get('escalation_sent', False)}")


if __name__ == "__main__":
    main()
