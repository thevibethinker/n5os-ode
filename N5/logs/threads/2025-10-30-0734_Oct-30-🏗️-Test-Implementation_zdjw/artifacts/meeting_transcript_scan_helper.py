#!/usr/bin/env python3
import sys, json, re, os, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

WORKSPACE = Path('/home/workspace')
INBOX_REQ = WORKSPACE / 'N5/inbox/meeting_requests'
INBOX_REQ_PROCESSED = INBOX_REQ / 'processed'
RECORDS_MEETINGS = WORKSPACE / 'N5/records/meetings'
INBOX_TRANSCRIPTS = WORKSPACE / 'N5/inbox/transcripts'

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

SAFE_CHARS = re.compile(r"[^A-Za-z0-9._ -]+")

def sanitize_filename(name: str) -> str:
    s = name.strip().replace('/', '-').replace('\n', ' ')
    s = SAFE_CHARS.sub('_', s)
    s = re.sub(r"\s+", ' ', s)
    return s

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", '-', s)
    s = s.strip('-')
    return s or 'unknown'

def load_dedup_ids():
    ids = set()
    # Scan request jsons
    for p in INBOX_REQ.rglob('*_request.json'):
        try:
            data = json.loads(p.read_text())
            gid = data.get('gdrive_id')
            if gid:
                ids.add(gid)
        except Exception:
            pass
    # Scan records metadata
    for p in RECORDS_MEETINGS.rglob('_metadata.json'):
        try:
            data = json.loads(p.read_text())
            gid = data.get('gdrive_id')
            if gid:
                ids.add(gid)
        except Exception:
            pass
    return ids

def find_completed_meetings():
    completed = []  # list of {gdrive_id, blocks_count}
    for p in RECORDS_MEETINGS.rglob('_metadata.json'):
        try:
            data = json.loads(p.read_text())
            bc = data.get('blocks_count')
            gid = data.get('gdrive_id')
            if gid and isinstance(bc, int) and bc > 0:
                completed.append({'gdrive_id': gid, 'blocks_count': bc})
        except Exception:
            pass
    return completed

def extract_metadata_from_name(name: str):
    # date
    m = DATE_RE.search(name)
    date = m.group(1) if m else None
    lower = name.lower()
    # participants: before "-transcript-" or " transcript "
    parts_anchor = None
    for anchor in ['-transcript-', ' transcript ', '_transcript_']:
        idx = lower.find(anchor)
        if idx != -1:
            parts_anchor = idx
            break
    participants = name[:parts_anchor].strip() if parts_anchor is not None else name.strip()
    # classification
    classification = 'internal' if ('daily team stand-up' in lower or 'internal-team' in lower) else 'external'
    # external participant slug (fallback to participants)
    cleaned = participants
    for token in ['internal-team', 'daily team stand-up']:
        cleaned = re.sub(token, '', cleaned, flags=re.IGNORECASE)
    participant_slug = slugify(cleaned)
    return date, participants, classification, participant_slug

def ensure_dirs():
    INBOX_TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    INBOX_REQ_PROCESSED.mkdir(parents=True, exist_ok=True)


def main():
    input_str = sys.stdin.read().strip()
    files = json.loads(input_str) if input_str else []
    ensure_dirs()
    dedup_ids = load_dedup_ids()
    completed = find_completed_meetings()

    to_download = []
    queued = []
    skipped = []

    now_et = datetime.datetime.now(ZoneInfo('America/New_York')).isoformat()

    for f in files:
        fid = f.get('id')
        name = f.get('name') or ''
        if not fid or not name:
            continue
        if fid in dedup_ids or name.startswith('[ZO-PROCESSED]'):
            skipped.append({'id': fid, 'name': name, 'reason': 'dedup_or_marked'})
            continue
        # Create sanitized filename and request JSON
        sanitized = sanitize_filename(name)
        download_path = str(INBOX_TRANSCRIPTS / sanitized)

        # Extract metadata
        date, participants, classification, participant_slug = extract_metadata_from_name(name)
        if not date:
            # fallback: use modifiedTime date if available? leave None
            pass
        meeting_id = f"{date or 'unknown'}_{classification}-{participant_slug}"
        request_path = INBOX_REQ_PROCESSED / f"{meeting_id}_request.json"
        req = {
            'meeting_id': meeting_id,
            'classification': classification,
            'participants': participants,
            'date': date,
            'gdrive_id': fid,
            'gdrive_link': f.get('webViewLink'),
            'original_filename': name,
            'external_participant': participant_slug,
            'created_at': now_et,
            'status': 'pending'
        }
        try:
            request_path.write_text(json.dumps(req, indent=2))
            queued.append({'meeting_id': meeting_id, 'request_path': str(request_path)})
            to_download.append({'id': fid, 'name': name, 'download_path': download_path})
        except Exception as e:
            skipped.append({'id': fid, 'name': name, 'reason': f'write_failed:{e}'})
            continue

    out = {
        'dedup_count': len(dedup_ids),
        'to_download': to_download,
        'queued_count': len(queued),
        'queued': queued,
        'skipped_count': len(skipped),
        'skipped': skipped,
        'completed_ready': completed
    }
    print(json.dumps(out))

if __name__ == '__main__':
    main()
