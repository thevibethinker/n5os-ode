---
project: Content Library System (SQLite + Block-Based)
created: 2025-11-12
total_workers: 8
status: ready
---
# Worker Assignments - Content Library Build

## Overview
Build unified Content Library system with SQLite storage and block-based ingestion.

## Workers Ready for Assignment

### Tier 1: Foundation (2 workers) ✅ COMPLETE

- `worker_schema` - ✅ Complete (2h)
  Output: `/home/workspace/Personal/Content-Library/content-library.db`
  
- `worker_settings` - ✅ Complete (1h)
  Output: `/home/workspace/Personal/Content-Library/settings.json`

### Tier 2: Ingestion (2 workers) - READY TO LAUNCH

- `worker_ingest_raw` - Ready
  Task: Build universal ingestion for raw materials
  Input: File paths or URLs
  Output: SQLite entries
  Dependencies: worker_schema, worker_settings
  Est: 3h
  
- `worker_ingest_blocks` - Ready
  Task: Ingest existing B-block files
  Input: Folder paths containing B-block files
  Output: SQLite block entries
  Dependencies: worker_schema, worker_settings
  Est: 2h

### Tier 3: Interface (3 workers) - BLOCKED

- `worker_query` - Blocked
  Task: Query and search interface
  Depends: worker_ingest_raw, worker_ingest_blocks
  Est: 2h
  
- `worker_knowledge_bridge` - Blocked
  Task: Append-only promotion to Knowledge
  Depends: worker_query
  Est: 2h
  
- `worker_evolution` - Blocked
  Task: Schema evolution for adding fields
  Depends: worker_knowledge_bridge
  Est: 1h

### Tier 4: Docs (1 worker) - BLOCKED

- `worker_docs` - Blocked
  Task: User documentation and examples
  Depends: worker_query, worker_knowledge_bridge
  Est: 2h

## How to Launch Workers

### Method 1: Sequential (same thread)
```bash
cd /home/workspace/N5/workers
python3 worker_ingest_raw.py
python3 worker_ingest_blocks.py
```

### Method 2: Parallel (new threads)
Copy assignment below and paste in new chat:
```
@run_worker worker_ingest_raw
```

## Launch Commands

----------------------------------------

**To launch worker_ingest_raw:**
```
Worker: worker_ingest_raw
Task: Build universal ingestion for raw materials
Input: File paths or URLs
Output: SQLite entries in content table
Dependencies: ✅ worker_schema, ✅ worker_settings
Priority: P0
Time estimate: 3 hours
Status: READY TO LAUNCH
```

**Worker file:** `/home/workspace/N5/workers/worker_ingest_raw.py`

----------------------------------------

**To launch worker_ingest_blocks:**
```
Worker: worker_ingest_blocks
Task: Ingest existing B-block files
Input: Folder paths containing B01-B100 block files
Output: SQLite entries in blocks table
Dependencies: ✅ worker_schema, ✅ worker_settings
Priority: P0
Time estimate: 2 hours
Status: READY TO LAUNCH
```

**Worker file:** `/home/workspace/N5/workers/worker_ingest_blocks.py`

----------------------------------------

**To launch worker_query:**
```
Worker: worker_query
Task: Query and search interface for Content Library
Input: SQLite database
Output: Query scripts and CLI tool
Dependencies: ⏳ worker_ingest_raw, ⏳ worker_ingest_blocks
Priority: P1
Time estimate: 2 hours
Status: BLOCKED (launch workers 3-4 first)
```

**Worker file:** `/home/workspace/N5/workers/worker_query.py`

----------------------------------------

**To launch worker_knowledge_bridge:**
```
Worker: worker_knowledge_bridge
Task: Append-only promotion to Knowledge Base
Input: SQLite database, knowledge system
Output: Promotion script + bridge table
Dependencies: ⏳ worker_query
Priority: P1
Time estimate: 2 hours
Status: BLOCKED (launch worker 5 first)
```

**Worker file:** `/home/workspace/N5/workers/worker_knowledge_bridge.py`

----------------------------------------

**To launch worker_evolution:**
```
Worker: worker_evolution
Task: Schema evolution for adding new fields
Input: Schema definitions
Output: Migration script
Dependencies: ⏳ worker_knowledge_bridge
Priority: P2
Time estimate: 1 hour
Status: BLOCKED (launch workers 3-6 first)
```

**Worker file:** `/home/workspace/N5/workers/worker_evolution.py`

----------------------------------------

**To launch worker_docs:**
```
Worker: worker_docs
Task: User documentation and examples
Input: Functioning system
Output: README.md, WORKFLOW.md, examples
Dependencies: ⏳ worker_query, ⏳ worker_knowledge_bridge
Priority: P2
Time estimate: 2 hours
Status: BLOCKED (launch workers 3-7 first)
```

**Worker file:** `/home/workspace/N5/workers/worker_docs.py`

## Next Steps

1. **Launch Tier 2 workers (3-4)** - Can start now
   - These run in parallel threads
   - No dependencies blocking them
   
2. **Wait for Tier 2 completion** - Then launch Tier 3 (5-7)
   - worker_query depends on workers 3-4
   - worker_knowledge_bridge depends on worker_query
   
3. **Finally launch Tier 4** - Documentation
   - Depends on workers 5-7

**Ready to launch? Copy any worker assignment above and paste in new chat.**

