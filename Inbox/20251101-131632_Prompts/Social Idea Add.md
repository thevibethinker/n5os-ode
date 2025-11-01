---
description: 'Command: social-idea-add'
tags:
- social-media
- content
- ideas
- capture
tool: true
---
# Social Idea: Add

Capture a social media content idea with rich details.

## Quick Start

```bash
# Add idea (command line)
python3 N5/scripts/n5_social_idea_add.py \
    --title "When vulnerability becomes strategic clarity" \
    --body "I've noticed the difference between dumping emotion and showing the exact decision..." \
    --tags "founders,vulnerability"

# Interactive mode (prompts for input)
python3 N5/scripts/n5_social_idea_add.py --interactive

# Dry-run preview
python3 N5/scripts/n5_social_idea_add.py \
    --title "Test idea" \
    --body "Test body" \
    --dry-run
```

## Manual Capture (Fastest)

1. Open file 'Lists/social-media-ideas.md'
2. Under "## Inbox", add a new block:

```markdown
**ID:** I-2025-10-22-XXX  
**Title:** Your compelling title  
**Body:**

Your detailed observation, story, or reflection.
Multiple paragraphs are fine—capture all the nuance.

**Tags:** #tag1 #tag2

---
```

3. Update ID (next sequential number for today)
4. Save

## Parameters

- `--title` - Clear, compelling title for the idea
- `--body` - Detailed body (observations, examples, angle, why it matters)
- `--tags` - Comma-separated tags (optional)
- `--interactive` - Prompt for input interactively
- `--dry-run` - Preview without adding

## What it Does

1. Generates next sequential ID for today (I-YYYY-MM-DD-NNN)
2. Formats as paragraph block with title, body, tags
3. Appends to Inbox section of Lists/social-media-ideas.md
4. Logs the ID for later generation

## ID Format

`I-YYYY-MM-DD-NNN` where NNN is sequential (001, 002, 003...)

Example: `I-2025-10-22-001`

## Next Steps

After adding ideas:
1. Review them in file 'Lists/social-media-ideas.md'
2. Move promising ones to "In Review" section
3. Generate content: `python3 N5/scripts/n5_social_idea_generate.py --id I-2025-10-22-001`

## See Also

- `file N5/commands/social-idea-generate.md` - Generate from ideas
- `file Lists/social-media-ideas.md` - The ideas list
- `file N5/commands/social-post-list.md` - View generated posts
