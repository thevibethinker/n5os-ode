import json
from datetime import datetime
from pathlib import Path
meetings = json.load(open('/home/workspace/N5/logs/meetings_with_followups.json'))
unsent = meetings
unsent_sorted = sorted(unsent, key=lambda x: x['meeting_date'])
content = []
content.append('# Unsent Follow-Up Emails\n')
content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}  \n**Count:** {len(unsent_sorted)} pending\n\n---\n\n")
for i,m in enumerate(unsent_sorted,1):
    content.append("## {}. **{}**\n\n- **Meeting date:** {} ({} days ago)\n- **Subject:** {}\n- **Email:** {}\n- **Action required:** {}\n- **Draft:** {}: cannot open `{}' (No such file or directory)\n\n**To drop this follow-up:** \n\n---\n\n".format(i,m['stakeholder_name'],m['meeting_date'],m['days_ago'],m['subject_line'],m['email'],m['action_steps'],m['followup_path'],m['stakeholder_name']))
outdir = Path('/home/workspace/N5/logs')
outdir.mkdir(parents=True, exist_ok=True)
path = outdir / f"unsent_followups_digest_{datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
path.write_text(''.join(content))
print(path)
