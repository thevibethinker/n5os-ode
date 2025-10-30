import json, sys
from pathlib import Path

def collect_ids(paths):
    ids=set()
    for pattern in paths:
        for p in Path('/home/workspace').glob(pattern):
            try:
                with open(p,'r') as f:
                    data=json.load(f)
                # handle both single object and list
                if isinstance(data, dict):
                    val=data.get('gdrive_id')
                    if val:
                        ids.add(str(val))
                elif isinstance(data, list):
                    for obj in data:
                        if isinstance(obj, dict) and obj.get('gdrive_id'):
                            ids.add(str(obj['gdrive_id']))
            except Exception:
                continue
    return sorted(ids)

if __name__=='__main__':
    patterns=[
        'N5/inbox/meeting_requests/**/*_request.json',
        'N5/records/meetings/**/_metadata.json',
    ]
    ids=collect_ids(patterns)
    out_path=Path(__file__).with_name('dedup_ids.json')
    out_path.write_text(json.dumps({'gdrive_ids':ids}, ensure_ascii=False))
    print(json.dumps({'dedup_count': len(ids), 'out': str(out_path)}))
