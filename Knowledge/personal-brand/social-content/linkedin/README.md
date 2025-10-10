# LinkedIn Social Content Catalog

**Purpose**: Knowledge repository of generated LinkedIn posts  
**Category**: Personal Brand | Social Media Output  
**Created**: 2025-10-10

---

## Overview

This directory catalogs all LinkedIn posts generated using the `linkedin-post-generate` command. Each generation creates three files:

1. **Post Draft** (`YYYY-MM-DD-HHmm-post-draft.md`) → Ready-to-paste LinkedIn content
2. **Metadata** (`YYYY-MM-DD-HHmm-post-metadata.json`) → Voice config, metrics, validation
3. **Analysis** (`YYYY-MM-DD-HHmm-post-analysis.md`) → Quality report, recommendations

---

## File Structure

```
linkedin/
├── README.md (this file)
├── 2025-10-10-0052-post-draft.md
├── 2025-10-10-0052-post-metadata.json
├── 2025-10-10-0052-post-analysis.md
└── ... (additional posts)
```

---

## Usage

### Generate New Post

```bash
linkedin-post-generate --seed "Your content idea here"
```

See `file 'N5/commands/linkedin-post-generate.md'` for full documentation.

---

## Catalog Statistics

Track your LinkedIn content over time:
- **Total Posts Generated**: (manually update as you use the system)
- **Average Word Count**: 
- **Most Common CTA Type**:
- **Voice Formality Distribution**:

---

## Best Practices

1. **Provide Rich Seed Content**: 100+ words with examples, anecdotes, stats
2. **Review Analysis Report**: Check validation before posting
3. **Iterate as Needed**: Regenerate with dial overrides if needed
4. **Track Performance**: Note which posts resonate (likes, comments, shares)
5. **Build Template Library**: Save successful patterns for reuse

---

## Post Performance Tracking (Optional)

You can manually track post performance here:

| Date | Topic | Word Count | Engagement (Likes/Comments) | Notes |
|------|-------|-----------|----------------------------|-------|
| 2025-10-10 | Retention as career dev | 86 | - | Test post |
|  |  |  |  |  |

---

## Related Commands

- `file 'N5/commands/linkedin-post-generate.md'` → Full command documentation
- `file 'N5/prefs/communication/voice.md'` → Voice preferences
- `file 'N5/prefs/communication/linkedin-stop-verbs.json'` → Prohibited language

---

## Future Enhancements

- **Tier 2**: Comedic mode, template library
- **Tier 3**: Analyzer, style learning from examples
- **Analytics**: Automated performance tracking
- **Scheduling**: Direct LinkedIn API integration
