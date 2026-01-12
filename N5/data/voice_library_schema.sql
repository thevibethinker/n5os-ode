-- Voice Library (Voice Primitives) schema
-- Shell only (Phase 1). Seeding deferred.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS primitives (
  id TEXT PRIMARY KEY,                 -- e.g., vp-000123_talent-as-optionality-frame
  primitive_type TEXT NOT NULL,        -- phrase|pivot|analogy|metaphor|comparison|disclaimer|framing_move
  exact_text TEXT NOT NULL,
  function TEXT,
  when_to_use TEXT,
  when_not_to_use TEXT,
  tags_json TEXT,                      -- JSON array of strings
  status TEXT NOT NULL DEFAULT 'candidate',   -- candidate|approved|deprecated
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  primitive_id TEXT NOT NULL,
  source_path TEXT NOT NULL,           -- workspace-relative path to transcript
  speaker TEXT,
  time_hint TEXT,                      -- freeform timestamp hint
  capture_signal TEXT,                 -- e.g., "I'm stealing that"
  context_before TEXT,
  context_after TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (primitive_id) REFERENCES primitives(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_primitives_type ON primitives(primitive_type);
CREATE INDEX IF NOT EXISTS idx_primitives_status ON primitives(status);
CREATE INDEX IF NOT EXISTS idx_sources_primitive ON sources(primitive_id);

