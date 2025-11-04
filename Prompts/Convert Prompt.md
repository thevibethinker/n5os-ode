---
description: 'Command: convert-prompt'
tool: true
tags:
- prompts
- conversion
- formatting
- ai
---
# `convert-prompt`

Version: 1.0.0

Summary: Convert prompts between different formats and AI platforms

Workflow: productivity

Tags: prompts, conversion, formatting, ai, templates

## Inputs
- input_file : file (required) — Path to prompt file to convert
- --from : string (required) — Source format: 'plaintext', 'xml', 'json', 'yaml', 'chatgpt', 'claude'
- --to : string (required) — Target format: 'plaintext', 'xml', 'json', 'yaml', 'chatgpt', 'claude'
- --output : file (optional) — Output file path (default: same name with new extension)
- --preserve-metadata : flag (optional) — Preserve metadata fields during conversion

## Outputs
- converted_file : file — Converted prompt file
- conversion_report : text — Summary of conversion including any warnings

## Side Effects
- writes:file (converted prompt file)

## Process Flow
1. **Parse Input**: Read and parse source prompt file
2. **Extract Components**: Identify structure, metadata, variables, examples
3. **Validate**: Check for format-specific requirements
4. **Transform**: Convert to target format structure
5. **Optimize**: Apply format-specific best practices
6. **Write**: Save converted prompt
7. **Report**: Generate conversion summary

## Examples
- Convert to XML: `python N5/scripts/convert_prompt.py prompt.txt --from plaintext --to xml`
- Claude to ChatGPT: `python N5/scripts/convert_prompt.py claude_prompt.xml --from claude --to chatgpt`
- JSON to YAML: `python N5/scripts/convert_prompt.py prompt.json --from json --to yaml --output prompt.yaml`
- Preserve metadata: `python N5/scripts/convert_prompt.py prompt.md --from plaintext --to xml --preserve-metadata`

## Supported Formats

### Plaintext
- Simple text with minimal structure
- Variables marked as {{variable}}
- Sections separated by headers

### XML
- Structured with semantic tags
- Supports nested contexts
- Preserves whitespace and formatting

### JSON
- Machine-readable structured format
- Supports complex nested data
- Good for programmatic manipulation

### YAML
- Human-readable structured format
- Clean syntax for hierarchical data
- Popular for configuration

### Platform-Specific
- **ChatGPT**: System/user/assistant message format
- **Claude**: XML-based structured prompt format

## Conversion Rules
- Variables are normalized to target format conventions
- Examples are preserved and reformatted
- Metadata mapped to equivalent fields when possible
- Comments converted to appropriate format
- Whitespace adjusted for target format requirements

## Related Components

**Related Commands**: [`prompt-import`](../commands/prompt-import.md), [`docgen`](../commands/docgen.md)

**Scripts**: `N5/scripts/convert_prompt.py` (to be created), `N5/scripts/prompt_parser.py` (to be created)

**Knowledge Areas**: [Prompt Engineering](../knowledge/prompt-engineering.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

## Implementation Notes
- Supports bidirectional conversion between all formats
- Validates output against target format schema
- Warns about lossy conversions (format limitations)
- Can batch convert multiple files
- Preserves git history if files are tracked

## Future Enhancements
- [ ] Auto-detect source format
- [ ] Support for more AI platforms (Gemini, Mistral, etc.)
- [ ] Template library integration
- [ ] Version control for prompt iterations
- [ ] A/B testing support for prompt variations
