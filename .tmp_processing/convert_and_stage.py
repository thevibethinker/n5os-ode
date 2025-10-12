from pathlib import Path
import hashlib
from docx import Document
import json

src = Path('/home/workspace/Documents/Meetings/_staging/spv-hmya-oeh-transcript-2025-10-10T17-51-00.314Z.docx')
text_out = src.with_suffix('.txt')

doc = Document(src)
full_text = []
for p in doc.paragraphs:
    full_text.append(p.text)
text = "\n".join(full_text)
text_out.write_text(text, encoding='utf-8')

# compute sha256 of original docx
h = hashlib.sha256()
with src.open('rb') as f:
    while True:
        chunk = f.read(8192)
        if not chunk:
            break
        h.update(chunk)
sha256 = h.hexdigest()

# create meeting folder
# parse date/time and stakeholder
name = src.name
parts = name.split('-transcript-')
if len(parts)==2:
    stakeholder = parts[0]
    dt = parts[1].split('Z')[0]
else:
    stakeholder = name.replace(' ','_')
    dt = 'undated'
# get date and time
if 'T' in dt:
    date_part, time_part = dt.split('T')
    hhmm = ''.join([c for c in time_part if c.isdigit()])[:4]
else:
    date_part='undated'
    hhmm='0000'

meeting_folder = Path(f'/home/workspace/Careerspan/Meetings/{date_part}_{hhmm}_general_{stakeholder}')
subdirs = ['INTELLIGENCE','DELIVERABLES/blurbs','DELIVERABLES/one_pagers','DELIVERABLES/proposals_pricing','OUTPUTS']
meeting_folder.mkdir(parents=True, exist_ok=True)
for s in subdirs:
    (meeting_folder / s).mkdir(parents=True, exist_ok=True)

# write transcript to OUTPUTS/transcript.txt
transcript_path = meeting_folder / 'OUTPUTS' / 'transcript.txt'
transcript_path.write_text(text, encoding='utf-8')

# write metadata
meta = {
    'file_name': src.name,
    'sha256': sha256,
    'blocks_generated_count': 0
}
(meeting_folder / '_metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')

print('staged_text_path:', str(text_out))
print('meeting_folder:', str(meeting_folder))
print('sha256:', sha256)
