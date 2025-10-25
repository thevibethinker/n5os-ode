# Principle 24: Information Flow Design

**Category**: Design  
**Priority**: Critical  
**Related**: P2 (SSOT), ZD2 (Flow vs. Pools)

---

## Statement

Design systems for information flow, not information storage. Every category of information must have defined entry points, transformation stages, and exit paths. Information that pools beyond expected residence times is a system failure.

---

## Rationale

From Zero-Doc Principle 2: Information is like water—it either flows to where it creates value, or pools where it rots.

**Pools are graveyards**:
- "Read Later" lists that never get read
- "Inbox Zero" archives that never get retrieved
- Perfectly organized folders that become digital landfills
- Comprehensive databases where information goes to die

The problem isn't the tool—it's that we optimize for *storage* when we should optimize for *flow*.

---

## Core Concepts

### Flow Stages

Every information type should have explicit stages:

```
Entry → Transformation → Destination → Archive/Delete
```

**Example: Article**
```
Save URL → Auto-summarize → Review → Knowledge (valuable) OR Delete (not)
Max time: instant → 24hr → 7days → permanent/gone
```

### Pool Detection

Information pooling beyond expected time = system failure:

| Stage | Expected Max Time | Pool Threshold |
|-------|-------------------|----------------|
| Intake | 24 hours | >2 days |
| Processing | 7 days | >14 days |
| Review queue | 7 days | >30 days |

**Trigger**: Automated alerts when thresholds crossed.

### Exit Paths

Every flow needs explicit exits:
- **Promote**: Move to permanent storage (Knowledge/)
- **Action**: Convert to task (Lists/)
- **Archive**: Move to long-term storage (rarely accessed)
- **Delete**: Remove entirely

**Anti-pattern**: Flows with only entry and no exit = guaranteed pool.

---

## Implementation Patterns

### Pattern 1: Flow Mapping

Before implementing any workflow, map the complete flow:

```markdown
## Article Ingestion Flow

**Entry**: User saves URL → Records/Intake/web/
**Stage 1 (Assess)**: AI summarizes, categorizes, extracts key points
**Stage 2 (Intervene)**: Move to Processing/ + flag for review if confidence <80%
**Stage 3 (Review)**: User sees summary weekly, decides Keep/Archive/Delete
**Exit**:
  - Keep → Knowledge/articles/[category].md
  - Archive → Archive/[year]/articles/
  - Delete → removed entirely

**Max residence**:
  - Intake: 24hr (auto-processes at night)
  - Processing: 7 days (weekly review)
  - Total: 8 days entry → exit
```

### Pattern 2: Residence Time Tracking

```python
import time
from pathlib import Path
from datetime import datetime, timedelta

def check_pools(directory, max_age_days=7):
    """Detect items pooling beyond expected time."""
    now = datetime.now()
    pools = []
    
    for file in Path(directory).rglob("*"):
        if file.is_file():
            age = now - datetime.fromtimestamp(file.stat().st_mtime)
            if age > timedelta(days=max_age_days):
                pools.append({
                    "file": str(file),
                    "age_days": age.days,
                    "warning": age.days > max_age_days * 2
                })
    
    return pools

# Run nightly
pools = check_pools("Records/Processing/", max_age_days=7)
if pools:
    log_warning(f"Pool detected: {len(pools)} items > 7 days old")
    notify_user(pools)
```

### Pattern 3: Flow Audit

Regular audits to identify new pools forming:

```bash
#!/bin/bash
# flow_audit.sh - Run monthly

echo "=== N5 Flow Audit ==="
echo

echo "1. Intake → Processing flow"
echo "   Items in Intake > 48hr:"
find Records/Intake -type f -mtime +2 -ls | wc -l

echo
echo "2. Processing → Output flow"  
echo "   Items in Processing > 14 days:"
find Records/Processing -type f -mtime +14 -ls | wc -l

echo
echo "3. Knowledge growth"
echo "   Items added this month:"
find Knowledge -type f -mtime -30 -ls | wc -l

echo
echo "4. Archive vs Delete ratio"
echo "   Archived: $(find Archive -type f -mtime -30 | wc -l)"
echo "   (Deleted items not tracked)"
```

---

## Key Insights

1. **Flow is Purpose**: The path information takes reveals its purpose. If you can't define the flow, you don't understand the information's role.

2. **Residence Time = Design Constraint**: How long information sits in each stage isn't just a metric—it's a design decision. Define it explicitly.

3. **Pools Happen at Transitions**: Information pools where flow stalls. Usually at decision points ("What do I do with this?"). Automate or streamline transitions.

4. **Exit is as Important as Entry**: We obsess over capture. But information must *leave* the system (to Knowledge, to Action, to Delete) or it pools.

---

## Flow Patterns by Information Type

### Meeting Notes
```
Entry: Auto-transcribe voice recording → Records/Intake/
Transform: Extract action items + key decisions → Records/Processing/Company/
Exit: 
  - Actions → Lists/
  - Decisions → Knowledge/meetings/[project].md
  - Full transcript → Archive/meetings/[date].md
Max time: 24hr → 7days → permanent
```

### Ideas (Voice Notes)
```
Entry: Voice capture → Records/Intake/voice/
Transform: Transcribe + categorize → Records/Processing/Personal/
Exit:
  - Valuable insight → Knowledge/insights/
  - Actionable → Lists/
  - Fleeting thought → Delete
Max time: 24hr → 7days → permanent/deleted
```

### Email/Messages
```
Entry: Forward to system → Records/Intake/email/
Transform: Parse + extract tasks/info → Records/Processing/
Exit:
  - Tasks → Lists/
  - Reference info → Knowledge/people/[person].md
  - Thread archived → Archive/communications/
Max time: 12hr → 3days → permanent
```

---

## Anti-Patterns

❌ **Indefinite storage**: Folders with no max residence time → guaranteed pools  
❌ **No exit paths**: Only entry + storage, no promote/archive/delete → accumulation  
❌ **Manual flow only**: Requiring human intervention for every transition → bottleneck  
❌ **Stage proliferation**: Too many stages → complexity → stalls  
❌ **Generic "Archive"**: Archive without criteria → becomes new pool

---

## Testing Flow Design

### Test 1: Trace One Item
Pick one item, track it through entire flow manually:
- How long at each stage?
- What triggered each transition?
- Were transitions automatic or manual?
- Did it reach appropriate exit?

### Test 2: Monitor Pool Formation
After 30 days:
- Check each Processing/ directory for items >14 days
- Identify which flow is stalling
- Diagnose: Missing automation? Unclear exit criteria? Too complex?

### Test 3: Volume Stress
Simulate 10x normal volume:
- Do flows still process in expected time?
- Do any stages become bottlenecks?
- Do manual review queues become overwhelming?

---

## Success Criteria

Flow design is working when:
- [ ] Every information type has documented flow with max residence times
- [ ] Pool warnings trigger <5% of the time (most items flow smoothly)
- [ ] Items reach appropriate exits (not just stalling in final stage)
- [ ] New information types can be added by defining flow, not creating storage
- [ ] Review queues are manageable (<50 items weekly)
- [ ] System can explain where any item currently is and next expected transition

---

## Migration Path: Storage → Flow

If you have existing "storage-oriented" structure:

1. **Audit current pools**: Find directories where information accumulates
2. **Map desired flows**: For each pool, define: Entry → Transform → Exit
3. **Set residence limits**: How long should items sit in each stage?
4. **Add exit paths**: Promote to Knowledge, convert to Action, or Delete
5. **Automate transitions**: Reduce manual routing decisions
6. **Monitor**: Track whether pools are draining or refilling

---

## Related Principles

- **P2 (SSOT)**: Flow requires knowing canonical destination for each info type
- **P7 (Idempotence)**: Flows should be rerunnable without creating duplicates
- **P11 (Failure Modes)**: Flows stall → needs recovery path
- **P24 (AIR Pattern)**: Assess-Intervene-Review is the implementation of flow stages
- **ZD2 (Flow vs. Pools)**: Philosophical foundation for this principle

---

*Added: 2025-10-24*  
*Source: Zero-Doc integration (ZD2)*