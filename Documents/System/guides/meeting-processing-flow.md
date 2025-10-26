# Meeting Processing Flow

**Version:** 3.0 (Google Drive Rename State Tracking)\
**Last Updated:** 2025-10-10\
**Status:** ✅ Active

---

## 🎯 Core Principle

**Process ONE transcript at a time, every 10 minutes, in FIFO order.**

**State Tracking:** Google Drive filenames are the source of truth. Files with `[ZO-PROCESSED]` prefix are skipped during detection.

This ensures:

- ✅ No context window overflow
- ✅ Full LLM attention to each transcript
- ✅ Predictable resource usage
- ✅ Clean error isolation
- ✅ Maintained arrival order

---

## 📊 Complete Workflow

### **Phase 1: Detection** (Every 30 Minutes)

**Scheduled Task:** "Process New Meeting Transcripts in FULL Mode"\
**Task ID:** `afda82fa-7096-442a-9d65-24d831e3df4f`\
**Frequency:** Every 30 minutes

**What Happens:**

```markdown
1. Scan Google Drive: Fireflies/Transcripts folder (ID: 1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV)
2. Detect new/unprocessed transcripts
3. For EACH new transcript:
   - Download to N5/inbox/transcripts/
   - Run Python classification (stakeholder type)
   - Create {meeting-id}_request.json in N5/inbox/meeting_requests/
4. All requests queued and ready
```

**Output:** Multiple request files created simultaneously if multiple transcripts arrived.

**Example:**

```markdown
N5/inbox/meeting_requests/
├── 2025-10-10_client-abc_request.json       (created 12:30:01)
├── 2025-10-10_internal-strategy_request.json (created 12:30:02)
└── 2025-10-10_partner-call_request.json      (created 12:30:03)
```

---

### **Phase 2: Processing** (Every 10 Minutes, ONE at a Time)

**Scheduled Task:** "Pending Meeting Requests Processing"\
**Task ID:** `4cb2fde2-2900-47d7-9040-fdf26cb4db62`\
**Frequency:** Every 10 minutes

**What Happens:**

```markdown
1. List pending requests in N5/inbox/meeting_requests/*.json
2. If no requests → Exit gracefully
3. If requests exist:
   a. Sort by filename (maintains FIFO by timestamp)
   b. Select OLDEST request
   c. Execute: command 'meeting-process' for THAT ONE transcript
   d. Zo processes directly:
      - Load transcript and classification
      - Extract content using native LLM
      - Generate all intelligence blocks
      - Save to N5/records/meetings/{meeting-id}/
   e. Move request to processed/ folder
   f. Rename Google Drive file: add [ZO-PROCESSED] prefix to original filename
   g. STOP (next run will process next one)
```

**Key Constraint:** **ONLY ONE** transcript processed per invocation.

---

## ⏱️ Timeline Example: 3 Transcripts Arrive

### **Scenario:**

Three transcripts uploaded to Google Drive at 12:00 PM

### **Timeline:**

| Time | Event | Action |
| --- | --- | --- |
| **12:00 PM** | 3 transcripts uploaded to Google Drive | Waiting for detection |
| **12:30 PM** | Auto-processor runs | Detects all 3, downloads, classifies, creates 3 requests |
| **12:30 PM** | Requests queued | `file A_request.json` , `file B_request.json` , `file C_request.json`  |
| **12:40 PM** | Processor Run #1 | Processes Request A (oldest), moves to processed/ |
| **12:50 PM** | Processor Run #2 | Processes Request B (next oldest), moves to processed/ |
| **1:00 PM** | Processor Run #3 | Processes Request C (last), moves to processed/ |
| **1:00 PM** | ✅ All complete | All 3 meetings fully processed |

**Total Duration:** 30 minutes from detection to full processing complete.

---

## 📂 Directory Structure & Flow

```markdown
CLOUD (Google Drive)
└── Fireflies Meetings/
    └── Transcripts/          ← 🎯 WATCHED FOLDER
        ├── Meeting A.docx    (uploaded 12:00)
        ├── Meeting B.docx    (uploaded 12:00)
        └── Meeting C.docx    (uploaded 12:00)

                    ↓
            Detection (12:30)
                    ↓

LOCAL (Zo Workspace)
├── N5/inbox/
│   ├── transcripts/          ← Downloaded staging
│   │   ├── meeting_a.txt
│   │   ├── meeting_b.txt
│   │   └── meeting_c.txt
│   │
│   └── meeting_requests/     ← Processing queue
│       ├── 2025-10-10_meeting-a_request.json  ← OLDEST (processed first)
│       ├── 2025-10-10_meeting-b_request.json
│       ├── 2025-10-10_meeting-c_request.json  ← NEWEST (processed last)
│       │
│       └── processed/        ← Completed requests moved here
│           ├── 2025-10-10_meeting-a_request.json ✅
│           ├── 2025-10-10_meeting-b_request.json ✅
│           └── 2025-10-10_meeting-c_request.json ✅

                    ↓
        Processing (one-at-a-time)
                    ↓

└── N5/records/meetings/      ← Final output
    ├── 2025-10-10_meeting-a/
    │   ├── REVIEW_FIRST.md
    │   ├── action-items.md
    │   ├── decisions.md
    │   ├── key-insights.md
    │   ├── debate-points.md
    │   ├── memo.md
    │   └── _metadata.json
    │
    ├── 2025-10-10_meeting-b/
    │   └── [same blocks]
    │
    └── 2025-10-10_meeting-c/
        └── [same blocks]
```

---

## 🔄 FIFO Ordering Mechanism

### **How Order is Maintained:**

1. **Detection phase:** Requests created with timestamps in filename

   - Format: `file YYYY-MM-DD_stakeholder-name_request.json` 
   - Creation time embedded in filesystem metadata

2. **Processing phase:**

   - List all `file *.json`  files in `N5/inbox/meeting_requests/`
   - Sort by filename (alphanumeric = chronological)
   - Select `[0]` (first/oldest)

3. **Result:** Strict FIFO processing order preserved

### **Example:**

```python
# Conceptual implementation
import os
import glob

requests = sorted(glob.glob("N5/inbox/meeting_requests/*.json"))
# Returns: ['2025-10-10_meeting-a_request.json', 
#           '2025-10-10_meeting-b_request.json',
#           '2025-10-10_meeting-c_request.json']

oldest_request = requests[0]  # Process this one only
# Process: 2025-10-10_meeting-a_request.json
# Stop. Next run will get meeting-b.
```

---

## 🎯 Processing Capacity

### **Current Throughput:**

- **Detection:** \~1-2 seconds per transcript (fast, no bottleneck)
- **Processing:** \~3-5 minutes per transcript (LLM extraction)
- **Frequency:** Every 10 minutes
- **Max throughput:** 6 transcripts per hour (one per 10-min cycle)

### **Queue Behavior:**

| Scenario | Result |
| --- | --- |
| 1 transcript arrives | Processed in next 10-min cycle (\~10 min wait) |
| 5 transcripts arrive | Processed over 50 minutes (one per cycle) |
| 10 transcripts arrive | Processed over 100 minutes (\~1.7 hours) |

### **Why This is Optimal:**

- **Context window safety:** Each transcript gets full attention without overflow risk
- **Quality over speed:** Deep extraction beats fast but shallow processing
- **Error isolation:** One failure doesn't cascade to others
- **Resource efficiency:** Predictable LLM usage, no spikes

---

## 🛡️ Error Handling

### **If Processing Fails for One Transcript:**

```markdown
Request A → ✅ Success (12:40) → processed/
Request B → ❌ Failed (12:50) → failed/ + error log
Request C → ✅ Success (1:00) → processed/
```

**What Happens:**

1. Failed request moved to `N5/inbox/meeting_requests/failed/`
2. Error logged to `N5/logs/meeting-process-errors.log`
3. Next request continues processing (no cascade failure)
4. Failed request can be manually retried (move back to main folder)

### **Error Log Format:**

```json
{
  "timestamp": "2025-10-10T12:50:00Z",
  "request_file": "2025-10-10_meeting-b_request.json",
  "error_type": "TranscriptParseError",
  "error_message": "Failed to extract participants from transcript",
  "transcript_path": "/home/workspace/N5/inbox/transcripts/meeting_b.txt",
  "stack_trace": "..."
}
```

---

## 🔍 Monitoring & Debugging

### **Check Queue Status:**

```bash
# Count pending requests
ls N5/inbox/meeting_requests/*.json 2>/dev/null | wc -l

# List pending (with timestamps)
ls -lht N5/inbox/meeting_requests/*.json

# Check processed
ls N5/inbox/meeting_requests/processed/ | wc -l

# Check failed
ls N5/inbox/meeting_requests/failed/ | wc -l
```

### **View Next Scheduled Runs:**

```markdown
list_scheduled_tasks
```

Look for:

- "Process New Meeting Transcripts in FULL Mode" (detection)
- "Pending Meeting Requests Processing" (processing)

### **Manual Processing:**

If you want to process immediately (bypass 10-min wait):

```markdown
command 'meeting-process'
```

This will process the oldest pending request right now.

---

## 📈 Scaling Considerations

### **Current Design Limits:**

- ✅ Handles 5-10 concurrent arrivals easily
- ✅ Queue buffers burst arrivals naturally
- ✅ Processing every 10 min = 6/hour throughput

### **If Higher Volume Needed:**

**Option 1:** Increase processing frequency

- Change from every 10 min → every 5 min
- Doubles throughput to 12/hour

**Option 2:** Parallel processing (careful!)

- Process 2-3 transcripts concurrently
- Requires coordination to avoid conflicts
- Context window risk increases

**Option 3:** Priority lanes

- Separate queues for internal vs external
- Process internal first (higher priority)

**Recommendation:** Current design (one-at-a-time, 10-min) is optimal for quality and reliability at current volume (\~100 transcripts over weeks).

---

## ✅ Architecture Verification

### **Key Principles Enforced:**

1. ✅ **One at a time:** Only one transcript processed per invocation
2. ✅ **FIFO ordering:** Oldest request processed first
3. ✅ **No subprocess calls:** Zo processes directly with native LLM
4. ✅ **Context window safety:** Full attention per transcript, no overflow
5. ✅ **Error isolation:** Failures don't cascade
6. ✅ **Queue-based:** Simple, reliable, inspectable

### **Success Criteria:**

- ✅ Sequential processing confirmed in command documentation
- ✅ Scheduled task updated with one-at-a-time constraint
- ✅ FIFO ordering mechanism documented
- ✅ Error handling preserves queue integrity
- ✅ No context window overflow risk

---

## 📚 Related Documentation

- `file N5/commands/meeting-process.md`  - Command implementation
- `file N5/docs/ARCHITECTURE_CORRECTION_COMPLETE.md`  - Architecture correction details
- `file N5/docs/stakeholder-classification-quickstart.md`  - Classification guide

---

## 🎉 Summary

**Meeting Processing Flow v3.0:**

- ✅ **Detection:** Every 30 min, queues ALL new transcripts
- ✅ **Processing:** Every 10 min, processes ONE transcript (oldest first)
- ✅ **Order:** Strict FIFO (first detected, first processed)
- ✅ **Safety:** No context window overflow, error isolation
- ✅ **Reliability:** Queue-based, inspectable, retryable

**Result:** Predictable, high-quality meeting intelligence extraction with guaranteed order and no resource contention.

---

**Last Updated:** 2025-10-10T23:45:00Z\
**Architecture Version:** 3.0 (Google Drive Rename State Tracking)