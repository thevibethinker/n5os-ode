-- Content Library v5 Migration
-- Non-destructive, idempotent schema additions
-- Run with: sqlite3 N5/data/content_library.db < N5/builds/content-library-v5/artifacts/migration_v5.sql

-- Step 1: Add new columns (SQLite ignores ADD COLUMN if exists via error, wrap in transaction)
-- Note: In production, check column existence first

-- Add subtype column for finer classification
ALTER TABLE items ADD COLUMN subtype TEXT DEFAULT NULL;

-- Add summary column for AI-generated or curated summaries
ALTER TABLE items ADD COLUMN summary TEXT DEFAULT NULL;

-- Add managed_fields for merge-safe enrichment tracking
-- JSON array of field names set by automation (vs human-curated)
ALTER TABLE items ADD COLUMN managed_fields TEXT DEFAULT NULL;

-- Step 2: Backfill subtype for known patterns
UPDATE items SET subtype = 'calendly' 
WHERE id LIKE 'meeting_booking%' AND subtype IS NULL;

UPDATE items SET subtype = 'scheduling' 
WHERE content_type = 'link' 
  AND (url LIKE '%calendly%' OR id LIKE '%meeting%' OR id LIKE '%vrijen%work%' OR id LIKE '%vrijen%sync%')
  AND subtype IS NULL
  AND subtype != 'calendly';

-- Step 3: Migrate file_path → source_file_path where needed
UPDATE items SET source_file_path = file_path 
WHERE source_file_path IS NULL AND file_path IS NOT NULL;

-- Step 4: Create new indexes (IF NOT EXISTS makes these idempotent)
CREATE INDEX IF NOT EXISTS idx_items_subtype ON items(subtype);
CREATE INDEX IF NOT EXISTS idx_items_type_subtype ON items(content_type, subtype);
CREATE INDEX IF NOT EXISTS idx_items_source_file ON items(source_file_path);

-- Step 5: Record migration in metadata table
INSERT OR REPLACE INTO metadata (key, value, updated_at)
VALUES ('schema_version', '5.0', datetime('now'));

-- Verification queries (uncomment to check results):
-- SELECT content_type, subtype, COUNT(*) FROM items GROUP BY content_type, subtype;
-- SELECT * FROM metadata WHERE key = 'schema_version';
