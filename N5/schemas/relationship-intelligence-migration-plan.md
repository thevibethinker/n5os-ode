---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_l99qggsWaRlWKcps
---

# Relationship Intelligence OS - Migration Plan

## Overview

Migration plan for implementing the Relationship Intelligence OS schemas and database changes. This document outlines the required SQLite table changes, data migrations, and backward compatibility considerations.

## Schema Overview

The following five new schemas have been defined:

1. **promotion-event.schema.json** - Memory promotion events and scoring
2. **relationship-delta.schema.json** - Relationship changes and evolution  
3. **org-delta.schema.json** - Organizational intelligence and changes
4. **deliverable-record.schema.json** - Deliverable tracking and reuse
5. **intro-opportunity.schema.json** - Introduction opportunities and mutual connections

## Required SQLite Tables

### New Tables to Create

#### 1. promotion_events
```sql
CREATE TABLE promotion_events (
    promotion_id TEXT PRIMARY KEY,
    meeting_id TEXT NOT NULL,
    block_ids TEXT NOT NULL, -- JSON array
    memory_type TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    score_breakdown TEXT, -- JSON object
    tier TEXT NOT NULL CHECK (tier IN ('A', 'B', 'C')),
    status TEXT NOT NULL,
    hard_overrides TEXT, -- JSON array
    deduplication TEXT, -- JSON object
    memory_writes TEXT, -- JSON object
    created_at TEXT NOT NULL,
    promoted_at TEXT,
    provenance TEXT NOT NULL, -- JSON object
    confidence TEXT NOT NULL, -- JSON object
    
    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
);

CREATE INDEX idx_promotion_events_meeting_id ON promotion_events(meeting_id);
CREATE INDEX idx_promotion_events_tier ON promotion_events(tier);
CREATE INDEX idx_promotion_events_status ON promotion_events(status);
CREATE INDEX idx_promotion_events_score ON promotion_events(score);
CREATE INDEX idx_promotion_events_created_at ON promotion_events(created_at);
```

#### 2. relationship_deltas
```sql
CREATE TABLE relationship_deltas (
    delta_id TEXT PRIMARY KEY,
    person_id TEXT NOT NULL,
    organization_id TEXT,
    delta_type TEXT NOT NULL,
    strength INTEGER NOT NULL CHECK (strength >= 1 AND strength <= 5),
    trend TEXT CHECK (trend IN ('positive', 'negative', 'neutral')),
    context TEXT, -- JSON object
    evidence TEXT NOT NULL, -- JSON array
    mutual_connections TEXT, -- JSON array
    impact_assessment TEXT, -- JSON object
    created_at TEXT NOT NULL,
    expires_at TEXT,
    provenance TEXT NOT NULL, -- JSON object
    confidence TEXT NOT NULL, -- JSON object
    
    FOREIGN KEY (person_id) REFERENCES people(person_id),
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
);

CREATE INDEX idx_relationship_deltas_person_id ON relationship_deltas(person_id);
CREATE INDEX idx_relationship_deltas_org_id ON relationship_deltas(organization_id);
CREATE INDEX idx_relationship_deltas_delta_type ON relationship_deltas(delta_type);
CREATE INDEX idx_relationship_deltas_strength ON relationship_deltas(strength);
CREATE INDEX idx_relationship_deltas_created_at ON relationship_deltas(created_at);
```

#### 3. org_deltas
```sql
CREATE TABLE org_deltas (
    delta_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    organization_name TEXT,
    delta_type TEXT NOT NULL,
    impact_level INTEGER NOT NULL CHECK (impact_level >= 1 AND impact_level <= 5),
    temporal_scope TEXT,
    change_details TEXT, -- JSON object
    business_implications TEXT, -- JSON object
    evidence TEXT NOT NULL, -- JSON array
    competitive_intelligence TEXT, -- JSON object
    created_at TEXT NOT NULL,
    effective_date TEXT,
    review_date TEXT,
    provenance TEXT NOT NULL, -- JSON object
    confidence TEXT NOT NULL, -- JSON object
    
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
);

CREATE INDEX idx_org_deltas_org_id ON org_deltas(organization_id);
CREATE INDEX idx_org_deltas_delta_type ON org_deltas(delta_type);
CREATE INDEX idx_org_deltas_impact_level ON org_deltas(impact_level);
CREATE INDEX idx_org_deltas_created_at ON org_deltas(created_at);
CREATE INDEX idx_org_deltas_effective_date ON org_deltas(effective_date);
```

#### 4. deliverable_records
```sql
CREATE TABLE deliverable_records (
    deliverable_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    client_name TEXT,
    deliverable_type TEXT NOT NULL,
    title TEXT,
    description TEXT,
    scope TEXT NOT NULL, -- JSON object
    status TEXT NOT NULL,
    timeline TEXT, -- JSON object
    ownership TEXT, -- JSON object
    similarity_analysis TEXT, -- JSON object
    context TEXT, -- JSON object
    artifacts TEXT, -- JSON object
    quality_metrics TEXT, -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT,
    provenance TEXT NOT NULL, -- JSON object
    confidence TEXT NOT NULL -- JSON object
);

CREATE INDEX idx_deliverable_records_client_id ON deliverable_records(client_id);
CREATE INDEX idx_deliverable_records_type ON deliverable_records(deliverable_type);
CREATE INDEX idx_deliverable_records_status ON deliverable_records(status);
CREATE INDEX idx_deliverable_records_created_at ON deliverable_records(created_at);
CREATE INDEX idx_deliverable_records_updated_at ON deliverable_records(updated_at);
```

#### 5. intro_opportunities
```sql
CREATE TABLE intro_opportunities (
    opportunity_id TEXT PRIMARY KEY,
    requester_id TEXT NOT NULL,
    requester_name TEXT,
    target_id TEXT NOT NULL,
    target_name TEXT,
    mutual_path TEXT NOT NULL, -- JSON array
    intent TEXT NOT NULL, -- JSON object
    status TEXT NOT NULL,
    feasibility_assessment TEXT, -- JSON object
    timing TEXT, -- JSON object
    preparation TEXT, -- JSON object
    execution TEXT, -- JSON object
    outcome TEXT, -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT,
    expires_at TEXT,
    provenance TEXT NOT NULL, -- JSON object
    confidence TEXT NOT NULL, -- JSON object
    
    FOREIGN KEY (requester_id) REFERENCES people(person_id),
    FOREIGN KEY (target_id) REFERENCES people(person_id)
);

CREATE INDEX idx_intro_opportunities_requester_id ON intro_opportunities(requester_id);
CREATE INDEX idx_intro_opportunities_target_id ON intro_opportunities(target_id);
CREATE INDEX idx_intro_opportunities_status ON intro_opportunities(status);
CREATE INDEX idx_intro_opportunities_created_at ON intro_opportunities(created_at);
CREATE INDEX idx_intro_opportunities_expires_at ON intro_opportunities(expires_at);
```

## Migration Steps

### Phase 1: Database Schema Updates

1. **Backup existing databases**
   ```bash
   cp Personal/CRM/crm.db Personal/CRM/crm.db.backup.$(date +%Y%m%d)
   cp Personal/Memory/brain.db Personal/Memory/brain.db.backup.$(date +%Y%m%d)
   ```

2. **Create new tables**
   - Execute the CREATE TABLE statements above
   - Add indexes for performance

3. **Verify table creation**
   ```bash
   python3 N5/scripts/validate_schema_migration.py --check-tables
   ```

### Phase 2: Data Migration (if applicable)

Since these are new tables, no existing data migration is required. However, we should:

1. **Initialize system metadata tables**
   ```sql
   INSERT INTO schema_versions (schema_name, version, applied_at)
   VALUES 
     ('promotion_events', '1.0', datetime('now')),
     ('relationship_deltas', '1.0', datetime('now')),
     ('org_deltas', '1.0', datetime('now')),
     ('deliverable_records', '1.0', datetime('now')),
     ('intro_opportunities', '1.0', datetime('now'));
   ```

2. **Set up foreign key constraints** (if not already enforced)
   ```sql
   PRAGMA foreign_keys = ON;
   ```

### Phase 3: Validation and Testing

1. **Schema validation**
   - Test all JSON schema validations
   - Verify foreign key constraints
   - Test index performance

2. **Integration testing**
   - Test with sample data
   - Verify all required fields are enforced
   - Test confidence and provenance fields

## Backward Compatibility Strategy

### Compatibility Approach

1. **Additive Changes Only**
   - All new schemas are additive - no existing data structures are modified
   - Existing CRM and brain.db schemas remain unchanged
   - New tables augment rather than replace existing functionality

2. **Versioned Schema Evolution**
   - All schemas include version numbers
   - Migration scripts track schema versions
   - Rollback capability maintained through versioning

3. **Graceful Degradation**
   - System continues to function without new tables
   - Missing tables are created on first use
   - Default values provided for all optional fields

### Migration Safety

1. **Dry-Run Mode**
   ```bash
   python3 N5/scripts/validate_schema_migration.py --dry-run
   ```

2. **Rollback Plan**
   - Backup all databases before migration
   - DROP TABLE statements available for rollback
   - Version tracking allows selective rollback

3. **Incremental Rollout**
   - Tables created but not immediately populated
   - Gradual activation of promotion pipeline
   - Monitoring and validation at each step

### Breaking Change Policy

**No breaking changes in v1.0:**
- All existing APIs remain functional
- No removal of existing fields or tables
- No changes to existing data formats

**Future breaking changes:**
- Will require v2.0 schema version
- Migration path provided for all breaking changes
- Deprecation notices provided 6 months in advance

## Validation Requirements

### Schema Validation

1. **JSON Schema Validation**
   - All JSON fields validate against their schemas
   - Required fields enforced at database level
   - Type constraints verified

2. **Foreign Key Validation**
   - Person IDs must exist in people table
   - Organization IDs must exist in organizations table  
   - Meeting IDs must exist in meetings table

3. **Business Rule Validation**
   - Confidence scores between 0 and 1
   - Strength/impact scores within defined ranges
   - Status transitions follow defined state machine

### Data Quality Validation

1. **Provenance Completeness**
   - All records must have valid provenance
   - Conversation IDs must be valid
   - Pipeline run IDs must be trackable

2. **Confidence Thresholds**
   - Overall confidence > 0.3 for auto-promotion
   - Evidence quality > 0.5 for Tier A promotion
   - Person identification > 0.8 for relationship deltas

## Testing Strategy

### Unit Tests
```bash
# Test individual schema validation
python3 N5/scripts/test_schema_validation.py

# Test database operations
python3 N5/scripts/test_database_operations.py

# Test migration scripts
python3 N5/scripts/test_migration_scripts.py
```

### Integration Tests
```bash
# Test full pipeline with sample data
python3 N5/scripts/test_relationship_intelligence_pipeline.py

# Test cross-table relationships
python3 N5/scripts/test_foreign_key_constraints.py

# Test performance with realistic data volumes
python3 N5/scripts/test_performance.py
```

### Validation Tests
```bash
# Test all sample payloads
python3 N5/scripts/validate_sample_payloads.py

# Test schema compliance
python3 N5/scripts/validate_schema_compliance.py
```

## Performance Considerations

### Index Strategy
- Primary keys for unique identification
- Foreign key indexes for join performance
- Date indexes for temporal queries
- Status indexes for filtering

### Storage Optimization
- JSON fields for flexible schema evolution
- Normalized person/organization references
- Efficient ID patterns for indexing

### Query Optimization
- Prepared statements for common queries
- Appropriate index usage
- Query plan analysis for complex joins

## Monitoring and Observability

### Schema Health Metrics
- Table row counts
- JSON validation error rates
- Foreign key constraint violations
- Query performance metrics

### Data Quality Metrics
- Average confidence scores by type
- Provenance completeness rates
- Duplicate detection rates
- Pipeline processing times

## Implementation Checklist

- [ ] Create all five database tables
- [ ] Add all required indexes
- [ ] Test foreign key constraints
- [ ] Validate JSON schema compliance
- [ ] Test sample data insertion
- [ ] Verify query performance
- [ ] Set up monitoring
- [ ] Document rollback procedures
- [ ] Run full integration test suite
- [ ] Update system documentation