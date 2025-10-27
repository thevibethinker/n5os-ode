# Distributed Build System

**Version:** 1.0  
**Purpose:** Multi-conversation orchestration for major Zo system upgrades

---

## Quick Start

1. **Decide:** Is this a distributed build? → `file 'decision-tree.md'`
2. **Learn:** First time? → `file 'protocol.md'` (read full workflow)
3. **Execute:** Ready to build? → Follow `file 'protocol.md'` step-by-step
4. **Stuck?** → `file 'troubleshooting.md'`
5. **Error?** → `file 'error-tracking-guide.md'`

---

## Documentation

### Core Workflow
- **`protocol.md`** - High-level workflow, roles, stages
- **`decision-tree.md`** - When to use distributed vs. sequential builds

### Operational Guides
- **`error-tracking-guide.md`** - Error codes, logging, recovery
- **`troubleshooting.md`** - Common issues and solutions

### Templates
- **`templates/WORKER_ASSIGNMENT.md`** - Standard worker assignment format
- **`templates/BUILD_STATE_SESSION.md`** - Build state tracking
- **`templates/INTEGRATION_CHECKLIST.md`** - Step-by-step integration
- **`templates/WORKER_ERROR_REPORT.md`** - Error documentation format

---

## Directory Structure

### Active Builds
```
/home/workspace/N5/logs/builds/[build-name]/
├── BUILD_STATE_SESSION.md
├── assignments/
│   └── WORKER_N_ASSIGNMENT.md
├── workers/
│   ├── WN_SUMMARY.md
│   └── WN_ERROR_LOG.md
└── integration/
    └── INTEGRATION_LOG.md
```

### Completed Builds (moved here after completion)
```
/home/workspace/N5/logs/threads/[date]_[build-name]_[id]/
```

---

## Philosophy

**Why distributed builds?**
- **Context isolation** = higher quality per module
- **Cognitive multiplication** = 4 workers = 4× focused attention
- **Failure isolation** = one worker fail ≠ entire build fail
- **Incremental integration** = test early, test often

**Core principle:**  
Trade orchestrator time (coordination) for implementation quality (fewer bugs, better architecture).

---

## Success Metrics

Track these over time to improve the system:

| Metric | Target |
|--------|--------|
| Rework cycles per worker | < 1 |
| Integration time per worker | < 30 min |
| Principle violations | 0 |
| Build completion rate | 100% |

---

## Contributing

After each distributed build:
1. Generate after-action report
2. Document lessons learned
3. Refine templates if needed
4. Update this documentation
5. Version bump in protocol.md

---

**Ready?** Start with `file 'decision-tree.md'` to determine if this is the right approach.
