-- YCB-style Entry/Comment Threading Schema Migration
-- Creates tables for thread management and comment hierarchies

BEGIN TRANSACTION;

-- Thread headers that group entries
CREATE TABLE content_threads (
    id TEXT PRIMARY KEY,
    root_item_id TEXT NOT NULL,  -- The original entry that started the thread
    title TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (root_item_id) REFERENCES items(id)
);

-- Individual comments/syntheses (the YCB model)
CREATE TABLE thread_comments (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    parent_comment_id TEXT,  -- NULL for top-level comments on root
    item_id TEXT,  -- If comment is itself a content item
    content TEXT NOT NULL,
    comment_type TEXT DEFAULT 'note',  -- 'note', 'synthesis', 'quote', 'link'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (thread_id) REFERENCES content_threads(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES thread_comments(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE INDEX idx_thread_comments_thread ON thread_comments(thread_id);
CREATE INDEX idx_thread_comments_parent ON thread_comments(parent_comment_id);

-- Explicit connections between entries
CREATE TABLE entry_links (
    id TEXT PRIMARY KEY,
    source_item_id TEXT NOT NULL,
    target_item_id TEXT NOT NULL,
    link_type TEXT DEFAULT 'related',  -- 'related', 'derived', 'contradicts', 'supports'
    strength REAL DEFAULT 0.5,  -- 0.0 to 1.0
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_item_id) REFERENCES items(id),
    FOREIGN KEY (target_item_id) REFERENCES items(id),
    UNIQUE(source_item_id, target_item_id, link_type)
);

CREATE INDEX idx_entry_links_source ON entry_links(source_item_id);
CREATE INDEX idx_entry_links_target ON entry_links(target_item_id);

-- Update schema metadata
INSERT OR REPLACE INTO metadata (key, value) VALUES ('ycb_threading_schema_version', '1.0');

COMMIT;