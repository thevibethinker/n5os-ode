---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# Meeting System Validation Plan

**Objective:** Validate meeting intelligence system end-to-end before processing 20 queued meetings

**Test Meeting:** watch_test-transcript.transcript.md (1 line, minimal complexity)

## Validation Steps

### 1. Manual Workflow Execution ✓
- [x] Understand scheduled task instruction
- [x] Identify queue system (processing_queue.jsonl)
- [ ] Create test output directory
- [ ] Manually execute B26 prompt
- [ ] Manually execute B28 prompt  
- [ ] Manually execute B01 prompt
- [ ] Manually execute B02 prompt
- [ ] Check if B08 triggers (external only)
- [ ] Check conditional blocks

### 2. Block Quality Validation
- [ ] B26: Real metadata (not placeholder)
- [ ] B28: Real strategic intelligence
- [ ] B01: Real recap
- [ ] B02: Real commitments
- [ ] All blocks have proper YAML frontmatter
- [ ] All blocks reference transcript content

### 3. Folder Naming Test
- [ ] Run name_normalizer.py on test output
- [ ] Verify folder name format matches YYYY-MM-DD_stakeholder_type

### 4. System Safety Checks
- [ ] Duplicate detection working
- [ ] Skip logic for already-processed meetings
- [ ] Error handling in completion marker

## Current Status

**Queue:** 20 meetings pending in processing_queue.jsonl  
**Recently Processed:** 2025-11-04_unknown_external (5 blocks), 2025-11-04_alex-caveny_wisdom-partners_coaching (7 blocks)

**Issue from Work Package:** Allie meeting generated empty placeholders  
**Hypothesis:** Scheduled task may not be properly invoking prompts as tools (using file mentions)

## Next Actions

1. Create test directory structure for watch_test
2. Execute each block generation prompt manually
3. Validate output quality
4. Document any issues found
5. Fix issues before bulk processing

