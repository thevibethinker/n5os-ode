# N5 OS Core - Content Generalization Guide

## Objective

Separate user-specific content (Vrijen's personal files) from core system content (distributable N5 components) to enable clean v0.1 distribution.

## Classification Framework

### Core Content (Include in Distribution)
**Definition**: Files that define N5 system behavior, provide templates, or document features.

**Categories**:
1. **System Scripts** - All Python scripts in `N5/scripts/`
2. **Schemas** - All JSON schemas in `N5/schemas/`
3. **Templates** - All template files in `N5/templates/`
4. **Documentation** - All docs in `N5/docs/`
5. **Default Preferences** - Generalized preference modules
6. **Example Content** - Minimal examples for demonstration

**Examples**:
```
✓ N5/scripts/session_state_manager.py
✓ N5/schemas/commands.schema.json
✓ N5/templates/config/commands.template.jsonl
✓ N5/docs/user_guide.md
✓ N5/prefs/operations/scheduled-task-protocol.md (generalized)
✓ N5/Recipes/example_audit.md
```

### User Content (Exclude from Distribution)
**Definition**: Files specific to your instance, personal data, or work-in-progress.

**Categories**:
1. **Active Configs** - Generated runtime configs in `N5/config/`
2. **Personal Lists** - Your todos, reading lists
3. **Personal Records** - Your session logs, decisions
4. **Active Bulletins** - Instance-specific announcements
5. **Personal Knowledge** - Your notes, research
6. **Client Work** - Careerspan materials
7. **Protected Paths** - Your specific .n5protected markers

**Examples**:
```
✗ N5/config/commands.jsonl (generated from template)
✗ N5/Lists/todos.md (your personal todos)
✗ N5/Records/sessions.jsonl (your session history)
✗ N5/bulletins/active/ (your instance bulletins)
✗ Knowledge/architectural/careerspan_notes.md
✗ Documents/N5.md (your customized quick reference)
```

## Generalization Strategy

### Step 1: Identify User-Specific References

Search for:
- Your name: "Vrijen", "Attawar"
- Company: "Careerspan"
- Email: "vademonstrator@zo.computer"
- Personal URLs/paths
- Specific project names
- Instance-specific configuration values

### Step 2: Create Generalized Versions

**Example**: Preference file with personal references

**Current** (`N5/prefs/operations/git_workflow.md`):
```markdown
# Git Workflow Preferences

When committing to Careerspan repositories:
- Use conventional commits
- Reference issues: CSPAN-123
- Sign commits with: Vrijen Attawar <va@careerspan.com>
```

**Generalized** (`N5/templates/prefs/operations/git_workflow.md`):
```markdown
# Git Workflow Preferences

When committing to repositories:
- Use conventional commits
- Reference issues using your project's convention
- Configure git identity with your details:
  ```bash
  git config user.name "Your Name"
  git config user.email "your@email.com"
  ```
```

### Step 3: Use Placeholders

For content that needs customization:

```markdown
# N5 Configuration

**Instance**: {{INSTANCE_NAME}}.zo.computer
**Owner**: {{USER_NAME}}
**Email**: {{USER_EMAIL}}

## Preferences

{{CUSTOM_PREFERENCES}}
```

Installation script replaces placeholders:
```python
def customize_config(template_path, user_data):
    content = template_path.read_text()
    content = content.replace("{{INSTANCE_NAME}}", user_data['instance'])
    content = content.replace("{{USER_NAME}}", user_data['name'])
    # ...
    return content
```

### Step 4: Provide Examples

Instead of distributing your actual data, include minimal examples:

**Your todos.md**:
```markdown
- [ ] Review Careerspan Q4 metrics
- [ ] Update client portal
- [ ] Prepare presentation for TechConf 2025
```

**Example todos.md** (distributed):
```markdown
# Todos

Example action items:

- [ ] Review project status
- [ ] Update documentation
- [ ] Prepare weekly report

## Usage

Add your own tasks here. Delete examples when ready.
```

## Specific File Decisions

### Bulletins

**Distribute**:
- `N5/bulletins/README.md` (documentation)
- `N5/scripts/bulletins.py` (script)
- `N5/schemas/bulletins.schema.json` (schema)

**Don't Distribute**:
- `N5/bulletins/*.json` (your active bulletins)

**Include in Distribution**:
- One example bulletin: `N5/bulletins/examples/welcome.json`

### Lists

**Distribute**:
- `N5/Lists/README.md`
- Empty templates:
  - `N5/templates/Lists/todos.template.md`
  - `N5/templates/Lists/reading_list.template.md`

**Don't Distribute**:
- Your populated lists

### Records

**Distribute**:
- `N5/Records/README.md`
- Schema: `N5/schemas/record_entry.schema.json`

**Don't Distribute**:
- Your records JSONL files

**Include**:
- Example record file with 1-2 sample entries

### Preferences

**Strategy**: Generalize all preference modules

**Process**:
1. Copy `N5/prefs/` to `N5/templates/prefs/`
2. Remove personal references
3. Add {{PLACEHOLDERS}} where customization needed
4. Add usage instructions
5. Keep your personal versions in `N5/prefs/` (gitignored)

**Example Files to Generalize**:
```
N5/prefs/prefs.md
N5/prefs/operations/scheduled-task-protocol.md
N5/prefs/operations/*.md
N5/prefs/workflows/*.md
```

### Knowledge Directory

**Your Structure**:
```
Knowledge/
├── architectural/
│   ├── planning_prompt.md        # ✓ Generalized and distribute
│   ├── careerspan_arch.md        # ✗ Your work
│   └── n5_decisions.md           # ✗ Your decisions
├── research/
│   └── ai_developments.md        # ✗ Your research
└── clients/                      # ✗ All client work
```

**Distribution**:
```
N5/templates/Knowledge/
└── architectural/
    └── planning_prompt.md        # Only this file
```

### Scripts Directory

**Distribute**: All scripts in `N5/scripts/`

**But**: Remove any hard-coded paths specific to your instance

**Example Generalization**:

**Current**:
```python
WORKSPACE = Path("/home/workspace")
N5_ROOT = Path("/home/workspace/N5")
CAREERSPAN_ROOT = Path("/home/workspace/Careerspan")  # Remove this
```

**Generalized**:
```python
WORKSPACE = Path("/home/workspace")
N5_ROOT = WORKSPACE / "N5"
# Scripts should discover other directories dynamically
```

## Distribution Checklist

Before packaging v0.1:

- [ ] Create `N5/templates/` with generalized versions of all preference files
- [ ] Remove personal references from all scripts (names, emails, companies)
- [ ] Replace hard-coded paths with dynamic discovery
- [ ] Create minimal example files for Lists, Records, Recipes
- [ ] Write README files for all major directories
- [ ] Create installation script that:
  - [ ] Generates configs from templates
  - [ ] Prompts for user information (name, email, preferences)
  - [ ] Creates directory structure
  - [ ] Validates installation
- [ ] Document customization points in user guide
- [ ] Create `.gitignore` for generated/user content:
  ```
  N5/config/
  N5/Lists/
  N5/Records/
  N5/bulletins/*.json
  Documents/N5.md
  ```

## Validation

After generalization, test distribution:

1. **Fresh Install Test**:
   ```bash
   # On clean Zo instance
   python3 n5_install.py
   # Should complete without errors
   # Should not reference "Vrijen", "Careerspan", etc.
   ```

2. **Customization Test**:
   ```bash
   # Verify user can customize
   # Edit generated configs
   # Changes should persist
   # System should work with custom values
   ```

3. **Documentation Test**:
   ```bash
   # Verify all docs accurate
   # No broken file references
   # Examples work as described
   ```

## Maintenance

**Going Forward**:

1. **Two Versions**:
   - `N5/templates/` - Generalized (tracked in git)
   - `N5/prefs/`, `N5/config/` - Your personal (gitignored)

2. **Update Process**:
   - Make changes to templates
   - Sync to your personal configs
   - Test both versions

3. **New Features**:
   - Add to templates first
   - Use placeholders for customization
   - Document in user guide
   - Update installation script

## Summary

**Core Principle**: Distribute the **system**, not your **data**.

**Include**:
- Scripts, schemas, templates
- Documentation, examples
- Generalized preferences

**Exclude**:
- Active configs, personal lists/records
- Your knowledge base, client work
- Instance-specific customizations

**Result**: Users get a functional N5 system they can customize to their needs, not a clone of your personal setup.
