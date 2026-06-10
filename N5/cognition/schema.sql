-- N5 Semantic Memory Schema
-- SQLite database schema for vector storage and search

CREATE TABLE IF NOT EXISTS resources (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    hash TEXT,
    last_indexed_at DATETIME,
    content_date DATETIME  -- Authoritative date from frontmatter (last_edited or created)
);

CREATE TABLE IF NOT EXISTS blocks (
    id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    block_type TEXT,
    content TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    token_count INTEGER,
    content_date DATETIME,  -- Denormalized from resource for fast search
    FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vectors (
    block_id TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,
    FOREIGN KEY(block_id) REFERENCES blocks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    resource_id TEXT, 
    tag TEXT, 
    PRIMARY KEY (resource_id, tag), 
    FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

-- Voice Library V2 Schema
-- Stores distinctive language primitives and their source provenance.

CREATE TABLE IF NOT EXISTS primitives (
    id TEXT PRIMARY KEY,
    exact_text TEXT NOT NULL,
    primitive_type TEXT NOT NULL,
    distinctiveness_score REAL DEFAULT 0.0,
    novelty_flagged INTEGER DEFAULT 0,
    domains_json TEXT DEFAULT '[]',
    use_count INTEGER DEFAULT 0,
    last_used_at TEXT,
    status TEXT DEFAULT 'client',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    primitive_id TEXT NOT NULL,
    source_path TEXT,
    source_type TEXT,
    block_type TEXT,
    speaker TEXT,
    capture_signal TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (primitive_id) REFERENCES primitives(id) ON DELETE CASCADE
);

CREATE TRIGGER IF NOT EXISTS update_primitives_timestamp
    AFTER UPDATE ON primitives
    FOR EACH ROW
    BEGIN
        UPDATE primitives SET updated_at = datetime('now') WHERE id = OLD.id;
    END;

-- Useful indexes for common queries
CREATE INDEX IF NOT EXISTS idx_resources_path ON resources(path);
CREATE INDEX IF NOT EXISTS idx_blocks_resource ON blocks(resource_id);
CREATE INDEX IF NOT EXISTS idx_blocks_date ON blocks(content_date);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_primitives_type ON primitives(primitive_type);
CREATE INDEX IF NOT EXISTS idx_primitives_status ON primitives(status);
CREATE INDEX IF NOT EXISTS idx_sources_primitive ON sources(primitive_id);
