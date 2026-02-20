#!/usr/bin/env python3
"""Check the ANN index freshness and emit JSON for automated monitoring."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any

from N5.cognition.n5_memory_client import N5MemoryClient


def humanize_freshness(freshness: dict[str, Any] | None) -> str:
    if not freshness:
        return "no index yet"
    demo = f"drift={freshness.get('drift_pct', 0):.1f}% (missing {freshness.get('missing_count', 0)}, orphan {freshness.get('orphan_count', 0)})"
    if freshness.get('needs_rebuild'):
        demo += " -> needs rebuild"
    return demo


def main() -> int:
    parser = argparse.ArgumentParser(description="Check semantic memory ANN index freshness.")
    parser.add_argument("--threshold", type=float, default=10.0, help="Drift % threshold that should trigger alerts")
    parser.add_argument("--auto-rebuild", action="store_true", help="If set, rebuild when stale instead of just reporting")
    args = parser.parse_args()

    client = N5MemoryClient()
    result = client.ensure_index_fresh(drift_threshold=args.threshold, auto_rebuild=args.auto_rebuild)
    freshness = result.get("freshness")
    summary = {
        "fresh": result.get("fresh", False),
        "rebuilt": result.get("rebuilt", False),
        "drift_pct": (freshness or {}).get("drift_pct"),
        "index_count": (freshness or {}).get("index_count"),
        "db_count": (freshness or {}).get("db_count"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    print(json.dumps(summary))
    print("ANN index check:", humanize_freshness(freshness))

    return 0 if result.get("fresh", False) else 1


if __name__ == "__main__":
    sys.exit(main())
