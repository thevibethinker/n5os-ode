#!/usr/bin/env python3
"""
SESSION_STATE Telemetry Collector

Collects diagnostic data about SESSION_STATE initialization for validation testing.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import sqlite3


def collect_telemetry(convo_id: str) -> dict:
    """
    Collect comprehensive telemetry about SESSION_STATE initialization.
    
    Returns telemetry dict with all diagnostic data.
    """
    telemetry = {
        "test_timestamp": datetime.now(timezone.utc).isoformat(),
        "conversation_id": convo_id,
        "version": "1.0",
        "checks": {}
    }
    
    workspace_path = Path(f"/home/.z/workspaces/{convo_id}")
    state_file = workspace_path / "SESSION_STATE.md"
    
    # Check 1: Workspace exists
    telemetry["checks"]["workspace_exists"] = {
        "pass": workspace_path.exists(),
        "path": str(workspace_path)
    }
    
    # Check 2: SESSION_STATE.md exists
    telemetry["checks"]["state_file_exists"] = {
        "pass": state_file.exists(),
        "path": str(state_file)
    }
    
    if state_file.exists():
        # Check 3: File is readable and non-empty
        try:
            content = state_file.read_text()
            telemetry["checks"]["state_file_readable"] = {
                "pass": True,
                "size_bytes": len(content)
            }
            
            # Check 4: Has YAML frontmatter
            has_frontmatter = content.startswith("---")
            telemetry["checks"]["has_frontmatter"] = {
                "pass": has_frontmatter
            }
            
            # Check 5: Extract frontmatter data
            if has_frontmatter:
                try:
                    lines = content.split("\n")
                    fm_lines = []
                    in_fm = False
                    for line in lines[1:]:  # Skip first ---
                        if line.strip() == "---":
                            break
                        fm_lines.append(line)
                    
                    frontmatter = {}
                    for line in fm_lines:
                        if ":" in line:
                            key, val = line.split(":", 1)
                            frontmatter[key.strip()] = val.strip()
                    
                    telemetry["frontmatter"] = frontmatter
                    
                    # Validate required fields
                    required_fields = ["conversation_id", "type", "status", "created", "last_updated"]
                    telemetry["checks"]["has_required_fields"] = {
                        "pass": all(f in frontmatter for f in required_fields),
                        "missing": [f for f in required_fields if f not in frontmatter]
                    }
                    
                    # Check 6: Type is valid
                    valid_types = ["build", "research", "discussion", "planning"]
                    telemetry["checks"]["valid_type"] = {
                        "pass": frontmatter.get("type") in valid_types,
                        "value": frontmatter.get("type")
                    }
                    
                except Exception as e:
                    telemetry["checks"]["frontmatter_parse"] = {
                        "pass": False,
                        "error": str(e)
                    }
            
            # Check 7: Has metadata section
            telemetry["checks"]["has_metadata_section"] = {
                "pass": "## Metadata" in content
            }
            
            # Check 8: Has required sections
            required_sections = ["Progress", "Covered", "Topics", "Artifacts"]
            telemetry["checks"]["has_required_sections"] = {
                "pass": all(f"## {s}" in content or f"**{s}:**" in content for s in required_sections),
                "missing": [s for s in required_sections if f"## {s}" not in content and f"**{s}:**" not in content]
            }
            
        except Exception as e:
            telemetry["checks"]["state_file_readable"] = {
                "pass": False,
                "error": str(e)
            }
    
    # Check 9: DB sync status
    db_path = Path("/home/workspace/N5/data/conversations.db")
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, type, status, created_at FROM conversations WHERE id=?",
                (convo_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            telemetry["checks"]["db_record_exists"] = {
                "pass": row is not None
            }
            
            if row:
                telemetry["db_record"] = dict(row)
                
                # Check 10: DB matches SESSION_STATE
                if "frontmatter" in telemetry:
                    type_match = row["type"] == telemetry["frontmatter"].get("type")
                    status_match = row["status"] == telemetry["frontmatter"].get("status")
                    
                    telemetry["checks"]["db_sync_accurate"] = {
                        "pass": type_match and status_match,
                        "type_match": type_match,
                        "status_match": status_match
                    }
        except Exception as e:
            telemetry["checks"]["db_check"] = {
                "pass": False,
                "error": str(e)
            }
    
    # Summary score
    total_checks = len([v for v in telemetry["checks"].values() if isinstance(v, dict) and "pass" in v])
    passed_checks = len([v for v in telemetry["checks"].values() if isinstance(v, dict) and v.get("pass") == True])
    
    telemetry["summary"] = {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "success_rate": round(passed_checks / total_checks * 100, 1) if total_checks > 0 else 0,
        "overall_pass": passed_checks == total_checks
    }
    
    return telemetry


def format_telemetry_report(telemetry: dict) -> str:
    """Format telemetry as readable report."""
    lines = []
    lines.append("="*70)
    lines.append("SESSION_STATE TELEMETRY REPORT")
    lines.append("="*70)
    lines.append(f"Conversation: {telemetry['conversation_id']}")
    lines.append(f"Test Time: {telemetry['test_timestamp']}")
    lines.append("")
    
    lines.append("CHECKS:")
    for check_name, check_data in telemetry["checks"].items():
        if isinstance(check_data, dict) and "pass" in check_data:
            status = "✅ PASS" if check_data["pass"] else "❌ FAIL"
            lines.append(f"  {status} - {check_name}")
            if not check_data["pass"] and "error" in check_data:
                lines.append(f"         Error: {check_data['error']}")
            if "missing" in check_data and check_data["missing"]:
                lines.append(f"         Missing: {check_data['missing']}")
    
    lines.append("")
    lines.append("SUMMARY:")
    summary = telemetry["summary"]
    lines.append(f"  Total Checks: {summary['total_checks']}")
    lines.append(f"  Passed: {summary['passed_checks']}")
    lines.append(f"  Success Rate: {summary['success_rate']}%")
    lines.append(f"  Overall: {'✅ PASS' if summary['overall_pass'] else '❌ FAIL'}")
    
    if "frontmatter" in telemetry:
        lines.append("")
        lines.append("FRONTMATTER DATA:")
        for key, val in telemetry["frontmatter"].items():
            lines.append(f"  {key}: {val}")
    
    lines.append("="*70)
    
    return "\n".join(lines)


def save_telemetry(telemetry: dict, output_dir: Path = None):
    """Save telemetry to JSON file."""
    if output_dir is None:
        output_dir = Path("/home/workspace/N5/tests/telemetry")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{telemetry['conversation_id']}_telemetry.json"
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    return output_path


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 session_state_telemetry.py <conversation_id>")
        sys.exit(1)
    
    convo_id = sys.argv[1]
    
    # Collect telemetry
    telemetry = collect_telemetry(convo_id)
    
    # Save to file
    output_path = save_telemetry(telemetry)
    
    # Print report
    report = format_telemetry_report(telemetry)
    print(report)
    print()
    print(f"Telemetry saved to: {output_path}")
    
    # Exit with status
    sys.exit(0 if telemetry["summary"]["overall_pass"] else 1)


if __name__ == "__main__":
    main()

