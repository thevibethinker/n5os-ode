# Content Library - Quick Reference

## Common Commands

### Search & Find
```bash
# Find Zo partnership items
python3 N5/scripts/content_library.py search --tag entity:zo_partnership

# Find all snippets
python3 N5/scripts/content_library.py search --type snippet

# Find founder-focused content
python3 N5/scripts/content_library.py search --tag audience:founders

# Text search
python3 N5/scripts/content_library.py search --query "bio"

# List everything
python3 N5/scripts/content_library.py list
```

### Add Content
```bash
# Add a bio snippet
python3 N5/scripts/content_library.py add \
  --id vrijen_bio_short \
  --type snippet \
  --title "Vrijen Bio (Short)" \
  --content "Your bio text here..." \
  --tag context:email \
  --tag audience:general \
  --tag purpose:introduction \
  --tag entity:vrijen

# Add a link
python3 N5/scripts/content_library.py add \
  --id new_link_id \
  --type link \
  --title "Link Title" \
  --content "https://example.com" \
  --tag context:email \
  --tag audience:general \
  --tag purpose:demo
```

### Update & Manage
```bash
# Update content
python3 N5/scripts/content_library.py update \
  --id vrijen_bio_short \
  --content "Updated bio..."

# Deprecate old item
python3 N5/scripts/content_library.py deprecate \
  --id old_link \
  --expires-at 2025-12-31
```

### Export
```bash
# Export as markdown
python3 N5/scripts/content_library.py export --tag entity:careerspan --format markdown

# Export as JSON
python3 N5/scripts/content_library.py export --tag audience:investors --format json
```

## Tag Reference

### context (where used)
- email, chat, meeting, pitch, social, website, presentation, demo

### audience (who receives)
- general, professional, founders, investors, job_seekers, candidates, employers, recruiters, friends, family, mba, consultants

### purpose (why used)
- demo, referral, education, scheduling, marketing, partnership, sales, introduction, bio, signature, trial, onboarding, fundraising, pitch, resource, tool

### tone (style)
- professional, casual, formal

### entity (related to)
- vrijen, careerspan, zo_partnership, founders

### duration (for meetings)
- 15min, 30min, 45min

## Programmatic Usage

```python
from content_library import ContentLibrary

# Initialize
lib = ContentLibrary()

# Search
items = lib.search(tags={
    "audience": ["founders"],
    "purpose": ["referral"]
})

# Get specific item
snippet = lib.get_by_id("vrijen_bio_short")
print(snippet["content"])

# Add item
lib.add(
    item_id="new_id",
    item_type="snippet",
    title="Title",
    content="Content...",
    tags={"context": ["email"], "audience": ["general"]}
)

# Mark as used
lib.mark_used("vrijen_bio_short")
```

## File Locations

- **CLI**: `N5/scripts/content_library.py`
- **Data**: `N5/prefs/communication/content-library.json`
- **Docs**: `Documents/System/content-library-system.md`
- **Examples**: `file '/home/.z/workspaces/con_frSxWyuzF9e9DgbU/SNIPPET_EXAMPLES.md'`

## Current Status

**Items**: 26 (22 links + 4 snippets)  
**Phase**: 1 Complete, Phase 2 (parallel operation)  
**Migration**: essential-links.json deprecated  
**Next**: Add bio/company snippets, update workflows
