#!/bin/bash
# Manual sync script - triggers Where's V email scan
# Usage: ./scripts/sync.sh

cd "$(dirname "$0")/.."
python3 scripts/email_scanner.py

