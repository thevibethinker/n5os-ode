# Build Scripts

Reusable patterns for system builds and migrations.

## Orchestration

### orchestrator_pattern.py
Parallel worker pattern for complex builds. Demonstrates:
- Control plane coordination
- Parallel phase execution
- Real-time monitoring
- State management
- Error handling

**Source:** N5 Platonic Realignment (2025-10-28)  
**Pattern:** Orchestrator spawns workers, monitors progress, aggregates results

### migration_survey_template.py
Pre-migration safety checks. Always run before destructive operations:
- Check protected paths
- Verify service dependencies
- Scan scheduled tasks
- Create pre-migration backup
- Validate essential directories

**Usage:** Adapt checklist to your specific migration

### backup_consolidation_template.py
Consolidate scattered backups with compression. Features:
- Find and compress backup directories
- Calculate compression ratios
- Clean old backup files (>30 days)
- Hidden dot-prefix archives
- Detailed logging

**Usage:** Update BACKUP_SOURCES list for your environment

---

## Usage

These are **templates**, not production scripts. Copy and adapt:

```bash
# Example: Create new migration
cp migration_survey_template.py my_migration_survey.py
# Edit checklist, paths, validation rules
# Test with --dry-run
python3 my_migration_survey.py --dry-run
```

---

## Principles

All build scripts follow:
- **P5:** Anti-Overwrite (backups before destruction)
- **P7:** Dry-Run by Default
- **P11:** Failure Modes & Recovery
- **P15:** Complete Before Claiming
- **P19:** Error Handling (try/except with context)

---

## Reference

Full case study: file 'Knowledge/architectural/case-studies/n5-realignment-2025-10-28.md'

---

*Created: 2025-10-28*
