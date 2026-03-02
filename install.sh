#!/bin/bash
# N5OS Ode Installer v2
# Moves repo contents to workspace root, merging with existing folders

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-/home/workspace}"

if [[ ! -f "$SCRIPT_DIR/BOOTLOADER.prompt.md" ]]; then
    echo "❌ Error: Run this from inside the n5os-ode directory"
    echo "   cd n5os-ode && bash install.sh"
    exit 1
fi

echo "📦 Installing N5OS Ode to $WORKSPACE"
echo ""

merge_dir() {
    local src="$1"
    local dst="$2"

    if [[ ! -d "$src" ]]; then
        return
    fi

    mkdir -p "$dst"
    cp -rn "$src"/* "$dst"/ 2>/dev/null || true
    echo "  ✓ Merged $src → $dst"
}

echo "Merging directories..."
merge_dir "$SCRIPT_DIR/N5" "$WORKSPACE/N5"
merge_dir "$SCRIPT_DIR/Prompts" "$WORKSPACE/Prompts"
merge_dir "$SCRIPT_DIR/Knowledge" "$WORKSPACE/Knowledge"
merge_dir "$SCRIPT_DIR/Records" "$WORKSPACE/Records"
merge_dir "$SCRIPT_DIR/Lists" "$WORKSPACE/Lists"
merge_dir "$SCRIPT_DIR/Skills" "$WORKSPACE/Skills"
merge_dir "$SCRIPT_DIR/docs" "$WORKSPACE/docs"
merge_dir "$SCRIPT_DIR/templates" "$WORKSPACE/templates"

echo ""
echo "Copying root files..."
for f in BOOTLOADER.prompt.md PERSONALIZE.prompt.md PLAN.prompt.md README.md CHANGELOG.md LICENSE .gitignore; do
    if [[ -f "$SCRIPT_DIR/$f" ]]; then
        if [[ ! -f "$WORKSPACE/$f" ]]; then
            cp "$SCRIPT_DIR/$f" "$WORKSPACE/$f"
            echo "  ✓ Copied $f"
        else
            echo "  ⏭ Skipped $f (already exists)"
        fi
    fi
done

echo ""
echo "Setting up config & directories..."
mkdir -p "$WORKSPACE/N5/config"
mkdir -p "$WORKSPACE/N5/builds"
mkdir -p "$WORKSPACE/Personal/Meetings/Inbox"

if [[ -d "$SCRIPT_DIR/templates/configs" ]]; then
    for template in "$SCRIPT_DIR"/templates/configs/*.template; do
        [[ -f "$template" ]] || continue
        target="$WORKSPACE/N5/config/$(basename "$template" .template)"
        if [[ ! -f "$target" ]]; then
            cp "$template" "$target"
            echo "  ✓ Created $target (from template — edit with your values)"
        fi
    done
fi

echo ""
echo "Cleaning up..."
cd "$WORKSPACE"
rm -rf "$SCRIPT_DIR"
echo "  ✓ Removed cloned directory"

echo ""
echo "✅ N5OS Ode v2 installed!"
echo ""
echo "Next steps:"
echo "  1. Open a new Zo conversation"
echo "  2. Run: @BOOTLOADER.prompt.md"
echo "  3. Then: @PERSONALIZE.prompt.md"
echo ""
echo "Optional:"
echo "  - Edit N5/config/drive_locations.yaml for Google Drive integration"
echo "  - Test meeting ingestion: python3 Skills/meeting-ingestion/scripts/meeting_cli.py status"
echo "  - See Skills/pulse/SKILL.md for build orchestration"
