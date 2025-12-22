---
created: 2025-12-16
last_edited: 2025-12-16
version: 1.0
provenance: agent_0dff3095-1068-4f53-a478-6f566f8164a0
---

# Reasoning Pattern: MG-5 v2 Scanning and Assessment Strategy

**Pattern Name**: Systematic Meeting Eligibility Assessment  
**Category**: Workflow Execution  
**Source Task**: MG-5 v2 Follow-Up Email Generation  
**Confidence**: High (validated through multi-phase scanning)  

## Pattern Summary

This pattern describes a methodical approach to scanning large file trees for workflow-eligible items when initial assumptions prove incorrect. It emphasizes data-driven iteration and progressive refinement of search criteria rather than assuming initial conditions.

## When to Use

- Scheduled tasks with complex eligibility criteria
- Large directory trees with inconsistent metadata
- When initial scanning returns zero results  
- Multi-criteria workflow triggers

## The Pattern

### Phase 1: Broad Scanning
1. Start with most restrictive criteria (exact field matches)
2. Catalog all potential candidates without filtering
3. Document zero-result scenarios explicitly

### Phase 2: Progressive Relaxation
When Phase 1 returns zero:
1. Relax one constraint at a time (status → folder name → location)
2. Check for degraded/minimal content that appears complete but isn't
3. Verify actual file contents vs. metadata expectations

### Phase 3: Reality Check
1. Check quarantine/archive directories for "hidden" candidates  
2. Validate content quality of "complete" meetings
3. Assess whether workflow should trigger on historical data

### Phase 4: Decision Point
1. If after relaxation no candidates exist → workflow complete
2. If candidates exist but content insufficient → flag for manual review
3. Document findings and completion status honestly

## Key Insights Applied

1. **Metadata ≠ Reality**: Manifest.json indicated "processed" but actual transcript was 2 seconds of unusable audio
2. **Location Matters**: All [M] state meetings were in quarantine/archive (not active)
3. **Content Quality Gates**: Required files existing ≠ sufficient content for workflow execution
4. **Honest Completion Reporting**: It's better to report "0/0 complete (100%)" than fabricate work

## Expected Output

For each candidate:
- Folder path
- Status (M/P/processed)
- Content completeness (boolean per required file)
- Quality assessment (usable/minimal/degraded)
- Eligibility decision (proceed/skip/flag)

## Validation Criteria

- All manifest.json files scanned (check count vs. expected)
- Zero ignored errors in content parsing
- Clear completion status communicated
- Reasoning patterns extracted and stored

---
**Pattern Status**: Validated and Stored  
**Next Review**: After next MG-5 execution
