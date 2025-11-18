-- Content Library Schema
-- Stores links and text snippets for reuse in emails, documents, and other communications
-- Replaces: N5/prefs/communication/content-library.json (deprecated)

CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('link', 'snippet')),
    title TEXT NOT NULL,
    content TEXT,  -- For snippets: the text content. For links: same as url
    url TEXT,      -- For links only
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    deprecated INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    last_used_at TEXT,
    notes TEXT,
    source TEXT  -- Where this item came from (e.g., 'migration', 'manual', 'quick-add')
);

CREATE TABLE IF NOT EXISTS tags (
    item_id TEXT NOT NULL,
    tag_key TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, tag_key, tag_value)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_items_type ON items(type);
CREATE INDEX IF NOT EXISTS idx_items_deprecated ON items(deprecated);
CREATE INDEX IF NOT EXISTS idx_items_title ON items(title COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_tags_key_value ON tags(tag_key, tag_value);
CREATE INDEX IF NOT EXISTS idx_items_updated ON items(updated_at DESC);

-- Metadata table
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR REPLACE INTO metadata (key, value) VALUES 
    ('schema_version', '1.0.0'),
    ('description', 'Content Library - Links and snippets for Vrijen & Careerspan'),
    ('migrated_from', 'content-library.json'),
    ('migration_date', datetime('now'));

