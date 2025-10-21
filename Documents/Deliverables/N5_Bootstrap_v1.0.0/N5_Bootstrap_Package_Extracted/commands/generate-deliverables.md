# `generate-deliverables`

Generate on-demand deliverables for a processed meeting.

## Usage

```bash
# Generate all recommended deliverables
N5: generate-deliverables <meeting-folder> --recommended

# Generate specific deliverables
N5: generate-deliverables <meeting-folder> --deliverables blurb,follow_up_email

# Generate everything
N5: generate-deliverables <meeting-folder> --all
```

## Examples

```bash
# After reviewing RECOMMENDED_DELIVERABLES.md, generate the blurb
N5: generate-deliverables "2025-10-10_0023_sales_lensa-mai-flynn" --deliverables blurb

# Generate blurb and follow-up email
N5: generate-deliverables "2025-10-10_0023_sales_lensa-mai-flynn" --deliverables blurb,follow_up_email

# Generate all recommended deliverables
N5: generate-deliverables "2025-10-10_0023_sales_lensa-mai-flynn" --recommended
```

## Available Deliverables

- `blurb` - 1-3 paragraph introduction for external sharing
- `follow_up_email` - Draft email to send to meeting participants
- `one_pager_memo` - Executive summary/memo
- `proposal_pricing` - Pricing proposal (if applicable)

## Implementation

**Script:** `/home/workspace/N5/scripts/generate_deliverables.py`

The script:
1. Loads meeting transcript and metadata
2. Loads knowledge base
3. Infers parameters for requested deliverables
4. Generates only requested deliverables
5. Saves to meeting folder under `DELIVERABLES/`

## Notes

- Only generates what you request (fast, focused)
- Uses validated parameters from Phase 1 processing
- Can regenerate if needed (idempotent)
