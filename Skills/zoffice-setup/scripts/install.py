#!/usr/bin/env python3
"""
Zoffice Layer 1 Installer

Creates the Zoffice directory structure, config files, database, and registry.
All operations are idempotent — safe to run multiple times.

Usage:
    python3 Skills/zoffice-setup/scripts/install.py [--dry-run]
"""

import argparse
import json
import os
import sys
from pathlib import Path

WORKSPACE = Path("/home/workspace")
ZOFFICE = WORKSPACE / "Zoffice"

DIRECTORIES = [
    "config",
    "capabilities/ingestion/handlers",
    "capabilities/communication/channels",
    "capabilities/communication/templates",
    "capabilities/publishing/pipelines",
    "capabilities/orchestration/scheduler",
    "capabilities/orchestration/workflows",
    "capabilities/zo2zo/trust",
    "capabilities/zo2zo/protocols",
    "capabilities/security/gates",
    "capabilities/security/audit",
    "capabilities/hr/evaluation",
    "capabilities/hr/development",
    "capabilities/memory",
    "staff/_template/knowledge",
    "staff/_template/tools",
    "staff/receptionist/knowledge",
    "staff/receptionist/tools",
    "staff/chief-of-staff/knowledge",
    "staff/chief-of-staff/tools",
    "staff/librarian/knowledge",
    "staff/librarian/tools",
    "data/contacts",
    "data/conversations",
    "data/decisions",
    "knowledge/about-owner",
    "knowledge/products",
    "knowledge/clients",
    "knowledge/domain",
    "scripts",
]

CONFIG_FILES = {
    "config/office.yaml": """# Zoffice Identity Configuration
office:
  name: "Zoffice"
  handle: null
  owner: null
  domain: null
  parent: null
  version: "1.0.0"
  installed_at: null
custom: {}
""",
    "config/autonomy.yaml": """# Zoffice Autonomy Configuration
thresholds:
  auto_act: 0.9
  act_and_notify: 0.7
  escalate_to_parent: 0.5
  escalate_to_human: 0.3
always_escalate:
  - send_email
  - delete_file
  - create_scheduled_task
  - register_service
  - payment_action
  - modify_config
never_escalate:
  - read_file
  - search
  - web_research
  - list_files
  - lookup_contact
custom: {}
""",
    "config/capabilities.yaml": """# Zoffice Capabilities Configuration
capabilities:
  ingestion:
    status: pending
    channels: []
  communication:
    status: pending
    channels: []
  publishing:
    status: pending
    platforms: []
  orchestration:
    status: pending
    dispatchers: []
  zo2zo:
    status: pending
    parent: null
  security:
    status: pending
    level: strict
  hr:
    status: pending
    evaluation_cadence: weekly
  memory:
    status: pending
    db: Zoffice/data/office.db
custom: {}
""",
    "config/routing.yaml": """# Zoffice Routing Configuration
routes:
  voice:
    default: receptionist
    patterns: []
  email:
    default: chief-of-staff
    patterns: []
  sms:
    default: receptionist
    patterns: []
  zo2zo:
    default: receptionist
    patterns: []
  webhook:
    default: chief-of-staff
    patterns: []
fallback: receptionist
custom: {}
""",
    "config/security.yaml": """# Zoffice Security Configuration
security:
  level: strict
  gates:
    inbound:
      enabled: true
      adversarial_detection: true
      pii_filter: true
    outbound:
      enabled: true
      content_review: true
  trust:
    trusted_instances: []
    trusted_domains: []
  audit:
    enabled: true
    retention_days: 365
    hash_verification: true
  api_keys:
    parent_key_env: null
    zo2zo_key_env: null
custom: {}
""",
}

MANIFEST = {
    "product": "Zoffice",
    "version": "1.0.0",
    "layer": 1,
    "requires_layer_0": "n5os-bootstrap >= 1.0",
    "installed_at": None,
    "installed_by": None,
    "instance": {
        "name": None,
        "handle": None,
        "owner": None,
        "parent": None,
    },
    "capabilities_installed": [],
    "staff_installed": [],
    "schema_version": "1.0",
}

CAPABILITY_READMES = {
    "security": "Validates inbound content, filters PII, maintains immutable audit trail. Cannot be disabled.",
    "memory": "Stores and retrieves contacts, conversations, and decisions via office.db.",
    "ingestion": "Receives and classifies inbound content from all channels.",
    "communication": "Manages outbound messages with channel selection and approval gates.",
    "orchestration": "Manages recurring tasks and multi-step workflows.",
    "zo2zo": "Enables communication between Zo Computer instances.",
    "publishing": "Manages content pipelines and public-facing output.",
    "hr": "Manages employee lifecycle — evaluation, onboarding, handoffs, sync.",
}

REGISTRY = """# Zoffice Staff Registry
staff: []
total_staff: 0
last_synced: null
"""

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit (
  id VARCHAR PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  capability VARCHAR NOT NULL,
  employee VARCHAR,
  action VARCHAR NOT NULL,
  channel VARCHAR,
  counterparty VARCHAR,
  content_hash VARCHAR,
  metadata JSON,
  parent_event_id VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_employee ON audit(employee);
CREATE INDEX IF NOT EXISTS idx_audit_capability ON audit(capability);
CREATE INDEX IF NOT EXISTS idx_audit_channel ON audit(channel);

CREATE TABLE IF NOT EXISTS contacts (
  id VARCHAR PRIMARY KEY,
  name VARCHAR,
  email VARCHAR,
  phone VARCHAR,
  organization VARCHAR,
  relationship VARCHAR,
  first_contact TIMESTAMP,
  last_contact TIMESTAMP,
  interaction_count INTEGER DEFAULT 0,
  profile JSON,
  tags VARCHAR[]
);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_relationship ON contacts(relationship);

CREATE TABLE IF NOT EXISTS decisions (
  id VARCHAR PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  origin_employee VARCHAR,
  summary TEXT NOT NULL,
  full_context JSON,
  options JSON,
  recommendation VARCHAR,
  status VARCHAR DEFAULT 'pending',
  resolved_at TIMESTAMP,
  resolution TEXT,
  resolved_by VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);
CREATE INDEX IF NOT EXISTS idx_decisions_created ON decisions(created_at);

CREATE TABLE IF NOT EXISTS conversations (
  id VARCHAR PRIMARY KEY,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  channel VARCHAR,
  employee VARCHAR,
  counterparty_id VARCHAR,
  summary TEXT,
  duration_seconds INTEGER,
  satisfaction DOUBLE,
  metadata JSON
);
CREATE INDEX IF NOT EXISTS idx_conversations_channel ON conversations(channel);
CREATE INDEX IF NOT EXISTS idx_conversations_employee ON conversations(employee);
CREATE INDEX IF NOT EXISTS idx_conversations_started ON conversations(started_at);

CREATE TABLE IF NOT EXISTS evaluations (
  id VARCHAR PRIMARY KEY,
  employee VARCHAR NOT NULL,
  evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  scenario_scores JSON,
  overall_score DOUBLE,
  strengths TEXT,
  improvements TEXT,
  evaluator VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_evaluations_employee ON evaluations(employee);
CREATE INDEX IF NOT EXISTS idx_evaluations_date ON evaluations(evaluated_at);
"""


def check_layer_0():
    """Verify Layer 0 (n5os-bootstrap) is present."""
    return (WORKSPACE / "N5" / "prefs").is_dir()


def install_directories(dry_run=False):
    created = 0
    for d in DIRECTORIES:
        path = ZOFFICE / d
        if not path.exists():
            if dry_run:
                print(f"  [dry-run] mkdir -p {path}")
            else:
                path.mkdir(parents=True, exist_ok=True)
            created += 1
    return created


def install_configs(dry_run=False):
    written = 0
    for relpath, content in CONFIG_FILES.items():
        path = ZOFFICE / relpath
        if not path.exists():
            if dry_run:
                print(f"  [dry-run] write {path}")
            else:
                path.write_text(content)
            written += 1
        else:
            print(f"  [skip] {relpath} already exists")
    return written


def install_manifest(dry_run=False):
    path = ZOFFICE / "MANIFEST.json"
    if not path.exists():
        if dry_run:
            print(f"  [dry-run] write {path}")
        else:
            path.write_text(json.dumps(MANIFEST, indent=2) + "\n")
        return 1
    else:
        print(f"  [skip] MANIFEST.json already exists")
        return 0


def install_capability_readmes(dry_run=False):
    written = 0
    for cap, desc in CAPABILITY_READMES.items():
        path = ZOFFICE / "capabilities" / cap / "README.md"
        if not path.exists():
            content = f"# {cap.title()} Capability\n\n**Status:** pending\n\n{desc}\n"
            if dry_run:
                print(f"  [dry-run] write {path}")
            else:
                path.write_text(content)
            written += 1
        else:
            print(f"  [skip] capabilities/{cap}/README.md already exists")
    return written


def install_registry(dry_run=False):
    path = ZOFFICE / "staff" / "registry.yaml"
    if not path.exists():
        if dry_run:
            print(f"  [dry-run] write {path}")
        else:
            path.write_text(REGISTRY)
        return 1
    else:
        print(f"  [skip] staff/registry.yaml already exists")
        return 0


def install_database(dry_run=False):
    db_path = ZOFFICE / "data" / "office.db"
    if dry_run:
        print(f"  [dry-run] create database {db_path}")
        print(f"  [dry-run] create 5 tables with indexes")
        return 1

    import duckdb
    con = duckdb.connect(str(db_path))
    for statement in DB_SCHEMA.strip().split(";"):
        statement = statement.strip()
        if statement:
            con.execute(statement)
    con.close()
    return 1


def main():
    parser = argparse.ArgumentParser(description="Zoffice Layer 1 Installer")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without executing")
    args = parser.parse_args()

    print("=" * 60)
    print("  Zoffice Layer 1 Installer")
    print("=" * 60)

    if args.dry_run:
        print("\n  *** DRY RUN — no changes will be made ***\n")

    # Step 1: Check Layer 0
    print("\n[1/7] Checking Layer 0 (n5os-bootstrap)...")
    if not check_layer_0():
        print("  ✗ Layer 0 not found (N5/prefs/ missing)")
        print("  Install n5os-bootstrap first.")
        sys.exit(1)
    print("  ✓ Layer 0 present")

    # Step 2: Create directories
    print("\n[2/7] Creating directory tree...")
    n = install_directories(args.dry_run)
    print(f"  ✓ {n} directories created ({len(DIRECTORIES)} total)")

    # Step 3: Write config files
    print("\n[3/7] Writing config files...")
    n = install_configs(args.dry_run)
    print(f"  ✓ {n} config files written")

    # Step 4: Write MANIFEST.json
    print("\n[4/7] Writing MANIFEST.json...")
    install_manifest(args.dry_run)

    # Step 5: Write capability READMEs
    print("\n[5/7] Writing capability READMEs...")
    n = install_capability_readmes(args.dry_run)
    print(f"  ✓ {n} READMEs written")

    # Step 6: Write staff registry
    print("\n[6/7] Writing staff registry...")
    install_registry(args.dry_run)

    # Step 7: Create database
    print("\n[7/7] Creating office.db...")
    install_database(args.dry_run)
    print("  ✓ Database created with 5 tables")

    print("\n" + "=" * 60)
    if args.dry_run:
        print("  Dry run complete. No changes made.")
    else:
        print("  ✓ Zoffice Layer 1 installed successfully.")
        print("  Run healthcheck: python3 Skills/zoffice-setup/scripts/healthcheck.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
