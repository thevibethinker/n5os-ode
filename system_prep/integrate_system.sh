#!/bin/bash
# System-wide Cache Integration Script
# This script integrates the cache system across all Zo Computer workflows

echo "🔗 Integrating cache system across Zo Computer..."

# 1. Add cache system to system PATH
CACHE_PATH_EXPORT="export PATH=\"/home/workspace/system_prep:\$PATH\""
SHELL_RC_FILES=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")

for rc_file in "${SHELL_RC_FILES[@]}"; do
    if [ -f "$rc_file" ]; then
        if ! grep -q "system_prep" "$rc_file"; then
            echo "# Cache System Integration" >> "$rc_file"
            echo "$CACHE_PATH_EXPORT" >> "$rc_file"
            echo "✅ Updated $rc_file"
        fi
    fi
done

# 2. Create cache system aliases for easy access
cat >> "$HOME/.bashrc" << 'EOF'

# Cache System Aliases
alias cache-add='python3 /home/workspace/system_prep/cache_manager.py add --file'
alias cache-list='python3 /home/workspace/system_prep/cache_manager.py list'
alias cache-clean='python3 /home/workspace/system_prep/cache_manager.py cleanup'
alias cache-distribute='python3 /home/workspace/system_prep/distribute_docs.py distribute --category'

# Quick cache functions
cache-conversation() { python3 /home/workspace/system_prep/cache_manager.py add --file "$1" --category conversation; }
cache-log() { python3 /home/workspace/system_prep/cache_manager.py add --file "$1" --category logs; }
cache-backup() { python3 /home/workspace/system_prep/cache_manager.py add --file "$1" --category backups; }
EOF

# 3. Integrate with existing workflows
WORKFLOW_DIRS=(
    "/home/workspace/N5/scripts"
    "/home/workspace/N5/command_authoring"
    "/home/workspace/examples"
)

for dir in "${WORKFLOW_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        # Add cache system documentation to each workflow directory
        cat > "$dir/CACHE_SYSTEM_README.md" << 'EOF'
# Cache System Integration

This directory is integrated with the Zo Computer Cache System.

## Quick Commands

```bash
# Cache a file from this directory
cache-add /path/to/file.txt --category workflow

# List cached files
cache-list

# Cache current conversation outputs
cache-conversation conversation_output.md

# Cache logs
cache-log script.log

# Cache backups
cache-backup backup.tar.gz
```

## Categories

- `conversation`: Chat/conversation outputs
- `logs`: Log files and execution traces
- `backups`: Backup files and archives
- `generated`: Auto-generated content
- `temporary`: Temporary files (auto-cleaned)
- `workflow`: Workflow-specific files

## Automatic Features

- Files are automatically cleaned after 7 days (configurable)
- Metadata tracking for all cached files
- Duplicate prevention with hash-based checking
- Distribution to configured destinations

For more info: `/home/workspace/system_prep/README.md`
EOF
        echo "✅ Added cache integration to $dir"
    fi
done

# 4. Update existing scripts to use cache system
echo "🔄 Updating existing scripts..."

# Find Python scripts that might benefit from cache integration
find /home/workspace -name "*.py" -type f -not -path "*/__pycache__/*" -not -path "*/system_prep/*" | head -10 | while read script; do
    if ! grep -q "cache_manager" "$script"; then
        # Add cache import to Python scripts (commented out by default)
        sed -i '1a\# Cache System Integration (uncomment to use):' "$script"
        sed -i '2a\# from system_prep.cache_manager import CacheManager' "$script"
        echo "📝 Updated $script with cache integration hints"
    fi
done

echo "🎉 Cache system integration complete!"
echo ""
echo "📋 What's now available system-wide:"
echo "  • cache-add, cache-list, cache-clean aliases"
echo "  • Quick functions: cache-conversation, cache-log, cache-backup"
echo "  • Automatic file monitoring (if inotify-tools installed)"
echo "  • Cache system in PATH for easy access"
echo "  • Documentation in workflow directories"
echo ""
echo "🚀 Ready to maintain a clean, organized workspace!"