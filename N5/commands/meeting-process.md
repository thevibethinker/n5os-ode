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

**Script:** `/home/workspace/N5/scripts/meeting_orchestrator.py`

The script:
1. Extracts participants, companies, topics from transcript
2. Validates extracted parameters with confidence scoring
3. Generates essential intelligence blocks
4. Recommends useful deliverables
5. Sends SMS notification with summary
6. Waits for your request to generate additional outputs

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
