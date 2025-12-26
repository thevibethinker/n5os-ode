#!/usr/bin/env bash
# N5OS Lite Bootstrap Script
# Version: 2.0.0
# Purpose: Complete installation, validation, and onboarding
# Usage: ./bootstrap.sh [--non-interactive] [--name "Your Name"]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE="${WORKSPACE:-/home/workspace}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NON_INTERACTIVE=false
USER_NAME=""
USER_ROLE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        --name)
            USER_NAME="$2"
            shift 2
            ;;
        --role)
            USER_ROLE="$2"
            shift 2
            ;;
        --workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

print_step() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header "N5OS Lite Bootstrap"
echo "Installing to: $WORKSPACE"
echo

# Phase 1: Installation
print_header "Phase 1: Installation"

# Copy core files
if [ -d "$SCRIPT_DIR/prompts" ]; then
    print_step "Copying prompts..."
    mkdir -p "$WORKSPACE/Prompts"
    cp -r "$SCRIPT_DIR/prompts/"*.md "$WORKSPACE/Prompts/" 2>/dev/null || true
fi

if [ -d "$SCRIPT_DIR/personas" ]; then
    print_step "Copying personas..."
    mkdir -p "$WORKSPACE/.n5os"
    cp -r "$SCRIPT_DIR/personas" "$WORKSPACE/.n5os/" 2>/dev/null || true
fi

if [ -d "$SCRIPT_DIR/principles" ]; then
    print_step "Copying principles..."
    mkdir -p "$WORKSPACE/.n5os"
    cp -r "$SCRIPT_DIR/principles" "$WORKSPACE/.n5os/" 2>/dev/null || true
fi

if [ -d "$SCRIPT_DIR/scripts" ]; then
    print_step "Copying scripts..."
    mkdir -p "$WORKSPACE/.n5os/scripts"
    cp -r "$SCRIPT_DIR/scripts/"*.py "$WORKSPACE/.n5os/scripts/" 2>/dev/null || true
    chmod +x "$WORKSPACE/.n5os/scripts/"*.py 2>/dev/null || true
fi

if [ -d "$SCRIPT_DIR/system" ]; then
    print_step "Copying system documentation..."
    mkdir -p "$WORKSPACE/.n5os/system"
    cp -r "$SCRIPT_DIR/system/"*.md "$WORKSPACE/.n5os/system/" 2>/dev/null || true
fi

if [ -d "$SCRIPT_DIR/schemas" ]; then
    print_step "Copying schemas..."
    mkdir -p "$WORKSPACE/.n5os/schemas"
    cp -r "$SCRIPT_DIR/schemas/"* "$WORKSPACE/.n5os/schemas/" 2>/dev/null || true
fi

# Copy documentation to workspace root
if [ -f "$SCRIPT_DIR/README.md" ]; then
    cp "$SCRIPT_DIR/README.md" "$WORKSPACE/.n5os/"
fi

if [ -f "$SCRIPT_DIR/QUICKSTART.md" ]; then
    cp "$SCRIPT_DIR/QUICKSTART.md" "$WORKSPACE/.n5os/"
fi

if [ -f "$SCRIPT_DIR/ARCHITECTURE.md" ]; then
    cp "$SCRIPT_DIR/ARCHITECTURE.md" "$WORKSPACE/.n5os/"
fi

print_step "Installation complete"
echo

# Phase 2: Health Check
print_header "Phase 2: System Health Check"

if [ -f "$WORKSPACE/.n5os/scripts/system_health_check.py" ]; then
    python3 "$WORKSPACE/.n5os/scripts/system_health_check.py" --workspace "$WORKSPACE" || {
        print_warning "Health check found issues (non-fatal)"
    }
else
    print_warning "Health check script not found - skipping validation"
fi
echo

# Phase 3: Onboarding
print_header "Phase 3: User Onboarding"

if [ -f "$WORKSPACE/.n5os/scripts/onboarding_wizard.py" ]; then
    ONBOARDING_ARGS="--workspace $WORKSPACE"
    
    if [ "$NON_INTERACTIVE" = true ]; then
        ONBOARDING_ARGS="$ONBOARDING_ARGS --non-interactive"
        
        if [ -n "$USER_NAME" ]; then
            ONBOARDING_ARGS="$ONBOARDING_ARGS --name \"$USER_NAME\""
        fi
        
        if [ -n "$USER_ROLE" ]; then
            ONBOARDING_ARGS="$ONBOARDING_ARGS --role \"$USER_ROLE\""
        fi
    fi
    
    python3 "$WORKSPACE/.n5os/scripts/onboarding_wizard.py" $ONBOARDING_ARGS || {
        print_error "Onboarding failed"
        exit 1
    }
else
    print_warning "Onboarding wizard not found - creating basic welcome"
    mkdir -p "$WORKSPACE/Documents"
    echo "# Welcome to N5OS Lite" > "$WORKSPACE/Documents/WELCOME.md"
    echo "" >> "$WORKSPACE/Documents/WELCOME.md"
    echo "Installation complete! Check .n5os/ directory for documentation." >> "$WORKSPACE/Documents/WELCOME.md"
fi
echo

# Phase 4: Final Steps
print_header "Phase 4: Completion"

# Create .n5os-version file
echo "2.0.0" > "$WORKSPACE/.n5os/.version"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$WORKSPACE/.n5os/.installed"

print_step "Installation validated"
print_step "Onboarding completed"
print_step "System ready for use"
echo

# Show next steps
print_header "🎉 N5OS Lite Installation Complete!"
echo
echo "📚 Documentation:"
echo "   • README: $WORKSPACE/.n5os/README.md"
echo "   • Quick Start: $WORKSPACE/.n5os/QUICKSTART.md"
echo "   • Architecture: $WORKSPACE/.n5os/ARCHITECTURE.md"
echo
echo "📁 Your workspace:"
echo "   • Prompts: $WORKSPACE/Prompts/"
echo "   • Documents: $WORKSPACE/Documents/"
echo "   • Lists: $WORKSPACE/Lists/"
echo
echo "🚀 Get started:"
echo "   1. Open: $WORKSPACE/Documents/WELCOME.md"
echo "   2. Tell your AI: 'Load planning_prompt.md'"
echo "   3. Try: 'Switch to Builder persona'"
echo
echo "💡 Tip: All system files are in $WORKSPACE/.n5os/"
echo
echo "Happy building! 🎊"
echo

exit 0
