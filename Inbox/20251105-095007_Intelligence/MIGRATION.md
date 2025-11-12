# Intelligence System Migration Guide

Guide for migrating from old block generation tools to the new unified system.

## Overview

The Intelligence system consolidates 37+ previously disparate block generation tools into a single, unified, testable system with:

- Centralized database for all blocks, prompts, and generation history
- Auto-generated wrapper tools for each block type
- Quality assurance through regression testing
- Version control for prompts
- Comprehensive generation logging

## What Changed

### Before (Old System)
- Manual scripts for each block type
- No centralized prompt management
- No systematic testing
- No generation history
- Inconsistent interfaces
- Hard to maintain and update

### After (New System)
- Single generation engine for all blocks
- Database-driven prompts and configuration
- Automated quality testing
- Full generation history and audit trail
- Consistent CLI interface across all blocks
- Easy to add new block types

## Migration Steps

### Step 1: Identify Your Current Usage

**Old pattern:**
```bash
# Old way - custom scripts
python3 /path/to/detailed_recap_generator.py meeting.json > output.md
python3 /path/to/commitments_extractor.py meeting.json > commitments.md
```

**New pattern:**
```bash
# New way - unified wrapper tools
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-file meeting.json \
  --output-file output.md

/home/workspace/Intelligence/tools/generate-b02 \
  --meeting-file meeting.json \
  --output-file commitments.md
```

### Step 2: Map Old Tools to New Block IDs

| Old Tool/Function | New Block ID | New Wrapper Tool | Description |
|-------------------|--------------|------------------|-------------|
| detailed_recap_generator | B01 | generate-b01 | Comprehensive meeting summary |
| commitments_extractor | B02 | generate-b02 | Action items with context |
| stakeholder_profiler | B03 | generate-b03 | Stakeholder analysis |
| questions_tracker | B05 | generate-b05 | Outstanding questions |
| pilot_analyzer | B06 | generate-b06 | Pilot program intelligence |
| intro_facilitator | B07 | generate-b07 | Warm introduction helper |
| stakeholder_intel_deep | B08 | generate-b08 | Deep stakeholder intelligence |
| metrics_extractor | B11 | generate-b11 | Metrics snapshot |
| action_plan_builder | B13 | generate-b13 | Plan of action |
| content_snippets | B14 | generate-b14 | Blurbs requested |
| stakeholder_mapper | B15 | generate-b15 | Stakeholder map |
| key_moments_finder | B21 | generate-b21 | Key moments |
| product_insights | B24 | generate-b24 | Product idea extraction |
| deliverable_mapper | B25 | generate-b25 | Deliverable content map |
| meeting_metadata | B26 | generate-b26 | Meeting metadata summary |
| messaging_extractor | B27 | generate-b27 | Key messaging |
| research_analyzer | B31 | generate-b31 | Stakeholder research |
| internal_decisions | B40 | generate-b40 | Internal decisions |
| team_coordination | B41 | generate-b41 | Team coordination |
| market_intel | B42 | generate-b42 | Market/competitive intel |
| product_strategy | B43 | generate-b43 | Product intelligence |
| gtm_insights | B44 | generate-b44 | GTM/sales intel |
| ops_improvements | B45 | generate-b45 | Operations/process |
| hiring_strategy | B46 | generate-b46 | Hiring/team |
| open_debates | B47 | generate-b47 | Open debates |
| strategy_memo | B48 | generate-b48 | Strategic memo |
| personal_reflection | B50 | generate-b50 | Personal reflection |
| learning_capture | B60 | generate-b60 | Learning & synthesis |
| thought_leadership | B70 | generate-b70 | Thought leadership |
| market_analysis | B71 | generate-b71 | Market analysis |
| product_analysis | B72 | generate-b72 | Product analysis |
| strategic_thinking | B73 | generate-b73 | Strategic thinking |
| linkedin_post | B80 | generate-b80 | LinkedIn post |
| blog_post | B81 | generate-b81 | Blog post |
| exec_memo | B82 | generate-b82 | Executive memo |
| insight_compounding | B90 | generate-b90 | Insight compounding |
| meta_reflection | B91 | generate-b91 | Meta-reflection |

### Step 3: Update Your Scripts

**Before:**
```bash
#!/bin/bash
# old_pipeline.sh

python3 /old/path/detailed_recap_generator.py meeting.json > recap.md
python3 /old/path/commitments_extractor.py meeting.json > commitments.md
python3 /old/path/stakeholder_intel.py meeting.json > intel.md
```

**After:**
```bash
#!/bin/bash
# new_pipeline.sh

INTELLIGENCE_TOOLS="/home/workspace/Intelligence/tools"
MEETING_FILE="meeting.json"

$INTELLIGENCE_TOOLS/generate-b01 --meeting-file "$MEETING_FILE" --output-file recap.md
$INTELLIGENCE_TOOLS/generate-b02 --meeting-file "$MEETING_FILE" --output-file commitments.md
$INTELLIGENCE_TOOLS/generate-b08 --meeting-file "$MEETING_FILE" --output-file intel.md
```

### Step 4: Update Meeting Data Format

The new system uses a standardized JSON format:

**Old format (varied):**
```json
{
  "transcript": "...",
  "people": ["A", "B"]
}
```

**New format (standardized):**
```json
{
  "meeting_id": "MTG_20251103_001",
  "meeting_type": "external",
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

**Migration helper script:**
```python
#!/usr/bin/env python3
"""Convert old meeting format to new format."""

import json
import sys
from pathlib import Path

def migrate_meeting_format(old_data):
    """Convert old meeting data to new standardized format."""
    return {
        "meeting_id": old_data.get("id", "MIGRATED_MEETING"),
        "meeting_type": old_data.get("type", "external"),
        "date": old_data.get("date", "2025-01-01"),
        "participants": [
            {"name": p, "role": "Participant"}
            for p in old_data.get("people", old_data.get("participants", []))
        ],
        "transcript": old_data.get("transcript", ""),
        "duration_minutes": old_data.get("duration", 60),
        "context": {
            "company": old_data.get("company", "Unknown"),
            "project": old_data.get("project", "Unknown")
        }
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: migrate_format.py <old_meeting.json> [output.json]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix('.new.json')
    
    with open(input_file) as f:
        old_data = json.load(f)
    
    new_data = migrate_meeting_format(old_data)
    
    with open(output_file, 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"✓ Migrated {input_file} → {output_file}")
```

### Step 5: Update Workflows and Automations

**Update cron jobs:**
```bash
# Old crontab entry
0 9 * * * /usr/bin/python3 /old/path/daily_recap.py

# New crontab entry
0 9 * * * /home/workspace/Intelligence/tools/generate-b01 --meeting-file /path/to/meeting.json --output-file /path/to/recap.md
```

**Update CI/CD pipelines:**
```yaml
# Old GitHub Actions / CI config
- name: Generate recap
  run: python3 scripts/old_recap.py input.json > output.md

# New GitHub Actions / CI config
- name: Generate recap
  run: /home/workspace/Intelligence/tools/generate-b01 --meeting-file input.json --output-file output.md
```

## Backwards Compatibility

### Option 1: Wrapper Scripts

Create wrapper scripts that maintain old interface:

```bash
#!/bin/bash
# detailed_recap_generator.py (compatibility wrapper)
# Maintains old interface, calls new system

INPUT_FILE="$1"
/home/workspace/Intelligence/tools/generate-b01 --meeting-file "$INPUT_FILE"
```

### Option 2: Symlinks

```bash
# Create symlinks with old names
ln -s /home/workspace/Intelligence/tools/generate-b01 /old/path/detailed_recap_generator.py
ln -s /home/workspace/Intelligence/tools/generate-b02 /old/path/commitments_extractor.py
```

### Option 3: Alias Functions

Add to your `.bashrc` or `.zshrc`:

```bash
# Backwards compatibility aliases
alias detailed_recap='generate-b01'
alias extract_commitments='generate-b02'
alias stakeholder_intel='generate-b08'
```

## Testing Your Migration

### Step 1: Parallel Testing

Run old and new systems side-by-side:

```bash
# Generate with old system
python3 /old/detailed_recap.py meeting.json > old_output.md

# Generate with new system
/home/workspace/Intelligence/tools/generate-b01 \
  --meeting-file meeting.json \
  --output-file new_output.md

# Compare outputs
diff old_output.md new_output.md
```

### Step 2: Regression Testing

Use the built-in quality testing:

```bash
# Add your production meeting as a test sample
python3 /home/workspace/Intelligence/scripts/add_quality_sample.py \
  --block-id B01 \
  --meeting-id PROD_SAMPLE_001 \
  --type baseline \
  --input-file production_meeting.json \
  --output-file expected_output.md \
  --score 0.90 \
  --notes "Production migration validation"

# Run quality test
python3 /home/workspace/Intelligence/scripts/run_quality_tests.py --block-id B01
```

### Step 3: Integration Testing

```bash
# Test end-to-end pipeline
python3 /home/workspace/Intelligence/tests/integration_test.py --block-id B01
```

## Common Migration Issues

### Issue 1: Meeting Data Format Mismatch

**Symptom:** Generation fails with missing field errors

**Solution:** Use the format migration script above, or manually convert data:

```python
# Quick fix in your pipeline
import json

with open('old_meeting.json') as f:
    old_data = json.load(f)

new_data = {
    "meeting_id": "TEMP_" + old_data.get("id", "001"),
    "meeting_type": "external",
    "date": old_data.get("date", "2025-01-01"),
    "participants": [{"name": p, "role": "Participant"} for p in old_data.get("people", [])],
    "transcript": old_data["transcript"],
    "duration_minutes": old_data.get("duration", 60),
    "context": {}
}

with open('new_meeting.json', 'w') as f:
    json.dump(new_data, f)
```

### Issue 2: Different Output Format

**Symptom:** Output structure or formatting differs from old system

**Solution:** 
1. Review and update prompt in database if needed
2. Or post-process output to match old format:

```bash
# Post-process to match old formatting
/home/workspace/Intelligence/tools/generate-b01 --meeting-file meeting.json | \
  sed 's/^## /### /' > output.md  # Example: adjust heading levels
```

### Issue 3: Slower Generation

**Symptom:** New system takes longer

**Solution:**
1. Use parallel generation for multiple blocks
2. Consider model optimization
3. Batch multiple meetings if needed

```bash
# Parallel generation
/home/workspace/Intelligence/tools/generate-b01 --meeting-file m1.json --output-file o1.md &
/home/workspace/Intelligence/tools/generate-b02 --meeting-file m1.json --output-file o2.md &
wait
```

### Issue 4: Missing Block Type

**Symptom:** Old tool has no equivalent block

**Solution:** Add new block type (see README.md "Adding New Block Types")

## Rollback Plan

If you need to rollback to the old system:

1. **Keep old scripts**: Don't delete old tools until confident in migration
2. **Document changes**: Keep notes on what was changed
3. **Version control**: Use git to track migration changes
4. **Test thoroughly**: Complete parallel testing before decommissioning old system

## Post-Migration Checklist

- [ ] All old tools mapped to new block IDs
- [ ] Scripts updated to use new wrapper tools
- [ ] Meeting data format standardized
- [ ] Parallel testing completed successfully
- [ ] Integration tests passing
- [ ] Quality regression tests added
- [ ] Documentation updated
- [ ] Team trained on new system
- [ ] Monitoring in place
- [ ] Old tools deprecated/removed

## Benefits of Migration

### Improved Maintainability
- Single codebase for all blocks
- Centralized prompt management
- Version control for prompts
- Easy to update and extend

### Better Quality Assurance
- Automated regression testing
- Quality sample library
- Generation history tracking
- Performance monitoring

### Enhanced Developer Experience
- Consistent CLI interface
- Better error handling
- Comprehensive documentation
- Integration testing

### Operational Excellence
- Audit trail for all generations
- Easy rollback capabilities
- Performance metrics
- Quality metrics

## Support

If you encounter migration issues:

1. Review this migration guide
2. Check file `Intelligence/README.md` for system documentation
3. Review completion reports in Intelligence directory
4. Check generation logs in `blocks.db`

## Timeline Recommendation

- **Week 1**: Read documentation, identify usage patterns
- **Week 2**: Set up parallel testing, migrate test data
- **Week 3**: Migrate scripts and workflows, run integration tests
- **Week 4**: Full production migration, monitor performance
- **Week 5+**: Deprecate old tools, complete documentation

---

**Migration Guide Version**: 1.0  
**Last Updated**: 2025-11-03  
**System Version**: 1.0
