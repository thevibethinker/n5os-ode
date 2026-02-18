#!/usr/bin/env python3
"""Migrate meeting edges from `edges.db` + pending JSONL into the unified graph."""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import sqlite3

sys.path.insert(0, "/home/workspace")

from N5.cognition.graph_store import GraphStore, BRAIN_DB

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOG = logging.getLogger("migrate_edges")

EDGES_DB = Path("/home/workspace/N5/data/edges.db")
PENDING_DIR = Path("/home/workspace/N5/review/edges/pending")
REPORT_PATH = Path("/home/workspace/N5/builds/unified-graph/completions/migrate_edges-report.json")


def backup_brain(dry_run: bool) -> Path:
    target = BRAIN_DB.with_suffix(f".backup-{datetime.now().strftime('%Y%m%d%H%M%S')}.db")
    LOG.info("Backing up brain.db -> %s", target)
    if not dry_run:
        shutil.copy(BRAIN_DB, target)
    return target


def migrate_edge_types(graph: GraphStore, dry_run: bool, report: Dict):
    if not EDGES_DB.exists():
        LOG.warning("edges.db not found, skipping committed edge types")
        return
    with sqlite3.connect(EDGES_DB) as conn:
        cursor = conn.execute("SELECT relation, category, description, inverse_relation FROM edge_types")
        for relation, category, description, inverse_relation in cursor:
            report["edge_types"] += 1
            LOG.debug("Migrating edge_type %s", relation)
            if not dry_run:
                graph.add_edge_type(relation, category, description, inverse_relation)


def migrate_committed_edges(graph: GraphStore, dry_run: bool, report: Dict):
    if not EDGES_DB.exists():
        LOG.warning("edges.db not found, skipping committed edges")
        return
    with sqlite3.connect(EDGES_DB) as conn:
        cursor = conn.execute(
            "SELECT source_type, source_id, relation, target_type, target_id, context_meeting_id, evidence, status, created_at, updated_at FROM edges"
        )
        for row in cursor:
            source_type, source_id, relation, target_type, target_id, meeting_id, evidence, status, created_at, updated_at = row
            meta = {
                "source": "edges.db",
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
            }
            report["committed"] += 1
            LOG.debug("Migrating committed edge %s -> %s", source_id, target_id)
            if not dry_run:
                graph.add_meeting_edge(
                    source_type=source_type,
                    source_id=source_id,
                    relation=relation,
                    target_type=target_type,
                    target_id=target_id,
                    meeting_id=meeting_id,
                    evidence=evidence or "",
                    status=status or "committed",
                    metadata=meta,
                )


def migrate_pending_edges(graph: GraphStore, dry_run: bool, report: Dict):
    if not PENDING_DIR.exists():
        LOG.warning("Pending edge directory missing, skipping")
        return
    for path in sorted(PENDING_DIR.glob("*.jsonl")):
        LOG.info("Processing pending file: %s", path.name)
        with open(path) as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    edge = json.loads(line)
                except json.JSONDecodeError as exc:
                    LOG.error("Skipping bad JSON line: %s", exc)
                    report["errors"].append(str(exc))
                    continue
                evidence = edge.get("evidence", "")
                if len(evidence) < 10 or not edge.get("source_id") or not edge.get("target_id"):
                    report["rejected"].append({
                        "line": line.strip(),
                        "reason": "Missing evidence/source/target",
                    })
                    continue
                report["pending"] += 1
                LOG.debug("Auto-committing pending edge %s -> %s", edge.get("source_id"), edge.get("target_id"))
                if not dry_run:
                    graph.add_meeting_edge(
                        source_type=edge.get("source_type", "idea"),
                        source_id=edge["source_id"],
                        relation=edge.get("relation", "related_to"),
                        target_type=edge.get("target_type", "idea"),
                        target_id=edge["target_id"],
                        meeting_id=edge.get("context_meeting_id"),
                        evidence=evidence,
                        status=edge.get("status", "auto-committed"),
                        metadata={"source": str(path.name)} if not dry_run else None,
                    )


def write_report(report: Dict):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as fh:
        json.dump(report, fh, indent=2)
    LOG.info("Report written to %s", REPORT_PATH)


def main():
    parser = argparse.ArgumentParser(description="Migrate edges into unified graph")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the migration")
    args = parser.parse_args()

    report = {
        "edge_types": 0,
        "committed": 0,
        "pending": 0,
        "rejected": [],
        "errors": [],
    }

    backup = backup_brain(args.dry_run)
    LOG.info("Backup path: %s", backup)

    graph = GraphStore()

    migrate_edge_types(graph, args.dry_run, report)
    migrate_committed_edges(graph, args.dry_run, report)
    migrate_pending_edges(graph, args.dry_run, report)

    if not args.dry_run:
        stats = graph.get_stats()
        LOG.info("Post-migration stats: %s", stats)
    write_report(report)

    if args.dry_run:
        LOG.info("Dry run completed. No writes were performed.")
    else:
        LOG.info("Migration completed. Meeting edges now live in brain.db")


if __name__ == "__main__":
    main()
