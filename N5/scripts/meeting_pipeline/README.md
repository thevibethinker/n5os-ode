# Meeting Pipeline Architecture

## Google Drive Integration

The Google Drive fetch component **cannot run as a standalone subprocess** because it requires Zo's Google Drive integration tools.

### Current Architecture

**CORRECT** - Zo orchestrates directly:
1. Scheduled task triggers Zo
2. Zo uses  tool directly
3. Zo downloads, converts, and processes files

**INCORRECT** - Subprocess tries to call tools:
1. Script runs as subprocess
2. Tries to import pipedream_helper
3. Fails - subprocess cannot access Zo tools

### Files

-  - Legacy (broken, uses subprocess pattern)
- Pipeline should call Zo directly with orchestration instructions

### Solution Pattern

Instead of running scripts that try to access Google Drive, the scheduled task
should provide instructions for Zo to:
1. List files from Google Drive folder
2. Filter unprocessed (no [ZO-PROCESSED] prefix)
3. Download each file
4. Convert to markdown via pandoc
5. Move to Inbox
6. Mark processed in Drive
