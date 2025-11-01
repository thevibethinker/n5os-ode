# N5 Scripts: Executable Primitives

This directory contains Python scripts that perform atomic operations in N5 OS. Scripts are the **executable building blocks** invoked by function files.

---

## Architecture

### Script Types

1. **User-Facing Scripts** (73 scripts)
   - Import `n5_safety.py` for protection enforcement
   - Accept CLI arguments
   - Perform data operations (lists, knowledge, files)
   - Create backups and validate operations

2. **Infrastructure Scripts** (3 core)
   - `n5_safety.py` - Tiered file protection (SPOF, imported by all)
   - `incantum_engine.py` - Natural language → command dispatcher
   - `listclassifier.py` - Intelligent list assignment

3. **System Scripts**
   - `n5_docgen.py` - Generate command catalog
   - `n5_index_rebuild.py` - Rebuild system indexes
   - `n5_core_audit.py` - System health validation

4. **Maintenance Scripts**
   - `n5_cleanup_runtime.py` - Runtime log cleanup
   - `n5_cleanup_backups.py` - Backup retention management

---

## Critical Infrastructure

### n5_safety.py (SPOF - Single Point of Failure)

**Purpose**: Enforce tiered file protection across all write operations

**Protection Tiers**:
- **HARD**: Manual edit only (prefs.md, architectural docs)
- **MEDIUM**: Validate before edit (lists, knowledge, configs)
- **AUTO**: Regenerate freely (catalogs, indexes)

**Usage**:
```python
from n5_safety import SafetyValidator

validator = SafetyValidator()
validator.validate_write(filepath, operation="modify")
validator.create_backup(filepath)
```

**Imported By**: All 73 user-facing scripts

---

### incantum_engine.py

**Purpose**: Map natural language intent to registered commands

**Flow**:
```
Natural Language Input
    ↓
Intent Analysis (LLM)
    ↓
Trigger Phrase Match (incantum_triggers.json)
    ↓
Command Lookup (commands.jsonl)
    ↓
Execute Function File
```

**Example**:
```
Input: "Add Lynnette to must-contact"
→ Trigger: "add to list"
→ Command: lists-add
→ Args: --list must-contact --title "Lynnette"
```

---

### listclassifier.py

**Purpose**: Intelligently assign items to appropriate lists

**Classification Methods**:
1. **URL Pattern Matching**
   - LinkedIn → `crm.jsonl`
   - GitHub → `tech-resources.jsonl`
   - News articles → `reading-list.jsonl`

2. **Keyword Analysis**
   - "investor", "funding" → `fundraising-opportunity-tracker.jsonl`
   - "idea", "concept" → `ideas.jsonl`
   - "contact", "reach out" → `must-contact.jsonl`

3. **Context Analysis**
   - Meeting notes → `must-contact.jsonl`
   - Technical concepts → `areas-for-exploration.jsonl`

**Usage**:
```python
from listclassifier import ListClassifier

classifier = ListClassifier()
target_list = classifier.classify(
    title="Lynnette Scott - HR Director",
    body="Met at Civana, looking for AI talent",
    url=None
)
# Returns: "must-contact"
```

---

## Naming Conventions

All scripts follow the pattern: `n5_<subsystem>_<operation>.py`

**Examples**:
- `n5_lists_add.py` - Add item to list
- `n5_knowledge_ingest.py` - Ingest knowledge
- `n5_git_audit.py` - Audit git status
- `n5_docgen.py` - Generate documentation

**Exceptions**:
- `n5_safety.py` - Core infrastructure (no subsystem)
- `incantum_engine.py` - Core infrastructure (special name)
- `listclassifier.py` - Core infrastructure (special name)

---

## Script Structure

### Standard Template

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Usage:
    python3 n5_script_name.py [args]

Examples:
    python3 n5_script_name.py --option value
"""

import argparse
import sys
from pathlib import Path
from n5_safety import SafetyValidator

# Constants
ROOT = Path("/home/workspace")
SAFETY = SafetyValidator()

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--option', help='Option description')
    args = parser.parse_args()
    
    # Validate operation
    SAFETY.validate_write(target_file, operation="modify")
    
    # Create backup
    SAFETY.create_backup(target_file)
    
    # Perform operation
    try:
        # ... operation logic ...
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Usage

### Direct Invocation
```bash
python3 /home/workspace/N5/scripts/n5_lists_add.py \
  --list ideas \
  --title "Build AI coach" \
  --tags "ai,career,product"
```

### Via Command Dispatcher
```bash
python3 /home/workspace/N5/scripts/n5_command_dispatcher.py lists-add
```

### Via Function File
Function file references script:
```markdown
## Scripts
- n5_lists_add.py
```

---

## Development

### Creating a New Script

1. **Create file**:
   ```bash
   touch /home/workspace/N5/scripts/n5_my_script.py
   chmod +x /home/workspace/N5/scripts/n5_my_script.py
   ```

2. **Add boilerplate** (use template above)

3. **Import safety**:
   ```python
   from n5_safety import SafetyValidator
   SAFETY = SafetyValidator()
   ```

4. **Implement logic**:
   - Validate inputs
   - Check protection tiers
   - Create backups
   - Perform operation
   - Log results

5. **Test**:
   ```bash
   # Dry run
   python3 n5_my_script.py --dry-run
   
   # Real execution
   python3 n5_my_script.py
   ```

### Best Practices

- **Atomic operations**: Scripts should do one thing well
- **Composability**: Design for chaining with other scripts
- **Error handling**: Catch exceptions and provide clear messages
- **Idempotency**: Safe to run multiple times
- **Logging**: Output to stdout (info) and stderr (errors)
- **Safety first**: Always validate through `n5_safety.py`
- **Dry-run mode**: Support `--dry-run` for preview
- **Documentation**: Clear docstrings with usage examples

---

## Testing

### Unit Testing
```bash
# Run test suite
python3 /home/workspace/N5/test/test_scripts.py
```

### Integration Testing
```bash
# End-to-end test
python3 /home/workspace/N5/test/test_e2e.py
```

### Manual Testing
```bash
# Test individual script with dry-run
python3 n5_lists_add.py --list test --title "Test Item" --dry-run
```

---

## Script Inventory

### Lists Scripts (8)
- `n5_lists_add.py` - Add item to list
- `n5_lists_find.py` - Search lists
- `n5_lists_export.py` - Export to formats
- `n5_lists_health_check.py` - Validate integrity
- `n5_lists_similarity_scanner.py` - Find duplicates
- `n5_lists_update.py` - Modify existing items
- `n5_lists_delete.py` - Remove items
- `n5_lists_merge.py` - Merge duplicate items

### Knowledge Scripts (6)
- `n5_knowledge_add.py` - Add fact to knowledge
- `n5_knowledge_ingest.py` - Process documents
- `n5_knowledge_sync.py` - Sync analysis results
- `n5_knowledge_query.py` - Query knowledge graph
- `n5_knowledge_export.py` - Export knowledge
- `n5_knowledge_validate.py` - Check consistency

### System Scripts (10)
- `n5_docgen.py` - Generate command catalog
- `n5_index_rebuild.py` - Rebuild indexes
- `n5_core_audit.py` - System health check
- `n5_cleanup_runtime.py` - Clean runtime logs
- `n5_cleanup_backups.py` - Manage backups
- `n5_review_workspace.py` - Analyze workspace
- `n5_organize_files.py` - File organization
- `n5_conversation_end.py` - Conversation cleanup
- `n5_git_audit.py` - Git status check
- `n5_git_check.py` - Pre-commit validation

### Job Scripts (3)
- `n5_jobs_find.py` - Search job postings
- `n5_jobs_add.py` - Add job posting
- `n5_jobs_analyze.py` - Analyze job trends

### Infrastructure Scripts (3)
- `n5_safety.py` - File protection
- `incantum_engine.py` - NL dispatcher
- `listclassifier.py` - List classification

**Total**: ~73 scripts

---

## Common Operations

### Add to List
```bash
python3 n5_lists_add.py --list ideas --title "New idea" --body "Details"
```

### Find in Lists
```bash
python3 n5_lists_find.py --query "investor" --status open
```

### Health Check
```bash
python3 n5_lists_health_check.py --verbose
```

### Generate Docs
```bash
python3 n5_docgen.py
```

### System Audit
```bash
python3 n5_core_audit.py --report
```

---

## Troubleshooting

**Issue**: Import error for `n5_safety`  
**Solution**: Ensure `n5_safety.py` exists and `PYTHONPATH` includes scripts dir

**Issue**: Permission denied  
**Solution**: Check protection tier via `n5_safety.py` validation

**Issue**: Script not executable  
**Solution**: `chmod +x /home/workspace/N5/scripts/<script>.py`

**Issue**: Schema validation failure  
**Solution**: Check schema version and required fields

---

## Related

- **Function Files**: `/home/workspace/N5/commands/`
- **Command Registry**: `/home/workspace/N5/data/executables.db`
- **Schemas**: `/home/workspace/N5/schemas/`
- **Tests**: `/home/workspace/N5/test/`

---

*Part of N5 OS Scripts Layer*  
*All scripts import n5_safety.py for protection enforcement*
