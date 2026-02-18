---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_yb4QuKxqeCS7HE9s
---

# Relationship Intelligence OS - Schema Documentation

## Overview

This directory contains canonical schemas for the Relationship Intelligence OS pipeline's five core data products. These schemas ensure consistent structure, validation, and interoperability across the intelligence processing pipeline.

## Core Data Products

### 1. Promotion Event (`promotion_event.schema.json`)
**Purpose:** Tracks meeting intelligence candidates through the promotion gate with scoring, tiering, and deduplication.

**Key Features:**
- 0-100 scoring with rubric breakdown (strategic importance, relationship strength, commitment clarity, evidence quality, novelty, execution value)
- Tier assignment: A (75-100, auto-promote), B (50-74, review digest), C (<50, archive)
- Hard override rules for explicit promises, intros, named deliverables
- Idempotency keys to prevent duplicate processing
- Write results tracking across semantic memory, graph edges, CRM projections

**ID Pattern:** `pe_[a-z0-9]{8}`

### 2. Relationship Delta (`relationship_delta.schema.json`)
**Purpose:** Captures person/org relationship changes with trend analysis and confidence scoring.

**Key Features:**
- Delta types: sentiment_shift, engagement_level, decision_authority, priority_change, urgency_shift, trust_level, champion_status, buying_role, influencer_mapping, relationship_depth
- Trend tracking: increasing, decreasing, stable, fluctuating
- Previous/current state comparison with confidence scores
- Evidence with direct quotes, behavioral indicators, sentiment markers
- Mutual connections and intro implications
- Impact assessment (deal stage, timeline, risk level)

**ID Pattern:** `rd_[a-z0-9]{8}`

### 3. Organization Delta (`org_delta.schema.json`)
**Purpose:** Tracks organizational changes and strategic shifts with competitive intelligence.

**Key Features:**
- Delta types: priority_shift, budget_change, timeline_update, process_change, decision_authority_shift, competitive_landscape, strategic_initiative, vendor_evaluation_process, approval_workflow, technology_adoption, compliance_requirement, organizational_restructure, leadership_change, market_pressure
- Impact scope: departmental, division, company_wide, ecosystem
- Strategic signals: expansion_signal, cost_reduction, digital_transformation, compliance_driven, competitive_response, efficiency_initiative, growth_phase, restructuring
- Buying process change tracking
- Competitive intelligence with market positioning shifts

**ID Pattern:** `od_[a-z0-9]{8}`

### 4. Deliverable Record (`deliverable_record.schema.json`)
**Purpose:** Tracks deliverable requests, commitments, and lifecycle status with reuse detection.

**Key Features:**
- Lifecycle status: identified, scoped, assigned, in_progress, review, delivered, accepted, rejected, cancelled, on_hold
- Client-scoped deduplication and similarity analysis
- Reuse decisions: create_new, reuse_existing, adapt_existing
- Launcher prompt generation for creation/adaptation/review
- Stakeholder tracking (requestor, approver, reviewers, recipients)
- Quality metrics (scope clarity, timeline clarity, stakeholder clarity)

**ID Pattern:** `del_[a-z0-9]{8}`

### 5. Introduction Opportunity (`intro_opportunity.schema.json`)
**Purpose:** Tracks introduction opportunities and mutual connection paths for networking facilitation.

**Key Features:**
- Opportunity types: business_development, partnership_potential, hiring_match, vendor_referral, knowledge_sharing, mutual_customer, industry_networking, geographic_connection, skill_complementarity, investment_opportunity, advisory_connection, speaking_opportunity
- Mutual value proposition with specific benefits to each party
- Connection path analysis (direct, one_hop, two_hop, multi_hop)
- Risk assessment (competitive concerns, privacy considerations)
- Recommended approach with introduction methods and templates
- Outcome tracking and lessons learned

**ID Pattern:** `io_[a-z0-9]{8}`

## Universal Requirements

All schemas include these mandatory fields:

### Provenance
```json
{
  "provenance": {
    "processor_version": "1.0.0",
    "conversation_id": "con_[A-Za-z0-9]+",
    "processing_mode": "production|dry_run|test",
    "source_blocks": ["block_id1", "block_id2"]
  }
}
```

### Confidence
```json
{
  "confidence": 0.85  // Float 0-1, overall confidence in the assessment
}
```

### Evidence Structure
```json
{
  "evidence": {
    "quotes": [
      {
        "text": "Direct quote from meeting",
        "speaker": "Person Name",
        "context": "Additional context",
        "timestamp_in_meeting": "optional"
      }
    ],
    "block_references": ["block_id1", "block_id2"]
  }
}
```

## Validation

### Schema Validation Tool
Use the provided validation utility:

```bash
# Test all sample payloads
python3 N5/schemas/validate_schemas.py --test-samples

# Validate specific file
python3 N5/schemas/validate_schemas.py --schema promotion_event --file data.json
```

### Validation Features
- JSON Schema compliance checking
- Additional business logic validation
- Provenance format verification
- Confidence range validation
- Schema-specific validation (score breakdown consistency, timeline chronology, etc.)

## Database Integration

### SQLite Tables
See `relationship_intelligence_migration.md` for complete database schema including:
- Table creation statements with constraints
- Indexes for query performance
- Migration strategy and rollback plans
- Data retention policies

### Key Database Features
- JSON column types for flexible nested data
- Foreign key relationships to existing `resources` table via `source_meeting_id`
- Check constraints for enum values and score ranges
- Indexes optimized for common query patterns

## Usage Patterns

### Promotion Pipeline
1. Extract candidates from meeting blocks
2. Score using rubric (0-100 scale)
3. Apply hard override rules
4. Run deduplication analysis  
5. Determine tier (A/B/C) and routing
6. Write to downstream systems (memory, graph, CRM)
7. Track promotion event with results

### Intelligence Extraction
1. Analyze meeting blocks for deltas/opportunities
2. Extract structured data using schemas
3. Validate against business rules
4. Store with provenance and confidence
5. Enable downstream consumption (email generation, launcher prompts, etc.)

## Backward Compatibility

### Schema Evolution
- New optional fields can be added without breaking changes
- Required fields cannot be removed
- Enum values can be extended but not removed
- Version tracking in provenance enables migration

### Integration Points
- Existing `brain.db` tables remain unchanged
- New tables use foreign keys to existing schema
- Existing queries continue to work
- Validation is additive, not restrictive

## Quality Assurance

### Confidence Scoring
- All records include confidence scores (0-1)
- Lower confidence items can be flagged for human review
- Confidence thresholds can be adjusted per use case

### Evidence Requirements
- All intelligence must include supporting evidence
- Direct quotes with speaker attribution required
- Block references enable traceability back to source
- Evidence quality affects promotion scoring

### Validation Gates
- Schema validation prevents malformed data
- Business rule validation catches logical inconsistencies
- Confidence thresholds enable quality filtering
- Human validation workflows for disputed items

## Monitoring and Observability

### Performance Metrics
- Schema validation success rates
- Confidence score distributions
- Processing times per schema type
- Database query performance on indexes

### Data Quality Metrics  
- Evidence completeness rates
- Confidence calibration accuracy
- Human validation agreement rates
- Downstream consumer satisfaction

This schema system enables the Relationship Intelligence OS to systematically capture, validate, and utilize meeting intelligence while maintaining data quality and traceability throughout the pipeline.