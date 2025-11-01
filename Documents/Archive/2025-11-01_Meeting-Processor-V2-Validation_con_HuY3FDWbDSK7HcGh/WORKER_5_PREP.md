# Worker 5 Prep - Metadata Updater

**Prepared:** 2025-11-01 07:01 ET  
**Status:** Ready to build  
**Complexity:** Low (simple JSON I/O)

---

## Objective

Build Worker 5 (Metadata Updater) - the final worker in the meeting-processor-v2 pipeline.

---

## Scope

Worker 5 updates metadata after successful processing:
1. Creates  in meeting folder
2. Appends entry to global registry ()
3. Generates W5_update_report.json

---

## Key Requirements (from spec)

### Inputs
- : Production meeting directory (from Worker 4)
- : Meeting identifier
- : Google Drive file ID

### Outputs
1. **_metadata.json** in meeting folder
   - meeting_id, classification, gdrive_id, status
   - blocks_generated (list), transcript_size_bytes
   - processed_at (ISO timestamp), processor_version

2. **Registry entry** (JSONL append)
   - Path: /home/workspace/N5/data/meeting_gdrive_registry.jsonl
   - Format: One-line JSON per meeting

3. **W5_update_report.json**
   - metadata_created, registry_updated, warnings

### Error Handling
**Non-critical worker:** Errors log warnings but don't fail pipeline
- Metadata write fails → Warning (meeting still usable)
- Registry append fails → Warning (can be added manually)

---

## Implementation Strategy

### Simple & Straightforward
1. Scan meeting folder for generated blocks
2. Get transcript size
3. Create metadata dict → write JSON
4. Create registry entry → append to JSONL
5. Generate report

### Tech Choices
- **Method:** Pure Python (no bash needed for JSON)
- **Libraries:** json, pathlib, datetime
- **Validation:** Check file exists, valid JSON structure

---

## Complexity Assessment

**Low Complexity:**
- Simple JSON I/O operations
- No external dependencies
- Straightforward error handling
- No content transformation needed

**Estimated Time:** 20-30 minutes to build + test

---

## Design Principles

- **Simple Over Easy:** Direct JSON writes, no over-engineering
- **Flow Over Pools:** Append to registry (streaming), not in-memory batch
- **Graceful Degradation:** Non-fatal errors (warning logs, continue)
- **P18 (Verify State):** Check metadata file created and valid

---

## Test Plan

1. **Success case:** Create metadata + registry entry
2. **Missing blocks:** Handle gracefully (empty list)
3. **Registry append:** Verify JSONL format
4. **Report generation:** Validate structure

---

## Status

**Spec:** ✅ Complete and clear
**Design:** ✅ Straightforward
**Ready:** ✅ Can proceed with build

**Next Action:** Activate Builder mode and create Worker 5

---

*Prepared: 2025-11-01 07:01:05 ET*
