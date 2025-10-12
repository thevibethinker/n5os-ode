# Corrected Scheduled Task Instruction

## Task: Meeting Transcript Processing
**Event ID**: `4cb2fde2-2900-47d7-9040-fdf26cb4db62`  
**Frequency**: Every 10 minutes  
**Model**: `anthropic:claude-sonnet-4-5-20250929`

---

## NEW INSTRUCTION (Corrected)

```
Process ONE pending meeting transcript from N5/inbox/meeting_requests/ using the modern Registry System.

CRITICAL CONSTRAINT: Process ONLY ONE transcript per invocation to avoid context window issues.

WORKFLOW:

1. Check N5/inbox/meeting_requests/ for pending *.json files
2. If no pending requests exist, exit gracefully with: "✅ No pending meeting requests to process"
3. If pending requests exist:
   - Select the OLDEST request file (by filename timestamp) to maintain FIFO ordering
   - Load the request JSON to get: meeting_id, gdrive_id, gdrive_link, classification, participants
   
4. Execute the 'meeting-process' command (v5.1.0) for this meeting:
   - Load N5/prefs/block_type_registry.json (v1.5+)
   - Download transcript from Google Drive using gdrive_id (if not already downloaded)
   - Save transcript to N5/inbox/transcripts/{meeting_id}.txt
   - Analyze transcript using Registry System workflow
   - Determine stakeholder type (FOUNDER, INVESTOR, CUSTOMER, NETWORKING, COMMUNITY, etc.)
   - Generate all REQUIRED blocks (7 blocks: B26, B01, B02, B08, B21, B31, B25)
   - Generate stakeholder-appropriate HIGH priority blocks
   - Generate CONDITIONAL blocks only when triggered
   - Apply CRM integration for eligible stakeholders (create profiles in Knowledge/crm/individuals/)
   - Generate Howie V-OS tags for scheduling harmonization
   - Save all blocks to N5/records/meetings/{meeting_id}/B##_BLOCKNAME.md
   - Create _metadata.json with full processing context
   
5. Post-processing:
   - Mark Google Drive file as processed by adding [ZO-PROCESSED] prefix to filename
   - Move request from N5/inbox/meeting_requests/ to N5/inbox/meeting_requests/processed/
   - Log completion: "✅ Processed: {meeting_id} | Blocks: {count} | CRM: {created/skipped}"
   
6. STOP (next run in 10 minutes will process the next one)

REGISTRY SYSTEM BLOCKS (v1.5):
- REQUIRED (7): B26 (Metadata), B01 (Recap), B02 (Commitments), B08 (Stakeholder Intelligence), B21 (Key Moments), B31 (Stakeholder Research), B25 (Deliverables + Follow-up Email)
- HIGH PRIORITY: Varies by stakeholder type (see file 'N5/commands/meeting-process.md' for details)
- CONDITIONAL: B06 (Pilot), B11 (Metrics), B15 (Stakeholder Map) - only when triggered

CRM INTEGRATION:
- Auto-create profiles for: FOUNDER, INVESTOR, CUSTOMER, COMMUNITY, NETWORKING
- Skip for: JOB_SEEKER (recruitment workflow)
- Path: Knowledge/crm/individuals/[firstname-lastname].md
- Mark enrichment priority: HIGH/MEDIUM/LOW

HOWIE INTEGRATION:
- Generate V-OS tags for all stakeholders: [LD-XXX] [GPT-X] [A-X]
- Include in B08 (Stakeholder Intelligence) and B26 (Metadata)

ERROR HANDLING:
- If transcript download fails: Log error, move request to failed/, continue
- If processing fails: Log error with stack trace, move request to failed/, continue
- If all files processed: Exit gracefully

RATIONALE: Processing one transcript at a time ensures no context window overflow, full attention to each meeting, predictable resource usage, clean error isolation, and FIFO ordering preservation.
```

---

## What Changed

### OLD (Broken):
- ❌ References deprecated `TemplateManager` class
- ❌ Uses old template-based approach
- ❌ Python script invocation model
- ❌ No CRM integration
- ❌ No Howie harmonization

### NEW (Working):
- ✅ Uses `meeting-process` command (v5.1.0)
- ✅ Registry System (v1.5) with 15 blocks
- ✅ AI-driven processing (guidance-based, not templates)
- ✅ CRM integration for eligible stakeholders
- ✅ Howie V-OS tag generation
- ✅ Modern workflow with proper error handling

---

## How to Apply This Fix

Use the `edit_scheduled_task` tool with the new instruction above.
