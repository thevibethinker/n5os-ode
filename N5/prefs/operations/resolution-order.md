# Resolution Order & Precedence

**Module:** Operations  
**Version:** 2.0.0  
**Date:** 2025-10-09

---

## Precedence Hierarchy

When preferences or rules conflict, resolve using this order (highest to lowest):

### 1. User's Direct Instruction (Highest)
Any explicit instruction in the current conversation overrides all stored preferences.

**Example:** If prefs say "use 24-hour time" but user says "use 12-hour format for this email," follow the user's instruction.

---

### 2. Folder POLICY.md
Folder-specific policy files override global preferences for operations within that folder.

**See:** `file 'N5/prefs/system/folder-policy.md'` for details

**Example:** `Lists/POLICY.md` specifies command-based interaction, overriding any global preference for direct file editing.

---

### 3. Critical Safety Rules
Safety rules from `file 'N5/prefs/system/safety.md'` cannot be overridden by lower-precedence preferences.

**Examples:**
- Never schedule without consent
- Always ask where to create files
- Require dry-run for destructive operations

---

### 4. Project-Level Prefs (If Exists)
Project-specific `_prefs.md` files within project folders override global preferences for that project.

**Pattern:** `/home/workspace/projects/[project-name]/_prefs.md`

---

### 5. Workflow Sub-Preferences
Specific workflow configurations within commands or modules.

**Example:** A specific command may define its own naming conventions or output formats.

---

### 6. Specialized Preference Modules
Modules in `N5/prefs/` hierarchy:
- `system/` — System governance
- `operations/` — Operational config
- `communication/` — Communication style
- `integration/` — Tool integrations
- `knowledge/` — Knowledge management

---

### 7. Global Preferences Index
`file 'N5/prefs/prefs.md'` — Base defaults

---

### 8. Knowledge Base (Informational)
Knowledge files **inform** but do not **override** preferences.

**Example:** `file 'Knowledge/stable/bio.md'` provides context about V but doesn't set operational rules.

**Exception:** Architectural principles files (`Knowledge/architectural/*.md`) have higher precedence as they define system behavior.

---

## Special Cases

### Architectural Principles
Files in `Knowledge/architectural/` are treated as operational rules, not just information:

**High-precedence architectural files:**
1. `file 'Knowledge/architectural/operational_principles.md'`

   - SSOT requirements
   - Anti-overwrite protocols

2. `file 'Knowledge/architectural/ingestion_standards.md'`
   - What to ingest
   - MECE principles
   - Knowledge structure

**Precedence:** Between Critical Safety Rules (#3) and Project-Level Prefs (#4)

---

### Schema Validation
Schemas validate structure but don't override preferences.

**Schemas enforce:**
- Data structure correctness
- Required fields
- Type validation

**Schemas do NOT enforce:**
- Preference choices
- Style decisions
- Operational policies

---

## Conflict Resolution Workflow

### Step 1: Identify Conflict
Two or more preferences give different instructions for the same decision.

### Step 2: Check Precedence
Use hierarchy above to determine which takes priority.

### Step 3: Apply Winner
Follow the higher-precedence rule.

### Step 4: Document (If Ambiguous)
If conflict resolution is not obvious:
1. Ask user for clarification
2. Document the decision
3. Consider updating preferences to prevent future conflicts

---

## Examples

### Example 1: File Creation Location

**Conflict:**
- Global prefs: "Ask where to create files"
- Project prefs: "Auto-create in `output/` folder"

**Resolution:**
- Project-level prefs (#4) > Global prefs (#6)
- Auto-create in project's `output/` folder
- But still subject to safety rule (#3) requiring confirmation for new files in protected areas

---

### Example 2: Communication Style

**Conflict:**
- Voice module: "Warmth: 0.80"
- User instruction: "Be more formal for this email"

**Resolution:**
- User's direct instruction (#1) > Voice module (#6)
- Use more formal tone for this specific email
- Future emails revert to voice module default

---

### Example 3: List Operations

**Conflict:**
- Global prefs: "Can edit .jsonl files directly"
- Lists POLICY.md: "Use commands only"

**Resolution:**
- Folder POLICY.md (#2) > Global prefs (#6)
- Use commands (lists-add, lists-set) only
- Direct edits prohibited

---

## Related Files

- **Folder Policy:** `file 'N5/prefs/system/folder-policy.md'`
- **Safety Rules:** `file 'N5/prefs/system/safety.md'`
- **Operational Principles:** `file 'Knowledge/architectural/operational_principles.md'`
- **Ingestion Standards:** `file 'Knowledge/architectural/ingestion_standards.md'`
- **Lists Policy:** `file 'Lists/POLICY.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Expanded into full hierarchy (8 levels)
- Added architectural principles as special case
- Added conflict resolution workflow
- Added concrete examples
- Cross-referenced related policy files
