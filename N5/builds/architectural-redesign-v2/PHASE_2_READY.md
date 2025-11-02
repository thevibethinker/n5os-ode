# PHASE 2: Principle Migration (3 hrs) - READY TO LAUNCH

## DEPENDENCIES ✅
- Phase 1A: COMPLETE (8 personas with stubs)
- Phase 1B: COMPLETE (6 core artifacts)
- Phase 1C: COMPLETE (8 personas with full protocol)

## MISSION
Convert 29 existing principles from markdown to YAML with versioning.

## SOURCE
file 'N5/lists/principles.md' (33 total, P36+P37 already done in 1B = 31 remaining)

## TARGET
Convert P1-P35 (excluding P36/P37 which exist) to:
N5/prefs/principles/P##_slug.yaml

## YAML SCHEMA


## EXECUTION STEPS

1. Load file 'N5/lists/principles.md'
2. For each P1-P35 (skip P36/P37):
   - Extract content from markdown
   - Convert to YAML schema
   - Determine category (behavior/communication/code_patterns/quality)
   - Set priority based on V usage patterns
   - Add concrete examples
   - Create N5/prefs/principles/P##_slug.yaml
3. Create N5/prefs/principles/principles_index.yaml listing all 35
4. Update BUILD_TRACKER phase2 to COMPLETE, phase3 to READY

## SUCCESS CRITERIA
- 33 total YAML files (P1-P35 new + P36-P37 existing)
- All follow schema
- principles_index.yaml complete
- BUILD_TRACKER updated

Launch: Load this file and execute
