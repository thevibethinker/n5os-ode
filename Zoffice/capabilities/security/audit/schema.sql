-- Audit table schema (reference documentation)
-- This table is created by rice-core during Zoffice installation.
-- The audit writer (writer.py) inserts into this table — it does NOT create it.

CREATE TABLE IF NOT EXISTS audit (
    id              VARCHAR NOT NULL PRIMARY KEY,
    timestamp       TIMESTAMP NOT NULL,
    capability      VARCHAR NOT NULL,
    employee        VARCHAR,
    action          VARCHAR NOT NULL,
    channel         VARCHAR,
    counterparty    VARCHAR,
    content_hash    VARCHAR,       -- SHA-256 of action + json(metadata)
    metadata        JSON,
    parent_event_id VARCHAR        -- links related audit events
);
