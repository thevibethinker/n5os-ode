# N5 Generalization Guide

**Purpose:** Instructions for separating personal content from distributable N5 OS Core system components

**Version:** 0.1  
**Last Updated:** 2025-10-28

---

## Overview

N5 as built contains both:
1. **Core system components** - Generalizable, distributable to others
2. **Personal content** - Your specific data, preferences, and customizations

This guide helps you extract the core system for distribution while preserving your personal instance.

## Core Philosophy

**Goal:** Anyone should be able to install N5 OS Core and get a clean, functional system without your personal data, but with all the architectural intelligence and automation built into your instance.

**Principle:** Generalization happens as side-effect of good architecture, not as separate activity.

---

## What To Distribute (Core)

### 1. System Architecture

**✓ Include:**
- Directory structure (`N5/`, `Knowledge/`, `Lists/`, `Records/`, `Documents/`)
- Architectural principles (`Knowledge/architectural/`)
- Planning prompt (`Knowledge/architectural/planning_prompt.md`)
- System documentation (`Documents/N5.md`)

**✗ Exclude:**
- Your specific knowledge articles
- Personal notes and documentation
- Company-specific information

**How:**
```bash
# Copy architectural foundations
mkdir -p n5-core-dist/Knowledge/architectural
cp -r Knowledge/architectural/* n5-core-dist/Knowledge/architectural/

# Create skeleton README
echo "# N5 System Overview" > n5-core-dist/Documents/N5.md
echo "See user guide for details." >> n5-core-dist/Documents/N5.md
```

### 2. Scripts & Automation

**✓ Include:**
- All scripts in `N5/scripts/` (they should be generalized)
- Schemas in `N5/schemas/`
- Command system (`N5/commands/` and compiler)

**✗ Exclude:**
- API keys and credentials
- Personal configurations
- Company-specific integrations

**How:**
```bash
# Copy scripts
cp -r N5/scripts n5-core-dist/N5/

# Copy schemas
cp -r N5/schemas n5-core-dist/N5/

# Copy commands (review each for personal data)
mkdir -p n5-core-dist/N5/commands
for cmd in N5/commands/*.md; do
    # Review and copy if generic
    cp "$cmd" n5-core-dist/N5/commands/
done
```

**Review checklist for each script:**
- [ ] No hardcoded email addresses
- [ ] No hardcoded names or company names
- [ ] No API keys embedded
- [ ] Paths use variables, not hardcoded
- [ ] Documentation uses examples, not real data

### 3. Configuration Templates

**✓ Include:**
- Default preferences (`N5/prefs/prefs.md` as template)
- Schema definitions
- Command system configuration structure

**✗ Exclude:**
- Your actual API keys
- Your specific preferences values
- Personal customizations

**How:**
```bash
# Create template with placeholders
cat > n5-core-dist/N5/prefs/prefs.md << 'EOF'
# N5 Preferences

## Touch Rate
- target: 15%
- alert_threshold: 25%

## Auto-Archive
- temporary_records_days: 14
- completed_tasks_days: 30

## Confidence Thresholds
- auto_triage: 0.85
- auto_categorize: 0.90

## SLA Defaults (hours)
- inbox_triage: 24
- records_processing: 168
EOF
```

### 4. Empty Data Structures

**✓ Include:**
- Empty lists (`Lists/inbox.md`, `Lists/someday.md`, `Lists/waiting.md`)
- Empty database schemas
- Directory structure for Records

**✗ Exclude:**
- Your actual list items
- Your actual records
- Your database data

**How:**
```bash
# Create empty lists
mkdir -p n5-core-dist/Lists
echo "# Inbox\n\n*New items requiring triage*\n\n" > n5-core-dist/Lists/inbox.md
echo "# Someday\n\n*Deferred but not forgotten*\n\n" > n5-core-dist/Lists/someday.md
echo "# Waiting\n\n*Blocked on external dependencies*\n\n" > n5-core-dist/Lists/waiting.md

# Create empty Records structure
mkdir -p n5-core-dist/Records/{Company,Personal,Temporary}
```

---

## What NOT To Distribute (Personal)

### 1. Stakeholder Intelligence
- Meeting notes with names
- Company-specific strategies
- Personal relationships and contacts
- Follow-up emails and content maps

### 2. Personal Data
- Health tracking
- Financial records
- Personal projects
- Learning notes with personal context

### 3. Credentials & Keys
- API keys
- OAuth tokens
- Database passwords
- Service credentials

### 4. Logs & History
- Conversation logs
- Session history
- Access logs
- Error logs with personal data

---

## Generalization Checklist

Use this checklist when preparing to distribute:

### Phase 1: Identify Core Components

- [ ] List all scripts in `N5/scripts/`
- [ ] List all commands in `N5/commands/`
- [ ] List all schemas in `N5/schemas/`
- [ ] List all architectural principles in `Knowledge/architectural/`
- [ ] Identify custom integrations

### Phase 2: Review Each Component

For each script/command/principle:
- [ ] Does it contain hardcoded personal data?
- [ ] Does it use environment variables for credentials?
- [ ] Are paths configurable or hardcoded?
- [ ] Is documentation generic or personal?
- [ ] Are examples using fake data?

### Phase 3: Extract & Sanitize

- [ ] Copy core directory structure to `n5-core-dist/`
- [ ] Copy architectural principles verbatim
- [ ] Copy scripts with sanitized configs
- [ ] Create template files for configuration
- [ ] Write comprehensive README
- [ ] Write user guide
- [ ] Write developer guide

### Phase 4: Test Clean Installation

- [ ] Install on fresh Zo instance
- [ ] Verify all scripts run with default config
- [ ] Test command system compiles
- [ ] Verify no personal data leaks
- [ ] Check for broken references

### Phase 5: Document

- [ ] README with overview
- [ ] Installation instructions
- [ ] Configuration guide
- [ ] Contribution guidelines
- [ ] License file

---

## Automation Script

Create `N5/scripts/generalize_for_distribution.py`:

```python
#!/usr/bin/env python3
"""
Generalize N5 for distribution.
Extracts core system components without personal data.
"""

import shutil
from pathlib import Path

# Core directories to copy structure
CORE_STRUCTURE = [
    "Documents",
    "Knowledge/architectural",
    "Lists",
    "Records/Company",
    "Records/Personal",
    "Records/Temporary",
    "N5/commands",
    "N5/config",
    "N5/data",  # Empty, structure only
    "N5/prefs",
    "N5/schemas",
    "N5/scripts",
]

# Files to copy verbatim
CORE_FILES = [
    "Knowledge/architectural/planning_prompt.md",
    "Knowledge/architectural/architectural_principles.md",
    # Add other core files
]

# Files to template (replace values with placeholders)
TEMPLATE_FILES = {
    "N5/prefs/prefs.md": {
        "replacements": {
            # Add personal→placeholder mappings
        }
    }
}

def main():
    source = Path("/home/workspace")
    dist = Path("/home/workspace/n5-core-dist")
    
    # Create structure
    for dir_path in CORE_STRUCTURE:
        (dist / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Copy core files
    for file_path in CORE_FILES:
        src = source / file_path
        dst = dist / file_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    
    # Create templates
    # (Implementation)
    
    print("✓ Core distribution created at:", dist)

if __name__ == "__main__":
    main()
```

---

## Best Practices

### 1. Design For Generalization

From the start, write code that's generalizable:
- Use environment variables for credentials
- Use configuration files, not hardcoded values
- Write documentation with example data, not real data
- Keep personal content in designated areas (Records/)

### 2. Separate Concerns

- **Core system:** `N5/`, `Knowledge/architectural/`
- **Personal knowledge:** `Knowledge/` (non-architectural)
- **Active work:** `Records/`
- **Documentation:** `Documents/`

### 3. Use Placeholders

In documentation and examples:
- Email: `user@example.com` not `vrijen@mycareerspan.com`
- Names: `John Doe`, `Jane Smith` not real names
- Companies: `Acme Corp`, `Example Inc` not real companies
- Paths: `/home/workspace/example.md` not actual paths

### 4. Gitignore Strategy

```
# .gitignore for n5-core distribution repo
N5/data/*.db
N5/config/credentials.json
Records/*
!Records/.gitkeep
Lists/*
!Lists/*.md
Knowledge/*
!Knowledge/architectural/
```

---

## Distribution Checklist

Before releasing:

### Code Quality
- [ ] All scripts follow template (logging, dry-run, error handling)
- [ ] All scripts tested on fresh install
- [ ] No personal data in code or comments
- [ ] No credentials committed

### Documentation
- [ ] README explains what N5 is and does
- [ ] User guide covers installation and daily use
- [ ] Developer guide covers architecture and extension
- [ ] This generalization guide included

### Legal & Licensing
- [ ] License file (MIT recommended)
- [ ] No proprietary code included
- [ ] No third-party code without proper attribution
- [ ] Privacy policy if collecting any data

### Testing
- [ ] Fresh install on new Zo instance works
- [ ] All default commands work
- [ ] No broken references to personal files
- [ ] No error messages with personal data

---

## Maintenance

After initial distribution:

### Syncing Updates

When you improve your personal N5:
1. Determine if improvement is core (generalizable) or personal
2. If core: Extract, sanitize, add to distribution
3. If personal: Keep in personal instance

### Versioning

Use semantic versioning:
- **Major** (1.0.0): Breaking changes to architecture
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes

### Community Contributions

When accepting contributions:
- Review for personal data leaks
- Ensure principle compliance
- Test on fresh install
- Update documentation

---

## Example: Generalizing a Script

**Original (Personal):**
```python
# N5/scripts/email_john.py
def send_email():
    to = "john@acmecorp.com"
    from_addr = "vrijen@mycareerspan.com"
    # ...
```

**Generalized (Core):**
```python
# N5/scripts/send_email.py
import os

def send_email(to: str, from_addr: str = None):
    from_addr = from_addr or os.getenv("N5_EMAIL_FROM")
    if not from_addr:
        raise ValueError("from_addr required or set N5_EMAIL_FROM")
    # ...
```

---

## FAQ

**Q: Should I distribute my specific workflows?**  
A: Only if they're generalizable. A "send follow-up email" workflow is core. A "send follow-up to John about Project X" is personal.

**Q: What about my custom commands?**  
A: Review each. Generic commands like `/search` are core. Specific ones like `/email-john` are personal.

**Q: How do I handle integrations?**  
A: Distribute integration scaffolding (API wrapper, config structure). Don't distribute your credentials.

**Q: Should I distribute my lessons learned?**  
A: Extract principle-level insights (e.g., "Don't pool information") and add to architectural principles. Don't distribute specific project post-mortems.

---

## Support

When users install your distribution:
- Provide clear README
- Include troubleshooting section in user guide
- Set up GitHub Discussions for questions
- Monitor Issues for bugs

---

**Next Steps:**
1. Run generalization checklist on your N5 instance
2. Create `n5-core-dist/` directory
3. Extract core components
4. Test fresh installation
5. Write distribution-specific documentation
6. Publish to GitHub

---

*Remember: The goal is to share your system intelligence while protecting your privacy.*
