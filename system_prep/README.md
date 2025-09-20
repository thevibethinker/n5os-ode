# System Prep - Cache and Document Management

This system provides centralized management for temporary files and automated document distribution in the Zo Computer environment.

## Quick Start

1. **Initialize the system:**
   ```bash
   ./init_cache.sh
   ```

2. **Add a file to cache:**
   ```bash
   python3 cache_manager.py add --file /path/to/your/file.txt --category job_search
   ```

3. **List cached files:**
   ```bash
   python3 cache_manager.py list --category job_search
   ```

4. **Distribute files:**
   ```bash
   python3 distribute_docs.py distribute --category job_search
   ```

## Components

### Cache Manager (`cache_manager.py`)
- **add**: Add files to cache with category and metadata
- **list**: List cached files by category
- **get**: Retrieve full path to cached file
- **cleanup**: Remove old files (default: 7 days)
- **clear**: Clear all files in a category

### Document Distributor (`distribute_docs.py`)
- **distribute**: Send files to configured destinations
- **add-destination**: Add local folder destinations
- **add-rule**: Create distribution rules for categories
- **show-config**: Display current configuration

### Startup Script (`init_cache.sh`)
Runs automatically to initialize the cache system and clean up old files.

## Configuration

Edit `distribution_config.json` to configure:
- Local folder destinations
- Email settings (for email distribution)
- Distribution rules by category
- Auto-cleanup settings

## Categories

Common categories to use:
- `job_search`: Job applications and related documents
- `reports`: Generated reports and analytics
- `temporary`: Short-term files that can be auto-cleaned
- `documents`: General documents for distribution

## Benefits

- **Organization**: All temporary files in one place
- **Automation**: Auto-cleanup and distribution
- **Tracking**: Full metadata for all cached files
- **Flexibility**: Multiple destinations and categories
- **Clean Workspace**: Prevents clutter in main workspace

## Integration

Add this to your conversation startup:
```bash
source /home/workspace/system_prep/init_cache.sh
```

This will ensure the cache system is ready for each conversation.