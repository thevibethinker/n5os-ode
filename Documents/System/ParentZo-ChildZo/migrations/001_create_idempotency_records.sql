-- Idempotency records table (YAGNI-optimized)
-- Apply to Postgres

CREATE TABLE IF NOT EXISTS idempotency_records (
  id SERIAL PRIMARY KEY,
  idempotency_key TEXT NOT NULL,
  handler TEXT NOT NULL,
  checksum TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('in_progress','succeeded','failed')),
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ttl_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '30 days'),
  details JSONB NULL,
  UNIQUE (idempotency_key, handler)
);

CREATE INDEX IF NOT EXISTS idx_idem_ttl ON idempotency_records (ttl_at);

-- Nightly cleanup example:
-- DELETE FROM idempotency_records WHERE ttl_at < now();
