-- Migration to align W1 schema with handoff spec
-- Run: sqlite3 /home/workspace/productivity_tracker.db < fix_schema.sql

BEGIN TRANSACTION;

-- Fix team_status_history: Add missing fields
ALTER TABLE team_status_history 
ADD COLUMN consecutive_poor_days INTEGER DEFAULT 0;

ALTER TABLE team_status_history 
ADD COLUMN reason TEXT;

ALTER TABLE team_status_history 
ADD COLUMN changed_at TIMESTAMP;

-- Fix status_transitions: Add missing fields
ALTER TABLE status_transitions 
ADD COLUMN grace_days_used INTEGER DEFAULT 0;

ALTER TABLE status_transitions 
ADD COLUMN consecutive_poor_days INTEGER DEFAULT 0;

ALTER TABLE status_transitions 
ADD COLUMN probation_triggered INTEGER DEFAULT 0;

COMMIT;

-- Verify schema
.schema team_status_history
.schema status_transitions
