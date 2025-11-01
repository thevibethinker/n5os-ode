#!/usr/bin/env python3
"""N5 helper: incantum

Translate free-form natural language after the trigger word into the best-matching N5 command, ask for confirmation, then execute it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add N5/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from executable_manager import list_executables, Executable

try:
    from rapidfuzz import process, fuzz  # type: ignore
except ImportError:  # pragma: no cover
    print("rapidfuzz not installed. Install it with: pip install rapidfuzz", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]

SIMILARITY_THRESHOLD = 55  # percent; below this we consider the match too weak
MAX_CANDIDATES = 3


def load_registry() -> List[Executable]:
    """Load executables from database"""
    return list_executables()


def choose_best_match(query: str, registry: List[Executable]) -> Tuple[List[Tuple[str, Executable, float]], bool]:
    """Return list of (name, executable_obj, score) sorted by score desc. bool indicates if we are confident."""
    names = [exe.name for exe in registry]
    # Use rapidfuzz to get top matches
    matches = process.extract(query, names, scorer=fuzz.QRatio, limit=MAX_CANDIDATES)
    results: List[Tuple[str, Executable, float]] = []
    for name, score, _ in matches:
        exe_obj = next(e for e in registry if e.name == name)
        results.append((name, exe_obj, score))
    confident = False
    if results and results[0][2] >= SIMILARITY_THRESHOLD and (len(results) == 1 or results[0][2] - results[1][2] >= 10):
        confident = True
    return results, confident


def format_candidate(idx: int, name: str, exe: Executable, score: float) -> str:
    """Format a candidate for display."""
    return f"  [{idx}] {name} (score: {score:.0f}%)\n      {exe.description or 'No description'}\n      Type: {exe.type}, File: {exe.file_path}"


def prompt_user(candidates: List[Tuple[str, Executable, float]], confident: bool) -> int:
    """Ask user to pick from candidates. Return chosen index or -1 if canceled."""
    print("\nMatching commands found:")
    for i, (name, exe, score) in enumerate(candidates, 1):
        print(format_candidate(i, name, exe, score))
    
    print("\n[0] Cancel")
    
    if confident:
        default_choice = 1
        prompt_text = f"Choose a command [1-{len(candidates)}, or 0 to cancel] (default: 1): "
    else:
        prompt_text = f"Choose a command [1-{len(candidates)}, or 0 to cancel]: "
        default_choice = None
    
    try:
        user_input = input(prompt_text).strip()
        if not user_input and default_choice:
            return default_choice - 1
        choice = int(user_input)
        if choice == 0:
            return -1
        if 1 <= choice <= len(candidates):
            return choice - 1
        print("Invalid choice.")
        return -1
    except (ValueError, EOFError, KeyboardInterrupt):
        return -1


def execute_command(exe: Executable, args: List[str]) -> int:
    """Execute the command with given args."""
    print(f"\n🚀 Executing: {exe.name}")
    
    # Build command based on type
    if exe.type == "script":
        cmd = ["python3", exe.file_path] + args
    elif exe.type == "prompt":
        # For prompts, we'd need to invoke them through the prompt system
        # For now, just show the file path
        print(f"Prompt file: {exe.file_path}")
        print("(Prompt execution not yet implemented in incantum)")
        return 0
    else:
        # Generic execution
        cmd = [exe.file_path] + args
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Translate natural language into N5 commands",
        usage="n5_incantum.py <natural language query> [-- <command args>]"
    )
    parser.add_argument("query", nargs="+", help="Natural language query")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without running")
    
    args, extra_args = parser.parse_known_args()
    
    query_text = " ".join(args.query)
    print(f"🔍 Searching for command matching: '{query_text}'")
    
    registry = load_registry()
    if not registry:
        print("Error: No commands found in registry", file=sys.stderr)
        return 1
    
    candidates, confident = choose_best_match(query_text, registry)
    
    if not candidates:
        print("❌ No matching commands found.")
        return 1
    
    if candidates[0][2] < SIMILARITY_THRESHOLD:
        print(f"❌ Best match score ({candidates[0][2]:.0f}%) is below threshold ({SIMILARITY_THRESHOLD}%)")
        print("Possible matches:")
        for name, exe, score in candidates:
            print(f"  - {name} ({score:.0f}%)")
        return 1
    
    # If confident and only one strong match, use it directly
    if confident and len(candidates) == 1:
        chosen_idx = 0
        print(f"✓ Using: {candidates[0][0]} (score: {candidates[0][2]:.0f}%)")
    else:
        chosen_idx = prompt_user(candidates, confident)
    
    if chosen_idx == -1:
        print("Canceled.")
        return 0
    
    chosen_name, chosen_exe, chosen_score = candidates[chosen_idx]
    
    if args.dry_run:
        print(f"\n[DRY RUN] Would execute: {chosen_name}")
        print(f"  Type: {chosen_exe.type}")
        print(f"  File: {chosen_exe.file_path}")
        if extra_args:
            print(f"  Args: {extra_args}")
        return 0
    
    return execute_command(chosen_exe, extra_args)


if __name__ == "__main__":
    sys.exit(main())
