#!/usr/bin/env python3
"""
Market Intelligence Migration Script (Worker 6)
==============================================
Consolidates GTM/market intelligence from Legacy_Inbox into 
Personal/Knowledge/Intelligence/World/Market/ per Phase 3 plan.

Usage:
    python3 N5/scripts/knowledge_migrate_market_intel.py --dry-run
    python3 N5/scripts/knowledge_migrate_market_intel.py --execute

Created: 2025-11-29
Orchestrator: con_Nd2RpEkeELRh3SBJ
Task ID: W6-MARKET-INTEL-MIGRATION
"""

import argparse
import hashlib
import json
import logging
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

WORKSPACE = Path("/home/workspace")

# Canonical target paths (from knowledge_paths.yaml)
TARGET_ROOT = WORKSPACE / "Personal/Knowledge/Intelligence/World/Market"
TARGET_DB_DIR = TARGET_ROOT / "db"
TARGET_NARRATIVES = TARGET_ROOT / "narratives"

# Legacy source paths
LEGACY_MARKET_INTEL = WORKSPACE / "Personal/Knowledge/Legacy_Inbox/market_intelligence"
LEGACY_MARKET = WORKSPACE / "Personal/Knowledge/Legacy_Inbox/market"
LEGACY_MARKET_INTEL_ALT = WORKSPACE / "Personal/Knowledge/Legacy_Inbox/market-intelligence"

# Archive destination for historical-only files
ARCHIVE_ROOT = WORKSPACE / "Personal/Knowledge/Archive/MarketIntelligence"

# Migration log path
LOG_DIR = WORKSPACE / "Records/Personal/knowledge-system/logs"

# Files that are operational/transient (not narratives)
OPERATIONAL_FILES = {
    "BACKFILL_REPORT.md",
    "DATABASE_CONTENTS.md",
    "SCHEDULED_TASK_CREATED.md",
    "UNPROCESSED_MEETINGS_MARKED.md",
    "README.md",
}

# Files that are scripts (skip in narrative migration)
SCRIPT_EXTENSIONS = {".py", ".sh", ".js"}

# Protection check script
PROTECT_SCRIPT = WORKSPACE / "N5/scripts/n5_protect.py"

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Data Classes
# -----------------------------------------------------------------------------

class FileDisposition(Enum):
    """How to handle a legacy file."""
    PROMOTE = "promote"       # Move to canonical location
    ARCHIVE = "archive"       # Move to archive (historical-only)
    SKIP = "skip"             # Don't migrate (operational/transient)
    COPY_DB = "copy_db"       # Copy database with backup
    COPY_REGISTRY = "copy_registry"  # Copy registry file


@dataclass
class MigrationAction:
    """A single migration action to perform."""
    disposition: FileDisposition
    source: Path
    destination: Path
    reason: str
    backup_path: Optional[Path] = None


@dataclass
class MigrationPlan:
    """Complete migration plan."""
    db_actions: list[MigrationAction] = field(default_factory=list)
    registry_actions: list[MigrationAction] = field(default_factory=list)
    narrative_promote: list[MigrationAction] = field(default_factory=list)
    narrative_archive: list[MigrationAction] = field(default_factory=list)
    skipped: list[MigrationAction] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    
    @property
    def total_actions(self) -> int:
        return (len(self.db_actions) + len(self.registry_actions) + 
                len(self.narrative_promote) + len(self.narrative_archive))


@dataclass
class MigrationReport:
    """Results of migration execution."""
    timestamp: str
    mode: str  # dry-run or execute
    plan: MigrationPlan
    executed_db: int = 0
    executed_registry: int = 0
    executed_promote: int = 0
    executed_archive: int = 0
    failed: list[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        return len(self.failed) == 0


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def check_protected(path: Path) -> tuple[bool, Optional[str]]:
    """
    Check if path or any parent directory is protected via n5_protect.py.
    Returns (is_protected, reason_if_protected).
    
    NOTE: For COPY operations, protection is logged but not blocking.
    Protection only blocks MOVE/DELETE operations.
    """
    if not PROTECT_SCRIPT.exists():
        logger.warning(f"Protection script not found: {PROTECT_SCRIPT}")
        return (False, None)
    
    try:
        result = subprocess.run(
            ["python3", str(PROTECT_SCRIPT), "check", str(path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Protected if script indicates protection
        is_protected = "protected" in result.stdout.lower()
        reason = None
        if is_protected:
            # Extract reason from output
            for line in result.stdout.split('\n'):
                if 'Reason:' in line:
                    reason = line.split('Reason:')[1].strip()
                    break
        return (is_protected, reason)
    except Exception as e:
        logger.warning(f"Protection check failed for {path}: {e}")
        return (False, None)


def compute_file_hash(path: Path) -> str:
    """Compute MD5 hash for a file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_narrative(file_path: Path) -> FileDisposition:
    """
    Classify a narrative file as PROMOTE or ARCHIVE.
    
    Current logic:
    - Files in OPERATIONAL_FILES → SKIP
    - Scripts → SKIP
    - Files with substantive content (>500 chars after frontmatter) → PROMOTE
    - Small/stub files → ARCHIVE
    """
    name = file_path.name
    
    if name in OPERATIONAL_FILES:
        return FileDisposition.SKIP
    
    if file_path.suffix.lower() in SCRIPT_EXTENSIONS:
        return FileDisposition.SKIP
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        
        # Strip YAML frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Check substantive content (excluding whitespace)
        substantive = content.strip()
        
        # Heuristic: >500 chars of content = promote, else archive
        # But also check for actual prose vs just headers
        if len(substantive) > 500:
            return FileDisposition.PROMOTE
        else:
            return FileDisposition.ARCHIVE
            
    except Exception as e:
        logger.warning(f"Could not read {file_path} for classification: {e}")
        return FileDisposition.ARCHIVE


def ensure_dir(path: Path, dry_run: bool = False) -> bool:
    """Ensure directory exists."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would create directory: {path}")
        return True
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def safe_copy(src: Path, dst: Path, dry_run: bool = False) -> bool:
    """Copy file with directory creation."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would copy: {src} → {dst}")
        return True
    
    try:
        ensure_dir(dst.parent)
        shutil.copy2(src, dst)
        logger.info(f"Copied: {src} → {dst}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy {src} → {dst}: {e}")
        return False


def safe_move(src: Path, dst: Path, dry_run: bool = False) -> bool:
    """Move file with directory creation."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would move: {src} → {dst}")
        return True
    
    try:
        ensure_dir(dst.parent)
        shutil.move(str(src), str(dst))
        logger.info(f"Moved: {src} → {dst}")
        return True
    except Exception as e:
        logger.error(f"Failed to move {src} → {dst}: {e}")
        return False


def backup_db(db_path: Path, dry_run: bool = False) -> Optional[Path]:
    """Create backup of database before migration."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would backup DB: {db_path} → {backup_path}")
        return backup_path
    
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"DB backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to backup DB {db_path}: {e}")
        return None


def validate_db(db_path: Path) -> bool:
    """Validate SQLite database integrity."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        return result[0] == "ok"
    except Exception as e:
        logger.error(f"DB validation failed for {db_path}: {e}")
        return False


def files_match(src: Path, dst: Path) -> bool:
    """Check if source and destination files have identical content."""
    if not dst.exists():
        return False
    return compute_file_hash(src) == compute_file_hash(dst)


# -----------------------------------------------------------------------------
# Migration Planning
# -----------------------------------------------------------------------------

def build_migration_plan() -> MigrationPlan:
    """Build the complete migration plan by scanning sources."""
    plan = MigrationPlan()
    
    # --- 1. Database files ---
    db_sources = [
        LEGACY_MARKET_INTEL / "gtm_intelligence.db",
    ]
    
    for db_src in db_sources:
        if db_src.exists():
            db_name = db_src.name
            db_dst = TARGET_DB_DIR / db_name
            
            # Idempotency check: skip if destination exists with same content
            if files_match(db_src, db_dst):
                logger.info(f"Skipping (already migrated): {db_src.name}")
                continue
            
            is_protected, reason = check_protected(db_src)
            if is_protected:
                logger.info(f"Note: Source is protected ({reason}) - proceeding with copy (non-destructive)")
            
            backup = TARGET_DB_DIR / f"{db_src.stem}_backup_TIMESTAMP{db_src.suffix}"
            
            plan.db_actions.append(MigrationAction(
                disposition=FileDisposition.COPY_DB,
                source=db_src,
                destination=db_dst,
                reason=f"Primary GTM intelligence database{' [source protected]' if is_protected else ''}",
                backup_path=backup
            ))
    
    # --- 2. Registry files (JSONL) ---
    registry_sources = [
        LEGACY_MARKET_INTEL_ALT / "meeting_registry.jsonl",
        LEGACY_MARKET_INTEL_ALT / "meeting-processing-registry.jsonl",
    ]
    
    for reg_src in registry_sources:
        if reg_src.exists():
            reg_dst = TARGET_ROOT / reg_src.name
            
            # Idempotency check
            if files_match(reg_src, reg_dst):
                logger.info(f"Skipping (already migrated): {reg_src.name}")
                continue
            
            is_protected, reason = check_protected(reg_src)
            if is_protected:
                logger.info(f"Note: Source is protected ({reason}) - proceeding with copy (non-destructive)")
            
            plan.registry_actions.append(MigrationAction(
                disposition=FileDisposition.COPY_REGISTRY,
                source=reg_src,
                destination=reg_dst,
                reason=f"Meeting registry for GTM tracking{' [source protected]' if is_protected else ''}"
            ))
    
    # --- 3. Narrative files (MD) ---
    narrative_sources = [
        LEGACY_MARKET_INTEL,
        LEGACY_MARKET,
        LEGACY_MARKET_INTEL_ALT,
    ]
    
    for src_dir in narrative_sources:
        if not src_dir.exists():
            continue
        
        for md_file in src_dir.glob("*.md"):
            disposition = classify_narrative(md_file)
            
            if disposition == FileDisposition.SKIP:
                plan.skipped.append(MigrationAction(
                    disposition=FileDisposition.SKIP,
                    source=md_file,
                    destination=md_file,
                    reason="Operational/transient file"
                ))
                continue
            
            # Determine destination based on disposition
            if disposition == FileDisposition.PROMOTE:
                dst = TARGET_NARRATIVES / md_file.name
            else:  # ARCHIVE
                dst = ARCHIVE_ROOT / md_file.name
            
            # Idempotency check
            if files_match(md_file, dst):
                logger.info(f"Skipping (already migrated): {md_file.name}")
                continue
            
            is_protected, reason = check_protected(md_file)
            if is_protected:
                logger.info(f"Note: {md_file.name} protected ({reason}) - proceeding with copy")
            
            if disposition == FileDisposition.PROMOTE:
                plan.narrative_promote.append(MigrationAction(
                    disposition=FileDisposition.PROMOTE,
                    source=md_file,
                    destination=dst,
                    reason=f"Substantive narrative content{' [source protected]' if is_protected else ''}"
                ))
            elif disposition == FileDisposition.ARCHIVE:
                plan.narrative_archive.append(MigrationAction(
                    disposition=FileDisposition.ARCHIVE,
                    source=md_file,
                    destination=dst,
                    reason=f"Historical/stub content{' [source protected]' if is_protected else ''}"
                ))
    
    return plan


# -----------------------------------------------------------------------------
# Migration Execution
# -----------------------------------------------------------------------------

def execute_migration(plan: MigrationPlan, dry_run: bool = False) -> MigrationReport:
    """Execute the migration plan."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    report = MigrationReport(
        timestamp=timestamp,
        mode="dry-run" if dry_run else "execute",
        plan=plan
    )
    
    # Create target directories
    if not dry_run:
        for d in [TARGET_ROOT, TARGET_DB_DIR, TARGET_NARRATIVES, ARCHIVE_ROOT]:
            ensure_dir(d)
    else:
        for d in [TARGET_ROOT, TARGET_DB_DIR, TARGET_NARRATIVES, ARCHIVE_ROOT]:
            logger.info(f"[DRY-RUN] Would ensure directory: {d}")
    
    # --- Execute DB migrations ---
    for action in plan.db_actions:
        if not dry_run:
            # Validate source DB first
            if not validate_db(action.source):
                report.failed.append(f"DB validation failed: {action.source}")
                continue
            
            # Create backup
            backup = backup_db(action.source, dry_run=False)
            if not backup:
                report.failed.append(f"DB backup failed: {action.source}")
                continue
            
            # Copy to destination
            if safe_copy(action.source, action.destination, dry_run=False):
                # Validate destination
                if validate_db(action.destination):
                    report.executed_db += 1
                    logger.info(f"✓ DB migrated: {action.destination}")
                else:
                    report.failed.append(f"Destination DB validation failed: {action.destination}")
            else:
                report.failed.append(f"DB copy failed: {action.source}")
        else:
            logger.info(f"[DRY-RUN] DB: {action.source} → {action.destination}")
            report.executed_db += 1
    
    # --- Execute registry migrations ---
    for action in plan.registry_actions:
        if safe_copy(action.source, action.destination, dry_run=dry_run):
            report.executed_registry += 1
        else:
            report.failed.append(f"Registry copy failed: {action.source}")
    
    # --- Execute narrative promotions ---
    for action in plan.narrative_promote:
        if safe_copy(action.source, action.destination, dry_run=dry_run):
            report.executed_promote += 1
        else:
            report.failed.append(f"Narrative promote failed: {action.source}")
    
    # --- Execute narrative archives ---
    for action in plan.narrative_archive:
        if safe_copy(action.source, action.destination, dry_run=dry_run):
            report.executed_archive += 1
        else:
            report.failed.append(f"Narrative archive failed: {action.source}")
    
    return report


# -----------------------------------------------------------------------------
# Report Generation
# -----------------------------------------------------------------------------

def generate_report(report: MigrationReport) -> str:
    """Generate markdown migration report."""
    lines = [
        "---",
        f"created: {report.timestamp[:10]}",
        f"last_edited: {report.timestamp[:10]}",
        "version: 1.0",
        "---",
        "",
        "# Market Intelligence Migration Report",
        "",
        f"**Timestamp:** {report.timestamp}",
        f"**Mode:** {report.mode}",
        f"**Status:** {'✅ SUCCESS' if report.success else '❌ FAILED'}",
        "",
        "## Summary",
        "",
        f"| Category | Planned | Executed |",
        f"|----------|---------|----------|",
        f"| Databases | {len(report.plan.db_actions)} | {report.executed_db} |",
        f"| Registries | {len(report.plan.registry_actions)} | {report.executed_registry} |",
        f"| Narratives (Promoted) | {len(report.plan.narrative_promote)} | {report.executed_promote} |",
        f"| Narratives (Archived) | {len(report.plan.narrative_archive)} | {report.executed_archive} |",
        f"| Skipped | {len(report.plan.skipped)} | - |",
        "",
    ]
    
    # Database details
    if report.plan.db_actions:
        lines.extend([
            "## Database Migrations",
            "",
        ])
        for action in report.plan.db_actions:
            lines.append(f"- `{action.source.name}` → `{action.destination}`")
            lines.append(f"  - Reason: {action.reason}")
        lines.append("")
    
    # Registry details
    if report.plan.registry_actions:
        lines.extend([
            "## Registry Migrations",
            "",
        ])
        for action in report.plan.registry_actions:
            lines.append(f"- `{action.source.name}` → `{action.destination}`")
        lines.append("")
    
    # Promoted narratives
    if report.plan.narrative_promote:
        lines.extend([
            "## Narratives Promoted (Canonical)",
            "",
        ])
        for action in report.plan.narrative_promote:
            lines.append(f"- `{action.source.name}` → `narratives/`")
        lines.append("")
    
    # Archived narratives
    if report.plan.narrative_archive:
        lines.extend([
            "## Narratives Archived (Historical)",
            "",
        ])
        for action in report.plan.narrative_archive:
            lines.append(f"- `{action.source.name}` → Archive")
        lines.append("")
    
    # Skipped files
    if report.plan.skipped:
        lines.extend([
            "## Files Skipped",
            "",
        ])
        for action in report.plan.skipped:
            lines.append(f"- `{action.source.name}` - {action.reason}")
        lines.append("")
    
    # Errors
    if report.plan.errors:
        lines.extend([
            "## Errors (Pre-execution)",
            "",
        ])
        for err in report.plan.errors:
            lines.append(f"- ⚠️ {err}")
        lines.append("")
    
    if report.failed:
        lines.extend([
            "## Failures (During execution)",
            "",
        ])
        for fail in report.failed:
            lines.append(f"- ❌ {fail}")
        lines.append("")
    
    # Canonical structure
    lines.extend([
        "## Canonical Structure After Migration",
        "",
        "```",
        "Personal/Knowledge/Intelligence/World/Market/",
        "├── db/",
        "│   └── gtm_intelligence.db",
        "├── meeting_registry.jsonl",
        "├── meeting-processing-registry.jsonl",
        "└── narratives/",
        "    └── *.md",
        "```",
        "",
        "---",
        "",
        "*Generated by knowledge_migrate_market_intel.py*",
    ])
    
    return "\n".join(lines)


def save_report(report: MigrationReport, dry_run: bool = False) -> Optional[Path]:
    """Save migration report to Records."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"market_intel_migration_run_{timestamp}.md"
    report_path = LOG_DIR / filename
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would save report to: {report_path}")
        return report_path
    
    try:
        ensure_dir(LOG_DIR)
        content = generate_report(report)
        report_path.write_text(content)
        logger.info(f"Report saved: {report_path}")
        return report_path
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        return None


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Migrate market intelligence to canonical location"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", 
                       help="Show planned actions without executing")
    group.add_argument("--execute", action="store_true",
                       help="Execute the migration")
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    logger.info("=" * 60)
    logger.info("Market Intelligence Migration Script")
    logger.info(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    logger.info("=" * 60)
    
    # Build plan
    logger.info("Building migration plan...")
    plan = build_migration_plan()
    
    logger.info(f"Plan summary:")
    logger.info(f"  - DB files: {len(plan.db_actions)}")
    logger.info(f"  - Registry files: {len(plan.registry_actions)}")
    logger.info(f"  - Narratives to promote: {len(plan.narrative_promote)}")
    logger.info(f"  - Narratives to archive: {len(plan.narrative_archive)}")
    logger.info(f"  - Skipped: {len(plan.skipped)}")
    logger.info(f"  - Pre-execution errors: {len(plan.errors)}")
    
    if plan.errors:
        for err in plan.errors:
            logger.warning(f"  ⚠️ {err}")
    
    # Execute
    logger.info("")
    logger.info("Executing migration...")
    report = execute_migration(plan, dry_run=dry_run)
    
    # Save report
    report_path = save_report(report, dry_run=dry_run)
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Migration Complete")
    logger.info("=" * 60)
    logger.info(f"DBs migrated: {report.executed_db}")
    logger.info(f"Registries migrated: {report.executed_registry}")
    logger.info(f"Narratives promoted: {report.executed_promote}")
    logger.info(f"Narratives archived: {report.executed_archive}")
    
    if report.failed:
        logger.error(f"Failures: {len(report.failed)}")
        for fail in report.failed:
            logger.error(f"  - {fail}")
        sys.exit(1)
    
    if report_path:
        logger.info(f"Report: {report_path}")
    
    logger.info("✓ Migration successful" if report.success else "✗ Migration had failures")
    sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()



