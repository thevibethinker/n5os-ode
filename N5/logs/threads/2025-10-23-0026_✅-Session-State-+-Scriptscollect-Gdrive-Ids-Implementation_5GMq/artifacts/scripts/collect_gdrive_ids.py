#!/usr/bin/env python3
import json, sys
from pathlib import Path

def collect(paths):
    ids = set()
    files = []
    for p in paths:
        for f in Path(p).parent.glob(Path(p).name):
            files.append(str(f))
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    gid = data.get('gdrive_id') or data.get('gdriveId')
                    if gid:
                        ids.add(str(gid))
            except Exception:
                pass
    return ids, files

if __name__ == '__main__':
    patterns = sys.argv[1:]
    ids, files = collect(patterns)
    outdir = Path(__file__).parent
    outdir.mkdir(parents=True, exist_ok=True)
    idfile = outdir / 'existing_gdrive_ids.txt'
    with open(idfile, 'w', encoding='utf-8') as fh:
        for gid in sorted(ids):
            fh.write(gid + '\n')
    print(str(idfile))
    # Also echo counts for logs
    print(f"FILES_SCANNED={len(files)} IDS_FOUND={len(ids)}")
