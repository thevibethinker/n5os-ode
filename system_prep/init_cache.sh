#!/bin/bash
# Cache System Initialization Script
# This script initializes the cache system at the start of conversations

CACHE_DIR="/home/workspace/system_prep/cache"
METADATA_FILE="$CACHE_DIR/metadata.json"
LOG_FILE="$CACHE_DIR/init.log"

# Create cache directory if it doesn't exist
mkdir -p "$CACHE_DIR"

# Log initialization
echo "$(date): Initializing cache system" >> "$LOG_FILE"

# Create initial metadata file if it doesn't exist
if [ ! -f "$METADATA_FILE" ]; then
    echo "Creating initial cache metadata..."
    cat > "$METADATA_FILE" << EOF
{
  "files": {},
  "created_at": "$(date -Iseconds)",
  "system_info": "Zo Computer Cache System v1.0"
}
EOF
    echo "$(date): Initial metadata created" >> "$LOG_FILE"
fi

# Clean up old files (older than 7 days)
echo "Cleaning up old cache files..."
python3 /home/workspace/system_prep/cache_manager.py cleanup --days 7 >> "$LOG_FILE" 2>&1

# Log cache status
CACHE_COUNT=$(find "$CACHE_DIR" -type f -name "*.json" -o -name "*.md" -o -name "*.txt" | wc -l)
echo "$(date): Cache system ready. $CACHE_COUNT files in cache." >> "$LOG_FILE"

echo "Cache system initialized successfully."