#!/bin/bash
set -e

#############################################################################
# N5 OS Core Bootstrap
# Minimal, high-confidence installation
#############################################################################

VERSION="1.0-core"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_PATH="${1:-/home/workspace}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "========================================"
echo "N5 OS Core Bootstrap v${VERSION}"
echo "========================================"
echo ""
echo "Installing to: $INSTALL_PATH"
echo "Dry run: $DRY_RUN"
echo ""

# Check prerequisites
log_info "Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { log_error "python3 is required but not installed"; exit 1; }
command -v git >/dev/null 2>&1 || log_warn "git not found (recommended but not required)"

# Create directories
log_info "Creating directory structure..."
if [ "$DRY_RUN" = false ]; then
  mkdir -p "$INSTALL_PATH/N5"/{prefs,scripts,schemas,commands}
  mkdir -p "$INSTALL_PATH/Knowledge/architectural"
  mkdir -p "$INSTALL_PATH/Lists"
  mkdir -p "$INSTALL_PATH/Documents"
fi

# Install core components
log_info "Installing core components..."

# 1. Prefs
log_info "  → Preferences (25 files)"
if [ "$DRY_RUN" = false ]; then
  cp -r "$SCRIPT_DIR/core/prefs/"* "$INSTALL_PATH/N5/prefs/"
fi

# 2. Schemas
log_info "  → Schemas (16 files)"
if [ "$DRY_RUN" = false ]; then
  cp "$SCRIPT_DIR/core/schemas/"* "$INSTALL_PATH/N5/schemas/" 2>/dev/null || true
fi

# 3. Commands
log_info "  → Command docs (4 files)"
if [ "$DRY_RUN" = false ]; then
  cp "$SCRIPT_DIR/core/commands/"* "$INSTALL_PATH/N5/commands/" 2>/dev/null || true
fi

# 4. Scripts
log_info "  → Scripts (4 essential)"
if [ "$DRY_RUN" = false ]; then
  cp "$SCRIPT_DIR/scripts/"*.py "$INSTALL_PATH/N5/scripts/"
  chmod +x "$INSTALL_PATH/N5/scripts/"*.py
fi

# 5. Knowledge
log_info "  → Architectural knowledge"
if [ "$DRY_RUN" = false ]; then
  cp "$SCRIPT_DIR/core/knowledge/"* "$INSTALL_PATH/Knowledge/architectural/"
fi

# 6. Lists
log_info "  → List system"
if [ "$DRY_RUN" = false ]; then
  cp "$SCRIPT_DIR/core/lists/POLICY.md" "$INSTALL_PATH/Lists/"
  cp "$SCRIPT_DIR/core/lists/"*.template "$INSTALL_PATH/Lists/" 2>/dev/null || true
fi

# 7. Documentation
log_info "  → Documentation"
if [ "$DRY_RUN" = false ]; then
  cp "$SCRIPT_DIR/docs/zero_touch_manifesto.md" "$INSTALL_PATH/Documents/"
fi

# Verify installation
log_info "Verifying installation..."
VERIFIED=0
[ -f "$INSTALL_PATH/N5/prefs/prefs.md" ] && VERIFIED=$((VERIFIED+1))
[ -f "$INSTALL_PATH/N5/scripts/n5_index_rebuild.py" ] && VERIFIED=$((VERIFIED+1))
[ -f "$INSTALL_PATH/Lists/POLICY.md" ] && VERIFIED=$((VERIFIED+1))
[ -f "$INSTALL_PATH/Knowledge/architectural/architectural_principles.md" ] && VERIFIED=$((VERIFIED+1))

if [ $VERIFIED -eq 4 ]; then
  log_info "✓ All core components verified"
else
  log_warn "Only $VERIFIED/4 core components found (this may be OK in dry-run mode)"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Read the philosophy:"
echo "   cat Documents/zero_touch_manifesto.md"
echo ""
echo "2. Review architectural principles:"
echo "   cat Knowledge/architectural/architectural_principles.md"
echo ""
echo "3. Understand preferences:"
echo "   cat N5/prefs/prefs.md"
echo ""
echo "4. Test core scripts:"
echo "   python3 N5/scripts/n5_git_check.py --dry-run"
echo "   python3 N5/scripts/n5_index_rebuild.py"
echo ""
echo "5. Initialize lists:"
echo "   cp Lists/ideas.jsonl.template Lists/ideas.jsonl"
echo ""
echo "Package: N5 OS Core v${VERSION}"
echo "Files: ~60 | Size: <500 KB"
echo ""
