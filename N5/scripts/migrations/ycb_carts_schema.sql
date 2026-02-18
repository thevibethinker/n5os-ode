-- YCB Content Carts Schema Migration
-- Creates tables for Content Carts - collections of entries for synthesis workflows
-- Part of: ycb-content-layer build (D1.2)

-- Content Carts table - containers for collections of content items
CREATE TABLE IF NOT EXISTS content_carts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'deleted')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Cart Items table - links between carts and content items
CREATE TABLE IF NOT EXISTS cart_items (
    id TEXT PRIMARY KEY,
    cart_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    added_at TEXT NOT NULL DEFAULT (datetime('now')),
    notes TEXT,  -- Optional notes about why this item is in the cart
    order_index INTEGER DEFAULT 0,  -- For manual ordering
    FOREIGN KEY (cart_id) REFERENCES content_carts(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id),
    UNIQUE(cart_id, item_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_item ON cart_items(item_id);
CREATE INDEX IF NOT EXISTS idx_content_carts_status ON content_carts(status);
CREATE INDEX IF NOT EXISTS idx_content_carts_updated ON content_carts(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_cart_items_order ON cart_items(cart_id, order_index);

-- Update trigger for content_carts.updated_at
CREATE TRIGGER IF NOT EXISTS trigger_content_carts_updated 
    AFTER UPDATE ON content_carts
BEGIN
    UPDATE content_carts SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Migration metadata
CREATE TABLE IF NOT EXISTS ycb_migration_log (
    migration_name TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    version TEXT NOT NULL
);

INSERT OR REPLACE INTO ycb_migration_log (migration_name, version) 
VALUES ('ycb_carts_schema', '1.0.0');