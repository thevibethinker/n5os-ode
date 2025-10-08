#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

BUNDLE = Path(__file__).resolve().parent.parent
CORE = json.loads((BUNDLE/'core_map.json').read_text(encoding='utf-8'))
OPER = json.loads((BUNDLE/'operational_map.json').read_text(encoding='utf-8'))

# Helpers

def friendly_due(dt_iso: str) -> str:
    try:
        return datetime.fromisoformat(dt_iso.replace('Z','+00:00')).strftime('%a, %b %d')
    except Exception:
        return 'within two business days'

# Pull facts
ctas = OPER.get('ctas', [])
# Owner indices: Logan (0,2,3), Shujaat (1), Vrijen (4)
cta_logan = [ctas[i] for i in [0,2,3] if i < len(ctas)]
cta_vrijen = ctas[4] if len(ctas) > 4 else None

due = friendly_due(cta_vrijen.get('due_date_suggested_utc','')) if cta_vrijen else 'within two business days'

# Hooks from relationship intelligence (keep tasteful)
rels = CORE.get('relationship_intelligence', [])
hooks = []
for r in rels:
    if r['category'] == 'media' and r['term'] in ('Interstate 60','Legend of Korra'):
        hooks.append(r['term'])
hooks = list(dict.fromkeys(hooks))[:2]

# Compose high-quality external-safe email
lines = []
lines.append('Subject: SDT paper + pilot options — quick next steps (PM‑first)')
lines.append('')
lines.append('Hi Shujaat,')
lines.append('')
lines.append("Thanks for the meeting today. I enjoyed learning about your perspective on career development and the international experience as 'base athleticism' for PMs.")
lines.append('')
lines.append("Here are the immediate next steps:")
lines.append('• I will send the SDT paper so you have something concrete to review.')
lines.append(f'• I will share a quick options memo with two pilot paths and success metrics by {due}.')
lines.append('')
lines.append('I believe this could be valuable for both of us — building stronger PM capabilities while exploring collaboration opportunities.')
lines.append('')
lines.append('Please take a look at the SDT materials and let me know your thoughts. We can schedule a 30-minute call to discuss the pilot options.')
if hooks:
    lines.append('')
    lines.append(f"P.S. I noticed the {hooks[0]} reference — great insight on building resilience through diverse experiences.")
lines.append('')
lines.append('Best regards,')
lines.append('Vrijen Attawar')
lines.append('Co-founder, Careerspan')

email_text = "\n".join(lines) + "\n"
(BUNDLE/"outputs"/"follow_up_email_to_shujaat_llm_v4.md").write_text(email_text, encoding='utf-8')
print(str(BUNDLE/"outputs"/"follow_up_email_to_shujaat_llm_v4.md"))