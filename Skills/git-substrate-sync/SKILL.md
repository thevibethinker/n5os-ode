---
name: git-substrate-sync
description: Skill that handles pushing content from va to the GitHub substrate and can be triggered by zoputer to pull updates. Provides the git layer for the va ↔ zoputer content sync pipeline.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
  created: "2026-02-07"
  build: zoputer-autonomy-v2
  drop: D1.2
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
provenance: con_nz9HgESqnYwwHhWf
---

# Git Substrate Sync

## Purpose

Provides the GitHub substrate synchronization layer for content exchange between va.zo.computer and zoputer.zo.computer. This skill handles the git operations while the consulting-api and librarian-export skills handle the higher-level bundling and transmission logic.

## Architecture

```
va.zo.computer                    GitHub Substrate               zoputer.zo.computer
┌─────────────┐                  ┌─────────────────┐             ┌─────────────────┐
│librarian-   │ bundles skills   │zoputer-substrate│  pulls      │localization-    │
│export       │ ──────────────► │(private repo)   │ ◄─────────── │maintainer       │
└─────────────┘                  │                 │             │                 │
       │                         │- Skills/        │             │                 │
       ▼                         │- MANIFEST.json  │             │                 │
┌─────────────┐                  │- metadata/      │             │                 │
│git-substrate│ push/pull ops    │- .gitignore     │             │                 │
│sync (THIS)  │ ◄─────────────► │                 │             │                 │
└─────────────┘                  └─────────────────┘             └─────────────────┘
```

**Flow:**
1. librarian-export → calls this skill to push Tier 0 content to GitHub
2. zoputer's localization-maintainer → calls this skill's pull script to fetch updates
3. All git operations isolated here for reusability and safety

## Usage

### va-side (Push to GitHub)

```bash
# Push latest Tier 0 content to substrate repo
python3 Skills/git-substrate-sync/scripts/sync.py push

# Dry run to see what would be pushed
python3 Skills/git-substrate-sync/scripts/sync.py push --dry-run

# Push specific skills only
python3 Skills/git-substrate-sync/scripts/sync.py push --skills content-classifier,audit-system

# Check status of local vs remote
python3 Skills/git-substrate-sync/scripts/sync.py status

# View recent sync history
python3 Skills/git-substrate-sync/scripts/sync.py history
```

### zoputer-side (Pull from GitHub)

```bash
# Pull latest updates from substrate repo
python3 Skills/git-substrate-sync/scripts/pull.py

# Dry run to see what would be pulled
python3 Skills/git-substrate-sync/scripts/pull.py --dry-run

# Pull and show summary of changes
python3 Skills/git-substrate-sync/scripts/pull.py --verbose
```

## Repository Structure

The substrate repo (`zoputer-substrate`) follows this structure:

```
zoputer-substrate/
├── README.md                 # Repo overview
├── MANIFEST.json            # Master manifest with all exported content
├── Skills/                  # Exported skills directory
│   ├── content-classifier/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── assets/
│   ├── audit-system/
│   └── ...
├── Documents/               # Exported system docs (if any)
├── Prompts/                 # Exported prompts (if any)
└── metadata/                # Export metadata
    ├── last_sync.json       # Sync tracking
    └── export_history/      # Historical exports
```

## Integration Points

### With content-classifier
```python
from Skills.content_classifier.scripts.scan import classify_path, build_manifest

def get_tier_0_skills():
    manifest = build_manifest()
    tier_0_skills = [b for b in manifest['bundles'] 
                     if b['tier'] == 'Tier 0' and b['path'].startswith('Skills/')]
    return tier_0_skills
```

### With librarian-export
Called by librarian-export after bundling but before transmission:
```bash
# librarian-export calls this to sync to GitHub
python3 Skills/git-substrate-sync/scripts/sync.py push --skills skill1,skill2
```

### With audit-system
All sync operations are logged for audit trail:
```python
# Log sync operations
from Skills.audit_system.scripts.audit_logger import log_audit_event
log_audit_event("git_sync", "push_complete", {...})
```

## Safety Features

1. **Tier 0 Only**: Only pushes content classified as Tier 0 by content-classifier
2. **Clean Clone**: Always works in `/tmp/zoputer-substrate/` to avoid workspace pollution  
3. **Conflict Detection**: Aborts on merge conflicts, never auto-resolves
4. **Dry Run Support**: All operations support `--dry-run` for verification
5. **State Verification**: Always pulls before push to ensure clean state
6. **Audit Logging**: All operations logged to audit system

## Configuration

Repository URL and credentials are read from environment:
- `GITHUB_TOKEN`: Personal access token for authentication
- `GITHUB_REPO`: Repository URL (defaults to `vrijenattawar/zoputer-substrate`)

The skill reads these from Zo's secrets system automatically.

## Error Handling

**Common failure modes:**
- Repository doesn't exist → Clone fresh copy
- Local changes conflict → Stash changes and abort with warning
- Network failure → Retry with exponential backoff (3 attempts)
- Authentication failure → Clear error message pointing to token setup
- Disk space → Clean old temp directories and retry

**Never auto-resolves merge conflicts** - always escalates to human review.

## Dependencies

- Git 2.30+
- Python 3.9+
- Network access to GitHub
- Valid GITHUB_TOKEN in environment

## Change Tracking

Updates `metadata/last_sync.json` on each successful operation:
```json
{
  "last_push": "2026-02-07T14:30:00Z",
  "last_pull": "2026-02-07T14:25:00Z",
  "git_sha": "abc123def456...",
  "exported_skills": ["content-classifier", "audit-system"],
  "operation_id": "sync_20260207_143000"
}
```

## Testing

```bash
# Verify content-classifier integration
python3 Skills/git-substrate-sync/scripts/sync.py --test-classifier

# Test git operations without network
python3 Skills/git-substrate-sync/scripts/sync.py --test-git

# Full integration test with dry-run
python3 Skills/git-substrate-sync/scripts/sync.py push --dry-run --verbose
```