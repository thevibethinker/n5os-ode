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

try:
    from rapidfuzz import process, fuzz  # type: ignore
except ImportError:  # pragma: no cover
    print("rapidfuzz not installed. Install it with: pip install rapidfuzz", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_FILE = ROOT / "commands.jsonl"

SIMILARITY_THRESHOLD = 55  # percent; below this we consider the match too weak
MAX_CANDIDATES = 3


def load_registry(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        sys.exit(f"Commands registry not found: {path}")
    registry: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                registry.append(json.loads(line))
            except json.JSONDecodeError as e:
                sys.exit(f"Invalid JSONL in {path}: {e}")
    return registry


def choose_best_match(query: str, registry: List[Dict[str, Any]]) -> Tuple[List[Tuple[str, Dict[str, Any], float]], bool]:
    """Return list of (command_name, obj, score) sorted by score desc. bool indicates if we are confident."""
    names = [cmd["name"] for cmd in registry]
    # Use rapidfuzz to get top matches
    matches = process.extract(query, names, scorer=fuzz.QRatio, limit=MAX_CANDIDATES)
    results: List[Tuple[str, Dict[str, Any], float]] = []
    for name, score, _ in matches:
        cmd_obj = next(c for c in registry if c["name"] == name)
        results.append((name, cmd_obj, score))
    confident = False
    if results and results[0][2] >= SIMILARITY_THRESHOLD and (len(results) == 1 or results[0][2] - results[1][2] >= 10):
        confident = True
    return results, confident


def prompt_user(candidates: List[Tuple[str, Dict[str, Any], float]], confident: bool) -> Dict[str, Any] | None:
    if not candidates:
        print("No matching command found.")
        return None

    if confident:
        top = candidates[0][1]
        yn = input(f"Run \u001b[1m{top['name']}\u001b[0m ? (y/N) ")
        if yn.lower() == "y":
            return top
        return None

    print("Multiple possible commands:")
    for idx, (name, _obj, score) in enumerate(candidates, 1):
        print(f" {idx}. {name}   ({score:.0f}%)")
    sel = input("Select # to run, or press Enter to cancel: ")
    try:
        choice = int(sel)
        if 1 <= choice <= len(candidates):
            return candidates[choice - 1][1]
    except ValueError:
        pass
    return None


def dispatch(cmd: Dict[str, Any], remaining_args: List[str]) -> None:
    cmd_name = cmd["name"]
    # Forward to n5 CLI (assumed to be on PATH)
    full_cmd = ["n5", cmd_name] + remaining_args
    print("→", " ".join(full_cmd))
    subprocess.run(full_cmd)


def main():
    parser = argparse.ArgumentParser(description="Natural language to N5 command translator")
    parser.add_argument("query", nargs=argparse.REMAINDER, help="Free-form text to map to a command (everything after 'incantum')")
    args = parser.parse_args()
    if not args.query:
        sys.exit("Usage: incantum <natural-language>")
    query_words = []
    extra_args: List[str] = []
    for tok in args.query:
        if tok.startswith("--"):
            extra_args.append(tok)
        else:
            query_words.append(tok)
    query = " ".join(query_words)

    registry = load_registry(COMMANDS_FILE)
    candidates, confident = choose_best_match(query, registry)
    selection = prompt_user(candidates, confident)
    if selection is None:
        print("Cancelled.")
        return
    dispatch(selection, extra_args)


if __name__ == "__main__":
    main()
