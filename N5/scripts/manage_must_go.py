#!/usr/bin/env python3
"""
Manage Must-Go Organizers
Add/remove organizers from the must-go list for event recommendations.

Usage:
  python3 manage_must_go.py --add "Name" --patterns "pattern1,pattern2" --reason "Why"
  python3 manage_must_go.py --remove "Name"
  python3 manage_must_go.py --list
"""
import json
import argparse
from pathlib import Path
from datetime import date

PREFS_FILE = Path("/home/workspace/N5/config/event_preferences.json")

def load_prefs():
    if PREFS_FILE.exists():
        return json.loads(PREFS_FILE.read_text())
    return {"must_go_rules": {"organizers": []}}

def save_prefs(prefs):
    prefs["last_updated"] = str(date.today())
    PREFS_FILE.write_text(json.dumps(prefs, indent=2))

def list_organizers():
    prefs = load_prefs()
    organizers = prefs.get("must_go_rules", {}).get("organizers", [])
    
    if not organizers:
        print("No must-go organizers configured.")
        return
    
    print("\n=== MUST-GO ORGANIZERS ===\n")
    for i, org in enumerate(organizers, 1):
        print(f"{i}. {org['name']}")
        print(f"   Reason: {org.get('reason', 'No reason specified')}")
        print(f"   Patterns: {', '.join(org.get('patterns', []))}")
        print()

def add_organizer(name: str, patterns: list, reason: str):
    prefs = load_prefs()
    
    if "must_go_rules" not in prefs:
        prefs["must_go_rules"] = {"organizers": []}
    if "organizers" not in prefs["must_go_rules"]:
        prefs["must_go_rules"]["organizers"] = []
    
    # Check if already exists
    existing = [o for o in prefs["must_go_rules"]["organizers"] if o["name"].lower() == name.lower()]
    if existing:
        print(f"'{name}' already in must-go list. Updating patterns...")
        existing[0]["patterns"] = list(set(existing[0].get("patterns", []) + patterns))
        existing[0]["reason"] = reason
    else:
        prefs["must_go_rules"]["organizers"].append({
            "name": name,
            "reason": reason,
            "patterns": patterns
        })
        print(f"✓ Added '{name}' to must-go list")
    
    save_prefs(prefs)
    print(f"  Patterns: {', '.join(patterns)}")
    print(f"  Reason: {reason}")

def remove_organizer(name: str):
    prefs = load_prefs()
    organizers = prefs.get("must_go_rules", {}).get("organizers", [])
    
    original_count = len(organizers)
    prefs["must_go_rules"]["organizers"] = [o for o in organizers if o["name"].lower() != name.lower()]
    
    if len(prefs["must_go_rules"]["organizers"]) < original_count:
        save_prefs(prefs)
        print(f"✓ Removed '{name}' from must-go list")
    else:
        print(f"'{name}' not found in must-go list")

def main():
    parser = argparse.ArgumentParser(description="Manage must-go organizers for event recommendations")
    parser.add_argument("--list", action="store_true", help="List all must-go organizers")
    parser.add_argument("--add", type=str, help="Add organizer by name")
    parser.add_argument("--patterns", type=str, help="Comma-separated patterns to match (lowercase)")
    parser.add_argument("--reason", type=str, default="Always recommend", help="Why this is a must-go")
    parser.add_argument("--remove", type=str, help="Remove organizer by name")
    
    args = parser.parse_args()
    
    if args.list:
        list_organizers()
    elif args.add:
        patterns = [p.strip().lower() for p in (args.patterns or args.add).split(",")]
        add_organizer(args.add, patterns, args.reason)
    elif args.remove:
        remove_organizer(args.remove)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

