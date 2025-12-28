# Plan: Meeting Intelligence Generation (Vrijen x Miami VC)

## Checklist
- [ ] Parse transcript and extract key entities/metadata
- [ ] Generate B01: Detailed Recap
- [ ] Generate B03: Stakeholder Intelligence
- [ ] Generate B03: Decisions (Note: File name B03_DECISIONS.md as requested, though usually B04)
- [ ] Generate B05: Action Items
- [ ] Generate B06: Business Context
- [ ] Generate B07: Tone & Context
- [ ] Generate B14: Blurbs Requested
- [ ] Generate B21: Key Moments
- [ ] Generate B25: Deliverables
- [ ] Generate B26: Meeting Metadata
- [ ] Generate B32: Thought Provoking Ideas
- [ ] Final Assembly into JSON format as requested

## Affected Files
- `N5/builds/meeting-intel-gen-vrijen-miami/B01_DETAILED_RECAP.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B03_STAKEHOLDER_INTELLIGENCE.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B03_DECISIONS.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B05_ACTION_ITEMS.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B06_BUSINESS_CONTEXT.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B07_TONE_AND_CONTEXT.md`
- \   N5/builds/meeting-intel-gen-vrijen-miami/B14_BLURBS_REQUESTED.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B21_KEY_MOMENTS.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B25_DELIVERABLES.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B26_MEETING_METADATA.md`
- `N5/builds/meeting-intel-gen-vrijen-miami/B32_THOUGHT_PROVOKING_IDEAS.md`

## Unit Tests
- Verify all requested files are present in the temporary build directory.
- Verify YAML frontmatter presence and correctness (created, last_edited, version, provenance).
- Verify JSON structure matches the user's requirement.

