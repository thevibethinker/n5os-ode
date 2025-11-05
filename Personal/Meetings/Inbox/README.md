---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---
# Meeting Transcript Inbox

**Status:** Ready for fresh transcripts from Google Drive bulk download

## Current State
- All corrupted files moved to `BACKUP_20251104_122007/`
- Inbox is clean and ready
- Waiting for V's bulk download from Google Drive

## Next Steps
1. V downloads all transcripts from Google Drive as `.docx` files
2. V uploads them here (or to a temp location)
3. Architect will:
   - Convert all `.docx` → `.md` using pandoc
   - Validate file integrity
   - Organize into proper structure
   - Queue for processing

## Expected File Format
- **From Fireflies:** `Name x Name-transcript-YYYY-MM-DDTHH-MM-SS.###Z.docx`
- **From Granola:** Google Docs with `[GRANOLA VERSION]` suffix
- **From Plaud Notes:** `.txt` files with timestamps

## Processing Pipeline
Once files are organized:
1. Detection → 2. Priority → 3. Block Selection → 4. AI Analysis → 5. Output to meeting folder

---
*Prepared for bulk import 2025-11-04*
