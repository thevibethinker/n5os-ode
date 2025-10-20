import json
from pathlib import Path

ROOT = Path('/home/workspace')

def collect_json_files():
    paths = [
        ROOT / 'N5/inbox/meeting_requests',
        ROOT / 'N5/inbox/meeting_requests/completed',
        ROOT / 'N5/inbox/meeting_requests/processed',
    ]
    files = []
    for p in paths:
        if p.exists():
            files.extend(sorted(p.glob('*.json')))
    meta_dirs = ROOT / 'N5/records/meetings'
    if meta_dirs.exists():
        for mdir in sorted(meta_dirs.glob('*/_metadata.json')):
            files.append(mdir)
    return files


def main():
    files = collect_json_files()
    gdrive_ids = set()
    meeting_ids = set()
    for f in files:
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if isinstance(data, dict):
            gid = data.get('gdrive_id')
            if gid:
                gdrive_ids.add(gid)
            mid = data.get('meeting_id')
            if mid:
                meeting_ids.add(mid)
    print(json.dumps({
        'gdrive_ids': sorted(gdrive_ids),
        'meeting_ids': sorted(meeting_ids),
        'scanned_count': len(files)
    }))

if __name__ == '__main__':
    main()
