---
created: 2025-11-04
work_package_id: meeting-quality-naming-fallbacks
status: ready
assigned_persona: Builder
parent_conversation: con_NlBXK8aOD29kiCDi
estimated_effort: 30min
---
# Work Package: Implement Meeting Folder Naming Fallbacks

## Context

Architect has reviewed meeting quality system and identified **BLOCKING ISSUE**: name_normalizer.py lacks flexible fallback logic for different stakeholder scenarios.

**Parent Architectural Plan:** file `/home/.z/workspaces/con_NlBXK8aOD29kiCDi/meeting_system_analysis.md`

**Current State:**
- Components built: validator, quality_controller, name_normalizer (basic)
- Bugs fixed: argparse, datetime deprecation
- **Gap:** Name normalizer only handles ideal case + unknown fallback

## Objective

Implement comprehensive naming fallback logic in `N5/scripts/meeting_pipeline/name_normalizer.py` to handle ALL stakeholder scenarios.

## Requirements Specification

### Naming Priority Hierarchy (MUST IMPLEMENT ALL 6)

**PRIORITY 1 (Ideal):**
- Format: `{date}_FirstLast-OrgName_{type}`
- Example: `2025-11-03_MihirMakwana-Northwell_external`
- Condition: Single external stakeholder with known org

**PRIORITY 2 (No Org):**
- Format: `{date}_FirstLast_{type}`
- Example: `2025-11-03_MihirMakwana_external`
- Condition: Single external stakeholder, org unknown/needs research

**PRIORITY 3 (Multiple Same Org):**
- Format: `{date}_OrgName-meeting_{type}`
- Example: `2025-11-03_Northwell-meeting_external`
- Condition: Multiple stakeholders from same organization

**PRIORITY 4 (Multiple Different Orgs):**
- Format: `{date}_multiple-stakeholders_{type}`
- Example: `2025-11-03_multiple-stakeholders_external`
- Condition: Multiple stakeholders from different orgs

**PRIORITY 5 (Unknown):**
- Format: `{date}_unknown_{type}`
- Example: `2025-11-03_unknown_external`
- Condition: Cannot infer stakeholder from context

**PRIORITY 6 (Internal):**
- Format: `{date}_team-{topic}_{type}`
- Example: `2025-11-03_team-standup_internal`
- Condition: Internal meeting, extract topic if possible

### Implementation Logic Flowchart

```
1. Parse B26 for stakeholders list with orgs
2. Filter out internal stakeholders (Vrijen, team members)
3. Count remaining external stakeholders
4. IF 0 external → PRIORITY 6 (internal format)
5. IF 1 external:
   a. Check if org present AND not "[Unknown]" or "[needs research]"
   b. Has valid org? → PRIORITY 1 (FirstLast-OrgName)
   c. No valid org? → PRIORITY 2 (FirstLast only)
6. IF multiple external:
   a. Group by organization
   b. All same org? → PRIORITY 3 (OrgName only)
   c. Different orgs? → PRIORITY 4 (multiple-stakeholders)
7. IF cannot parse/determine → PRIORITY 5 (unknown)
```

### Edge Cases (MUST HANDLE)

1. Org marked as "[Unknown]", "[needs research]", or similar → Treat as no org
2. "Vrijen" or "Vrijen Attawar" in participants → Filter out (internal)
3. Names with special characters (é, ñ, etc) → Slugify properly using existing function
4. Multiple people with same first name → Use FirstLast format
5. Org names with spaces → Slugify to hyphens
6. Meeting type with multiple words → Use first word only (e.g., "internal team coordination" → "internal")
7. Empty stakeholder list → Unknown fallback
8. B26 missing stakeholder section → Parse from Participants section fallback

## Function to Modify

**File:** `N5/scripts/meeting_pipeline/name_normalizer.py`

**Function:** `generate_folder_name_from_b26(meeting_dir: Path, metadata: Dict) -> str`

**Current Issues:**
- Only handles Priority 1 and Priority 5
- Missing org extraction logic
- Missing multi-stakeholder logic
- Missing internal meeting topic extraction

## Enhanced B26 Parsing Requirements

Update `extract_metadata_from_b26()` to also return structured stakeholder data:

```python
{
    'meeting_id': str,
    'date': str,
    'meeting_type': str,
    'participants': List[str],
    'stakeholders': [
        {
            'name': str,
            'organization': str | None,  # None if unknown
            'is_internal': bool
        },
        ...
    ]
}
```

Parse from B26 sections:
1. "Stakeholders" section (if exists) - preferred
2. "Participants" section (fallback)
3. Look for patterns like:
   - `**Name** - Organization`
   - `**Name** ([Organization])`
   - `**Name** - [Organization Unknown]`

## Test Cases (REQUIRED)

Create test function `test_naming_scenarios()` that validates:

```python
test_cases = [
    {
        'scenario': 'Single external + org',
        'stakeholders': [{'name': 'Mihir Makwana', 'organization': 'Northwell', 'is_internal': False}],
        'expected': '2025-11-03_MihirMakwana-Northwell_external'
    },
    {
        'scenario': 'Single external no org',
        'stakeholders': [{'name': 'Mihir Makwana', 'organization': None, 'is_internal': False}],
        'expected': '2025-11-03_MihirMakwana_external'
    },
    {
        'scenario': 'Multiple same org',
        'stakeholders': [
            {'name': 'John Smith', 'organization': 'Northwell', 'is_internal': False},
            {'name': 'Jane Doe', 'organization': 'Northwell', 'is_internal': False}
        ],
        'expected': '2025-11-03_Northwell-meeting_external'
    },
    {
        'scenario': 'Multiple different orgs',
        'stakeholders': [
            {'name': 'John Smith', 'organization': 'Northwell', 'is_internal': False},
            {'name': 'Jane Doe', 'organization': 'Mayo Clinic', 'is_internal': False}
        ],
        'expected': '2025-11-03_multiple-stakeholders_external'
    },
    {
        'scenario': 'Unknown stakeholder',
        'stakeholders': [],
        'expected': '2025-11-03_unknown_external'
    },
    {
        'scenario': 'Internal meeting',
        'stakeholders': [
            {'name': 'Vrijen', 'organization': 'Careerspan', 'is_internal': True},
            {'name': 'Tiffany', 'organization': 'Careerspan', 'is_internal': True}
        ],
        'expected': '2025-11-03_team-standup_internal'  # or extract topic from title
    }
]
```

## Success Criteria

1. ✅ All 6 priority naming patterns implemented
2. ✅ All 8 edge cases handled correctly
3. ✅ Test cases pass for all scenarios
4. ✅ Backward compatible with existing B26 files
5. ✅ No regression - existing meetings still parse correctly
6. ✅ Code documented with docstrings explaining logic

## Deliverables

1. **Modified File:** `N5/scripts/meeting_pipeline/name_normalizer.py`
   - Enhanced `extract_metadata_from_b26()` with stakeholder parsing
   - Complete `generate_folder_name_from_b26()` with all fallbacks
   - Add test function (can be at bottom or separate test file)

2. **Verification Output:**
   - Run test cases and show results
   - Test on 3 real meetings from `/home/workspace/Personal/Meetings/`
   - Show before/after naming for each

3. **Documentation:**
   - Update docstrings
   - Add inline comments for complex logic
   - Note any assumptions or limitations

## Reference Files

**Must Read:**
- file `N5/scripts/meeting_pipeline/name_normalizer.py` (current implementation)
- file `N5/prefs/meeting_block_standards.yaml` (B26 structure)
- file `/home/.z/workspaces/con_NlBXK8aOD29kiCDi/DEBUGGING_COMPLETE.md` (system context)

**For Examples:**
- file `Personal/Meetings/tko-ucny-okw-transcript-2025-11-03T21-30-01/B26_metadata.md`
- file `Personal/Meetings/bdr-rjwf-ehc-transcript-2025-11-03T08-34-24.986Z/B26_metadata.md`

## Constraints

- **Time Budget:** 70% think/plan, 10% execute, 20% review
- **No Placeholders:** Real implementations only
- **Backward Compatibility:** Must work with existing B26 files
- **Performance:** Parsing should be <100ms per meeting
- **Error Handling:** Graceful fallbacks if B26 malformed

## After Completion

Report back to parent conversation `con_NlBXK8aOD29kiCDi` with:
1. Implementation complete confirmation
2. Test results summary
3. Any issues encountered
4. Recommended next steps

---

**Status:** READY FOR ASSIGNMENT
**Priority:** BLOCKING (system cannot go to production without this)
**Estimated Time:** 30 minutes
