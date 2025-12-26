#!/usr/bin/env python3
"""
One-off Backfill Script: Generate FOLLOW_UP_EMAIL.md for Week-of folders

This is a diagnostic/listing script that identifies meetings needing follow-up emails.
Actual email generation should be done by MG-5 or manually using the Follow-Up Email Generator prompt.

Usage:
    python3 backfill_followup_emails.py             # List meetings needing backfill
    python3 backfill_followup_emails.py --json      # Output JSON for further processing
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

MEETINGS = Path("/home/workspace/Personal/Meetings")

def is_internal_meeting(folder_path: Path) -> bool:
    """Check if meeting appears to be internal-only (no follow-up needed)."""
    name = folder_path.name.lower()
    internal_signals = [
        "logan",
        "ilya",
        "tiff",
        "internal",
        "standup",
        "daily",
        "team",
        "sync",
        "1on1",
        "oneononea"
    ]
    
    # Check if name suggests internal meeting
    for signal in internal_signals:
        if signal in name and not any(ext in name for ext in ["client", "external", "demo", "pitch"]):
            # Double-check by looking for external signals
            external_signals = ["x-vrijen", "x-careerspan", "advisor", "investor", "vc", "partner"]
            if not any(ext in name for ext in external_signals):
                return True
    
    # Check manifest for meeting_type if available
    manifest_path = folder_path / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                data = json.load(f)
                meeting_type = data.get("meeting_type", "").lower()
                if meeting_type in ["internal", "team", "standup"]:
                    return True
        except:
            pass
    
    return False

def has_external_stakeholders(folder_path: Path) -> bool:
    """Check if meeting has external stakeholders from B26 or B03."""
    # Check B26 for participant info
    b26_path = folder_path / "B26_MEETING_METADATA.md"
    if b26_path.exists():
        try:
            content = b26_path.read_text()
            # Look for external participants
            if "@careerspan" not in content.lower() and "@theapply" not in content.lower():
                return True
            # Check for mixed company domains
            if "@" in content:
                return True
        except:
            pass
    
    # Check stakeholder intelligence
    b03_path = folder_path / "B03_STAKEHOLDER_INTELLIGENCE.md"
    if not b03_path.exists():
        b03_path = folder_path / "B08_STAKEHOLDER_INTELLIGENCE.md"
    
    if b03_path.exists():
        try:
            content = b03_path.read_text()
            # External stakeholders usually have org names
            if any(term in content.lower() for term in ["company:", "organization:", "ceo", "founder", "investor", "partner"]):
                return True
        except:
            pass
    
    return False

def has_deliverables(folder_path: Path) -> bool:
    """Check if meeting has deliverables from B25 or B05."""
    for block_name in ["B25_DELIVERABLES.md", "B05_ACTION_ITEMS.md", "B02_COMMITMENTS.md"]:
        block_path = folder_path / block_name
        if block_path.exists():
            try:
                content = block_path.read_text()
                # Non-empty deliverables file with actual content
                lines = [l for l in content.split('\n') if l.strip() and not l.startswith('#')]
                if len(lines) > 2:  # More than just headers
                    return True
            except:
                pass
    return False

def scan_week_folders():
    """Scan all Week-of folders for meetings needing follow-up emails."""
    results = {
        "needs_followup": [],
        "skip_internal": [],
        "already_has": [],
        "missing_blocks": []
    }
    
    for week_folder in sorted(MEETINGS.glob("Week-of-2025-12-*")):
        if not week_folder.is_dir():
            continue
        
        for meeting in sorted(week_folder.iterdir()):
            if not meeting.is_dir():
                continue
            
            meeting_info = {
                "path": str(meeting),
                "name": meeting.name,
                "week": week_folder.name
            }
            
            # Check if already has follow-up email
            if (meeting / "FOLLOW_UP_EMAIL.md").exists():
                results["already_has"].append(meeting_info)
                continue
            
            # Check for required intelligence blocks
            has_transcript = (meeting / "transcript.md").exists() or (meeting / "transcript.jsonl").exists()
            has_manifest = (meeting / "manifest.json").exists()
            has_b01 = (meeting / "B01_DETAILED_RECAP.md").exists()
            
            if not (has_transcript and has_manifest and has_b01):
                meeting_info["missing"] = []
                if not has_transcript:
                    meeting_info["missing"].append("transcript")
                if not has_manifest:
                    meeting_info["missing"].append("manifest")
                if not has_b01:
                    meeting_info["missing"].append("B01")
                results["missing_blocks"].append(meeting_info)
                continue
            
            # Check if internal-only meeting
            if is_internal_meeting(meeting):
                meeting_info["reason"] = "Internal meeting (team/standup)"
                results["skip_internal"].append(meeting_info)
                continue
            
            # Check for external stakeholders and deliverables
            has_external = has_external_stakeholders(meeting)
            has_delivs = has_deliverables(meeting)
            
            meeting_info["has_external_stakeholders"] = has_external
            meeting_info["has_deliverables"] = has_delivs
            
            if has_external or has_delivs:
                meeting_info["priority"] = "high" if (has_external and has_delivs) else "medium"
                results["needs_followup"].append(meeting_info)
            else:
                meeting_info["reason"] = "No external stakeholders or deliverables detected"
                results["skip_internal"].append(meeting_info)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Identify meetings needing FOLLOW_UP_EMAIL.md backfill")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()
    
    results = scan_week_folders()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*70}")
        print("FOLLOW_UP_EMAIL.md Backfill Analysis")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*70}\n")
        
        print(f"✅ Already has FOLLOW_UP_EMAIL.md: {len(results['already_has'])}")
        print(f"⏭️  Skip (internal meetings): {len(results['skip_internal'])}")
        print(f"❌ Missing required blocks: {len(results['missing_blocks'])}")
        print(f"📧 NEEDS FOLLOW-UP EMAIL: {len(results['needs_followup'])}")
        
        if results['needs_followup']:
            print(f"\n{'='*70}")
            print("Meetings Needing Follow-Up Email Backfill:")
            print(f"{'='*70}")
            for m in results['needs_followup']:
                priority = "🔴" if m.get('priority') == 'high' else "🟡"
                print(f"\n{priority} {m['name']}")
                print(f"   Week: {m['week']}")
                print(f"   External stakeholders: {m.get('has_external_stakeholders', '?')}")
                print(f"   Has deliverables: {m.get('has_deliverables', '?')}")
        
        if results['missing_blocks']:
            print(f"\n{'='*70}")
            print("Meetings Missing Required Blocks (cannot backfill):")
            print(f"{'='*70}")
            for m in results['missing_blocks']:
                print(f"  ⚠️ {m['name']}: missing {', '.join(m.get('missing', []))}")
        
        print(f"\n{'='*70}")
        print("Summary")
        print(f"{'='*70}")
        print(f"Total in Week-of-2025-12-*: {sum(len(v) for v in results.values())}")
        print(f"Actionable (need backfill): {len(results['needs_followup'])}")
        
        if results['needs_followup']:
            print(f"\nTo generate follow-up emails for these meetings:")
            print(f"  1. Use: @Follow-Up Email Generator")
            print(f"  2. Or run MG-5 manually on each meeting folder")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())

