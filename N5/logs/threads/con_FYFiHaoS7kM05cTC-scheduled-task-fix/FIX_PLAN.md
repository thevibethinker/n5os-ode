# Meeting System Fix Plan - Complete Remediation

## Problems Identified

### 1. ❌ USER SERVICE: Wrong Detection Source
- **Service**: `meeting-detector` (svc_QYJiLcIIh2E)
- **Script**: `/home/workspace/N5/scripts/meeting_auto_processor.py`
- **Problem**: Scanning `/home/workspace/Document Inbox` (local filesystem)
- **Should Be**: Scanning Google Drive via API (`/Fireflies/Transcripts` folder)
- **Impact**: No new transcripts being detected since system switched to Google Drive

### 2. ❌ SCHEDULED TASK #1: Detection Task May Be Redundant
- **Task**: `afda82fa-7096-442a-9d65-24d831e3df4f` (💾 Gdrive Meeting Pull)
- **Frequency**: Every 30 minutes
- **Command**: `meeting-transcript-scan`
- **Problem**: Task exists but USER SERVICE is doing detection (incorrectly)
- **Decision Needed**: Disable service OR disable task (not both)

### 3. ❌ SCHEDULED TASK #2: Processing Uses Deprecated System
- **Task**: `4cb2fde2-2900-47d7-9040-fdf26cb4db62` (📝 Meeting Transcript Processing)
- **Frequency**: Every 10 minutes
- **Problem**: Instruction references deprecated `TemplateManager` 
- **Should Be**: Use `meeting-process` command with Registry System v1.5
- **Impact**: 144 pending transcripts not being processed

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DETECTION LAYER                          │
│  Scheduled Task (30 min) → Google Drive API → Queue        │
│  ✅ Use: meeting-transcript-scan command                    │
│  ❌ Stop: meeting-detector USER SERVICE (wrong source)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                          │
│  Scheduled Task (10 min) → Queue → Registry System         │
│  ✅ Use: meeting-process command (v5.1.0)                   │
│  ❌ Stop: TemplateManager (deprecated)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                             │
│  → Block files (N5/records/meetings/)                       │
│  → CRM profiles (Knowledge/crm/individuals/)                │
│  → Howie V-OS tags (B08, B26)                               │
└─────────────────────────────────────────────────────────────┘
```

## Fix Actions

### ACTION 1: Stop Wrong Detection Service ⚡ CRITICAL
```bash
# Delete the user service that's scanning wrong location
delete_user_service("svc_QYJiLcIIh2E")
```

### ACTION 2: Fix Detection Task Instruction
Verify scheduled task `afda82fa-...` uses Google Drive API correctly

### ACTION 3: Fix Processing Task Instruction ⚡ CRITICAL
Update task `4cb2fde2-...` to use Registry System

### ACTION 4: Process Backlog
After fixes, process 144 pending transcripts

---

## NEW INSTRUCTIONS

### Detection Task (30 min)
```
Execute command 'meeting-transcript-scan' from file 'N5/commands/meeting-transcript-scan.md'.

WORKFLOW:
1. Connect to Google Drive API
2. List files from folder: Fireflies/Transcripts (ID: 1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV)
3. Filter: Exclude files starting with [ZO-PROCESSED]
4. Check duplicates: Load existing gdrive_ids from:
   - N5/inbox/meeting_requests/*.json
   - N5/inbox/meeting_requests/processed/*.json
   - N5/records/meetings/*/_metadata.json
5. For each NEW file:
   - Download to N5/inbox/transcripts/{meeting_id}.txt
   - Parse filename for meeting details
   - Classify stakeholder type (internal/external)
   - Create request: N5/inbox/meeting_requests/{meeting_id}_request.json
6. Report: "✅ Detected {N} new | 📥 Downloaded {N} | 📋 Queued {N} | ⏭️  Skipped {N} duplicates"

CRITICAL: Use Google Drive API, NOT local filesystem.
```

### Processing Task (10 min)
```
Process ONE pending meeting transcript using Registry System v1.5.

CONSTRAINT: Process ONLY ONE transcript per invocation.

WORKFLOW:
1. Check N5/inbox/meeting_requests/ for pending *.json files
2. If empty: Exit with "✅ No pending requests"
3. If pending:
   - Select OLDEST request (FIFO)
   - Load request JSON: meeting_id, gdrive_id, classification, participants
   
4. Load Registry System:
   - Load: N5/prefs/block_type_registry.json (v1.5)
   - Read: N5/commands/meeting-process.md (v5.1.0)
   
5. Process Transcript:
   - Download from Google Drive if needed (use gdrive_id)
   - Save to: N5/inbox/transcripts/{meeting_id}.txt
   - Analyze transcript, determine stakeholder type
   - Generate 7 REQUIRED blocks:
     * B26 (Metadata with V-OS tags)
     * B01 (Detailed Recap)
     * B02 (Commitments)
     * B08 (Stakeholder Intelligence + CRM + Howie)
     * B21 (Key Moments: quotes + questions)
     * B31 (Stakeholder Research)
     * B25 (Deliverables + Follow-up Email)
   - Generate stakeholder-specific HIGH priority blocks
   - Generate CONDITIONAL blocks when triggered
   - Save to: N5/records/meetings/{meeting_id}/B##_BLOCKNAME.md
   
6. CRM Integration:
   - Create profile for: FOUNDER, INVESTOR, CUSTOMER, COMMUNITY, NETWORKING
   - Skip for: JOB_SEEKER
   - Path: Knowledge/crm/individuals/[firstname-lastname].md
   - Mark enrichment priority: HIGH/MEDIUM/LOW
   
7. Finalize:
   - Create _metadata.json
   - Mark Google Drive file: Add [ZO-PROCESSED] prefix
   - Move request: N5/inbox/meeting_requests/ → processed/
   - Log: "✅ {meeting_id} | Blocks: {N} | CRM: {created/skipped}"
   
8. STOP (next run processes next one)

ERROR HANDLING:
- Download fails → Log, move to failed/, continue
- Processing fails → Log error, move to failed/, continue
- No requests → Exit gracefully

RATIONALE: One-at-a-time prevents context overflow, ensures full attention per meeting, maintains FIFO order.
```

---

## Execution Order

1. ✅ Delete wrong user service (ACTION 1)
2. ✅ Update processing task instruction (ACTION 3)
3. ✅ Verify detection task (ACTION 2)
4. ✅ Test with one transcript manually
5. ✅ Let automated system process backlog
6. ✅ Monitor for 24 hours

---

**Ready to execute fixes.**
