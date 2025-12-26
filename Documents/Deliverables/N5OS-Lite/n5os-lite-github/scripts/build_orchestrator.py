#!/usr/bin/env python3
"""
Build Orchestrator - Coordinate parallel workers for Content Library system
Creates worker assignments and tracks progress
"""

import json
from pathlib import Path
from datetime import datetime

WORKERS_DIR = Path("/home/workspace/N5/workers/")
ASSIGNMENTS_FILE = WORKERS_DIR / "assignments.jsonl"

class BuildOrchestrator:
    def __init__(self, project_name):
        self.project_name = project_name
        self.workers = []
        
    def create_worker(self, worker_id, component, description, dependencies=None, estimated_hours=None):
        """Create a discrete worker assignment"""
        assignment = {
            "worker_id": worker_id,
            "project": self.project_name,
            "component": component,
            "description": description,
            "status": "pending",
            "dependencies": dependencies or [],
            "estimated_hours": estimated_hours,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "output_path": None
        }
        
        # Ensure workers directory exists
        WORKERS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Write assignment
        with open(ASSIGNMENTS_FILE, "a") as f:
            f.write(json.dumps(assignment) + "\n")
        
        self.workers.append(worker_id)
        return assignment
    
    def list_workers(self):
        """List all workers and their status"""
        if not ASSIGNMENTS_FILE.exists():
            return []
        
        workers = []
        with open(ASSIGNMENTS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    workers.append(json.loads(line))
        
        return workers
    
    def get_ready_workers(self):
        """Get workers whose dependencies are complete"""
        all_workers = {w["worker_id"]: w for w in self.list_workers()}
        
        ready = []
        for worker in all_workers.values():
            if worker["status"] == "pending":
                # Check if all dependencies are complete
                deps_complete = all(
                    all_workers.get(dep, {}).get("status") == "completed"
                    for dep in worker.get("dependencies", [])
                )
                if deps_complete:
                    ready.append(worker)
        
        return ready

if __name__ == "__main__":
    import sys
    
    # Create orchestrator for Content Library build
    orchestrator = BuildOrchestrator("content-library-build-v1")
    
    # Worker 1: Database schema
    orchestrator.create_worker(
        worker_id="worker_schema",
        component="sqlite_schema",
        description="Create SQLite database schema for content library (content, blocks, topics, knowledge_refs tables)",
        dependencies=[],
        estimated_hours=2
    )
    
    # Worker 2: Settings/config
    orchestrator.create_worker(
        worker_id="worker_settings",
        component="system_settings",
        description="Create settings.json with file paths, entry types, block codes, rules",
        dependencies=[],
        estimated_hours=1
    )
    
    # Worker 3: Ingest raw materials
    orchestrator.create_worker(
        worker_id="worker_ingest_raw",
        component="ingest_raw",
        description="Build universal ingestion for raw materials (meetings, articles, emails, notes)",
        dependencies=["worker_schema", "worker_settings"],
        estimated_hours=4
    )
    
    # Worker 4: Ingest blocks
    orchestrator.create_worker(
        worker_id="worker_ingest_blocks",
        component="ingest_blocks",
        description="Build block ingestion from existing B-block files into content library",
        dependencies=["worker_schema", "worker_settings"],
        estimated_hours=3
    )
    
    # Worker 5: Query interface
    orchestrator.create_worker(
        worker_id="worker_query",
        component="query_interface",
        description="Build query system for searching materials, blocks, topics, tags",
        dependencies=["worker_ingest_raw", "worker_ingest_blocks"],
        estimated_hours=4
    )
    
    # Worker 6: Knowledge bridge
    orchestrator.create_worker(
        worker_id="worker_knowledge_bridge",
        component="knowledge_bridge",
        description="Build promotion from content library to knowledge base (append-only)",
        dependencies=["worker_query"],
        estimated_hours=5
    )
    
    # Worker 7: Schema evolution/self-healing
    orchestrator.create_worker(
        worker_id="worker_evolution",
        component="schema_evolution",
        description="Build regeneration system for schema updates and reprocessing",
        dependencies=["worker_knowledge_bridge"],
        estimated_hours=2
    )
    
    # Worker 8: Documentation
    orchestrator.create_worker(
        worker_id="worker_docs",
        component="documentation",
        description="Write comprehensive docs for system usage, workflows, examples",
        dependencies=["worker_query", "worker_knowledge_bridge"],
        estimated_hours=2
    )
    
    # List all workers
    print("=" * 80)
    print(f"Content Library Build - {len(orchestrator.list_workers())} Workers Created")
    print("=" * 80)
    
    ready = orchestrator.get_ready_workers()
    print(f"\n✅ Ready to start: {len(ready)} workers")
    for w in ready:
        print(f"  - {w['worker_id']}: {w['component']} ({w['estimated_hours']}h)")
    
    blocked = [w for w in orchestrator.list_workers() if w["status"] == "pending" and w not in ready]
    if blocked:
        print(f"\n⏳ Blocked (waiting for dependencies): {len(blocked)}")
        for w in blocked:
            deps = ", ".join(w.get("dependencies", []))
            print(f"  - {w['worker_id']}: waiting on [{deps}]")

