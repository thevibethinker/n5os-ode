---
created: 2025-12-11
last_edited: 2025-12-11
version: 1
---
# Semantic Cleanup Workflow - Build Plan

## Objective

Leverage the new `text-embedding-3-large` semantic index to identify:
1. **Duplicate/near-duplicate content** across the workspace
2. **Stale/obsolete documentation** superseded by newer versions
3. **Consolidation opportunities** (scattered content that should be merged)
4. **Orphaned files** (docs that nothing references or uses)

## Phase 1: Duplicate Detection

### Approach
- For each indexed resource, find top-5 semantically similar documents
- Filter to similarity > 0.85 (high overlap threshold)
- Cluster into duplicate groups
- Rank by file modification date to identify "canonical" version

### Output
```
DUPLICATE_CLUSTERS.md
├── Cluster 1: "Meeting Orchestrator Documentation"
│   ├── N5/docs/meeting_orchestrator.md (2025-11-15) ← CANONICAL
│   ├── N5/docs/MEETING_ORCHESTRATOR_README.md (2025-10-28) ← STALE
│   └── Documents/System/orchestrator-complete-summary.md (2025-10-09) ← ARCHIVE
...
```

### Script: `n5_duplicate_detector.py`
```python
# Pseudocode
for resource in all_resources:
    similar = client.search(resource.content, limit=5, min_similarity=0.85)
    if len(similar) > 1:
        cluster = create_cluster(resource, similar)
        rank_by_date(cluster)
        mark_canonical(cluster[0])  # newest
        mark_stale(cluster[1:])
```

## Phase 2: Staleness Detection

### Approach
- Compare documents with similar titles/paths but different dates
- Identify docs referencing deprecated patterns (old system names, removed features)
- Flag docs not modified in 60+ days that have newer related content

### Staleness Signals
| Signal | Weight | Example |
|--------|--------|---------|
| Newer doc with same topic | High | v2 exists, v1 is stale |
| References removed system | High | Mentions "mode system" (deprecated) |
| No modifications 60+ days | Medium | Last edit Oct 2025 |
| Low semantic uniqueness | Medium | Everything it says exists elsewhere |

### Output
```
STALE_DOCS_REPORT.md
├── High Confidence (safe to archive)
│   └── 23 files
├── Medium Confidence (review recommended)  
│   └── 47 files
└── Low Confidence (keep but flag)
    └── 12 files
```

## Phase 3: Consolidation Recommendations

### Approach
- Find documents that are semantically related but fragmented
- Identify "topic clusters" that should be single documents
- Generate merge recommendations

### Example Output
```
CONSOLIDATION_OPPORTUNITIES.md

## Topic: "CRM System"
Currently spread across 6 files:
- N5/docs/crm_interface_guide.md (800 words)
- N5/prefs/communication/crm_protocols.md (400 words)  
- Documents/CRM_Consolidation_Final.md (1200 words)
- ...

Recommendation: Merge into single N5/docs/crm_system_guide.md
Estimated reduction: 6 files → 1 file
```

## Phase 4: Cleanup Execution

### Safety Protocol
1. **Dry-run first** - Generate report only, no file changes
2. **V reviews report** - Approve/reject recommendations
3. **Staged execution** - Move to Archive/, don't delete
4. **Rollback capability** - Keep manifest of all changes

### Archive Structure
```
Documents/Archive/semantic-cleanup-2025-12-11/
├── MANIFEST.json  # What was moved and why
├── duplicates/    # Duplicate files (non-canonical)
├── stale/         # Outdated docs
└── consolidated/  # Files merged into others
```

## Implementation Timeline

| Phase | Script | Est. Time | Dependency |
|-------|--------|-----------|------------|
| 1. Duplicate Detection | `n5_duplicate_detector.py` | 2 hours | Index complete |
| 2. Staleness Analysis | `n5_staleness_analyzer.py` | 1 hour | Phase 1 |
| 3. Consolidation | `n5_consolidation_planner.py` | 1 hour | Phase 2 |
| 4. Report Generation | `n5_cleanup_report.py` | 30 min | Phase 3 |
| 5. V Review | Manual | Variable | Phase 4 |
| 6. Execution | `n5_cleanup_executor.py` | 30 min | V approval |

## Success Metrics

- **File reduction**: Target 15-25% fewer redundant files
- **Search quality**: Queries return more precise results (less noise)
- **Maintenance burden**: Fewer places to update when things change

## Next Steps

1. ✅ Complete semantic index (in progress - ~23 min remaining)
2. Build Phase 1 script (`n5_duplicate_detector.py`)
3. Run duplicate detection, generate initial report
4. Review with V, refine thresholds
5. Proceed through phases

## Notes

- Meeting blocks (B*.md) should be excluded from duplicate detection (they're intentionally similar across meetings)
- Lists/*.jsonl are structured data, handle separately
- Prompts/ are intentionally standalone, don't consolidate

