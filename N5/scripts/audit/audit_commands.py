#!/usr/bin/env python3
"""Audit N5 command files for completeness and proper structure."""

import os
import json
from pathlib import Path

COMMANDS_DIR = Path("/home/workspace/N5/commands")

def check_file(filepath):
    """Check a single command file for issues."""
    issues = []
    filename = filepath.name
    
    # Check if file is empty
    size = filepath.stat().st_size
    if size == 0:
        issues.append("EMPTY FILE (0 bytes)")
        return issues
    
    # Read content
    try:
        content = filepath.read_text()
    except Exception as e:
        issues.append(f"ERROR READING: {e}")
        return issues
    
    # Check for frontmatter
    if not content.startswith("---"):
        issues.append("MISSING FRONTMATTER")
    else:
        # Check if frontmatter is complete
        parts = content.split("---", 2)
        if len(parts) < 3:
            issues.append("INCOMPLETE FRONTMATTER")
        else:
            frontmatter = parts[1]
            required_fields = ["date", "checksum", "tags", "category", "priority"]
            for field in required_fields:
                if field not in frontmatter:
                    issues.append(f"MISSING FIELD: {field}")
    
    # Check for basic sections
    required_sections = ["# `", "Summary:", "## Inputs", "## Side Effects"]
    for section in required_sections:
        if section not in content:
            issues.append(f"MISSING SECTION: {section}")
    
    # Check if file is suspiciously small (less than 500 bytes and not a stub)
    if size < 500 and "MISSING FRONTMATTER" in issues:
        issues.append(f"SUSPICIOUSLY SMALL ({size} bytes)")
    
    return issues

def main():
    """Audit all command files."""
    print("=" * 80)
    print("N5 COMMAND FILES AUDIT")
    print("=" * 80)
    print()
    
    # Get all .md files
    md_files = sorted(COMMANDS_DIR.glob("*.md"))
    
    total = len(md_files)
    empty = []
    missing_frontmatter = []
    incomplete = []
    ok = []
    
    for filepath in md_files:
        issues = check_file(filepath)
        
        if issues:
            if "EMPTY FILE" in issues[0]:
                empty.append(filepath.name)
            elif any("MISSING FRONTMATTER" in i for i in issues):
                missing_frontmatter.append((filepath.name, issues))
            else:
                incomplete.append((filepath.name, issues))
        else:
            ok.append(filepath.name)
    
    # Report
    print(f"📊 SUMMARY:")
    print(f"  Total files: {total}")
    print(f"  ✅ OK: {len(ok)}")
    print(f"  ⚠️  Issues: {len(empty) + len(missing_frontmatter) + len(incomplete)}")
    print()
    
    if empty:
        print(f"🚨 EMPTY FILES ({len(empty)}):")
        for f in empty:
            print(f"  - {f}")
        print()
    
    if missing_frontmatter:
        print(f"⚠️  MISSING FRONTMATTER ({len(missing_frontmatter)}):")
        for f, issues in missing_frontmatter:
            print(f"  - {f}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"      • {issue}")
        print()
    
    if incomplete:
        print(f"⚠️  INCOMPLETE STRUCTURE ({len(incomplete)}):")
        for f, issues in incomplete:
            print(f"  - {f}")
            for issue in issues[:3]:
                print(f"      • {issue}")
        print()
    
    # Create detailed JSON report
    report = {
        "total": total,
        "ok": len(ok),
        "issues": len(empty) + len(missing_frontmatter) + len(incomplete),
        "empty": empty,
        "missing_frontmatter": [{"file": f, "issues": i} for f, i in missing_frontmatter],
        "incomplete": [{"file": f, "issues": i} for f, i in incomplete],
        "ok_files": ok
    }
    
    report_path = Path("/home/.z/workspaces/con_tY3K512yUo3sG7Iv/audit_report.json")
    report_path.write_text(json.dumps(report, indent=2))
    print(f"📄 Detailed report saved to: {report_path}")
    
    return len(empty) + len(missing_frontmatter) + len(incomplete)

if __name__ == "__main__":
    exit(main())
