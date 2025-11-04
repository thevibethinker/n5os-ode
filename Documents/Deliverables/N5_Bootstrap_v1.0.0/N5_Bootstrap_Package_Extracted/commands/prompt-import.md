---
date: '2025-10-08T23:17:56Z'
last-tested: '2025-10-08T23:17:56Z'
generated_date: '2025-10-08T23:17:56Z'
checksum: prompt_import_v1_0_0
tags: ['prompts', 'ai']
category: productivity
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/prompt-import.md
---
# `prompt-import`

**Version**: 1.0.0  
**Summary**: Import personal prompts into N5 OS with standardized conversion

---

## Description

Standardized pipeline for converting personal Function/Companion files into N5 commands with full integration (command files, registry, incantum triggers).

---

## Filename Format

**Required pattern**:
```
Function [NN] - Title v0.0.ext
Companion [NN] - Title v0.0.ext
```

**Examples**:
- `Function [01] - Deep Research Due Diligence v0.3.txt`
- `Companion [05] - Master Voice Vrijen v1.3.txt`

**Components**:
- `[NN]`: Two-digit number (priority/category)
- `Title`: Descriptive title (converted to command name)
- `v0.0`: Version number
- `.ext`: Any extension (txt, pdf, md, etc.)

---

## Conversion Process

### Automatic Steps

1. **Extract Metadata**
   - Parse filename for number, title, version
   - Generate command name: Title → lowercase-hyphenated

2. **Create Command File**
   - Convert to `N5/commands/{command-name}.md`
   - Wrap original prompt in N5 command format
   - Add usage examples, metadata

3. **Register Command**
   - Add entry to `N5/config/commands.jsonl`
   - Include version, summary, tags

4. **Create Incantum Triggers**
   - Generate natural language triggers
   - Add to `N5/config/incantum_triggers.json`
   - Enable conversational invocation

5. **Handle Companion Files**
   - Move to `Knowledge/` (context for AI)
   - Preserve original filename

---

## Usage

### Single File Import
```bash
python N5/scripts/n5_import_prompt.py "Prompts/Function [01] - Title v1.0.txt"
```

### Batch Import (Directory)
```bash
python N5/scripts/n5_import_prompt.py --batch "Prompts/"
```

### Via N5 Command
```
N5: import-prompt Prompts/Function [01] - Title v1.0.txt
N5: import-prompt --batch Prompts/
```

---

## Example

### Input File
```
Prompts/Function [01] - Deep Research Due Diligence v0.3.txt
```

### Output

**1. Command File Created**:
```
N5/commands/deep-research-due-diligence.md
```

**2. Registry Entry**:
```json
{
  "name": "deep-research-due-diligence",
  "version": "0.3",
  "workflow": "single-shot",
  "summary": "Deep Research Due Diligence (personal prompt)",
  "function_file": "commands/deep-research-due-diligence.md",
  "entry_point": "function_file",
  "tags": ["personal", "prompt", "deep", "research"]
}
```

**3. Incantum Triggers**:
```json
{
  "trigger": "deep research due diligence",
  "aliases": [
    "deep research due diligence",
    "deep research",
    "research due diligence"
  ],
  "command": "deep-research-due-diligence"
}
```

**4. Usage**:
```
N5: deep research on Sequoia Capital
N5: run deep research
N5: deep-research-due-diligence
```

---

## Workflow for Bulk Import

### Step 1: Collect Prompts
Place all Function/Companion files in a single directory:
```
Prompts/
├── Function [01] - Prompt A v1.0.txt
├── Function [02] - Prompt B v1.2.pdf
├── Function [03] - Prompt C v0.5.txt
├── Companion [01] - Context A v1.0.txt
└── Companion [02] - Context B v1.5.txt
```

### Step 2: Run Batch Import
```bash
python N5/scripts/n5_import_prompt.py --batch "Prompts/"
```

### Step 3: Review Output
```
Importing: Function [01] - Prompt A v1.0.txt
  ✓ Created: N5/commands/prompt-a.md
  ✓ Added to commands.jsonl
  ✓ Added natural language triggers

Importing: Function [02] - Prompt B v1.2.pdf
  ✓ Created: N5/commands/prompt-b.md
  ✓ Added to commands.jsonl
  ✓ Added natural language triggers

...

BATCH COMPLETE: 5/5 imported
```

### Step 4: Test
```
N5: prompt a
N5: run prompt b
N5: help prompt-c
```

---

## Validation

After import, validate with:
```bash
# Check command file exists
ls N5/commands/{command-name}.md

# Check registry entry
grep "{command-name}" N5/config/commands.jsonl

# Check triggers
cat N5/config/incantum_triggers.json | grep "{command-name}"

# Test invocation
N5: {command-name}
```

---

## Updating Existing Prompts

To update a prompt with a new version:

1. **Delete old command** (optional - or keep for history)
2. **Import new version** with updated filename
3. **Old triggers preserved** - manual cleanup if needed

**Example**:
```bash
# Old: Function [01] - Title v1.0.txt → title command
# New: Function [01] - Title v2.0.txt → imports as title-v2 or updates existing
```

**Recommended**: Keep version in command name for major updates, or update in place for minor.

---

## Companion Files

Companion files are context/reference materials:
- Moved to `Knowledge/` (AI context)
- Not converted to commands
- Referenced by Function commands

**Example Flow**:
```
Companion [01] - Master Voice v1.3.txt
  → Knowledge/Companion [01] - Master Voice v1.3.txt
  → Referenced when executing related Function commands
```

---

## Troubleshooting

### Error: "Could not extract metadata"
- Check filename format matches pattern
- Ensure square brackets and version number present

### Error: "Command already exists"
- Command with that name already registered
- Choose different name or delete existing first

### Error: "Triggers already exist"
- Triggers for that command already created
- Safe to ignore or manually edit incantum_triggers.json

---

## Best Practices

1. **Consistent Naming**: Use clear, descriptive titles
2. **Version Control**: Always include version number
3. **Batch Import**: Import multiple prompts at once for efficiency
4. **Test After Import**: Verify commands work via Incantum
5. **Document**: Add usage notes to command files after import
6. **Archive Originals**: Keep original files in Prompts/ as backup

---

## Related Commands

- `docgen` - Regenerate command catalog after import
- `index-rebuild` - Rebuild system index
- `help {command-name}` - View imported command details

---

*Standardized prompt import pipeline for N5 OS*
