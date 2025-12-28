# Meeting Pipeline V2 - Final Build Plan (Approach B)

**Build Orchestrator:** con_gEITMa8CweOAFip5  
**Architecture:** Script as Zo Agent (Integrated Intelligence)  
**Created:** 2025-10-31 21:52 ET

---

## Architecture Summary

**Single Agent Pattern:** transcript_processor.py runs as Zo agent
- Phase 1: Python reads new transcripts
- Phase 2: Zo analyzes + selects blocks intelligently
- Phase 3: Python queues blocks to block_registry.db
- Phase 4: Zo generates queued blocks one-by-one
- Phase 5: Python finalizes + notifies V

**Two Databases:**
- meeting_pipeline.db: Meeting lifecycle tracking
- block_registry.db: Block queue + completed blocks

**Trigger:** Scheduled task every 30 minutes

---

## Build Workers (Revised)

### ✅ BUILD_WORKER_1: Database Foundation (COMPLETE)
- meeting_pipeline.db created
- block_selector.py functional
- Test data inserted

### ⏳ BUILD_WORKER_2: Block Generation Tools (75% COMPLETE)
**Remaining:** Finish Approach B integration
- Create block_registry.db schema
- Create intelligent block selector prompt
- Update stage_2_generator.py for Approach B pattern

### 🔲 BUILD_WORKER_3: Transcript Processor Script
- transcript_processor.py (main script as Zo agent)
- Integrates transcript detection + block selection + generation
- Runs as single conversation workflow

### 🔲 BUILD_WORKER_4: Scheduled Trigger
- Create scheduled task (every 30 min)
- Launches transcript_processor as Zo agent
- Monitors completion + notifies V

### 🔲 BUILD_WORKER_5: Testing + Documentation
- End-to-end test with Lisa Noble meeting
- Documentation for manual invocation
- Validation of 30-60 min SLA

---

## Next Action

Complete BUILD_WORKER_2 with:
1. block_registry.db schema
2. Intelligent block selector prompt
3. Approach B architecture proof of concept

Then proceed sequentially to W3, W4, W5.

