-- Migration: Team Status Career Progression
-- Date: 2025-10-30
-- Worker: W1 (Schema)
-- Description: Adds tables for tracking team status hierarchy, transitions, coaching emails, and career statistics
-- Version: 1.0.0

-- =============================================================================
-- SAFETY: Drop existing tables if re-running (idempotent migration)
-- =============================================================================
DROP TABLE IF EXISTS team_status_history;
DROP TABLE IF EXISTS status_transitions;
DROP TABLE IF EXISTS coaching_emails;
DROP TABLE IF EXISTS career_stats;

-- =============================================================================
-- TABLE 1: team_status_history
-- Purpose: Daily record of V's team status in the Arsenal FC career simulator
-- Growth: 1 row per day (slow growth, ~365 rows/year)
-- =============================================================================
CREATE TABLE team_status_history (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Date this status applied (YYYY-MM-DD format, unique constraint)
    date TEXT UNIQUE NOT NULL,
    
    -- Current status: 'transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend'
    status TEXT NOT NULL CHECK(status IN ('transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend')),
    
    -- Consecutive days at current status (resets on status change)
    days_in_status INTEGER NOT NULL DEFAULT 1,
    
    -- Previous status before this one (NULL if first entry or starting status)
    previous_status TEXT CHECK(previous_status IS NULL OR previous_status IN ('transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend')),
    
    -- Top 5 of 7 average RPI that determined this status (performance metric)
    top5_avg REAL,
    
    -- How many of the 2 worst days were excluded from calculation (0-2)
    grace_days_used INTEGER DEFAULT 0 CHECK(grace_days_used >= 0 AND grace_days_used <= 2),
    
    -- Is V eligible for promotion? (has been at level long enough, 1=yes, 0=no)
    promotion_eligible INTEGER DEFAULT 0 CHECK(promotion_eligible IN (0, 1)),
    
    -- Days remaining in probation period after promotion (0 if not in probation)
    probation_days_remaining INTEGER DEFAULT 0 CHECK(probation_days_remaining >= 0),
    
    -- Record creation timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABLE 2: status_transitions
-- Purpose: Log every status change for career history analysis
-- Growth: Variable, depends on V's performance volatility
-- =============================================================================
CREATE TABLE status_transitions (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Date the transition occurred
    date TEXT NOT NULL,
    
    -- Status moving from
    from_status TEXT NOT NULL CHECK(from_status IN ('transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend')),
    
    -- Status moving to
    to_status TEXT NOT NULL CHECK(to_status IN ('transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend')),
    
    -- Why did this transition happen?
    -- 'performance': Met/failed performance thresholds
    -- 'unlock_elite': Unlocked Invincible/Legend tier
    -- 'probation_end': Probation period completed
    -- 'manual_override': Admin/testing adjustment
    reason TEXT NOT NULL CHECK(reason IN ('performance', 'unlock_elite', 'probation_end', 'manual_override')),
    
    -- Performance metric at time of transition
    top5_avg REAL,
    
    -- Optional notes for manual overrides or special circumstances
    notes TEXT,
    
    -- Record creation timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABLE 3: coaching_emails
-- Purpose: Track what coaching alerts have been sent to avoid spam
-- Growth: Variable, typically 2-5 emails per week
-- =============================================================================
CREATE TABLE coaching_emails (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Date email was sent
    date TEXT NOT NULL,
    
    -- Type of coaching email
    -- 'demotion': Status dropped
    -- 'promotion': Status improved
    -- 'warning': Performance trending down
    -- 'grace_alert': Using grace days
    -- 'achievement': Milestone reached
    email_type TEXT NOT NULL CHECK(email_type IN ('demotion', 'promotion', 'warning', 'grace_alert', 'achievement')),
    
    -- V's team status when email was sent
    status_at_time TEXT NOT NULL CHECK(status_at_time IN ('transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend')),
    
    -- What triggered this email? (human-readable description)
    trigger_context TEXT NOT NULL,
    
    -- How was it sent? 'gmail', 'dry_run', 'manual'
    sent_via TEXT NOT NULL CHECK(sent_via IN ('gmail', 'dry_run', 'manual')),
    
    -- Record creation timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABLE 4: career_stats
-- Purpose: Single-row aggregate statistics updated daily
-- Growth: 1 row only, updated in place
-- =============================================================================
CREATE TABLE career_stats (
    -- Primary key (always 1, enforced by app logic)
    id INTEGER PRIMARY KEY CHECK(id = 1),
    
    -- Total days in the career system
    total_game_days INTEGER DEFAULT 0,
    
    -- Days spent at each status level
    days_transfer_list INTEGER DEFAULT 0,
    days_reserves INTEGER DEFAULT 0,
    days_squad_member INTEGER DEFAULT 0,
    days_first_team INTEGER DEFAULT 0,
    days_invincible INTEGER DEFAULT 0,
    days_legend INTEGER DEFAULT 0,
    
    -- Career movement statistics
    total_promotions INTEGER DEFAULT 0,
    total_demotions INTEGER DEFAULT 0,
    
    -- Elite tier unlocks (how many times reached Invincible or Legend)
    elite_unlocks INTEGER DEFAULT 0,
    
    -- Longest streaks at high-performance tiers
    longest_streak_first_team INTEGER DEFAULT 0,
    longest_streak_invincible INTEGER DEFAULT 0,
    
    -- Last update date for cache invalidation
    last_updated TEXT,
    
    -- Record creation timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES: Optimize common query patterns
-- =============================================================================

-- team_status_history indexes
CREATE INDEX idx_team_status_date ON team_status_history(date);
CREATE INDEX idx_team_status_status ON team_status_history(status);
CREATE INDEX idx_team_status_promotion_eligible ON team_status_history(promotion_eligible);

-- status_transitions indexes
CREATE INDEX idx_transitions_date ON status_transitions(date);
CREATE INDEX idx_transitions_to_status ON status_transitions(to_status);
CREATE INDEX idx_transitions_reason ON status_transitions(reason);

-- coaching_emails indexes
CREATE INDEX idx_coaching_date ON coaching_emails(date);
CREATE INDEX idx_coaching_type ON coaching_emails(email_type);
CREATE INDEX idx_coaching_status ON coaching_emails(status_at_time);

-- =============================================================================
-- INITIAL DATA: Bootstrap career_stats with empty row
-- =============================================================================
INSERT INTO career_stats (id, total_game_days, last_updated) 
VALUES (1, 0, date('now'));

-- =============================================================================
-- Migration complete!
-- Next step: Run test_data_team_status.sql to populate sample data
-- =============================================================================
