#!/usr/bin/env python3
import json, re, os, sys, time
from pathlib import Path

REQ_DIR = Path('/home/workspace/N5/inbox/meeting_requests')
REC_DIR = Path('/home/workspace/N5/records/meetings')
OUT_DIR = Path('/home/.z/workspaces/con_vXixJQMWC3rv2EqE')
OUT_DIR.mkdir(parents=True, exist_ok=True)

def collect_dedup_ids():
    ids = set()
    if REQ_DIR.exists():
        for p in REQ_DIR.rglob('*_request.json'):
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                gid = data.get('gdrive_id')
                if isinstance(gid, str) and gid:
                    ids.add(gid)
            except Exception:
                pass
    if REC_DIR.exists():
        for p in REC_DIR.rglob('_metadata.json'):
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                gid = data.get('gdrive_id')
                if isinstance(gid, str) and gid:
                    ids.add(gid)
            except Exception:
                pass
    return ids


def collect_ids_for_marking():
    ids = set()
    if REC_DIR.exists():
        for p in REC_DIR.rglob('_metadata.json'):
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                bc = data.get('blocks_count') or 0
                gid = data.get('gdrive_id')
                if isinstance(bc, (int, float)) and bc > 0 and isinstance(gid, str) and gid:
                    ids.add(gid)
            except Exception:
                pass
    return ids


def sanitize_filename(name: str) -> str:
    # Replace path separators and trim spaces
    safe = re.sub(r'[\\/]+', '-', name)
    safe = re.sub(r'\s+', ' ', safe).strip()
    # Restrict to safe chars
    safe = re.sub(r'[^A-Za-z0-9._\- ()\[\]]+', '-', safe)
    return safe[:200]


def parse_metadata_from_filename(filename: str):
    # Expected patterns include date YYYY-MM-DD and participant names before '-transcript-'
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    date = date_match.group(1) if date_match else ''
    base = filename
    # Extract participants: before "-transcript-" or before last extension
    participants = ''
    m = re.split(r'-transcript-', base, maxsplit=1, flags=re.IGNORECASE)
    if len(m) >= 2:
        participants = m[0]
    else:
        participants = os.path.splitext(base)[0]
    participants = participants.replace('_', ' ').replace('-', ' ').strip()

    # classification
    lower = filename.lower()
    if 'daily team stand-up' in lower or 'internal-team' in lower or 'standup' in lower:
        classification = 'internal'
        participant_slug = 'team'
    else:
        classification = 'external'
        # take first non-empty token from participants as external name
        token = participants.split(' ')[0] if participants else 'unknown'
        participant_slug = re.sub(r'[^a-z0-9]+', '-', token.lower()).strip('-') or 'unknown'

    meeting_id = f"{date}_{classification}-{participant_slug}" if date else f"{classification}-{participant_slug}-{int(time.time())}"
    return {
        'date': date,
        'participants': participants,
        'classification': classification,
        'participant_slug': participant_slug,
        'meeting_id': meeting_id,
    }


def write_request_json(payload: dict, meeting_id: str):
    out_path = Path('/home/workspace/N5/inbox/meeting_requests/processed') / f"{meeting_id}_request.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(payload, f, indent=2)
    return str(out_path)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'dedup':
        ids = sorted(collect_dedup_ids())
        out = OUT_DIR / 'dedup_ids.txt'
        out.write_text('\n'.join(ids))
        print(f"DEDUP_COUNT={len(ids)}\nPATH={out}")
    elif cmd == 'mark':
        ids = sorted(collect_ids_for_marking())
        out = OUT_DIR / 'processed_ids_for_marking.txt'
        out.write_text('\n'.join(ids))
        print(f"MARK_COUNT={len(ids)}\nPATH={out}")
    elif cmd == 'meta':
        # args: filename, gdrive_id, webViewLink
        filename = sys.argv[2]
        gdrive_id = sys.argv[3]
        web = sys.argv[4]
        meta = parse_metadata_from_filename(filename)
        payload = {
            'meeting_id': meta['meeting_id'],
            'classification': meta['classification'],
            'participants': meta['participants'],
            'date': meta['date'],
            'gdrive_id': gdrive_id,
            'gdrive_link': web,
            'original_filename': filename,
            'external_participant': meta['participant_slug'],
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'status': 'pending'
        }
        path = write_request_json(payload, meta['meeting_id'])
        print(path)
    elif cmd == 'sanitize':
        name = sys.argv[2]
        print(sanitize_filename(name))
    else:
        print('Usage: transcript_util.py [dedup|mark|meta|sanitize] ...', file=sys.stderr)
        sys.exit(2)
