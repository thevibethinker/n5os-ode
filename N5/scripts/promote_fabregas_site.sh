#!/usr/bin/env bash
set -euo pipefail

# Backwards-compatible wrapper for promoting the Fabregas site.
# Delegates to the generic promote_site.sh script.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/promote_site.sh" fabregas-cannon "$@"

