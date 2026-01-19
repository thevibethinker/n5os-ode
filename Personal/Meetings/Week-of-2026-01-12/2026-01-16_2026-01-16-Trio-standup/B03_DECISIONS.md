---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: 074838b3-3b6f-4e5c-a843-858a7d072141
---

# B03 - Decisions

## Decisions Made

### 1. Silent Scan Feature Enabled for Production
**Decision:** Enable silent database scanning for employer use
**Rationale:** Allows employers to scan candidate database without candidate awareness; enables auto-apply functionality
**Owner:** Ilse (technical), V (business enablement)

### 2. Credit/Day Limit Set at 250
**Decision:** Backend cap of 250 days on scanning regardless of UI settings
**Rationale:** Cost control - prevents runaway expenses from unlimited scans
**Owner:** Ilse

### 3. No Minimum Stories Restriction
**Decision:** Remove minimum stories requirement from UI
**Rationale:** V wants flexibility for paying customers
**Owner:** Ilse (implemented)

### 4. Duplicate Scan Prevention Active
**Decision:** System will prevent multiple simultaneous scans on same role
**Rationale:** Prevents "exotic and dumb" failure modes
**Owner:** Ilse

## Decisions Deferred

### CSV Export Enhancement
**Topic:** Adding more candidate data to CSV exports beyond email + scores
**Status:** Acknowledged need, not yet implemented
**Owner:** Ilse (future backlog)
