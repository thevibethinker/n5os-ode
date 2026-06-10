#!/usr/bin/env python3
"""Compatibility entrypoint for the pulse visual elevation skill."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Explain the pulse visual elevation workflow for this export."
    )
    parser.add_argument("target", nargs="?", help="Optional page/component target")
    args = parser.parse_args()
    if args.target:
        print(f"Use Skills/recommend-skill-chain to plan visual elevation for {args.target}.")
    else:
        print("Use Skills/recommend-skill-chain to plan a visual elevation pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
