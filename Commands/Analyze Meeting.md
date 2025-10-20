---
description: Process meeting notes with standard analysis blocks
tags:
  - meetings
  - analysis
  - processing
---

# Meeting Analysis

Process meeting notes using standard analysis framework.

**Instructions:**

1. Ask me which meeting to analyze (provide path to meeting notes/transcript)
2. Load `file N5/config/meeting-processing-blocks.json` for available analysis types
3. Ask me which processing blocks to apply, or use standard set:
   - B01_DETAILED_RECAP
   - B05_OUTSTANDING_QUESTIONS  
   - B08_STAKEHOLDER_INTELLIGENCE
   - B13_PLAN_OF_ACTION
   - B21_KEY_MOMENTS

**Scripts:** 
- `file N5/scripts/meeting_processor.py` - Manual processing
- `file N5/scripts/meeting_auto_processor.py` - Automated batch processing

**Output:** Individual .md files for each block in meeting directory
