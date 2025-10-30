# Export Spec 002: Timeline System

**System:** Development Timeline & Historical Audit Trail  
**Version:** 2.0 (Production)  
**Maturity:** Battle-tested, 10+ months active use  
**Last Updated:** 2025-10-28

---

## 1. System Overview

### Purpose
Record system evolution as a queryable timeline. Answers: "When did we add X?", "What changed in October?", "Show me all infrastructure upgrades."

### Core Concept
**Timeline as audit trail.** Each entry captures a development event with category, impact, status, and links to artifacts. Think: git log meets changelog meets project journal.

### Key Capabilities
- Add timestamped entries (manual or automated)
- Query by date range, category, impact level, status
- Link to conversation threads, artifacts, documentation
- Multiple timeline types (system, project-specific)
- Export to various formats (table, JSON, markdown)

---

## 2. Architecture

### File Structure
```
N5/config/
└── system-timeline.jsonl     # Main system timeline

N5/scripts/
├── n5_system_timeline.py     # View/query timeline
├── n5_system_timeline_add.py # Add new entries
└── timeline_automation_module.py  # Auto-capture from conversations
```

### Data Model

**Timeline Entry:**
```json
{
  "date": "2025-10-14",
  "title": "Feature Launch: Command Authoring",
  "category": "feature",
  "impact": "high",
  "status": "completed",
  "description": "Launched comprehensive command authoring pipeline with 6-stage validation.",
  "components": [
    "N5/scripts/author_command/",
    "N5/schemas/commands.schema.json"
  ],
  "thread_id": "con_abc123xyz",
  "artifacts": [
    "Documents/System/command-authoring-design.md",
    "N5/logs/threads/2025-10-14-command-authoring/"
  ],
  "tags": ["automation", "core-infrastructure"],
  "related_to": ["EXPORT_001_LIST_SYSTEM"]
}
```

### Schema Fields

**Required:**
- `date`: ISO date (YYYY-MM-DD)
- `title`: Short description (max 100 chars)
- `category`: Enum value (see below)
- `status`: Enum value (see below)

**Optional but Recommended:**
- `impact`: low|medium|high|critical
- `description`: Detailed explanation
- `components`: Array of affected files/directories
- `thread_id`: Conversation where work happened
- `artifacts`: Links to docs, logs, outputs
- `tags`: Searchable keywords
- `related_to`: Cross-references to other entries

### Categories

```
infrastructure  - Core system changes
feature         - New capabilities
command         - Command additions/updates
workflow        - Process improvements
ui              - Interface changes
integration     - External service connections
fix             - Bug fixes
refactor        - Code improvements (no behavior change)
docs            - Documentation updates
data            - Schema or data migrations
```

### Status Values

```
proposed     - Planned but not started
in-progress  - Currently working on
completed    - Done and deployed
blocked      - Waiting on external dependency
deferred     - Postponed to later
abandoned    - Decided not to do
```

---

## 3. Core Operations

### View Timeline
```bash
# Show recent entries (default: 20)
python3 n5_system_timeline.py

# Filter by category
python3 n5_system_timeline.py --category feature

# Date range
python3 n5_system_timeline.py --from 2025-10-01 --to 2025-10-31

# Multiple filters
python3 n5_system_timeline.py \
  --category feature,infrastructure \
  --impact high \
  --status completed \
  --limit 50

# Output formats
python3 n5_system_timeline.py --format json > export.json
python3 n5_system_timeline.py --format markdown > changelog.md
```

### Add Entry
```bash
# Manual entry
python3 n5_system_timeline_add.py \
  --title "Launched List System" \
  --category feature \
  --impact high \
  --status completed \
  --description "JSONL-backed action tracking with auto-generated views" \
  --components "N5/lists/,N5/scripts/n5_lists_*.py" \
  --thread-id con_xyz789

# Interactive mode
python3 n5_system_timeline_add.py --interactive

# From automation (captures current conversation context)
python3 timeline_automation_module.py capture \
  --title "Performance optimization" \
  --category refactor
```

### Query Examples
```python
# In Python scripts
from n5_system_timeline import TimelineQuery

tq = TimelineQuery('/home/workspace/N5/config/system-timeline.jsonl')

# Recent features
features = tq.filter(category='feature', limit=10)

# High-impact items this quarter
q4 = tq.filter(
    from_date='2025-10-01',
    to_date='2025-12-31',
    impact='high'
)

# All infrastructure work
infra = tq.filter(category='infrastructure', status='completed')
```

---

## 4. Design Decisions & Rationale

### Why JSONL Over Database?
- **Simple**: No database setup, migrations, or admin
- **Portable**: Plain text, version control friendly
- **Grepable**: Standard text tools work
- **Append-friendly**: Safe concurrent writes
- **Backup-friendly**: Part of regular file backups

### Why Manual + Automated Capture?
- **Manual**: High-signal, intentional milestones
- **Automated**: Capture context automatically from conversations
- **Both**: Manual for planning, automated for "what actually happened"

### Date Granularity: Why Days Not Hours?
- **Simpler**: No timezone complexity
- **Clearer**: Focus on "what happened when", not exact timestamps
- **Practical**: Most development events map to day-level granularity
- **Exception**: Use `created_at` with full timestamp if needed

### Impact Levels
- **Critical**: System-breaking or user-blocking issues
- **High**: Major features, architectural changes
- **Medium**: Incremental improvements, minor features
- **Low**: Docs, small fixes, cleanup

---

## 5. Integration Points

### With Conversation System
Timeline automation can detect significant work in conversations and propose timeline entries. Looks for keywords: "implemented", "launched", "completed", "fixed".

### With Commands
Timeline operations themselves can be registered as commands: `N5: add to system timeline "Shipped feature X"`

### With Documentation
`docgen --timeline` generates human-readable changelog from timeline entries. Grouped by month and category.

### With Lists
Timeline entries can reference list items being promoted or completed.

---

## 6. Testing Strategy

### Validation Tests
- Date format validation (ISO 8601)
- Category/status enum validation
- Required fields present
- Component paths exist (optional check)

### Query Tests
- Date range filtering
- Category filtering
- Combined filters (AND logic)
- Limit/offset pagination
- Format outputs (JSON, table, markdown)

### Example Test Cases
```python
def test_add_entry():
    entry = {
        "date": "2025-10-28",
        "title": "Test Entry",
        "category": "feature",
        "status": "completed"
    }
    timeline.add(entry)
    assert timeline.find_by_title("Test Entry") is not None

def test_date_range_filter():
    results = timeline.filter(
        from_date="2025-10-01",
        to_date="2025-10-31"
    )
    assert all("2025-10" in r['date'] for r in results)
```

---

## 7. Operational Considerations

### Performance
- **Read**: O(n) scan (fast for <10k entries)
- **Filter**: O(n) with early termination
- **Add**: O(1) append

### Scaling
- Works well up to ~5k entries
- Beyond 10k: consider SQLite or index file
- Current size: ~100 entries after 10 months

### Backup
- JSONL in git repository
- Auto-backup before bulk operations
- Manual snapshots before major cleanups

### Error Handling
- Invalid date → Skip entry, log warning
- Missing category → Default to "infrastructure"
- Malformed JSON → Skip line, continue processing

---

## 8. Migration Guide

### Minimal Implementation (30 minutes)
```python
import json
from pathlib import Path
from datetime import datetime

class SimpleTimeline:
    def __init__(self, path):
        self.path = Path(path)
        
    def add(self, title, category, status, **kwargs):
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "title": title,
            "category": category,
            "status": status,
            **kwargs
        }
        with self.path.open('a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def filter(self, **criteria):
        entries = []
        with self.path.open('r') as f:
            for line in f:
                entry = json.loads(line.strip())
                if all(entry.get(k) == v for k, v in criteria.items()):
                    entries.append(entry)
        return entries
```

### Full Implementation (2-4 hours)
1. Add schema validation
2. Implement all filter options (date range, multi-category, impact)
3. Add output formatters (table, JSON, markdown)
4. Build interactive add command
5. Create automation module for conversation capture

---

## 9. Use Cases

### Development Team Retrospectives
"Show me all features we shipped in Q3"
```bash
python3 n5_system_timeline.py \
  --from 2025-07-01 --to 2025-09-30 \
  --category feature --status completed
```

### Debugging "When Did This Change?"
"When did we refactor the list system?"
```bash
python3 n5_system_timeline.py \
  --category refactor \
  --search "list"
```

### Changelog Generation
"Generate changelog for last release"
```bash
python3 n5_system_timeline.py \
  --from 2025-10-01 --to 2025-10-28 \
  --format markdown > CHANGELOG.md
```

### Impact Assessment
"What critical/high impact work is in progress?"
```bash
python3 n5_system_timeline.py \
  --impact high,critical \
  --status in-progress
```

---

## 10. Known Issues & Gotchas

### Issue: No Built-in Search
**Current:** Must grep JSONL or use --search flag (basic string match)  
**Future:** Consider full-text search index

### Issue: No Editing
**Current:** Must manually edit JSONL file  
**Rationale:** Timeline is audit trail, shouldn't be edited  
**Workaround:** Add correcting entry with note about error

### Issue: No Links Validation
**Current:** Component paths and artifact links not validated  
**Workaround:** Run periodic link checker script

---

## 11. Success Metrics

**System is working well when:**
- New features auto-captured 80%+ of the time
- Team references timeline weekly for context
- Changelog generation is automated
- No manual "when did we..." questions

**Current Stats:**
- 100+ entries over 10 months
- Avg 10 entries/month
- Categories: 40% feature, 30% infrastructure, 20% fix, 10% other
- 85% of entries have thread_id links

---

## 12. Extensions & Variations

### Project-Specific Timelines
Create separate timeline files for different projects:
```
N5/config/
├── system-timeline.jsonl
├── careerspan-timeline.jsonl
└── client-project-timeline.jsonl
```

### Timeline Dashboard
Build web UI that visualizes timeline entries as interactive chart. Group by category, filter by date, click through to artifacts.

### Automated Capture
Hook into conversation close event to prompt: "Add this conversation to timeline?" with auto-filled title and thread_id.

---

## Philosophy Notes

Timeline embodies **"Maintenance Over Organization"** - it's designed for long-term use, not just initial setup. The JSONL format ensures it survives system migrations.

It's **"Flow Over Pools"** - entries flow chronologically, never reorganized or bucketed (except by query filters).

---

**Implementation Checklist:**
- [ ] Create timeline.jsonl file
- [ ] Implement add operation
- [ ] Implement filter/query operation
- [ ] Add date range filtering
- [ ] Add category filtering
- [ ] Build output formatters (table, JSON, markdown)
- [ ] Create interactive add command
- [ ] Add schema validation
- [ ] Write tests for core operations
- [ ] Document custom categories (if any)

---

*Export specification format v1.0*
