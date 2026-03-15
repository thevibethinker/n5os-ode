#!/bin/bash
# N5OS Ode Installer
# Moves repo contents to workspace root, merging with existing folders

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE_ROOT:-/home/workspace}"

# Must be run from inside the n5os-ode directory
if [[ ! -f "$SCRIPT_DIR/BOOTLOADER.prompt.md" ]]; then
    echo "❌ Error: Run this from inside the n5os-ode directory"
    echo "   cd n5os-ode && bash install.sh"
    exit 1
fi

echo "📦 Installing N5OS Ode to $WORKSPACE"
echo ""

# Function to merge directory contents (not replace)
merge_dir() {
    local src="$1"
    local dst="$2"
    
    if [[ ! -d "$src" ]]; then
        return
    fi
    
    mkdir -p "$dst"
    
    # Copy contents, not the directory itself
    # -n = no clobber (don't overwrite existing files)
    cp -rn "$src"/* "$dst"/ 2>/dev/null || true
    echo "  ✓ Merged $src → $dst"
}

# ===== Phase 1: Merge all directories =====
echo "Merging directories..."
merge_dir "$SCRIPT_DIR/N5" "$WORKSPACE/N5"
merge_dir "$SCRIPT_DIR/Prompts" "$WORKSPACE/Prompts"
merge_dir "$SCRIPT_DIR/Knowledge" "$WORKSPACE/Knowledge"
merge_dir "$SCRIPT_DIR/Records" "$WORKSPACE/Records"
merge_dir "$SCRIPT_DIR/Lists" "$WORKSPACE/Lists"
merge_dir "$SCRIPT_DIR/docs" "$WORKSPACE/docs"
# templates are now under N5/templates (merged with N5/)
merge_dir "$SCRIPT_DIR/Skills" "$WORKSPACE/Skills"
merge_dir "$SCRIPT_DIR/scripts" "$WORKSPACE/scripts"
merge_dir "$SCRIPT_DIR/Personal" "$WORKSPACE/Personal"

# ===== Phase 2: Copy root-level files =====
echo ""
echo "Copying root files..."
for f in BOOTLOADER.prompt.md PERSONALIZE.prompt.md WALKTHROUGH.prompt.md README.md CHANGELOG.md LICENSE .gitignore; do
    if [[ -f "$SCRIPT_DIR/$f" ]]; then
        if [[ ! -f "$WORKSPACE/$f" ]]; then
            cp "$SCRIPT_DIR/$f" "$WORKSPACE/$f"
            echo "  ✓ Copied $f"
        else
            echo "  ⚠️  Skipped $f (already exists — delete it first to get the latest version)"
        fi
    fi
done

# ===== Phase 3: Set up config templates =====
echo ""
echo "Setting up configuration..."
mkdir -p "$WORKSPACE/N5/config"

if [[ -d "$SCRIPT_DIR/templates/configs" ]]; then
    for template in "$SCRIPT_DIR"/templates/configs/*.template; do
        [[ -f "$template" ]] || continue
        target="$WORKSPACE/N5/config/$(basename "$template" .template)"
        if [[ ! -f "$target" ]]; then
            cp "$template" "$target"
            echo "  ✓ Created: $target (from template — edit with your values)"
        else
            echo "  ⏭ Skipped: $target (already exists)"
        fi
    done
fi

# Create Personal/Meetings directory structure
mkdir -p "$WORKSPACE/Personal/Meetings/Inbox"

# ===== Phase 4: Clean up =====
echo ""
echo "Installation complete. The cloned n5os-ode/ folder will now be removed."
echo "(Your installed files are safely in $WORKSPACE)"
read -p "Press Enter to continue (or Ctrl+C to keep the folder)..." 2>/dev/null || true
echo ""
echo "Cleaning up..."
cd "$WORKSPACE"
rm -rf "$SCRIPT_DIR"
echo "  ✓ Removed n5os-ode/ directory"

# ===== Done =====
echo ""
echo "✅ N5OS Ode installed!"
echo ""
echo "Next steps:"
echo "  1. Open a new Zo conversation"
echo "  2. Run: @BOOTLOADER.prompt.md"
echo "  3. Then: @PERSONALIZE.prompt.md"
echo "  4. Then: @WALKTHROUGH.prompt.md (optional guided tour)"
echo ""
echo "📝 For Meeting Ingestion:"
echo "   1. Edit N5/config/drive_locations.yaml with your Google Drive folder ID"
echo "   2. Connect Google Drive in Zo Settings > Integrations"
echo "   3. Test with: python3 Skills/meeting-ingestion/scripts/meeting_cli.py status"
echo ""
echo "📝 For Pulse (build orchestration):"
echo "   1. Create a build: mkdir -p N5/builds/my-build/{drops,deposits,artifacts}"
echo "   2. See Skills/pulse/SKILL.md for full documentation"
