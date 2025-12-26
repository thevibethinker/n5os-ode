#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

import sys
sys.path.insert(0, "/home/workspace/N5/cognition")

from n5_memory_client import N5MemoryClient  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
LOG = logging.getLogger("memory_lab")


def format_result(idx: int, r: Dict[str, Any]) -> str:
    path = r.get("path", "")
    score = r.get("score", 0.0)
    bm25 = r.get("bm25_score", 0.0)
    cdate = r.get("content_date") or "-"
    preview = (r.get("content", "") or "").replace("\n", " ")
    if len(preview) > 140:
        preview = preview[:137] + "..."
    return f"{idx:>2}. score={score:0.3f} bm25={bm25:0.3f} date={cdate} \n    {path}\n    {preview}\n"


def run_memory_lab(query: str, profile: str | None, db_path: str, limit: int) -> int:
    client = N5MemoryClient(db_path=db_path)
    LOG.info("Query: %s", query)
    LOG.info("Profile: %s", profile or "<none - global search>")

    if profile:
        results = client.search_profile(profile=profile, query=query, limit=limit)
    else:
        results = client.search(query=query, limit=limit)

    if not results:
        print("No results found.")
        return 0

    print("\nTop results:\n" + "-" * 60)
    for i, r in enumerate(results, 1):
        print(format_result(i, r))

    # Simple summary by top-level directory
    by_root: Dict[str, int] = {}
    for r in results:
        path = r.get("path") or ""
        parts = path.split("/")
        root = "/".join(parts[:4]) if len(parts) >= 4 else path
        by_root[root] = by_root.get(root, 0) + 1

    print("Summary by root path:")
    for root, count in sorted(by_root.items(), key=lambda x: x[1], reverse=True):
        print(f"  {count:>2}  {root}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="N5 Semantic Memory Lab - inspect retrieval behavior")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--profile", help="Named retrieval profile (e.g., system-architecture, meetings, crm, content-library, voice-guides)")
    parser.add_argument("--db", default="/home/workspace/N5/cognition/brain.db", help="Path to brain.db (default: %(default)s)")
    parser.add_argument("--limit", type=int, default=10, help="Number of results to show (default: %(default)s)")

    args = parser.parse_args()
    return run_memory_lab(query=args.query, profile=args.profile, db_path=args.db, limit=args.limit)


if __name__ == "__main__":
    raise SystemExit(main())

