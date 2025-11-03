# CONVERSATION 4: Safety & Quality Principles

**Phase:** 2 (Batch 1 of 3)  
**Persona:** Vibe Builder  
**Duration:** 2 hours  
**Dependencies:** Conv 3 ✅

---

## MISSION

Migrate 13 principles to YAML format with complete schema compliance.

---

## DELIVERABLES

### Safety Batch (6 principles)
1. **P5:** Safety, Determinism, Anti-Overwrite
2. **P7:** Idempotence and Dry-Run
3. **P11:** Failure Modes and Recovery
4. **P19:** Error Handling (Silent Errors)
5. **P21:** Document Assumptions
6. **P23:** Identify Trap Doors

### Quality Batch (7 principles)
1. **P15:** Complete Before Claiming
2. **P16:** No Invented Limits
3. **P18:** Verify State Changes
4. **P20:** Modular and Composable
5. **P28:** Plans as Code DNA
6. **P30:** Maintain Feel for Code
7. **P33:** Old Tricks Still Work

---

## YAML SCHEMA (Required Fields)



---

## EXECUTION PROTOCOL

1. Load planning_prompt.md
2. For each of the 13 principles:
   - Create file N5/prefs/principles/P##_slug.yaml
   - Follow schema exactly
   - Include all required fields
   - Add examples (good + bad)
   - List anti-patterns
   - Cross-reference related principles
3. Validate all 13 against schema
4. Update principle index
5. Quality gate check

---

## QUALITY GATE

✅ All 13 files created  
✅ All validate against schema  
✅ No duplicate IDs  
✅ Cross-references valid  
✅ Examples present (good + bad)  
✅ Anti-patterns documented  

---

## TIME ESTIMATE

- 8 min per principle × 13 = 104 min (1h 44m)
- Index update: 10 min
- Validation: 6 min
- **Total: 2 hours**

---

**Ready to execute Conv 4**
