import json, sys
from pathlib import Path

paths = [
    Path('/home/workspace/N5/inbox/meeting_requests'),
    Path('/home/workspace/N5/inbox/meeting_requests/completed'),
    Path('/home/workspace/N5/inbox/meeting_requests/processed'),
    Path('/home/workspace/N5/records/meetings'),
]
ids = set()
files_scanned = 0
for base in paths:
    if not base.exists():
        continue
    if base.name == 'meetings':
        for meta in base.rglob('_metadata.json'):
            try:
                with meta.open('r') as f:
                    data = json.load(f)
                gid = data.get('gdrive_id') or data.get('gdriveId') or data.get('source', {}).get('gdrive_id')
                if gid:
                    ids.add(gid)
                files_scanned += 1
            except Exception:
                continue
    else:
        for jf in base.glob('*.json'):
            try:
                with jf.open('r') as f:
                    data = json.load(f)
                gid = data.get('gdrive_id') or data.get('gdriveId')
                if gid:
                    ids.add(gid)
                files_scanned += 1
            except Exception:
                continue

out = {
    'count': len(ids),
    'files_scanned': files_scanned,
    'ids': sorted(ids),
}
print(json.dumps(out))
