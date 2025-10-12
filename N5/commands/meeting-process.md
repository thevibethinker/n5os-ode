# `meeting-process`

**Version**: 3.0.0  
**Category**: Meeting Intelligence  
**Workflow**: Automation  
**Script**: `N5/scripts/meeting_intelligence_orchestrator.py`

## Purpose

This command processes meeting transcripts that have been queued in the meeting requests inbox. When invoked (typically by a scheduled task), Zo processes ONE transcript at a time, generating comprehensive "Smart Blocks" that provide structured meeting intelligence.

## Architecture

**Key Principle:** Zo processes content directly using native LLM capabilities with template guidance from the TemplateManager.

```
Processing Request (JSON) → Zo Loads Templates → Zo Analyzes Transcript → Smart Blocks Generated
```

## What This Command Does

**CRITICAL:** Process **ONLY ONE** transcript per invocation to avoid context window issues.

When invoked (via scheduled task or manually), Zo will:

1. **Check for pending requests** in `N5/inbox/meeting_requests/`
2. **Select the OLDEST request** (by filename/timestamp) to maintain FIFO ordering
3. **Process ONLY that single request:**
   - Load the processing request JSON to get transcript details (gdrive_id, classification, participants)
   - Download transcript from Google Drive using the gdrive_id
   - Save transcript to `N5/inbox/transcripts/{meeting_id}.txt`
   - Initialize TemplateManager with meeting_id and stakeholder classification
   - Load appropriate templates based on classification (internal vs external)
   - Generate Smart Blocks using native LLM analysis
   - Save all blocks to `N5/records/meetings/{meeting_id}/`
   - Create `_metadata.json` with full processing context
   - Mark the Google Drive file as processed by adding `[ZO-PROCESSED]` prefix
   - Move request to `N5/inbox/meeting_requests/processed/`
4. **Stop after one transcript** — next invocation (10 min later) will process the next one

## Processing Request Format

Each request in `N5/inbox/meeting_requests/{meeting-id}_request.json` contains:

```json
{
  "meeting_id": "2025-10-10_stakeholder-name",
  "gdrive_id": "1abc...",
  "gdrive_link": "https://drive.google.com/...",
  "stakeholder_classification": "internal" or "external",
  "participants": ["Vrijen", "Other Person"],
  "detected_date": "2025-10-10T19:00:00Z",
  "source": "google_drive"
}
```

## Smart Blocks Generated

### Internal Meeting Blocks (Priority Order)
- **B01: DETAILED_RECAP** (required) - Key decisions and agreements
- **B08: RESONANCE_POINTS** (required) - Moments of connection and enthusiasm
- **B21: SALIENT_QUESTIONS** (high priority) - Strategic questions from the meeting
- **B22: DEBATE_TENSION_ANALYSIS** (high priority) - Areas of disagreement
- **B24: PRODUCT_IDEA_EXTRACTION** (conditional) - Product/feature ideas discussed
- **B29: KEY_QUOTES_HIGHLIGHTS** (medium priority) - Significant verbatim quotes

### External Meeting Blocks (Priority Order)
- **B01: DETAILED_RECAP** (required) - Key decisions and agreements
- **B08: RESONANCE_POINTS** (required) - Moments of connection and enthusiasm
- **B21: SALIENT_QUESTIONS** (high priority) - Strategic questions from the meeting
- **B25: DELIVERABLE_CONTENT_MAP** (high priority) - Promised deliverables
- **B28: FOUNDER_PROFILE_SUMMARY** (external only) - Founder/company profile
- **B14: BLURBS_REQUESTED** (medium priority) - Intro blurbs for warm intros
- **B30: INTRO_EMAIL_TEMPLATE** (conditional) - Introduction email template

## Usage

### Via Scheduled Task (Recommended)
The scheduled task runs every 10 minutes and automatically processes pending transcripts one at a time.

### Manual Invocation
```bash
# Process the next pending transcript
command 'meeting-process'
```

## Integration Points

- **Upstream**: `transcript-auto-processor` creates request files in the inbox
- **Downstream**: 
  - `meeting-approve` displays generated blocks for review
  - `deliverable-generate` uses blocks to create deliverables
  - `follow-up-email-generator` consumes block data for email drafting

## Files and Directories

### Input
- `N5/inbox/meeting_requests/*.json` - Pending processing requests

### Output
- `N5/records/meetings/{meeting_id}/` - Meeting directory with all blocks
- `N5/inbox/transcripts/{meeting_id}.txt` - Downloaded transcript
- `N5/inbox/meeting_requests/processed/` - Completed requests

### Templates
- `N5/prefs/block_templates/internal/` - Templates for internal meetings
- `N5/prefs/block_templates/external/` - Templates for external meetings

## Related Commands

- `meeting-intelligence-orchestrator` (alias: `mio`) - Direct invocation with explicit parameters
- `meeting-approve` - Review and approve generated blocks
- `deliverable-generate` - Generate deliverables from blocks
- `transcript-ingest` - Manual transcript ingestion

## Notes

- Processing one transcript at a time ensures predictable resource usage and prevents context window overflow
- FIFO ordering ensures meetings are processed in the order they were received
- The TemplateManager provides structure and guidance, but Zo performs the actual content extraction
- Templates are customized based on stakeholder classification to generate relevant intelligence blocks
