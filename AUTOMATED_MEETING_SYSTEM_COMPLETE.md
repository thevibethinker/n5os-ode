# Automated Meeting Processing System - Complete Setup

## ✅ System Status: ACTIVE

**Frequency**: Every hour at :00 minutes  
**Next Run**: Check https://va.zo.computer/schedule  
**Model**: Claude Sonnet 4 (for high-quality analysis)  
**Processing Log**: `file 'N5/logs/meeting-processing/processed_transcripts.jsonl'`

---

## System Components

### 1. Scheduled Task ✅
- **Location**: https://va.zo.computer/schedule
- **Frequency**: Hourly (on the hour)
- **Model**: Claude Sonnet 4 for comprehensive analysis
- **Mode**: FULL processing (all intelligence blocks)

### 2. Duplicate Detection ✅
- **Method**: Date + Stakeholder matching
- **Verification**: SHA256 checksums
- **Script**: `file 'N5/scripts/meeting_duplicate_detector.py'`
- **Logging**: Duplicates logged with `status: 'duplicate_skipped'`

### 3. Processing Log ✅
- **Location**: `file 'N5/logs/meeting-processing/processed_transcripts.jsonl'`
- **Format**: JSONL (one record per line)
- **Schema**: Compatible with N5 JSONL conventions
- **Initialized**: ✅ (Alex Caveny meeting already logged)

### 4. N5 Integration ✅
- **Schema Compliance**: `file 'N5/schemas/meeting-metadata.schema.json'`
- **Workspace Organization**: Per `file 'Documents/N5.md'` structure
- **Output Location**: `file 'Careerspan/Meetings/'`
- **Commands Registry**: Updated with `meeting-auto-process`

---

## How Duplicate Detection Works

### Fireflies Duplicate Problem
Fireflies sometimes stores 2+ versions of the same meeting (e.g., processing issues, re-uploads).

### Detection Logic
```
For each transcript file:
1. Extract date from filename (YYYY-MM-DD)
2. Extract stakeholder name (first name)
3. Create signature: "{date}_{stakeholder}"
4. Check if signature exists in processed log
5. If exists + different file_id → DUPLICATE
6. Log duplicate, skip processing
```

### Example
```
File 1: "Alex x Vrijen - Coaching-2025-10-09T18-06-05.docx"
  → Signature: "2025-10-09_alex"
  → Status: Processed ✅

File 2: "Alex x Vrijen - Coaching-2025-10-09T18-12-30.docx"
  → Signature: "2025-10-09_alex"
  → Status: DUPLICATE (skipped) ⚠️
  → Logged as: duplicate_of: [file1_id]
```

### SHA256 Verification
- Each transcript gets SHA256 checksum
- Stored in `_metadata.json` and processing log
- Additional layer to verify content uniqueness

---

## Processing Workflow

### Every Hour:
```
1. Check Google Drive (Fireflies/Transcripts)
2. Load processing log
3. For each file:
   a. Extract date + stakeholder signature
   b. Check against processed log
   c. If duplicate → log and skip
   d. If new → download and process
4. Generate full intelligence package
5. Update processing log
6. Update _metadata.json with checksums
```

### Quality Standards:
- **FULL mode** - All intelligence blocks generated
- **Real analysis** - Claude Sonnet 4 doing actual LLM work
- **N5 compliance** - Following all schemas and conventions
- **Same depth** - As Alex Caveny 2025-10-09 reference

---

## Generated Files

For each processed transcript:

```
Careerspan/Meetings/YYYY-MM-DD_HHMM_type_stakeholder/
├── _metadata.json           # Meeting metadata (N5 schema compliant)
├── REVIEW_FIRST.md          # Executive dashboard - START HERE
├── action-items.md          # 10-20 specific action items
├── decisions.md             # 5-8 categorized decisions
├── key-insights.md          # 10-15 strategic insights
├── stakeholder-profile.md   # Comprehensive participant profile
├── follow-up-email.md       # Draft follow-up email
└── transcript.txt           # Full transcript copy
```

### _metadata.json Structure
```json
{
  "meeting_id": "abc123",
  "date": "2025-10-09",
  "meeting_type": ["coaching", "advisory"],
  "stakeholder_primary": "alex-caveny",
  "transcript_source": {
    "type": "google_drive",
    "identifier": "1tpIPt...",
    "sha256": "a3b5c7...",
    "size_bytes": 57922,
    "line_count": 631
  },
  "processing": {
    "version": "auto-v1",
    "mode": "full",
    "timestamp": "2025-10-09T19:30:00Z",
    "blocks_generated": 7
  },
  "intelligence": {
    "action_items_count": 14,
    "decisions_count": 6,
    "insights_count": 12
  }
}
```

---

## N5 System Integration

### Follows N5 Structure:
✅ **Workspace Organization** - Output to `Careerspan/Meetings/`  
✅ **Schema Compliance** - Uses `meeting-metadata.schema.json`  
✅ **JSONL Conventions** - Processing log format  
✅ **Commands Registry** - `meeting-auto-process` registered  
✅ **No Conflicts** - Doesn't interfere with existing N5 commands

### Synced With:
- `file 'Documents/N5.md'` - System architecture
- `file 'N5/schemas/meeting-metadata.schema.json'` - Metadata format
- `file 'N5/config/commands.jsonl'` - Command registry
- `file 'N5/prefs/prefs.md'` - System preferences

---

## Processing Log Format

### Record Types:

**Completed Processing:**
```json
{
  "file_id": "1tpIPt-xvE6sLP7...",
  "file_name": "Alex x Vrijen - Coaching-2025-10-09...",
  "download_path": "/home/workspace/Documents/Meetings/...",
  "discovered_at": "2025-10-09T18:56:00Z",
  "processed_at": "2025-10-09T19:30:00Z",
  "output_dir": "/home/workspace/Careerspan/Meetings/2025-10-09_Alex-Caveny-Coaching",
  "status": "completed",
  "sha256": "a3b5c7d...",
  "duplicate_checked": true
}
```

**Duplicate Skipped:**
```json
{
  "file_id": "1xyz...",
  "file_name": "Alex x Vrijen - Coaching-2025-10-09T18-12-30...",
  "status": "duplicate_skipped",
  "duplicate_of": "1tpIPt-xvE6sLP7...",
  "discovered_at": "2025-10-09T19:45:00Z",
  "duplicate_checked": true
}
```

---

## Monitoring & Verification

### Check System Status
```bash
# View all processed transcripts
cat N5/logs/meeting-processing/processed_transcripts.jsonl | jq .

# Count total processed
wc -l N5/logs/meeting-processing/processed_transcripts.jsonl

# Count duplicates found
grep 'duplicate_skipped' N5/logs/meeting-processing/processed_transcripts.jsonl | wc -l

# View recent processing
tail -10 N5/logs/meeting-processing/processed_transcripts.jsonl | jq .

# Check for specific stakeholder
grep -i "alex" N5/logs/meeting-processing/processed_transcripts.jsonl | jq .
```

### Test Duplicate Detection
```bash
# Test a filename
python3 N5/scripts/meeting_duplicate_detector.py "Alex x Vrijen - 2025-10-09.docx"
```

### View Meeting Folders
```bash
# List all processed meetings
ls -lt Careerspan/Meetings/

# Count total meetings
ls -1 Careerspan/Meetings/ | wc -l

# View specific meeting
ls -lh Careerspan/Meetings/2025-10-09_Alex-Caveny-Coaching/
```

---

## Manual Operations

### Force Process Now (Don't Wait)
```
Process any new meeting transcripts from Google Drive now
```

### Check for Duplicates Manually
```
Check for duplicate transcripts in the processing log
```

### Reprocess a Meeting
1. Remove entry from processing log
2. Delete output folder
3. Wait for next hourly run or trigger manually

### View Scheduled Task
Visit: https://va.zo.computer/schedule

---

## Quality Guarantees

### ✅ Every Processed Meeting Includes:

1. **Full Transcript Analysis**
   - No truncation - entire conversation analyzed
   - All timestamps and speakers preserved

2. **Specific Action Items** (10-20 items)
   - Owner assignments
   - Deadlines (calculated from meeting date)
   - Priority levels
   - Context and dependencies

3. **Strategic Decisions** (5-8 decisions)
   - Categorized: Strategic, Process, Product
   - Rationale documented
   - Impact analysis
   - Decision makers identified

4. **Key Insights** (10-15 insights)
   - Hiring market dynamics
   - Founder wellness themes
   - Product strategy observations
   - Relationship intelligence

5. **Stakeholder Profile**
   - Background and experience
   - Communication style
   - Pain points and interests
   - Opportunities and network
   - How to work with them effectively

6. **Follow-up Email Draft**
   - Specific next steps
   - Clear asks
   - Relationship moves
   - Timeline commitments

7. **Executive Dashboard**
   - Priority actions (next 48hrs)
   - Key takeaways
   - Strategic questions
   - Quick links to all files

---

## Architecture

### Why This Approach Works

**Problem Solved**: Stub LLM clients return placeholder text

**Solution**: Scheduled task triggers real LLM (Claude Sonnet 4)
- I do actual analysis (not stubs)
- Full transcript reading
- Comprehensive intelligence generation
- N5 schema compliance

### The Flow
```
Every hour at :00
    ↓
Scheduled task (Sonnet 4)
    ↓
Check Google Drive
    ↓
Load processing log
    ↓
For each file:
  - Check duplicates ✅
  - Download if new
  - Generate full intelligence
  - Update log with checksums
    ↓
Done until next hour
```

---

## File Locations

| Component | Path |
|-----------|------|
| Processing Log | `file 'N5/logs/meeting-processing/processed_transcripts.jsonl'` |
| Duplicate Detector | `file 'N5/scripts/meeting_duplicate_detector.py'` |
| Staging Area | `file 'Documents/Meetings/_staging/'` |
| Output Folders | `file 'Careerspan/Meetings/'` |
| Command Doc | `file 'N5/commands/meeting-auto-process.md'` |
| Metadata Schema | `file 'N5/schemas/meeting-metadata.schema.json'` |
| System Guide | `file 'N5/docs/meeting-auto-processing-guide.md'` |

---

## Testing

### Upload Test Transcript
1. Add new .docx to Google Drive: `Fireflies > Transcripts`
2. Wait up to 1 hour (or trigger manually)
3. Check processing log for new entry
4. Verify meeting folder created
5. Review REVIEW_FIRST.md for quality

### Upload Duplicate
1. Upload same meeting twice to Google Drive
2. First will process normally
3. Second will be logged as `duplicate_skipped`
4. Check log to verify duplicate detection

---

## Troubleshooting

### No Transcripts Being Processed
**Check**:
- Google Drive connection active
- Scheduled task enabled (https://va.zo.computer/schedule)
- Processing log accessible
- Files in correct Google Drive folder

### Duplicate Not Detected
**Check**:
- Filename has date (YYYY-MM-DD format)
- Filename has stakeholder name (first name)
- Processing log has original entry
- Run duplicate detector script manually

### Processing Quality Issues
**Check**:
- Task using Claude Sonnet 4 (not mini model)
- Mode set to FULL (not essential/quick)
- All 7 blocks being generated
- _metadata.json created

---

## Current Status

✅ **System Active** - Running hourly  
✅ **Duplicate Detection** - Fully implemented  
✅ **N5 Integration** - Schema compliant  
✅ **Processing Log** - Initialized with Alex meeting  
✅ **Quality Standards** - FULL mode, Sonnet 4  
✅ **Documentation** - Complete  

**Next Automatic Run**: Check https://va.zo.computer/schedule

**Already Processed**: 1 transcript (Alex Caveny 2025-10-09)

**System Ready**: Upload new transcripts to Google Drive and they'll be automatically processed!

---

## Key Principles

1. **Never Reprocesses** - Log + duplicate detection prevent duplicates
2. **Runs Automatically** - No manual intervention needed
3. **Real Analysis** - Claude Sonnet 4 does actual LLM work
4. **Full Transparency** - All operations logged with checksums
5. **N5 Compliant** - Follows all schemas and conventions
6. **Safe & Idempotent** - Can run multiple times without issues
