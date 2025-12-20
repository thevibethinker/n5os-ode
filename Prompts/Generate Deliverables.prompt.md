---
description: 'Command: generate-deliverables'
tool: true
tags: []
---
# `generate-deliverables`

Generate on-demand deliverables for a processed meeting.

## Usage

```bash
# Generate all recommended deliverables (excluding follow-up email)
N5: generate-deliverables <meeting-folder> --recommended

# Generate specific deliverables
N5: generate-deliverables <meeting-folder> --deliverables blurb,one_pager_memo

# Generate everything (excluding follow-up email, which is handled by MG-5)
N5: generate-deliverables <meeting-folder> --all
```

## Examples

```bash
# After reviewing RECOMMENDED_DELIVERABLES.md, generate the blurb
N5: generate-deliverables "2025-10-10_0023_sales_lensa-mai-flynn" --deliverables blurb

# Generate blurb and one-pager memo
N5: generate-deliverables "2025-10-10_0023_sales_lensa-mai-flynn" --deliverables blurb,one_pager_memo

# Generate all recommended deliverables (non-email)
N5: generate-deliverables "2025-10-10_0023_sales_lensa-mai-flynn" --recommended
```

## Available Deliverables

- `blurb` - 1-3 paragraph introduction for external sharing
- `one_pager_memo` - Executive summary/memo
- `proposal_pricing` - Pricing proposal (if applicable)

> **Note:** Follow-up emails are now generated exclusively by the MG-5 **Follow-Up Email Generator v2** workflow:
> - Prompt: `file 'Prompts/Follow-Up Email Generator.prompt.md'`
> - Capability: `file 'N5/capabilities/workflows/follow-up-email-generator-v2-agent.md'`

## Implementation

**Script:** `/home/workspace/N5/scripts/generate_deliverables.py`

The script:
1. Loads meeting transcript and metadata
2. Loads knowledge base
3. Infers parameters for requested deliverables
4. Generates only requested deliverables (non-email)
5. Saves to meeting folder under `DELIVERABLES/`

## Notes

- Only generates what you request (fast, focused)
- Uses validated parameters from Phase 1 processing
- Can regenerate if needed (idempotent)

