# Internal Stakeholder System - TODO & Progress

**Created:** 2025-10-13  
**Status:** Foundation Complete - Ready for Generation Logic  
**Priority:** High - Foundational system enhancement

---

## Quick Status

✅ **Phases 1-2 Complete** (33% overall)
- Classification system working
- Block definitions complete
- Templates ready
- Registry updated

🚧 **Phase 3 Next** - Build generation logic for B40-B48 blocks

---

## What's Been Built

### 1. Classification Infrastructure ✅
- **Config:** `file 'N5/prefs/internal_domains.json'`
- **Classifier:** `file 'N5/scripts/utils/stakeholder_classifier.py'`
- **Principles:** `file 'N5/prefs/architectural_principles.md'`

**Capabilities:**
- Detects 3 internal meeting types (co-founder standup, team standup, strategic)
- Recognizes N5OS hashtag (#N5OS) for meeting classification
- Distinguishes strategic vs standup meetings by keywords and context

### 2. Block System ✅
- **Definitions:** `file 'N5/prefs/internal_block_definitions.json'`
- **Templates:** `file 'N5/prefs/internal_block_templates.md'`
- **Registry:** `file 'N5/prefs/block_type_registry.json'` (updated)

**New Blocks (B40-B48):**
- **B40:** Internal Decisions - Strategic/tactical with interrelationships
- **B41:** Team Coordination - Action items linked to decisions
- **B42:** Market/Competitive Intel - From internal discussions
- **B43:** Product Intelligence - Product strategy & roadmap
- **B44:** GTM/Sales Intel - Go-to-market & sales
- **B45:** Operations/Process - Tools & workflows
- **B46:** Hiring/Team - People strategy
- **B47:** Open Debates - Unresolved strategic questions
- **B48:** Strategic Memo - Executive synthesis (≥30min meetings)

### 3. Architectural Principles ✅
- **MISI Framework:** Mutually Exclusive, Collectively Exhaustive, Minimally Repeated
- **Two-Axis Decisions:** Strategic/Tactical × Decision Type
- **Cross-Referencing:** [B40.D#] for decisions, [B41.A#] for actions
- **Tactical Debate Protocol:** Resolved → B40, Unresolved → B47

---

## What's Next

### Phase 3: Generation Logic (NEXT - 3-4 hours)

**Priority Tasks:**
1. Create internal meeting block generator
2. Implement B40 decision extraction (strategic + tactical + holistic pushes)
3. Implement B41 action items with cross-references
4. Implement B42-B46 conditional generation
5. Implement B47 open debates (distinguish resolved vs unresolved)
6. Implement B48 strategic memo synthesis
7. Update meeting_auto_processor.py to route internal meetings

### Phase 4: Testing (2-3 hours)
- Test on existing internal meeting transcripts
- Validate decision extraction quality
- Verify cross-references work
- Check MISI compliance

### Phase 5: Reprocessing (2-3 hours)
- Reprocess ~10-15 existing internal meetings
- Validate quality improvements
- Update logs

### Phase 6: Internal Digest (2-4 hours) - FUTURE
- Design internal digest format
- Weekly automation
- Decision tracking over time
- Strategic evolution visualization

---

## Files to Reference

**Configuration:**
- `N5/prefs/internal_domains.json` - Domain and team config
- `N5/prefs/architectural_principles.md` - MISI framework
- `N5/prefs/internal_block_definitions.json` - Block schemas
- `N5/prefs/internal_block_templates.md` - Generation templates
- `N5/prefs/block_type_registry.json` - Registry with internal types

**Scripts:**
- `N5/scripts/utils/stakeholder_classifier.py` - Enhanced classifier
- `N5/scripts/meeting_auto_processor.py` - Needs update for routing
- `N5/scripts/meeting_core_generator.py` - May need enhancement

**Test Data:**
- `N5/test/sample_internal_transcript.txt` - For testing
- `N5/records/meetings/2025-08-27_internal-team/` - Real example

---

## Design Decisions Made

### Meeting Type Detection
1. **Co-founder standup:** 2-person meeting with Vrijen + (Logan OR Ilse)
2. **Team standup:** 3+ people, all internal, <30min OR standup keywords
3. **Strategic:** 2+ people, all internal, strategic keywords OR ≥30min

### N5OS Protocol
- Use #N5OS hashtag in event descriptions
- Classifier auto-detects and routes to internal processing
- Protocol: Add #N5OS to all internal strategic meetings

### Block Namespace
- **B01-B39:** Reserved for external stakeholder blocks
- **B40-B48:** Internal stakeholder blocks ONLY
- **B49-B99:** Available for future expansion

### Cross-Reference Format
- Decision: `[B40.D#]`
- Tactical: `[B40.T#]`
- Action: `[B41.A#]`
- Question: `[B47.Q#]`
- Past meeting: `[YYYY-MM-DD_meeting-slug/B##.ID]`

### MISI Compliance
- **B40 = PRIMARY:** All decisions live here
- **B41 = DERIVATIVE:** Actions reference B40 for context
- **B42-B46 = PRIMARY:** Domain-specific intelligence
- **B47 = PRIMARY:** Unresolved questions
- **B48 = SYNTHESIS:** Only block that synthesizes (exception to MISI for readability)

---

## Key Principles

1. **Distinguish Internal from External**
   - Internal: Strategic decisions, team accountability, evolution tracking
   - External: Relationship building, deal progression, CRM intelligence

2. **Decision Tracking**
   - Capture strategic AND tactical
   - Show interrelationships
   - Link tactical to strategic objectives

3. **Strategic Evolution**
   - Track how strategy evolves over time
   - Open debates become decisions
   - Decisions become action items
   - Cross-reference across meetings

4. **Team Accountability**
   - Clear owners for actions
   - Link actions to strategic context
   - Dependencies and blockers explicit

5. **Information Architecture**
   - MISI: No overlap, no gaps, minimal repetition
   - Cross-references instead of duplication
   - Canonical locations for each info type

---

## Success Criteria

**Phase 3 Success:**
- [ ] Internal meetings generate B40-B48 blocks (not B01-B31)
- [ ] B40 captures strategic + tactical + holistic pushes
- [ ] B41 cross-references B40 correctly
- [ ] B42-B46 generated conditionally based on topics
- [ ] B47 distinguishes resolved vs unresolved
- [ ] B48 generated for ≥30min meetings with strategic decisions
- [ ] Cross-references work across blocks

**Overall Success:**
- [ ] Can track strategic decisions across meetings
- [ ] Can see tactical execution linking to strategy
- [ ] Open debates are captured and resolved over time
- [ ] Team accountability is clear
- [ ] Information follows MISI principles
- [ ] Internal digest provides strategic evolution view

---

## Questions to Resolve

None currently - design is complete and approved.

---

## Related Documentation

**In Conversation Workspace:**
- `file '/home/.z/workspaces/con_O5K85vsnm2SKb5QG/implementation-progress-final.md'` - Detailed progress
- `file '/home/.z/workspaces/con_O5K85vsnm2SKb5QG/implementation-plan-internal-blocks.md'` - Original plan
- `file '/home/.z/workspaces/con_O5K85vsnm2SKb5QG/internal-external-block-analysis.md'` - Gap analysis

---

**Ready for Phase 3 Implementation**

*2025-10-13 3:38 PM ET*
