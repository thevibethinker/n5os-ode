#!/usr/bin/env bash
set -euo pipefail

# Generic site promotion script
# Usage: promote_site.sh <slug> [--dry-run]
# Example: promote_site.sh fabregas-cannon

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -lt 1 ]]; then
  cat <<EOF
Usage: $(basename "$0") <slug> [--dry-run]

Promote a staging site to production by syncing:
  Sites/<slug>-staging/  →  Sites/<slug>/

Options:
  --dry-run   Show what would be copied/deleted without changing anything.
EOF
  exit 0
fi

SLUG="$1"
shift || true

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

ROOT="/home/workspace/Sites"
STAGING_DIR="$ROOT/${SLUG}-staging"
PROD_DIR="$ROOT/${SLUG}"

echo "[site-promote] Slug:      $SLUG"
echo "[site-promote] Staging:   $STAGING_DIR"
echo "[site-promote] Prod:      $PROD_DIR"

if [ ! -d "$STAGING_DIR" ]; then
  echo "[site-promote] ERROR: staging directory not found: $STAGING_DIR" >&2
  exit 1
fi

if [ ! -d "$PROD_DIR" ]; then
  echo "[site-promote] ERROR: production directory not found: $PROD_DIR" >&2
  exit 1
fi

# Optional visibility into protection status
python3 /home/workspace/N5/scripts/n5_protect.py check "$STAGING_DIR" || true
python3 /home/workspace/N5/scripts/n5_protect.py check "$PROD_DIR" || true

RSYNC_FLAGS=("-av" "--delete" "--exclude" "node_modules/")

if [ "$DRY_RUN" = true ]; then
  echo "[site-promote] DRY RUN: showing rsync operations only (no changes)." >&2
  RSYNC_FLAGS+=("--dry-run")
fi

echo "[site-promote] Syncing staging → prod (excluding node_modules/)..."
rsync "${RSYNC_FLAGS[@]}" "$STAGING_DIR"/ "$PROD_DIR"/

if [ "$DRY_RUN" = true ]; then
  echo "[site-promote] DRY RUN complete. No files were modified." >&2
else
  echo "[site-promote] Sync complete. Remember to restart the '$SLUG' service if needed." >&2
fi

