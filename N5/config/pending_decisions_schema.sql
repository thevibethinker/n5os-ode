-- Schema for Pending Decisions Store
-- Created by D3.1 Drop for zoputer-autonomy-v2

CREATE TABLE IF NOT EXISTS pending_decisions (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'resolved', 'expired', 'cancelled')),
    
    -- Origin info
    origin TEXT NOT NULL CHECK (origin IN ('va', 'zoputer')),
    origin_conversation TEXT,
    
    -- Decision content
    summary TEXT NOT NULL CHECK (length(summary) <= 160),  -- SMS-friendly
    full_context TEXT NOT NULL,  -- JSON blob with all details
    options TEXT,                -- JSON array of options if applicable
    
    -- Resolution
    resolved_at TEXT,
    resolved_by TEXT,            -- conversation ID that resolved it
    resolution TEXT,             -- The decision made
    resolution_notes TEXT
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_decisions(status);
CREATE INDEX IF NOT EXISTS idx_pending_priority ON pending_decisions(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_pending_origin ON pending_decisions(origin, status);
CREATE INDEX IF NOT EXISTS idx_pending_expires ON pending_decisions(expires_at) WHERE status = 'pending';