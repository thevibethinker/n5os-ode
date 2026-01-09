---
created: 2026-01-09
worker_id: W1
component: Database Schema
status: pending
depends_on: []
---

# W1: Database Schema

## Objective
Create the SQLite database schema for the X Thought Leadership Engine.

## Output Files
- `Projects/x-thought-leader/db/tweets.db`
- `Projects/x-thought-leader/db/schema.sql`

## Schema Design

```sql
-- Accounts we monitor for engagement opportunities
CREATE TABLE monitored_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,      -- X user ID
    username TEXT NOT NULL,            -- @handle
    display_name TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    active INTEGER DEFAULT 1,
    last_checked TEXT,
    last_tweet_id TEXT,                -- High watermark for polling
    notes TEXT
);

-- Tweets we've ingested from monitored accounts
CREATE TABLE tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT UNIQUE NOT NULL,
    author_user_id TEXT NOT NULL,
    author_username TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT,
    ingested_at TEXT DEFAULT CURRENT_TIMESTAMP,
    retweet_count INTEGER,
    like_count INTEGER,
    reply_count INTEGER,
    -- Correlation results
    processed INTEGER DEFAULT 0,
    top_position_id TEXT,
    correlation_score REAL,
    correlation_details TEXT,          -- JSON
    -- Status
    status TEXT DEFAULT 'new',         -- new|processed|drafts_sent|responded|skipped
    FOREIGN KEY (author_user_id) REFERENCES monitored_accounts(user_id)
);

-- Position correlation scores for each tweet
CREATE TABLE position_correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT NOT NULL,
    position_id TEXT NOT NULL,
    similarity_score REAL NOT NULL,
    matched_components TEXT,           -- JSON: which parts matched
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id)
);

-- Generated draft responses
CREATE TABLE drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT NOT NULL,
    draft_set_id TEXT NOT NULL,        -- Groups 4 variants together
    variant TEXT NOT NULL,             -- supportive|challenging|spicy|comedic
    text TEXT NOT NULL,
    position_id TEXT,                  -- Which position inspired this
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    -- Approval flow
    status TEXT DEFAULT 'pending',     -- pending|approved|posted|skipped|expired|refined
    approved_at TEXT,
    posted_at TEXT,
    expires_at TEXT,                   -- EOD expiry
    -- Refinement tracking
    refinement_of INTEGER,             -- Parent draft ID if this is a refinement
    refinement_suggestion TEXT,
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id)
);

-- Tweets we've posted (our replies)
CREATE TABLE our_tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    our_tweet_id TEXT UNIQUE,          -- X tweet ID of our reply
    draft_id INTEGER NOT NULL,
    in_reply_to_tweet_id TEXT NOT NULL,
    in_reply_to_user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    variant TEXT NOT NULL,
    position_id TEXT,
    posted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    -- Engagement tracking (updated by learner)
    like_count INTEGER DEFAULT 0,
    retweet_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    engagement_checked_at TEXT,
    FOREIGN KEY (draft_id) REFERENCES drafts(id)
);

-- V's historical tweets (from archive) for voice learning
CREATE TABLE historical_tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT UNIQUE NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT,
    is_reply INTEGER DEFAULT 0,
    reply_to_tweet_id TEXT,
    retweet_count INTEGER,
    favorite_count INTEGER,
    -- Voice analysis
    analyzed INTEGER DEFAULT 0,
    voice_features TEXT                -- JSON
);

-- Indexes for performance
CREATE INDEX idx_tweets_author ON tweets(author_user_id);
CREATE INDEX idx_tweets_status ON tweets(status);
CREATE INDEX idx_drafts_status ON drafts(status);
CREATE INDEX idx_drafts_set ON drafts(draft_set_id);
CREATE INDEX idx_correlations_tweet ON position_correlations(tweet_id);
CREATE INDEX idx_our_tweets_date ON our_tweets(posted_at);
```

## Seed Data

Initial monitored account:
```sql
INSERT INTO monitored_accounts (user_id, username, display_name, notes)
VALUES ('14aborman', 'asanwal', 'Anand Sanwal', 'CB Insights founder - HR tech, AI, business intelligence');
```

(Get actual user_id from X API during setup)

## Acceptance Criteria
- [ ] All tables created with proper constraints
- [ ] Indexes in place for query performance
- [ ] Schema documented in schema.sql
- [ ] Database file created at correct path
- [ ] Seed data for @asanwal inserted
