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
# Owner indices: Kamina (0,3), Vrijen (1,2,4), Brian (4)
cta_kamina = [ctas[i] for i in [0,3] if i < len(ctas)]
cta_vrijen = [ctas[i] for i in [1,2] if i < len(ctas)]
cta_brian = [ctas[i] for i in [4] if i < len(ctas)]

due_dates = []
for cta in cta_vrijen + cta_kamina:
    if 'due_date_suggested_utc' in cta:
        due_dates.append(friendly_due(cta['due_date_suggested_utc']))

due = due_dates[0] if due_dates else 'within two business days'

# Hooks from relationship intelligence (keep tasteful)
rels = CORE.get('relationship_intelligence', [])
hooks = []
for r in rels:
    if r['category'] in ('organization', 'interest'):
        hooks.append(r['term'])
hooks = list(dict.fromkeys(hooks))[:2]

# Compose high-quality external-safe email
lines = []
lines.append('Subject: Northwell Health + Careerspan collaboration — next steps')
lines.append('')
lines.append('Hi Brian,')
lines.append('')
lines.append("Thank you for taking the time to meet today. It was great to learn about Northwell's innovative work in healthcare education and workforce development, particularly the Northwell Health Sciences High School program in Queens.")
lines.append('')
lines.append("As discussed, here are the immediate next steps:")
lines.append(f'• I will coordinate a follow-up meeting to discuss partnership opportunities in more detail by {due}.')
lines.append('')
lines.append('I believe there could be significant value in collaborating on career coaching and workforce development initiatives, especially given the healthcare industry\'s growing talent needs.')
lines.append('')
lines.append('Please let me know your availability for that follow-up discussion.')
if hooks:
    lines.append('')
    lines.append(f"P.S. I was particularly interested in the {hooks[0]} aspect of your work — it aligns well with our focus on early career development.")
lines.append('')
lines.append('Best regards,')
lines.append('Vrijen Attawar')
lines.append('Co-founder, Careerspan')

email_text = "\n".join(lines) + "\n"
(BUNDLE/"outputs"/"follow_up_email_to_brian.md").write_text(email_text, encoding='utf-8')
print(str(BUNDLE/"outputs"/"follow_up_email_to_brian.md"))