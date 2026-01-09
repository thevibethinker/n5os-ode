#!/bin/bash
# R-Block Framework: Worker Runner for Claude Code
# Usage: ./run_workers.sh [worker_id] or ./run_workers.sh --parallel w01 w02

set -e

PROJECT="r-block-framework"
WORKERS_DIR="/home/workspace/N5/builds/r-block-framework/workers"

show_status() {
    python3 /home/workspace/N5/scripts/build_orchestrator_v2.py status --project "$PROJECT"
}

show_ready() {
    python3 /home/workspace/N5/scripts/build_orchestrator_v2.py ready --project "$PROJECT"
}

run_single() {
    local worker_id="$1"
    local worker_file="$WORKERS_DIR/${worker_id}.md"
    
    if [[ ! -f "$worker_file" ]]; then
        echo "Error: Worker file not found: $worker_file"
        exit 1
    fi
    
    echo "Spawning worker: $worker_id"
    echo "Command for Claude Code:"
    echo ""
    echo "  claude \"Execute the worker assignment in $worker_file\""
    echo ""
}

run_parallel() {
    shift  # Remove --parallel flag
    echo "Parallel worker spawn commands:"
    echo ""
    for worker_id in "$@"; do
        local worker_file="$WORKERS_DIR/${worker_id}.md"
        if [[ -f "$worker_file" ]]; then
            echo "claude \"Execute the worker assignment in $worker_file\" &"
        else
            echo "# Skipping $worker_id - file not found"
        fi
    done
    echo "wait"
    echo ""
}

case "${1:-}" in
    --status)
        show_status
        ;;
    --ready)
        show_ready
        ;;
    --parallel)
        run_parallel "$@"
        ;;
    --help|"")
        echo "R-Block Framework Worker Runner"
        echo ""
        echo "Usage:"
        echo "  ./run_workers.sh --status           Show project status"
        echo "  ./run_workers.sh --ready            Show ready workers"
        echo "  ./run_workers.sh <worker_id>        Show spawn command for single worker"
        echo "  ./run_workers.sh --parallel w01 w02 Show parallel spawn commands"
        echo ""
        echo "Ready workers right now:"
        show_ready
        ;;
    *)
        run_single "$1"
        ;;
esac

