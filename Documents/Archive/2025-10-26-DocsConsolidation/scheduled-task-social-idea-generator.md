# Scheduled Task: Social Media Idea Generator

**Purpose:** Auto-generate LinkedIn posts from high-potential ideas in inbox

**Schedule:** Every Wednesday at 10:00 AM ET (weekly)

**RRULE:** `FREQ=WEEKLY;BYDAY=WE;BYHOUR=10;BYMINUTE=0`

---

## Instruction (Tightened)

Auto-generate LinkedIn posts from captured ideas with full context loading.

**STEP 1: Load ideas**
Read file 'Lists/social-media-ideas.md'
Parse "## Inbox" section for ideas with format:
  **ID:** I-YYYY-MM-DD-NNN
  **Title:** ...
  **Body:** ...
  **Tags:** ...

**STEP 2: Select ideas**
Choose top 1-2 detailed ideas with:
- Clear topics aligned to founder/career-coaching themes
- Sufficient body content (multiple paragraphs preferred)
- Relevance to V's work

Stop if < 3 ideas in inbox—needs fresh capture first.

**STEP 3: Generate with context**
For each selected idea, run:
python3 /home/workspace/N5/scripts/n5_social_idea_generate.py --id [IDEA_ID]

The generator auto-loads:
- file 'Knowledge/stable/bio.md'
- file 'Knowledge/stable/company.md'
- file 'Knowledge/semi_stable/positioning_current.md'
- file 'Knowledge/semi_stable/product_current.md'

**STEP 4: Verify import**
Run: python3 /home/workspace/N5/scripts/n5_social_post.py list --status draft
Confirm new posts exist with today's timestamp

**STEP 5: Report**

---

## Context Loading

The generator automatically loads:
- `Knowledge/stable/bio.md` - Who V is
- `Knowledge/stable/company.md` - Careerspan context
- `Knowledge/semi_stable/positioning_current.md` - Current positioning
- `Knowledge/semi_stable/product_current.md` - Product state
- Any files in `Knowledge/V-Beliefs/` - Core values

This ensures generated content is:
- Authentic to V's voice
- Aligned with current positioning
- Grounded in core beliefs
- Contextually relevant

---

## Output Format

```markdown
# Social Media Auto-Generation Report
**Date:** [Date]

## Ideas Processed
- [IDEA_ID_1]: [Title] → post_[POST_ID]
- [IDEA_ID_2]: [Title] → post_[POST_ID]

## Generated Posts
- [Count] new drafts created
- Topics: [Brief list]
- Files: [Relative paths]

## Inbox Status
- Remaining ideas: [Count]
- High-potential ideas awaiting generation: [Count]

## Next Steps
- Review new drafts: `python3 N5/scripts/n5_social_post.py list --status draft`
- Promote to pending when ready: `python3 N5/scripts/n5_social_post.py status [POST_ID] pending`
```

---

## Notes

- Fully automated - no V interaction required
- Results emailed to V
- V can review drafts at their convenience
- Ideas remain in system (moved to Processed section)
- Stop generation if inbox has < 3 ideas (needs fresh capture first)
