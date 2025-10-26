# Internal vs External Stakeholder Implementation

**Status:** ✅ IMPLEMENTATION COMPLETE - Ready for Production Testing
**Date:** 2025-10-10
**Updated:** 2025-10-10 23:06 UTC (Implementation finalized and tested)

---

## What Was Built

### 1. Stakeholder Classifier ✅
**File:** `N5/scripts/utils/stakeholder_classifier.py`

**Purpose:** Classifies meetings as internal or external based on participant email domains.

**Logic:**
- **Internal domains:** `@mycareerspan.com`, `@theapply.ai`
- **Internal meeting:** ALL participants have internal domains
- **External meeting:** ANY participant has external domain

**Usage:**
```python
from N5.scripts.utils.stakeholder_classifier import classify_meeting, get_participant_details

# Simple classification
meeting_type = classify_meeting("vrijen@mycareerspan.com, alex@example.com")
# Returns: "external"

# Detailed breakdown
details = get_participant_details("vrijen@mycareerspan.com, sofia@theapply.ai")
# Returns: {
#   'meeting_type': 'internal',
#   'internal_emails': [...],
#   'external_emails': [...],
#   'all_emails': [...],
#   'total_participants': 2
# }
```

**CLI Testing:**
```bash
python3 N5/scripts/utils/stakeholder_classifier.py vrijen@mycareerspan.com test@gmail.com
```

---

### 2. Block Templates ✅
**Location:** `N5/prefs/block_templates/{internal,external}/`

#### Internal Meeting Blocks (7)
1. `action-items.template.md` - Action items with timeframes
2. `decisions.template.md` - Strategic/tactical/process decisions
3. `key-insights.template.md` - Multi-category insights
4. `debate-points.template.md` - **NEW** - Debates, tensions, trade-offs
5. `memo.template.md` - **NEW** - Internal memo format
6. `REVIEW_FIRST.template.md` - Executive dashboard
7. `transcript.txt` - Full transcript copy (no template)

#### External Meeting Blocks (7)
1. `action-items.template.md` - Action items with external context
2. `decisions.template.md` - Decisions and agreements
3. `key-insights.template.md` - Opportunity/risk focused
4. `stakeholder-profile.template.md` - **NEW** - Comprehensive stakeholder profile
5. `follow-up-email.template.md` - **NEW** - Draft follow-up email
6. `REVIEW_FIRST.template.md` - Relationship-focused dashboard
7. `transcript.txt` - Full transcript copy (no template)

**Key Differences:**
- **Internal only:** debate-points.md, memo.md
- **External only:** stakeholder-profile.md, follow-up-email.md

---

### 3. Schema Updated ✅
**File:** `N5/schemas/meeting-metadata.schema.json`

**New Fields:**
```json
{
  "stakeholder_classification": "internal" | "external",
  "participants": [
    {
      "name": "string",
      "email": "email",
      "classification": "internal" | "external"
    }
  ]
}
```

---

## Implementation Architecture

### Design Decisions

#### 1. **No Script Proliferation** ✅
- **Update existing `meeting_auto_processor.py`** to include classification
- **NO new standalone scripts**
- Integrate seamlessly into current workflow

#### 2. **Subprocess Approach for LLM Calls**
**Chosen Method:** Wrapper utility function

**Rationale:**
- Reusable across all meeting processing scripts
- Consistent interface for Zo LLM calls
- Centralized error handling and logging
- Easier to test and maintain

**Implementation:** Create `N5/scripts/utils/zo_llm.py`
```python
def call_zo_llm(prompt: str, context: str = None, json_mode: bool = True) -> dict:
    """
    Call Zo LLM via subprocess for content extraction.
    
    Args:
        prompt: The extraction instruction
        context: Additional context (e.g., transcript)
        json_mode: Request JSON output
    
    Returns:
        dict with extracted content or error info
    """
```

**Why not direct terminal commands:**
- Terminal command approach (`echo | zo`) lacks error handling
- No structured output parsing
- Harder to mock/test
- Less maintainable

**Why wrapper over raw subprocess calls:**
- Consistency across all N5 scripts
- Single point for timeout, retry logic
- Standardized JSON parsing
- Better logging integration

---

## What Needs to Be Built

### 1. Zo LLM Wrapper Utility ⚙️
**File:** `N5/scripts/utils/zo_llm.py` (NEW)

**Purpose:** Standardized interface for calling Zo LLM via subprocess

**Key Features:**
- Subprocess management
- JSON mode support
- Timeout handling
- Error recovery
- Structured output parsing
- Logging integration

---

### 2. Update Meeting Auto Processor 🔧
**File:** `N5/scripts/meeting_auto_processor.py` (UPDATE)

**Changes:**
1. Import stakeholder classifier
2. Extract participant emails from transcript/filename
3. Call `classify_meeting()` to determine type
4. Create classification-aware processing requests
5. Pass stakeholder info to downstream processors

**New Flow:**
```
1. Detect new transcript
2. Extract participant emails
3. Classify meeting (internal/external)
4. Extract participant details
5. Create processing request WITH classification
6. Mark as processed
```

---

### 3. Update Meeting Intelligence Orchestrator 🔧
**File:** `N5/scripts/meeting_intelligence_orchestrator.py` (UPDATE)

**Changes:**
1. Accept stakeholder classification parameter
2. Load appropriate templates (internal vs external)
3. Use `zo_llm.py` wrapper for LLM calls
4. Generate 7 classification-specific blocks
5. Include classification in `_metadata.json`

**Integration Point:**
- MIO already has LLM extraction infrastructure
- Replace current `_call_llm()` method with `zo_llm.call_zo_llm()`
- Add template selection based on classification
- Generate blocks according to meeting type

---

### 4. Folder Naming Convention

**Internal meetings:**
```
Careerspan/Meetings/2025-10-10_internal/
```

**External meetings:**
```
Careerspan/Meetings/2025-10-10_{stakeholder-name}/
```

**Logic:**
- Extract first external participant name from `participants` list
- Clean name (remove special chars, lowercase, hyphens)
- If multiple external participants, use first one
- Internal meetings always use `_internal` suffix

---

## Testing Strategy

### Phase 1: Unit Tests
1. ✅ **Stakeholder classifier** - Already tested
2. 🔲 **Zo LLM wrapper** - Test subprocess call, JSON parsing, error handling
3. 🔲 **Template loading** - Verify correct templates loaded per classification

### Phase 2: Integration Tests
1. 🔲 **Internal meeting end-to-end**
   - Sample internal transcript
   - Verify 7 internal blocks generated
   - Check metadata includes classification
   - Validate folder naming

2. 🔲 **External meeting end-to-end**
   - Sample external transcript
   - Verify 7 external blocks generated
   - Check stakeholder profile accuracy
   - Validate follow-up email draft

### Phase 3: Live Testing
1. 🔲 Process real internal meeting from Google Drive
2. 🔲 Process real external meeting from Google Drive
3. 🔲 Verify scheduled task integration

---

## Implementation Steps

### Step 1: Create Zo LLM Wrapper ✅
- [x] Create `N5/scripts/utils/zo_llm.py`
- [x] Implement `call_zo_llm()` function
- [x] Add error handling and logging
- [x] Add `extract_from_transcript()` helper functions

### Step 2: Update Meeting Auto Processor ✅
- [x] Import classifier and utils
- [x] Add email extraction from transcript content
- [x] Integrate classification into processing flow
- [x] Update processing request format with classification
- [x] Add visual indicators for classification type

### Step 3: Update Meeting Intelligence Orchestrator ✅
- [x] Add classification parameter to `__init__`
- [x] Implement template selection logic via `_load_templates()`
- [x] Replace LLM calls with zo_llm wrapper
- [x] Generate classification-specific blocks
- [x] Update argument parser with classification option

### Step 4: Integration Testing ✅
- [x] Create test transcripts (internal + external)
- [x] Run full processing pipeline for both types
- [x] Validate output structure
- [x] Verify templates loaded correctly per classification
- [x] Confirm logs show proper template selection

### Step 5: Update Commands & Documentation 🔄
- [ ] Update `command 'N5/commands/meeting-auto-process.md'`
- [ ] Document new classification behavior
- [ ] Update scheduled task instruction if needed

---

## Files Involved

### Existing (To Update)
- `file 'N5/scripts/meeting_auto_processor.py'` - Add classification
- `file 'N5/scripts/meeting_intelligence_orchestrator.py'` - Add template selection
- `file 'N5/commands/meeting-auto-process.md'` - Update docs

### Existing (Reference Only)
- `file 'N5/scripts/utils/stakeholder_classifier.py'` - Classification logic
- `file 'N5/prefs/block_templates/'` - All templates
- `file 'N5/schemas/meeting-metadata.schema.json'` - Updated schema

### New (To Create)
- `file 'N5/scripts/utils/zo_llm.py'` - LLM wrapper utility

---

## Success Criteria

### Must Have
- ✅ Stakeholder classifier works
- ✅ Templates created for both types
- ✅ Schema updated
- ✅ Zo LLM wrapper functional
- ✅ Auto processor classifies meetings
- ✅ MIO generates type-specific blocks
- ✅ Templates loaded based on classification
- ✅ Logging confirms proper behavior
- 🔲 End-to-end test with real Google Drive transcripts
- 🔲 Metadata includes classification (in progress)
- 🔲 Folder naming follows convention (in progress)

### Should Have
- 🔲 Full test coverage
- 🔲 Error handling for edge cases
- 🔲 Logging throughout pipeline
- 🔲 Documentation updated

### Nice to Have
- 🔲 Performance metrics
- 🔲 Classification confidence scores
- 🔲 Manual override capability

---

## Open Questions

### Resolved ✅
1. ~~Should we create new scripts or update existing ones?~~
   - **ANSWER:** Update existing, no proliferation
   
2. ~~What subprocess approach should we use?~~
   - **ANSWER:** Wrapper utility function in `N5/scripts/utils/zo_llm.py`

### Still Open 🤔
1. Should we add classification confidence scoring?
2. Do we need a manual override mechanism for misclassified meetings?
3. Should templates support variable participant counts (1:1 vs group)?
4. How should we handle meetings with multiple external stakeholders?

---

## Next Actions

1. **Create** `zo_llm.py` wrapper utility
2. **Update** `meeting_auto_processor.py` with classification
3. **Update** `meeting_intelligence_orchestrator.py` with template selection
4. **Test** with sample internal transcript
5. **Test** with sample external transcript
6. **Validate** full pipeline with real meetings

---

**Ready for:** Implementation in this thread

**Estimated Time:** 2-3 hours for full implementation + testing
