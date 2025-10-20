# CRM Hybrid System Design

**Purpose:** Fast indexing + network intelligence via SQLite, full details in markdown

## Use Cases (Priority Order)

1. **Fast Indexing:** Query DB to quickly find markdown files
   - "Find all FOUNDER contacts at Series A companies"
   - "Show me everyone I met in October"
   - "List high-priority uncontacted leads"

2. **Network Understanding:** Surface connections between stakeholders
   - "Who introduced me to X?"
   - "Show all connections at Company Y"
   - "Map investor network"

3. **Touchpoint Tracking:** Understand relationship history
   - "When did I last contact X?"
   - "Show all interactions with Company Y"
   - "List unsent follow-ups"

## Architecture

### Data Flow
```
Markdown File (Source of Truth)
    ↓
    ↓ [Dual Write]
    ↓
SQLite (Index + Relationships)
    ↓
    ↓ [Query Results]
    ↓
Point back to Markdown for full details
```

### Database Schema

**individuals** - Fast indexing to markdown
- Core identifiers: name, email, linkedin, company, title
- Categorization: category, tags, priority
- Temporal: last_contact_date, created_at, updated_at
- **KEY:** markdown_path (points to source of truth)

**interactions** - Touchpoint history
- Link to individual
- Type: meeting, email, call, event
- Date + context + meeting_path

**relationships** - Network connections
- Link person A ↔ person B
- Type: introduced_by, works_with, invested_in, colleagues
- Context + discovered_date

**organizations** - Lightweight company tracking
- Name, domain, industry, notes
- Links to individuals via junction table

**individual_organizations** - Employment history
- Current and past roles
- Start/end dates

## Implementation Phases

### Phase 1: Schema + One-Shot Migration
- Create/update schema
- Migrate 57 existing profiles
- Backfill interactions from stakeholder intelligence
- Extract organizations from profiles
- **Deliverable:** 57/57 profiles in DB, fully indexed

### Phase 2: Dual-Write Integration
- Update: meeting processing workflow
- Update: networking event processor
- Update: manual profile creation
- Add: Robust error handling (DB write fails → log + continue)
- **Deliverable:** All workflows write markdown + DB

### Phase 3: Query Commands
- crm-find: Fast search (name/company/tag/category)
- crm-connections: Show relationships for person
- crm-network: Network analysis
- crm-touchpoints: Interaction history
- **Deliverable:** Query interface ready

### Phase 4: Scheduled Validation (1PM Daily)
- Compare markdown ↔ DB
- Detect drift, repair automatically
- Report discrepancies
- Latch onto existing 1PM task slot
- **Deliverable:** Automated consistency check

## Error Handling Strategy

**Dual-Write Failure Modes:**
1. Markdown write succeeds, DB write fails → Log error, continue (markdown is truth)
2. DB write succeeds, markdown write fails → Rollback DB, raise error
3. Both fail → Raise error, no partial state

**Daily Sync Safety Net:**
- Catches missed DB writes
- Repairs drift
- Validates integrity

## Query Performance

**Expected queries:**
- Find by name: O(log n) with index on full_name
- Find by company: O(log n) with index on company
- Find by tag: O(n) - acceptable at <10k records
- Network traversal: O(connections) - typically small

**Optimization later:** Add indexes as needed based on actual query patterns

## Success Criteria

✅ Schema created with all 5 tables
✅ 57 profiles migrated to DB
✅ Interactions backfilled from existing intelligence
✅ Organizations extracted and linked
✅ Dual-write working in 3+ workflows
✅ 4+ query commands operational
✅ Daily sync scheduled at 1PM
✅ Error handling tested (dry-run + production)
✅ Documentation complete
✅ Zero data loss verified

## Rollback Plan

1. Database only - no markdown changes
2. Can delete crm.db and restart
3. Daily sync can rebuild from markdown
4. Backups in .migration_backups/

## Principles Applied

- P0: Rule-of-Two (loading only schema + 1 example profile at a time)
- P2: SSOT (markdown is source, DB is index)
- P5: Anti-Overwrite (backups before migration)
- P7: Dry-Run (test migration first)
- P15: Complete Before Claiming (verify all 57 migrated)
- P18: Verify State (check DB counts match files)
- P19: Error Handling (comprehensive try/except in dual-write)
