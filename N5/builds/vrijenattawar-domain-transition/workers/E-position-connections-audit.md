---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_nxvKhHpwzg225fn8
---

# Worker E: Position Connections Audit

**Project:** vrijenattawar-domain-transition
**Component:** Investigate why mind map nodes appear disconnected
**Dependencies:** None (analysis task)

---

## Objective

The mind map visualization shows 124 positions but they appear less interconnected than expected. Investigate:

1. **Data Analysis**: How many positions actually have connections defined?
2. **Connection Quality**: Are the connections in the `connections` JSON field valid (pointing to real position IDs)?
3. **Coverage Gap**: Which positions are "islands" with no connections?
4. **Recommendations**: Should we generate more connections? Are there obvious relationships not captured?

---

## Data Source

- Database: `/home/workspace/N5/data/positions.db`
- Schema has `connections` field (JSON array with target_id and relationship type)

---

## Tasks

1. Query the database to count positions with vs without connections
2. Parse connection JSON and validate target IDs exist
3. Identify orphan positions (no inbound or outbound connections)
4. Analyze by domain - are some domains more connected than others?
5. Generate report with findings and recommendations

---

## Deliverables

1. Analysis report at `N5/builds/vrijenattawar-domain-transition/reports/position-connections-audit.md`
2. Recommendations for improving graph connectivity
3. Optionally: SQL or script to generate missing connections based on semantic similarity

---

## Execution Notes

This is an **analysis worker** - no code changes to the site. Output is a report that informs whether we need to backfill connections.

