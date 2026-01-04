-- Context Graph Schema v1.0
-- Created: 2026-01-04
-- Purpose: Edge-based graph for decision tracing and cognitive mirror

-- Entity Registry: Canonical IDs for all referenceable entities
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,           -- 'person', 'idea', 'decision', 'meeting', 'position'
    entity_id TEXT NOT NULL,             -- Slug: 'vrijen', 'context-graph-adoption', 'mtg_2026-01-04'
    name TEXT,                           -- Human-readable: "Vrijen Attawar", "Context Graph System"
    created_at TEXT DEFAULT (datetime('now')),
    metadata TEXT,                       -- JSON blob for type-specific data
    UNIQUE(entity_type, entity_id)
);

-- Core Edges Table
CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source node
    source_type TEXT NOT NULL,           -- 'person', 'idea', 'decision', 'position'
    source_id TEXT NOT NULL,             -- Entity slug
    
    -- Relation
    relation TEXT NOT NULL,              -- 'originated_by', 'supported_by', etc.
    
    -- Target node
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    
    -- Provenance
    context_meeting_id TEXT,             -- Meeting where this edge was captured (nullable for manual)
    evidence TEXT,                       -- Quote or description supporting this edge
    captured_at TEXT DEFAULT (datetime('now')),
    
    -- Lifecycle
    status TEXT DEFAULT 'active',        -- 'active', 'superseded', 'reversed', 'decayed'
    superseded_by INTEGER,               -- FK to replacement edge (if superseded)
    reversed_at TEXT,                    -- Timestamp if reversed
    reversal_reason TEXT,                -- Why it was reversed
    
    -- Outcome tracking (for hoped_for, concerned_about)
    outcome_status TEXT,                 -- 'validated', 'invalidated', 'pending', NULL
    outcome_edge_id INTEGER,             -- FK to edge that validated/invalidated
    outcome_note TEXT,                   -- Freeform note on outcome
    
    -- Audit
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (superseded_by) REFERENCES edges(id),
    FOREIGN KEY (outcome_edge_id) REFERENCES edges(id)
);

-- Edge Types Reference (canonical vocabulary)
CREATE TABLE IF NOT EXISTS edge_types (
    relation TEXT PRIMARY KEY,
    category TEXT NOT NULL,              -- 'provenance', 'stance', 'expectation', 'chain'
    description TEXT NOT NULL,
    inverse_relation TEXT,               -- For bidirectional queries
    created_at TEXT DEFAULT (datetime('now'))
);

-- Seed canonical edge types
INSERT OR IGNORE INTO edge_types (relation, category, description, inverse_relation) VALUES
    -- Provenance (who/where did this come from)
    ('originated_by', 'provenance', 'Who first surfaced this idea/decision', 'originated'),
    ('influenced_by', 'provenance', 'Shaped my thinking without being the origin', 'influenced'),
    
    -- Stance (positions on ideas)
    ('supported_by', 'stance', 'Endorsed or validated', 'supports'),
    ('challenged_by', 'stance', 'Pushed back or questioned', 'challenges'),
    
    -- Expectation (forward-looking)
    ('hoped_for', 'expectation', 'Expected positive outcome', NULL),
    ('concerned_about', 'expectation', 'Worried about negative outcome', NULL),
    
    -- Chain (logical dependencies)
    ('preceded_by', 'chain', 'Earlier version or precursor', 'preceded'),
    ('depends_on', 'chain', 'Logical prerequisite', 'enables'),
    ('supersedes', 'chain', 'Replaces earlier decision', 'superseded_by');

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_edges_relation ON edges(relation);
CREATE INDEX IF NOT EXISTS idx_edges_meeting ON edges(context_meeting_id);
CREATE INDEX IF NOT EXISTS idx_edges_status ON edges(status);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);

-- View: Active edges only (most common query pattern)
CREATE VIEW IF NOT EXISTS active_edges AS
SELECT * FROM edges WHERE status = 'active';

-- View: Edges with entity names resolved
CREATE VIEW IF NOT EXISTS edges_resolved AS
SELECT 
    e.id,
    e.source_type,
    e.source_id,
    src.name as source_name,
    e.relation,
    e.target_type,
    e.target_id,
    tgt.name as target_name,
    e.context_meeting_id,
    e.evidence,
    e.status,
    e.outcome_status,
    e.created_at
FROM edges e
LEFT JOIN entities src ON e.source_type = src.entity_type AND e.source_id = src.entity_id
LEFT JOIN entities tgt ON e.target_type = tgt.entity_type AND e.target_id = tgt.entity_id;

