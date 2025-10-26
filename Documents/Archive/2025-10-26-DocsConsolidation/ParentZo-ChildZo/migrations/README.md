# Migrations

Apply SQL files in numeric order to your Postgres database.

Example:

psql "$DATABASE_URL" -f 001_create_idempotency_records.sql

Nightly cleanup:

psql "$DATABASE_URL" -c "DELETE FROM idempotency_records WHERE ttl_at < now();"
