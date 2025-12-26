CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    mode TEXT,
    
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    
    focus TEXT,
    objective TEXT,
    tags TEXT,
    
    parent_id TEXT,
    related_ids TEXT,
    
    starred INTEGER DEFAULT 0,
    progress_pct INTEGER DEFAULT 0,
    
    workspace_path TEXT,
    state_file_path TEXT,
    aar_path TEXT,
    
    FOREIGN KEY (parent_id) REFERENCES conversations(id)
);
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    filepath TEXT NOT NULL,
    artifact_type TEXT,
    created_at TEXT NOT NULL,
    description TEXT,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
CREATE TABLE issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    severity TEXT NOT NULL,
    category TEXT,
    message TEXT NOT NULL,
    context TEXT,
    resolution TEXT,
    resolved INTEGER DEFAULT 0,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
CREATE TABLE learnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    lesson_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    principle_refs TEXT,
    status TEXT DEFAULT 'pending',
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT,
    alternatives TEXT,
    outcome TEXT,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
CREATE INDEX idx_conversations_type ON conversations(type);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_starred ON conversations(starred);
CREATE INDEX idx_conversations_parent ON conversations(parent_id);
CREATE INDEX idx_artifacts_convo ON artifacts(conversation_id);
CREATE INDEX idx_issues_convo ON issues(conversation_id);
CREATE INDEX idx_issues_severity ON issues(severity, resolved);
CREATE INDEX idx_learnings_convo ON learnings(conversation_id);
CREATE INDEX idx_learnings_status ON learnings(status);
