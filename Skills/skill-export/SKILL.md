---
name: skill-export
description: Automated pipeline to sanitize, package, and prepare Zo-optimized skills for store distribution. Removes sensitive data, generates listings, and creates distribution packages.
compatibility: Created for Zo Computer
---

# Skill Export Pipeline

Automated pipeline for preparing Zo-optimized skills for sale on the store. This skill sanitizes source code, generates store listings, and creates distribution packages.

## Features

- **Smart Sanitization**: Automatically removes sensitive data (API keys, absolute paths, personal info)
- **Store-Ready Packaging**: Creates optimized ZIP packages for distribution
- **Listing Generation**: Auto-generates store listing JSON from skill metadata
- **Multi-Format Support**: Can create both Zo-optimized and Claude Code Cursor versions
- **Safe Processing**: Works on copies, never modifies original skills

## Usage

The main command is `export.py` which orchestrates the entire pipeline:

```bash
python3 Skills/skill-export/scripts/export.py <skill-slug> [options]
```

### Options
- `--output-dir PATH`: Directory for output files (default: current directory)
- `--claude-code`: Also create Claude Code Cursor compatible version
- `--help`: Show detailed usage

### Example
```bash
# Export the 'pulse' skill to artifacts directory
python3 Skills/skill-export/scripts/export.py pulse --output-dir ./artifacts
```

This will:
1. Sanitize the skill (remove sensitive data)
2. Generate store listing JSON
3. Create `pulse-zo.zip` package
4. Output listing metadata to stdout

## Sanitization Rules

The pipeline automatically removes or replaces:

- **Absolute Paths**: `/home/workspace/` → relative paths
- **Internal Systems**: `N5/` references → generic placeholders  
- **API Keys**: Patterns like `sk-`, `FILLOUT_SECRET_*` → `<YOUR_API_KEY>`
- **Personal Info**: Email addresses, phone numbers → placeholders
- **Webhook URLs**: Zo-specific URLs → `<YOUR_WEBHOOK_URL>`

## Output Structure

For each exported skill, you'll get:
- `<skill>-zo.zip`: Main distribution package
- `<skill>-claude-code.zip`: (optional) Claude Code version
- Listing JSON printed to stdout for store integration

The listing JSON includes auto-detected badges like "zo-optimized" and features extracted from the skill's documentation.