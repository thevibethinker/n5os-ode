#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT = Path('/home/workspace')
patterns = [
    'N5/inbox/meeting_requests/*.json',
    'N5/inbox/meeting_requests/completed/*.json',
    'N5/inbox/meeting_requests/processed/*.json',
    'N5/records/meetings/*/_metadata.json',
]

ids = set()
files_checked = []
for pat in patterns:
    for p in ROOT.glob(pat):
        try:
            txt = p.read_text(encoding='utf-8', errors='ignore')
            data = None
            # Some may be JSONL with single line
            try:
                data = json.loads(txt)
            except json.JSONDecodeError:
                # try first line
                first = txt.splitlines()[0] if txt.strip() else ''
                try:
                    data = json.loads(first)
                except Exception:
                    data = None
            if isinstance(data, dict):
                gid = data.get('gdrive_id') or data.get('drive_file_id')
                if gid:
                    ids.add(gid)
            files_checked.append(str(p))
        except Exception:
            pass

out = {
    'count': len(ids),
    'ids': sorted(ids),
    'files_checked': files_checked,
}
print(json.dumps(out))
