# N5 Commands Directory

This directory contains command definitions for the N5 operating system.

## Structure

Each command is documented in a markdown file with the following structure:

### Required YAML Frontmatter
```yaml
---
date: '<ISO 8601 timestamp>'
last-tested: '<ISO 8601 timestamp>'
generated_date: '<ISO 8601 timestamp>'
checksum: '<unique identifier>'
tags: [tag1, tag2, ...]
category: <category>
priority: <high|medium|low>
related_files: []
anchors:
  input: <path or null>
  output: <path>
---
```

### Required Sections
- `# \`command-name\`` - Title with command name in backticks
- `Version: X.Y.Z` - Semantic version
- `Summary: <one-line description>` - Brief description
- `Workflow: <workflow-type>` - Workflow category
- `## Inputs` - Command inputs/parameters
- `## Side Effects` - What the command modifies
- `## Related Components` - Links to related commands, scripts, etc.

### Optional Sections
- `## Outputs` - What the command produces
- `## Permissions Required` - Required permissions
- `## Process Flow` - Step-by-step execution
- `## Examples` - Usage examples

## Command Registry

Commands are also registered in:
- `N5/config/commands.jsonl` - Machine-readable registry
- `N5/config/incantum_triggers.json` - Shortcut triggers

## Categories

- **data**: Data ingestion and processing
- **lists**: List management operations  
- **knowledge**: Knowledge base operations
- **audit**: System auditing and health checks
- **productivity**: Productivity tools
- **system**: System operations

## Usage

Commands can be invoked via:
- Direct script execution: `python N5/scripts/<command>.py`
- N5 command interface: `N5: run <command>`
- Incantum triggers: `/shortcut`

## Development

When adding a new command:
1. Create command file with proper structure
2. Add entry to `commands.jsonl`
3. Add scripts to `N5/scripts/` if needed
4. Update this README if introducing new patterns
5. Run `N5: run core-audit` to validate

## See Also

- `file 'Documents/N5.md'` - N5 system overview
- `file 'N5/prefs/prefs.md'` - System preferences
- `file 'N5/schemas/index.schema.json'` - Schema definitions
