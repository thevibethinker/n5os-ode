# Script Consolidation Archive - Phase B

**Date**: 2025-11-15T10:00:31Z  
**Reason**: Consolidated 6 duplicate detection scripts into detect_meeting_duplicates.py  
**Orchestrator**: con_wkDPnaagydefZ4QH  
**Worker**: Worker 02 (con_jVhSit901SkcXhgH)

## Archived Scripts

These scripts were replaced by `detect_meeting_duplicates.py` (canonical version):

1. **cleanup_duplicate_meeting_files.py** (47 lines) - Basic filesystem cleanup for intelligence files
   - Purpose: Cleaned duplicate lowercase intelligence files, kept B## and UPPERCASE versions
   - Merged into canonical: Intelligence file pattern detection

2. **cleanup_duplicate_requests.py** (63 lines) - Request queue deduplication  
   - Purpose: Removed AI requests for already processed meetings
   - Status: Archived (specific use case, kept for reference)

3. **deduplicate_meetings.py** (74 lines) - Simple scanner
   - Purpose: LLM-based semantic meeting deduplication (incomplete)
   - Status: Archived (incomplete implementation)

4. **duplicate_scanner.py** (325 lines) - Comprehensive filesystem scanner
   - Purpose: Multi-strategy duplicate detection (hash, names, orphans)
   - Merged into canonical: BASE SCRIPT - core logic used for canonical implementation

5. **meeting_ai_deduplicator.py** (303 lines) - AI-based similarity detection
   - Purpose: AI-powered semantic meeting comparison
   - Status: Archived (overlaps with meeting_duplicate_manager.py canonical tool)

6. **meeting_registry_deduplicate.py** (117 lines) - Registry-focused deduplication
   - Purpose: Removed duplicate entries from meeting registry
   - Merged into canonical: Registry deduplication logic

## Consolidation Strategy

**Base Script**: duplicate_scanner.py (most comprehensive)
**Features Merged**:
- Intelligence file patterns from cleanup_duplicate_meeting_files.py
- Registry checking from meeting_registry_deduplicate.py
- Enhanced with meeting-specific context

**NOT Merged**: meeting_ai_deduplicator.py (redundant with existing canonical meeting_duplicate_manager.py)

## Migration

Use `detect_meeting_duplicates.py` instead. See:
- `/home/workspace/N5/scripts/detect_meeting_duplicates.py --help`
- `/home/workspace/N5/docs/duplicate-detection.md`

## Commands

```bash
# Scan for duplicates
python3 N5/scripts/detect_meeting_duplicates.py scan

# Intelligence files only
python3 N5/scripts/detect_meeting_duplicates.py scan --intelligence

# Registry only
python3 N5/scripts/detect_meeting_duplicates.py scan --registry

# Cleanup (dry run)
python3 N5/scripts/detect_meeting_duplicates.py cleanup --dry-run

# Cleanup (execute)
python3 N5/scripts/detect_meeting_duplicates.py cleanup
```

## Rollback

If needed, restore from this archive:
```bash
cd /home/workspace/N5/scripts
cp "$ARCHIVE_DIR"/*.py ./
rm -f detect_meeting_duplicates.py
```
