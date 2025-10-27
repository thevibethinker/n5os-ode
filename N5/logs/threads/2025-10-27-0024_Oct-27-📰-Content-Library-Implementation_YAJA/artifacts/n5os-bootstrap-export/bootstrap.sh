#!/bin/bash
set -e

#############################################################################
# N5 OS Bootstrap Installer
# Installs N5 OS onto Eric's Zo instance (or any Unix environment)
#############################################################################

VERSION="1.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_PATH="${1:-.}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

#############################################################################
# Welcome & Preflight
#############################################################################

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}N5 OS Bootstrap v${VERSION}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

log_info "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
  log_error "Python 3 is required but not installed"
fi
log_ok "Python 3 found: $(python3 --version)"

# Check Git (optional but recommended)
if command -v git &> /dev/null; then
  log_ok "Git found: $(git --version)"
else
  log_warn "Git not found (optional, but recommended for future updates)"
fi

# Install path
if [ ! -d "$INSTALL_PATH" ]; then
  log_warn "Installation path does not exist: $INSTALL_PATH"
  read -p "Create it? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p "$INSTALL_PATH"
    log_ok "Created: $INSTALL_PATH"
  else
    log_error "Installation cancelled"
  fi
fi

#############################################################################
# Module Selection
#############################################################################

echo ""
log_info "Selecting modules to install..."
echo ""

declare -A SELECTED

echo "Module Selection Menu:"
echo "====================="
echo ""
echo "CORE MODULES (required):"
echo "  [1] Core Foundation (prefs, schemas, command registry)"
SELECTED["core"]=true
echo "      → SELECTED (required)"
echo ""

echo "SYSTEM MODULES (optional):"
echo ""

read -p "Install List Management System? (y/n, default: y) " -n 1 -r
echo
SELECTED["lists"]=$([[ $REPLY =~ ^[Yy]?$ ]] && echo true || echo false)

read -p "Install Meeting Ingestion Workflows? (y/n, default: y) " -n 1 -r
echo
SELECTED["meetings"]=$([[ $REPLY =~ ^[Yy]?$ ]] && echo true || echo false)

read -p "Install Knowledge Base Reference? (y/n, default: n) " -n 1 -r
echo
SELECTED["knowledge"]=$([[ $REPLY =~ ^[Yy]$ ]] && echo true || echo false)

echo ""
echo "SCRIPT MODULES (optional):"
echo ""
echo "  [A] Minimal (core utilities only) ~8 MB"
echo "  [B] Standard (core + workflows) ~45 MB [DEFAULT]"
echo "  [C] Full Suite (all 259 scripts) ~120 MB"
echo "  [N] None"
echo ""

read -p "Select scripts package (A/B/C/N, default: B) " -n 1 -r
echo
SCRIPTS_CHOICE=${REPLY:-B}

case $SCRIPTS_CHOICE in
  A|a) SELECTED["scripts"]="minimal" ;;
  B|b) SELECTED["scripts"]="standard" ;;
  C|c) SELECTED["scripts"]="full" ;;
  N|n) SELECTED["scripts"]="none" ;;
  *) SELECTED["scripts"]="standard" ;;
esac

read -p "Install Communication Templates? (y/n, default: n) " -n 1 -r
echo
SELECTED["communications"]=$([[ $REPLY =~ ^[Yy]$ ]] && echo true || echo false)

#############################################################################
# Summary
#############################################################################

echo ""
log_info "Installation Summary:"
echo "  Installation Path: $INSTALL_PATH"
echo "  Modules to install:"
echo "    • Core Foundation: ${SELECTED[core]}"
echo "    • Lists System: ${SELECTED[lists]}"
echo "    • Meeting Ingestion: ${SELECTED[meetings]}"
echo "    • Knowledge Base: ${SELECTED[knowledge]}"
echo "    • Scripts Package: ${SELECTED[scripts]}"
echo "    • Communications: ${SELECTED[communications]}"
echo ""

read -p "Proceed with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  log_warn "Installation cancelled"
  exit 0
fi

#############################################################################
# Installation
#############################################################################

echo ""
log_info "Starting installation..."
echo ""

MODULES_INSTALLED=0

# Core (always installed)
if [ "${SELECTED[core]}" = true ]; then
  log_info "Installing Core Foundation..."
  mkdir -p "$INSTALL_PATH/N5/"{prefs,schemas,config,commands}
  cp -r "$SCRIPT_DIR/core/prefs" "$INSTALL_PATH/N5/" 2>/dev/null || true
  cp -r "$SCRIPT_DIR/core/schemas" "$INSTALL_PATH/N5/" 2>/dev/null || true
  cp -r "$SCRIPT_DIR/core/config"/* "$INSTALL_PATH/N5/config/" 2>/dev/null || true
  cp -r "$SCRIPT_DIR/core/commands" "$INSTALL_PATH/N5/" 2>/dev/null || true
  log_ok "Core Foundation installed"
  ((MODULES_INSTALLED++))
fi

# Lists
if [ "${SELECTED[lists]}" = true ]; then
  log_info "Installing List Management System..."
  mkdir -p "$INSTALL_PATH/Lists"
  cp -r "$SCRIPT_DIR/systems/lists"/* "$INSTALL_PATH/Lists/" 2>/dev/null || true
  log_ok "List Management System installed"
  ((MODULES_INSTALLED++))
fi

# Meetings
if [ "${SELECTED[meetings]}" = true ]; then
  log_info "Installing Meeting Ingestion Workflows..."
  mkdir -p "$INSTALL_PATH/N5/protocols/meetings"
  cp -r "$SCRIPT_DIR/systems/meetings"/* "$INSTALL_PATH/N5/protocols/meetings/" 2>/dev/null || true
  log_ok "Meeting Ingestion Workflows installed"
  ((MODULES_INSTALLED++))
fi

# Knowledge
if [ "${SELECTED[knowledge]}" = true ]; then
  log_info "Installing Knowledge Base Reference..."
  mkdir -p "$INSTALL_PATH/Knowledge/stable"
  cp -r "$SCRIPT_DIR/systems/knowledge"/* "$INSTALL_PATH/Knowledge/stable/" 2>/dev/null || true
  log_ok "Knowledge Base Reference installed"
  ((MODULES_INSTALLED++))
fi

# Scripts
if [ "${SELECTED[scripts]}" != "none" ]; then
  log_info "Installing Scripts Package (${SELECTED[scripts]})..."
  mkdir -p "$INSTALL_PATH/N5/scripts"
  
  if [ "${SELECTED[scripts]}" = "minimal" ] || [ "${SELECTED[scripts]}" = "standard" ] || [ "${SELECTED[scripts]}" = "full" ]; then
    cp -r "$SCRIPT_DIR/scripts/core"/* "$INSTALL_PATH/N5/scripts/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR/scripts/lib" "$INSTALL_PATH/N5/scripts/" 2>/dev/null || true
  fi
  
  if [ "${SELECTED[scripts]}" = "standard" ] || [ "${SELECTED[scripts]}" = "full" ]; then
    cp -r "$SCRIPT_DIR/scripts/modules"/* "$INSTALL_PATH/N5/scripts/" 2>/dev/null || true
  fi
  
  if [ "${SELECTED[scripts]}" = "full" ]; then
    cp -r "$SCRIPT_DIR/scripts"/* "$INSTALL_PATH/N5/scripts/" 2>/dev/null || true
  fi
  
  log_ok "Scripts Package (${SELECTED[scripts]}) installed"
  ((MODULES_INSTALLED++))
fi

# Communications
if [ "${SELECTED[communications]}" = true ]; then
  log_info "Installing Communication Templates..."
  mkdir -p "$INSTALL_PATH/N5/prefs/communication"
  cp -r "$SCRIPT_DIR/config/communications"/* "$INSTALL_PATH/N5/prefs/communication/" 2>/dev/null || true
  log_ok "Communication Templates installed"
  ((MODULES_INSTALLED++))
fi

#############################################################################
# Post-Install
#############################################################################

echo ""
log_info "Running post-installation setup..."

# Create basic directory structure
mkdir -p "$INSTALL_PATH"/{Knowledge,Lists,Documents,Records} 2>/dev/null || true

# Initialize git if available
if command -v git &> /dev/null; then
  if [ ! -d "$INSTALL_PATH/.git" ]; then
    log_info "Initializing git repository..."
    cd "$INSTALL_PATH"
    git init
    git config user.email "eric@zo.computer" 2>/dev/null || true
    git config user.name "Eric" 2>/dev/null || true
    cd - > /dev/null
    log_ok "Git repository initialized"
  fi
fi

# Create .gitignore
cat > "$INSTALL_PATH/.gitignore" << 'EOF'
*.pyc
__pycache__/
.state/
*.log
.DS_Store
N5/.state/
N5/records/
N5/inbox/
N5/logs/
Records/
EOF
log_ok "Created .gitignore"

#############################################################################
# Final Summary
#############################################################################

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
log_ok "Installed $MODULES_INSTALLED module(s)"
log_ok "Installation path: $INSTALL_PATH"
echo ""
echo "Next steps:"
echo "  1. cd $INSTALL_PATH"
echo "  2. Review N5/prefs/prefs.md for system overview"
echo "  3. Review ARCHITECTURE.md in the docs/ folder"
echo "  4. Run: python3 N5/scripts/n5_index_rebuild.py"
echo ""
echo "For more help:"
echo "  • Read: $INSTALL_PATH/docs/ARCHITECTURE.md"
echo "  • Read: $INSTALL_PATH/docs/MODULES.md"
echo "  • Check: $INSTALL_PATH/N5/prefs/prefs.md"
echo ""
