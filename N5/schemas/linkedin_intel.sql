-- LinkedIn Intelligence System Schema
-- Stores LinkedIn conversations, messages, and extracted commitments from Kondo webhooks
-- Version: 1.0.0
-- Created: 2025-10-30

-- Conversations: LinkedIn conversation threads
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,                    -- Kondo conversation_id
    linkedin_profile_url TEXT,              -- Participant's LinkedIn profile
    participant_name TEXT,
    participant_email TEXT,                 -- If available from Kondo
    first_message_at INTEGER NOT NULL,      -- Unix timestamp (milliseconds)
    last_message_at INTEGER NOT NULL,       -- Unix timestamp (milliseconds)
    last_message_from TEXT NOT NULL,        -- 'me' or 'them'
    message_count INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE, PENDING_RESPONSE, ARCHIVED
    response_time_threshold INTEGER DEFAULT 172800000,  -- 48 hours in milliseconds
    crm_profile_slug TEXT,                  -- Link to CRM: individuals/{slug}.md
    metadata TEXT,                          -- JSON for additional Kondo data
    created_at INTEGER DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER DEFAULT (strftime('%s', 'now') * 1000),
    
    CHECK (status IN ('ACTIVE', 'PENDING_RESPONSE', 'ARCHIVED', 'SNOOZED')),
    CHECK (last_message_from IN ('me', 'them'))
);

CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_crm ON conversations(crm_profile_slug);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at);
CREATE INDEX IF NOT EXISTS idx_conversations_pending ON conversations(status, last_message_from) 
    WHERE status = 'PENDING_RESPONSE' AND last_message_from = 'them';

-- Messages: Individual messages within conversations
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    message_id TEXT,                        -- Kondo's message ID (if provided)
    sender TEXT NOT NULL,                   -- 'me' or participant name
    sender_profile_url TEXT,                -- LinkedIn profile of sender
    content TEXT NOT NULL,
    sent_at INTEGER NOT NULL,               -- Unix timestamp (milliseconds)
    commitment_extraction_needed BOOLEAN DEFAULT 1,
    commitment_extracted_at INTEGER,
    extraction_error TEXT,                  -- Error message if extraction failed
    metadata TEXT,                          -- JSON for additional message data
    created_at INTEGER DEFAULT (strftime('%s', 'now') * 1000),
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_extraction_needed ON messages(commitment_extraction_needed)
    WHERE commitment_extraction_needed = 1;
CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);

-- Commitments: Extracted promises and commitments from messages
CREATE TABLE IF NOT EXISTS commitments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    message_id INTEGER NOT NULL,
    commitment_type TEXT NOT NULL,          -- I_OWE_THEM, THEY_OWE_ME, MUTUAL
    what TEXT NOT NULL,                     -- Description of commitment
    deadline TEXT,                          -- ISO format deadline (if mentioned)
    deadline_timestamp INTEGER,             -- Unix timestamp for sorting
    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, FULFILLED, OVERDUE, CANCELLED
    confidence REAL DEFAULT 1.0,            -- LLM confidence score (0.0-1.0)
    notes TEXT,                             -- Additional context
    fulfilled_at INTEGER,                   -- When marked as fulfilled
    created_at INTEGER DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER DEFAULT (strftime('%s', 'now') * 1000),
    
    CHECK (commitment_type IN ('I_OWE_THEM', 'THEY_OWE_ME', 'MUTUAL', 'INFO_ONLY')),
    CHECK (status IN ('PENDING', 'FULFILLED', 'OVERDUE', 'CANCELLED')),
    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_commitments_status ON commitments(status);
CREATE INDEX IF NOT EXISTS idx_commitments_type ON commitments(commitment_type);
CREATE INDEX IF NOT EXISTS idx_commitments_deadline ON commitments(deadline_timestamp);
CREATE INDEX IF NOT EXISTS idx_commitments_conversation ON commitments(conversation_id);
CREATE INDEX IF NOT EXISTS idx_commitments_pending ON commitments(status, commitment_type)
    WHERE status = 'PENDING';

-- Processing Log: Track webhook receipts and processing status
CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,               -- WEBHOOK_RECEIVED, EXTRACTION_RUN, ENRICHMENT_RUN
    event_data TEXT,                        -- JSON with event details
    status TEXT NOT NULL,                   -- SUCCESS, ERROR, PARTIAL
    error_message TEXT,
    duration_ms INTEGER,
    created_at INTEGER DEFAULT (strftime('%s', 'now') * 1000)
);

CREATE INDEX IF NOT EXISTS idx_processing_log_type ON processing_log(event_type);
CREATE INDEX IF NOT EXISTS idx_processing_log_status ON processing_log(status);
CREATE INDEX IF NOT EXISTS idx_processing_log_created ON processing_log(created_at);

-- Views for common queries

-- Pending responses: Conversations where they messaged last and it's been >48hrs
CREATE VIEW IF NOT EXISTS pending_responses AS
SELECT 
    c.id,
    c.participant_name,
    c.linkedin_profile_url,
    c.crm_profile_slug,
    c.last_message_at,
    ((strftime('%s', 'now') * 1000) - c.last_message_at) AS elapsed_ms,
    ((strftime('%s', 'now') * 1000) - c.last_message_at) / 3600000.0 AS elapsed_hours,
    m.content AS last_message_content,
    m.sent_at AS last_message_timestamp
FROM conversations c
LEFT JOIN messages m ON m.id = (
    SELECT id FROM messages 
    WHERE conversation_id = c.id 
    ORDER BY sent_at DESC 
    LIMIT 1
)
WHERE c.status = 'PENDING_RESPONSE'
    AND c.last_message_from = 'them'
    AND ((strftime('%s', 'now') * 1000) - c.last_message_at) > c.response_time_threshold
ORDER BY c.last_message_at ASC;

-- My pending commitments: What I owe people
CREATE VIEW IF NOT EXISTS my_commitments AS
SELECT
    cm.id,
    cm.what,
    cm.deadline,
    cm.status,
    cm.confidence,
    c.participant_name,
    c.linkedin_profile_url,
    c.crm_profile_slug,
    m.content AS message_context,
    m.sent_at AS message_timestamp,
    cm.created_at
FROM commitments cm
JOIN conversations c ON cm.conversation_id = c.id
JOIN messages m ON cm.message_id = m.id
WHERE cm.commitment_type = 'I_OWE_THEM'
    AND cm.status IN ('PENDING', 'OVERDUE')
ORDER BY 
    CASE WHEN cm.deadline_timestamp IS NOT NULL THEN 0 ELSE 1 END,
    cm.deadline_timestamp ASC,
    cm.created_at DESC;

-- Their pending commitments: What they owe me
CREATE VIEW IF NOT EXISTS their_commitments AS
SELECT
    cm.id,
    cm.what,
    cm.deadline,
    cm.status,
    cm.confidence,
    c.participant_name,
    c.linkedin_profile_url,
    c.crm_profile_slug,
    m.content AS message_context,
    m.sent_at AS message_timestamp,
    cm.created_at
FROM commitments cm
JOIN conversations c ON cm.conversation_id = c.id
JOIN messages m ON cm.message_id = m.id
WHERE cm.commitment_type = 'THEY_OWE_ME'
    AND cm.status IN ('PENDING', 'OVERDUE')
ORDER BY 
    CASE WHEN cm.deadline_timestamp IS NOT NULL THEN 0 ELSE 1 END,
    cm.deadline_timestamp ASC,
    cm.created_at DESC;
