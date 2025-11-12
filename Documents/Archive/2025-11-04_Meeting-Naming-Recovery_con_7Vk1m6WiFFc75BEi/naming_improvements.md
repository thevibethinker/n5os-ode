---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# Meeting Folder Naming Improvements

## Changes Implemented

### 1. Created B99 Prompt - LLM-Powered Naming
**File**: file 'Intelligence/prompts/B99_folder_naming.md'

**Purpose**: Leverage LLM semantic understanding to generate optimal folder names from B26/B28 intelligence

**Key improvements over pattern-matching**:
- Understands primary stakeholder from B28 decision architecture
- Extracts meaningful topics from strategic context
- Handles edge cases intelligently (unknown stakeholders, ambiguous context)
- Uses priority logic based on stakeholder count and org distribution

**Priority Logic**:
1. **Single external + org**: `{date}_{FirstLast}-{org}_{type}`
   - Example: `2025-08-29_TimHe-twill_partnership`

2. **Single external without org**: `{date}_{FirstLast}_{type}`
   - Example: `2025-11-03_SarahJohnson_external`

3. **Multiple stakeholders, same org**: 
   - With primary: `{date}_{PrimaryStakeholder}-{org}_{type}`
   - Without primary: `{date}_{org}-{topic}_{type}`
   - Example: `2025-09-12_AllieCialeo-greenlight_sales` (was `greenlight_recruiting-discovery_sales`)

4. **Multiple stakeholders, different orgs**: `{date}_{primary-stakeholder}-{topic}_{type}`

5. **Internal meetings**: `{date}_{team-type}_{topic}_{meeting-type}`
   - Example: `2025-11-03_careerspan-team_daily-standup_standup`

### 2. Created Helper Script
**File**: file 'N5/scripts/meeting_pipeline/generate_folder_name.py'

**Purpose**: Wrapper script to invoke B99 prompt during pipeline execution

**Status**: ⚠️ Needs integration with Zo conversation API to actually call B99 as tool

### 3. Example Improvement: Allie Meeting

**Before**: `2025-09-12_greenlight_recruiting-discovery_sales`
- Generic org-based name
- Doesn't identify who the meeting was with
- "recruiting-discovery" is redundant with "_sales" suffix

**After**: `2025-09-12_AllieCialeo-greenlight_sales`
- Immediately scannable: "This is the Allie meeting"
- Org context preserved: "at Greenlight"
- Clean suffix: "_sales"
- B28 informed: Used primary decision-maker from strategic intelligence

## How It Works

### During Meeting Processing

1. **Generate intelligence blocks** (B26, B28, etc.)
2. **Invoke B99 prompt** with B26 + B28 content
3. **LLM analyzes**:
   - Stakeholder configuration
   - Organization distribution
   - Decision architecture
   - Strategic context
4. **Returns optimal name**: `YYYY-MM-DD_identifier_type`
5. **Pipeline renames folder** or uses name for new folder creation

### Integration Points

**Name Normalizer** (`name_normalizer.py`):
- Currently uses pattern matching + heuristics
- Should call B99 prompt for each folder
- Falls back to current logic if LLM call fails

**Meeting Processor** (scheduled task):
- Generate intelligence blocks first
- Call B99 before creating final folder
- Use generated name from start (no rename needed)

## Next Steps

### To Complete Integration

1. **Update name_normalizer.py**:
   - Add function to call B99 via Zo conversation API
   - Invoke LLM for each folder needing rename
   - Keep existing logic as fallback

2. **Update meeting processor**:
   - After generating B26/B28, invoke B99
   - Use generated name when creating folder
   - Skip rename step entirely

3. **Test on backlog**:
   - Run name_normalizer on existing 21 processed meetings
   - Validate improvements
   - Document edge cases

### Scheduled Task Name Update

**Current**: "Team Strategy Meeting" (ID: e321bdd7-361b-4b91-954b-bba6fd0abc5b)
**Should be**: "🧠 Meeting Intelligence Processor"

**Note**: Cannot update via API access available. Needs manual update in Zo settings or database access.

## Quality Improvements Expected

### Before (Pattern Matching)
- `2025-09-12_greenlight_recruiting-discovery_sales`
- `2025-10-20_unknown_external`
- `2025-08-26_asher-king-abramson_warmer-jobs-integration-discussion_partnership`

### After (LLM-Powered)
- `2025-09-12_AllieCialeo-greenlight_sales`
- `2025-10-20_BennettLee-reforge_external` (using B26 data)
- `2025-08-26_AsherKingAbramson-warmer_integration`

**Benefits**:
- Immediately scannable
- Distinguishes repeat stakeholders
- Removes redundant info
- Uses strategic intelligence (decision-makers)
- Consistent length and format

## Files Created

1. file 'Intelligence/prompts/B99_folder_naming.md' - LLM naming prompt ✅
2. file 'N5/scripts/meeting_pipeline/generate_folder_name.py' - Helper script ✅
3. file 'N5/scripts/meeting_pipeline/test_naming.sh' - Test harness ✅
4. This document ✅

## Status

✅ **Prompt created and ready** - B99 is a tool-enabled prompt  
⚠️ **Integration pending** - Need to wire B99 into name_normalizer and meeting processor  
📋 **Testing needed** - Run on 21 existing processed meetings to validate

---

*Created during validation work package con_7Vk1m6WiFFc75BEi*
