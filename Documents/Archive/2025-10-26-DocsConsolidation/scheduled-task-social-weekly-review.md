# Scheduled Task: Weekly Social Media Review

**Purpose:** Review pending posts, analyze performance, surface insights

**Schedule:** Every Monday at 9:00 AM ET

**RRULE:** `FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0`

---

## Instruction (Tightened)

Execute weekly social media content review.

**STEP 1: List all posts**
Run: python3 /home/workspace/N5/scripts/n5_social_post.py list --status pending
Run: python3 /home/workspace/N5/scripts/n5_social_post.py list --status draft
Run: python3 /home/workspace/N5/scripts/n5_social_post.py list --status submitted
Run: python3 /home/workspace/N5/scripts/n5_social_post.py stats

**STEP 2: Check ideas inbox**
Read file 'Lists/social-media-ideas.md'
Count ideas under "## Inbox" section
Identify high-potential ideas (detailed, clear topics, aligned to founder/career themes)

**STEP 3: Analyze patterns (if metrics exist)**
Check submitted posts for:
- Posting times
- Topic themes
- Engagement indicators (if recorded via record-metrics command)

**STEP 4: Generate concise report**

---

## Output Format

```markdown
# Weekly Social Media Review
**Week of:** [Date]

## Pending Posts (Ready for Review)
- [Count] posts waiting
- Themes: [List]
- Recommended priority: [Top 2-3 with rationale]

## Draft Posts
- [Count] drafts available
- Status: [Any that need work?]

## Ideas Inbox
- [Count] active ideas
- High-potential: [List 2-3 with brief rationale]

## Performance Insights
[Once metrics are tracked]
- Best performing topics
- Optimal post times
- Engagement patterns

## Recommendations
1. [Action item]
2. [Action item]
3. [Action item]
```

---

## Notes

- Email results to V
- Keep concise - focus on actionable insights
- Evolve analysis as metrics accumulate
