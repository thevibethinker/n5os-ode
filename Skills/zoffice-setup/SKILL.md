---
name: zoffice-setup
description: Installs the Zoffice (Layer 1) on a Zo Computer. Creates directory structure, config schemas, DuckDB database, and validates the installation. Supports --dry-run for preview.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  layer: 1
  version: 1.0.0
---

# Zoffice Setup

Installs and validates a Zoffice (Layer 1) on a Zo Computer.

## Usage

**Full install:**
```bash
python3 Skills/zoffice-setup/scripts/install.py
```

**Dry run (preview without changes):**
```bash
python3 Skills/zoffice-setup/scripts/install.py --dry-run
```

**Health check (validate existing install):**
```bash
python3 Skills/zoffice-setup/scripts/healthcheck.py
```

**Export audit trail:**
```bash
python3 Zoffice/scripts/export-audit.py --format json --since 2026-01-01
```

## What It Does

1. Creates the `Zoffice/` directory tree (30 directories)
2. Writes 5 config YAML files with sensible defaults
3. Writes MANIFEST.json with office identity
4. Creates `office.db` DuckDB with 5 tables and indexes
5. Creates empty staff registry
6. Writes capability README.md placeholders
7. Runs healthcheck to validate

## Prerequisites

- Layer 0 (n5os-bootstrap) must be present
- Python 3.12+ with duckdb and pyyaml packages
- Zo Computer with root access

## Architecture Reference

See `file 'N5/builds/n5os-rice/artifacts/architecture-brief.md'` for the Troika Architecture that this installer implements.
