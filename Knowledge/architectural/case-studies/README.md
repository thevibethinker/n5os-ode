# Case Studies

Real-world architectural decisions and their outcomes.

## System Migrations

### [N5 Realignment 2025-10-28](n5-realignment-2025-10-28.md)
Full system restructuring from 42→20 directories using build orchestrator pattern with parallel workers.

**Key Outcomes:**
- 52% reduction in N5 subdirectories
- 63% backup space savings
- Zero breaking changes (symlink compatibility)
- Reusable orchestration pattern

**Reusable Artifacts:**
- Build orchestrator pattern: file 'N5/scripts/build/orchestrator_pattern.py'
- Migration templates: file 'N5/scripts/build/'

**Principles Applied:** P5, P7, P11, P15, P19, P23, P28

---

*Index created: 2025-10-28*
