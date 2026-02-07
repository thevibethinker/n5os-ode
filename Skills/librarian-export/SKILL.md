---
name: librarian-export
description: Automated daily export pipeline that bundles curated skills from va and ships them to zoputer via the Consulting API. Runs at 9 AM ET, exports only changed Tier 0 content, verifies checksums, and notifies V via SMS.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
  created: "2026-02-06"
  build: consulting-zoffice-stack
  drop: D3.1
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_KqcJ9kLgj76a0Mne
---

# Librarian Export Pipeline

## Purpose

One-way skill export from va.zo.computer → zoputer.zo.computer. The pipeline:
1. Runs the content classifier to generate CONSULTING_MANIFEST.json
2. Filters for Tier 0 skills modified since last export
3. Bundles each skill with metadata and checksums
4. Uploads via the Consulting API layer
5. Verifies ingestion on zoputer
6. Logs results to the audit system
7. Notifies V via SMS

**Critical:** Export is ONE-WAY only. Never sync back from zoputer to prevent contamination.

## Usage

```bash
# Run the full daily export pipeline
python3 Skills/librarian-export/scripts/daily_export.py

# Force export specific skills (bypass change detection)
python3 Skills/librarian-export/scripts/daily_export.py --force content-classifier security-gate

# Dry run (no actual upload)
python3 Skills/librarian-export/scripts/daily_export.py --dry-run

# Export with verbose logging
python3 Skills/librarian-export/scripts/daily_export.py --verbose

# Bundle a single skill without uploading
python3 Skills/librarian-export/scripts/bundle_skill.py --skill content-classifier --output /tmp/bundle.tar.gz
```

## Scheduled Execution

The `DAILY_EXPORT_LIBRARIAN` agent runs this pipeline at 9:00 AM ET daily.

**Manual trigger:** V can text "export now" to trigger an immediate export cycle.

## Pipeline Flow

```
9:00 AM ET trigger
├── 1. Run content classifier
│   └── Generate CONSULTING_MANIFEST.json
├── 2. Filter Tier 0 content modified since last export
├── 3. For each skill to export:
│   ├── Create tarball
│   ├── Generate metadata.json
│   └── Calculate SHA-256 checksums
├── 4. Upload via consulting-api bundle_manager
├── 5. Verify ingestion (query zoputer endpoint)
├── 6. Update CONSULTING_MANIFEST.md
├── 7. Update N5/data/last_export.json
└── 8. Notify V via SMS
```

## Export Format

Each skill is bundled as a tarball:

```
content-classifier-v1.0.0-20260206.tar.gz
├── SKILL.md
├── scripts/
├── assets/
├── references/
└── metadata.json
```

**metadata.json:**
```json
{
  "name": "content-classifier",
  "version": "1.0.0",
  "exported_from": "va.zo.computer",
  "exported_at": "2026-02-06T09:00:00Z",
  "git_sha": "abc123def...",
  "files": ["SKILL.md", "scripts/scan.py", ...],
  "checksums": {
    "SKILL.md": "sha256:...",
    "scripts/scan.py": "sha256:..."
  },
  "notes": ""
}
```

## Change Detection

Skills are exported when:
- Git shows changes since last export timestamp
- OR `--force <skill-name>` flag is passed
- OR this is the skill's first export (not in last_export.json)

**State file:** `N5/data/last_export.json`
```json
{
  "last_run": "2026-02-06T14:00:00Z",
  "exports": {
    "content-classifier": {
      "version": "1.0.0",
      "exported_at": "2026-02-06T14:00:00Z",
      "git_sha": "abc123...",
      "checksum": "sha256:..."
    }
  }
}
```

## SMS Notifications

**On success:**
```
[Zoffice] Daily export complete. 3 skills synced to zoputer: content-classifier, security-gate, audit-logger. All checksums verified.
```

**On partial failure:**
```
[Zoffice] ⚠️ Export partial: 2/3 skills synced. Failed: audit-logger (timeout). Check email for details.
```

**On total failure:**
```
[Zoffice] ❌ Export failed: Unable to reach zoputer. 0 skills synced. Pipeline will retry at next scheduled run.
```

## Retry Logic

- Each skill upload is retried 3x with exponential backoff (1s, 2s, 4s)
- If all retries fail, the skill is marked as failed and reported
- Next scheduled run will re-attempt failed skills

## Export History

30 days of export history is retained at `N5/data/export_history/`:
```
N5/data/export_history/
├── 2026-02-06_090000.json
├── 2026-02-05_090000.json
└── ...
```

## Integration Points

- **content-classifier** (D2.2): Generates CONSULTING_MANIFEST.json
- **consulting-api** (D1.3): bundle_manager.py for transmission
- **audit-system** (D1.2): Logs all export operations
- **security-gate** (D1.1): Pre-validates bundles before export
