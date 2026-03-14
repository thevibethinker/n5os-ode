#!/usr/bin/env bash
set -euo pipefail

# Usage: bash bootstrap_empty_duckdbs.sh [workspace_root]
# Default root: current working directory
ROOT="${1:-$(pwd)}"
KIT="$ROOT/Documents/zo2zo-transfer/db-bootstrap-2026-03-02"

SOCIAL_DB="$ROOT/Skills/zode-moltbook/state/social_intelligence.db"
CAREER_DB="$ROOT/Datasets/career-hotline-calls/data.duckdb"

mkdir -p "$(dirname "$SOCIAL_DB")" "$(dirname "$CAREER_DB")"

# Recreate as empty DBs from dependency-ordered schema SQL
rm -f "$SOCIAL_DB" "$CAREER_DB"
duckdb "$SOCIAL_DB" < "$KIT/social_intelligence.bootstrap.sql"
duckdb "$CAREER_DB" < "$KIT/career_hotline_calls.bootstrap.sql"

# Sanity checks
duckdb "$SOCIAL_DB" -c "SHOW TABLES"
duckdb "$CAREER_DB" -c "SHOW TABLES"

echo "DB bootstrap complete:"
echo "- $SOCIAL_DB"
echo "- $CAREER_DB"
