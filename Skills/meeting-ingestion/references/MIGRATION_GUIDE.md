---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
provenance: con_EHo97McpEpE09T3Z
---

# Migration Guide: Meeting Ingestion v2 → v3

Complete guide for migrating from Meeting Ingestion v2 to the new v3 pipeline with calendar triangulation, quality gates, and intelligent block selection.

## Overview of Changes

### Major Improvements in v3

**Pipeline Architecture:**
- v2: `pull → stage → process → archive`
- v3: `ingest → identify → gate → process → archive`

**State Management:**
- v2: Folder name suffixes (`_[P]`, `_[B]`, `_[M]`)
- v3: `manifest.json` with versioned schema

**Block Selection:**
- v2: Fixed block lists based on meeting type
- v3: Intelligent LLM-powered selector with conditional blocks

**Quality Assurance:**
- v2: Basic validation
- v3: 16-check quality gate with HITL escalation

**Participant Identification:**
- v2: Heuristic-based parsing
- v3: Calendar triangulation + CRM enrichment

### Backward Compatibility

✅ **Fully Compatible:** v3 can process existing v2 meeting folders  
✅ **Automatic Conversion:** v2 folders are seamlessly upgraded to v3  
✅ **Legacy Commands:** All v2 CLI commands still work  
✅ **Existing Archives:** Weekly folders remain unchanged

## Pre-Migration Checklist

### 1. Backup Current System

```bash
# Create full backup of current meetings
cd /home/workspace
tar -czf /tmp/meetings-backup-v2.tar.gz Personal/Meetings/

# Backup any custom configurations
cp -r N5/config/meeting_* /tmp/config-backup-v2/

# Export current statistics (optional)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py stats --export /tmp/v2-stats.json 2>/dev/null || echo "v2 stats not available"
```

### 2. Verify Prerequisites

```bash
# Check Python version (3.8+ required)
python3 --version

# Verify Google Calendar API access  
python3 -c "import google.auth; print('✅ Google Auth available')" 2>/dev/null || echo "❌ Install google-auth-oauthlib"

# Check Zo API token
echo $ZO_CLIENT_IDENTITY_TOKEN | wc -c  # Should be >100 characters

# Verify disk space (need 10-20% extra for migration)
df -h Personal/Meetings/
```

### 3. Document Current State

```bash
# Count current meetings by state (v2)
find Personal/Meetings/Inbox/ -type d -name "*_[P]" | wc -l  # Processing
find Personal/Meetings/Inbox/ -type d -name "*_[B]" | wc -l  # Blocked  
find Personal/Meetings/Inbox/ -type d -name "*_[M]" | wc -l  # Manual
find Personal/Meetings/Inbox/ -type d -name "*" -not -name "_*" | grep -v "\[" | wc -l  # Complete

# List any orphaned files
find Personal/Meetings/Inbox/ -maxdepth 1 -type f -name "*.md" | head -10
```

## Migration Process

### Phase 1: Install v3 System

The v3 system is already installed as part of the `meeting-system-v3` build. The migration happens automatically during normal processing.

### Phase 2: Verify v3 Installation

```bash
# Check v3 CLI is working
python3 Skills/meeting-ingestion/scripts/meeting_cli.py --version

# Verify new modules
python3 Skills/meeting-ingestion/scripts/quality_gate.py --self-test
python3 Skills/meeting-ingestion/scripts/block_selector.py --help
python3 Skills/meeting-ingestion/scripts/calendar_match.py test-connection

# Check HITL queue system
python3 Skills/meeting-ingestion/scripts/hitl.py status
```

### Phase 3: Test Migration (Dry Run)

```bash
# Test v3 on a single v2 meeting
V2_MEETING=$(find Personal/Meetings/Inbox/ -type d -name "*_[P]" | head -1)
echo "Testing migration on: $V2_MEETING"

# Run v3 identify on v2 folder (converts automatically)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py identify "$V2_MEETING" --dry-run

# Verify conversion worked
if [ -f "$V2_MEETING/manifest.json" ]; then
    echo "✅ Manifest created successfully"
    python3 Skills/meeting-ingestion/scripts/validate_manifest.py "$V2_MEETING/manifest.json"
else
    echo "❌ Migration test failed"
fi
```

### Phase 4: Migrate Processing Queue

```bash
# Switch to v3 pipeline gradually
echo "Migrating processing queue..."

# Process v2 meetings with v3 pipeline (this converts them)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py tick --batch-size 5

# Monitor progress
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status --detailed
```

### Phase 5: Update Scheduled Agent

The Meeting Orchestrator v3 agent is already updated as part of the build. The old MG-* agents have been disabled.

### Phase 6: Verify Migration Success

```bash
# Check all meetings have manifests
find Personal/Meetings/Inbox/ -type d -not -name "_*" -exec test ! -f {}/manifest.json \; -print | head -5

# Verify v3 state tracking is working
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status

# Check for any conversion errors
grep -r "conversion_error" Personal/Meetings/Inbox/ 2>/dev/null || echo "✅ No conversion errors"

# Test new features
python3 Skills/meeting-ingestion/scripts/hitl.py status
python3 Skills/meeting-ingestion/scripts/quality_gate.py --stats day
```

## Command Mapping

### v2 → v3 Command Translation

| v2 Command | v3 Equivalent | Notes |
|------------|---------------|-------|
| `pull` | `pull` | ✅ Unchanged |
| `stage` | `ingest` | 🔄 Enhanced with manifest creation |
| `process` | `identify` + `gate` + `process` | 🆕 Split into multiple stages |
| `archive` | `archive` | ✅ Enhanced with collision detection |
| `status` | `status` | 🔄 Enhanced with v3 states |
| `fix` | `fix` | 🔄 Enhanced with manifest repair |

### Updated Workflows

**v2 Daily Workflow:**
```bash
# Old way
python3 Scripts/meeting_cli.py pull --batch-size 5
python3 Scripts/meeting_cli.py stage  
python3 Scripts/meeting_cli.py process --batch-size 5
python3 Scripts/meeting_cli.py archive --execute
```

**v3 Daily Workflow:**
```bash
# New way (automated)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py tick

# Or manual (for debugging)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --batch-size 5
python3 Skills/meeting-ingestion/scripts/meeting_cli.py ingest .
for meeting in $(find Personal/Meetings/Inbox/ -type d -name "2026-*" -exec test -f {}/manifest.json \; -print); do
    python3 Skills/meeting-ingestion/scripts/meeting_cli.py identify "$meeting"
    python3 Skills/meeting-ingestion/scripts/meeting_cli.py gate "$meeting"  
    python3 Skills/meeting-ingestion/scripts/meeting_cli.py process "$meeting"
done
python3 Skills/meeting-ingestion/scripts/meeting_cli.py archive --execute
```

## Manifest Conversion

### v2 → v3 State Mapping

| v2 State | v2 Indicator | v3 Status | v3 Manifest Field |
|----------|--------------|-----------|-------------------|
| Raw file | `meeting.md` | `raw` | `"status": "raw"` |
| Staged | `Meeting/` folder | `ingested` | `"status": "ingested"` |
| Processing | `Meeting_[P]/` | `processing` | `"status": "identified"/"gated"` |
| Blocked | `Meeting_[B]/` | `hitl_pending` | `"status": "hitl_pending"` |
| Manual | `Meeting_[M]/` | `hitl_pending` | `"status": "hitl_pending"` |
| Complete | `Meeting/` with blocks | `processed` | `"status": "processed"` |

### Manifest Schema Differences

**v2 (folder-based state):**
```
2026-01-26_David-x-Careerspan_[P]/
├── transcript.md
├── B01_DETAILED_RECAP.md
└── B05_ACTION_ITEMS.md
```

**v3 (manifest-based state):**
```
2026-01-26_David-x-Careerspan/
├── transcript.md
├── manifest.json              # 🆕 v3 schema
├── B01_DETAILED_RECAP.md
└── B05_ACTION_ITEMS.md
```

**Sample v3 manifest.json:**
```json
{
  "manifest_version": "3.0",
  "meeting_id": "2026-01-26_David-x-Careerspan",
  "date": "2026-01-26", 
  "participants": [
    {"name": "David", "role": "external", "confidence": 0.95},
    {"name": "V", "role": "host", "confidence": 1.0}
  ],
  "meeting_type": "external",
  "status": "processed",
  "conversion": {
    "from_v2": true,
    "original_suffix": "_[P]",
    "converted_at": "2026-02-09T10:30:00Z"
  }
}
```

## Feature Migration

### Block Selection Changes

**v2 Block Selection:**
- Fixed lists per meeting type
- Manual block specification
- All-or-nothing generation

**v3 Block Selection:**
- Intelligent LLM-powered selection
- Conditional blocks based on content
- Recipe-based defaults with smart overrides

**Migration Impact:**
- Existing blocks are preserved
- Future processing uses smart selection
- Can manually override with `--blocks` flag

### Quality Assurance Upgrade

**v2 Quality Checks:**
- Basic transcript validation
- Manual error detection

**v3 Quality Gate:**
- 16 automated quality checks
- HITL escalation for uncertain cases
- Confidence scoring and thresholds

**Migration Actions:**
1. Existing meetings bypass quality gate (assumed valid)
2. New meetings go through full quality validation  
3. HITL queue handles uncertainty automatically

### Participant Identification Improvements

**v2 Identification:**
- Regex-based speaker parsing
- Manual participant resolution

**v3 Identification:**
- Calendar triangulation via Google Calendar API
- CRM enrichment with confidence scoring
- Automated HITL escalation for unknown speakers

**Migration Steps:**
1. CRM database is automatically created from existing meetings
2. Calendar matching applied retroactively where possible
3. Unknown participants escalated to HITL queue

## Troubleshooting Migration Issues

### Common Migration Problems

#### Issue: "No manifest.json found"

**Symptom:** v3 commands fail on v2 meetings  
**Cause:** Automatic conversion didn't trigger  
**Solution:**
```bash
# Force conversion
python3 Skills/meeting-ingestion/scripts/manifest_converter.py convert <v2-meeting-folder>

# Verify conversion
python3 Skills/meeting-ingestion/scripts/validate_manifest.py <meeting-folder>/manifest.json
```

#### Issue: "Suffix conversion failed"

**Symptom:** `_[P]` folders not being processed  
**Cause:** Conversion script doesn't recognize v2 state  
**Solution:**
```bash
# Manual state conversion
python3 Skills/meeting-ingestion/scripts/manifest_converter.py fix-suffix <meeting-folder>

# Remove suffix after conversion
mv "Meeting_[P]" "Meeting"
```

#### Issue: "HITL queue overflowing"

**Symptom:** Too many meetings escalated during migration  
**Cause:** Low confidence thresholds for legacy data  
**Solution:**
```bash
# Temporarily lower HITL thresholds
python3 Skills/meeting-ingestion/scripts/hitl.py tune-thresholds --migration-mode

# Batch process low-risk items
python3 Skills/meeting-ingestion/scripts/hitl.py batch-resolve --priority P2 --auto-confirm
```

#### Issue: "Block generation inconsistency"

**Symptom:** Different blocks generated for same meeting type  
**Cause:** Smart selector vs. legacy fixed lists  
**Solution:**
```bash
# Use legacy mode for consistent behavior
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process <meeting> --recipe external_standard --skip-smart

# Or force specific blocks
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process <meeting> --blocks B01,B05,B08
```

### Recovery Procedures

#### Rollback to v2 (Emergency Only)

```bash
# Stop v3 processing
python3 /home/workspace/N5/scripts/agents.py disable <meeting-orchestrator-v3-id>

# Restore v2 backup
cd /home/workspace
tar -xzf /tmp/meetings-backup-v2.tar.gz

# Remove v3 manifests
find Personal/Meetings/Inbox/ -name "manifest.json" -delete

# Re-enable v2 agent (if available)
# python3 /home/workspace/N5/scripts/agents.py enable <legacy-meeting-agent-id>
```

#### Partial Migration Reset

```bash
# Reset specific meetings to v2 state  
python3 Skills/meeting-ingestion/scripts/manifest_converter.py revert <meeting-folder>

# Remove v3-specific data
rm <meeting-folder>/manifest.json

# Restore v2 suffix if needed
mv "Meeting" "Meeting_[P]"
```

#### Database Recovery

```bash
# Rebuild CRM database from v2 data
python3 Skills/meeting-ingestion/scripts/crm_enricher.py rebuild --from-v2-meetings

# Rebuild meeting registry
python3 Skills/meeting-ingestion/scripts/meeting_cli.py rebuild-registry --scan-all-meetings

# Verify database integrity
sqlite3 Personal/Knowledge/CRM/crm.db "PRAGMA integrity_check;"
sqlite3 N5/data/meeting_registry.db "PRAGMA integrity_check;"
```

## Post-Migration Optimization

### Performance Tuning

```bash
# Optimize database performance
sqlite3 Personal/Knowledge/CRM/crm.db "VACUUM; REINDEX; ANALYZE;"
sqlite3 N5/data/meeting_registry.db "VACUUM; REINDEX; ANALYZE;"

# Establish v3 performance baselines
python3 Skills/meeting-ingestion/scripts/meeting_cli.py benchmark --establish-baseline

# Configure optimal batch sizes
python3 Skills/meeting-ingestion/scripts/meeting_cli.py benchmark --batch-sizes 1,3,5,10
```

### Quality Threshold Calibration

```bash
# Analyze quality gate performance on migrated data
python3 Skills/meeting-ingestion/scripts/quality_gate.py --stats week

# Adjust thresholds based on V's preferences  
python3 Skills/meeting-ingestion/scripts/quality_gate.py --recalibrate --sample-size 50

# Review HITL escalation patterns
python3 Skills/meeting-ingestion/scripts/hitl.py analytics --period week
```

### Block Selector Training

```bash
# Analyze block selection patterns on historical data
python3 Skills/meeting-ingestion/scripts/block_selector.py --analyze-historical --weeks 8

# Update priority relevance based on recent focus
python3 Skills/meeting-ingestion/scripts/block_selector.py --update-priorities --from-calendar

# Optimize recipe definitions
python3 Skills/meeting-ingestion/scripts/block_selector.py --optimize-recipes --sample-period 30d
```

## Feature Adoption Timeline

### Week 1: Core Migration
- ✅ v3 system installed
- ✅ Existing meetings converted
- ✅ Basic pipeline functional
- 🎯 Goal: No processing interruption

### Week 2: Quality Gate Training  
- 🎯 Calibrate quality thresholds
- 🎯 Process HITL queue efficiently
- 🎯 Train on edge cases

### Week 3: Smart Block Selection
- 🎯 Review block selection accuracy
- 🎯 Tune conditional block triggers
- 🎯 Optimize for V's priorities

### Week 4: Full Optimization
- 🎯 Performance baseline established
- 🎯 All v3 features operational  
- 🎯 Maintenance procedures documented

## Monitoring Post-Migration

### Daily Checks

```bash
# Migration health check
python3 Skills/meeting-ingestion/scripts/meeting_cli.py health-check --migration-report

# Quality gate performance
python3 Skills/meeting-ingestion/scripts/quality_gate.py --stats today

# HITL queue status  
python3 Skills/meeting-ingestion/scripts/hitl.py status --summary
```

### Weekly Reviews

```bash
# Block selection accuracy review
python3 Skills/meeting-ingestion/scripts/block_selector.py --accuracy-report --week

# Performance comparison with v2 baseline
python3 Skills/meeting-ingestion/scripts/meeting_cli.py benchmark --compare-to-v2

# Migration completeness check
find Personal/Meetings/Inbox/ -type d -not -name "_*" -exec test ! -f {}/manifest.json \; -print | wc -l
```

### Monthly Optimization

```bash
# Full system optimization review
python3 Skills/meeting-ingestion/scripts/meeting_cli.py optimize --full-analysis

# Quality threshold adjustment
python3 Skills/meeting-ingestion/scripts/quality_gate.py --recalibrate --month-sample

# Archive structure validation
python3 Skills/meeting-ingestion/scripts/archive.py --verify --weeks 8 --migration-check
```

## Success Criteria

### Migration Complete When:

✅ **All v2 meetings have manifest.json files**  
✅ **No folder name suffixes remain (`_[P]`, `_[B]`, `_[M]`)**  
✅ **HITL queue size <10 items consistently**  
✅ **Quality gate pass rate >80%**  
✅ **Block generation success rate >95%**  
✅ **No v2-related errors in logs for 7 days**  
✅ **Meeting Orchestrator v3 running successfully**  
✅ **Daily pipeline completing within 30 minutes**  

### Performance Targets:

- **Ingest time**: <30 seconds per meeting
- **Identify time**: <60 seconds per meeting  
- **Quality gate time**: <10 seconds per meeting
- **Process time**: <5 minutes per meeting
- **Archive time**: <10 seconds per meeting
- **Total pipeline**: <6 minutes per meeting average

## Getting Help

### Documentation References
- **SKILL.md**: Complete v3 feature documentation
- **CLI_REFERENCE.md**: All command syntax and options
- **RUNBOOK.md**: Operations and troubleshooting
- **quality-harness-checks.md**: Quality gate specification
- **hitl-queue-spec.md**: HITL system documentation

### Troubleshooting Resources
```bash
# Get help with any command
python3 Skills/meeting-ingestion/scripts/meeting_cli.py --help
python3 Skills/meeting-ingestion/scripts/hitl.py --help

# Enable debug logging
export MEETING_DEBUG=1
python3 Skills/meeting-ingestion/scripts/meeting_cli.py tick --dry-run

# Generate diagnostic report
python3 Skills/meeting-ingestion/scripts/meeting_cli.py diagnose --full-report /tmp/migration-diagnosis.txt
```

### Common Questions

**Q: Can I use both v2 and v3 commands?**  
A: Yes, v3 is fully backward compatible. v2 commands work on v3 data.

**Q: What happens to existing scheduled agents?**  
A: Legacy MG-* agents are disabled. Meeting Orchestrator v3 handles all automation.

**Q: Are my existing blocks affected?**  
A: No, existing block files are preserved unchanged. Only new processing uses v3 features.

**Q: Can I revert the migration?**  
A: Yes, see "Recovery Procedures" section. Keep your backup for 30 days.

**Q: How do I handle HITL queue items?**  
A: See `hitl.py` commands. Most can be auto-resolved or batch-processed.

---

*Meeting Ingestion Migration Guide v1.0 | February 2026 | From meeting-system-v3 build*