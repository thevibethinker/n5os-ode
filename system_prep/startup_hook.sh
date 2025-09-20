#!/bin/bash
# Cache System Startup Hook
# This hook integrates the cache system into the Zo Computer startup process

# Source the cache initialization
if [ -f "/home/workspace/system_prep/init_cache.sh" ]; then
    echo "🔄 Initializing cache system..."
    source /home/workspace/system_prep/init_cache.sh
    echo "✅ Cache system ready"
fi

# Add cache system to PATH for easy access
export PATH="/home/workspace/system_prep:$PATH"

# Set up automatic file monitoring (if inotify-tools is available)
if command -v inotifywait >/dev/null 2>&1; then
    echo "📁 Setting up automatic file monitoring..."

    # Monitor for new temporary files and automatically cache them
    nohup inotifywait -m -r -e create,moved_to /home/workspace \
        --format '%w%f' \
        --include '\.(tmp|log|bak|backup)$|temp|cache|generated|output' \
        --exclude '__pycache__|\\.git' \
        | while read file; do
            if [ -f "$file" ]; then
                echo "📄 Auto-caching new file: $file"
                python3 /home/workspace/system_prep/cache_manager.py add --file "$file" --category auto >/dev/null 2>&1
            fi
        done &
fi

echo "🎯 Cache system fully integrated"