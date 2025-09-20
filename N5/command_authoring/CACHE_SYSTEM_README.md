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
