-- Test Data: Team Status Career Progression
-- Date: 2025-10-30
-- Worker: W1 (Schema)
-- Description: Sample data for testing status tracking, transitions, emails, and career stats
-- Scenario: 14-day career journey from Transfer List → First Team with some ups and downs

-- =============================================================================
-- CLEANUP: Remove any existing test data
-- =============================================================================
DELETE FROM team_status_history;
DELETE FROM status_transitions;
DELETE FROM coaching_emails;
UPDATE career_stats SET 
    total_game_days = 0,
    days_transfer_list = 0,
    days_reserves = 0,
    days_squad_member = 0,
    days_first_team = 0,
    days_invincible = 0,
    days_legend = 0,
    total_promotions = 0,
    total_demotions = 0,
    elite_unlocks = 0,
    longest_streak_first_team = 0,
    longest_streak_invincible = 0,
    last_updated = date('now')
WHERE id = 1;

-- =============================================================================
-- SCENARIO: V's 14-day career journey
-- =============================================================================
-- Day 1-3: Starting on Transfer List (poor performance)
-- Day 4-5: Promoted to Reserves (improvement)
-- Day 6-10: Promoted to Squad Member, then First Team (sustained excellence)
-- Day 11: Brief dip but stays at First Team
-- Day 12-14: Strong performance at First Team
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Days 1-3: Transfer List (struggling)
-- -----------------------------------------------------------------------------
INSERT INTO team_status_history (date, status, days_in_status, previous_status, top5_avg, grace_days_used, promotion_eligible, probation_days_remaining)
VALUES 
    ('2025-10-16', 'transfer_list', 1, NULL, 0.65, 2, 0, 0),
    ('2025-10-17', 'transfer_list', 2, NULL, 0.68, 2, 0, 0),
    ('2025-10-18', 'transfer_list', 3, NULL, 0.72, 2, 1, 0);

-- -----------------------------------------------------------------------------
-- Days 4-5: Reserves (showing improvement)
-- -----------------------------------------------------------------------------
INSERT INTO team_status_history (date, status, days_in_status, previous_status, top5_avg, grace_days_used, promotion_eligible, probation_days_remaining)
VALUES 
    ('2025-10-19', 'reserves', 1, 'transfer_list', 0.88, 1, 0, 0),
    ('2025-10-20', 'reserves', 2, 'transfer_list', 0.92, 1, 0, 0);

-- Transition: Transfer List → Reserves
INSERT INTO status_transitions (date, from_status, to_status, reason, top5_avg, notes)
VALUES ('2025-10-19', 'transfer_list', 'reserves', 'performance', 0.88, 'Improved performance, 3 days above 90%');

-- Coaching email: Promotion to Reserves
INSERT INTO coaching_emails (date, email_type, status_at_time, trigger_context, sent_via)
VALUES ('2025-10-19', 'promotion', 'reserves', 'Promoted from Transfer List - good improvement!', 'gmail');

-- -----------------------------------------------------------------------------
-- Days 6-7: Squad Member (probation period after promotion)
-- -----------------------------------------------------------------------------
INSERT INTO team_status_history (date, status, days_in_status, previous_status, top5_avg, grace_days_used, promotion_eligible, probation_days_remaining)
VALUES 
    ('2025-10-21', 'squad_member', 1, 'reserves', 0.95, 0, 0, 7),
    ('2025-10-22', 'squad_member', 2, 'reserves', 0.98, 0, 0, 6);

-- Transition: Reserves → Squad Member
INSERT INTO status_transitions (date, from_status, to_status, reason, top5_avg, notes)
VALUES ('2025-10-21', 'reserves', 'squad_member', 'performance', 0.95, 'Strong 3-day performance above 90%');

-- Coaching email: Promotion to Squad Member
INSERT INTO coaching_emails (date, email_type, status_at_time, trigger_context, sent_via)
VALUES ('2025-10-21', 'promotion', 'squad_member', 'Promoted to Squad Member - 7 day probation period begins', 'gmail');

-- -----------------------------------------------------------------------------
-- Days 8-10: First Team (established, out of probation)
-- -----------------------------------------------------------------------------
INSERT INTO team_status_history (date, status, days_in_status, previous_status, top5_avg, grace_days_used, promotion_eligible, probation_days_remaining)
VALUES 
    ('2025-10-23', 'first_team', 1, 'squad_member', 1.02, 0, 0, 7),
    ('2025-10-24', 'first_team', 2, 'squad_member', 1.05, 0, 0, 6),
    ('2025-10-25', 'first_team', 3, 'squad_member', 1.08, 0, 0, 5);

-- Transition: Squad Member → First Team
INSERT INTO status_transitions (date, from_status, to_status, reason, top5_avg, notes)
VALUES ('2025-10-23', 'squad_member', 'first_team', 'performance', 1.02, 'Excellent sustained performance');

-- Coaching email: Promotion to First Team
INSERT INTO coaching_emails (date, email_type, status_at_time, trigger_context, sent_via)
VALUES ('2025-10-23', 'promotion', 'first_team', 'Promoted to First Team Starter - expectations met consistently!', 'gmail');

-- -----------------------------------------------------------------------------
-- Day 11: First Team (brief dip but still above threshold)
-- -----------------------------------------------------------------------------
INSERT INTO team_status_history (date, status, days_in_status, previous_status, top5_avg, grace_days_used, promotion_eligible, probation_days_remaining)
VALUES ('2025-10-26', 'first_team', 4, 'squad_member', 0.94, 1, 0, 4);

-- Coaching email: Warning about performance dip
INSERT INTO coaching_emails (date, email_type, status_at_time, trigger_context, sent_via)
VALUES ('2025-10-26', 'warning', 'first_team', 'Performance dipped slightly - used 1 grace day', 'gmail');

-- -----------------------------------------------------------------------------
-- Days 12-14: First Team (strong recovery and performance)
-- -----------------------------------------------------------------------------
INSERT INTO team_status_history (date, status, days_in_status, previous_status, top5_avg, grace_days_used, promotion_eligible, probation_days_remaining)
VALUES 
    ('2025-10-27', 'first_team', 5, 'squad_member', 1.01, 0, 0, 3),
    ('2025-10-28', 'first_team', 6, 'squad_member', 1.06, 0, 0, 2),
    ('2025-10-29', 'first_team', 7, 'squad_member', 1.10, 0, 1, 1);

-- -----------------------------------------------------------------------------
-- Update career_stats with aggregated data
-- -----------------------------------------------------------------------------
UPDATE career_stats SET
    total_game_days = 14,
    days_transfer_list = 3,
    days_reserves = 2,
    days_squad_member = 2,
    days_first_team = 7,
    days_invincible = 0,
    days_legend = 0,
    total_promotions = 3,
    total_demotions = 0,
    elite_unlocks = 0,
    longest_streak_first_team = 7,
    longest_streak_invincible = 0,
    last_updated = '2025-10-29'
WHERE id = 1;

-- =============================================================================
-- Test data complete!
-- =============================================================================
-- Summary:
--   - 14 days of status history
--   - 3 promotions (Transfer List → Reserves → Squad Member → First Team)
--   - 0 demotions
--   - 5 coaching emails (3 promotions, 1 warning, 0 demotions)
--   - Career stats reflect 14-day journey
--
-- Use this data to verify:
--   1. Status progression logic (W2)
--   2. Email triggering rules (W4)
--   3. Dashboard display (W5)
--   4. Query performance (all workers)
-- =============================================================================
