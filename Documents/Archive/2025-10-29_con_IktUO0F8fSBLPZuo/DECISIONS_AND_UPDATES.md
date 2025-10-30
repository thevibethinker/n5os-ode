# Phase 0.5 Onboarding - Decisions & Updates

**Date**: 2025-10-28 05:15 ET  
**Status**: Incorporating V's feedback into spec

---

## ✅ V's Decisions

### 1. Trigger Mechanism
- **Auto-trigger** on first conversation upon install
- Part of installation instructions (manual run option)
- Command: `/onboard` or similar registered recipe

### 2. Re-Onboarding
- **Full reset allowed** via command flag (e.g., `/onboard --reset`)
- Users can completely reset and rerun onboarding

### 3. Integration Timing
- **External apps connected BEFORE onboarding**
- Gmail, Drive, Notion, etc. should be pre-connected
- Onboarding assumes integrations are available
- Onboarding can leverage these during personalization

### 4. Validation Strictness
- **Block completion if test failures**
- No warnings/proceed options - must pass to complete
- Hard requirement for setup validation

### 5. Skip Interview
- **Generic starter profile with note to customize**
- User can skip and configure manually later
- System still functional, just not personalized

---

## 🔧 Critical Architecture Updates

### Commands → Recipes Migration
**IMPORTANT**: `commands.jsonl` is **DEPRECATED** in Phase 5

**Old (Phase 0-4)**:
- `/N5/config/commands.jsonl`
- Command registry system

**New (Phase 5+)**:
- `/Recipes/recipes.jsonl`
- Recipe-based system
- More flexible, markdown-based

**Impact on Onboarding**:
- Generate custom recipes (not commands)
- Register in `Recipes/recipes.jsonl`
- Create `.md` recipe files in `Recipes/` directory
- Use recipe frontmatter (description, tags)

### N5 OS Current State

From `file 'phase5_transfer/N5.md'`:

```markdown
**DEPRECATED:** `N5/config/commands.jsonl` has been migrated to `Recipes/recipes.jsonl`
```

**Current Architecture**:
```
/home/workspace/
├── Recipes/               # NEW: Recipe system
│   ├── recipes.jsonl     # Recipe registry
│   └── *.md              # Individual recipes
├── N5/
│   ├── config/
│   │   ├── rules.md      # User rules (Phase 0)
│   │   └── prefs.md      # Preferences (Phase 4)
│   ├── scripts/          # System scripts
│   ├── schemas/          # Data schemas
│   └── data/             # System data (conversations.db)
├── Knowledge/            # SSOT reference material
├── Lists/                # Action items
├── Records/              # Staging area
└── Documents/            # Documentation
```

---

## 📋 Updated Onboarding Flow

### Pre-Onboarding (External)
**Before user starts N5 for first time**:
1. Clone N5 OS (Phases 0-4)
2. Connect external apps via Zo settings:
   - Gmail
   - Google Drive
   - Google Calendar
   - Notion
   - Any other integrations

### Onboarding Trigger
**First conversation OR manual `/onboard` command**:
- Auto-detect if onboarding complete (check for user_profile.json)
- If not complete, trigger onboarding flow
- If complete, normal conversation mode

### Onboarding Components Generated

**1. Custom Recipes** (not commands):
```
Recipes/
├── research_workflow.md
├── crm_update.md
├── daily_standup.md
└── weekly_review.md
```

**2. Recipe Registry Entry**:
```jsonl
{"slug": "research-workflow", "path": "Recipes/research_workflow.md", "description": "...", "tags": [...]}
```

**3. Personalized Configs**:
```
N5/config/
├── user_profile.json
├── work_style.json
└── use_cases.json
```

**4. Scheduled Tasks**:
- Daily standup (if requested)
- Weekly review (if requested)
- Custom automations

**5. Welcome Guide**:
```
Documents/N5_Welcome_Guide_{username}.md
```

---

## 🔍 Integration Points

### With Phase 0 (Rules)
- Onboarding respects existing rules
- Can suggest rule customizations based on interview
- Rules remain in `N5/config/rules.md`

### With Phase 1 (Infrastructure)
- Uses `session_state_manager.py` for tracking
- Conversation stored in `N5/data/conversations.db`
- Follows safety protocols (dry-run, validation)

### With Phase 2 (Recipes)
- Generates custom recipes
- Registers in `recipes.jsonl`
- Uses recipe schema and format

### With Phase 3 (Build System)
- May generate build-related recipes if user is technical
- Integration with deployment workflows

### With Phase 4 (Preferences & Knowledge)
- Populates `N5/config/prefs.md` with personalized settings
- May seed `Knowledge/` with user-specific reference material
- Architectural principles awareness

### With Phase 5 (Sessions & Reflection)
- First conversation tracked via session state
- Onboarding itself is a "session"
- Sets up reflection habits if user wants them

### With External Apps
- **Gmail**: Generate email-related recipes
- **Drive**: Setup file sync workflows
- **Calendar**: Create scheduling automations
- **Notion**: Database integration recipes

---

## 🧪 Validation Tests (23 total)

### Category 1: File Existence (6 tests)
1. `user_profile.json` exists
2. `work_style.json` exists
3. `use_cases.json` exists
4. At least 1 custom recipe exists
5. `recipes.jsonl` updated
6. Welcome guide exists

### Category 2: File Validity (5 tests)
7. `user_profile.json` valid JSON + required fields
8. `work_style.json` valid JSON + required fields
9. `use_cases.json` valid JSON + required fields
10. `recipes.jsonl` valid JSONL
11. Recipe files have valid frontmatter

### Category 3: Integration (6 tests)
12. Session state created correctly
13. Conversation recorded in DB
14. Recipes loadable by Zo
15. External app connections verified
16. Scheduled tasks created (if any)
17. Safety systems active

### Category 4: Functionality (6 tests)
18. User can invoke custom recipe
19. Recipe executes without errors
20. Welcome guide renders correctly
21. User preferences applied
22. Session state accessible
23. Re-onboarding works (reset flag)

---

## 📦 Updated Deliverables

### Scripts (5 modules)
1. `onboard_orchestrator.py` - Main entry point
2. `interview_conductor.py` - Conversational flow
3. `recipe_generator.py` - **UPDATED**: Generate recipes (not commands)
4. `personalize_config.py` - Config from templates
5. `validate_setup.py` - 23 tests

### Templates
1. `recipe_template.md.j2` - Recipe file template
2. `user_profile.schema.json` - Profile data schema
3. `work_style.schema.json` - Work preferences schema
4. `use_cases.schema.json` - Use case tracking
5. `welcome_guide_template.md.j2` - Personalized guide

### Documentation
1. This spec (updated)
2. Installation instructions (onboarding section)
3. User guide (onboarding experience)

---

## 🚀 Next Steps

1. **V reviews** this update document
2. **Confirm** architectural alignment (Recipes vs commands)
3. **Proceed to EXECUTE** phase:
   - Implement 5 Python scripts
   - Create templates
   - Build validation suite
   - Write integration tests
   - Manual QA

**Estimated time**: 12-15 hours total

---

**Ready for your approval to begin implementation!**

*Updated: 2025-10-28 05:15 ET*
