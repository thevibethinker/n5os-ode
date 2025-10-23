#!/usr/bin/env bash
# Enforce output-only contract for follow-up emails
# Usage: email_postprocess.sh <raw_out_path> <dest_email_txt>
set -euo pipefail
RAW=${1:?raw_out_missing}
DEST=${2:?dest_missing}
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
VALIDATOR="$SCRIPT_DIR/email_validator.py"
TMP=$(mktemp)

# Validate and extract
if python3 "$VALIDATOR" --in "$RAW" --min-words 120 >"$TMP" 2>"$TMP.err"; then
  mkdir -p "$(dirname "$DEST")"
  mv "$TMP" "$DEST"
  echo "ok: wrote $DEST"
else
  code=$?
  echo "postprocess_failed code=$code" >&2
  cat "$TMP.err" >&2 || true
  rm -f "$TMP" "$TMP.err"
  exit $code
fi
