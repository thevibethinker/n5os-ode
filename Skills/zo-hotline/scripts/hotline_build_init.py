#!/usr/bin/env python3
"""
hotline_build_init.py — Initialize a Pulse build for hotline improvements.

Wraps pulse_cc.py to create a new hotline improvement build with
pre-populated standard drops for the analysis-improve-deploy cycle.

Usage:
    python3 Skills/zo-hotline/scripts/hotline_build_init.py "description of improvement"
    python3 Skills/zo-hotline/scripts/hotline_build_init.py "reduce latency on greeting" --dry-run

Standard Drops:
    D1.1: Call Data Analysis Review (W1)
    D1.2: Improvement Identification (W1)
    D2.1: Implementation (W2, depends D1.1 D1.2)
    D2.2: Testing & Validation (W2, depends D2.1)
    D2.3: Deploy & Verify (W2, depends D2.2)
"""

import argparse
import re
import subprocess
import sys

PULSE_CC = "Skills/pulse/scripts/pulse_cc.py"
WORKDIR = "/home/workspace"


def slugify(description: str) -> str:
    """Generate a hotline-prefixed slug from a description."""
    slug = description.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    max_len = 40 - len("hotline-")
    slug = slug[:max_len].rstrip("-")
    return f"hotline-{slug}"


def run_pulse(args: list[str], dry_run: bool = False) -> int:
    """Run a pulse_cc.py command. Returns exit code."""
    cmd = ["python3", PULSE_CC] + args
    if dry_run:
        print(f"  [dry-run] {' '.join(cmd)}")
        return 0
    result = subprocess.run(cmd, cwd=WORKDIR, capture_output=False)
    return result.returncode


STANDARD_DROPS = [
    {
        "drop_id": "D1.1",
        "name": "Call Data Analysis Review",
        "wave": "W1",
        "depends": [],
    },
    {
        "drop_id": "D1.2",
        "name": "Improvement Identification",
        "wave": "W1",
        "depends": [],
    },
    {
        "drop_id": "D2.1",
        "name": "Implementation",
        "wave": "W2",
        "depends": ["D1.1", "D1.2"],
    },
    {
        "drop_id": "D2.2",
        "name": "Testing & Validation",
        "wave": "W2",
        "depends": ["D2.1"],
    },
    {
        "drop_id": "D2.3",
        "name": "Deploy & Verify",
        "wave": "W2",
        "depends": ["D2.2"],
    },
]


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a Pulse build for hotline improvements.",
        epilog="""
Examples:
  %(prog)s "reduce greeting latency"
  %(prog)s "add caller sentiment tracking" --dry-run
  %(prog)s "fix transcription accuracy for Zo mentions"
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "description",
        help="Description of the hotline improvement (used to generate title and slug)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    args = parser.parse_args()

    slug = slugify(args.description)
    title = f"Hotline: {args.description}"

    print(f"Initializing hotline improvement build")
    print(f"  Slug:  {slug}")
    print(f"  Title: {title}")
    print()

    if args.dry_run:
        print("[DRY RUN] The following commands would be executed:\n")

    rc = run_pulse(["init", slug, "--title", title, "--type", "code_build"], dry_run=args.dry_run)
    if rc != 0:
        print(f"\nFailed to initialize build (exit code {rc})")
        return rc

    for drop in STANDARD_DROPS:
        brief_args = [
            "brief", slug, drop["drop_id"],
            "--name", drop["name"],
            "--wave", drop["wave"],
        ]
        if drop["depends"]:
            brief_args += ["--depends"] + drop["depends"]

        rc = run_pulse(brief_args, dry_run=args.dry_run)
        if rc != 0:
            print(f"\nFailed to create brief for {drop['drop_id']} (exit code {rc})")
            return rc

    print()
    print(f"Build ready. Next steps:")
    print(f"  1. Fill briefs in N5/builds/{slug}/drops/")
    print(f"  2. Run: python3 {PULSE_CC} execute {slug}")
    print(f"  3. After each drop: python3 {PULSE_CC} deposit {slug} <drop_id> --status complete --summary \"...\"")
    print(f"  4. Finalize: python3 {PULSE_CC} finalize {slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
