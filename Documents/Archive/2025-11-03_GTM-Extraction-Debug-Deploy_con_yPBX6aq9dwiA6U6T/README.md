---
created: 2025-11-03
conversation_id: con_yPBX6aq9dwiA6U6T
title: GTM Intelligence Database Debug, Fix, and Nuclear Reset
duration: ~2.5 hours
status: Complete
---

# GTM Intelligence Database: Debug → Fix → Deploy → Nuclear Reset

## Overview

Debugged broken GTM intelligence extraction pipeline (63% empty records), built LLM-based fix, deployed automation, performed nuclear reset to start completely fresh.

## Root Causes Identified

1. **Regex routing bug** - Line 180 substring check matched both H2 (`##`) and H3 (`###`) headers, routing mismatched formats to wrong parsers
2. **Format fragmentation** - 209 B31 files using 6 different formats, only 4 parsers
3. **Silent failures** - Failed extractions marked as "successful" with 0 insights

## Solution Built

Replaced regex-based parsing with direct LLM interpretation:
- Script presents B31 content to Zo during execution
- Zo interprets and extracts insights in real-time
- Writes structured JSON to database
- Format-agnostic, handles all variants

## Deployment

- **Script:** file `N5/scripts/gtm_extract_direct.py`
- **Automation:** Every 1 hour, 2 meetings per batch
- **Schedule ID:** 36adc023-b446-4416-a682-4ab14a90483f
- **Model:** Claude Haiku (efficient for routine processing)

## Nuclear Reset (User-Requested)

After audit revealed legacy data 69% garbage:

1. ✅ **Meetings backup** - `/home/workspace/meetings_backup_2025-11-03.tar.gz` (2.4M, 3,295 files, 228 dirs)
2. ✅ **Database wiped** - All gtm_insights and gtm_processing_registry deleted
3. ✅ **Meetings folder cleared** - All 133 meeting directories removed

## System State

- **Database:** Empty, clean slate (0 insights, 0 registry)
- **Meetings folder:** Empty `/home/workspace/Personal/Meetings/`
- **Backup:** Secured at workspace root
- **Automation:** Running, ready to process fresh data

## Next Steps

1. Determine meeting data source for reprocessing
2. Set up ingestion pipeline  
3. Test on 1-2 meetings manually
4. Monitor automated extraction

## Key Artifacts

Created in conversation workspace:
- `DEBUGGER_VERIFICATION_REPORT.md` - System audit findings
- `QUALITY_AUDIT.md` - Database quality analysis
- `WHY_REPROCESSING_EXPLAINED.md` - Extraction logic explanation
- `QUEUE_PREDICTION.md` - Next 5 meetings forecast
- `RESET_LOG.md` - Nuclear reset audit trail

## Lessons Learned

1. **P15 violation risk** - Builder claimed "Production Ready" before testing automation
2. **Trust metrics cautiously** - "insights_extracted > 0" was meaningless, records were 78% empty
3. **Audit before trusting** - "Successful" extractions were mostly garbage (title-only stubs)
4. **Nuclear reset was right call** - Can't salvage 69% empty data, better to start fresh

---

*Completed: 2025-11-03 1:28pm EST*  
*Debugger: Vibe Debugger v2.0*
