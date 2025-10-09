# `meeting-process`

Process a meeting transcript end-to-end using the Meeting Orchestrator.

## Usage

```bash
N5: meeting-process <transcript_source> \
  --type <types...> \
  --stakeholder <roles...> \
  [--mode full|essential|quick]
```

- `transcript_source`: Path to transcript or meeting folder.
- `--type`: Meeting classification (e.g., `sales`, `networking`).
- `--stakeholder`: Role of the primary stakeholder (e.g., `customer_founder`).
- `--mode`: Processing depth. `full` is default.

## Description

This command runs the entire meeting intelligence pipeline, which now includes the automatic generation of deliverables as its final step.

## What Gets Generated

The Meeting Orchestrator generates a comprehensive meeting intelligence package with 15-20+ blocks:

### Core Blocks (7 - always generated)
- `action-items.md` - 10-20 action items with owners, deadlines, priorities
- `decisions.md` - 5-8 key decisions (strategic, process, product)
- `key-insights.md` - 10-15 strategic insights across hiring, wellness, product themes
- `stakeholder-profile.md` - Comprehensive participant profile
- `follow-up-email.md` - Draft follow-up with specific next steps
- `REVIEW_FIRST.md` - Executive dashboard
- `transcript.txt` - Full transcript copy

### Intelligence Blocks (in INTELLIGENCE/ subfolder - conditional)
- `warm-intros.md` - Warm introduction opportunities
- `risks.md` - Identified risks and concerns
- `opportunities.md` - Business opportunities
- `user-research.md` - User pain points and insights
- `competitive-intel.md` - Competitor intelligence
- `career-insights.md` - Career development themes (coaching/networking)
- `deal-intelligence.md` - Deal analysis (sales)
- `investor-thesis.md` - Investor alignment (fundraising)
- `partnership-scope.md` - Partnership framework (partnerships)

### Deliverables (in DELIVERABLES/ subfolder - conditional)
Generated automatically based on meeting type and content:
- `DELIVERABLES/blurbs/blurb_YYYY-MM-DD.md` - Company/product blurb
- `DELIVERABLES/one_pagers/one_pager_YYYY-MM-DD.md` - Executive one-pager
- `DELIVERABLES/proposals_pricing/proposal_pricing_YYYY-MM-DD.md` - Pricing proposal

### Metadata
- `_metadata.json` - Meeting metadata with SHA256 checksums, intelligence counts

**Total: 15-20+ blocks per meeting depending on content and meeting type**
