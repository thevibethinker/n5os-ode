-- Database Schema for X Thought Leader Engine
-- Created: 2026-01-08
-- Version: 1.0

-- Table: monitored_accounts
-- Stores X/Twitter accounts we're monitoring for engagement opportunities.
CREATE TABLE monitored_accounts (
    id TEXT PRIMARY KEY,                    -- X user ID (numeric string)
    username TEXT NOT NULL UNIQUE,          -- @handle without @
    display_name TEXT,                      -- Full name
    category TEXT,                          -- e.g., 'hr_tech', 'recruiting', 'future_of_work'
    priority INTEGER DEFAULT 5,             -- 1-10, higher = more important
    last_polled_at TEXT,                    -- ISO timestamp of last poll
    last_tweet_id TEXT,                     -- For pagination (get tweets since this)
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT                              -- Why we're monitoring them
);

-- Table: tweets
-- Raw tweets ingested from monitored accounts.
CREATE TABLE tweets (
    id TEXT PRIMARY KEY,                    -- Tweet ID
    account_id TEXT NOT NULL,               -- FK to monitored_accounts.id
    author_username TEXT NOT NULL,          -- @handle
    content TEXT NOT NULL,                  -- Full tweet text
    created_at TEXT NOT NULL,               -- Tweet timestamp (ISO)
    ingested_at TEXT DEFAULT CURRENT_TIMESTAMP,
    engagement_metrics TEXT,                -- JSON: {likes, retweets, replies, views}
    is_reply INTEGER DEFAULT 0,             -- 1 if this is a reply to someone
    reply_to_id TEXT,                       -- Parent tweet ID if reply
    correlation_score REAL,                 -- Best position match score (0-1)
    correlation_computed_at TEXT,           -- When we computed correlations
    status TEXT DEFAULT 'new',              -- new, correlated, drafted, posted, skipped, expired
    FOREIGN KEY (account_id) REFERENCES monitored_accounts(id)
);

CREATE INDEX idx_tweets_status ON tweets(status);
CREATE INDEX idx_tweets_account ON tweets(account_id);
CREATE INDEX idx_tweets_created ON tweets(created_at);
CREATE INDEX idx_tweets_correlation ON tweets(correlation_score);

-- Table: position_correlations
-- Links tweets to matching positions from positions.db.
CREATE TABLE position_correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT NOT NULL,                 -- FK to tweets.id
    position_id TEXT NOT NULL,              -- Position ID from positions.db
    position_title TEXT NOT NULL,           -- Cached for display
    similarity_score REAL NOT NULL,         -- 0-1 semantic similarity
    computed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tweet_id) REFERENCES tweets(id),
    UNIQUE(tweet_id, position_id)
);

CREATE INDEX idx_corr_tweet ON position_correlations(tweet_id);
CREATE INDEX idx_corr_score ON position_correlations(similarity_score);

-- Table: drafts
-- Generated draft responses (4 variants per tweet).
CREATE TABLE drafts (
    id TEXT PRIMARY KEY,                    -- UUID
    tweet_id TEXT NOT NULL,                 -- FK to tweets.id
    variant TEXT NOT NULL,                  -- supportive, challenging, spicy, comedic
    content TEXT NOT NULL,                  -- Draft text (max 280 chars)
    position_ids TEXT,                      -- JSON array of position IDs used
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    generation_prompt TEXT,                 -- The prompt used (for debugging)
    FOREIGN KEY (tweet_id) REFERENCES tweets(id)
);

CREATE INDEX idx_drafts_tweet ON drafts(tweet_id);
CREATE INDEX idx_drafts_variant ON drafts(variant);

-- Table: approval_queue
-- Pending approvals sent to V via SMS.
CREATE TABLE approval_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT NOT NULL UNIQUE,          -- FK to tweets.id
    sent_at TEXT DEFAULT CURRENT_TIMESTAMP, -- When SMS was sent
    expires_at TEXT NOT NULL,               -- EOD in ET
    sms_message_id TEXT,                    -- For tracking
    response_received INTEGER DEFAULT 0,    -- 1 when V responds
    response_text TEXT,                     -- Raw response from V
    response_at TEXT,                       -- When response received
    selected_variant TEXT,                  -- supportive/challenging/spicy/comedic/skip
    refinement_suggestion TEXT,             -- If V sent keyword + suggestion
    FOREIGN KEY (tweet_id) REFERENCES tweets(id)
);

CREATE INDEX idx_queue_expires ON approval_queue(expires_at);
CREATE INDEX idx_queue_pending ON approval_queue(response_received);

-- Table: posted_tweets
-- Tweets we've posted (for anti-repetition and voice learning).
CREATE TABLE posted_tweets (
    id TEXT PRIMARY KEY,                    -- Our posted tweet ID
    original_tweet_id TEXT NOT NULL,        -- The tweet we replied to
    original_author TEXT NOT NULL,          -- Who we replied to
    original_content TEXT NOT NULL,         -- What they said
    our_content TEXT NOT NULL,              -- What we posted
    variant_used TEXT NOT NULL,             -- Which voice variant
    position_ids TEXT,                      -- JSON array of positions referenced
    posted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    engagement_metrics TEXT,                -- JSON: {likes, retweets, replies} (updated later)
    FOREIGN KEY (original_tweet_id) REFERENCES tweets(id)
);

CREATE INDEX idx_posted_at ON posted_tweets(posted_at);
CREATE INDEX idx_posted_variant ON posted_tweets(variant_used);

-- Table: voice_samples
-- V's historical tweets for voice learning.
CREATE TABLE voice_samples (
    id TEXT PRIMARY KEY,                    -- Tweet ID from archive
    content TEXT NOT NULL,                  -- Tweet text
    created_at TEXT,                        -- Original tweet timestamp
    engagement_metrics TEXT,                -- JSON if available
    ingested_at TEXT DEFAULT CURRENT_TIMESTAMP,
    source TEXT DEFAULT 'archive',          -- archive, manual, posted
    embedding BLOB,                         -- For similarity search
    tags TEXT                               -- JSON array of manual tags
);

CREATE INDEX idx_samples_created ON voice_samples(created_at);

-- Table: variant_preferences
-- Track which variants V selects over time for voice learning.
CREATE TABLE variant_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    selected_variant TEXT NOT NULL,         -- What V chose
    all_variants_shown TEXT NOT NULL,       -- JSON array of all 4 shown
    context_category TEXT,                  -- What category was the original tweet
    selected_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pref_variant ON variant_preferences(selected_variant);

