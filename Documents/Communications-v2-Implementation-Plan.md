---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
---

# Communications Architecture v2 - Implementation Plan

**Created:** 2025-11-16 14:18 EST  
**Status:** Ready for execution  
**Goal:** Integrate voice transformation system, update registries, add [R] state, create scheduled task

---

## Updates Based on Feedback

### Key Changes from V:

1. **Voice Transformation System Integration**
   - Use existing transformation system (`file 'N5/prefs/communication/voice-transformation-system.md'`)
   - Apply "polished version of V's voice" to all communications
   - Few-shot learning approach (style-free → transformed)
   - Multi-angle evaluation before selecting best output

2. **Scheduled Task Creation**
   - Create scheduled task to run communications generator automatically
   - Scan for meetings in [P] state
   - Trigger when B14 or B25 exists
   - Move to [R] state after completion

3. **Registry Updates**
   - Update `block_type_registry.json` with B14 v2 and B25 v2 definitions
   - Ensure guidance matches new intelligence-only approach

4. **State Machine Enhancement**
   - Add [R] state support across system
   - Update folder renaming logic
   - Add state transition tracking

---

## Implementation Phases

### PHASE 1: Core System Updates (30-45 min)
**Goal:** Update registries, add [R] state, integrate voice system

**Tasks:**

**1.1 Update Block Registry**
- File: `N5/prefs/block_type_registry.json`
- Action: Replace B14 and B25 guidance with v2 definitions
- Verification: Validate JSON syntax, test block generation

**1.2 Update Communications Generator Prompt**
- File: `Prompts/communications-generator.prompt.md`
- Action: Integrate voice transformation system
- Changes:
  - Add voice transformation system loading
  - Include few-shot transformation pairs
  - Add multi-angle generation
  - Add quality validation against voice anti-patterns

**1.3 Add [R] State Support**
- Files to update:
  - State management scripts (if exist)
  - Block generator prompt (state transition logic)
  - Any folder renaming utilities
- Action: Add [R] as valid state, update all state checks

---

### PHASE 2: Scheduled Task Creation (15-20 min)
**Goal:** Create automated agent to run communications generator

**2.1 Create Scheduled Task**
- Use: `create_scheduled_task` tool
- Schedule: Every 2 hours (or as V prefers)
- Instruction: Comprehensive execution instructions
- Delivery: Email (or none, as V prefers)

**2.2 Task Instruction Template**
```
Scan for meetings in [P] state that need communications generation.

Process:
1. Find meetings in /home/workspace/Personal/Meetings with [P] suffix
2. Check each meeting for B14 or B25 existence
3. Load voice transformation system from N5/prefs/communication/
4. Load context from Knowledge/current/
5. Generate communications using transformation system
6. Validate output quality
7. Move folder from [P] to [R] state
8. Log completion

Generate brief summary of meetings processed.
```

---

### PHASE 3: Testing & Validation (20-30 min)
**Goal:** Test on real meetings, validate quality

**3.1 Manual Test Run**
- Select 2 recent meetings with B14 or B25
- Run communications generator manually
- Validate:
  - Voice transformation applied correctly
  - Knowledge/current/ context incorporated
  - Output quality meets standards
  - State transition works

**3.2 Scheduled Task Test**
- Run scheduled task once manually
- Verify:
  - Discovers meetings correctly
  - Processes them in batch
  - Logs completion
  - Doesn't fail on edge cases

---

### PHASE 4: Documentation & Cleanup (10-15 min)
**Goal:** Update docs, clean up artifacts

**4.1 Update Architecture Doc**
- Mark Phase 1 tasks complete
- Document any deviations
- Update next steps

**4.2 Clean Up**
- Remove any test artifacts
- Archive old versions if needed
- Update SESSION_STATE

---

## Detailed Task Breakdown

### Task 1: Update block_type_registry.json

**File:** `file 'N5/prefs/block_type_registry.json'`

**Action:** Update B14 and B25 entries

**B14 Update:**
```json
{
  "B14": {
    "name": "BLURBS_REQUESTED",
    "type": "CONDITIONAL",
    "priority": "Generate when blurbs/descriptions explicitly requested",
    "length": "100-200 words",
    "guidance": [
      "PURPOSE: Intelligence extraction ONLY. Track what blurbs, descriptions, one-pagers, or materials were explicitly requested, by whom, and for what purpose.",
      "",
      "NOTE: This block does NOT generate the actual blurbs. Blurb generation happens in Pipeline 2 (Communications Generator) with full Careerspan context.",
      "",
      "STRUCTURE: Simple list format",
      "1. [Type of Material]",
      "   - Requested by: [Name/Role]",
      "   - Purpose: [What they want to do with it]",
      "   - Target audience: [Who will read it]",
      "   - Deadline: [If specified]",
      "   - Key focus: [What to emphasize]",
      "",
      "VALIDATION:",
      "- Each request has all 5 fields filled",
      "- Type of material is specific and actionable",
      "- No actual blurb content included (intelligence only)",
      "- Length is 100-200 words"
    ]
  }
}
```

**B25 Update:**
```json
{
  "B25": {
    "name": "DELIVERABLE_CONTENT_MAP",
    "type": "REQUIRED",
    "priority": "Generate for every meeting",
    "length": "100-200 words",
    "guidance": [
      "PURPOSE: Intelligence extraction ONLY. Map what deliverables, resources, or materials were promised, by whom, and when.",
      "",
      "NOTE: This block does NOT generate the follow-up email. Email generation happens in Pipeline 2 (Communications Generator) with full Careerspan context.",
      "",
      "STRUCTURE: Simple table format",
      "| Item | Promised By | To Whom | Due Date | Status | Notes |",
      "|------|-------------|---------|----------|--------|-------|",
      "",
      "FOLLOW-UP FLAG:",
      "Follow-Up Email Needed? [YES/NO]",
      "",
      "VALIDATION:",
      "- Table has all promised deliverables (or explicitly notes 'None')",
      "- Each row has all 6 fields filled",
      "- Follow-up email flag is clearly YES or NO",
      "- No email content included (intelligence only)",
      "- Length is 100-200 words"
    ]
  }
}
```

**Verification:**
```bash
# Validate JSON syntax
python3 -m json.tool /home/workspace/N5/prefs/block_type_registry.json > /dev/null

# Check B14 and B25 exist
jq '.blocks.B14, .blocks.B25' /home/workspace/N5/prefs/block_type_registry.json
```

---

### Task 2: Update Communications Generator with Voice System

**File:** `file 'Prompts/communications-generator.prompt.md'`

**Updates Needed:**

**2.1 Add Voice System Loading Section:**

```markdown
## Voice Transformation System

**CRITICAL:** All communications MUST use V's authentic voice through transformation system.

### System Files
- Transformation system: `file 'N5/prefs/communication/voice-transformation-system.md'`
- Voice profiles: `file 'N5/prefs/communication/voice-profiles.json'`
- Few-shot examples: Built into transformation system

### Process
1. **Style-Free Draft:** Generate factual, personality-free content first
2. **Load Transformation Pairs:** Use 2-3 relevant few-shot examples from system
3. **Transform:** Apply learned pattern to generate V's voice
4. **Validate:** Check against voice anti-patterns and quality criteria

### For Follow-Up Emails
**Profile:** Email (professional, warm, action-oriented)
**Examples:** PAIR 1, 2, 3, 5 from transformation system
**Validation:**
- Opens with warmth or rapport
- Uses specific details for credibility
- Reduces pressure on recipient
- Natural transitions
- Personality without being performative
- Avoids all anti-patterns (no emoji, no corporate jargon, no performative vulnerability)

### For Blurbs
**Profile:** Doc/professional (clear, accurate, well-structured)
**Adaptation:** More formal than email, less conversational than social
**Validation:**
- Extremely high accuracy (no placeholders, no hallucinations)
- Current Careerspan positioning incorporated
- Appropriate tone for target audience
- Copy-paste ready
```

**2.2 Update Context Loading Section:**

```markdown
### 2. Careerspan Context & Voice System
```bash
# Load ALL documents from Knowledge/current/
find /home/workspace/Knowledge/current -type f -name "*.md" -o -name "*.txt"

# Load voice transformation system
cat /home/workspace/N5/prefs/communication/voice-transformation-system.md
```
```

**2.3 Update Generation Requirements:**

Add to both email and blurbs sections:

```markdown
**Voice Quality:**
- [ ] Uses transformation system (style-free → voiced)
- [ ] Matches V's authentic patterns (from few-shot examples)
- [ ] No anti-patterns present
- [ ] Sounds like something V would actually write
- [ ] Natural flow (not choppy or generic)
```

---

### Task 3: Add [R] State Support

**Files to Update:**

**3.1 Block Generator Prompt**
File: `Prompts/meeting-block-generator.prompt.md`

Add state transition logic:
```markdown
## State Transitions

**[M] → [P]:**
- All blocks in manifest generated
- Validates all blocks present
- Renames folder from [M] to [P]
- Checks: Does B14 or B25 exist?
  - If YES: Log "Communications needed"
  - If NO: Log "No communications needed"

**[P] → [R]:**
- Communications generator completes (if triggered)
- FOLLOW_UP_EMAIL.md exists (if B25 triggered)
- BLURBS_GENERATED.md exists (if B14 triggered)
- Renames folder from [P] to [R]
```

**3.2 State Management Scripts**
If state management scripts exist, add [R] to valid states list.

Search for existing scripts:
```bash
find /home/workspace/N5/scripts -name "*state*" -o -name "*meeting*manager*"
```

---

### Task 4: Create Scheduled Task

**Tool:** `create_scheduled_task`

**Parameters:**

**Schedule:** Every 2 hours (RRULE)
```
FREQ=HOURLY;INTERVAL=2;BYHOUR=8,10,12,14,16,18,20
```
(Runs: 8am, 10am, 12pm, 2pm, 4pm, 6pm, 8pm EST)

**Instruction:**
```markdown
Run the communications generator for meetings ready for outbound communications.

CONTEXT FILES TO LOAD:
1. Voice transformation system: file 'N5/prefs/communication/voice-transformation-system.md'
2. Communications generator prompt: file 'Prompts/communications-generator.prompt.md'
3. Current Careerspan context: All files in file 'Knowledge/current/' folder

PROCESS:

Step 1: Discovery
- Find meetings in /home/workspace/Personal/Meetings with [P] suffix
- For each meeting, check if B14_BLURBS_REQUESTED.md or B25_DELIVERABLE_CONTENT_MAP.md exists
- Skip if FOLLOW_UP_EMAIL.md and BLURBS_GENERATED.md already exist (idempotent)

Step 2: Context Assembly (for each meeting needing communications)
- Load transcript.txt
- Load B08_STAKEHOLDER_INTELLIGENCE.md
- Load B25 if exists
- Load B14 if exists
- Load ALL files from Knowledge/current/ folder
- Load voice transformation system

Step 3: Generate Communications
- Use Claude Opus (or best available powerful model)
- Generate style-free drafts first
- Apply voice transformation using few-shot examples from system
- Follow guidance in communications-generator.prompt.md

For FOLLOW_UP_EMAIL.md (if B25 exists and triggers):
- Use transformation system PAIR 1, 2, 3, 5 as examples
- Generate send-ready email incorporating deliverables
- Validate against voice anti-patterns
- Length: 150-250 words

For BLURBS_GENERATED.md (if B14 exists):
- Generate each requested blurb
- Match requested length and tone
- Incorporate Knowledge/current/ positioning
- Validate accuracy (no placeholders)

Step 4: State Transition
- Save outputs to meeting folder
- Rename folder from [P] to [R]
- Log: "[Date] Processed [meeting_id]: [email_generated] [blurbs_count]"

Step 5: Summary
Report: "Processed X meetings. Generated Y emails and Z blurbs."

ERROR HANDLING:
- If Knowledge/current/ is empty: Warn but continue with available context
- If generation fails: Log error, keep folder in [P] state, retry next run
- If validation fails: Include in summary for manual review

QUALITY STANDARDS:
- Use V's authentic voice (transformation system)
- Incorporate current Careerspan positioning
- Match stakeholder resonance from B08
- Send-ready quality (minimal edits needed)
```

**Delivery Method:** None (or email, as V prefers)

---

## Verification Checklist

### After Phase 1:
- [ ] block_type_registry.json updated and validates
- [ ] B14 guidance is intelligence-only (100-200 words)
- [ ] B25 guidance is intelligence-only (100-200 words)
- [ ] Communications generator includes voice system
- [ ] [R] state added to all relevant places
- [ ] No syntax errors in updated files

### After Phase 2:
- [ ] Scheduled task created successfully
- [ ] Task instruction is comprehensive
- [ ] Schedule is appropriate (every 2 hours recommended)
- [ ] Task can access all required files

### After Phase 3:
- [ ] Manual test passed on 2 meetings
- [ ] Voice transformation applied correctly
- [ ] Knowledge/current/ context incorporated
- [ ] State transitions work ([P] → [R])
- [ ] Scheduled task test run successful

### After Phase 4:
- [ ] Documentation updated
- [ ] SESSION_STATE reflects completion
- [ ] No test artifacts remaining
- [ ] System ready for production

---

## Timeline Estimate

**Total Time:** 75-110 minutes

| Phase | Task | Est. Time |
|-------|------|-----------|
| 1.1 | Update block registry | 10-15 min |
| 1.2 | Update communications generator | 15-20 min |
| 1.3 | Add [R] state support | 5-10 min |
| 2.1 | Create scheduled task | 10-15 min |
| 2.2 | Write task instruction | 5 min |
| 3.1 | Manual test run | 15-20 min |
| 3.2 | Scheduled task test | 5-10 min |
| 4.1 | Update documentation | 5 min |
| 4.2 | Cleanup | 5 min |

**Recommended Approach:** Execute Phase 1 and 2 in one session, test in next session.

---

## Success Criteria

**System is successful when:**

1. **B14 and B25 blocks are simpler:** 100-200 words, intelligence-only
2. **Communications use V's voice:** Transformation system applied, authentic output
3. **Automation works:** Scheduled task runs every 2 hours, processes meetings correctly
4. **Quality is high:** V can send emails/blurbs with 0-2 edits
5. **State machine works:** [P] → [R] transitions correctly
6. **No manual intervention:** System runs autonomously except for Knowledge/current/ updates

---

## Next Steps

1. **V: Populate Knowledge/current/** with initial documents
   - Current positioning doc
   - Value props
   - Recent wins/traction
   - Example emails (optional)

2. **Execute Phase 1:** Update registries and add voice system

3. **Execute Phase 2:** Create scheduled task

4. **Test Phase 3:** Validate on 2-3 meetings

5. **Monitor:** Check first few scheduled runs

---

## Open Questions

1. **Scheduled task frequency:** Every 2 hours OK, or prefer different schedule?
2. **Delivery method:** Email summary of processed meetings, or silent operation?
3. **Knowledge/current/ initial population:** Need help creating first docs?
4. **Voice transformation testing:** Want to test voice quality on sample before full rollout?

---

**This is conversation con_MMUy9beXziOyCQC5**

*Generated: 2025-11-16 14:18 EST*

