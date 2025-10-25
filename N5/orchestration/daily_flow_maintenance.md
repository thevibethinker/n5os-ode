# Daily Flow Maintenance Orchestration

**Purpose**: Zero-Doc daily maintenance rhythm (replaces manual filing)

---

## Morning: Flow Assessment (5 min)

**Human**: Review digest email  
**System**: Generates overnight assessment

```bash
# System runs nightly (2 AM ET)
python3 /home/workspace/N5/scripts/file_flow_router.py --scan /home/workspace
python3 /home/workspace/N5/scripts/file_flow_router.py --digest > /tmp/daily_digest.md
# Email digest to V
```

**V reviews**:
- Files queued for review (low confidence)
- System's predictions + confidence scores
- Reply with corrections or "approve"

---

## Evening: Learning Update (automated)

**System**: Learns from V's corrections

```bash
# Runs nightly (11 PM ET)
python3 /home/workspace/N5/scripts/flow_learner.py --train
# Updates patterns and thresholds based on day's corrections
```

---

## Weekly: Flow Health Report (automated)

**System**: Generates health metrics

```bash
# Runs Sunday 9 AM ET
python3 /home/workspace/N5/scripts/flow_learner.py --report > /tmp/weekly_flow_report.md
# Email to V
```

**Metrics**:
- Accuracy by file type
- Confidence threshold adjustments
- Files processed (auto vs review)
- Learning progress (entity mappings, patterns)

**V reviews**:
- What's working / stuck?
- Which channels need attention?
- Any new flows needed?

---

## Zero-Doc Principles Applied

✓ **Organization Step Shouldn't Exist**: System files, V reviews  
✓ **AIR Pattern**: Assess (scan) → Intervene (route/queue) → Review (corrections)  
✓ **Self-Healing**: Learns from mistakes automatically  
✓ **Maintenance > Organization**: Review = training, not filing  
✓ **Minimal Touch**: V's 5 min/day trains system for hours of future work

---

## Scheduled Task Stubs (Phase 3)

**To be implemented**:

1. **Nightly Scan & Route** (2 AM ET)
   - Instruction: "Run file flow scanner on workspace root. Auto-route high-confidence files. Generate review digest for files needing assessment."
   - RRULE: `FREQ=DAILY;BYHOUR=2;BYMINUTE=0`

2. **Nightly Learning** (11 PM ET)
   - Instruction: "Train flow learner from today's corrections. Update patterns and confidence thresholds."
   - RRULE: `FREQ=DAILY;BYHOUR=23;BYMINUTE=0`

3. **Weekly Health Report** (Sunday 9 AM ET)
   - Instruction: "Generate weekly flow health report. Include accuracy metrics, threshold changes, and recommendations."
   - RRULE: `FREQ=WEEKLY;BYDAY=SU;BYHOUR=9;BYMINUTE=0`

---

**Version**: 1.0  
**Status**: Infrastructure complete, scheduled tasks ready to deploy  
**Updated**: 2025-10-24
