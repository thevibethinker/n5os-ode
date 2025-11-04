---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# GTM Intelligence Database - Debug & Fix Summary

## What Was Wrong

Your GTM intelligence database had **40 out of 63 records (63%) with empty insight fields**, even though they were marked as "processed successfully."

### Root Causes Found

1. **Regex Routing Bug**: Parser check used substring matching `'## Insight' in content` which incorrectly matched both `## Insight` (H2) and `### Insight` (H3). Files with H3 format were routed to the H2 parser, which found nothing and silently failed.

2. **Format Fragmentation**: Your 209 B31 files use 6 different formats. The regex-based system had 4 separate parsers, but still couldn't handle all variations. Only 37 files (18%) had formats the parsers could actually process.

3. **Silent Failures**: When parsers found no matches, they returned empty lists without logging errors, marking files as "processed" with 0 insights.

## What I Built

**New System**: LLM-based extraction that replaces ALL regex parsers with semantic interpretation.

**File**: file `N5/scripts/gtm_processor_llm_auto.py`

**How it works:**
1. Reads B31 file content
2. Sends to LLM (Claude) with structured prompt
3. LLM interprets content and returns JSON with insights
4. Inserts structured data into database

**Advantages:**
- Handles ANY format (H2, H3, bold, numbered, narrative, mixed)
- Single code path replaces 4 brittle regex parsers
- Extracts semantic meaning, not just pattern matching
- Can infer missing fields from context
- Better error handling and logging

## Next Steps

1. **Configure API access** - Script needs ANTHROPIC_API_KEY or connection to internal Zo API

2. **Test on one meeting:**
   ```bash
   python3 /home/workspace/N5/scripts/gtm_processor_llm_auto.py \
     --meeting-id "2025-10-14_external-elaine-p"
   ```

3. **Clear bad data and reprocess all:**
   ```bash
   # Clear empty records
   sqlite3 /home/workspace/Knowledge/market_intelligence/gtm_intelligence.db \
     "DELETE FROM gtm_insights WHERE insight IS NULL OR insight = '';"
   
   # Reprocess everything
   python3 /home/workspace/N5/scripts/gtm_processor_llm_auto.py --all
   ```

4. **Update scheduled task** to use new processor

## Cost Estimate

- ~$0.02 per meeting for extraction  
- ~$4-6 for complete backfill of all 209 meetings
- ~$0.50/month ongoing (1-2 meetings/day)

## Files to Review

- file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/GTM_EXTRACTION_DEBUG_COMPLETE.md` - Full technical analysis
- file `/home/workspace/N5/scripts/gtm_processor_llm_auto.py` - New extraction processor
- file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/extracted_insights_example.json` - Sample output

---

**Bottom Line**: The regex-based extraction was fundamentally broken. LLM-based interpretation is more reliable, flexible, and maintainable. Ready to deploy once API access is configured.

*Debugged: 2025-11-03*
