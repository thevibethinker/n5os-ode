#!/usr/bin/env python3
import json
from pathlib import Path

RESULTS_PATH = Path("/home/workspace/N5/builds/position-system-overhaul/merge_execution_results.json")
CANDIDATES_PATH = Path("/home/workspace/N5/data/position_candidates.jsonl")

def main():
    with open(RESULTS_PATH) as f:
        results = json.load(f)
    
    # Map of ID -> new_status
    status_map = {}
    for r in results:
        cid = r.get("candidate")
        status = r.get("status")
        if status == "merged":
            status_map[cid] = "promoted"
        elif status == "promoted":
            status_map[cid] = "promoted"
        elif status == "rejected":
            status_map[cid] = "rejected"

    new_lines = []
    updated_count = 0
    with open(CANDIDATES_PATH) as f:
        for line in f:
            c = json.loads(line)
            cid = c.get("id")
            if cid in status_map:
                c["status"] = status_map[cid]
                updated_count += 1
            new_lines.append(json.dumps(c))
    
    with open(CANDIDATES_PATH, 'w') as f:
        for line in new_lines:
            f.write(line + '\n')
            
    print(f"Updated {updated_count} candidates in {CANDIDATES_PATH}")

if __name__ == "__main__":
    main()

