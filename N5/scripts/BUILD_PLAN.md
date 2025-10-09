# Meeting Processing System - Build Plan

## Phase 1: MVP (Working End-to-End)
**Goal**: Process transcript → Generate 2 useful outputs  
**Time**: 30-45 min

### Components
1. ✅ Command definition
2. ✅ Orchestrator skeleton
3. ✅ Meeting info extractor
4. 🚧 Action items extractor (NEXT)
5. 🚧 Decisions extractor
6. 🚧 Simple dashboard (minimal)
7. 🚧 Test with real transcript

### Test Criteria
- Can run: `python meeting_orchestrator.py transcript.txt --type sales --stakeholder customer_founder`
- Generates folder with structure
- Produces `action_items.md` and `decisions.md`
- Creates basic `REVIEW_FIRST.md`

---

## Phase 2: Core Intelligence (Rich Outputs)
**Goal**: Add follow-up email + stakeholder profile + insights  
**Time**: 45-60 min

### Components
1. Follow-up email generator (with voice config)
2. Key insights extractor
3. Stakeholder profile generator
4. Enhanced dashboard
5. Meeting history lookup
6. Warm intro detector

### Test Criteria
- Generates professional follow-up email
- Profile enriches CRM data
- Dashboard shows priority actions

---

## Phase 3: Automation & Polish
**Goal**: Integrate with N5 lists + email history  
**Time**: 30-45 min

### Components
1. Email history fetcher (Gmail integration)
2. List integrator (auto-populate action-items.jsonl, etc.)
3. Conditional blocks (risks, opportunities, user research, competitive intel)
4. Category-specific blocks (deal intelligence, career insights, etc.)
5. Confidence scoring
6. Error handling enhancements

### Test Criteria
- Email includes history context
- Action items auto-added to N5 lists
- All 14+ blocks working
- Graceful degradation on errors

---

## Current Status: Phase 1 in progress

### Completed
- [x] Command: `N5/commands/meeting-process.md`
- [x] Schema: `N5/schemas/meeting-metadata.schema.json`
- [x] Orchestrator: `N5/scripts/meeting_orchestrator.py`
- [x] Extractor: `N5/scripts/blocks/meeting_info_extractor.py`

### Next 3 Tasks
1. Build `action_items_extractor.py` (simple)
2. Build `decisions_extractor.py` (moderate)
3. Build minimal `dashboard_generator.py`

Then test end-to-end before adding complexity.

---

## Development Principles
1. **Make it work** (MVP)
2. **Make it right** (refactor)
3. **Make it fast** (optimize)
4. Test after each phase
5. One block at a time
