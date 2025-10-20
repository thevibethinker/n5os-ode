import json, os
from pathlib import Path

def load_json_safe(p: Path):
    try:
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

base = Path('/home/workspace')
paths = [
    base / 'N5/inbox/meeting_requests',
    base / 'N5/inbox/meeting_requests' / 'completed',
    base / 'N5/inbox/meeting_requests' / 'processed',
]
# _metadata.json under N5/records/meetings/*/
meetings_dir = base / 'N5/records/meetings'

gdrive_ids = set()

for p in paths:
    if not p.exists():
        continue
    for fp in p.rglob('*.json'):
        data = load_json_safe(fp)
        if isinstance(data, dict):
            gid = data.get('gdrive_id')
            if gid:
                gdrive_ids.add(gid)

if meetings_dir.exists():
    for sub in meetings_dir.iterdir():
        meta = sub / '_metadata.json'
        if meta.exists():
            data = load_json_safe(meta)
            if isinstance(data, dict):
                gid = data.get('gdrive_id')
                if gid:
                    gdrive_ids.add(gid)

out_path = Path('/home/.z/workspaces/con_WFqtaXfQ5XvDKcwK/dedup_gdrive_ids.json')
out_path.write_text(json.dumps(sorted(gdrive_ids), ensure_ascii=False, indent=2))
print(f"dedup_ids_count={len(gdrive_ids)} out={out_path}")
