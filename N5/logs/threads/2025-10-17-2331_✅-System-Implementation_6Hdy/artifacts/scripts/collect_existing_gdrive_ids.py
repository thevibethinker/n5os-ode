#!/usr/bin/env python3
import json, sys
from pathlib import Path

SEARCH_PATHS = [
    Path('/home/workspace/N5/inbox/meeting_requests'),
    Path('/home/workspace/N5/inbox/meeting_requests/completed'),
    Path('/home/workspace/N5/inbox/meeting_requests/processed'),
    Path('/home/workspace/N5/records/meetings'),
]

def iter_json_files():
    for p in SEARCH_PATHS:
        if not p.exists():
            continue
        if p.name == 'meetings':
            # recurse one level: */_metadata.json
            for sub in p.glob('*'):
                if sub.is_dir():
                    m = sub / '_metadata.json'
                    if m.exists():
                        yield m
        else:
            for f in p.glob('*.json'):
                yield f

def main():
    ids = set()
    files = 0
    for f in iter_json_files():
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        files += 1
        gid = data.get('gdrive_id') or data.get('gdriveId')
        if gid:
            ids.add(gid)
    out = {
        'count': len(ids),
        'files_scanned': files,
        'gdrive_ids': sorted(ids),
    }
    print(json.dumps(out))

if __name__ == '__main__':
    main()
