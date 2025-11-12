# Quality Sampling Strategy - Meeting Intelligence System

**Version**: 1.0  
**Created**: 2025-11-03  
**Purpose**: Define systematic approach to quality assurance through strategic sampling and regression testing

---

## Overview

The quality sampling strategy ensures consistent output quality across 37 production blocks through strategic sample collection, regression testing, and continuous monitoring.

---

## Sampling Categories

### 1. **Baseline Samples** (Golden Samples)
- **Purpose**: Establish quality baseline for each block type
- **Coverage**: 1-2 samples per block (minimum)
- **Selection Criteria**:
  - Representative of typical meeting context
  - Clean, well-structured input data
  - Demonstrates all key block features
  - Expected output clearly defined
- **Priority Blocks**: Start with high-usage blocks (B01, B02, B08, B13, B26, B40)

### 2. **Edge Case Samples**
- **Purpose**: Test boundary conditions and unusual inputs
- **Examples**:
  - Very short meetings (< 10 minutes)
  - Very long meetings (> 2 hours)
  - Multi-speaker complex dynamics
  - Technical/jargon-heavy content
  - Sparse information (minimal context)
  - Missing metadata
- **Coverage**: 3-5 critical edge cases per category

### 3. **Regression Samples**
- **Purpose**: Catch quality degradation from prompt/system changes
- **Selection**: Previous high-quality outputs that must remain stable
- **Update Strategy**: Add samples when bugs are fixed to prevent recurrence
- **Coverage**: Build to 20-30 total samples across all block types

### 4. **Cross-Category Samples**
- **Purpose**: Test consistency across meeting types
- **Coverage**: Same meeting processed through multiple blocks
- **Categories**:
  - External meetings (client, partner, investor)
  - Internal meetings (team sync, planning, review)
  - Reflection sessions
  - Market/competitive intelligence

---

## Sample Collection Process

### Phase 1: Initial Collection (Target: 15-20 samples)
1. **High-Priority Blocks** (Week 1):
   - B01 DETAILED_RECAP (2 samples: standard, complex)
   - B02 COMMITMENTS_CONTEXTUAL (2 samples: single, multiple commitments)
   - B08 STAKEHOLDER_INTELLIGENCE (2 samples: single, multiple stakeholders)
   - B13 PLAN_OF_ACTION (2 samples: simple, multi-step plan)
   - B26 MEETING_METADATA_SUMMARY (2 samples: standard, edge case)
   - B40 INTERNAL_DECISIONS (2 samples: clear, ambiguous decisions)

2. **Category Coverage** (Week 2):
   - External meeting samples: 3-4 diverse examples
   - Internal meeting samples: 2-3 examples
   - Reflection samples: 2-3 examples

3. **Edge Cases** (Week 3):
   - Short meeting (< 15 min)
   - Long meeting (> 90 min)
   - Sparse context
   - Multi-stakeholder complexity

### Phase 2: Expansion (Target: 30-40 samples)
- Cover remaining 31 blocks
- Add 1 sample minimum per uncovered block
- Focus on blocks with validation failures

### Phase 3: Continuous Addition
- Add samples when bugs are discovered
- Add samples for new block types
- Replace outdated samples quarterly

---

## Testing Frequency

### Automated Testing Schedule

**Daily** (Smoke Tests):
- Run top 5 critical samples
- Alert on any failures
- Time: 5 minutes

**Weekly** (Regression Suite):
- Run full sample set (15-40 samples)
- Generate quality report
- Review trends
- Time: 15-30 minutes

**On-Demand** (Validation):
- Before deploying prompt changes
- After system updates
- When investigating quality issues
- Time: 5-30 minutes depending on scope

### Manual Review Schedule

**Weekly**:
- Review automated test results
- Investigate any failures
- Update expected outputs if needed
- Document pattern changes

**Monthly**:
- Comprehensive quality audit
- Sample set health check
- Remove outdated samples
- Add new strategic samples
- Update quality thresholds

---

## Quality Metrics

### Sample-Level Metrics
- **Validation Score**: 0.0-1.0 (target: > 0.85)
- **Pass Rate**: % of successful validations
- **Regression Status**: Stable vs. Degraded
- **Last Tested**: Timestamp of last test run

### Block-Level Metrics
- **Sample Coverage**: Number of samples per block
- **Average Quality Score**: Mean validation score across samples
- **Failure Rate**: % of samples failing validation
- **Trend**: Improving, Stable, Degrading

### System-Level Metrics
- **Total Sample Count**: Current sample inventory
- **Overall Pass Rate**: % passing across all samples
- **Coverage Ratio**: Blocks with samples / Total blocks
- **Test Execution Time**: Time to run full suite

---

## Expected Output Standards

### Documentation Requirements
Each quality sample must include:

1. **Input Snapshot**:
   - Meeting transcript or key context
   - Meeting metadata (duration, participants, type)
   - Any relevant historical context
   - Block-specific requirements

2. **Expected Output**:
   - Full expected block output
   - Validation criteria that should pass
   - Known edge cases handled
   - Format requirements met

3. **Metadata**:
   - Sample type (baseline, edge case, regression)
   - Meeting ID or synthetic ID
   - Creation date
   - Last validation date
   - Current validation score

4. **Notes**:
   - Why this sample was selected
   - Key features being tested
   - Historical context (e.g., "Added after bug #42 fix")
   - Edge cases demonstrated

---

## Validation Criteria

### Automatic Checks
- **Format Validation**: Structure matches expected format
- **Completeness**: All required sections present
- **Length Bounds**: Output within expected size range
- **Data Quality**: No placeholder text, proper formatting

### Manual Review Criteria
- **Accuracy**: Information matches meeting content
- **Relevance**: Focus on most important points
- **Clarity**: Output is clear and actionable
- **Consistency**: Style matches block conventions

---

## Quality Degradation Response

### Alert Thresholds
- **Critical**: > 25% of samples failing (immediate investigation)
- **Warning**: > 10% of samples failing (review within 24 hours)
- **Notice**: Individual sample failure (review within week)

### Investigation Process
1. **Identify**: Which samples failed and when
2. **Diagnose**: Compare to expected output, check recent changes
3. **Classify**: Is this a prompt issue, data issue, or system issue?
4. **Fix**: Update prompts, fix bugs, or update expected outputs
5. **Verify**: Re-run failed samples
6. **Document**: Log the issue and resolution

### Rollback Criteria
- Critical samples failing after deployment
- > 50% failure rate in any category
- Severe quality degradation affecting core blocks

---

## Sample Storage

### Database Schema
Using existing `quality_samples` table:
```sql
sample_id (PK)
block_id (FK)
meeting_id
generation_id (optional FK)
sample_type: 'baseline' | 'edge_case' | 'regression'
input_snapshot: JSON
output_snapshot: JSON
validation_score: 0.0-1.0
notes: TEXT
created_at
last_tested_at
test_pass_count
test_fail_count
```

### File Organization
```
Intelligence/
├── test_samples/
│   ├── inputs/
│   │   ├── B01_standard.json
│   │   ├── B01_complex.json
│   │   └── ...
│   ├── expected_outputs/
│   │   ├── B01_standard_expected.md
│   │   ├── B01_complex_expected.md
│   │   └── ...
│   └── test_configs/
│       ├── smoke_tests.json
│       └── full_suite.json
```

---

## Integration with Generation Engine

### Pre-Generation Validation
- Check if block has quality samples
- Reference expected formats
- Use sample context for consistency

### Post-Generation Testing
- Compare new outputs to sample patterns
- Flag significant deviations
- Suggest sample additions for new patterns

### Continuous Learning
- High-quality generations → candidate samples
- Failed generations → edge case samples
- User-approved outputs → golden samples

---

## Success Metrics

### Short-term (1 month)
- ✅ 15-20 quality samples collected
- ✅ Test suite runs automatically
- ✅ Weekly regression testing established
- ✅ Basic quality dashboard available

### Medium-term (3 months)
- ✅ 30-40 quality samples covering all critical blocks
- ✅ < 5% regression failure rate
- ✅ Automated alerting on quality degradation
- ✅ Quality trends tracked and reported

### Long-term (6 months)
- ✅ Full block coverage (1+ sample per block)
- ✅ Comprehensive edge case library
- ✅ Quality scores improving or stable
- ✅ Regression catches issues before production

---

## Maintenance Schedule

### Weekly
- Run full regression suite
- Review any failures
- Update pass/fail counts

### Monthly
- Audit sample quality
- Add new strategic samples
- Remove outdated samples
- Update documentation

### Quarterly
- Comprehensive system review
- Revalidate all baselines
- Update quality thresholds
- Plan next quarter priorities

---

**Next Steps**:
1. Collect initial 15-20 samples (W6 deliverable)
2. Implement test runner script (W6 deliverable)
3. Run first baseline test
4. Establish weekly testing routine
5. Build quality dashboard (future)

---

*Last Updated: 2025-11-03 04:19 EST*
