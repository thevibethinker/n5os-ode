# Worker 6: Main Orchestrator & Integration

**Mission:** Orchestrate full pipeline + scheduled task setup  
**Time Estimate:** 60 minutes  
**Dependencies:** Workers 1-5 (all must be complete)  
**Parallelizable:** No

---

## Objectives

1. ✅ Build main orchestrator: `N5/scripts/reflection_orchestrator_v2.py`
2. ✅ Integrate all components into single pipeline
3. ✅ Create registry tracking system
4. ✅ Set up scheduled task for automated ingestion
5. ✅ Create command shortcut
6. ✅ Write comprehensive documentation

---

## Deliverables

### 1. Main Orchestrator Script

**File:** `N5/scripts/reflection_orchestrator_v2.py`

**Requirements:**
- Orchestrate full pipeline: ingest → classify → generate → track
- Support manual and automated modes
- Comprehensive logging
- Dry-run support
- Error recovery

**Pipeline Flow:**
```python
def run_pipeline(dry_run: bool = False) -> dict:
    """
    Full reflection processing pipeline.
    
    Returns summary of work done.
    """
    
    summary = {
        "ingested": 0,
        "classified": 0,
        "blocks_generated": 0,
        "errors": []
    }
    
    # Step 1: Ingest new files from Drive
    logger.info("Step 1: Ingesting files from Drive...")
    ingest_result = subprocess.run([
        "python3", "/home/workspace/N5/scripts/reflection_ingest_v2.py",
        "--dry-run" if dry_run else ""
    ], capture_output=True, text=True)
    
    if ingest_result.returncode != 0:
        summary["errors"].append(f"Ingestion failed: {ingest_result.stderr}")
        return summary
    
    # Count new files
    new_files = list(Path("/home/workspace/N5/records/reflections/incoming").glob("*.jsonl"))
    summary["ingested"] = len(new_files)
    
    if len(new_files) == 0:
        logger.info("No new files to process")
        return summary
    
    # Step 2: Classify each reflection
    logger.info(f"Step 2: Classifying {len(new_files)} reflections...")
    for transcript_file in new_files:
        classify_result = subprocess.run([
            "python3", "/home/workspace/N5/scripts/reflection_classifier.py",
            "--input", str(transcript_file),
            "--output", str(transcript_file.with_suffix(".classification.json"))
        ], capture_output=True, text=True)
        
        if classify_result.returncode == 0:
            summary["classified"] += 1
        else:
            summary["errors"].append(f"Classification failed for {transcript_file.name}")
    
    # Step 3: Generate blocks
    logger.info(f"Step 3: Generating blocks for {summary['classified']} reflections...")
    generate_result = subprocess.run([
        "python3", "/home/workspace/N5/scripts/reflection_block_generator.py",
        "--process-all",
        "--dry-run" if dry_run else ""
    ], capture_output=True, text=True)
    
    if generate_result.returncode != 0:
        summary["errors"].append(f"Block generation failed: {generate_result.stderr}")
        return summary
    
    # Count blocks generated
    output_dirs = list(Path("/home/workspace/N5/records/reflections/outputs").glob("*/*/blocks"))
    summary["blocks_generated"] = sum(len(list(d.glob("*.md"))) for d in output_dirs)
    
    # Step 4: Run pattern detection
    logger.info("Step 4: Running pattern detection...")
    suggester_result = subprocess.run([
        "python3", "/home/workspace/N5/scripts/reflection_block_suggester.py",
        "--days", "30",
        "--min-frequency", "3"
    ], capture_output=True, text=True)
    
    # Step 5: Update registry
    logger.info("Step 5: Updating reflection registry...")
    update_registry(new_files, summary)
    
    # Step 6: Move processed files
    logger.info("Step 6: Archiving processed files...")
    archive_processed_files(new_files)
    
    return summary
```

---

### 2. Reflection Registry

**File:** `N5/records/reflections/registry/reflection_registry.jsonl`

**Format:** One JSON object per line, one per processed reflection

```json
{
  "reflection_id": "2025-10-24_pricing-strategy",
  "ingested_at_iso": "2025-10-24T20:15:00Z",
  "source_file": "Pricing Strategy Reflection.m4a",
  "drive_file_id": "xyz123",
  "classifications": ["market_analysis", "product_analysis", "strategic"],
  "blocks_generated": ["B71", "B72", "B73"],
  "output_directory": "N5/records/reflections/outputs/2025-10-24/pricing-strategy",
  "approval_status": "awaiting_approval",
  "word_count": 1324,
  "processed_by": "reflection_orchestrator_v2",
  "version": "2.0"
}
```

---

### 3. Scheduled Task

**Use scheduled task protocol:**
- Load: `file 'N5/prefs/operations/scheduled-task-protocol.md'`

**Task Configuration:**
```yaml
schedule: "7 */6 * * *"  # Every 6 hours at :07 (4x daily)
instruction: |
  Run the reflection processing pipeline to ingest new reflections from Google Drive,
  classify them, generate blocks, and update the registry.
  
  Execute: python3 /home/workspace/N5/scripts/reflection_orchestrator_v2.py
  
  Email me a summary of:
  - Number of new reflections processed
  - Block types generated
  - Any errors encountered
  - Link to outputs awaiting approval
delivery_method: email
```

**Create task:**
```bash
create_scheduled_task(
  rrule="FREQ=DAILY;INTERVAL=6;BYHOUR=0,6,12,18;BYMINUTE=7",
  instruction="Run reflection processing pipeline...",
  delivery_method="email"
)
```

---

### 4. Command Shortcut

**File:** `N5/commands/reflection-process.md`

```markdown
---
category: content
priority: high
description: Process reflections from Google Drive through full V2 pipeline
---
# Reflection Process

Run full reflection processing pipeline (V2):
1. Ingest from Drive
2. Classify reflections
3. Generate blocks
4. Detect patterns
5. Update registry

## Usage

```bash
python3 /home/workspace/N5/scripts/reflection_orchestrator_v2.py [--dry-run]
```

## Output

Results saved to:
- `N5/records/reflections/outputs/{date}/{slug}/blocks/`
- Registry: `N5/records/reflections/registry/reflection_registry.jsonl`
- Suggestions: `N5/records/reflections/suggestions/block_suggestions.jsonl`

## Manual Review

Outputs awaiting approval: file 'N5/records/reflections/outputs/'
```

---

### 5. Documentation

**File:** `N5/Documentation/reflection-system-v2.md`

Comprehensive guide covering:
- System overview
- Architecture diagram
- Component descriptions
- Usage instructions
- Troubleshooting
- Extension guide (adding new blocks)

---

## Testing

### End-to-End Test
1. Place test audio file in Drive folder
2. Run orchestrator manually
3. Verify:
   - File downloaded
   - Transcription created
   - Classification generated
   - Blocks created
   - Registry updated
   - Output directory structured correctly
4. Run again, verify no re-processing
5. Test scheduled task execution

---

## Scheduled Task Protocol Compliance

Per `file 'N5/prefs/operations/scheduled-task-protocol.md'`:

✅ **Safety Requirements:**
- Dry-run tested before production
- No destructive operations without backups
- State tracking prevents duplicates
- Error handling comprehensive

✅ **Instruction Structure:**
- Clear, direct command
- Self-contained (no external dependencies)
- Includes success criteria
- Specifies delivery method

✅ **Testing Checklist:**
- Manual execution tested
- Dry-run mode works
- Error scenarios handled
- Output format validated
- Delivery method confirmed

✅ **Documentation:**
- Command reference created
- System documentation complete
- Troubleshooting guide included

---

## Integration Points

**Upstream:**
- Google Drive (source)
- Existing transcription tools

**Downstream:**
- Knowledge system (insights extraction)
- Social media posting (LinkedIn automation)
- Task system (action items)

**Future Enhancements:**
- Auto-post B80 (LinkedIn) blocks after approval
- Extract action items → task system
- Compound insights → Knowledge base
- Cross-reference with meeting blocks

---

## Principles Applied

- **P7 (Dry-Run):** Full pipeline supports dry-run
- **P15 (Complete Before Claiming):** Comprehensive testing before deployment
- **P17 (Test Production):** Scheduled task tested with real Drive folder
- **P18 (Verify State):** Registry tracking ensures no duplicates
- **P19 (Error Handling):** Comprehensive error handling throughout

---

## Success Criteria

Worker 6 is complete when:
1. ✅ Orchestrator script functional
2. ✅ Full pipeline tested end-to-end
3. ✅ Registry system working
4. ✅ Scheduled task created and tested
5. ✅ Command shortcut created
6. ✅ Documentation complete
7. ✅ System ready for production use

---

**Status:** Waiting for Workers 1-5  
**Created:** 2025-10-24
