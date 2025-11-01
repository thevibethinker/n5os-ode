---
description: 'Generate a descriptive thread title using N5 title generator'
tags:
- thread
- title
- export
- system
---
# Generate Thread Title

Version: 1.0.0

Summary: Generate a descriptive thread title based on conversation content using the N5 thread title generator script

Workflow: system

Tags: thread, title, export, system, automation

## Inputs
- --test : flag (optional) — Run with test data to see sample output

## Outputs
- thread_title : text — Generated thread title following N5 naming conventions (18-30 chars target, 35 max)
- title_options : list — Multiple title options with reasoning

## Side Effects
None - read-only title generation

## Description

Uses `N5/scripts/n5_title_generator.py` to generate thread titles following N5 conventions:
- Emoji prefix from centralized legend
- Noun-first principle
- 18-30 character target (35 max)
- Content-driven analysis

## Usage

**Test mode (see sample output):**
```bash
python3 /home/workspace/N5/scripts/n5_title_generator.py --test
```

**Interactive mode:**
This script is typically called by:
- Thread Export workflow (automatic)
- Conversation End process (automatic)

To manually generate a title for the current thread, ask Zo to run the title generator and provide the conversation context.

## Dependencies
- `N5/scripts/n5_title_generator.py`
- `N5/config/emoji-legend.json`

## Notes
- Title generation uses AI analysis of conversation content
- Follows centralized emoji legend for consistent categorization
- Automatically handles thread sequencing (#1, #2, etc.)
- Integrated into Thread Export and Conversation End workflows
