# Content Library — Quick Start Guide

**Location:** `N5/prefs/communication/content-library.json`  
**CLI:** `N5/scripts/content_library.py`

---

## What It Does

A self-feeding knowledge flywheel that:
1. Stores links & reusable text snippets (SSOT)
2. Auto-discovers resources from meetings
3. Auto-injects into generated outputs (emails, docs)
4. Tracks usage, versions, deprecation

---

## Quick Commands

### Add Content
```bash
# Quick-add (auto-categorizes)
python3 N5/scripts/content_library.py quick-add \
  --text "Your content or URL" \
  --title "Optional title"

# Manual add (full control)
python3 N5/scripts/content_library.py add \
  --type link \
  --title "Zo Referral" \
  --url "https://www.zo.computer/?promo=VATT50" \
  --tags "purpose=referral,audience=founders"
```

### Search
```bash
# Text search
python3 N5/scripts/content_library.py search --query "zo"

# Tag search
python3 N5/scripts/content_library.py search \
  --tag "purpose=referral" \
  --tag "audience=founders"

# Combined
python3 N5/scripts/content_library.py search \
  --query "career" \
  --tag "entity=careerspan"
```

### Update & Deprecate
```bash
# Update content
python3 N5/scripts/content_library.py update \
  --id vrijen_bio_short \
  --content "New bio text"

# Deprecate
python3 N5/scripts/content_library.py deprecate \
  --id old_pitch \
  --expires-at 2025-12-31
```

---

## Meeting Processing Pipeline

```bash
# 1. Parse meeting transcript
python3 N5/scripts/b_block_parser.py \
  /path/to/transcript.txt \
  --output blocks.json

# 2. Generate follow-up email
python3 N5/scripts/email_composer.py \
  blocks.json \
  --recipient "Name" \
  --summary "Brief summary" \
  --output draft.txt

# 3. Auto-discover new content (dry-run)
python3 N5/scripts/auto_populate_content.py \
  blocks.json \
  --dry-run

# 4. If good, add to library
python3 N5/scripts/auto_populate_content.py blocks.json
```

---

## Tag Schema

### Common Tags
- **purpose:** bio, hook, boilerplate, signature, resource, guide, education
- **audience:** founders, investors, job_seekers, general, operators
- **tone:** concise, confident, provocative, empathetic, technical
- **entity:** vrijen, careerspan, N5, zo_computer
- **channel:** email, linkedin, docs, social
- **status:** active, deprecated, placeholder

### Example Item
```json
{
  "id": "vrijen_bio_short",
  "type": "snippet",
  "title": "Bio (short)",
  "content": "Founder, Careerspan. Builder of N5 OS.",
  "tags": {
    "purpose": ["bio"],
    "audience": ["general"],
    "tone": ["concise"],
    "entity": ["vrijen"]
  }
}
```

---

## Integration Points

### Current
- B-Block Parser (meeting → structured data)
- Email Composer (auto-inject signature, resources)
- Auto-Population (meeting → library)

### Pending (Next Phase)
- `n5_follow_up_email_generator.py` (full integration)
- Auto-injection rules (per-channel, per-audience)
- Weekly review workflow (approve discovered snippets)

---

## Principles

1. **Explicit vs. Suggested:** Resources mentioned in conversation take priority over "might be helpful" suggestions
2. **Deduplication:** URL normalization prevents duplicate links
3. **Version tracking:** Every update bumps version number
4. **Last-used telemetry:** Track what's actually being used
5. **Deprecation with expiry:** Old content can be sunset gracefully

---

## Troubleshooting

**Q: Item not found in search?**  
A: Check tags with `--tag` flag; search is case-insensitive but exact match on tags

**Q: Duplicates still appearing?**  
A: Parser deduplicates by normalized URL (lowercase, no trailing slash)

**Q: How to batch import?**  
A: Use `quick-add --input-file` for text files, or write a loop:
```bash
for url in $(cat urls.txt); do
  python3 N5/scripts/content_library.py quick-add --text "$url"
done
```

**Q: Can I edit the JSON directly?**  
A: Yes! It's human-readable and git-tracked. Just follow the schema.

---

## File Locations

- **SSOT:** `N5/prefs/communication/content-library.json`
- **CLI:** `N5/scripts/content_library.py`
- **Parser:** `N5/scripts/b_block_parser.py`
- **Composer:** `N5/scripts/email_composer.py`
- **Auto-pop:** `N5/scripts/auto_populate_content.py`

---

**Version:** 1.0.0 | **Date:** 2025-10-22
