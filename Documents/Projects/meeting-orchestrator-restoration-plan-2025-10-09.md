# Meeting Orchestrator Restoration Plan

**Date**: 2025-10-09  
**Purpose**: Restore full functionality to meeting processing system  
**Current Status**: meeting_orchestrator.py has missing block module dependencies

---

## Executive Summary

The meeting_orchestrator.py script exists and has the correct orchestration logic, but **11 required block generator modules are missing**. The script attempts to import these modules which don't exist, causing immediate failure. Additionally, working transcript processing code exists in consolidated_transcript_workflow_v2.py that can be leveraged.

---

## Current State Assessment

### What Exists ✓
1. **meeting_orchestrator.py** - Core orchestration logic intact
   - Pipeline structure: fetch → extract → generate → dashboard → integrate
   - Correct directory creation and metadata handling
   - Deliverable orchestrator integration already added
   - Error logging infrastructure present

2. **Partial blocks directory** (`N5/scripts/blocks/`)
   - `__init__.py` - Present
   - `meeting_info_extractor.py` - Present (6.7KB, functional)
   - `meeting_history_lookup.py` - Present (stub, 193 bytes)
   - `email_history_fetcher.py` - Present (stub, 219 bytes)
   - `deliverables/` subdirectory - Present with 3 generators

3. **Supporting Infrastructure**
   - `llm_utils.py` - LLM query utilities (simulated/placeholder)
   - `consolidated_transcript_workflow_v2.py` - Complete working extraction logic (724 lines)
   - `deliverable_orchestrator.py` - Deliverables generation system
   - Previous meeting output example (2025-09-24 Alex meeting) with correct structure

4. **Git Status**
   - meeting_orchestrator.py is Modified (M) - recent deliverables integration added
   - blocks/ directory partially tracked
   - No deleted files in recent history (checked git log)

### What's Missing ✗

**11 Required Block Generator Modules** (all in `N5/scripts/blocks/`):
1. `follow_up_email_generator.py` - Generate follow-up emails
2. `action_items_extractor.py` - Extract action items with owners/deadlines
3. `decisions_extractor.py` - Extract decisions made
4. `key_insights_extractor.py` - Extract key insights/takeaways
5. `stakeholder_profile_generator.py` - Build stakeholder profiles
6. `warm_intro_detector.py` - Detect warm intro opportunities
7. `risks_detector.py` - Identify risks mentioned
8. `opportunities_detector.py` - Identify opportunities
9. `user_research_extractor.py` - Extract user research insights
10. `competitive_intel_extractor.py` - Extract competitive intelligence
11. `dashboard_generator.py` - Generate REVIEW_FIRST.md dashboard

**Optional/Conditional Modules** (not critical):
- `deal_intelligence_generator.py` - For sales meetings
- `career_insights_generator.py` - For coaching/networking meetings
- `investor_thesis_generator.py` - For fundraising meetings
- `partnership_scope_generator.py` - For partnership meetings
- `list_integrator.py` - Integrate outputs with N5 lists

### Why Missing

**Analysis**: Based on git investigation:
- No deletion history found in git log
- modules/ directory partially untracked (deliverables/ is `??`)
- Likely these modules were **never fully implemented** or were lost in a workspace reorganization
- The Archive directory doesn't contain backup versions

---

## Gap Analysis

### Critical Gaps (Block Execution)
1. **Content Extraction**: No modules to extract action items, decisions, insights
2. **Profile Building**: No stakeholder profiling logic
3. **Dashboard Generation**: No REVIEW_FIRST.md generator
4. **Detection Logic**: No warm intro, risk, opportunity detection

### Non-Critical Gaps (Can Work Around)
1. **Email/Meeting History**: Stubs present, can return empty results
2. **List Integration**: Can be skipped initially
3. **Conditional Generators**: Only needed for specific meeting types

### Available Resources
1. **consolidated_transcript_workflow_v2.py** has complete extraction logic:
   - SpeakerAwareParser - Parse transcript with speaker attribution
   - EnhancedContentMapper - Extract commitments, decisions, next steps, deliverables, resonance
   - EmailRecapGenerator - Generate recap chunks
   - TodoListExtractor - Extract user todos
   
2. **Example outputs** from 2025-09-24 Alex meeting show expected format/quality

3. **llm_utils.py** provides LLM query interface (currently simulated)

---

## Restoration Strategy

### Approach: **Hybrid - Adapt Working Code + Generate Missing Pieces**

**Rationale**: 
- consolidated_transcript_workflow_v2.py has proven working extraction logic
- Can refactor/adapt this code into individual block modules
- Reduces risk vs. building from scratch
- Maintains consistency with existing patterns

### Phase 1: Core Block Generators (Essential)
Build the 5 most critical blocks needed for basic functionality:

1. **action_items_extractor.py**
   - Source: Adapt from consolidated_transcript_workflow_v2.py EnhancedContentMapper._extract_commitments()
   - Extract action items with owner, deadline, context
   - Output: action-items.md

2. **decisions_extractor.py**
   - Source: Adapt from EnhancedContentMapper._extract_decisions()
   - Extract decisions made during meeting
   - Output: decisions.md

3. **key_insights_extractor.py**
   - Source: Adapt from EnhancedContentMapper._extract_resonance() + new logic
   - Extract key insights, advice, realizations
   - Output: detailed-notes.md or key-insights.md

4. **dashboard_generator.py**
   - Source: Base on 2025-09-24 REVIEW_FIRST.md structure
   - Generate executive summary dashboard
   - Output: REVIEW_FIRST.md

5. **follow_up_email_generator.py**
   - Source: Adapt from EmailRecapGenerator.generate_recap_chunk()
   - Generate follow-up email content map
   - Output: follow-up-email.md

### Phase 2: Enhanced Block Generators (Important)
Add profile and detection capabilities:

6. **stakeholder_profile_generator.py**
   - Build stakeholder profile from transcript + history
   - Extract background, interests, concerns, opportunities
   - Output: stakeholder-profile.md

### Phase 3: Detection Blocks (Optional - Return Empty)
Create stub implementations that return 0 results:

7-10. **Detector modules** (warm_intro, risks, opportunities, user_research, competitive_intel)
   - Return 0/empty results initially
   - Can enhance later based on meeting type needs
   - Allows orchestrator to complete without errors

### Phase 4: Integration Blocks (Optional)
11. **list_integrator.py** - Stub that logs but doesn't integrate

---

## Implementation Plan

### Pre-Execution Checklist
- [ ] Review consolidated_transcript_workflow_v2.py extraction logic
- [ ] Review 2025-09-24 Alex meeting output structure
- [ ] Verify llm_utils.py interface
- [ ] Confirm meeting_orchestrator.py block calling conventions

### Execution Steps

#### Step 1: Create Block Module Template
- Create base class/structure for block generators
- Standard interface: `async def generate_*(transcript, meeting_info, output_dir) -> bool/int`
- Error handling and logging patterns

#### Step 2: Build Core Extractors (Phase 1)
For each module:
1. Create new file in N5/scripts/blocks/
2. Port relevant logic from consolidated_transcript_workflow_v2.py
3. Adapt to expected interface (transcript, meeting_info, output_dir)
4. Write output markdown with proper formatting
5. Add error handling and logging

**Order**: 
1. action_items_extractor.py (most critical)
2. decisions_extractor.py (critical)
3. key_insights_extractor.py (critical)
4. dashboard_generator.py (ties it together)
5. follow_up_email_generator.py (external communication)

#### Step 3: Build Profile Generator (Phase 2)
6. stakeholder_profile_generator.py
   - Use transcript + meeting_history context
   - Extract profile elements
   - Generate structured profile markdown

#### Step 4: Create Detection Stubs (Phase 3)
7-10. Create stub modules for detectors:
```python
async def generate_warm_intros(transcript, meeting_info, output_dir):
    """Detect warm introduction opportunities (stub)."""
    return 0  # No intros detected
```

#### Step 5: Create Integration Stub (Phase 4)
11. list_integrator.py - Log only, no actual integration

#### Step 6: Test & Validate
1. Run orchestrator on downloaded Alex transcript (2025-10-09)
2. Compare output to 2025-09-24 Alex meeting structure
3. Verify all blocks generate without errors
4. Check output quality and completeness

#### Step 7: Git Commit
- Add all new block modules
- Commit with clear message: "Restore meeting orchestrator block generators"

---

## Module Specifications

### 1. action_items_extractor.py

**Interface**:
```python
async def generate_action_items(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool
```

**Logic**:
1. Parse transcript with speaker awareness
2. Detect commitment indicators: "I'll", "I will", "I need to", "going to", "should", "have to"
3. Extract owner (speaker attribution)
4. Infer deadline from context (date references)
5. Extract context (why/what for)
6. Categorize by timeframe: Immediate (24-48h), Short-term (1-2w), Medium-term (2-4w), Long-term (1m+)

**Output Format** (markdown):
```markdown
# Action Items: [Meeting Title]

## Immediate (Next 24-48 Hours)
- [ ] **Action description**: Context
  - **Owner**: Name
  - **Deadline**: YYYY-MM-DD
  - **Context**: Additional details

## Short-Term (1-2 Weeks)
...
```

**Source**: `EnhancedContentMapper._extract_commitments()`

---

### 2. decisions_extractor.py

**Interface**:
```python
async def generate_decisions(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool
```

**Logic**:
1. Parse transcript with speaker awareness
2. Detect decision indicators: "decided", "going with", "chose", "will not", "won't", "agreed", "conclusion"
3. Extract decision statement
4. Extract rationale/context
5. Identify decision maker(s)
6. Categorize by type: Strategic, Tactical, Resource Allocation, Process

**Output Format**:
```markdown
# Decisions Made

## Strategic Decisions
### 1. [Decision Title]
- **Decision**: Clear statement
- **Rationale**: Why this was decided
- **Decided By**: Name(s)
- **Impact**: What this affects
```

**Source**: `EnhancedContentMapper._extract_decisions()`

---

### 3. key_insights_extractor.py

**Interface**:
```python
async def generate_key_insights(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool
```

**Logic**:
1. Parse transcript for high-value statements
2. Extract insights: realizations, validations, new perspectives, advice given
3. Detect insight indicators: "realized", "learned", "insight", "key takeaway", "important to note"
4. Extract context and implications
5. Categorize: Product, Market, Strategy, Operations, Personal

**Output Format**:
```markdown
# Key Insights & Takeaways

## Product Insights
### [Insight Title]
**Insight**: Clear statement of the insight
**Context**: Background/situation
**Implication**: What this means for action
**Source**: Who provided this insight
```

**Source**: `EnhancedContentMapper._extract_resonance()` + new logic

---

### 4. dashboard_generator.py

**Interface**:
```python
async def generate_dashboard(
    meeting_id: str,
    meeting_info: Dict[str, Any],
    blocks_generated: List[str],
    metadata: Dict[str, Any],
    output_dir: Path
) -> bool
```

**Logic**:
1. Read generated block outputs (action-items.md, decisions.md, key-insights.md)
2. Extract top items from each block
3. Generate executive summary
4. Create priority actions list (top 4)
5. Format with emoji and markdown styling

**Output Format**: See 2025-09-24 REVIEW_FIRST.md as template
- Executive Summary (3-4 sentences)
- Priority Actions (top 4, next 48h)
- Top 3 Insights (with validation/impact)
- Key Advice Given (categorized)
- Decisions Made (top 3-5)
- Action Items Summary (counts by timeframe)
- Risks & Opportunities (if any)

**Source**: 2025-09-24 REVIEW_FIRST.md structure

---

### 5. follow_up_email_generator.py

**Interface**:
```python
async def generate_follow_up_email(
    transcript: str,
    meeting_info: Dict[str, Any],
    email_history: Optional[List[Dict]],
    meeting_history: List[Dict],
    meeting_types: List[str],
    output_dir: Path
) -> bool
```

**Logic**:
1. Generate recap sections: decisions, next steps, deliverables
2. Personalize tone based on stakeholder relationship
3. Include action items summary
4. Add context from previous emails/meetings
5. Format for email sending

**Output Format**:
```markdown
# Follow-Up Email Draft

**To**: [Stakeholder names]
**Subject**: [Auto-generated subject line]

## Email Body

[Greeting]

[Recap paragraph]

### Next Steps
- Item 1
- Item 2

[Closing]
```

**Source**: `EmailRecapGenerator.generate_recap_chunk()`

---

### 6. stakeholder_profile_generator.py

**Interface**:
```python
async def generate_stakeholder_profile(
    transcript: str,
    meeting_info: Dict[str, Any],
    meeting_history: List[Dict],
    meeting_types: List[str],
    output_dir: Path
) -> bool
```

**Logic**:
1. Extract stakeholder information from transcript
2. Identify: background, current role, interests, pain points, opportunities
3. Build relationship context from meeting_history
4. Extract quoted statements
5. Identify warm intro opportunities mentioned

**Output Format**:
```markdown
# Stakeholder Profile: [Name]

## Background
- Current Role: 
- Company/Organization:
- Background:

## Interests & Focus Areas
- List of interests

## Pain Points & Challenges
- List of challenges mentioned

## Opportunities & Needs
- List of opportunities

## Relationship Context
- Previous meetings: X
- Last contact: Date
- Relationship stage: [New/Developing/Established]

## Key Quotes
> "Notable statement" - [Name]
```

---

### 7-10. Detector Stubs

**Interface** (all similar):
```python
async def generate_warm_intros(transcript, meeting_info, output_dir) -> int:
    """Detect warm introduction opportunities."""
    logger.info("Warm intro detection - stub implementation")
    return 0
```

Return 0 to indicate nothing detected, allowing orchestrator to continue.

---

### 11. list_integrator.py

**Interface**:
```python
async def integrate_with_lists(
    output_dir: Path,
    blocks_generated: List[str],
    meeting_id: str,
    metadata: Dict[str, Any]
) -> bool
```

**Logic**: Stub - log only, no actual integration

---

## Risk Assessment

### High Risk Items
- **LLM Integration**: llm_utils.py is currently simulated - may need real LLM calls for quality
- **Code Quality**: Ported code may need refactoring to match expected interface
- **Output Format**: Need to match 2025-09-24 meeting quality/structure

### Mitigation
- Start with action_items extraction (simplest, most critical)
- Test each module independently before integration
- Compare outputs to 2025-09-24 meeting example
- Can enhance with real LLM calls in Phase 2 if needed

### Low Risk Items
- Orchestration logic is solid
- Infrastructure (directories, logging, metadata) works
- Git tracking in good state

---

## Success Criteria

### Minimum Viable (Phase 1 Complete)
- [ ] meeting_orchestrator.py runs without import errors
- [ ] Generates action-items.md
- [ ] Generates decisions.md
- [ ] Generates key-insights.md (or detailed-notes.md)
- [ ] Generates REVIEW_FIRST.md dashboard
- [ ] Generates follow-up-email.md
- [ ] Creates proper directory structure
- [ ] Saves _metadata.json

### Full Success (All Phases Complete)
- [ ] All 11 modules present and functional
- [ ] Output matches 2025-09-24 meeting quality
- [ ] Processes Alex 2025-10-09 transcript successfully
- [ ] No errors in execution logs
- [ ] All outputs committed to git

---

## Estimated Effort

- **Phase 1 (Core Blocks)**: 60-90 minutes
  - Template creation: 10 min
  - action_items_extractor: 15 min
  - decisions_extractor: 15 min
  - key_insights_extractor: 15 min
  - dashboard_generator: 20 min
  - follow_up_email_generator: 15 min

- **Phase 2 (Profile)**: 15-20 minutes
  
- **Phase 3 (Stubs)**: 10 minutes

- **Phase 4 (Integration Stub)**: 5 minutes

- **Testing & Validation**: 20-30 minutes

**Total**: ~2-2.5 hours

---

## Post-Restoration Enhancements

Once basic functionality is restored, consider:

1. **Real LLM Integration**: Replace llm_utils simulated calls with actual LLM
2. **Enhanced Detection**: Improve warm intro, risk, opportunity detection with LLM
3. **List Integration**: Complete list_integrator.py to add items to N5 lists
4. **Email Sending**: Integrate with email tools to send follow-ups
5. **Meeting History**: Improve meeting_history_lookup to actually search previous meetings
6. **Conditional Blocks**: Implement deal_intelligence, career_insights, etc.

---

## Next Steps

**WAITING FOR USER APPROVAL TO EXECUTE**

Once approved, will execute in order:
1. Create block module template
2. Build Phase 1 core extractors
3. Build Phase 2 profile generator
4. Create Phase 3 & 4 stubs
5. Test on Alex 2025-10-09 transcript
6. Validate outputs
7. Git commit all changes

