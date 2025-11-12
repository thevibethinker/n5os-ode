---
created: 2025-11-04
version: 2.0
purpose: MECE Knowledge Decomposition with Cross-Reference Strategy
---

# Enhanced Decomposition Plan: MECE + Knowledge Graph

## MECE Domain Boundaries (Conflict Resolution Rules)

### Hierarchy of Truth
1. **stable/** = Timeless facts about company (what IS)
2. **semi_stable/** = Current state that changes quarterly (what IS NOW)
3. **hypotheses/** = Testable claims requiring validation (what we BELIEVE)
4. **patterns/** = Reusable strategic insights (HOW things work)
5. **market_intelligence/** = External landscape facts (what OTHERS are)
6. **stakeholder_research/** = Specific entity deep-dives (WHO specifically)
7. **architectural/** = Decision frameworks & mental models (HOW TO THINK)

### Conflict Resolution Rules
- **Metric appears in multiple contexts?** → stable/ gets definition, semi_stable/ gets current value, hypotheses/ gets prediction
- **Competitive insight?** → market_intelligence/ gets facts, patterns/ gets "why" analysis
- **Positioning statement?** → stable/company/ gets canonical version, architectural/ gets framework, semi_stable/ gets current experiments
- **Stakeholder info appears elsewhere?** → stakeholder_research/ is SSOT, others reference it

## Content Allocation Matrix

| Source Section | Primary Destination | Secondary References | Rationale |
|----------------|-------------------|---------------------|-----------|
| 1.1: What Careerspan Is | stable/company/positioning.md | architectural/frameworks (ref only) | Canonical identity |
| 1.2: Three-Layer Moat | stable/company/overview.md | hypotheses/business_model (testable claims) | Core architecture |
| 1.3: Traction Metrics | semi_stable/current_metrics.md | stable/company/overview (references only) | Changes quarterly |
| 2: Positioning Framework | architectural/frameworks.md | stable/company/positioning (application) | Reusable framework |
| 3: Competitive Analysis | market_intelligence/competitive_landscape.md | patterns/two_sided (why analysis) | External facts |
| 4: SHRM Profile | stakeholder_research/shrm_application.md | market_intelligence (context only) | Entity-specific |
| 5: Mid-market Opportunity | hypotheses/gtm_hypotheses.md | market_intelligence (market facts) | Testable GTM claim |
| 6: Messaging Architecture | architectural/frameworks.md | stable/company/positioning (links) | Mental model |
| 7: Competitive Why | patterns/two_sided_marketplace.md | market_intelligence (facts used) | Strategic pattern |
| 8: Q49 Challenges | stakeholder_research/shrm_application.md | ONLY there | Application-specific |

## Cross-Reference Strategy (Knowledge Graph via Breadcrumbs)

### Bidirectional Linking Pattern
Every file includes:
1. **"See Also" section** at bottom with contextual pointers
2. **Inline references** using path: cannot open `path' (No such file or directory) syntax where concepts connect
3. **"Referenced By" backlinks** when creating new files

### Example Cross-Reference Web

**stable/company/positioning.md:**


**market_intelligence/competitive_landscape_2024.md:**


**patterns/two_sided_marketplace_patterns.md:**


### Cross-Reference Density Target
- **Minimum:** 3 outbound references per file
- **Optimal:** 5-7 outbound references per file
- **Pattern:** Mix of inline (contextual) + "See Also" section (exploratory)

## MECE Verification Checklist

### Pre-Execution
- [ ] Content allocation matrix covers ALL source sections
- [ ] No source section maps to >1 PRIMARY destination
- [ ] Domain conflict rules defined for edge cases

### During Execution
- [ ] Track extracted content line-by-line
- [ ] Mark source content as "allocated" after extraction
- [ ] Flag any ambiguous content for manual review

### Post-Execution
- [ ] Source report 100% allocated (verified by section)
- [ ] No duplicate content across files (spot check)
- [ ] Every created/updated file has ≥3 cross-references
- [ ] Cross-references are bidirectional (A→B and B→A)
- [ ] Archive original report with "Decomposed to:" links

## Execution Sequence (Revised)

1. **Create skeleton files** with metadata + "See Also" stubs
2. **Extract content** following allocation matrix strictly
3. **Add inline references** while writing each section
4. **Complete "See Also" sections** after all files created
5. **Verify bidirectional links** (automated check)
6. **Run MECE verification** checklist
7. **Update indices** in each Knowledge subdirectory

## Success Metrics

- ✅ Zero orphaned content (all source content allocated)
- ✅ Zero duplication (each fact in exactly one place)
- ✅ 100% cross-reference coverage (every file has ≥3 links)
- ✅ Bidirectional graph (if A→B then B→A exists)
- ✅ Domain boundaries respected (no conflicts)
