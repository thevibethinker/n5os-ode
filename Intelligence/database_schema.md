# Block Registry Database Schema

**Database:** `/home/workspace/Intelligence/blocks.db`  
**Created:** 2025-11-02  
**Purpose:** Unified storage for block metadata, generation history, validation results, and quality metrics

## Table 1: blocks (Master Registry)

```sql
CREATE TABLE blocks (
    block_id TEXT PRIMARY KEY,
    block_number INTEGER UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    input_requirements TEXT,
    output_format TEXT,
    validation_rubric TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_generated_at TIMESTAMP,
    total_generations INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0
);

CREATE INDEX idx_blocks_category ON blocks(category);
CREATE INDEX idx_blocks_status ON blocks(status);
```

## Table 2: generation_history

```sql
CREATE TABLE generation_history (
    generation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id TEXT NOT NULL,
    meeting_id TEXT NOT NULL,
    attempt_number INTEGER DEFAULT 1,
    status TEXT NOT NULL,
    input_context TEXT,
    output_path TEXT,
    generation_time_ms INTEGER,
    model_used TEXT,
    token_count INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (block_id) REFERENCES blocks(block_id)
);

CREATE INDEX idx_generation_history_block_id ON generation_history(block_id);
CREATE INDEX idx_generation_history_meeting_id ON generation_history(meeting_id);
CREATE INDEX idx_generation_history_status ON generation_history(status);
```

## Table 3: validation_results

```sql
CREATE TABLE validation_results (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    generation_id INTEGER NOT NULL,
    block_id TEXT NOT NULL,
    validation_type TEXT NOT NULL,
    status TEXT NOT NULL,
    score REAL,
    criteria_checked TEXT,
    failures TEXT,
    warnings TEXT,
    validator_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generation_id) REFERENCES generation_history(generation_id)
);

CREATE INDEX idx_validation_results_generation_id ON validation_results(generation_id);
CREATE INDEX idx_validation_results_block_id ON validation_results(block_id);
```

## Table 4: quality_samples

```sql
CREATE TABLE quality_samples (
    sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id TEXT NOT NULL,
    meeting_id TEXT NOT NULL,
    generation_id INTEGER,
    sample_type TEXT NOT NULL,
    input_snapshot TEXT NOT NULL,
    output_snapshot TEXT NOT NULL,
    validation_score REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_tested_at TIMESTAMP,
    test_pass_count INTEGER DEFAULT 0,
    test_fail_count INTEGER DEFAULT 0,
    FOREIGN KEY (block_id) REFERENCES blocks(block_id)
);

CREATE INDEX idx_quality_samples_block_id ON quality_samples(block_id);
CREATE INDEX idx_quality_samples_sample_type ON quality_samples(sample_type);
```

## Design Decisions

- **JSON Storage:** Flexible fields for validation rubrics, context, results
- **Denormalization:** Cached aggregates for performance  
- **Status Tracking:** Lifecycle states for blocks, generations, validations

---

*Schema Version: 1.0*  
*Created: 2025-11-02 23:45 EST*
