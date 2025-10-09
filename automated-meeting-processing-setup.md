# Automated Meeting Processing System

## ✅ System Deployed

I've set up an automated system that will process new meeting transcripts from Google Drive every hour.

---

## How It Works

### Every Hour (on the hour):
1. **I check Google Drive** (Fireflies > Transcripts folder) for new files
2. **Compare against processing log** to find unprocessed transcripts
3. **Download new transcripts** to staging area
4. **Generate full meeting intelligence** (action items, decisions, insights, stakeholder profiles, follow-ups)
5. **Update processing log** with completion status

### Quality Guarantee:
- **Real LLM analysis** (me doing manual work, not stub placeholders)
- **Full transcript reading** - I analyze the entire conversation
- **Same quality** as the Alex Caveny meeting processing you just reviewed

---

## Scheduled Task

**Status**: ✅ Active  
**Frequency**: Every hour at :00 minutes  
**Next Run**: Today at 3:00 PM (and every hour after)

View your scheduled tasks at: https://va.zo.computer/schedule

---

## Processing Log

**Location**: `file 'N5/logs/meeting-processing/processed_transcripts.jsonl'`

Each line tracks one processed transcript:
```json
{
  "file_id": "1tpIPt...",
  "file_name": "Alex x Vrijen - Wisdom Partners...",
  "download_path": "/home/workspace/Documents/Meetings/...",
  "discovered_at": "2025-10-09T18:56:00Z",
  "processed_at": "2025-10-09T19:30:00Z",
  "output_dir": "/home/workspace/Careerspan/Meetings/...",
  "status": "completed"
}
```

**Current Status**: 1 transcript already processed (Alex Caveny 2025-10-09)

---

## What Gets Generated

For each new transcript, I create a complete meeting folder with:

### Core Intelligence
- **`action-items.md`** - Specific action items with owners, deadlines, priorities
- **`decisions.md`** - Key decisions categorized by type
- **`key-insights.md`** - Strategic insights on hiring, product, personal topics
- **`stakeholder-profile.md`** - Comprehensive participant profile
- **`follow-up-email.md`** - Draft follow-up with next steps
- **`REVIEW_FIRST.md`** - Executive dashboard summary
- **`transcript.txt`** - Full transcript copy

### Output Location
`file 'Careerspan/Meetings/YYYY-MM-DD_HHMM_type_stakeholder/'`

Example: `file 'Careerspan/Meetings/2025-10-09_Alex-Caveny-Coaching'`

---

## Manual Commands

### Check Processing Status
```bash
# View all processed transcripts
cat N5/logs/meeting-processing/processed_transcripts.jsonl | jq .

# Count total processed
wc -l N5/logs/meeting-processing/processed_transcripts.jsonl

# View most recent 5
tail -5 N5/logs/meeting-processing/processed_transcripts.jsonl | jq .
```

### Force Processing Now
Instead of waiting for the hourly run, you can trigger me manually:
```
Process any new meeting transcripts from Google Drive now
```

### View Scheduled Task
Visit: https://va.zo.computer/schedule

---

## The Architecture

### Why This Approach Works

**Previous problem**: The meeting orchestrator script used a stub LLM client that returned placeholder text instead of real analysis.

**Current solution**: 
- Scheduled task triggers **me (Zo)** directly
- I do the actual LLM work (reading, analyzing, generating)
- Maintains quality while being fully automated
- Processing log prevents reprocessing

### The Flow

```
Every hour at :00
    ↓
Scheduled task triggers Zo
    ↓
Zo checks Google Drive
    ↓
Compares against processing log
    ↓
For each new transcript:
    - Downloads file
    - Reads ENTIRE transcript
    - Generates real insights
    - Creates meeting folder
    - Updates log
    ↓
Done until next hour
```

---

## Monitoring

### Check if it's working:
1. Visit https://va.zo.computer/schedule - see the task and next run time
2. Check the processing log after each run
3. Look for new folders in `file 'Careerspan/Meetings/'`

### What to expect:
- **If new transcripts found**: Full meeting intelligence package generated
- **If no new transcripts**: Simple log message "No new transcripts found"
- **Never reprocesses**: Log prevents duplicate work

---

## File Locations

| Purpose | Location |
|---------|----------|
| Processing Log | `file 'N5/logs/meeting-processing/processed_transcripts.jsonl'` |
| Staging Area | `file 'Documents/Meetings/_staging/'` |
| Output Folders | `file 'Careerspan/Meetings/'` |
| Command Doc | `file 'N5/commands/meeting-auto-process.md'` |

---

## Next Steps

1. **Wait for next hour** - The system will run automatically at the top of every hour
2. **Upload test transcript** - Add a new file to Google Drive Fireflies/Transcripts to test
3. **Check results** - Look for new folder in Careerspan/Meetings/

The system is now live and will process transcripts automatically! 🎉

---

## Example: What You'll See

When the hourly task runs and finds a new transcript:

```
Processing new transcript: John Doe Meeting-2025-10-09...
✓ Downloaded to staging
✓ Generated action-items.md (8 items)
✓ Generated decisions.md (4 decisions)
✓ Generated key-insights.md (10 insights)
✓ Generated stakeholder-profile.md
✓ Generated follow-up-email.md
✓ Generated REVIEW_FIRST.md
✓ Created meeting folder: Careerspan/Meetings/2025-10-09_1400_advisory_john-doe
✓ Updated processing log

Processing complete. Next check in 1 hour.
```
