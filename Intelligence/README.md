# Intelligence Block Generator System

Automated generation system for 37 types of intelligence blocks from meeting data.

## Quick Start

### Generate a Block

```bash
# Using a wrapper tool
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-file /path/to/meeting.json \
  --output-file /path/to/output.md

# Using the engine directly
python3 /home/workspace/Intelligence/scripts/block_generator_engine.py \
  --block-id B01 \
  --meeting-file /path/to/meeting.json \
  --output-file /path/to/output.md
```

### Test the System

```bash
# Run integration tests (Batch 1 blocks)
python3 /home/workspace/Intelligence/tests/integration_test.py

# Run quality regression tests
python3 /home/workspace/Intelligence/scripts/run_quality_tests.py

# Validate all samples
python3 /home/workspace/Intelligence/scripts/validate_samples.py
```

## System Overview

### Architecture

```
Intelligence/
├── blocks.db              # Core database (blocks, prompts, samples, history)
├── scripts/               # Generation and testing scripts
│   ├── block_generator_engine.py    # Core generation engine
│   ├── generate_tool_wrappers.py    # Tool wrapper generator
│   ├── run_quality_tests.py         # Quality regression testing
│   ├── add_quality_sample.py        # Sample management
│   └── validate_samples.py          # Sample validation
├── tools/                 # Auto-generated wrapper tools (37 blocks)
│   ├── generate-b01       # DETAILED_RECAP wrapper
│   ├── generate-b02       # COMMITMENTS_CONTEXTUAL wrapper
│   └── ...                # 35 more block wrappers
├── prompts/               # System and block prompts
├── test_samples/          # Quality samples for regression testing
│   ├── inputs/            # Sample meeting JSON files
│   └── expected_outputs/  # Expected block outputs
└── tests/                 # Test suites
    └── integration_test.py
```

### Available Blocks (37 Total)

#### External Meeting Intelligence (16 blocks)
- **B01** - DETAILED_RECAP: Comprehensive meeting summary
- **B02** - COMMITMENTS_CONTEXTUAL: Action items with context
- **B03** - STAKEHOLDER_PROFILES: Stakeholder analysis
- **B05** - OUTSTANDING_QUESTIONS: Unanswered questions
- **B06** - PILOT_INTELLIGENCE: Pilot program insights
- **B07** - WARM_INTRO_BIDIRECTIONAL: Introduction facilitation
- **B08** - STAKEHOLDER_INTELLIGENCE: Deep stakeholder intel
- **B11** - METRICS_SNAPSHOT: Key metrics and KPIs
- **B13** - PLAN_OF_ACTION: Implementation roadmap
- **B14** - BLURBS_REQUESTED: Content snippets
- **B15** - STAKEHOLDER_MAP: Relationship mapping
- **B21** - KEY_MOMENTS: Critical conversation points
- **B24** - PRODUCT_IDEA_EXTRACTION: Product insights
- **B25** - DELIVERABLE_CONTENT_MAP: Content deliverables
- **B26** - MEETING_METADATA_SUMMARY: Meeting metadata
- **B27** - KEY_MESSAGING: Core messaging
- **B31** - STAKEHOLDER_RESEARCH: Research-backed analysis

#### Internal Meeting Intelligence (9 blocks)
- **B40** - Internal Decisions: Strategic decisions
- **B41** - Team Coordination: Team alignment
- **B42** - Market/Competitive Intel: Market insights
- **B43** - Product Intelligence: Product strategy
- **B44** - GTM/Sales Intel: Go-to-market insights
- **B45** - Operations/Process: Process improvements
- **B46** - Hiring/Team: Hiring strategy
- **B47** - Open Debates: Unresolved discussions
- **B48** - Strategic Memo: Strategic documentation

#### Reflection & Synthesis (12 blocks)
- **B50** - Personal Reflection: Self-reflection
- **B60** - Learning & Synthesis: Learning capture
- **B70** - Thought Leadership: Leadership insights
- **B71** - Market Analysis: Market trends
- **B72** - Product Analysis: Product analysis
- **B73** - Strategic Thinking: Strategic insights
- **B80** - LinkedIn Post: Social content
- **B81** - Blog Post: Long-form content
- **B82** - Executive Memo: Executive communication
- **B90** - Insight Compounding: Cross-meeting synthesis
- **B91** - Meta-Reflection: Meta-cognitive analysis

## How to Use

### 1. Generate a Single Block

The easiest way is to use the auto-generated wrapper tools:

```bash
# Example: Generate a detailed recap
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-file meeting_data.json \
  --output-file recap.md
```

All wrapper tools support:
- `--meeting-file` (required): Path to meeting JSON
- `--output-file` (optional): Output path (defaults to stdout)
- `--dry-run`: Validate without generating

### 2. Generate Multiple Blocks

Create a simple script:

```bash
#!/bin/bash
MEETING_FILE="meeting_data.json"
OUTPUT_DIR="outputs"

# Generate key blocks
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-file "$MEETING_FILE" \
  --output-file "$OUTPUT_DIR/01_recap.md"

/home/workspace/Intelligence/tools/generate-b02 \
  --meeting-file "$MEETING_FILE" \
  --output-file "$OUTPUT_DIR/02_commitments.md"

/home/workspace/Intelligence/tools/generate-b08 \
  --meeting-file "$MEETING_FILE" \
  --output-file "$OUTPUT_DIR/08_stakeholder_intel.md"
```

### 3. Meeting Data Format

Meeting JSON must include:

```json
{
  "meeting_id": "MTG_20251103_001",
  "meeting_type": "external|internal|reflection",
  "date": "2025-11-03",
  "participants": [
    {"name": "Person A", "role": "Role A"},
    {"name": "Person B", "role": "Role B"}
  ],
  "transcript": "Full meeting transcript...",
  "duration_minutes": 45,
  "context": {
    "company": "Company Name",
    "project": "Project Name"
  }
}
```

### 4. Quality Assurance

```bash
# Add a new quality sample
python3 /home/workspace/Intelligence/scripts/add_quality_sample.py \
  --block-id B01 \
  --meeting-id SAMPLE_001 \
  --type baseline \
  --input-file test_samples/inputs/sample.json \
  --output-file test_samples/expected_outputs/expected.md \
  --score 0.90 \
  --notes "Description of sample"

# Run regression tests
python3 /home/workspace/Intelligence/scripts/run_quality_tests.py

# Run integration tests
python3 /home/workspace/Intelligence/tests/integration_test.py
```

## Adding New Block Types

### Step 1: Define Block Schema

Add to `blocks` table in `blocks.db`:

```sql
INSERT INTO blocks (block_id, name, category, description, output_format, status)
VALUES ('B99', 'New Block Type', 'external_meeting', 'Description', 'markdown', 'active');
```

### Step 2: Create Prompt

Add prompt to `prompts` table:

```sql
INSERT INTO prompts (prompt_id, block_id, content, version)
VALUES ('P99_v1', 'B99', 'Your generation prompt...', '1.0');
```

### Step 3: Generate Wrapper Tool

```bash
python3 /home/workspace/Intelligence/scripts/generate_tool_wrappers.py
```

This automatically:
1. Creates `/home/workspace/Intelligence/tools/generate-b99`
2. Registers tool in executables database
3. Makes it available system-wide

### Step 4: Add Quality Samples

```bash
python3 /home/workspace/Intelligence/scripts/add_quality_sample.py \
  --block-id B99 \
  --meeting-id SAMPLE_B99_001 \
  --type baseline \
  --input-file test_samples/inputs/b99_sample.json \
  --output-file test_samples/expected_outputs/b99_expected.md \
  --score 0.85 \
  --notes "Baseline sample for new block"
```

### Step 5: Test

```bash
# Test the new block
python3 /home/workspace/Intelligence/tests/integration_test.py --block-id B99

# Run quality tests
python3 /home/workspace/Intelligence/scripts/run_quality_tests.py --block-id B99
```

## Updating Prompts

### Option 1: Direct Database Update

```sql
UPDATE prompts
SET content = 'Updated prompt content...',
    version = '1.1',
    updated_at = datetime('now')
WHERE prompt_id = 'P01_v1';
```

### Option 2: Using Script (Recommended)

```python
import sqlite3
from pathlib import Path

BLOCKS_DB = Path("/home/workspace/Intelligence/blocks.db")

def update_prompt(block_id, new_content):
    conn = sqlite3.connect(BLOCKS_DB)
    cursor = conn.cursor()
    
    # Get current version
    cursor.execute("""
        SELECT prompt_id, version FROM prompts
        WHERE block_id = ? AND status = 'active'
        ORDER BY created_at DESC LIMIT 1
    """, (block_id,))
    
    current = cursor.fetchone()
    if not current:
        print(f"No active prompt for {block_id}")
        return
    
    # Increment version
    old_version = current[1]
    major, minor = old_version.split('.')
    new_version = f"{major}.{int(minor) + 1}"
    
    # Deactivate old prompt
    cursor.execute("""
        UPDATE prompts SET status = 'deprecated'
        WHERE block_id = ?
    """, (block_id,))
    
    # Insert new prompt
    new_prompt_id = f"P{block_id[1:]}_v{new_version.replace('.', '_')}"
    cursor.execute("""
        INSERT INTO prompts (prompt_id, block_id, content, version, status)
        VALUES (?, ?, ?, ?, 'active')
    """, (new_prompt_id, block_id, new_content, new_version))
    
    conn.commit()
    conn.close()
    print(f"✓ Updated {block_id} to version {new_version}")

# Usage
update_prompt('B01', 'New improved prompt...')
```

## Troubleshooting

### Block Generation Fails

**Check 1: Meeting data format**
```bash
# Validate JSON structure
python3 -c "import json; print(json.load(open('meeting.json')))"
```

**Check 2: Database connectivity**
```bash
sqlite3 /home/workspace/Intelligence/blocks.db "SELECT COUNT(*) FROM blocks WHERE status='active';"
```

**Check 3: Prompt exists**
```bash
sqlite3 /home/workspace/Intelligence/blocks.db "SELECT prompt_id, status FROM prompts WHERE block_id='B01';"
```

### Wrapper Tools Not Found

**Regenerate wrappers:**
```bash
python3 /home/workspace/Intelligence/scripts/generate_tool_wrappers.py
```

**Verify registration:**
```bash
sqlite3 /home/workspace/N5/data/executables.db "SELECT name, file_path FROM executables WHERE category='intelligence';"
```

### Quality Tests Failing

**Check sample validity:**
```bash
python3 /home/workspace/Intelligence/scripts/validate_samples.py
```

**Update expected outputs:**
```bash
# Re-generate expected output for a sample
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-file test_samples/inputs/B01_sample.json \
  --output-file test_samples/expected_outputs/B01_expected_new.md
```

### Low Quality Scores

1. **Review prompt**: Check if prompt is clear and specific
2. **Check samples**: Ensure sample data is representative
3. **Adjust threshold**: May need to tune similarity threshold in tests
4. **Update prompt**: Iterate on prompt based on output quality

## Performance

### Generation Times

Average generation time per block: ~2-5 seconds (depends on model and transcript length)

### Optimization Tips

1. **Batch processing**: Generate multiple blocks in parallel
2. **Caching**: Consider caching commonly-used blocks
3. **Model selection**: Balance quality vs speed based on use case

## System Maintenance

### Weekly Tasks

- Run quality tests on critical blocks (B01, B02, B08, B40)
- Review any failing tests
- Check generation history for anomalies

### Monthly Tasks

- Run full regression suite (all blocks)
- Review coverage gaps
- Add new quality samples for uncovered blocks
- Update prompts based on learnings

### Pre-deployment Tasks

- Run complete integration test suite
- Verify 100% test pass rate
- Review generation logs for errors
- Update documentation if needed

## Support & Issues

For issues or questions:
1. Check this documentation
2. Review completion reports in Intelligence directory
3. Check generation history in blocks.db
4. Review quality sampling strategy document

## License & Credits

Developed for internal use at Careerspan.
Built on the N5 architectural framework.

---

**Last Updated**: 2025-11-03  
**System Version**: 1.0  
**Total Blocks**: 37 active production blocks
