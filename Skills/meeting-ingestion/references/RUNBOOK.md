---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
provenance: con_EHo97McpEpE09T3Z
---

# Meeting Ingestion v3 Operations Runbook

Comprehensive guide for monitoring, troubleshooting, and maintaining the Meeting Ingestion v3 pipeline.

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Pipeline Monitoring](#pipeline-monitoring)  
3. [Troubleshooting Guide](#troubleshooting-guide)
4. [HITL Queue Management](#hitl-queue-management)
5. [Emergency Procedures](#emergency-procedures)
6. [Maintenance Tasks](#maintenance-tasks)
7. [Performance Optimization](#performance-optimization)
8. [System Health Checks](#system-health-checks)

---

## Daily Operations

### Morning Check (Post-Orchestrator)

The Meeting Orchestrator v3 runs daily at 6 AM ET. Perform these checks around 7 AM ET:

```bash
# 1. Check orchestrator status
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status

# 2. Review any HITL items  
python3 Skills/meeting-ingestion/scripts/hitl.py status

# 3. Check for failed processing
grep -r "failed" Personal/Meetings/Inbox/*/manifest.json 2>/dev/null || echo "No failures"

# 4. Verify archive ran correctly
ls -la "Personal/Meetings/Week-of-$(date -d 'last monday' +%Y-%m-%d)/"
```

**Expected healthy output:**
```
Raw files (needs ingest): 0-3
Ingested (needs identify): 0-1
Identified (needs gate): 0-1  
Gated (needs process): 0-1
Processed (needs archive): 0-2
HITL queue: 0-2 pending items
No failures found
Archive folder exists with today's meetings
```

### Weekly Tasks (Mondays)

```bash
# 1. HITL queue cleanup (resolve stale items >7 days)
python3 Skills/meeting-ingestion/scripts/hitl.py cleanup --older-than 7d

# 2. Registry statistics review
python3 Skills/meeting-ingestion/scripts/meeting_cli.py stats --week

# 3. Archive folder verification  
python3 Skills/meeting-ingestion/scripts/archive.py --verify --weeks 4

# 4. System performance check
python3 Skills/meeting-ingestion/scripts/meeting_cli.py health-check
```

### Monthly Tasks

```bash
# 1. CRM database maintenance
sqlite3 Personal/Knowledge/CRM/crm.db "VACUUM; ANALYZE;"

# 2. Meeting registry optimization
sqlite3 N5/data/meeting_registry.db "VACUUM; ANALYZE;"

# 3. Archive storage audit
du -sh Personal/Meetings/Week-of-* | tail -12

# 4. Quality gate performance review
python3 Skills/meeting-ingestion/scripts/quality_gate.py --stats --month
```

---

## Pipeline Monitoring

### Real-time Monitoring Commands

```bash
# Pipeline status overview
python3 meeting_cli.py status

# Individual meeting status
python3 meeting_cli.py status <meeting-folder>

# Quality gate statistics  
python3 quality_gate.py --stats --today

# Block generation performance
python3 block_generator.py --stats --day

# HITL queue summary
python3 hitl.py status --summary
```

### Key Metrics to Watch

| Metric | Healthy Range | Alert Threshold | Action |
|--------|---------------|-----------------|---------|
| Daily ingest count | 0-10 | >20 | Check Drive API limits |
| Quality gate pass rate | 80-95% | <70% | Review quality thresholds |
| HITL queue size | 0-5 items | >15 items | Process HITL backlog |
| Block generation failures | 0-2% | >10% | Check Zo API token |
| Archive success rate | >95% | <90% | Check disk space |

### Log Locations

```bash
# Meeting Orchestrator v3 agent logs
grep "Meeting Orchestrator" /dev/shm/agents.log | tail -20

# Pipeline processing logs  
tail -f /dev/shm/meeting-ingestion.log

# Quality gate detailed logs
tail -f /dev/shm/quality-gate.log

# HITL queue activity
tail -f /dev/shm/hitl-queue.log
```

### Performance Monitoring

```bash
# Average processing times by stage
python3 meeting_cli.py perf-report --stages

# Block generation timing analysis  
python3 block_generator.py --timing-report --days 7

# Quality gate bottleneck analysis
python3 quality_gate.py --bottleneck-report

# Calendar API usage tracking
python3 calendar_match.py --usage-report --week
```

---

## Troubleshooting Guide

### Issue: Pipeline Stuck at Identification

**Symptoms:**
- Meetings stuck in "ingested" status for >2 hours
- Calendar triangulation failures
- Low participant confidence scores

**Diagnosis:**
```bash
# Check calendar API connectivity
python3 calendar_match.py --test-connection

# Review identification logs for specific meeting
python3 meeting_cli.py identify <meeting> --dry-run --verbose

# Check CRM database connectivity
sqlite3 Personal/Knowledge/CRM/crm.db "SELECT COUNT(*) FROM participants;"
```

**Common Causes & Solutions:**

1. **Calendar API Rate Limit**
   ```bash
   # Check quota usage
   python3 calendar_match.py --quota-status
   # Solution: Wait for quota reset or reduce batch size
   ```

2. **CRM Database Lock**
   ```bash
   # Check for locks
   lsof Personal/Knowledge/CRM/crm.db
   # Solution: Kill conflicting processes or restart
   ```

3. **Participant Name Parsing Issues**
   ```bash
   # Test participant extraction
   python3 ingest.py --test-participant-extraction <transcript>
   # Solution: Check transcript speaker labels format
   ```

### Issue: Quality Gate Failures

**Symptoms:**
- High HITL escalation rate (>20%)
- Meetings stuck in "identified" status
- Quality scores consistently <0.8

**Diagnosis:**
```bash
# Run quality gate with detailed output
python3 quality_gate.py <meeting>/manifest.json --verbose --debug

# Check individual quality checks
python3 quality_gate.py <meeting>/manifest.json --check-by-check

# Review quality thresholds
cat Skills/meeting-ingestion/references/quality-harness-checks.md
```

**Quality Check Troubleshooting:**

| Failed Check | Common Cause | Solution |
|--------------|--------------|----------|
| transcript_length | Short meeting (<5 min) | Adjust threshold or skip short meetings |
| participant_confidence | Unknown speakers | Add to CRM or improve speaker labeling |
| calendar_match_score | Meeting not in calendar | Manual calendar linking via HITL |
| transcript_encoding | File corruption | Re-download from Drive |

### Issue: Block Generation Failures

**Symptoms:**
- Meetings stuck in "gated" status
- Empty or incomplete block files
- High block generation failure rate

**Diagnosis:**
```bash
# Test Zo API connectivity
python3 block_generator.py --test-api

# Check block selector output
python3 block_selector.py <meeting> --debug

# Verify block prompts
python3 block_generator.py --verify-prompts

# Check individual block generation
python3 block_generator.py <meeting> --blocks B01 --verbose
```

**Common Causes & Solutions:**

1. **Zo API Token Issues**
   ```bash
   # Verify token
   echo $ZO_CLIENT_IDENTITY_TOKEN | wc -c  # Should be >100 chars
   # Solution: Refresh token from Zo settings
   ```

2. **Block Selector Issues**
   ```bash
   # Test selector logic
   python3 block_selector.py <meeting> --dry-run --debug
   # Solution: Check BLOCK_INDEX.yaml integrity
   ```

3. **Prompt Quality Issues**
   ```bash
   # Validate all block prompts
   python3 block_generator.py --validate-all-prompts
   # Solution: Fix malformed prompts in Prompts/Blocks/
   ```

### Issue: Archive Failures

**Symptoms:**
- Completed meetings not moving to Week-of folders
- Archive command returns errors
- Naming collisions

**Diagnosis:**
```bash
# Test archive operation
python3 meeting_cli.py archive --dry-run --verbose

# Check for naming collisions
python3 archive.py --check-collisions --weeks 4

# Verify archive folder permissions
ls -la Personal/Meetings/Week-of-*/
```

**Solutions:**
```bash
# Resolve naming collisions
python3 archive.py --resolve-collisions --suffix-strategy

# Fix permissions
chmod 755 Personal/Meetings/Week-of-*/

# Manual archive specific meeting
python3 archive.py --meeting <meeting-folder> --force
```

### Issue: HITL Queue Overflow

**Symptoms:**
- HITL queue >20 items
- Processing backlog building up
- SMS notification spam

**Immediate Actions:**
```bash
# Batch resolve low-priority items
python3 hitl.py batch-resolve --priority P2 --auto-dismiss

# Extend HITL timeout for borderline items
python3 hitl.py extend-timeout --priority P1 --hours 24

# Temporarily disable SMS notifications
python3 hitl.py disable-notifications --hours 4
```

**Long-term Solutions:**
1. **Lower quality thresholds** (temporary)
2. **Improve CRM data quality** 
3. **Enhance participant extraction logic**
4. **Batch process similar HITL items**

---

## HITL Queue Management

### Queue Operations

```bash
# View queue status
python3 hitl.py status [--priority P0|P1|P2] [--age <hours>]

# Process specific item
python3 hitl.py process <HITL_ID>

# Batch operations
python3 hitl.py batch-process --priority P1 --limit 5

# Auto-resolve items with high confidence
python3 hitl.py auto-resolve --confidence-threshold 0.85
```

### Resolution Workflows

**Unidentified Participant:**
```bash
# 1. Review transcript excerpt
python3 hitl.py show HITL-20260209-001

# 2. Add to CRM if new person
python3 crm_enricher.py add-participant "John Smith" --company "TechCorp" --role "external"

# 3. Resolve HITL item
python3 hitl.py resolve HITL-20260209-001 --participant "John Smith"

# 4. Reprocess meeting
python3 meeting_cli.py identify <meeting> --retry
```

**Calendar Match Failed:**
```bash
# 1. Manual calendar search
python3 calendar_match.py search --date 2026-02-09 --keywords "project meeting"

# 2. Link manually
python3 hitl.py resolve HITL-20260209-002 --calendar-event "abc123xyz"

# 3. Continue pipeline
python3 meeting_cli.py gate <meeting>
```

**Meeting Topic Unclear:**
```bash
# 1. Review meeting content
python3 hitl.py review HITL-20260209-003 --show-context

# 2. Set topic manually
python3 hitl.py resolve HITL-20260209-003 --topic "Strategy planning" --type "internal"

# 3. Continue pipeline
python3 meeting_cli.py gate <meeting>
```

### HITL Performance Tuning

```bash
# Analyze HITL patterns
python3 hitl.py analytics --period week

# Adjust escalation thresholds
python3 hitl.py tune-thresholds --decrease-sensitivity 0.05

# Review auto-resolution opportunities  
python3 hitl.py suggest-auto-rules --confidence 0.9
```

---

## Emergency Procedures

### Complete Pipeline Failure

**Symptoms:**
- Orchestrator agent failing repeatedly
- No meetings processing for >24 hours
- Critical system errors

**Emergency Actions:**
```bash
# 1. Stop orchestrator to prevent damage
python3 /home/workspace/N5/scripts/agents.py disable <orchestrator-agent-id>

# 2. Check system health
python3 meeting_cli.py health-check --full

# 3. Process manually if urgent
python3 meeting_cli.py tick --batch-size 1 --dry-run

# 4. Escalate to V if needed
python3 /home/workspace/N5/scripts/sms.py send "URGENT: Meeting pipeline failure. Manual intervention required."
```

### Drive API Quota Exceeded

**Symptoms:**
- Pull operations failing
- "Quota exceeded" errors
- No new transcripts downloading

**Actions:**
```bash
# 1. Check quota status
python3 pull.py --quota-status

# 2. Switch to manual processing of urgent items
python3 meeting_cli.py ingest <local-transcript> --priority urgent

# 3. Reduce batch sizes temporarily
python3 /home/workspace/N5/scripts/agents.py update <orchestrator-id> --instruction "tick --batch-size 2"

# 4. Wait for quota reset (usually 24 hours)
```

### Quality Gate System Failure

**Symptoms:**
- All meetings failing quality gate
- Quality scores = 0.0
- Gate process hanging

**Actions:**
```bash
# 1. Bypass quality gate temporarily (EMERGENCY ONLY)
python3 meeting_cli.py bypass-gate <meeting> --reason "system-failure"

# 2. Check quality gate system
python3 quality_gate.py --self-test

# 3. Reset quality gate thresholds
python3 quality_gate.py --reset-to-defaults

# 4. Reprocess affected meetings
find Personal/Meetings/Inbox -name manifest.json -exec grep -l "\"status\": \"identified\"" {} \; | xargs python3 meeting_cli.py gate
```

### Database Corruption

**Symptoms:**
- SQLite errors in logs
- CRM/Registry operations failing
- Inconsistent data states

**Recovery Actions:**
```bash
# 1. Backup corrupted databases
cp Personal/Knowledge/CRM/crm.db Personal/Knowledge/CRM/crm.db.corrupted.$(date +%Y%m%d)
cp N5/data/meeting_registry.db N5/data/meeting_registry.db.corrupted.$(date +%Y%m%d)

# 2. Attempt repair
sqlite3 Personal/Knowledge/CRM/crm.db ".recover" > crm_recovered.sql
sqlite3 Personal/Knowledge/CRM/crm.db < crm_recovered.sql

# 3. If repair fails, rebuild from manifests  
python3 meeting_cli.py rebuild-registry --scan-all-meetings

# 4. Rebuild CRM from known contacts
python3 crm_enricher.py rebuild --from-manifests Personal/Meetings/
```

---

## Maintenance Tasks

### Weekly Maintenance

```bash
# 1. Clean up processed logs (keep 30 days)
find /dev/shm/ -name "*meeting*log" -mtime +30 -delete

# 2. Optimize databases
sqlite3 Personal/Knowledge/CRM/crm.db "VACUUM; REINDEX; ANALYZE;"
sqlite3 N5/data/meeting_registry.db "VACUUM; REINDEX; ANALYZE;"

# 3. Archive old HITL items  
python3 hitl.py archive --older-than 30d --to-file N5/data/hitl-archive.jsonl

# 4. Verify manifest integrity
python3 validate_manifest.py Personal/Meetings/Inbox/ --recursive --fix-minor

# 5. Update statistics
python3 meeting_cli.py generate-stats --export N5/data/meeting-stats.json
```

### Monthly Maintenance

```bash
# 1. Full system health check
python3 meeting_cli.py health-check --full --report /tmp/health-$(date +%Y%m).txt

# 2. Performance baseline update
python3 meeting_cli.py benchmark --update-baseline

# 3. Clean up old Week-of folders (keep 1 year)
find Personal/Meetings/ -name "Week-of-*" -type d -mtime +365 -exec rm -rf {} \;

# 4. CRM database cleanup
python3 crm_enricher.py cleanup --remove-orphans --merge-duplicates

# 5. Block prompt performance analysis
python3 block_generator.py --prompt-analysis --export-recommendations
```

### Quarterly Maintenance

```bash
# 1. Full system rebuild test (on copy)
cp -r Personal/Meetings /tmp/meetings-backup
python3 meeting_cli.py full-rebuild --test-mode --backup-path /tmp/meetings-backup

# 2. Quality threshold recalibration
python3 quality_gate.py --recalibrate --sample-size 100

# 3. Block selector optimization
python3 block_selector.py --optimize-recipes --sample-period 90d

# 4. Archive format migration check
python3 archive.py --check-format-migration --suggest-upgrades
```

---

## Performance Optimization

### Batch Size Optimization

```bash
# Test different batch sizes
python3 meeting_cli.py benchmark-batches --sizes 1,3,5,10,20

# Optimal batch size calculation
python3 meeting_cli.py calculate-optimal-batch --api-limits --performance-target
```

**Recommended batch sizes:**
- **Ingest**: 10-20 (I/O bound)
- **Identify**: 5-10 (API limited) 
- **Gate**: 15-25 (CPU bound)
- **Process**: 3-5 (LLM API limited)
- **Archive**: 20-50 (I/O bound)

### API Rate Limit Management

```bash
# Monitor API usage
python3 meeting_cli.py api-usage --services calendar,zo-ask

# Implement adaptive rate limiting
python3 meeting_cli.py enable-adaptive-batching

# Pre-cache calendar data
python3 calendar_match.py cache-refresh --days 7
```

### Database Performance Tuning

```bash
# Analyze query performance  
sqlite3 N5/data/meeting_registry.db ".timer on" "SELECT * FROM meetings WHERE date > '2026-01-01';"

# Add missing indexes
python3 meeting_cli.py optimize-database --add-indexes

# Partition large tables (if >10k meetings)
python3 meeting_cli.py partition-tables --by-year
```

### Memory Usage Optimization

```bash
# Monitor memory usage
python3 meeting_cli.py memory-profile --stage process

# Enable streaming for large transcripts
python3 meeting_cli.py enable-streaming --min-size 1MB

# Cache optimization
python3 meeting_cli.py optimize-cache --max-size 500MB
```

---

## System Health Checks

### Automated Health Checks

Create a daily health check script:

```bash
#!/bin/bash
# /home/workspace/Scripts/meeting_health_check.sh

echo "=== Meeting Ingestion v3 Health Check ==="
echo "Date: $(date)"
echo

# 1. Pipeline status
echo "1. Pipeline Status:"
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status | head -10
echo

# 2. API connectivity  
echo "2. API Connectivity:"
python3 Skills/meeting-ingestion/scripts/calendar_match.py --test-connection
python3 Skills/meeting-ingestion/scripts/block_generator.py --test-api
echo

# 3. Database integrity
echo "3. Database Integrity:"
sqlite3 Personal/Knowledge/CRM/crm.db "PRAGMA integrity_check;" | head -1
sqlite3 N5/data/meeting_registry.db "PRAGMA integrity_check;" | head -1  
echo

# 4. Disk space
echo "4. Disk Space:"
df -h Personal/Meetings | tail -1
echo

# 5. Error summary
echo "5. Recent Errors:"
grep -c "ERROR" /dev/shm/meeting-*.log 2>/dev/null | head -5 || echo "No error logs"
echo

# 6. HITL queue status
echo "6. HITL Queue:"
python3 Skills/meeting-ingestion/scripts/hitl.py status --summary
echo

echo "=== Health Check Complete ==="
```

### Health Check Alerts

Set up automated alerts for critical issues:

```bash
# Create alert thresholds file
cat > /home/workspace/N5/config/meeting_alerts.yaml << 'EOF'
alerts:
  critical:
    - hitl_queue_size: 20
    - quality_gate_pass_rate: 0.6
    - api_error_rate: 0.1
    - processing_delay_hours: 24
    
  warning:  
    - hitl_queue_size: 10
    - quality_gate_pass_rate: 0.75
    - api_error_rate: 0.05
    - processing_delay_hours: 8

notification:
  sms: true
  email: false
  priority_hours: [6, 7, 8, 18, 19, 20]  # Only alert during these hours
EOF

# Implement health check with alerts
python3 meeting_cli.py health-check --config N5/config/meeting_alerts.yaml --alert
```

### Performance Baselines

Establish performance baselines for monitoring:

```bash
# Create initial baselines  
python3 meeting_cli.py benchmark --establish-baseline --output N5/data/meeting_baseline.json

# Compare current performance to baseline
python3 meeting_cli.py benchmark --compare-to-baseline --alert-threshold 20%

# Weekly performance report
python3 meeting_cli.py performance-report --period week --export N5/data/performance-$(date +%Y%m%d).json
```

**Baseline Metrics:**
- **Ingest time**: 5-15 seconds per meeting
- **Identify time**: 10-30 seconds per meeting  
- **Quality gate time**: 3-8 seconds per meeting
- **Block generation time**: 2-5 minutes per meeting (varies by block count)
- **Archive time**: 2-5 seconds per meeting

### Log Analysis

Regular log analysis to identify patterns:

```bash
# Daily error analysis
python3 meeting_cli.py analyze-logs --period today --export-issues

# Weekly performance trends
python3 meeting_cli.py analyze-logs --period week --performance-trends

# Monthly failure pattern analysis  
python3 meeting_cli.py analyze-logs --period month --failure-patterns
```

---

## Disaster Recovery

### Backup Procedures

```bash
# Daily backup of critical data
tar -czf /tmp/meeting-backup-$(date +%Y%m%d).tar.gz \
    Personal/Meetings/Inbox/ \
    Personal/Knowledge/CRM/ \
    N5/data/meeting_registry.db \
    N5/review/meetings/hitl-queue.jsonl

# Archive backup to secure location
cp /tmp/meeting-backup-$(date +%Y%m%d).tar.gz ~/Backups/meetings/
```

### Recovery Procedures

```bash
# Restore from backup
cd /tmp
tar -xzf meeting-backup-20260209.tar.gz
rsync -av Personal/ /home/workspace/Personal/
rsync -av N5/ /home/workspace/N5/

# Rebuild derived data
python3 meeting_cli.py rebuild-registry --full
python3 meeting_cli.py rebuild-cache --all
python3 meeting_cli.py health-check --full
```

---

*Meeting Ingestion v3 Operations Runbook | Version 1.0 | February 2026*