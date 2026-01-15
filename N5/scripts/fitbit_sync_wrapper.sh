#!/bin/bash
# Fitbit Sync Wrapper - ensures PYTHONPATH is set correctly
# Usage: ./fitbit_sync_wrapper.sh [sync-recent|start-auth|finish-auth] [args...]

set -e

export PYTHONPATH=/home/workspace

SCRIPT_DIR="/home/workspace/Personal/Health/WorkoutTracker"
LOG_FILE="/dev/shm/fitbit-sync.log"

echo "=== Fitbit Sync: $(date -Iseconds) ===" >> "$LOG_FILE"

python3 "$SCRIPT_DIR/fitbit_sync.py" "$@" 2>&1 | tee -a "$LOG_FILE"

echo "=== Sync complete ===" >> "$LOG_FILE"

