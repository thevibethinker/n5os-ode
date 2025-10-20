# Meeting Intelligence System - Impact Map

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  MEETING INTELLIGENCE SYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: DETECTION & INGESTION
├── Scheduled Task: "💾 Gdrive Meeting Pull" (every 30 min)
│   ├── Scans: Google Drive /Fireflies/Transcripts folder
│   ├── Command: meeting-transcript-scan
│   ├── Output: N5/inbox/meeting_requests/*.json
│   └── Status: 🔴 BROKEN (scanning wrong location)

PHASE 2: PROCESSING
├── Scheduled Task: "📝 Meeting Transcript Processing" (every 10 min)
│   ├── Reads: N5/inbox/meeting_requests/*.json
│   ├── Command: meeting-process (v5.1.0)
│   ├── Registry: N5/prefs/block_type_registry.json (v1.5)
│   ├── Output: N5/records/meetings/{meeting_id}/B##_*.md
│   └── Status: 🔴 BROKEN (using deprecated system)

PHASE 3: CRM INTEGRATION
├── Creates: Knowledge/crm/individuals/*.md
├── Triggers: Enrichment workflow
└── Status: ❌ NOT RUNNING (depends on Phase 2)

PHASE 4: HOWIE HARMONIZATION
├── Generates: V-OS tags [LD-XXX] [GPT-X] [A-X]
├── Updates: B08 and B26 blocks
└── Status: ❌ NOT RUNNING (depends on Phase 2)
```

---

## Component Inventory

### 1. SCHEDULED TASKS
| ID | Title | Frequency | Status | Issues |
|----|-------|-----------|--------|--------|
| `afda82fa-...` | 💾 Gdrive Meeting Pull | 30 min | 🔴 BROKEN | Scanning wrong path |
| `4cb2fde2-...` | 📝 Meeting Transcript Processing | 10 min | 🔴 BROKEN | Using deprecated system |

### 2. COMMANDS
| File | Version | Status | Issues |
|------|---------|--------|--------|
| `N5/commands/meeting-transcript-scan.md` | Current | ✅ OK | None |
| `N5/commands/meeting-process.md` | v5.1.0 | ✅ OK | None |

### 3. SCRIPTS
| File | Status | Usage | Issues |
|------|--------|-------|--------|
| `N5/scripts/meeting_intelligence_orchestrator.py` | ⚠️ DEPRECATED | Referenced by broken task | Should not be used |
| `N5/scripts/gdrive_meeting_detector.py` | 🔴 BROKEN | Detection task | Scanning wrong path |
| `N5/scripts/meeting_core_generator.py` | ✅ OK | Registry system | Working |
| `N5/scripts/n5_meeting_transcript_scanner.py` | ⚠️ UNKNOWN | Unclear usage | Need to verify |

### 4. CONFIGURATION FILES
| File | Version | Status | Issues |
|------|---------|--------|--------|
| `N5/prefs/block_type_registry.json` | v1.5 | ✅ OK | None |
| `N5/commands.md` | Current | ❓ CHECK | May need updates |
| `N5/config/commands.jsonl` | Current | ❓ CHECK | May need updates |

### 5. DIRECTORIES
| Path | Purpose | Status | Pending Count |
|------|---------|--------|---------------|
| `N5/inbox/meeting_requests/` | Pending requests | 🔴 FULL | 144 files |
| `N5/inbox/meeting_requests/processed/` | Completed | ✅ OK | Archive |
| `N5/inbox/meeting_requests/failed/` | Errors | ✅ OK | Error tracking |
| `N5/inbox/transcripts/` | Downloaded transcripts | ❓ CHECK | Need to verify |
| `N5/records/meetings/` | Processed outputs | ✅ OK | Block storage |
| `Knowledge/crm/individuals/` | CRM profiles | ✅ OK | Profile storage |

### 6. EXTERNAL INTEGRATIONS
| Service | Purpose | Status | Issues |
|---------|---------|--------|--------|
| Google Drive API | Transcript source | ✅ OK | None |
| Gmail API | Email scanning | ✅ OK | None |
| Google Calendar API | Meeting prep | ✅ OK | None |

---

## Root Causes Identified

### 🔴 ISSUE 1: Detection Task Scanning Wrong Path
**File**: Script invoked by scheduled task `afda82fa-...`  
**Problem**: Scanning `/home/workspace/Document Inbox` instead of Google Drive  
**Impact**: No new transcripts detected, queue not growing  
**Fix Required**: Update script or task to use Google Drive API

### 🔴 ISSUE 2: Processing Task Using Deprecated System
**Task**: `4cb2fde2-2900-47d7-9040-fdf26cb4db62`  
**Problem**: References `TemplateManager` which is deprecated  
**Impact**: Processing fails silently, 144 pending requests idle  
**Fix Required**: Update task instruction to use `meeting-process` command

### 🔴 ISSUE 3: 144 Pending Requests Accumulating
**Location**: `N5/inbox/meeting_requests/`  
**Problem**: No processing occurring since system broke  
**Impact**: All meeting intelligence delayed  
**Fix Required**: Fix Issues 1 & 2, then process backlog

---

## Dependencies & Flow

```
Google Drive                         User Services
     ↓                                    ↓
[Detection Task] ──────────────→ meeting_requests/*.json
     ↓                                    ↓
     └─────────────────────────→ [Processing Task]
                                          ↓
                                    ┌─────┴─────┐
                                    ↓           ↓
                            Block Files      CRM Profiles
                         (N5/records/)   (Knowledge/crm/)
                                    ↓
                              Howie Tags
                            (V-OS system)
```

---

## Fix Strategy

### Phase 1: Update Scheduled Tasks ✋ PRIORITY
1. Fix detection task instruction (Google Drive API)
2. Fix processing task instruction (Registry System)
3. Verify task execution logs

### Phase 2: Verify Scripts & Commands
1. Check if scripts are properly invoked
2. Verify Registry System components
3. Test manual execution

### Phase 3: Process Backlog
1. Test with 1 transcript
2. Process oldest 10 transcripts
3. Bulk process remaining 134

### Phase 4: Monitoring
1. Set up error tracking
2. Verify CRM integration
3. Confirm Howie tags generated

---

## Files Requiring Changes

### 🔧 IMMEDIATE CHANGES NEEDED
1. **Scheduled Task `4cb2fde2-2900-47d7-9040-fdf26cb4db62`** - Update instruction
2. **Scheduled Task `afda82fa-7096-442a-9d65-24d831e3df4f`** - Verify correct command
3. **`N5/scripts/gdrive_meeting_detector.py`** - Fix scan path (if this is what's running)

### 📋 VERIFICATION NEEDED
1. **`N5/config/commands.jsonl`** - Ensure meeting-process registered
2. **`N5/commands.md`** - Ensure documentation current
3. **`N5/scripts/n5_meeting_transcript_scanner.py`** - Check usage

### 📚 DOCUMENTATION TO UPDATE
1. **Implementation summary** - Document fixes
2. **Meeting system README** - Update workflow diagrams
3. **Conversation log** - Record what was fixed

---

## Testing Plan

### Test 1: Manual Detection
```bash
# Verify Google Drive scan works
python3 N5/scripts/n5_meeting_transcript_scanner.py
# Expected: New files detected from Google Drive
```

### Test 2: Manual Processing (Single)
```bash
# Process oldest pending request
# Expected: Blocks generated, CRM created, request moved to processed/
```

### Test 3: Scheduled Task Execution
```bash
# Wait for next scheduled run
# Check logs in /dev/shm/
# Verify conversation workspace has output
```

---

## Success Metrics

- ✅ Detection task finds new transcripts from Google Drive
- ✅ Processing task generates 7 REQUIRED blocks per meeting
- ✅ CRM profiles created for eligible stakeholders
- ✅ Howie V-OS tags generated in B08 and B26
- ✅ Pending requests move to processed/
- ✅ Google Drive files marked [ZO-PROCESSED]
- ✅ 144 backlog transcripts processed within 24 hours

---

**Next Step**: Execute fix strategy starting with Phase 1
