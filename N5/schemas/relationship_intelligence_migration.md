---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_GQyankzmwHlDkCuV
---

# Relationship Intelligence OS - Database Migration Plan

## Overview

This document defines the SQLite schema migration plan for the Relationship Intelligence OS pipeline. The schema supports the five core data products while maintaining backward compatibility with the existing `brain.db` structure.

## Migration Strategy

### Phase 1: Table Creation (No Breaking Changes)
- Add new tables with foreign key relationships to existing `resources` table
- All new tables are additive - existing queries continue to work
- Use JSON column types for flexible nested data storage

### Phase 2: Index Creation (Performance)
- Add indexes for common query patterns
- Optimize for promotion gate queries and intelligence retrieval

### Phase 3: Data Population (Optional)
- Backfill existing meeting data if desired
- Can be done gradually without system downtime

## Database Schema

### Core Tables

#### `promotion_events` Table
Tracks all promotion gate events with scoring and routing decisions.

```sql
CREATE TABLE IF NOT EXISTS promotion_events (
    event_id TEXT PRIMARY KEY CHECK (event_id GLOB 'pe_[a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9]'),
    timestamp DATETIME NOT NULL,
    source_meeting_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    candidate_type TEXT NOT NULL CHECK (candidate_type IN ('relationship_delta', 'org_delta', 'deliverable_record', 'intro_opportunity', 'general_intelligence')),
    candidate_id TEXT,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    score_breakdown JSON NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('A', 'B', 'C')),
    hard_override JSON,
    deduplication JSON,
    status TEXT NOT NULL CHECK (status IN ('promoted', 'queued_for_review', 'archived', 'blocked', 'duplicate')),
    routing JSON,
    write_results JSON,
    idempotency_key TEXT UNIQUE,
    processing_mode TEXT NOT NULL CHECK (processing_mode IN ('production', 'dry_run', 'test')),
    provenance JSON NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### `relationship_deltas` Table
Captures person/organization relationship changes over time.

```sql
CREATE TABLE IF NOT EXISTS relationship_deltas (
    delta_id TEXT PRIMARY KEY CHECK (delta_id GLOB 'rd_[a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9]'),
    timestamp DATETIME NOT NULL,
    source_meeting_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    person_id TEXT NOT NULL,
    organization_id TEXT,
    delta_type TEXT NOT NULL CHECK (delta_type IN (
        'sentiment_shift', 'engagement_level', 'decision_authority', 'priority_change',
        'urgency_shift', 'trust_level', 'champion_status', 'buying_role',
        'influencer_mapping', 'relationship_depth', 'communication_frequency',
        'responsiveness_change', 'meeting_participation', 'project_involvement'
    )),
    trend TEXT NOT NULL CHECK (trend IN ('increasing', 'decreasing', 'stable', 'fluctuating')),
    previous_state JSON,
    current_state JSON NOT NULL,
    change_magnitude TEXT CHECK (change_magnitude IN ('subtle', 'moderate', 'significant', 'dramatic')),
    evidence JSON NOT NULL,
    impact_assessment JSON,
    mutual_connections JSON,
    next_actions JSON,
    provenance JSON NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### `org_deltas` Table
Tracks organizational changes and strategic shifts.

```sql
CREATE TABLE IF NOT EXISTS org_deltas (
    delta_id TEXT PRIMARY KEY CHECK (delta_id GLOB 'od_[a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9]'),
    timestamp DATETIME NOT NULL,
    source_meeting_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL,
    department_context TEXT,
    delta_type TEXT NOT NULL CHECK (delta_type IN (
        'priority_shift', 'budget_change', 'timeline_update', 'process_change',
        'decision_authority_shift', 'competitive_landscape', 'strategic_initiative',
        'vendor_evaluation_process', 'approval_workflow', 'technology_adoption',
        'compliance_requirement', 'organizational_restructure', 'leadership_change',
        'market_pressure', 'merger_acquisition', 'expansion_plan', 'cost_reduction_initiative'
    )),
    change_description TEXT NOT NULL,
    impact_scope TEXT NOT NULL CHECK (impact_scope IN ('departmental', 'division', 'company_wide', 'ecosystem')),
    previous_state JSON,
    current_state JSON NOT NULL,
    strategic_signals JSON,
    competitive_intelligence JSON,
    buying_process_changes JSON,
    evidence JSON NOT NULL,
    timeline_implications JSON,
    risk_assessment JSON,
    provenance JSON NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### `deliverable_records` Table
Tracks deliverable requests and lifecycle with reuse analysis.

```sql
CREATE TABLE IF NOT EXISTS deliverable_records (
    deliverable_id TEXT PRIMARY KEY CHECK (deliverable_id GLOB 'del_[a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9]'),
    timestamp DATETIME NOT NULL,
    source_meeting_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    client_id TEXT NOT NULL,
    project_context TEXT,
    deliverable_type TEXT NOT NULL CHECK (deliverable_type IN (
        'proposal', 'contract', 'technical_specification', 'design_document',
        'implementation_plan', 'training_materials', 'documentation', 'presentation',
        'report', 'analysis', 'strategy_document', 'roadmap', 'assessment',
        'recommendation', 'prototype', 'demo', 'integration', 'configuration',
        'deployment', 'testing', 'other'
    )),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN (
        'identified', 'scoped', 'assigned', 'in_progress', 'review',
        'delivered', 'accepted', 'rejected', 'cancelled', 'on_hold'
    )),
    commitment_details JSON NOT NULL,
    scope JSON,
    timeline JSON,
    quality_metrics JSON,
    reuse_analysis JSON,
    launcher_prompts JSON,
    evidence JSON NOT NULL,
    financial_context JSON,
    provenance JSON NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### `intro_opportunities` Table
Tracks introduction opportunities with outcome analysis.

```sql
CREATE TABLE IF NOT EXISTS intro_opportunities (
    opportunity_id TEXT PRIMARY KEY CHECK (opportunity_id GLOB 'io_[a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9]'),
    timestamp DATETIME NOT NULL,
    source_meeting_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    introducer_id TEXT NOT NULL,
    introducee_a JSON NOT NULL,
    introducee_b JSON NOT NULL,
    opportunity_type TEXT NOT NULL CHECK (opportunity_type IN (
        'business_development', 'partnership_potential', 'hiring_match', 'vendor_referral',
        'knowledge_sharing', 'mutual_customer', 'industry_networking', 'geographic_connection',
        'skill_complementarity', 'investment_opportunity', 'advisory_connection', 'speaking_opportunity',
        'board_opportunity', 'mentorship_connection', 'customer_referral', 'strategic_alliance'
    )),
    mutual_value JSON NOT NULL,
    connection_analysis JSON NOT NULL,
    risk_assessment JSON NOT NULL,
    recommended_approach JSON NOT NULL,
    evidence JSON NOT NULL,
    outcome_tracking JSON,
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT NOT NULL CHECK (status IN (
        'identified', 'evaluated', 'approved', 'introduction_made', 
        'outcome_pending', 'successful', 'unsuccessful', 'declined'
    )),
    provenance JSON NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Indexes

#### Primary Query Optimization Indexes
```sql
-- Promotion events by meeting and tier for gate queries
CREATE INDEX IF NOT EXISTS idx_promotion_events_meeting_tier ON promotion_events(source_meeting_id, tier);

-- Promotion events by status and timestamp for queue processing
CREATE INDEX IF NOT EXISTS idx_promotion_events_status_timestamp ON promotion_events(status, timestamp);

-- Relationship deltas by person for trend analysis
CREATE INDEX IF NOT EXISTS idx_relationship_deltas_person_timestamp ON relationship_deltas(person_id, timestamp);

-- Relationship deltas by type and trend for pattern queries
CREATE INDEX IF NOT EXISTS idx_relationship_deltas_type_trend ON relationship_deltas(delta_type, trend);

-- Org deltas by organization for intelligence aggregation
CREATE INDEX IF NOT EXISTS idx_org_deltas_org_timestamp ON org_deltas(organization_id, timestamp);

-- Org deltas by type for strategic signal analysis
CREATE INDEX IF NOT EXISTS idx_org_deltas_type_impact ON org_deltas(delta_type, impact_scope);

-- Deliverable records by client for reuse analysis
CREATE INDEX IF NOT EXISTS idx_deliverable_records_client_type ON deliverable_records(client_id, deliverable_type);

-- Deliverable records by status for lifecycle management
CREATE INDEX IF NOT EXISTS idx_deliverable_records_status_timestamp ON deliverable_records(status, timestamp);

-- Intro opportunities by people for connection analysis
CREATE INDEX IF NOT EXISTS idx_intro_opportunities_introducer ON intro_opportunities(introducer_id);

-- Intro opportunities by status for workflow management
CREATE INDEX IF NOT EXISTS idx_intro_opportunities_status_priority ON intro_opportunities(status, priority);
```

#### JSON Field Indexes (SQLite 3.38+)
```sql
-- Index promotion event scores for tier analysis
CREATE INDEX IF NOT EXISTS idx_promotion_events_score ON promotion_events(json_extract(score_breakdown, '$.strategic_importance'));

-- Index relationship confidence for quality filtering
CREATE INDEX IF NOT EXISTS idx_relationship_deltas_confidence ON relationship_deltas(confidence);

-- Index deliverable reuse decisions for similarity analysis
CREATE INDEX IF NOT EXISTS idx_deliverable_reuse_decision ON deliverable_records(json_extract(reuse_analysis, '$.reuse_decision'));
```

### Triggers for Updated Timestamps
```sql
-- Promotion events trigger
CREATE TRIGGER IF NOT EXISTS update_promotion_events_timestamp 
    AFTER UPDATE ON promotion_events
    FOR EACH ROW
BEGIN
    UPDATE promotion_events SET updated_at = CURRENT_TIMESTAMP WHERE event_id = NEW.event_id;
END;

-- Relationship deltas trigger
CREATE TRIGGER IF NOT EXISTS update_relationship_deltas_timestamp 
    AFTER UPDATE ON relationship_deltas
    FOR EACH ROW
BEGIN
    UPDATE relationship_deltas SET updated_at = CURRENT_TIMESTAMP WHERE delta_id = NEW.delta_id;
END;

-- Org deltas trigger
CREATE TRIGGER IF NOT EXISTS update_org_deltas_timestamp 
    AFTER UPDATE ON org_deltas
    FOR EACH ROW
BEGIN
    UPDATE org_deltas SET updated_at = CURRENT_TIMESTAMP WHERE delta_id = NEW.delta_id;
END;

-- Deliverable records trigger
CREATE TRIGGER IF NOT EXISTS update_deliverable_records_timestamp 
    AFTER UPDATE ON deliverable_records
    FOR EACH ROW
BEGIN
    UPDATE deliverable_records SET updated_at = CURRENT_TIMESTAMP WHERE deliverable_id = NEW.deliverable_id;
END;

-- Intro opportunities trigger
CREATE TRIGGER IF NOT EXISTS update_intro_opportunities_timestamp 
    AFTER UPDATE ON intro_opportunities
    FOR EACH ROW
BEGIN
    UPDATE intro_opportunities SET updated_at = CURRENT_TIMESTAMP WHERE opportunity_id = NEW.opportunity_id;
END;
```

## Migration Execution Plan

### Prerequisites
- SQLite version 3.31+ (for JSON support and CHECK constraints)
- Existing `brain.db` with `resources` table
- Foreign key constraints enabled (`PRAGMA foreign_keys = ON;`)

### Migration Script Execution Order

1. **Enable JSON validation and foreign keys**
```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
```

2. **Create tables in dependency order**
```bash
sqlite3 brain.db < relationship_intelligence_schema.sql
```

3. **Verify table creation**
```sql
.tables
.schema promotion_events
```

4. **Create indexes**
```bash
sqlite3 brain.db < relationship_intelligence_indexes.sql
```

5. **Verify schema integrity**
```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

### Rollback Strategy

#### Drop Tables (Destructive - Data Loss)
```sql
-- Drop in reverse dependency order
DROP TABLE IF EXISTS intro_opportunities;
DROP TABLE IF EXISTS deliverable_records;
DROP TABLE IF EXISTS org_deltas;
DROP TABLE IF EXISTS relationship_deltas;
DROP TABLE IF EXISTS promotion_events;
```

#### Drop Indexes Only (Safe)
```sql
-- Drop performance indexes while preserving data
DROP INDEX IF EXISTS idx_promotion_events_meeting_tier;
DROP INDEX IF EXISTS idx_promotion_events_status_timestamp;
-- ... (all other indexes)
```

### Data Retention Policies

#### Archive Old Data
```sql
-- Archive promotion events older than 2 years
DELETE FROM promotion_events 
WHERE timestamp < datetime('now', '-2 years') 
AND status IN ('archived', 'duplicate');

-- Archive completed deliverables older than 1 year
DELETE FROM deliverable_records 
WHERE timestamp < datetime('now', '-1 year') 
AND status IN ('delivered', 'accepted', 'cancelled');
```

#### Vacuum After Cleanup
```sql
VACUUM;
ANALYZE;
```

## Backward Compatibility

### Existing Queries
- All existing queries against `resources`, `memories`, and other tables continue to work
- No schema changes to existing tables
- New tables use foreign keys to maintain referential integrity

### Gradual Adoption
- New intelligence can be stored in new tables immediately
- Existing intelligence remains in current structure
- Migration can proceed table by table as needed

### Integration Points
- `source_meeting_id` in all new tables references `resources.id`
- Promotion gate can write to both new schema and existing memory structures
- Queries can join across old and new schemas for comprehensive analysis

## Query Examples

### Common Analytics Queries

#### Promotion Gate Performance
```sql
SELECT 
    tier,
    status,
    COUNT(*) as count,
    AVG(score) as avg_score,
    AVG(confidence) as avg_confidence
FROM promotion_events 
WHERE timestamp > datetime('now', '-30 days')
GROUP BY tier, status
ORDER BY tier, status;
```

#### Relationship Trend Analysis
```sql
SELECT 
    person_id,
    delta_type,
    trend,
    COUNT(*) as occurrences,
    AVG(confidence) as avg_confidence
FROM relationship_deltas 
WHERE timestamp > datetime('now', '-90 days')
GROUP BY person_id, delta_type, trend
HAVING COUNT(*) > 1
ORDER BY person_id, occurrences DESC;
```

#### Deliverable Reuse Opportunities
```sql
SELECT 
    client_id,
    deliverable_type,
    json_extract(reuse_analysis, '$.reuse_decision') as decision,
    COUNT(*) as count
FROM deliverable_records
WHERE timestamp > datetime('now', '-6 months')
GROUP BY client_id, deliverable_type, json_extract(reuse_analysis, '$.reuse_decision')
ORDER BY count DESC;
```

#### Introduction Success Rates
```sql
SELECT 
    opportunity_type,
    COUNT(*) as total_opportunities,
    SUM(CASE WHEN status = 'successful' THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN status = 'successful' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM intro_opportunities
WHERE status IN ('successful', 'unsuccessful')
GROUP BY opportunity_type
ORDER BY success_rate DESC;
```

## Monitoring and Observability

### Key Metrics to Track
- Table sizes and growth rates
- Query performance on indexes
- Data quality metrics (confidence distributions)
- Schema validation success rates
- Foreign key constraint violations

### Performance Monitoring
```sql
-- Check table sizes
SELECT name, COUNT(*) as row_count 
FROM sqlite_master, (
    SELECT 'promotion_events' as name UNION
    SELECT 'relationship_deltas' UNION
    SELECT 'org_deltas' UNION
    SELECT 'deliverable_records' UNION
    SELECT 'intro_opportunities'
) tables
WHERE type = 'table' AND sqlite_master.name = tables.name;

-- Check index usage
PRAGMA optimize;
ANALYZE;
```

This migration plan provides a robust foundation for the Relationship Intelligence OS while maintaining full backward compatibility with existing systems.