---
created: 2025-11-12
last_edited: 2025-11-12
version: 1.0
---

# Reasoning Pattern: Immutable External ID Triangulation

## Pattern Name
**Immutable External ID Triangulation with Bidirectional Sync**

## Context
When tracking entities that span multiple systems where data can be lost/corrupted.

## Problem
- Internal IDs (filenames, paths) can change
- Data files (metadata) can be lost/corrupted
- Need bulletproof tracking across system boundaries

## Solution Structure
1. Use immutable external IDs (e.g., Google IDs, UUIDs) as primary keys
2. Store IDs in MULTIPLE locations (registry + metadata)
3. Implement bidirectional sync (either can restore the other)
4. Define clear conflict resolution hierarchy
5. Build recovery tools for when data is lost

## Key Insights
- **Redundancy > Efficiency** for critical tracking
- External IDs must be immutable (controlled by external system)
- Need validation that ID → entity mapping stays consistent
- Recovery tools are mandatory, not optional

## Application to Meeting System
- Drive ID (immutable) stored in registry + metadata.json
- Calendar ID (immutable) stored in metadata.json
- Folder name (mutable) derived from other fields
- Registry ↔ Metadata can restore each other
- Daily validation ensures consistency

## When to Reuse
- Multi-system entity tracking
- High reliability requirements  
- Data loss is possible
- External systems provide immutable IDs

## Related Patterns
- Database foreign key constraints
- Event sourcing with correlation IDs
- Distributed system entity resolution

