---
description: 'Command: social-idea-generate'
tool: true
tags:
- social-media
- generation
- content
- automation
---
# Social Idea: Generate

Generate social media content from one or more captured ideas.

## Quick Start

```bash
# Generate from single idea
python3 N5/scripts/n5_social_idea_generate.py --id I-2025-10-22-001

# Combine multiple ideas (synthesis)
python3 N5/scripts/n5_social_idea_generate.py \
    --id I-2025-10-22-001 \
    --id I-2025-10-22-004

# With generation options
python3 N5/scripts/n5_social_idea_generate.py \
    --id I-2025-10-22-001 \
    --platform linkedin \
    --mode insight \
    --formality medium

# Dry-run preview
python3 N5/scripts/n5_social_idea_generate.py \
    --id I-2025-10-22-001 \
    --dry-run
```

## Parameters

- `--id` - Idea ID(s) to generate from (can specify multiple)
- `--platform` - Target platform (default: linkedin)
- `--mode` - Generation mode: insight, story, announcement, question (default: insight)
- `--formality` - Formality level: low, medium, high (default: medium)
- `--dry-run` - Preview without generating

## What it Does

1. Reads idea(s) from file 'Lists/social-media-ideas.md'
2. Moves idea(s) to "In Progress" section
3. Calls LinkedIn post generator with idea content as seed
4. Saves generated draft with metadata
5. Auto-imports to tracking system (status: draft, platform: linkedin)
6. Moves processed idea(s) to "Processed" section with link to post ID
7. Reports post ID and file location

## Generation Modes

- **insight** - Analytical, framework-driven (default)
- **story** - Narrative, vulnerable, relatable
- **announcement** - Direct, promotional
- **question** - Engagement-focused, community-building

## Output

Generated posts go to:
- File: `Knowledge/personal-brand/social-content/linkedin/draft/🔗_TIMESTAMP_SLUG.md`
- Registry: `N5/data/social-posts.jsonl`
- Status: draft (ready for review)

## Next Steps

After generation:
1. Review draft: `python3 N5/scripts/n5_social_post.py list --status draft`
2. Open the file and refine
3. Mark as pending: `python3 N5/scripts/n5_social_post.py status <post_id> pending`
4. Publish and track: `python3 N5/scripts/n5_social_post.py status <post_id> submitted --url <url>`

## Synthesis (Multiple Ideas)

When you specify multiple `--id` flags:
- Generator combines themes and examples
- Creates richer, multi-layered post
- References all source idea IDs in metadata
- All source ideas moved to "Processed" together

## See Also

- `file N5/commands/social-idea-add.md` - Add new ideas
- `file N5/commands/social-post-list.md` - List generated posts
- `file N5/commands/social-post-status.md` - Update post status
- `file Lists/social-media-ideas.md` - The ideas list
