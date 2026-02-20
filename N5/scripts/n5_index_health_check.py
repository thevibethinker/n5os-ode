import json
import os
import sys

sys.path.insert(0, "./")
from N5.cognition.n5_memory_client import N5MemoryClient


def main():
    client = N5MemoryClient()
    status = client.ensure_index_fresh(auto_rebuild=False)
    freshness = status.get("freshness") or {}

    # Print structured summary
    payload = {
        "fresh": status.get("fresh", False),
        "rebuilt": status.get("rebuilt", False),
        "drift_pct": freshness.get("drift_pct"),
        "missing_count": freshness.get("missing_count"),
        "orphan_count": freshness.get("orphan_count"),
        "index_mtime": freshness.get("index_mtime"),
        "latest_indexed": freshness.get("latest_indexed"),
    }
    print(json.dumps(payload))

    # Exit code indicates freshness
    if not payload["fresh"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
