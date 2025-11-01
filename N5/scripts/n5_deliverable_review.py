#!/usr/bin/env python3
"""N5 Command: deliverable-review"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="List and review generated deliverables.")
    parser.add_argument("meeting_folder", help="Name of the meeting folder in Personal/Meetings/")
    args = parser.parse_args()

    print("## N5 Deliverable Review (Placeholder)")
    print(f"- Meeting: {args.meeting_folder}")
    
    deliverables_dir = f"/home/workspace/Personal/Meetings/{args.meeting_folder}/DELIVERABLES"
    if os.path.isdir(deliverables_dir):
        print("- Found deliverables:")
        for root, _, files in os.walk(deliverables_dir):
            for name in files:
                print(f"  - {os.path.join(root, name).replace(deliverables_dir + '/', '')}")
    else:
        print("- No DELIVERABLES/ directory found.")

if __name__ == "__main__":
    sys.exit(main())
