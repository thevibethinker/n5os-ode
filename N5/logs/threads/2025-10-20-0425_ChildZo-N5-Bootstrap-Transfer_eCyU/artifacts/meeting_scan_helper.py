import json, re, sys, glob, os
from pathlib import Path
from datetime import datetime

ROOT = Path('/home/workspace')

REQ_DIR = ROOT / 'N5/inbox/meeting_requests'
COMP_DIR = REQ_DIR / 'completed'
PROC_DIR = REQ_DIR / 'processed'
MEET_REC_DIR = ROOT / 'N5/records/meetings'
TRANSCRIPTS_DIR = ROOT / 'N5/inbox/transcripts'

EMAIL_INTERNAL_DOMAINS = {'mycareerspan.com','theapply.ai'}

slug_re = re.compile(r'[^a-z0-9]+')

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = slug_re.sub('-', s)
    s = s.strip('-')
    return s or 'unknown'

FN_TIME_RE = re.compile(r'(\d{4}-\d{2}-\d{2})t(\d{2})[-:]?(\d{2})[-:]?(\d{2})', re.I)

DATE_ONLY_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')

KEYWORDS_INTERNAL = [
    'daily team stand-up','co-founder','extended cof','bi-weekly extended','internal sync','cofounder standup'
]

REMOVE_PARTS = [
    'x vrijen','and vrijen attawar','+ logan currie','- transcript','transcript',' - '\
]


def load_existing_ids():
    paths = []
    paths += glob.glob(str(REQ_DIR / '*.json'))
    paths += glob.glob(str(COMP_DIR / '*.json'))
    paths += glob.glob(str(PROC_DIR / '*.json'))
    paths += glob.glob(str(MEET_REC_DIR / '*' / '_metadata.json'))

    g_ids = set()
    meeting_ids = set()
    for p in paths:
        try:
            with open(p,'r') as f:
                data = json.load(f)
            if isinstance(data, dict):
                gid = data.get('gdrive_id')
                mid = data.get('meeting_id') or data.get('id')
                if gid:
                    g_ids.add(str(gid))
                if mid:
                    meeting_ids.add(str(mid))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        gid = item.get('gdrive_id')
                        mid = item.get('meeting_id') or item.get('id')
                        if gid:
                            g_ids.add(str(gid))
                        if mid:
                            meeting_ids.add(str(mid))
        except Exception:
            continue
    return g_ids, meeting_ids


def parse_filename(name: str):
    base = name
    if base.lower().endswith('.docx'):
        base = base[:-5]
    # remove any leading tags like [ZO-PROCESSED]
    base = re.sub(r'^\[[^\]]+\]\s*','',base)
    # split on '-transcript-'
    parts = base.split('-transcript-')
    left = parts[0]
    right = parts[1] if len(parts)>1 else ''
    # date/time
    m = FN_TIME_RE.search(right.replace('_', '-'))
    dt = None
    date_s = None
    time_hms = None
    if m:
        date_s = m.group(1)
        time_hms = f"{m.group(2)}:{m.group(3)}:{m.group(4)}"
    else:
        m2 = DATE_ONLY_RE.search(right)
        if m2:
            date_s = m2.group(1)
    # participants string
    participants = left.strip()
    return {
        'date': date_s,
        'time': time_hms,
        'participants_raw': participants
    }


def classify_internal(participants: str) -> bool:
    p = participants.lower()
    return any(k in p for k in KEYWORDS_INTERNAL)


def external_slug(participants: str) -> str:
    q = participants.lower()
    for rem in REMOVE_PARTS:
        q = q.replace(rem, ' ')
    q = re.sub(r'\s+',' ', q)
    return slugify(q)


def ensure_unique_meeting_id(base_id: str, have_ids: set, time_hms: str | None):
    if base_id not in have_ids:
        return base_id
    if time_hms:
        tag = time_hms.replace(':','')
        candidate = f"{base_id}_{tag}"
        if candidate not in have_ids:
            return candidate
    # fallback with index
    i = 2
    cand = f"{base_id}-{i}"
    while cand in have_ids:
        i += 1
        cand = f"{base_id}-{i}"
    return cand


def build_request(meeting_id: str, classification: str, participants: str, date_s: str, gdrive_id: str, gdrive_link: str, original_filename: str, external_slug_val: str | None):
    now = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    req = {
        'meeting_id': meeting_id,
        'classification': classification,
        'participants': participants,
        'date': date_s,
        'gdrive_id': gdrive_id,
        'gdrive_link': gdrive_link,
        'original_filename': original_filename,
        'created_at': now,
        'status': 'pending'
    }
    if classification == 'external' and external_slug_val:
        req['external_participant'] = external_slug_val
    return req


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--drive-json', required=True, help='Path to JSON file with Google Drive list (array of {id,name,...})')
    ap.add_argument('--out-plan', required=True, help='Write plan JSON here')
    args = ap.parse_args()

    with open(args.drive_json,'r') as f:
        files = json.load(f)

    existing_gids, existing_mids = load_existing_ids()

    plan = {
        'skip_ids': [],
        'new': [],
    }

    for item in files:
        fid = item['id']
        name = item['name']
        if name.startswith('[ZO-PROCESSED]') or name.startswith('[INTERNAL-SKIPPED]'):
            plan['skip_ids'].append({'id':fid,'name':name,'reason':'prefixed-processed'})
            continue
        if fid in existing_gids:
            plan['skip_ids'].append({'id':fid,'name':name,'reason':'duplicate-gdrive-id'})
            continue
        meta = parse_filename(name)
        date_s = meta['date'] or datetime.utcnow().date().isoformat()
        time_hms = meta['time']
        participants = meta['participants_raw']
        is_internal = classify_internal(participants)
        classification = 'internal' if is_internal else 'external'
        if is_internal:
            base_id = f"{date_s}_internal-team"
            ext_slug = None
        else:
            ext_slug = external_slug(participants)
            base_id = f"{date_s}_external-{ext_slug}"
        meeting_id = ensure_unique_meeting_id(base_id, existing_mids, time_hms)
        existing_mids.add(meeting_id)
        plan['new'].append({
            'file': item,
            'meeting_id': meeting_id,
            'classification': classification,
            'participants': participants,
            'date': date_s,
            'time': time_hms,
            'external_slug': ext_slug
        })

    Path(args.out_plan).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_plan,'w') as f:
        json.dump(plan,f)
    print(args.out_plan)

if __name__ == '__main__':
    main()
