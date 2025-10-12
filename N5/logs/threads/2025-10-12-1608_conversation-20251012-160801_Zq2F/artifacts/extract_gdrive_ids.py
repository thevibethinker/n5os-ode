#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main():
    roots = [
        Path('/home/workspace/N5/inbox/meeting_requests'),
        Path('/home/workspace/N5/inbox/meeting_requests/completed'),
        Path('/home/workspace/N5/inbox/meeting_requests/processed'),
        Path('/home/workspace/N5/records/meetings'),
    ]
    ids = set()
    # meeting_requests JSONs
    for base in roots[:3]:
        if not base.exists():
            continue
        for p in base.glob('*.json'):
            try:
                data = json.loads(p.read_text())
                gid = data.get('gdrive_id')
                if gid:
                    ids.add(gid)
            except Exception:
                pass
    # records/meetings/*/_metadata.json
    rec_base = roots[3]
    if rec_base.exists():
        for folder in rec_base.iterdir():
            meta = folder / '_metadata.json'
            if meta.exists():
                try:
                    data = json.loads(meta.read_text())
                    gid = data.get('gdrive_id')
                    if gid:
                        ids.add(gid)
                except Exception:
                    pass
    print(json.dumps(sorted(ids)))

if __name__ == '__main__':
    main()
