import json
from pathlib import Path

items=[]
for p in Path('/home/workspace/N5/records/meetings').glob('**/_metadata.json'):
    try:
        data=json.loads(p.read_text())
    except Exception:
        continue
    if not isinstance(data, dict):
        continue
    gid=data.get('gdrive_id')
    blocks=data.get('blocks_count')
    orig=data.get('original_filename') or data.get('filename')
    if gid and isinstance(blocks, int) and blocks>0:
        items.append({'gdrive_id': gid, 'original_filename': orig})

out=Path(__file__).with_name('to_mark.json')
out.write_text(json.dumps(items, ensure_ascii=False))
print(json.dumps({'count': len(items), 'out': str(out)}))
