# `meeting-process`

Process a meeting transcript end-to-end using the phased workflow.

**Version:** 2.1 (Phased - essentials first, deliverables on-demand)

## Overview

The meeting processor now uses a smart, phased approach:
- **Phase 1 (automatic):** Generate only essential intelligence
- **Phase 2 (on-demand):** Generate deliverables you request

This saves time and reduces cognitive load while still providing everything you need.

## Usage

```bash
N5: meeting-process <transcript-path> [--type TYPE] [--stakeholder STAKEHOLDER]
```

## Examples

```bash
# Process a sales meeting
N5: meeting-process "path/to/transcript.txt" --type sales --stakeholder business_partner

# Process a community partnerships meeting
N5: meeting-process "path/to/transcript.txt" --type community_partnerships

# Process with just the transcript (will infer type)
N5: meeting-process "path/to/transcript.txt"
```

## What Gets Generated (Phase 1)

**Essential Intelligence:**
- `REVIEW_FIRST.md` - Executive dashboard with summary, action items, decisions
- `content-map.md` - Extraction details, parameters, confidence scores
- `RECOMMENDED_DELIVERABLES.md` - Smart suggestions for what to generate
- `action-items.md` - Critical action items
- `decisions.md` - Key decisions made
- `stakeholder-profile.md` - Participant information
- `_metadata.json` - Processing metadata

**Time:** ~30 seconds

**Notification:** SMS sent with summary and recommendations

## Generate Additional Deliverables (Phase 2)

After reviewing Phase 1 outputs, request deliverables:

```bash
# Generate specific deliverables
N5: generate-deliverables <meeting-folder> --deliverables blurb,follow_up_email

# Generate all recommended
N5: generate-deliverables <meeting-folder> --recommended

# Generate everything
N5: generate-deliverables <meeting-folder> --all
```

## Available Deliverables (on-demand)

- `blurb` - Company introduction for external sharing
- `follow_up_email` - Draft email to participants
- `one_pager_memo` - Executive summary document
- `proposal_pricing` - Pricing proposal (if applicable)

## Meeting Types

- `sales` - Sales/business development meetings
- `fundraising` - Investor meetings
- `community_partnerships` - Community/partnership discussions
- `coaching` - Career coaching sessions
- `internal` - Internal team meetings

## Implementation

**Script:** `/home/workspace/N5/scripts/meeting_intelligence_orchestrator.py`

**Required Arguments:**
- `--transcript_path PATH` - Path to meeting transcript file (.txt, .md, .docx)
- `--meeting_id ID` - Unique meeting identifier (e.g., "meeting-20251010-1400")

**Optional Arguments:**
- `--essential_links_path PATH` - Path to essential links JSON (default: `/home/workspace/N5/prefs/communication/essential-links.json`)
- `--block_registry_path PATH` - Path to block registry JSON (default: `/home/workspace/N5/prefs/block_type_registry.json`)
- `--use-simulation` - Use simulated LLM responses for testing

**Output Directory:** `/home/workspace/N5/records/meetings/{meeting_id}/`

The script:
1. Loads transcript and configuration files (block registry, essential links)
2. Creates extraction request files for LLM processing
3. Generates intelligence blocks based on registry definitions
4. Writes structured outputs to meeting directory
5. Logs processing details for debugging

**Direct Usage Example:**
```bash
# Generate meeting ID
MEETING_ID="meeting-$(date +%Y%m%d-%H%M%S)"

# Run orchestrator
python3 /home/workspace/N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path "path/to/transcript.txt" \
  --meeting_id "$MEETING_ID"

# View outputs
ls -la /home/workspace/N5/records/meetings/$MEETING_ID/
```

**Testing Mode:**
```bash
# Use simulation mode (no real LLM calls)
python3 /home/workspace/N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path "test_transcript.txt" \
  --meeting_id "test-meeting" \
  --use-simulation
```

## Key Features

- ✅ **Fast initial processing** (~30 seconds vs 2-3 minutes)
- ✅ **Smart recommendations** based on meeting content
- ✅ **Validated extractions** (no more wrong context)
- ✅ **Confidence scores** for all inferences
- ✅ **SMS notifications** with actionable summary
- ✅ **On-demand deliverables** (generate only what you need)

## Notes

- Old workflow (v1) has been deprecated
- All meetings now use the phased approach
- Deliverables are generated fast (~30-60s) when requested
- System learns from your choices to improve recommendations
