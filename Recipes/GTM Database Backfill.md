---
description: Process unprocessed B31 files into GTM intelligence database
tags: [gtm, intelligence, backfill]
---

# GTM Database Backfill

**Purpose**: Extract insights from unprocessed B31 files into structured database

---

## Instructions

Process all unprocessed GTM meetings in batches.

**For EACH meeting with B31 file:**

1. **Read** `file 'Personal/Meetings/{meeting_id}/B31_STAKEHOLDER_RESEARCH.md'`

2. **Extract insights** with this structure:
   - Meeting: meeting_id, date
   - Stakeholder: name, role, type (infer: recruiter/founder/consultant/hiring_manager/big_company)
   - Per insight: category, signal_strength (count ● symbols), title, full text, why_it_matters, quote, confidence_level

3. **Insert to database**:
```python
import sqlite3
conn = sqlite3.connect("/home/workspace/Knowledge/market_intelligence/gtm_intelligence.db")
cursor = conn.cursor()

# For each insight
cursor.execute("""
    INSERT INTO gtm_insights (
        meeting_id, meeting_date, source_b31_path,
        stakeholder_name, stakeholder_role, stakeholder_type,
        category, signal_strength,
        title, insight, why_it_matters, quote, confidence_level
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", values)

# After all insights from meeting
cursor.execute("""
    INSERT INTO gtm_processing_registry (meeting_id, b31_path, insights_extracted)
    VALUES (?, ?, ?)
""", (meeting_id, b31_path, insight_count))

conn.commit()
conn.close()
```

4. **Report progress** after each batch of 10

---

## Get Unprocessed List

```bash
python3 /home/workspace/N5/scripts/gtm_worker.py
```

---

## Critical Rules

- **NO rewriting** - Extract text exactly as written
- **Signal strength** - Count filled circles (●●●●○ = 4)
- **Categories** - Use exact category from B31 or map to standard:
  - GTM & Distribution
  - Product Strategy
  - Market Pain Points
  - Founder/Recruiter/Hiring Manager Pain Points
  - Competitive Landscape
  - Fundraising & Business Model

---

**Process ALL batches sequentially. Report total insights extracted at end.**
