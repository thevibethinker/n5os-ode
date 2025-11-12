---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Quick Start Guide - Intelligence Block Generator

Get started generating intelligence blocks in 3 simple steps.

---

## Prerequisites

- Meeting transcript file (text format or JSON with transcript field)
- Meeting ID (format: `MXX_YYYY-MM-DD_description`)

---

## 3-Step Quick Start

### Step 1: Identify Your Block

Find the block you want to generate:

```bash
# List all available blocks
python3 /home/workspace/Intelligence/scripts/block_generator_engine.py list

# List blocks by category
python3 /home/workspace/Intelligence/scripts/block_generator_engine.py list --category external
```

**Most Common Blocks:**
- **B01** - DETAILED_RECAP: Comprehensive meeting summary
- **B02** - COMMITMENTS_CONTEXTUAL: Action items with context
- **B08** - STAKEHOLDER_INTELLIGENCE: Deep stakeholder analysis
- **B21** - KEY_MOMENTS: Critical conversation points
- **B25** - DELIVERABLE_CONTENT_MAP: Content deliverables
- **B40** - INTERNAL_DECISIONS: Strategic decisions (internal meetings)

### Step 2: Generate the Block

Use the wrapper tool for your chosen block:

```bash
# Generate B01 (Detailed Recap)
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-id M01_2025-11-03_strategy-session \
  --transcript-path /path/to/transcript.txt

# Generate B08 (Stakeholder Intelligence)
/home/workspace/Intelligence/tools/generate-b08 \
  --meeting-id M01_2025-11-03_strategy-session \
  --transcript-path /path/to/transcript.txt

# Specify custom output location
/home/workspace/Intelligence/tools/generate-b02 \
  --meeting-id M01_2025-11-03_strategy-session \
  --transcript-path /path/to/transcript.txt \
  --output-dir /home/workspace/Custom/Location
```

### Step 3: Find Your Output

By default, blocks are saved to:

```
/home/workspace/Intelligence/Blocks/{meeting_id}/{block_id}.md
```

**Example:**
```bash
# For meeting M01_2025-11-03_strategy-session, block B01:
/home/workspace/Intelligence/Blocks/M01_2025-11-03_strategy-session/B01.md
```

---

## Common Workflows

### Generate Multiple Blocks for One Meeting

```bash
# Generate comprehensive meeting intelligence
/home/workspace/Intelligence/tools/generate-b01 --meeting-id M01_2025-11-03_call --transcript-path transcript.txt
/home/workspace/Intelligence/tools/generate-b02 --meeting-id M01_2025-11-03_call --transcript-path transcript.txt
/home/workspace/Intelligence/tools/generate-b08 --meeting-id M01_2025-11-03_call --transcript-path transcript.txt
/home/workspace/Intelligence/tools/generate-b21 --meeting-id M01_2025-11-03_call --transcript-path transcript.txt
```

### Using the Engine Directly

```bash
# More control over generation
python3 /home/workspace/Intelligence/scripts/block_generator_engine.py generate \
  --block-id B01 \
  --meeting-id M01_2025-11-03_call \
  --transcript-path transcript.txt \
  --output-dir /custom/location
```

### Batch Generation for All Required Blocks

```bash
# Generate all required blocks for a meeting
MEETING_ID="M01_2025-11-03_strategy"
TRANSCRIPT="/path/to/transcript.txt"

for BLOCK in b01 b02 b08 b21 b25 b26 b31; do
  /home/workspace/Intelligence/tools/generate-${BLOCK} \
    --meeting-id ${MEETING_ID} \
    --transcript-path ${TRANSCRIPT}
done
```

---

## Real Examples

### Example 1: External Sales Call

```bash
# Meeting: Sales call with potential customer
MEETING_ID="M42_2025-11-03_acme-corp-discovery"
TRANSCRIPT="/home/workspace/Personal/Meetings/2025-11-03_acme-corp/transcript.txt"

# Generate key blocks
/home/workspace/Intelligence/tools/generate-b01 --meeting-id ${MEETING_ID} --transcript-path ${TRANSCRIPT}  # Recap
/home/workspace/Intelligence/tools/generate-b02 --meeting-id ${MEETING_ID} --transcript-path ${TRANSCRIPT}  # Commitments
/home/workspace/Intelligence/tools/generate-b08 --meeting-id ${MEETING_ID} --transcript-path ${TRANSCRIPT}  # Stakeholder intel
/home/workspace/Intelligence/tools/generate-b31 --meeting-id ${MEETING_ID} --transcript-path ${TRANSCRIPT}  # Research

# Output location: /home/workspace/Intelligence/Blocks/M42_2025-11-03_acme-corp-discovery/
```

### Example 2: Internal Strategy Meeting

```bash
# Meeting: Internal product strategy session
MEETING_ID="M15_2025-11-03_product-roadmap-q4"
TRANSCRIPT="/home/workspace/Personal/Meetings/2025-11-03_product-strategy/transcript.txt"

# Generate internal blocks
/home/workspace/Intelligence/tools/generate-b40 --meeting-id ${MEETING_ID} --transcript-path ${TRANSCRIPT}  # Decisions
/home/workspace/Intelligence/tools/generate-b43 --meeting-id ${MEETING_ID} --transcript-path ${TRANSCRIPT}  # Product intel
/home/workspace/Intelligence/tools/generate-b44 --meeting-id ${MEETING_ID} --transcript-path ${TRANSCRIPT}  # GTM/Sales intel

# Output location: /home/workspace/Intelligence/Blocks/M15_2025-11-03_product-roadmap-q4/
```

---

## Common Issues & Fixes

### Issue: "Transcript file not found"

**Solution:**
```bash
# Verify file exists
ls -la /path/to/transcript.txt

# Use absolute path
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-id M01_2025-11-03_call \
  --transcript-path /home/workspace/full/path/to/transcript.txt
```

### Issue: "Block not found in database"

**Solution:**
```bash
# List available blocks
python3 /home/workspace/Intelligence/scripts/block_generator_engine.py list

# Make sure block ID is uppercase
/home/workspace/Intelligence/tools/generate-b01  # ✓ Correct
/home/workspace/Intelligence/tools/generate-B01  # ✓ Also works
```

### Issue: "Output already exists"

**Solution:**
```bash
# Blocks are versioned automatically
# If B01.md exists, new generation creates B01_v2.md

# Or specify custom output file
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-id M01_2025-11-03_call \
  --transcript-path transcript.txt \
  --output-file /path/to/custom_output.md
```

### Issue: Generation seems slow

**Expected:** 15-45 seconds per block depending on:
- Transcript length
- Block complexity
- LLM model used

**Tips:**
- External blocks (B01-B31): 20-45s
- Internal blocks (B40-B48): 15-30s
- Reflection blocks (B50+): 10-20s

---

## Next Steps

- **Learn more:** Read file 'Intelligence/README.md' for full system documentation
- **Migrate from old tools:** See file 'Intelligence/MIGRATION.md'
- **Add new blocks:** See "How to Add New Blocks" in README
- **Quality testing:** Run `python3 Intelligence/scripts/run_quality_tests.py`
- **Validate samples:** Run `python3 Intelligence/scripts/validate_samples.py`

---

## Quick Reference

| Block Category | Range | Use For |
|----------------|-------|---------|
| External Meeting | B01-B31 | Customer calls, sales, partnerships |
| Internal Meeting | B40-B48 | Team meetings, strategy sessions |
| Reflection & Synthesis | B50-B99 | Personal insights, market analysis |

| Command | Purpose |
|---------|---------|
| `tools/generate-bXX` | Generate specific block |
| `scripts/block_generator_engine.py list` | List available blocks |
| `tests/integration_test.py --dry-run` | Test system setup |
| `scripts/run_quality_tests.py` | Run regression tests |

---

**Ready to generate your first block? Pick a tool and go!** 🚀

*Last updated: 2025-11-03 | Version 1.0*
