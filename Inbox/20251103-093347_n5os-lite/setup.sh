#!/usr/bin/env bash
# N5OS Lite Setup Script
# Version: 1.0
# Created: 2025-11-03

set -e  # Exit on error

WORKSPACE="${HOME}/workspace"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== N5OS Lite Setup ==="
echo ""

# Check if workspace exists
if [! -d "$WORKSPACE" ]; then
    echo "Creating workspace directory: $WORKSPACE"
    mkdir -p "$WORKSPACE"
fi

# Setup options
echo "Choose setup option:"
echo "  1) Full installation (all components)"
echo "  2) Minimal installation (prompts + principles only)"
echo "  3) Custom installation (select components)"
echo "  4) Dry-run (show what would be copied)"
echo ""
read -p "Enter option (1-4): " OPTION

# Dry-run mode
if [ "$OPTION" = "4" ]; then
    echo ""
    echo "=== Dry-Run Mode ==="
    echo "Would copy to: $WORKSPACE"
    echo ""
    echo "Full installation would include:"
    tree -L 2 "$SCRIPT_DIR" 2>/dev/null || find "$SCRIPT_DIR" -type f -o -type d | head -20
    echo ""
    echo "No files copied (dry-run mode)"
    exit 0
fi

# Full installation
if [ "$OPTION" = "1" ]; then
    echo ""
    echo "Installing full N5OS Lite to: $WORKSPACE"
    
    # Copy components
    echo "- Copying prompts..."
    mkdir -p "$WORKSPACE/Prompts"
    cp -r "$SCRIPT_DIR/prompts/"* "$WORKSPACE/Prompts/" 2>/dev/null || true
    
    echo "- Copying principles..."
    mkdir -p "$WORKSPACE/principles"
    cp -r "$SCRIPT_DIR/principles/"* "$WORKSPACE/principles/" 2>/dev/null || true
    
    echo "- Copying personas..."
    mkdir -p "$WORKSPACE/personas"
    cp -r "$SCRIPT_DIR/personas/"* "$WORKSPACE/personas/" 2>/dev/null || true
    
    echo "- Copying system docs..."
    mkdir -p "$WORKSPACE/system"
    cp -r "$SCRIPT_DIR/system/"* "$WORKSPACE/system/" 2>/dev/null || true
    
    echo "- Copying rules..."
    mkdir -p "$WORKSPACE/rules"
    cp -r "$SCRIPT_DIR/rules/"* "$WORKSPACE/rules/" 2>/dev/null || true
    
    echo "- Copying documentation..."
    cp "$SCRIPT_DIR/README.md" "$WORKSPACE/" 2>/dev/null || true
    cp "$SCRIPT_DIR/ARCHITECTURE.md" "$WORKSPACE/" 2>/dev/null || true
    
    echo ""
    echo "✅ Full installation complete!"
fi

# Minimal installation
if [ "$OPTION" = "2" ]; then
    echo ""
    echo "Installing minimal N5OS Lite to: $WORKSPACE"
    
    echo "- Copying prompts..."
    mkdir -p "$WORKSPACE/Prompts"
    cp "$SCRIPT_DIR/prompts/planning_prompt.md" "$WORKSPACE/Prompts/" 2>/dev/null || true
    
    echo "- Copying principles..."
    mkdir -p "$WORKSPACE/principles"
    cp -r "$SCRIPT_DIR/principles/"* "$WORKSPACE/principles/" 2>/dev/null || true
    
    echo "- Copying README..."
    cp "$SCRIPT_DIR/README.md" "$WORKSPACE/" 2>/dev/null || true
    
    echo ""
    echo "✅ Minimal installation complete!"
fi

# Custom installation
if [ "$OPTION" = "3" ]; then
    echo ""
    echo "Custom installation:"
    echo ""
    
    read -p "Install prompts? (y/n): " INSTALL_PROMPTS
    if [ "$INSTALL_PROMPTS" = "y" ]; then
        mkdir -p "$WORKSPACE/Prompts"
        cp -r "$SCRIPT_DIR/prompts/"* "$WORKSPACE/Prompts/" 2>/dev/null || true
        echo "✓ Prompts installed"
    fi
    
    read -p "Install principles? (y/n): " INSTALL_PRINCIPLES
    if [ "$INSTALL_PRINCIPLES" = "y" ]; then
        mkdir -p "$WORKSPACE/principles"
        cp -r "$SCRIPT_DIR/principles/"* "$WORKSPACE/principles/" 2>/dev/null || true
        echo "✓ Principles installed"
    fi
    
    read -p "Install personas? (y/n): " INSTALL_PERSONAS
    if [ "$INSTALL_PERSONAS" = "y" ]; then
        mkdir -p "$WORKSPACE/personas"
        cp -r "$SCRIPT_DIR/personas/"* "$WORKSPACE/personas/" 2>/dev/null || true
        echo "✓ Personas installed"
    fi
    
    read -p "Install system docs? (y/n): " INSTALL_SYSTEM
    if [ "$INSTALL_SYSTEM" = "y" ]; then
        mkdir -p "$WORKSPACE/system"
        cp -r "$SCRIPT_DIR/system/"* "$WORKSPACE/system/" 2>/dev/null || true
        echo "✓ System docs installed"
    fi
    
    read -p "Install documentation? (y/n): " INSTALL_DOCS
    if [ "$INSTALL_DOCS" = "y" ]; then
        cp "$SCRIPT_DIR/README.md" "$WORKSPACE/" 2>/dev/null || true
        cp "$SCRIPT_DIR/ARCHITECTURE.md" "$WORKSPACE/" 2>/dev/null || true
        echo "✓ Documentation installed"
    fi
    
    echo ""
    echo "✅ Custom installation complete!"
fi

# Next steps
echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Read: $WORKSPACE/README.md"
echo "2. Load planning prompt: Tell your AI to load Prompts/planning_prompt.md"
echo "3. Reference principles: Use P1, P15, P36, etc. in conversations"
echo "4. Use personas: 'Switch to Builder mode' or 'Activate Strategist persona'"
echo ""
echo "For help: Check README.md and ARCHITECTURE.md"
echo ""
