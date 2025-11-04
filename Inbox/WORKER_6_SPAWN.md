# WORKER 6: Post-Meeting Enrichment

**Orchestrator:** con_iGbYpztfBufW4szX  
**Phase:** 2  
**Estimate:** 4 hours

## Objective
Build system that enriches stakeholder profiles after meetings complete.

## Key Requirements
- Trigger: Detect transcript.jsonl creation (watcher pattern)
- Data: Read blocks (key_insights, relationship_notes, action_items)
- Output: NEW relationship_delta + regenerated relationship_context
- Separate orchestration (don't touch meeting_processor_v3)

## Deliverables
1. profile_enricher_watcher.py
2. enrich_profile_post_meeting() function
3. Update profiles.db schema
4. Scheduled task (every 30 min)

Full spec in Architect design docs.
