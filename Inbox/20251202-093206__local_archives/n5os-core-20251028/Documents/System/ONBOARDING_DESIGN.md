# N5 OS Interactive Onboarding — Design Spec

**Goal**: Personalized, privacy-first setup in 10-15 minutes

---

## Architecture Overview

### Config Separation Strategy

```
n5os-core/                    # Git repo (upstream)
├── core/                     # Base system (tracked)
├── defaults/                 # Default configs (tracked)
└── .gitignore               # Excludes user_config/

After first run:
/home/workspace/
├── N5/                       # Installed system
│   ├── config/              # Base configs
│   └── user_config/         # Personal (NEVER tracked) ✅
│       ├── bio.md
│       ├── preferences.json
│       ├── workflows_enabled.json
│       └── telemetry_settings.json
├── Lists/                    # User's lists
└── .n5_install_metadata.json # Track version, personalization
```

**Key Principle**: User configs in `user_config/` are `.gitignored` and never leave their machine.

---

## Interactive Onboarding Flow

### Script: `onboard.py`

**Runs automatically on first bootstrap, or manually via `python3 N5/scripts/onboard.py`**

---

### Phase 1: Welcome & Context (2 min)

**Questions**:
1. **"What's your name?"**
   - Stores in `user_config/bio.md`
   - Used for personalization

2. **"What's your timezone?"** (auto-detect, confirm)
   - Stores in `user_config/preferences.json`
   - Used for scheduling

3. **"What's your primary work focus?"**
   - Options: Entrepreneurship, Consulting, Research, Creative Work, Other
   - Stores in `user_config/preferences.json`
   - Affects workflow recommendations

4. **"Tell me about your current workflow challenges in 1-2 sentences"**
   - Stores in `user_config/bio.md`
   - Used to customize recommendations

---

### Phase 2: Workflow Preferences (3 min)

**Questions**:
5. **"Which systems do you want to enable?"**
   - [x] Lists (ideas, contacts) — Default ON
   - [ ] Meeting workflows — Ask
   - [ ] Daily digests — Ask
   - [ ] Social media management — Ask
   
   Stores in `user_config/workflows_enabled.json`

6. **"How do you prefer to work with AI?"**
   - Options: 
     - "Collaborative" (AI asks questions)
     - "Autonomous" (AI decides)
     - "Supervised" (AI proposes, I approve)
   - Default: Collaborative
   - Stores in `user_config/preferences.json`

7. **"What's your preferred level of automation?"**
   - Options: Manual, Semi-Auto (2-3 tasks), Full-Auto (5-7 tasks)
   - Stores in `user_config/preferences.json`
   - Configures scheduled tasks

---

### Phase 3: Personalization (3 min)

**Questions**:
8. **"What are your top 3 goals for the next 30 days?"**
   - Creates initial `Lists/goals.jsonl`
   - Shown in daily digest (if enabled)

9. **"Any specific preferences for how AI should communicate with you?"**
   - Examples: "Be concise", "Explain reasoning", "Challenge my thinking"
   - Stores in `user_config/ai_communication_prefs.md`
   - Used in persona prompts

10. **"What integrations do you use?"** (optional)
    - Gmail, Google Calendar, Notion, Slack, etc.
    - Stores in `user_config/integrations.json`
    - Shows setup links

---

### Phase 4: Privacy & Telemetry (2 min)

**Questions**:
11. **"Enable anonymous usage telemetry?"** (Opt-in, default NO)
    ```
    What we track (if you opt in):
    - Commands run (names only, not args/data)
    - Script execution counts
    - Workflow patterns (e.g., "user runs meeting-process 3x/week")
    - Errors encountered (no personal data)
    
    What we DON'T track:
    - Your data (lists, notes, files)
    - Your conversations
    - Names, emails, or identifiers
    - Anything in user_config/
    
    Data stored: Locally only (no phone-home by default)
    Export: Available on request for debugging
    ```
    
    Stores in `user_config/telemetry_settings.json`

12. **"Enable crash reporting?"** (Opt-in, helps improve system)
    - If yes, errors logged to `N5/logs/errors.jsonl`
    - Never includes personal data
    - Can review before sharing

---

### Phase 5: Finalization (2 min)

**Actions**:
13. Generate personalized files:
    - `user_config/bio.md` — Your context
    - `user_config/preferences.json` — All settings
    - `user_config/workflows_enabled.json` — Active systems
    - `.n5_install_metadata.json` — Installation metadata

14. Set up initial lists:
    - `Lists/ideas.jsonl` — Empty, ready
    - `Lists/goals.jsonl` — Your 3 goals
    - `Lists/must-contact.jsonl` — Empty

15. Configure scheduled tasks (if enabled):
    - Based on automation preference level
    - Creates Zo scheduled tasks via API

16. Show personalized quickstart:
    ```
    ✅ N5 OS configured for [Name]!
    
    Your setup:
    - Work focus: [focus]
    - Automation: [level]
    - Active workflows: [X, Y, Z]
    
    Next steps:
    1. Try: "Load Vibe Builder persona"
    2. Add your first idea: echo '{"title": "Test", "date": "2025-10-26"}' >> Lists/ideas.jsonl
    3. Run: python3 N5/scripts/n5_index_rebuild.py
    4. Read: Documents/zero_touch_manifesto.md
    
    Your config: N5/user_config/ (private, never shared)
    System version: v1.0-core
    Update check: python3 N5/scripts/n5_update.py
    ```

---

## Personalization Applied

### File Customizations

**`user_config/bio.md`**:
```markdown
# About [Name]

**Work Focus**: [focus]
**Timezone**: [timezone]

## Current Challenges
[challenges from Q4]

## Top Goals (Next 30 Days)
1. [goal 1]
2. [goal 2]
3. [goal 3]

## AI Communication Preferences
[prefs from Q9]

---

*Generated*: 2025-10-26  
*N5 Version*: 1.0-core
```

**`user_config/preferences.json`**:
```json
{
  "version": "1.0",
  "user": {
    "name": "...",
    "timezone": "America/New_York",
    "work_focus": "entrepreneurship"
  },
  "ai": {
    "mode": "collaborative",
    "communication_style": "...",
    "explanation_level": "detailed"
  },
  "automation": {
    "level": "semi-auto",
    "scheduled_tasks_enabled": true,
    "tasks": ["index-rebuild", "git-check", "empty-files"]
  },
  "workflows": {
    "lists": true,
    "meetings": false,
    "digests": true,
    "social": false
  }
}
```

**`user_config/telemetry_settings.json`**:
```json
{
  "enabled": false,
  "anonymous_id": "uuid-generated",
  "events_tracked": ["command_run", "script_execute", "error"],
  "storage": "local_only",
  "last_upload": null,
  "opt_in_date": null
}
```

---

## Update Mechanism Design

### Script: `n5_update.py`

**Purpose**: Pull upstream changes without losing personalization

**Flow**:

1. **Check for updates**:
   ```bash
   python3 N5/scripts/n5_update.py --check
   ```
   - Fetches origin/main
   - Compares with local version
   - Shows changelog

2. **Preview changes**:
   ```bash
   python3 N5/scripts/n5_update.py --preview
   ```
   - Lists files that will change
   - Highlights any conflicts
   - Shows `user_config/` is protected

3. **Apply update**:
   ```bash
   python3 N5/scripts/n5_update.py --apply
   ```
   - Creates snapshot: `.n5_snapshots/pre-update-YYYY-MM-DD/`
   - Pulls upstream changes
   - **Preserves**: `user_config/`, `Lists/`, `Records/`
   - **Updates**: `core/`, `scripts/`, `docs/`
   - **Merges**: `N5/config/` (keeps user overrides)
   - Shows summary

4. **Rollback**:
   ```bash
   python3 N5/scripts/n5_update.py --rollback
   ```
   - Lists available snapshots
   - Restores selected snapshot
   - User data untouched

**Safety**:
- Always creates snapshot before update
- User configs NEVER overwritten
- Dry-run mode available
- Clear changelog before applying

---

## Telemetry Design (Privacy-First)

### What Gets Tracked (If Opted In)

**Local storage only by default** (`N5/logs/telemetry.jsonl`):

```jsonl
{"event": "command_run", "command": "index-rebuild", "timestamp": "2025-10-26T10:00:00Z", "duration_ms": 1234}
{"event": "script_execute", "script": "n5_git_check.py", "success": true, "timestamp": "2025-10-26T11:00:00Z"}
{"event": "workflow_pattern", "pattern": "morning_routine", "count": 3, "timestamp": "2025-10-26"}
{"event": "error", "script": "meeting_process.py", "error_type": "FileNotFoundError", "timestamp": "2025-10-26T12:00:00Z"}
```

**Never tracked**:
- Personal data (names, emails, content)
- File contents
- Conversation transcripts
- Anything in `user_config/`

**Export** (for debugging):
```bash
python3 N5/scripts/n5_telemetry.py --export telemetry_export.json
```

**Opt-out anytime**:
```bash
python3 N5/scripts/n5_telemetry.py --disable
```

---

## Implementation Priority

### Phase 1 (Core v1.1)
- [ ] Create `onboard.py` script
- [ ] Implement config separation (`user_config/`)
- [ ] Update `.gitignore` to protect user configs
- [ ] Add to bootstrap.sh

### Phase 2 (Core v1.2)
- [ ] Build `n5_update.py` (safe updates)
- [ ] Snapshot/rollback system
- [ ] Changelog viewer

### Phase 3 (Core v1.3)
- [ ] Telemetry (opt-in, local-only)
- [ ] Usage analytics dashboard
- [ ] Export functionality

---

## User Experience Summary

**First time**:
```bash
bash bootstrap.sh
# → Installs system
# → Runs onboard.py automatically
# → 10-15 min interactive setup
# → Personalized, ready to use
```

**Updates**:
```bash
python3 N5/scripts/n5_update.py --check
# → "v1.1 available: 3 new scripts, 2 bug fixes"
python3 N5/scripts/n5_update.py --apply
# → Snapshot created
# → Update applied
# → Your configs untouched ✅
```

**Privacy**:
- User configs never leave their machine
- Telemetry opt-in, local-only by default
- Full control over data

---

**Version**: 1.0 (Design)  
**Status**: Ready for implementation  
**Estimated**: 2-3 days development
