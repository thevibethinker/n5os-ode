# Meeting Intelligence Orchestrator

## Overview

The Meeting Intelligence Orchestrator is a production-ready system that extracts structured intelligence from meeting transcripts and generates modular, copyable blocks for follow-up emails.

## Features

- **✅ Real LLM Integration**: Structured prompts for each block type with fallback to simulation mode
- **✅ Modular Block Generation**: 10+ block types (recap, questions, debates, deliverables, etc.)
- **✅ Smart Speaker Detection**: Granola diarization detection (`Me:` / `Them:` format)
- **✅ Conditional Logic**: Generates blocks based on transcript content (warm intros, founder profiles, product ideas)
- **✅ Logging System**: Detailed logs for debugging and auditing
- **✅ Error Handling**: Graceful fallbacks when LLM extraction fails

## Installation

### Prerequisites
- Python 3.8+
- Required files:
  - Block Registry: `N5/prefs/block_type_registry.json`
  - Essential Links: `N5/prefs/communication/essential-links.json`

### Setup
```bash
# No installation needed - script is ready to use
cd /home/workspace
```

## Usage

### Basic Usage (Simulation Mode - for Testing)
```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=/path/to/transcript.txt \
  --meeting_id=meeting-2025-10-09 \
  --use-simulation
```

### Production Usage (Real LLM Extraction)
```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=/path/to/transcript.txt \
  --meeting_id=meeting-2025-10-09
```

### Advanced Options
```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=/home/workspace/transcripts/call.txt \
  --meeting_id=investor-pitch-2025-10-09 \
  --essential_links_path=/custom/path/essential-links.json \
  --block_registry_path=/custom/path/block_registry.json \
  --use-simulation  # Optional: use simulation mode for testing
```

## Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--transcript_path` | ✅ Yes | - | Path to the meeting transcript file |
| `--meeting_id` | ✅ Yes | - | Unique identifier for the meeting |
| `--essential_links_path` | No | `N5/prefs/communication/essential-links.json` | Path to essential links JSON file |
| `--block_registry_path` | No | `N5/prefs/block_type_registry.json` | Path to block registry JSON file |
| `--use-simulation` | No | `False` | Enable simulation mode for testing |

## Output

### Generated Files

1. **`blocks.md`** - Main output file with all extracted blocks
   - Location: `N5/records/meetings/{meeting_id}/blocks.md`
   
2. **Log File** - Debugging and audit trail
   - Location: `N5/logs/orchestrator_{meeting_id}.log`

### Block Types Generated

#### Always Generated (REQUIRED):
- **B26** - Meeting Metadata Summary (title, subject line, granola detection)
- **B01** - Detailed Recap (key decisions and agreements)
- **B08** - Resonance Points (what generated energy/enthusiasm)

#### High Priority (Generated when applicable):
- **B21** - Salient Questions (up to 5 strategic questions with action hints)
- **B22** - Debate/Tension Analysis (conflicting viewpoints and resolutions)

#### Conditional (Based on transcript content):
- **B24** - Product Idea Extraction (if product ideas discussed)
- **B29** - Key Quotes & Highlights (2-3 most impactful verbatim quotes)
- **B25** - Deliverable Content Map (promised items with send-with-email flags)
- **B14** - Blurbs Requested (for warm introductions - "send me a blurb")
- **B30** - Intro Email Template (for making introductions)
- **B28** - Founder Profile Summary (if startup/founder meeting)

## Transcript Format

### Supported Formats

#### 1. Granola-style (Recommended)
```
Me: Hey, how's the project going?
Them: Really well! We're making great progress.
Me: That's great to hear. What's the next milestone?
```

#### 2. Generic Speaker Labels
```
Speaker 1: Let's discuss the Q3 roadmap.
Speaker 2: Sounds good. I have some ideas.
```

#### 3. Named Speakers
```
Vrijen: How can Careerspan help?
Sofia: We need help with community partnerships.
```

## Example Workflow

```bash
# Step 1: Place transcript in meeting folder
mkdir -p N5/records/meetings/sofia-2025-10-09
cp /path/to/transcript.txt N5/records/meetings/sofia-2025-10-09/

# Step 2: Run orchestrator (simulation mode for testing)
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/sofia-2025-10-09/transcript.txt \
  --meeting_id=sofia-2025-10-09 \
  --use-simulation

# Step 3: Review output
cat N5/records/meetings/sofia-2025-10-09/blocks.md

# Step 4: Check logs if needed
cat N5/logs/orchestrator_sofia-2025-10-09.log
```

## Architecture

### Key Components

1. **`_extract_content_for_block(block_id)`**
   - Routes to real LLM or simulation based on `use_simulation` flag
   - Falls back to simulation if LLM extraction fails

2. **`_real_llm_extract(block_id, block_def)`**
   - Builds structured prompts using `_build_extraction_prompt()`
   - Calls `_call_llm()` with system and user prompts
   - Returns structured JSON data

3. **`_emit(block_id, variables)`**
   - Custom formatting logic for each block type
   - Transforms extracted data into markdown format

4. **`run()`**
   - Orchestrates the full extraction pipeline
   - Applies conditional logic for block generation
   - Assembles final markdown output

### Data Flow

```
Transcript → _extract_content_for_block()
           ↓
      [Real LLM / Simulation]
           ↓
      Structured JSON
           ↓
      _emit() transforms to markdown
           ↓
      Final blocks.md output
```

## Logging

Logs are written to: `N5/logs/orchestrator_{meeting_id}.log`

Example log entries:
```
[2025-10-09 22:48:12] Extracting content for block B01: DETAILED_RECAP
[2025-10-09 22:48:13] LLM extraction failed for B01, using simulation fallback
[2025-10-09 22:48:14] Generated block B21 with 2 salient questions
```

## Troubleshooting

### Issue: Empty blocks generated
**Solution**: Check logs for extraction errors. Use `--use-simulation` to verify extraction logic works.

### Issue: LLM extraction fails
**Solution**: System automatically falls back to simulation mode. Check logs for specific error messages.

### Issue: Missing blocks
**Solution**: Verify transcript contains relevant keywords for conditional blocks (e.g., "product", "startup", "introduce").

### Issue: Granola detection incorrect
**Solution**: Ensure transcript uses `Me:` and `Them:` speaker tags for Granola-style detection.

## Production Deployment

### Checklist

- [ ] Test with `--use-simulation` flag first
- [ ] Verify block registry is up to date (v1.2+)
- [ ] Ensure essential-links.json exists
- [ ] Create meeting directory structure
- [ ] Monitor logs for first few runs
- [ ] Validate output quality

### Integration Points

The orchestrator is designed to integrate with:
1. **Follow-Up Email Generator** - Consumes generated blocks
2. **Google Drive API** - For transcript and deliverable file resolution
3. **Google Calendar API** - For meeting metadata extraction
4. **Essential Links Companion** - For resolving shared resources

## Development

### Adding New Block Types

1. Add block definition to `N5/prefs/block_type_registry.json`
2. Add extraction logic to `_build_extraction_prompt()`
3. Add formatting logic to `_emit()`
4. Update simulation data in `_simulate_llm_extract()`
5. Test with `--use-simulation` flag

### Testing

```bash
# Run with simulation mode
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/test/transcript.txt \
  --meeting_id=test-run \
  --use-simulation

# Compare output with expected results
diff N5/records/meetings/test/blocks.md expected_output.md
```

## Version History

- **v1.5** (2025-10-09): Real LLM integration with fallback simulation
- **v1.4** (2025-10-09): All blocks generating correctly with proper formatting
- **v1.3** (2025-10-09): Added conditional block logic and warm intro detection
- **v1.2** (2025-10-09): Initial modular block system with simulation

## Support

For issues or questions:
1. Check logs: `N5/logs/orchestrator_{meeting_id}.log`
2. Review changelog: `N5/scripts/meeting_intelligence_orchestrator_CHANGELOG.md`
3. Test with simulation mode: `--use-simulation`

## License

Internal use only - Careerspan/N5 system