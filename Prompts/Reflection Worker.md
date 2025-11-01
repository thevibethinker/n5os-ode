---
description: 'Command: reflection-worker'
tags: []
---
# Reflection Worker (Manual)

## Usage
```
python3 N5/scripts/reflection_worker.py --file /home/workspace/N5/records/reflections/incoming/<audio>
```

## Steps
1) Transcribe audio → `<audio>.transcript.jsonl`
2) Generate Summary + Detailed Recap → `outputs/<slug>/summary.md`, `detail.md`
3) Classify reflection types and select voice profile
4) Update Registry (status `awaiting-approval`)
5) Generate Multi-Angle Proposal → `Records/Reflections/Proposals/<slug>_proposal.md`
6) Extract Semi-Stable Beliefs → `Knowledge/V-Beliefs/<slug>.md`

## Notes
- Only email back if there are questions or issues.
- Final content will be generated only after V selects options.
