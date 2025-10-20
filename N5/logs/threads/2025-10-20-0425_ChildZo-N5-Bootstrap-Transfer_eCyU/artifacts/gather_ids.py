import json, glob
from pathlib import Path

paths = []
paths += glob.glob('/home/workspace/N5/inbox/meeting_requests/*.json')
paths += glob.glob('/home/workspace/N5/inbox/meeting_requests/completed/*.json')
paths += glob.glob('/home/workspace/N5/inbox/meeting_requests/processed/*.json')
paths += glob.glob('/home/workspace/N5/records/meetings/*/_metadata.json')

ids = set()
for p in paths:
    try:
        with open(p,'r') as f:
            data = json.load(f)
        if isinstance(data, dict):
            gid = data.get('gdrive_id')
            if gid:
                ids.add(str(gid))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('gdrive_id'):
                    ids.add(str(item['gdrive_id']))
    except Exception:
        pass

out = Path('/home/.z/workspaces/con_Ded9iWm2RNNbeCyU/existing_gdrive_ids.txt')
out.write_text('\n'.join(sorted(ids)))
print(str(out))
