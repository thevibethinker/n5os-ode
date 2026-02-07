# Worker 6: CLI Interface & Query Tools

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Task ID:** W6-CLI-INTERFACE  
**Estimated Time:** 30 minutes  
**Dependencies:** Worker 1 ✅, Worker 2 ✅, Worker 3 ✅, Worker 4 ✅, Worker 4B ✅  
**Can Run Parallel With:** Worker 5 (Email Tracker)

---

## Mission

Build command-line interface for CRM V3 that enables:
1. **Manual profile creation** - Add contacts not yet in system
2. **Intelligent search** - Find profiles by name/email/company
3. **Intelligence queries** - AI-powered synthesis across sources

**Goal:** Give V direct control over CRM data with simple, powerful commands.

---

## Context

**Use Cases:**
- V meets someone at event → Manually add to CRM immediately
- V needs prep for call → Search profile, get intelligence synthesis
- V wants to know "Who do I know at Company X?" → Query relationships

**Architecture Pattern:**
- CLI script calls database directly (fast, no AI needed)
- Intelligence synthesis uses AI (Zo internal API or prompt invocation)

---

## Deliverables

### 1. CRM CLI Script (Main Interface)

**File:** `N5/scripts/crm_cli.py`

**Commands:**
```bash
# Create profile manually
crm create --email john@example.com --name "John Doe" [--category INVESTOR] [--notes "Met at TechCrunch"]

# Search profiles
crm search --email john@example.com
crm search --name "John Doe"
crm search --company "Acme Corp"

# List profiles
crm list [--category INVESTOR] [--limit 20]

# Get intelligence synthesis (AI-powered)
crm intel --email john@example.com
crm intel --id 42

# Queue enrichment manually
crm enrich --email john@example.com [--priority 100]

# Show statistics
crm stats
```

---

## Implementation

### Command 1: `crm create` (Manual Profile Creation)

**Function:**
```python
def create_profile(email: str, name: str, category: str = 'NETWORKING', notes: str = None) -> int:
    """
    Manually create profile.
    
    Args:
        email: Contact email
        name: Full name
        category: NETWORKING | INVESTOR | ADVISOR | COMMUNITY
        notes: Optional notes
        
    Returns:
        profile_id
        
    Behavior:
        1. Check if profile exists (error if duplicate)
        2. Use get_or_create_profile() from helpers
        3. If notes provided, append to YAML
        4. Schedule immediate enrichment (priority 100)
        5. Print success message with profile_id and yaml_path
    """
```

**Output:**
```
✓ Profile created: john_doe_john (ID: 51)
  Email: john@example.com
  Path: N5/crm_v3/profiles/John_Doe_john.yaml
  Enrichment: Queued (priority 100, immediate)
```

---

### Command 2: `crm search` (Profile Search)

**Function:**
```python
def search_profiles(email: str = None, name: str = None, company: str = None) -> List[Dict]:
    """
    Search profiles by email, name, or company.
    
    Args:
        email: Exact email match
        name: Fuzzy name search (LIKE %name%)
        company: Company domain search
        
    Returns:
        List of matching profiles with summary data
        
    SQL:
        SELECT id, email, name, category, last_contact_at, meeting_count, profile_quality
        FROM profiles
        WHERE email = ? OR name LIKE ? OR email LIKE ?
        ORDER BY last_contact_at DESC NULLS LAST
    """
```

**Output:**
```
Found 2 profiles:

[1] John Doe (john@example.com)
    Category: NETWORKING | Quality: enriched | Last Contact: 2025-11-15
    Meetings: 3 | Path: N5/crm_v3/profiles/John_Doe_john.yaml

[2] Jane Doe (jane@example.com)
    Category: INVESTOR | Quality: stub | Last Contact: Never
    Meetings: 0 | Path: N5/crm_v3/profiles/Jane_Doe_jane.yaml
```

---

### Command 3: `crm intel` (Intelligence Synthesis)

**Function:**
```python
def get_intelligence_synthesis(email: str = None, profile_id: int = None) -> str:
    """
    AI-powered intelligence synthesis across all sources.
    
    Args:
        email: Profile email
        profile_id: Profile database ID
        
    Behavior:
        1. Fetch profile from database
        2. Read YAML profile file
        3. Query intelligence_sources table for all sources
        4. Use Zo AI to synthesize:
           - Key facts about person
           - Relationship context
           - Recent interactions
           - Strategic intelligence
           - Warm intro paths (if applicable)
        5. Return formatted synthesis
        
    Implementation:
        - Use Zo's internal API or create prompt file
        - Load file 'N5/workflows/crm_intel_synthesis.prompt.md' (to be created)
    """
```

**Output:**
```
Intelligence Synthesis: John Doe (john@example.com)

Overview:
- Senior Product Manager at Tech Corp
- Based in San Francisco, CA
- Met at TechCrunch Disrupt 2025-10-15

Relationship:
- Category: NETWORKING
- Strength: Moderate (3 meetings, 2 email threads)
- Last Contact: 2025-11-15 (3 days ago)

Recent Context:
- Meeting 2025-11-15: Discussed B2B partnerships
- Email thread: Follow-up on integration proposal
- LinkedIn: Promoted to Senior PM (2025-10-01)

Strategic Intelligence:
- Interested in API partnerships
- Decision maker for product integrations
- Warm intro possible via Sarah Chen (mutual connection)

Sources: 3 meetings (B08 blocks), Aviato enrichment, 2 Gmail threads, LinkedIn
```

---

### Command 4: `crm enrich` (Manual Enrichment Queue)

**Function:**
```python
def queue_enrichment(email: str, priority: int = 100):
    """
    Manually queue enrichment for profile.
    
    Uses schedule_enrichment_job() from helpers.
    Scheduled for immediate processing (now).
    """
```

---

### Command 5: `crm list` (List Profiles)

**Function:**
```python
def list_profiles(category: str = None, limit: int = 20):
    """
    List profiles with filters.
    
    SQL:
        SELECT id, name, email, category, profile_quality, last_contact_at
        FROM profiles
        WHERE category = ? OR ? IS NULL
        ORDER BY last_contact_at DESC NULLS LAST
        LIMIT ?
    """
```

---

### Command 6: `crm stats` (Statistics)

**Function:**
```python
def show_stats():
    """
    Display CRM statistics.
    
    Queries:
    - Total profiles
    - Profiles by category
    - Profiles by quality (stub, partial, enriched)
    - Enrichment queue status
    - Recent activity (profiles added last 7 days)
    """
```

**Output:**
```
CRM V3 Statistics

Profiles: 50 total
  ├─ NETWORKING: 43
  ├─ COMMUNITY: 4
  └─ ADVISOR: 3

Quality:
  ├─ stub: 45 (90%)
  ├─ partial: 3 (6%)
  └─ enriched: 2 (4%)

Enrichment Queue: 12 pending jobs
  ├─ Priority 100 (morning-of): 2
  ├─ Priority 75 (3-day): 8
  └─ Priority 25 (gmail): 2

Recent Activity:
  └─ 5 profiles added in last 7 days
```

---

## Implementation Steps

### Step 1: Create CLI Script (20 min)

**File:** `N5/scripts/crm_cli.py`

Use argparse or Click for command parsing:

```python
#!/usr/bin/env python3
"""
CRM V3 Command Line Interface
"""

import argparse
import sqlite3
from crm_calendar_helpers import get_or_create_profile, schedule_enrichment_job

DB_PATH = '/home/workspace/N5/data/crm_v3.db'

def main():
    parser = argparse.ArgumentParser(description='CRM V3 CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # crm create
    create_parser = subparsers.add_parser('create', help='Create profile')
    create_parser.add_argument('--email', required=True)
    create_parser.add_argument('--name', required=True)
    create_parser.add_argument('--category', default='NETWORKING')
    create_parser.add_argument('--notes')
    
    # crm search
    search_parser = subparsers.add_parser('search', help='Search profiles')
    search_parser.add_argument('--email')
    search_parser.add_argument('--name')
    search_parser.add_argument('--company')
    
    # crm intel
    intel_parser = subparsers.add_parser('intel', help='Get intelligence')
    intel_parser.add_argument('--email')
    intel_parser.add_argument('--id', type=int)
    
    # ... other commands
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_profile(args.email, args.name, args.category, args.notes)
    elif args.command == 'search':
        search_profiles(args.email, args.name, args.company)
    # ... handle other commands

if __name__ == '__main__':
    main()
```

### Step 2: Create Intelligence Synthesis Prompt (5 min)

**File:** `N5/workflows/crm_intel_synthesis.prompt.md`

```markdown
---
title: CRM Intelligence Synthesis
description: Synthesize multi-source intelligence for profile
tags: [crm, intelligence, synthesis]
tool: false
---

# Mission

Synthesize intelligence across all sources for profile: {{profile_name}} ({{profile_email}})

# Context

**Profile YAML:**
```
{{profile_yaml_content}}
```

**Intelligence Sources ({{source_count}} total):**
{{intelligence_sources}}

# Task

Create concise intelligence synthesis covering:
1. Overview (who they are, role, location)
2. Relationship context (category, strength, last contact)
3. Recent interactions (meetings, emails, updates)
4. Strategic intelligence (interests, decision authority, warm intro paths)

Format as markdown. Be specific and actionable.
```

### Step 3: Make CLI Executable (2 min)

```bash
chmod +x /home/workspace/N5/scripts/crm_cli.py

# Create symlink for easy access
ln -sf /home/workspace/N5/scripts/crm_cli.py /usr/local/bin/crm
```

### Step 4: Testing (3 min)

```bash
# Test create
crm create --email test@example.com --name "Test User" --notes "Test profile"

# Test search
crm search --email test@example.com
crm search --name "Test"

# Test stats
crm stats

# Test intel (on existing profile)
crm intel --email epak171@gmail.com

# Test list
crm list --limit 5
```

---

## Success Criteria

1. ✅ CLI script created and executable
2. ✅ All 6 commands working (create, search, intel, enrich, list, stats)
3. ✅ Intelligence synthesis prompt created
4. ✅ Symlink created (`crm` command available globally)
5. ✅ Test profile created and queried successfully

---

## Validation Commands

```bash
# Test CLI exists
which crm

# Test commands
crm --help
crm create --help
crm search --help

# Create test profile
crm create --email worker6test@example.com --name "Worker Six Test"

# Search for it
crm search --email worker6test@example.com

# Check database
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT * FROM profiles WHERE email='worker6test@example.com';"

# View stats
crm stats
```

---

## Deliverables

**Report back to Orchestrator:**

1. CLI script created and tested
2. Command test results (6/6 working)
3. Intelligence synthesis validation
4. Sample output from each command
5. Any issues or blockers

**Ready for Worker 7:** After Workers 5 & 6 both complete, Worker 7 (integration testing) can begin.

---

## Notes

**Intelligence Synthesis Implementation:**
- Option A: Use Zo CLI (`zo "synthesize intelligence for..."`)
- Option B: Create prompt file and invoke via internal API
- Option C: Inline prompt in Python with subprocess call

**Command Aliases:**
```bash
# Could add bash aliases for common operations
alias crm-add='crm create'
alias crm-find='crm search'
alias crm-info='crm intel'
```

**Architecture Context:**
- `file 'N5/builds/crm-v3-unified/crm-v3-design.md'` - Full CRM V3 architecture
- `file 'N5/scripts/crm_calendar_helpers.py'` - Shared helper functions
- `file 'N5/data/crm_v3.db'` - Database

---

**Orchestrator Contact:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-18 04:25 ET  
**Status:** Ready to Execute  
**Parallel Worker:** W5 (Email Tracker)

