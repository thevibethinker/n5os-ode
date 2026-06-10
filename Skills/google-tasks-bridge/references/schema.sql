CREATE TABLE IF NOT EXISTS google_task_lists (
    list_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    etag TEXT,
    updated_at TEXT,
    self_link TEXT,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS poll_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_system TEXT NOT NULL,
    list_id TEXT,
    list_title TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    fetched_count INTEGER NOT NULL DEFAULT 0,
    changed_count INTEGER NOT NULL DEFAULT 0,
    cursor_used TEXT,
    cursor_next TEXT,
    error_text TEXT
);

CREATE TABLE IF NOT EXISTS sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS google_tasks_current (
    task_id TEXT PRIMARY KEY,
    list_id TEXT NOT NULL,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL,
    due_date TEXT,
    completed_at TEXT,
    deleted INTEGER NOT NULL DEFAULT 0,
    hidden INTEGER NOT NULL DEFAULT 0,
    parent_id TEXT,
    position TEXT,
    updated_at TEXT,
    etag TEXT,
    web_view_link TEXT,
    execution_requested INTEGER NOT NULL DEFAULT 0,
    execution_suffix TEXT,
    snapshot_hash TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    last_run_id INTEGER,
    FOREIGN KEY (list_id) REFERENCES google_task_lists(list_id) ON DELETE CASCADE,
    FOREIGN KEY (last_run_id) REFERENCES poll_runs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS google_task_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    list_id TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    source_updated_at TEXT,
    snapshot_hash TEXT NOT NULL,
    state_status TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    run_id INTEGER,
    UNIQUE (task_id, snapshot_hash),
    FOREIGN KEY (task_id) REFERENCES google_tasks_current(task_id) ON DELETE CASCADE,
    FOREIGN KEY (list_id) REFERENCES google_task_lists(list_id) ON DELETE CASCADE,
    FOREIGN KEY (run_id) REFERENCES poll_runs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS google_task_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    list_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_at TEXT NOT NULL,
    run_id INTEGER,
    version_id INTEGER,
    summary TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    dedupe_key TEXT NOT NULL UNIQUE,
    FOREIGN KEY (task_id) REFERENCES google_tasks_current(task_id) ON DELETE CASCADE,
    FOREIGN KEY (list_id) REFERENCES google_task_lists(list_id) ON DELETE CASCADE,
    FOREIGN KEY (run_id) REFERENCES poll_runs(id) ON DELETE SET NULL,
    FOREIGN KEY (version_id) REFERENCES google_task_versions(version_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS intake_candidates (
    task_id TEXT PRIMARY KEY,
    list_id TEXT NOT NULL,
    canonical_title TEXT NOT NULL,
    execution_requested INTEGER NOT NULL DEFAULT 0,
    action_type TEXT,
    functional_area TEXT,
    intent_class TEXT,
    parser_confidence REAL,
    classifier_confidence REAL,
    candidate_status TEXT NOT NULL DEFAULT 'observed',
    staging_task_id INTEGER,
    promoted_task_id INTEGER,
    execution_target TEXT,
    last_routed_at TEXT,
    notes TEXT,
    classification_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (task_id) REFERENCES google_tasks_current(task_id) ON DELETE CASCADE,
    FOREIGN KEY (list_id) REFERENCES google_task_lists(list_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS execution_jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    list_id TEXT NOT NULL,
    execution_target TEXT NOT NULL,
    model_name TEXT,
    prompt_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    queued_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    response_json TEXT,
    error_text TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 1,
    attempt_token TEXT,
    lease_expires_at TEXT,
    last_heartbeat_at TEXT,
    worker_pid INTEGER,
    writeback_done INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (task_id) REFERENCES google_tasks_current(task_id) ON DELETE CASCADE,
    FOREIGN KEY (list_id) REFERENCES google_task_lists(list_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS meeting_review_batches (
        batch_id TEXT PRIMARY KEY,
        source_meeting_id TEXT NOT NULL,
        source_meeting_path TEXT NOT NULL,
        source_artifact TEXT,
        candidate_count INTEGER NOT NULL,
        digest_status TEXT NOT NULL DEFAULT 'created',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        presented_at TEXT,
        decided_at TEXT
    );

CREATE TABLE IF NOT EXISTS meeting_review_candidates (
        candidate_id TEXT PRIMARY KEY,
        batch_id TEXT NOT NULL,
        source_meeting_id TEXT NOT NULL,
        source_meeting_path TEXT NOT NULL,
        source_artifact TEXT NOT NULL,
        source_section TEXT,
        source_index INTEGER,
        raw_text TEXT,
        evidence_quotes TEXT,
        context_summary TEXT,
        process_notes TEXT,
        proposed_title TEXT NOT NULL,
        proposed_body TEXT,
        owner TEXT,
        project_or_area TEXT,
        urgency TEXT,
        importance TEXT,
        confidence REAL,
        task_size TEXT,
        size_rationale TEXT,
        sequence_group TEXT,
        step_index INTEGER,
        prerequisites TEXT,
        decomposition TEXT,
        review_status TEXT NOT NULL DEFAULT 'pending',
        v_decision_reason TEXT,
        final_title TEXT,
        final_body TEXT,
        final_due TEXT,
        final_google_task_id TEXT,
        final_google_list_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        decided_at TEXT,
        FOREIGN KEY (batch_id) REFERENCES meeting_review_batches(batch_id)
    );

CREATE TABLE IF NOT EXISTS meeting_review_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT,
        batch_id TEXT,
        event_type TEXT NOT NULL,
        event_data TEXT,
        actor TEXT,
        created_at TEXT NOT NULL
    );

CREATE TABLE IF NOT EXISTS meeting_review_inbound_messages (
        inbound_id TEXT PRIMARY KEY,
        channel TEXT NOT NULL,
        chat_id TEXT,
        message_id TEXT,
        sender TEXT,
        raw_text TEXT NOT NULL,
        matched_batch_id TEXT,
        parse_status TEXT NOT NULL,
        processing_status TEXT NOT NULL,
        error TEXT,
        created_at TEXT NOT NULL,
        processed_at TEXT,
        UNIQUE(channel, chat_id, message_id)
    );

CREATE TABLE IF NOT EXISTS meeting_review_lessons (
        lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        batch_id TEXT,
        candidate_id TEXT,
        kind TEXT NOT NULL,
        original_value TEXT,
        corrected_value TEXT,
        feedback_text TEXT,
        applied_to_policy_at TEXT,
        FOREIGN KEY (batch_id) REFERENCES meeting_review_batches(batch_id),
        FOREIGN KEY (candidate_id) REFERENCES meeting_review_candidates(candidate_id)
    );

CREATE TABLE IF NOT EXISTS meeting_review_task_creation_queue (
        queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        title TEXT NOT NULL,
        notes TEXT,
        target_list TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        attempt_count INTEGER NOT NULL DEFAULT 0,
        last_error TEXT,
        created_at TEXT NOT NULL,
        last_attempted_at TEXT,
        google_task_id TEXT,
        UNIQUE(candidate_id, target_list)
    );

CREATE INDEX IF NOT EXISTS idx_google_task_events_task
    ON google_task_events(task_id, event_at);

CREATE INDEX IF NOT EXISTS idx_google_task_events_type
    ON google_task_events(event_type, event_at);

CREATE INDEX IF NOT EXISTS idx_google_task_versions_task
    ON google_task_versions(task_id, observed_at);

CREATE INDEX IF NOT EXISTS idx_google_tasks_current_list
    ON google_tasks_current(list_id, status, deleted, hidden);

CREATE INDEX IF NOT EXISTS idx_google_tasks_current_updated
    ON google_tasks_current(updated_at);

CREATE INDEX IF NOT EXISTS idx_intake_candidates_status
    ON intake_candidates(candidate_status, execution_requested);

CREATE INDEX IF NOT EXISTS idx_mrb_meeting ON meeting_review_batches(source_meeting_id);
CREATE INDEX IF NOT EXISTS idx_mrb_status ON meeting_review_batches(digest_status);
CREATE INDEX IF NOT EXISTS idx_mrc_batch ON meeting_review_candidates(batch_id);
CREATE INDEX IF NOT EXISTS idx_mrc_meeting ON meeting_review_candidates(source_meeting_id);
CREATE INDEX IF NOT EXISTS idx_mrc_status ON meeting_review_candidates(review_status);
CREATE INDEX IF NOT EXISTS idx_mre_batch ON meeting_review_events(batch_id);
CREATE INDEX IF NOT EXISTS idx_mre_candidate ON meeting_review_events(candidate_id);
CREATE INDEX IF NOT EXISTS idx_mre_type ON meeting_review_events(event_type);
CREATE INDEX IF NOT EXISTS idx_mri_batch ON meeting_review_inbound_messages(matched_batch_id);
CREATE INDEX IF NOT EXISTS idx_mri_channel_msg ON meeting_review_inbound_messages(channel, chat_id, message_id);
CREATE INDEX IF NOT EXISTS idx_mri_status ON meeting_review_inbound_messages(processing_status);
CREATE INDEX IF NOT EXISTS idx_mrl_batch ON meeting_review_lessons(batch_id);
CREATE INDEX IF NOT EXISTS idx_mrl_kind ON meeting_review_lessons(kind);
CREATE INDEX IF NOT EXISTS idx_mrl_unapplied ON meeting_review_lessons(applied_to_policy_at) WHERE applied_to_policy_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_mrtcq_batch ON meeting_review_task_creation_queue(batch_id);
CREATE INDEX IF NOT EXISTS idx_mrtcq_status ON meeting_review_task_creation_queue(status);

CREATE UNIQUE INDEX IF NOT EXISTS idx_execution_jobs_active
    ON execution_jobs(task_id, status)
    WHERE status IN ('queued', 'launching', 'running');

CREATE VIEW IF NOT EXISTS v_active_google_tasks AS
SELECT
    g.task_id,
    g.list_id,
    l.title AS list_title,
    g.title,
    g.normalized_title,
    g.notes,
    g.status,
    g.due_date,
    g.updated_at,
    g.execution_requested,
    g.deleted,
    g.hidden,
    c.action_type,
    c.functional_area,
    c.intent_class,
    c.candidate_status,
    c.execution_target,
    c.staging_task_id,
    c.promoted_task_id
FROM google_tasks_current g
JOIN google_task_lists l ON l.list_id = g.list_id
LEFT JOIN intake_candidates c ON c.task_id = g.task_id
WHERE g.deleted = 0 AND g.hidden = 0;
