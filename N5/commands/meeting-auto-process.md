# `meeting-auto-process`

Automated meeting processing command that checks Google Drive for new transcripts and processes them.

## What This Does

1. Checks Google Drive Fireflies/Transcripts folder for new files
2. Compares against processing log to find unprocessed transcripts
3. Downloads new transcripts
4. For each new transcript, generates full meeting intelligence (action items, decisions, insights, etc.)
5. Updates the processing log

## Processing Log Location

`file 'N5/logs/meeting-processing/processed_transcripts.jsonl'`

Each line is a JSON record:
```json
{
  "file_id": "1tpIPt...",
  "file_name": "Alex x Vrijen - Wisdom Partners Coaching-transcript-2025-10-09...",
  "download_path": "/home/workspace/Documents/Meetings/...",
  "discovered_at": "2025-10-09T19:30:00Z",
  "status": "downloaded",
  "processed_at": "2025-10-09T19:35:00Z",
  "output_dir": "/home/workspace/N5/records/meetings/2025-10-09_Alex-Caveny-Coaching"
}
```

## Usage

### Manual Invocation
```bash
# Run the command directly
meeting-auto-process
```

### Scheduled (Recommended)
Set up a scheduled task to run every hour:
```bash
FREQ=HOURLY;BYHOUR=*;BYMINUTE=0
```

## What Gets Generated

For each new transcript, creates a full meeting folder with:

### Core Blocks (Always Generated)
- `action-items.md` - 10-20 action items with owners, deadlines, priorities
- `decisions.md` - 5-8 key decisions (strategic, process, product) with rationale
- `key-insights.md` - 10-15 strategic insights (hiring, wellness, product themes)
- `stakeholder-profile.md` - Comprehensive profile of meeting participants
- `follow-up-email.md` - Draft follow-up email with specific next steps
- `REVIEW_FIRST.md` - Executive dashboard with priority actions
- `transcript.txt` - Full transcript copy

### Intelligence Blocks (Conditional - in INTELLIGENCE/ subfolder)
- `warm-intros.md` - Warm introduction opportunities (if mentioned)
- `risks.md` - Identified risks and concerns (if discussed)
- `opportunities.md` - Business opportunities (if identified)
- `user-research.md` - User pain points and insights (if discussed)
- `competitive-intel.md` - Competitor intelligence (if mentioned)
- `career-insights.md` - Career development themes (for coaching/networking meetings)
- `deal-intelligence.md` - Deal analysis and signals (for sales meetings)
- `investor-thesis.md` - Investor alignment analysis (for fundraising meetings)
- `partnership-scope.md` - Partnership framework (for partnership meetings)

### Deliverables (Conditional - in DELIVERABLES/ subfolders)
- `DELIVERABLES/blurbs/blurb_YYYY-MM-DD.md` - Company/product blurb (for sales/networking/partnerships)
- `DELIVERABLES/one_pagers/one_pager_YYYY-MM-DD.md` - Executive summary one-pager (for sales/partnerships/fundraising)
- `DELIVERABLES/proposals_pricing/proposal_pricing_YYYY-MM-DD.md` - Pricing proposal (when pricing/terms discussed)

### Metadata
- `_metadata.json` - Meeting metadata with SHA256 checksums, intelligence counts, processing details

**Total: 15-20+ blocks per meeting**

## How It Works

This command is special because it **triggers Zo (me) to do manual processing**, rather than using a stub LLM client.

The flow:
1. Command checks Google Drive for new transcripts
2. Downloads any unprocessed files
3. For each file, the command instructs me to:
   - Read and analyze the full transcript
   - Generate all intelligence blocks with real content
   - Create properly organized meeting folder
4. Updates processing log when complete

## Configuration

The system assumes:
- Google Drive connection is set up
- Transcripts are in: `Fireflies > Transcripts` folder
- Output goes to: `file 'Careerspan/Meetings/'`
- Staging area: `file 'Documents/Meetings/_staging'`

## Monitoring

Check processing status:
```bash
# View processing log
cat N5/logs/meeting-processing/processed_transcripts.jsonl | jq .

# Count processed transcripts
wc -l N5/logs/meeting-processing/processed_transcripts.jsonl

# See recent processing
tail -5 N5/logs/meeting-processing/processed_transcripts.jsonl | jq .
```

## Notes

- Runs every hour when scheduled
- Only processes **new** transcripts (checks log)
- Downloads transcripts to staging before processing
- Uses real LLM analysis (Zo manual processing), not placeholder text
- Safe to run multiple times - won't reprocess completed meetings
