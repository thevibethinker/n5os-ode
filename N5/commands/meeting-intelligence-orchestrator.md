---
date: 2025-10-09
last-tested: 2025-10-09
generated_date: 2025-10-09
checksum: meeting_intelligence_orchestrator
---
# `meeting-intelligence-orchestrator` (alias: `mio`)

**Category**: Meeting Intelligence
**Workflow**: Automation
**Script**: `N5/scripts/meeting_intelligence_orchestrator.py`

## Description

This command orchestrates the comprehensive extraction of intelligence from meeting transcripts and generates a set of modular "Smart Blocks". These blocks provide summarized insights, action items, critical questions, and other relevant information, designed to streamline follow-up and decision-making.

It leverages an adaptive generation mechanism, incorporating user feedback to optimize which blocks are generated based on context and usefulness over time.

## Usage

```bash
mio --transcript_path "/path/to/your/transcript.txt" --meeting_id "unique_meeting_id"
```

## Arguments

*   `--transcript_path`: Absolute path to the meeting transcript file (required).
*   `--meeting_id`: A unique identifier for the meeting (e.g., a timestamp or a slug derived from the meeting title) (required).
*   `--essential_links_path`: Path to the essential links JSON file. (Default: `/home/workspace/N5/prefs/communication/essential-links.json`)
*   `--block_registry_path`: Path to the block type registry JSON file. (Default: `/home/workspace/N5/prefs/block_type_registry.json`)

## Generated Smart Blocks

Upon execution, this command generates several intelligence blocks (Markdown format) that are displayed to the user and (where applicable) persisted as JSONL for further analysis. Blocks may include:

*   **MEETING_METADATA_SUMMARY (B26)**: Overall meeting details and proposed subject line.
*   **DETAILED_RECAP (B01)**: Key decisions and agreements.
*   **FOUNDER_PROFILE_SUMMARY (B28)**: Structured summary of a non-Careerspan founder's venture (if applicable).
*   **SALIENT_QUESTIONS (B21)**: Top strategic questions from the meeting.
*   **DEBATE_TENSION_ANALYSIS (B22)**: Highlights areas of disagreement or unresolved topics.
*   **USER_FEEDBACK_SUMMARY (B23)**: Synthesized user/customer feedback.
*   **PRODUCT_IDEA_EXTRACTION (B24)**: Extracted product or feature ideas.
*   **KEY_QUOTES_HIGHLIGHTS (B29)**: Significant verbatim quotes.
*   **DELIVERABLE_CONTENT_MAP (B25)**: Structured map of promised deliverables.
*   **OUTSTANDING_QUESTIONS (B05)**: Unresolved items and identified blockers.
*   **PRIVATE_NOTES_FOR_ME (B27)**: Personal, private notes.

## Feedback Mechanism

Many blocks include a `**Feedback**: [Useful/Not Useful]` section. You can directly edit this line to mark the block's utility. This feedback will be logged and used to adaptively refine future block generation, optimizing for relevance and reducing token usage over time.

## Persistence

Relevant block data is persisted in per-meeting directories (`N5/records/meetings/<meeting_id>/`) and aggregated into central lists (`N5/lists/product-feedback.jsonl`, `N5/lists/product-ideas.jsonl`).

## Integration Points

*   `meeting-process`: This command can be replaced by or orchestrates calls to `mio`.
*   `meeting-approve`: Will display `mio` generated blocks for review and allow for feedback.
*   `follow-up-email-generator`: Consumes structured data from `mio` for email drafting.
