---
description: 'Command: deliverable-generate'
tags: []
---
# `deliverable-generate`

Generate deliverables (blurbs, one-pagers/memos, proposals/pricing) from a meeting transcript using the Deliverable Orchestrator.

## Usage

```bash
N5: deliverable-generate <transcript_path> \
  --meeting-type <types...> \
  [--stakeholder <roles...>]
```

- `transcript_path`: Absolute path to the transcript file or meeting folder.
- `--meeting-type`: One or more meeting types (e.g., `community_partnerships`, `sales`).
- `--stakeholder`: (Optional) Role of the primary stakeholder.

## Description

Generates deliverables from a meeting transcript. Deliverables are automatically generated during the `meeting-process` workflow, but this command allows standalone generation or regeneration.

### Deliverable Types

Three types of deliverables are generated based on meeting type and content:

1. **Blurbs** (`DELIVERABLES/blurbs/`) - 2-3 paragraph company/product descriptions
   - Generated for: sales, networking, community partnership meetings
   - Tailored to specific audience mentioned in meeting

2. **One-Pagers** (`DELIVERABLES/one_pagers/`) - Executive summary format
   - Generated for: sales, partnerships, fundraising meetings
   - Includes problem, solution, value prop, differentiators

3. **Proposals/Pricing** (`DELIVERABLES/proposals_pricing/`) - Customized proposals
   - Generated when: pricing, terms, or proposals discussed
   - Includes pricing structure, terms, next steps

All deliverables are saved to the meeting folder under `DELIVERABLES/` with appropriate subdirectories.
