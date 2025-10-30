-- GTM Intelligence Database Schema
-- Purpose: Structured, queryable market intelligence from stakeholder meetings
-- Source: B31_STAKEHOLDER_RESEARCH.md files (immutable after creation)

CREATE TABLE IF NOT EXISTS gtm_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Meeting Context
    meeting_id TEXT NOT NULL,
    meeting_date TEXT NOT NULL,
    source_b31_path TEXT NOT NULL,
    
    -- Stakeholder Information
    stakeholder_name TEXT NOT NULL,
    stakeholder_role TEXT,
    stakeholder_type TEXT,  -- e.g., 'recruiter', 'founder', 'big_company', 'consultant'
    stakeholder_company TEXT,
    
    -- Insight Classification
    category TEXT NOT NULL,  -- e.g., 'Market Pain Point', 'GTM Strategy', 'Product Strategy'
    signal_strength INTEGER CHECK(signal_strength >= 1 AND signal_strength <= 5),
    
    -- Insight Content (FULL TEXT EXTRACTED)
    title TEXT NOT NULL,
    insight TEXT NOT NULL,  -- Full insight description
    why_it_matters TEXT,    -- Context/implications
    quote TEXT,             -- Supporting quote from transcript
    
    -- Metadata
    confidence_level TEXT,  -- 'HIGH', 'MEDIUM', 'LOW'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_by TEXT DEFAULT 'aggregate_b31_insights_v2.py',
    
    -- Indexing
    UNIQUE(meeting_id, stakeholder_name, title)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_stakeholder_type ON gtm_insights(stakeholder_type);
CREATE INDEX IF NOT EXISTS idx_category ON gtm_insights(category);
CREATE INDEX IF NOT EXISTS idx_signal_strength ON gtm_insights(signal_strength);
CREATE INDEX IF NOT EXISTS idx_meeting_date ON gtm_insights(meeting_date);
CREATE INDEX IF NOT EXISTS idx_stakeholder_name ON gtm_insights(stakeholder_name);

-- Full-text search index
CREATE VIRTUAL TABLE IF NOT EXISTS gtm_insights_fts USING fts5(
    title, 
    insight, 
    why_it_matters, 
    quote,
    content='gtm_insights',
    content_rowid='id'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS gtm_insights_ai AFTER INSERT ON gtm_insights BEGIN
    INSERT INTO gtm_insights_fts(rowid, title, insight, why_it_matters, quote)
    VALUES (new.id, new.title, new.insight, new.why_it_matters, new.quote);
END;

CREATE TRIGGER IF NOT EXISTS gtm_insights_ad AFTER DELETE ON gtm_insights BEGIN
    DELETE FROM gtm_insights_fts WHERE rowid = old.id;
END;

-- Processing registry (track which meetings have been extracted)
CREATE TABLE IF NOT EXISTS gtm_processing_registry (
    meeting_id TEXT PRIMARY KEY,
    b31_path TEXT NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insights_extracted INTEGER DEFAULT 0,
    extraction_version TEXT DEFAULT '2.0'
);
