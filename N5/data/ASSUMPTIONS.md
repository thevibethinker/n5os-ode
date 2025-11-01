# Executables System - Assumptions & Limitations

**Version:** 1.0  
**Created:** 2025-11-01  
**System:** Modern Prompt System (executables.db)

## Design Assumptions

### 1. Single-User Environment
- **Assumption:** One user accessing database at a time
- **Rationale:** SQLite default (no connection pooling needed)
- **Impact:** Not safe for concurrent writes from multiple processes
- **Mitigation:** N5 is single-user system

### 2. File System Stability  
- **Assumption:** Prompt files in  don't move
- **Rationale:** Database stores absolute paths
- **Impact:** Moving files breaks references
- **Mitigation:** Use symlinks or update DB if files move

### 3. ID Immutability
- **Assumption:** Once registered, executable IDs never change
- **Rationale:** Incantum triggers reference IDs
- **Impact:** Renaming breaks natural language triggers
- **Mitigation:** Keep IDs stable, update triggers separately

### 4. Frontmatter Format
- **Assumption:** Prompts use YAML frontmatter (---\n...\n---)
- **Rationale:** Zo convention, migration source
- **Impact:** Non-standard format won't parse correctly
- **Mitigation:** Validate frontmatter during registration

### 5. Search Query Length
- **Assumption:** Search queries are reasonable length (<1000 chars)
- **Rationale:** FTS5 has internal limits
- **Impact:** Very long queries may fail
- **Mitigation:** Client-side validation recommended

## Known Limitations

### 1. No Dry-Run Support (Yet)
- **Status:** Planned but not implemented
- **Workaround:** Test in separate database or backup first
- **Priority:** Medium (P7 compliance)

### 2. No Automatic File Watching
- **Status:** Manual registration required
- **Impact:** New prompts must be explicitly registered
- **Workaround:** Run migration script periodically

### 3. Minimal Type Hints
- **Status:** Basic types only, no full coverage
- **Impact:** IDE autocomplete limited
- **Priority:** Low (works correctly, just less discoverable)

### 4. No Test Suite
- **Status:** Manual testing only
- **Impact:** Regressions possible during updates
- **Priority:** High (P33 violation)

### 5. Analytics Limited
- **Status:** Only tracks invocation count & timestamp
- **Missing:** Success/failure, duration, error types
- **Priority:** Low (sufficient for current needs)

## Migration Notes

### Backward Compatibility
- All 140 prompt IDs preserved from recipes.jsonl
- Incantum triggers work without modification
- Prompt files unchanged (database is additive)

### Backup Strategy
- Original: 
- Database:  (snapshot recommended)
- Script: 

## Future Enhancements

### Short Term
1. Add dry-run flag (P7)
2. Add basic test suite (P33)
3. Complete type hints (P33)
4. Document CLI fully

### Long Term
1. Register scripts automatically
2. Success/failure tracking
3. Duration metrics
4. File watcher integration
5. Web UI for analytics

## Questions & Clarifications Needed

1. **Script Registration:** Should existing N5/scripts/*.py be auto-registered?
2. **Analytics Depth:** Need success rates or just counts?
3. **Backward Compat Window:** Keep recipes.jsonl.backup forever or delete after N days?

---

**Contact:** Vibe Builder  
**Last Updated:** 2025-11-01 00:13 ET
