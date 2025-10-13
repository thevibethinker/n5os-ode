import json,os,re
from pathlib import Path
meeting_id = "2025-09-05_external-malvika-jethmalani"
base = Path('/home/workspace')
meeting_folder = base / 'N5' / 'records' / 'meetings' / meeting_id
meeting_folder.mkdir(parents=True,exist_ok=True)
transcript_path = base / 'N5' / 'inbox' / 'transcripts' / (meeting_id + '.md')
text = transcript_path.read_text()
# simple speaker-segment extraction
segments = re.split(r"\n\n\d{2}:\d{2}\n", "\n\n"+text)
# extract metrics
metrics = []
for m in re.finditer(r"(\d{1,3}%|\d{1,3}(?:,\d{3})+|\d+ members|over a thousand hours|\d+\s+hours|\d{1,3}% open rate|\d+% click|\d+% click through rate|\d+% click-through rate|\d{1,3} members)", text, re.I):
    metrics.append(m.group(0))
metrics = list(dict.fromkeys(metrics))
# Build blocks
blocks = {}
blocks['B26_MEETING_METADATA_SUMMARY.md'] = f"""# B26 - MEETING_METADATA_SUMMARY

Title: Malvika Jethmalani x Vrijen — Community/partnership exploration
Stakeholder Type: FOUNDER
Confidence: High
V-OS Tags: [LD-FND] [GPT-E] [A-2]
Transcript Quality: Good
"""
# B01
b01 = "# B01 - DETAILED_RECAP\n\n---\n\n## Key Decisions and Agreements\n"
b01 += "- Explore community partnership between Careerspan and Women Shaping AI (trial code + dedicated community code).\n"
b01 += "- Malvika will introduce Logan and provide a dedicated code for the community; will share links to HR communities.\n"
b01 += "- Offer trial code to Malvika's VC client and community members; track engagement.\n"
b01 += "\n## Strategic Context\n"
b01 += "Malvika runs a community of senior women in AI and is positioning Careerspan as a candidate-centric matching and narrative tool connecting communities to jobs. The meeting surfaced clear partnership levers: community distribution, private job pipelines, and potential virtual event with Logan.\n"
b01 += "\n## Critical Next Action\n- Owner: Malvika -> Deliverable: Dedicated community code + blurb -> When: ASAP -> Purpose: community trial and tracking\n- Owner: Vrijen -> Deliverable: share community link and follow-up with Logan intro -> When: ASAP -> Purpose: event coordination\n"
blocks['B01_DETAILED_RECAP.md'] = b01
# B02
b02 = "# B02 - COMMITMENTS_CONTEXTUAL\n\nOwner | Deliverable | Context/Why | Due Date | Dependencies\n---|---|---|---|---\nMalvika | Dedicated community code & blurb | To onboard community & track engagement | [ASAP] | None\nVrijen | Share community link & coordinate follow-up with Logan | Event coordination & introductions | [ASAP] | Contact details for Logan\nMalvika | Send links to HR communities | Expand outreach & feedback | [TBD] | Confirmation of links\n"
blocks['B02_COMMITMENTS_CONTEXTUAL.md'] = b02
# B08
b08 = "# B08 - STAKEHOLDER_INTELLIGENCE\n\n---\n\n## Foundational Profile\n- Name: Malvika Jethmalani\n- Role: Founder / community leader\n- Organization: Women Shaping AI (global community)\n- Community size: 170 members across 15+ countries\n- Motivation: Candidate-centric experiences; help underrepresented professionals surface strengths\n- Funding Status: [Unknown]\n- Key Challenges: Making qualitative strengths visible; distribution & engagement; converting community into monetizable placements\n\n## What Resonated\n- Candidate-centric framing and narrative-building as core product strength.\n- Strong community engagement signals (high open rates referenced).\n\n## CRM Integration\n- Profile will be created at Knowledge/crm/individuals/malvika-jethmalani.md\n- Enrichment Priority: HIGH\n\n## Howie Tags\n- Recommended: [LD-FND] [GPT-E] [A-2]  (Exploratory founder partnership, flexible scheduling)\n"
blocks['B08_STAKEHOLDER_INTELLIGENCE.md'] = b08
# B21
b21 = "# B21 - KEY_MOMENTS\n\n---\n\n## Memorable Quotes\n- (00:00) Malvika: 'I think right now could be a potentially transformative moment for this industry.'\n- (03:10) Malvika: 'The average career span user that engages with our coach tells almost an hour\'s worth of stories to the AI.'\n\n## Salient Questions\n- Who should we be talking to / who to get in front of? (asks for introductions to HR communities)\n"
blocks['B21_KEY_MOMENTS.md'] = b21
# B31
b31 = "# B31 - STAKEHOLDER_RESEARCH\n\nPerspective: Founder / community operator\n\n1. Community-first distribution works: Evidence - high engagement metrics (email open 85-90%, CTR ~16%).\n   - Why it matters: Community channels provide high signal candidate pools and monetization pathways.\n\n2. Narrative & qualitative strengths are under-served by resumes.\n   - Why it matters: Product differentiation lies in enabling story banks and narrative framing.\n\n3. Competitive landscape includes Boardie/Bordie - watch positioning and event strategies.\n"
blocks['B31_STAKEHOLDER_RESEARCH.md'] = b31
# B25
b25 = "# B25 - DELIVERABLE_CONTENT_MAP\n\n## Deliverable Content Map\nItem | Promised By | Promised When | Status | Send with Email\n---|---|---|---|---\nDedicated community code & blurb | Malvika | ASAP | HAVE | Yes\nTrial code for VC client | Malvika | ASAP | HAVE | Yes\nCommunity event with Logan (virtual) | Malvika + Logan | TBD | NEED | No\nLinks to HR communities | Malvika | TBD | NEED | No\n\n---\n\n## Follow-Up Email Draft\nSubject: Follow-Up: Malvika Jethmalani x Careerspan • Community partnership\n\nHi Malvika,\n\nGreat to connect — I loved hearing about Women Shaping AI and your work bringing senior women together. Thank you for offering a dedicated community code and for the offer to share Careerspan with your VC client and members.\n\nRecap:\n- You will provide a dedicated community code and a short blurb to distribute to the community.\n- I will share the community link and coordinate a follow-up involving Logan to discuss a virtual event.\n\nNext steps:\n1) Malvika: Send the dedicated code + blurb (ASAP)\n2) Vrijen: Share community link and propose times to include Logan\n\nAppreciate the warm intro and excited to test this with your community — looking forward to continued conversation.\n\nBest,\nVrijen\n"
blocks['B25_DELIVERABLE_CONTENT_MAP.md'] = b25
# B05
b05 = "# B05 - OUTSTANDING_QUESTIONS\n\n- Who is the primary contact at Communities (for distribution integrations)? - Owner: Malvika - Needed by: [TBD]\n- What metrics will define success for the trial (engagement thresholds, placement rate)? - Owner: Joint - Needed by: Before pilot\n"
blocks['B05_OUTSTANDING_QUESTIONS.md'] = b05
# B14
b14 = "# B14 - BLURBS_REQUESTED\n\n**Suggested blurb (for Women Shaping AI community):**\n\nCareerspan is a candidate-centered platform that helps professionals surface the stories and experiences that don\'t fit neatly on a resume. They\'re offering an exclusive trial for Women Shaping AI members — submit your stories and receive tailored narrative framing and job matching support.\n\n(If you\'d like the blurb shortened or tailored, let me know.)\n"
blocks['B14_BLURBS_REQUESTED.md'] = b14
# B11
b11 = "# B11 - METRICS_SNAPSHOT\n\n- Community members: 170 members across 15+ countries\n- Engagement: Email open rate 85-90%\n- Click-through rate: ~16%\n- User engagement: \"over a thousand hours of coaching recorded\"; average session ~1 hour\n"
blocks['B11_METRICS_SNAPSHOT.md'] = b11
# write files
for name,content in blocks.items():
    (meeting_folder / name).write_text(content)
# create CRM profile
crm_folder = base / 'Knowledge' / 'crm' / 'individuals'
crm_folder.mkdir(parents=True,exist_ok=True)
crm_path = crm_folder / 'malvika-jethmalani.md'
crm_content = "# Malvika Jethmalani\n- Role: Founder, Women Shaping AI\n- Community: 170 members (15+ countries)\n- Notes: Interested in community partnership, will provide dedicated code and blurb; potential event with Logan; offered trial to VC client.\n- Enrichment Priority: HIGH\n"
crm_path.write_text(crm_content)
# metadata
meta = {
    'meeting_id': meeting_id,
    'processed_by': 'Zo',
    'stakeholder_type': 'FOUNDER',
    'blocks_generated': len(list(meeting_folder.iterdir())),
    'crm_created': True
}
(meeting_folder / '_metadata.json').write_text(json.dumps(meta,indent=2))
print('DONE')
