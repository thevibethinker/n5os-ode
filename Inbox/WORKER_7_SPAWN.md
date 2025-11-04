# WORKER 7: Warm Intro Tracking

**Orchestrator:** con_iGbYpztfBufW4szX  
**Phase:** 2  
**Estimate:** 3 hours

## Objective
Detect warm intro opportunities and track them for follow-up.

## Key Requirements
- Use LLM (not regex) to detect warm intro promises
- Extract: who promised, to whom, target person/org, timeline
- Store in warm_intros table
- Generate actionable follow-up tasks

## Deliverables
1. Update warm_intro_detector.py (currently stub)
2. warm_intros table in profiles.db
3. Integration with meeting_processor_v3 blocks
4. Detection quality: V wants "master with warm intros"

Full spec in Architect design docs.
