-- Zo Task System Schema
-- Created for: zo-task-system build (D1.1)
-- Purpose: Track tasks as "plans of action" with domain/project hierarchy, latency tracking, and source linking

-- Domains: Core life/work areas (permanent, rarely change)
CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    color TEXT DEFAULT '#4A90E2',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived BOOLEAN DEFAULT FALSE
);

-- Projects: Organized under domains, can be ephemeral, permanent, or recurring
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT NOT NULL DEFAULT 'ephemeral', -- ephemeral, permanent, recurring
    active BOOLEAN DEFAULT TRUE,
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE
);

-- Tasks: Core unit with full tracking and latency measurement
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    domain_id INTEGER NOT NULL,
    project_id INTEGER,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, in_progress, blocked, complete, abandoned
    priority_bucket TEXT NOT NULL DEFAULT 'normal', -- strategic, external, urgent, normal
    source_type TEXT NOT NULL DEFAULT 'manual', -- conversation, meeting, manual, email
    source_id TEXT, -- conversation_id, meeting_id, email_id, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_minutes INTEGER,
    actual_minutes INTEGER,
    parent_task_id INTEGER, -- For subtasks/milestones
    plan_json TEXT, -- Stores the plan of action (JSON), adjustable
    archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Task Events: Event log for latency analysis and pattern detection
CREATE TABLE IF NOT EXISTS task_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    event_type TEXT NOT NULL, -- created, started, blocked, unblocked, completed, abandoned, rescheduled, updated
    event_data TEXT, -- JSON with additional context (e.g., blocking_reason, reschedule_notes)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Indexes for performance

-- Tasks by status and priority (common query patterns)
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority_bucket ON tasks(priority_bucket);
CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks(status, priority_bucket);

-- Tasks by due date
CREATE INDEX IF NOT EXISTS idx_tasks_due_at ON tasks(due_at);
CREATE INDEX IF NOT EXISTS idx_tasks_due_at_active ON tasks(due_at) WHERE status IN ('pending', 'in_progress', 'blocked');

-- Tasks by source (for linking back to conversations/meetings)
CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_tasks_conversation ON tasks(source_type, source_id) WHERE source_type = 'conversation';

-- Task events for analytics
CREATE INDEX IF NOT EXISTS idx_task_events_task_id ON task_events(task_id);
CREATE INDEX IF NOT EXISTS idx_task_events_timestamp ON task_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_task_events_task_timestamp ON task_events(task_id, timestamp);

-- Domain/Project queries
CREATE INDEX IF NOT EXISTS idx_projects_domain ON projects(domain_id);
CREATE INDEX IF NOT EXISTS idx_projects_active ON projects(active) WHERE active = TRUE;

-- Helper views

-- View for current pending tasks with domain/project names
CREATE VIEW IF NOT EXISTS v_pending_tasks AS
SELECT
    t.id,
    t.title,
    t.description,
    t.status,
    t.priority_bucket,
    d.name AS domain_name,
    p.name AS project_name,
    t.due_at,
    t.created_at,
    t.estimated_minutes,
    t.source_type,
    t.source_id
FROM tasks t
JOIN domains d ON t.domain_id = d.id
LEFT JOIN projects p ON t.project_id = p.id
WHERE t.status IN ('pending', 'in_progress', 'blocked')
  AND t.archived = FALSE;

-- View for latency calculations (completed tasks only)
CREATE VIEW IF NOT EXISTS v_task_latency AS
SELECT
    t.id,
    t.title,
    t.due_at,
    t.completed_at,
    t.created_at,
    d.name AS domain_name,
    p.name AS project_name,
    CAST(
        CASE
            WHEN t.completed_at IS NOT NULL AND t.due_at IS NOT NULL
            THEN julianday(t.completed_at) - julianday(t.due_at)
            ELSE NULL
        END AS REAL
    ) * 24 AS hours_overdue,
    CAST(
        CASE
            WHEN t.completed_at IS NOT NULL
            THEN julianday(t.completed_at) - julianday(t.created_at)
            ELSE NULL
        END AS REAL
    ) * 24 AS hours_to_complete
FROM tasks t
JOIN domains d ON t.domain_id = d.id
LEFT JOIN projects p ON t.project_id = p.id
WHERE t.status = 'complete' AND t.completed_at IS NOT NULL;

-- View for today's tasks
CREATE VIEW IF NOT EXISTS v_tasks_today AS
SELECT
    t.*,
    d.name AS domain_name,
    p.name AS project_name
FROM tasks t
JOIN domains d ON t.domain_id = d.id
LEFT JOIN projects p ON t.project_id = p.id
WHERE t.status IN ('pending', 'in_progress', 'blocked')
  AND t.archived = FALSE
  AND (
    t.due_at IS NULL
    OR date(t.due_at) <= date('now', 'localtime', '+1 day')
  )
ORDER BY
    CASE t.priority_bucket
        WHEN 'strategic' THEN 1
        WHEN 'external' THEN 2
        WHEN 'urgent' THEN 3
        WHEN 'normal' THEN 4
        ELSE 5
    END,
    t.due_at ASC;
