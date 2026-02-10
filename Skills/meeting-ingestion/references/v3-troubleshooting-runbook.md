---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
provenance: con_5x72M3IUnJTCLYfX
---

# Meeting System v3 Troubleshooting Runbook

Comprehensive troubleshooting guide for the meeting ingestion v3 pipeline with step-by-step diagnosis and resolution procedures.

## Quick Diagnostics

### System Health Check

```bash
# Check overall system status
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status

# Check scheduled agent status  
python3 N5/scripts/list_agents.py | grep "Meeting Orchestrator v3"

# Check HITL queue
python3 Skills/meeting-ingestion/scripts/hitl_manager.py status

# Check for recent errors
tail -n 50 /dev/shm/meeting-orchestrator.log
```

### Queue Status Interpretation

**Normal Queue Status:**
```
Pipeline Queue Status:
  Raw files: 0
  Ingested: 1-3 (normal backlog)
  Identified: 0-1 (processing)
  Gated: 0-2 (ready for blocks)
  Processed: 0-5 (ready for archive)
  
HITL Queue: 0 items
```

**Problem Indicators:**
- **High "Ingested" count (>5):** Calendar/CRM issues
- **High "Identified" count (>3):** Quality gate failures
- **HITL Queue >0:** Manual intervention needed
- **Agent not running:** Scheduled execution broken

## Pipeline Stage Issues

### Stage 1: Ingest Issues

#### Problem: Raw transcript won't ingest

**Symptoms:**
```
Error: Unable to parse transcript metadata
```

**Diagnosis:**
```bash
# Check file format and encoding
file /path/to/transcript.md
head -20 /path/to/transcript.md

# Try manual ingest with verbose output
python3 Skills/meeting-ingestion/scripts/ingest.py /path/to/transcript.md --verbose
```

**Common Causes & Solutions:**

1. **Invalid file encoding:**
   ```bash
   # Convert to UTF-8
   iconv -f ISO-8859-1 -t UTF-8 transcript.md > transcript_utf8.md
   ```

2. **Missing metadata:**
   - Check for date/time in filename or content
   - Manually add missing metadata to transcript header

3. **Unsupported format:**
   - Convert .docx/.pdf to .md using pandoc
   - Extract plain text and reformat

#### Problem: Meeting folder naming conflicts

**Symptoms:**
```
Error: Meeting folder already exists: 2026-02-09_Meeting-Name
```

**Solutions:**
```bash
# Check existing folder
ls -la "Personal/Meetings/Inbox/2026-02-09_Meeting-Name"

# If duplicate/orphan, move to quarantine
mv "Personal/Meetings/Inbox/2026-02-09_Meeting-Name" "Personal/Meetings/_orphaned/"

# Or append suffix if legitimate duplicate
python3 Skills/meeting-ingestion/scripts/ingest.py /path/to/transcript.md --suffix "-v2"
```

### Stage 2: Identification Issues

#### Problem: Calendar triangulation fails

**Symptoms:**
```
Meeting stuck at "ingested" status
Error: No calendar events found in time window
```

**Diagnosis:**
```bash
# Check calendar API access
python3 Skills/meeting-ingestion/scripts/calendar_match.py /path/to/manifest.json --verbose

# Check Google Calendar connection
python3 -c "
from use_app_google_calendar import list_app_tools
print(list_app_tools('google_calendar'))
"
```

**Common Causes & Solutions:**

1. **API quota exceeded:**
   ```bash
   # Check Google Cloud Console quotas
   # Wait for quota reset (usually daily)
   # Or use manual override in manifest
   ```

2. **No calendar events in time window:**
   ```bash
   # Check if calendar has events around meeting time
   # Manually verify in Google Calendar web interface
   # Adjust search window if needed
   ```

3. **Calendar authentication issues:**
   ```bash
   # Re-authenticate Google Calendar integration
   # Check [Settings > Integrations > Google Calendar](/?t=settings&s=integrations)
   ```

4. **Timestamp parsing errors:**
   ```json
   // Fix in manifest.json
   {
     "meeting": {
       "date": "2026-02-09",
       "time_utc": "15:00:00"  // Ensure proper format
     }
   }
   ```

**Manual Override:**
```json
// Add to manifest.json
{
  "calendar_match": {
    "event_id": "manual_override",
    "confidence": 0.8,
    "method": "manual",
    "override_reason": "Calendar API unavailable"
  }
}
```

#### Problem: CRM enrichment fails

**Symptoms:**
```
Error: Cannot access CRM database
Warning: Participant confidence below threshold (0.4)
```

**Diagnosis:**
```bash
# Check CRM database access
ls -la "Personal/Knowledge/Legacy_Inbox/crm/crm.db"

# Test CRM enricher directly
python3 Skills/meeting-ingestion/scripts/crm_enricher.py /path/to/meeting --verbose
```

**Solutions:**

1. **CRM database missing/corrupted:**
   ```bash
   # Restore from backup or recreate
   # Check if database moved to new location
   find /home/workspace -name "crm.db" 2>/dev/null
   ```

2. **Low participant confidence:**
   ```bash
   # Manual participant identification in manifest.json
   # Add known participants with proper email addresses
   # Increase confidence score manually if appropriate
   ```

### Stage 3: Quality Gate Issues

#### Problem: Quality gate validation fails

**Symptoms:**
```
Quality Gate: ❌ FAILED (Score: 0.65)
Failed checks: transcript_length, participant_confidence
```

**Diagnosis:**
```bash
# Run quality gate with verbose output
python3 Skills/meeting-ingestion/scripts/quality_gate.py /path/to/manifest.json --verbose

# Check individual quality checks
python3 Skills/meeting-ingestion/scripts/quality_gate.py /path/to/manifest.json --check transcript_length
```

**Quality Check Resolutions:**

1. **transcript_length failure (<300 chars):**
   ```bash
   # Check actual transcript content
   wc -c /path/to/meeting/transcript.md
   
   # If transcript is actually longer, check for parsing issues
   # If legitimately short, consider manual override or rejection
   ```

2. **participant_confidence failure (<0.7):**
   ```bash
   # Manual participant correction in manifest.json
   # Add missing participant emails
   # Increase confidence if identification is certain
   ```

3. **calendar_match failure (<0.6):**
   ```bash
   # Re-run calendar triangulation with different parameters
   # Manual calendar event ID override
   # Adjust confidence threshold if appropriate
   ```

4. **duration_consistency failure:**
   ```bash
   # Check if duration in manifest matches transcript length
   # Adjust duration_minutes in manifest.json
   # Account for breaks, late starts, early ends
   ```

**Quality Gate Bypass (Use with caution):**
```bash
# Override specific checks
python3 Skills/meeting-ingestion/scripts/quality_gate.py /path/to/manifest.json --override transcript_length

# Force pass (emergency only)
python3 Scripts/meeting-ingestion/scripts/meeting_cli.py gate /path/to/meeting --force-pass
```

### Stage 4: Block Processing Issues

#### Problem: LLM block selection fails

**Symptoms:**
```
Error: Block selection API call failed
Error: Invalid block configuration returned
```

**Diagnosis:**
```bash
# Test block selector directly
python3 Skills/meeting-ingestion/scripts/block_selector.py /path/to/meeting --verbose

# Check ZO_CLIENT_IDENTITY_TOKEN
echo $ZO_CLIENT_IDENTITY_TOKEN | cut -c1-20  # Should show token prefix
```

**Solutions:**

1. **API authentication issues:**
   ```bash
   # Check token validity
   # Re-authenticate if needed
   # Use manual block selection as fallback
   ```

2. **Invalid transcript analysis:**
   ```bash
   # Use manual block selection
   python3 Skills/meeting-ingestion/scripts/meeting_cli.py process /path/to/meeting --blocks B01,B08,B21,B26
   
   # Or use recipe-based selection
   python3 Skills/meeting-ingestion/scripts/block_selector.py /path/to/meeting --recipe external_standard
   ```

#### Problem: Block generation fails

**Symptoms:**
```
Error generating block B01: API timeout
Block B08 failed: Invalid response format
```

**Diagnosis:**
```bash
# Check individual block generation
python3 Skills/meeting-ingestion/scripts/process.py /path/to/meeting --blocks B01 --verbose

# Check logs for specific errors
grep -A 10 -B 5 "Block generation error" /dev/shm/meeting-*.log
```

**Solutions:**

1. **API timeouts:**
   ```bash
   # Retry with smaller batch
   # Process blocks individually
   # Check API status/quotas
   ```

2. **Invalid response format:**
   ```bash
   # Check prompt integrity
   # Regenerate specific failed blocks
   # Manual block creation if needed
   ```

### Stage 5: Archive Issues

#### Problem: Archive conflicts

**Symptoms:**
```
Error: Target week folder collision
Error: Cannot move to Week-of-2026-02-09 - folder exists
```

**Solutions:**
```bash
# Check collision details
ls -la "Personal/Meetings/Week-of-2026-02-09/"

# Resolve naming conflicts
python3 Skills/meeting-ingestion/scripts/archive.py --resolve-conflicts

# Manual archive with suffix
python3 Scripts/meeting-ingestion/scripts/archive.py --suffix "-v2"
```

## HITL Queue Management

### Understanding HITL Escalations

**Priority Levels:**
- **P0 (Immediate):** System failures, corruption, critical data issues
- **P1 (Standard):** Quality failures, missing data, low confidence
- **P2 (Batch):** Minor issues, borderline cases

### Processing HITL Items

#### P0 - Critical Issues

**Example P0 escalation:**
```json
{"meeting_id": "2026-02-09_Corrupt-Encoding", "priority": "P0", "reason": "transcript_encoding", "error": "Invalid UTF-8 sequences", "escalated_at": "2026-02-09T10:30:00Z"}
```

**Resolution Process:**
1. **Immediate diagnosis:**
   ```bash
   # Check file encoding
   file /path/to/meeting/transcript.md
   hexdump -C /path/to/meeting/transcript.md | head -10
   ```

2. **Fix encoding:**
   ```bash
   # Convert encoding
   iconv -f ISO-8859-1 -t UTF-8 transcript.md > transcript_fixed.md
   mv transcript_fixed.md transcript.md
   ```

3. **Resolve HITL item:**
   ```bash
   python3 Skills/meeting-ingestion/scripts/hitl_manager.py resolve "2026-02-09_Corrupt-Encoding" --reason "Fixed UTF-8 encoding"
   ```

#### P1 - Standard Issues

**Example P1 escalation:**
```json
{"meeting_id": "2026-02-09_Low-Confidence", "priority": "P1", "reason": "participant_confidence_low", "confidence": 0.45, "escalated_at": "2026-02-09T10:30:00Z"}
```

**Resolution Process:**
1. **Review participant data:**
   ```bash
   python3 Skills/meeting-ingestion/scripts/crm_enricher.py /path/to/meeting --verbose
   ```

2. **Manual participant correction:**
   ```json
   // Edit manifest.json
   {
     "participants": {
       "identified": [
         {"name": "John Doe", "role": "external", "email": "john@company.com"},
         {"name": "V", "role": "host", "email": "attawar.v@gmail.com"}
       ],
       "confidence": 0.85  // Increase after manual verification
     }
   }
   ```

3. **Resolve and continue pipeline:**
   ```bash
   python3 Skills/meeting-ingestion/scripts/hitl_manager.py resolve "2026-02-09_Low-Confidence" --reason "Manual participant verification"
   python3 Skills/meeting-ingestion/scripts/meeting_cli.py tick
   ```

## Scheduled Agent Issues

### Agent Not Running

**Diagnosis:**
```bash
# Check agent status
python3 N5/scripts/list_agents.py | grep -i "meeting"

# Check agent logs
tail -f /dev/shm/agent-*.log | grep "Meeting Orchestrator"
```

**Solutions:**
```bash
# Re-enable agent
python3 N5/scripts/edit_agent.py <agent_id> --active true

# Check agent schedule
# Verify no conflicting agents
# Check for system resource issues
```

### Agent Execution Errors

**Common Issues:**

1. **Permission errors:**
   ```bash
   # Check file permissions
   ls -la Skills/meeting-ingestion/scripts/meeting_cli.py
   chmod +x Skills/meeting-ingestion/scripts/meeting_cli.py
   ```

2. **Environment issues:**
   ```bash
   # Check environment variables in agent context
   # Verify path configurations
   # Test script execution manually
   ```

3. **Resource exhaustion:**
   ```bash
   # Check disk space
   df -h /home/workspace
   
   # Check memory usage
   free -h
   
   # Clean up old logs if needed
   ```

## Emergency Procedures

### Complete Pipeline Reset

**When to use:** System completely broken, multiple failures

**Procedure:**
```bash
# 1. Stop all scheduled agents
python3 N5/scripts/edit_agent.py <meeting_agent_id> --active false

# 2. Backup current state
cp -r "Personal/Meetings/Inbox" "Personal/Meetings/Inbox.backup.$(date +%Y%m%d)"

# 3. Clean HITL queue
cp N5/review/meetings/hitl-queue.jsonl N5/review/meetings/hitl-queue.jsonl.backup
echo > N5/review/meetings/hitl-queue.jsonl

# 4. Reset problematic meetings to earlier stage
# Edit manifest.json status fields manually

# 5. Re-enable agent
python3 N5/scripts/edit_agent.py <meeting_agent_id> --active true

# 6. Monitor recovery
tail -f /dev/shm/meeting-orchestrator.log
```

### Data Recovery

**Corrupted manifest.json:**
```bash
# Restore from git if available
git checkout HEAD -- "Personal/Meetings/Inbox/Meeting-Name/manifest.json"

# Or regenerate from transcript
python3 Skills/meeting-ingestion/scripts/ingest.py /path/to/transcript.md --regenerate-manifest
```

**Lost blocks:**
```bash
# Check git history
git log --oneline -- "Personal/Meetings/*/B*.md"

# Regenerate from manifest
python3 Skills/meeting-ingestion/scripts/process.py /path/to/meeting --regenerate
```

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Queue depths:** Should not grow unbounded
2. **HITL escalation rate:** <10% normal, >20% problematic
3. **Pipeline throughput:** Should process daily volume
4. **Error rates:** Quality gate failures, API errors
5. **Agent execution success:** Daily runs should complete

### Setting up Monitoring

```bash
# Daily health check script
python3 Skills/meeting-ingestion/scripts/health_check.py --email-report

# Add to crontab for daily monitoring
# 0 7 * * * cd /home/workspace && python3 Skills/meeting-ingestion/scripts/health_check.py --email-report
```

### Alert Thresholds

- **P0 HITL items:** Immediate SMS
- **Queue depth >10:** Daily email alert  
- **Agent failures >2 consecutive:** SMS alert
- **Quality gate failure rate >30%:** Investigation needed

---

*This runbook should be updated as new failure modes are discovered and resolved.*