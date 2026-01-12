-- Voice Library Schema V2
-- Expands shell schema with distinctiveness, domain tags, and throttle tracking
-- Per PLAN.md v2.0 Phase 1

PRAGMA foreign_keys = ON;

-- Drop old tables if migrating (comment out for fresh install)
-- DROP TABLE IF EXISTS sources;
-- DROP TABLE IF EXISTS primitives;

CREATE TABLE IF NOT EXISTS primitives (
  id TEXT PRIMARY KEY,                          -- e.g., vp-000123
  exact_text TEXT NOT NULL,                     -- The actual phrase/analogy/metaphor
  primitive_type TEXT NOT NULL,                 -- phrase | analogy | metaphor | pivot | example
  
  -- V2 additions: Distinctiveness
  distinctiveness_score REAL DEFAULT NULL,      -- 0.0-1.0 from Pangram (1.0 - fraction_ai)
  novelty_flagged INTEGER DEFAULT 0,            -- 1 if explicit capture signal ("I'm stealing that")
  
  -- V2 additions: Domain tags (replaces concepts table)
  domains_json TEXT DEFAULT '[]',               -- JSON array: ["career", "incentives", "ethics"]
  
  -- V2 additions: Throttle tracking
  use_count INTEGER DEFAULT 0,                  -- How many times used in generation
  last_used_at TEXT DEFAULT NULL,               -- ISO timestamp of last use
  
  -- Metadata
  status TEXT DEFAULT 'candidate',              -- candidate | approved | rejected | archived
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  notes TEXT DEFAULT NULL                       -- Human review notes
);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  primitive_id TEXT NOT NULL,
  source_path TEXT NOT NULL,                    -- Path to transcript/document
  source_type TEXT DEFAULT 'transcript',        -- transcript | document | manual | block
  block_type TEXT DEFAULT NULL,                 -- B35, B21, etc. if from meeting block
  speaker TEXT DEFAULT NULL,                    -- Who said it (V, other, unknown)
  timestamp_approx TEXT DEFAULT NULL,           -- Approximate timestamp in source
  capture_signal TEXT DEFAULT NULL,             -- e.g., "I'm stealing that" if present
  extracted_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (primitive_id) REFERENCES primitives(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_primitives_type ON primitives(primitive_type);
CREATE INDEX IF NOT EXISTS idx_primitives_status ON primitives(status);
CREATE INDEX IF NOT EXISTS idx_primitives_distinctiveness ON primitives(distinctiveness_score);
CREATE INDEX IF NOT EXISTS idx_primitives_domains ON primitives(domains_json);
CREATE INDEX IF NOT EXISTS idx_sources_primitive ON sources(primitive_id);
CREATE INDEX IF NOT EXISTS idx_sources_path ON sources(source_path);

-- Trigger to update updated_at on modification
CREATE TRIGGER IF NOT EXISTS update_primitives_timestamp 
AFTER UPDATE ON primitives
BEGIN
  UPDATE primitives SET updated_at = datetime('now') WHERE id = NEW.id;
END;

