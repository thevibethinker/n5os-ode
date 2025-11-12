---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# B99 LLM Naming - Full Integration Complete ✅

**Status**: Wired up, tested, ready for production

## How It Works

### Meeting Intelligence Processor (Every 10 minutes)
**Task ID**: `e321bdd7-361b-4b91-954b-bba6fd0abc5b`

**Workflow**:
1. Dequeues ONE meeting from queue
2. Reads transcript
3. **Invokes prompts AS TOOLS**: Loads file 'Intelligence/prompts/B01_generation_prompt.md', follows instructions, generates B01 block
4. Repeats for B02, B26, B28 (and conditional blocks)
5. **Invokes B99 naming prompt AS TOOL**: Loads file 'Intelligence/prompts/B99_folder_naming.md', passes B26+B28 content, generates optimal folder name
6. Creates folder with LLM-generated name
7. Moves all files into folder
8. Creates `.processed` marker

**Key Point**: The AI (Zo) executes the task by **loading prompts as tools** and following their instructions. This is pure LLM reasoning - no Python pattern matching.

### B99 Naming Logic (Simplified per V's feedback)

**Priority 1**: Single external stakeholder
- Format: `{date}_{First-Last}_{type}`
- Example: `2025-10-20_Bennett-Lee_advisory`

**Priority 2**: Multiple external stakeholders from same org
- Format: `{date}_{org}_{type}`
- Example: `2025-09-12_greenlight_sales`

**Priority 3**: Multiple stakeholders, different orgs
- Format: `{date}_{topic}_{type}`
- Example: `2025-08-15_career-services-workshop_partnership`

**Priority 4**: Ambiguous
- Format: `{date}_unknown_{type}`
- Example: `2025-10-22_unknown_external`

### Batch Rename (One-time + Weekly)

**One-Time Task** (482ad067 - Tonight at 8pm):
- DRY RUN FIRST - shows rename plan
- Waits for V's approval
- Then renames all 21 existing folders

**Weekly Task** (f25ccda0 - Sundays at 3am):
- Renames any folders that were processed before B99 was integrated
- Handles edge cases
- Runs in perpetuity

## Files Created/Modified

✅ file 'Intelligence/prompts/B99_folder_naming.md' - LLM naming prompt (tool-enabled)
✅ file 'N5/scripts/meeting_pipeline/llm_naming.py' - Python wrapper (fallback only)
✅ file 'N5/scripts/meeting_pipeline/name_normalizer.py' - Updated with LLM integration
✅ file 'N5/scripts/meeting_pipeline/batch_rename_meetings.py' - Batch rename script

## Scheduled Tasks

✅ **Meeting Intelligence Processor** - Every 10 minutes, invokes B99 for new meetings
✅ **Batch Rename (One-time)** - Tonight 8pm, dry-run first
✅ **Batch Rename (Weekly)** - Sundays 3am, cleanup stragglers

## Testing

✅ **Manual test**: Generated names for Tim He (2025-08-29_Tim-He_partnership) and Allie meeting (2025-09-12_greenlight_sales)
✅ **Validation**: Confirmed scheduled task instruction properly invokes prompts as tools
✅ **Safety**: Atomic fallbacks, dry-run mode, full logging

## Production Ready

- ✅ All new meetings get LLM-generated names automatically
- ✅ Existing meetings will be renamed after V approves dry-run
- ✅ Zero disruption - all fallbacks in place
- ✅ Clean, simple naming logic (per V's preference)

---

**Completed**: 2025-11-04 14:15 EST  
**Operator**: Vibe Operator
