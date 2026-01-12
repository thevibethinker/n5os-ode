#!/usr/bin/env python3
"""
Reflection Engine v2 — Smoke Test

Validates that all components of the reflection system are in place and functional.
Run this to verify the system is production-ready.

Usage:
    python3 N5/scripts/reflection_smoke_test.py
    python3 N5/scripts/reflection_smoke_test.py --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Paths
WORKSPACE = Path("/home/workspace")
PROMPTS_DIR = WORKSPACE / "Prompts" / "Blocks" / "Reflection"
ORCHESTRATOR = WORKSPACE / "Prompts" / "Process Reflection.prompt.md"
REGISTRY = WORKSPACE / "N5" / "prefs" / "reflection_blocks_v2.md"
OUTPUT_DIR = WORKSPACE / "Personal" / "Reflections"
INPUT_DIR = WORKSPACE / "Inbox" / "Voice Thoughts"
EDGES_SCRIPT = WORKSPACE / "N5" / "scripts" / "reflection_edges.py"
EDGES_DATA = WORKSPACE / "N5" / "data" / "reflection_edges.jsonl"

# Expected blocks
EXPECTED_BLOCKS = [
    "R00_Emergent.prompt.md",
    "R01_Personal.prompt.md",
    "R02_Learning.prompt.md",
    "R03_Strategic.prompt.md",
    "R04_Market.prompt.md",
    "R05_Product.prompt.md",
    "R06_Synthesis.prompt.md",
    "R07_Prediction.prompt.md",
    "R08_Venture.prompt.md",
    "R09_Content.prompt.md",
    "RIX_Integration.prompt.md",
]


def check(name: str, condition: bool, verbose: bool = False, detail: str = "") -> bool:
    """Check a condition and print result."""
    status = "✓" if condition else "✗"
    print(f"  {status} {name}")
    if verbose and detail:
        print(f"      {detail}")
    return condition


def main():
    parser = argparse.ArgumentParser(description="Reflection Engine smoke test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details")
    args = parser.parse_args()
    
    print("Reflection Engine v2 — Smoke Test")
    print("=" * 40)
    
    all_passed = True
    
    # 1. Check block prompts
    print("\n1. Block Prompts")
    for block in EXPECTED_BLOCKS:
        path = PROMPTS_DIR / block
        exists = path.exists()
        detail = f"{path}" if args.verbose else ""
        if not check(block, exists, args.verbose, detail):
            all_passed = False
    
    # 2. Check orchestrator
    print("\n2. Orchestrator")
    if not check("Process Reflection.prompt.md exists", ORCHESTRATOR.exists(), args.verbose):
        all_passed = False
    else:
        content = ORCHESTRATOR.read_text()
        has_frontmatter = content.startswith("---")
        has_tool_flag = "tool: true" in content
        check("Has frontmatter", has_frontmatter, args.verbose)
        check("Has tool: true", has_tool_flag, args.verbose)
    
    # 3. Check registry
    print("\n3. Registry")
    if not check("reflection_blocks_v2.md exists", REGISTRY.exists(), args.verbose):
        all_passed = False
    else:
        content = REGISTRY.read_text()
        has_r_blocks = "R01" in content and "R09" in content
        check("Contains R-block definitions", has_r_blocks, args.verbose)
    
    # 4. Check edge system
    print("\n4. Edge System")
    if not check("reflection_edges.py exists", EDGES_SCRIPT.exists(), args.verbose):
        all_passed = False
    if not check("reflection_edges.jsonl exists", EDGES_DATA.exists(), args.verbose):
        all_passed = False
    else:
        with open(EDGES_DATA) as f:
            edge_count = sum(1 for line in f if line.strip() and not line.startswith("#"))
        check(f"Edge data has content ({edge_count} edges)", edge_count > 0, args.verbose)
    
    # 5. Check input path
    print("\n5. Input Path")
    check("Inbox/Voice Thoughts/ exists", INPUT_DIR.exists(), args.verbose)
    
    # 6. Check output structure
    print("\n6. Output Structure")
    check("Personal/Reflections/ exists", OUTPUT_DIR.exists(), args.verbose)
    
    # Find recent output
    recent_outputs = []
    cutoff = datetime.now() - timedelta(days=30)
    if OUTPUT_DIR.exists():
        for year_dir in OUTPUT_DIR.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir():
                        for reflection_dir in month_dir.iterdir():
                            if reflection_dir.is_dir():
                                analysis = reflection_dir / "analysis.md"
                                if analysis.exists():
                                    mtime = datetime.fromtimestamp(analysis.stat().st_mtime)
                                    if mtime > cutoff:
                                        recent_outputs.append(reflection_dir.name)
    
    has_recent = len(recent_outputs) > 0
    detail = f"Recent: {recent_outputs[:3]}" if args.verbose and recent_outputs else ""
    check(f"Has recent output (last 30 days): {len(recent_outputs)} found", has_recent, args.verbose, detail)
    
    # Summary
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All checks passed — system is production-ready")
        return 0
    else:
        print("✗ Some checks failed — review issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

