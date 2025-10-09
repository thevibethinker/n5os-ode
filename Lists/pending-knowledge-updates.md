# Pending Knowledge Base Updates

**Purpose**: Track semi-stable information extracted from meetings that needs to be integrated into the knowledge base.

**Last Updated**: 2025-10-09

---

## Overview

This list captures proposed updates to the knowledge base generated during meeting processing. Each entry represents validated insights, constraints, patterns, or principles that should be permanently integrated into strategic documentation.

**Status Values**:
- `pending` - Awaiting review and integration
- `in-progress` - Being integrated
- `completed` - Successfully integrated into knowledge base
- `rejected` - Decided not to integrate (with reason)

---

## Pending Updates (2)

### PKB-004: Break the mold all the way
**Source**: Alex Caveny Coaching (2025-09-24)  
**Type**: Strategic Principle  
**Target**: `file 'Knowledge/stable/company/principles.md'` → Product Philosophy  
**Priority**: High  
**Confidence**: High

**Update**:
Core principle: If disrupting recruiting industry, don't do it halfway. Don't just filter resumes better - present information in fundamentally different format. Don't just target better - use different channels. Don't just pitch better - use different approach. "Format IS product when attention is scarce."

**Evidence**:
- Synthesized from Alex session + Vrijen realization "question all the priors here"
- Led to 5+ tactical decisions:
  - Playing card UI (different format)
  - URL-based bundles (different delivery)
  - Thematic categories vs. fit scores (different framing)
  - Hiring managers vs. HR (different channel)
  - Goods upfront (different approach)

**Long-term implications**: PM guilds concept, signing bonus model - fundamentally different paradigm for talent industry

**Status**: Pending

---

### PKB-005: Alex Caveny stakeholder profile
**Source**: Alex Caveny Coaching (2025-09-24)  
**Type**: Stakeholder Profile  
**Target**: `file 'Knowledge/context/stakeholders/alex-caveny.md'` (new file)  
**Priority**: Low  
**Confidence**: High

**Update**:
Create stakeholder profile for Alex Caveny:
- **Role**: Advisor (new stakeholder type)
- **Background**: Former founder, now doing advisory work as "middle ground"
- **Expertise**: Product development, go-to-market, hiring (firsthand hiring manager experience)
- **Relationship potential**: 
  - Current: Business/leadership coaching advisor
  - Can refer: Talented engineers/PMs looking for jobs
  - Potential customer: If advising companies with hiring needs

**Contact**: Uses booking link for scheduling, next session October

**Status**: Pending

---

## Completed Updates (4)

### PKB-001: Hiring managers prefer goods-upfront approach ✅
**Source**: Alex Caveny Coaching (2025-09-24)  
**Completed**: 2025-10-09  
**Integrated**: `file 'Knowledge/hypotheses/gtm_hypotheses.md'` as **H-GTM-008**

Validated that hiring managers prefer seeing candidates immediately vs. relationship-building first. Integrated with full evidence and implications for outreach strategy.

---

### PKB-002: Subscription contingent on placement proof ✅
**Source**: Alex Caveny Coaching (2025-09-24)  
**Completed**: 2025-10-09  
**Integrated**: `file 'Knowledge/stable/company/strategy.md'` → **Pricing Model** section

Strategic constraint documented: Companies require proof before subscription. Phased approach (warm intro → subscription) now part of pricing strategy.

---

### PKB-003: PM hiring more chaotic than engineering ✅
**Source**: Alex Caveny Coaching (2025-09-24)  
**Completed**: 2025-10-09  
**Integrated**: `file 'Knowledge/stable/company/strategy.md'` → **Target Market** section

Market insight integrated explaining strategic rationale for product manager focus. Documented why PM hiring chaos matches Careerspan's strengths.

---

### PKB-006: HR resists disruption due to job security ✅
**Source**: Alex Caveny Coaching (2025-09-24)  
**Completed**: 2025-10-09  
**Integrated**: `file 'Knowledge/hypotheses/gtm_hypotheses.md'` as **H-GTM-009**

Validated hypothesis about HR resistance and hiring manager receptiveness. Integrated with targeting implications and positioning guidance.

---

## Integration Workflow

### For Each Pending Update:

1. **Review**: Read source meeting files, validate evidence
2. **Locate target**: Find correct knowledge base file and section
3. **Check duplicates**: Search for existing similar content
4. **Integrate**: Add content following MECE principles
5. **Cross-reference**: Update related files if needed
6. **Update glossary**: Add new terminology if introduced
7. **Mark complete**: Change status, add completion timestamp
8. **Log**: Document what was integrated and where

---

## Statistics

- **Total entries**: 6
- **Pending**: 2
- **Completed**: 4
- **High priority pending**: 1
- **Medium priority**: 0
- **Low priority**: 1

**By Type**:
- Hypothesis Validation: 2 (both completed ✅)
- Strategic Constraint: 1 (completed ✅)
- Market Insight: 1 (completed ✅)
- Strategic Principle: 1 (pending)
- Stakeholder Profile: 1 (pending)

**By Source Meeting**:
- 2025-09-24 Alex Caveny Coaching: 6 (4 completed, 2 pending)

---

## Related Files

- `file 'N5/commands/meeting-process.md'` - Meeting processing generates these updates
- `file 'Knowledge/architectural/ingestion_standards.md'` - Standards for knowledge base updates
- `file 'N5/prefs/knowledge/lookup.md'` - Knowledge base structure and hierarchy
- `file 'Lists/POLICY.md'` - Lists management policy

---

## Notes

- Updates generated during **essential** and **full** meeting processing modes (not quick)
- Each meeting can generate 0-10 updates depending on strategic content
- Priority determined by: impact on decisions × confidence × immediacy
- Updates should be batched and integrated weekly to maintain knowledge base quality
