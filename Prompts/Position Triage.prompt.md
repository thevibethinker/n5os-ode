---
title: Position Triage
description: Review extracted position candidates, approve/reject, and promote to positions.db
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_fCxNsgBS9Vw33X2k
tool: true
tags: [positions, triage, worldview, knowledge]
---

# Position Triage

Review position candidates extracted from B32 blocks and promote approved ones to `positions.py`.

## Quick Start

```bash
# See pending candidates
python3 N5/scripts/b32_position_extractor.py list-pending

# See stats
python3 N5/scripts/b32_position_extractor.py stats
```

## Triage Workflow

For each pending candidate, you (V) decide:

### ✅ APPROVE
This is a legitimate position I hold. Add to positions.db.

**Action:**
```bash
python3 N5/scripts/positions.py add \
  --domain "<domain>" \
  --title "<short title>" \
  --insight "<the full claim/position>" \
  --stability emerging \
  --confidence 3 \
  --source-conversation "<meeting_id>"
```

Then mark as approved in candidates.jsonl.

### ➡️ EXTEND
This is related to an existing position. Add as evidence.

**Action:**
1. First find the existing position:
```bash
python3 N5/scripts/positions.py search "<keywords>"
```

2. If found, extend it:
```bash
python3 N5/scripts/positions.py extend <position_id> \
  --evidence "meeting:<meeting_id>"
```

Then mark as approved in candidates.jsonl.

### ❌ REJECT
This is noise, too tactical, a question, or not a position I hold.

**Action:** Mark as rejected in candidates.jsonl.

## Candidate Update Helper

To mark a candidate as approved or rejected:

```python
# In Python or via script
import json
from pathlib import Path

candidates_file = Path("/home/workspace/N5/data/position_candidates.jsonl")

# Read all candidates
candidates = []
with open(candidates_file) as f:
    for line in f:
        candidates.append(json.loads(line.strip()))

# Update status for specific candidate
for c in candidates:
    if c["id"] == "cand_XXXXXXXX_meeting_001":
        c["status"] = "approved"  # or "rejected"

# Write back
with open(candidates_file, "w") as f:
    for c in candidates:
        f.write(json.dumps(c) + "\n")
```

## Batch Triage Mode

When triaging multiple candidates at once:

1. I'll show you 5-10 candidates
2. For each, give a quick verdict: `A` (approve), `R` (reject), `E` (extend), `S` (skip for now)
3. I'll execute the actions

## Domain Reference

| Domain | Use For |
|--------|---------|
| `hiring-market` | Labor market dynamics, hiring practices |
| `careerspan` | Careerspan-specific product beliefs |
| `ai-automation` | AI, agents, automation, future of work |
| `founder` | Entrepreneurship, startup strategy |
| `worldview` | General life/career philosophy |
| `epistemology` | Knowledge, learning, understanding |

## Example Session

**Me:** Here are 3 pending candidates:

1. **cand_20251227_001**: "Attention is the scarcest resource in hiring"
   - Speaker: V | Stance: endorsed | Domain: hiring-market

2. **cand_20251227_002**: "Should we use email or SMS for notifications?"
   - Speaker: V | Stance: questioning | Domain: careerspan

3. **cand_20251227_003**: "Longitudinal data wins over snapshots"
   - Speaker: V | Stance: endorsed | Domain: hiring-market

**You:** 
- 1: A (strong position)
- 2: R (tactical question)
- 3: A (good position)

**Me:** 
✓ Added "Attention is the scarcest resource in hiring" to positions.db
✓ Rejected cand_20251227_002
✓ Added "Longitudinal data wins over snapshots" to positions.db

