#!/usr/bin/env python3
"""
Resolve Placeholder Emails via Gmail Search

For CRM profiles with placeholder emails (unknown+Name@placeholder.local),
searches Gmail by name to find actual email addresses.

Outputs a review queue for V to confirm before updating.

Usage:
    python3 resolve_placeholder_emails.py --scan        # Scan and create review queue
    python3 resolve_placeholder_emails.py --apply FILE  # Apply confirmed updates
    
NOTE: This script generates a review file - it does NOT auto-update profiles.
V must review and confirm before changes are applied.
"""

import sys
import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/home/workspace')
from N5.lib.paths import CRM_DB

from N5.lib.paths import N5_ROOT
REVIEW_DIR = N5_ROOT / "review" / "email_resolution"


def get_placeholder_profiles():
    """Get all profiles with placeholder emails."""
    conn = sqlite3.connect(CRM_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT id, name, email, yaml_path
        FROM profiles
        WHERE email LIKE '%placeholder%'
        ORDER BY name
    """)
    
    profiles = [dict(row) for row in c.fetchall()]
    conn.close()
    return profiles


def generate_review_queue(profiles: list) -> Path:
    """Generate a markdown review queue for V to confirm email resolutions."""
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    review_file = REVIEW_DIR / f"email_resolution_review_{timestamp}.md"
    
    lines = [
        "---",
        f"created: {datetime.now().strftime('%Y-%m-%d')}",
        "version: 1.0",
        "provenance: resolve_placeholder_emails.py",
        "---",
        "",
        "# Email Resolution Review Queue",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} ET",
        f"**Profiles to resolve:** {len(profiles)}",
        "",
        "## Instructions",
        "",
        "For each profile below, I need you to:",
        "1. Confirm the correct email address (search Gmail if needed)",
        "2. Mark as `[x]` to approve, or add the correct email",
        "3. Mark as `[SKIP]` if you can't find them or don't want to update",
        "",
        "Once reviewed, run: `python3 N5/scripts/resolve_placeholder_emails.py --apply <this_file>`",
        "",
        "---",
        "",
        "## Profiles to Review",
        "",
    ]
    
    for p in profiles:
        name = p['name'] or 'Unknown'
        lines.append(f"### {name}")
        lines.append(f"- **Profile ID:** {p['id']}")
        lines.append(f"- **Current (placeholder):** `{p['email']}`")
        lines.append(f"- **Gmail search:** Search for \"{name}\" in Gmail")
        lines.append(f"- **Resolved email:** [ ] _enter email here or SKIP_")
        lines.append("")
    
    review_file.write_text("\n".join(lines))
    return review_file


def apply_resolutions(review_file: Path) -> dict:
    """Parse a reviewed file and apply confirmed email updates."""
    if not review_file.exists():
        return {"error": f"File not found: {review_file}"}
    
    content = review_file.read_text()
    
    # Parse the file for resolved emails
    # Format: - **Resolved email:** [x] someone@example.com
    import re
    
    results = {
        "updated": [],
        "skipped": [],
        "errors": []
    }
    
    # Find all profile blocks
    profile_pattern = re.compile(
        r'### (.+?)\n'
        r'- \*\*Profile ID:\*\* (\d+)\n'
        r'- \*\*Current.*?\n'
        r'- \*\*Gmail search:.*?\n'
        r'- \*\*Resolved email:\*\* \[([x\s]|SKIP)\]\s*(.+)?',
        re.MULTILINE | re.IGNORECASE
    )
    
    conn = sqlite3.connect(CRM_DB)
    c = conn.cursor()
    
    # Collect all updates first, then apply atomically
    updates_to_apply = []
    
    for match in profile_pattern.finditer(content):
        name = match.group(1).strip()
        profile_id = int(match.group(2))
        checkbox = match.group(3).strip().lower()
        email = (match.group(4) or "").strip()
        
        if checkbox == 'skip' or not email or email.startswith('_'):
            results["skipped"].append(name)
            continue
        
        if checkbox == 'x' and '@' in email:
            updates_to_apply.append((name, profile_id, email))
        else:
            results["skipped"].append(f"{name} (invalid format)")
    
    # Apply all updates in a single atomic transaction
    try:
        c.execute("BEGIN TRANSACTION")
        for name, profile_id, email in updates_to_apply:
            c.execute(
                "UPDATE profiles SET email = ?, primary_email = ? WHERE id = ?",
                (email, email, profile_id)
            )
            results["updated"].append(f"{name} → {email}")
        conn.commit()
    except Exception as e:
        conn.rollback()
        results["errors"].append(f"Transaction failed, rolled back: {e}")
        results["updated"] = []  # Clear any partial success messaging
    finally:
        conn.close()
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Resolve placeholder emails via Gmail search')
    parser.add_argument('--scan', action='store_true', help='Scan and generate review queue')
    parser.add_argument('--apply', type=str, metavar='FILE', help='Apply confirmed resolutions from review file')
    parser.add_argument('--count', action='store_true', help='Just count placeholder profiles')
    
    args = parser.parse_args()
    
    if args.count:
        profiles = get_placeholder_profiles()
        print(f"Placeholder profiles: {len(profiles)}")
        return
    
    if args.scan:
        profiles = get_placeholder_profiles()
        if not profiles:
            print("✓ No placeholder profiles found")
            return
        
        review_file = generate_review_queue(profiles)
        print(f"✓ Generated review queue: {review_file}")
        print(f"  {len(profiles)} profiles to review")
        print(f"\nNext steps:")
        print(f"  1. Open {review_file}")
        print(f"  2. Search Gmail for each person's email")
        print(f"  3. Fill in resolved emails or mark SKIP")
        print(f"  4. Run: python3 {__file__} --apply {review_file}")
        return
    
    if args.apply:
        review_file = Path(args.apply)
        results = apply_resolutions(review_file)
        print(json.dumps(results, indent=2))
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()


