---
name: google-stitch
description: Generate UI screens from text prompts using Google Stitch. Create projects, generate mobile/web screens, edit designs, and export HTML/screenshots via the @google/stitch-sdk.
category: Media & Graphics
metadata:
  author: <YOUR_HANDLE>.zo.computer
  emojis: ["🎨", "🖼️", "✨"]
  emoji: 🎨
tags:
  - stitch
  - ui-design
  - ui-generation
  - design
  - screens
  - html
---

# Google Stitch Integration

Google Stitch generates UI screens from text prompts, making design ideation fast and easy.

## Setup

The `STITCH_API_KEY` secret must be configured in [Zo Settings > Advanced](/?t=settings&s=advanced).

## Usage

```bash
bun Skills/google-stitch/scripts/stitch.ts <command> [args]
```

### Commands

| Command | Description |
|---------|-------------|
| `projects` | List all projects |
| `create <title>` | Create a new project |
| `screens <projectId>` | List screens in a project |
| `generate <projectId> <prompt>` | Generate a screen from text |
| `preview <projectId> <prompt>` | Generate and save HTML + screenshot |
| `save <projectId> <prompt> [filename]` | Generate and save HTML to file |
| `get <projectId> <screenId>` | Get screen details |
| `html <projectId> <screenId>` | Get screen HTML URL |
| `image <projectId> <screenId>` | Get screen image URL |
| `edit <projectId> <screenId> <prompt>` | Edit a screen |
| `variants <projectId> <screenId> <prompt>` | Generate variants |
| `tools` | List available MCP tools |

### Options

- `--device T` - Device type: MOBILE, DESKTOP, TABLET, AGNOSTIC (default: AGNOSTIC)
- `--creative R` - Creative range: REFINE, EXPLORE, REIMAGINE (default: EXPLORE)
- `--count N` - Number of variants (default: 3)

## Viewing Generated Screens

Use the `preview` command to generate a screen and save both HTML and screenshot:

```bash
bun Skills/google-stitch/scripts/stitch.ts preview "project-id" "A login page"
```

This saves:
- `/home/workspace/Images/stitch-preview.html` - Interactive HTML you can open in a browser
- `/home/workspace/Images/stitch-preview.png` - Screenshot image

## Examples

```bash
# List projects
bun Skills/google-stitch/scripts/stitch.ts projects

# Create a project
bun Skills/google-stitch/scripts/stitch.ts create "My App"

# Generate a screen (full JSON output)
bun Skills/google-stitch/scripts/stitch.ts generate "project-id" "A login page with email and password"

# Generate and preview (saves HTML + PNG)
bun Skills/google-stitch/scripts/stitch.ts preview "project-id" "A login page"

# Generate for mobile specifically
bun Skills/google-stitch/scripts/stitch.ts generate "project-id" "A mobile checkout flow" --device MOBILE
```
