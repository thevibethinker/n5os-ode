#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path('/home/workspace')
paths = [
    ROOT / 'N5/inbox/meeting_requests',
    ROOT / 'N5/inbox/meeting_requests/completed',
    ROOT / 'N5/inbox/meeting_requests/processed',
]
meta_glob = ROOT.glob('N5/records/meetings/*/_metadata.json')
ids = set()

for p in paths:
    if not p.exists():
        continue
    for fp in p.glob('*.json'):
        try:
            data = json.loads(fp.read_text())
            val = data.get('gdrive_id') or data.get('drive_id') or data.get('source', {}).get('gdrive_id')
            if isinstance(val, str) and val.strip():
                ids.add(val.strip())
        except Exception:
            pass

for fp in meta_glob:
    try:
        data = json.loads(fp.read_text())
        val = data.get('gdrive_id') or data.get('source', {}).get('gdrive_id')
        if isinstance(val, str) and val.strip():
            ids.add(val.strip())
    except Exception:
        pass

for i in sorted(ids):
    print(i)
