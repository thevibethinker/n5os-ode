#!/usr/bin/env python3
"""N5 Command: meeting-approve"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Approve meeting outputs.")
    parser.add_argument("meeting_folder", help="Name of the meeting folder in Careerspan/Meetings/")
    parser.add_argument("--blocks", nargs='*', help="Optional list of specific blocks to approve (e.g., action_items)")
    args = parser.parse_args()

    print("## N5 Meeting Approve (Placeholder)")
    print(f"- Meeting: {args.meeting_folder}")
    if args.blocks:
        print(f"- Blocks Approved: {', '.join(args.blocks)}")
    else:
        print("- All blocks approved.")

if __name__ == "__main__":
    sys.exit(main())
