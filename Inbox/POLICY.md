# Inbox Policy

**Purpose:** Clearinghouse for workspace root items awaiting classification and routing

**Version:** 1.0.0  
**Created:** 2025-10-27

---

## What Is This Folder?

The **Inbox** is a temporary staging area for files that appear in the workspace root. It acts as a clearinghouse where items are:

1. **Collected** from root (daily cleanup)
2. **Analyzed** by AI (weekly processing)
3. **Routed** to permanent homes (automated or manual)

Think of it as your workspace's "inbox zero" system—items flow through, not pool indefinitely.

---

## How Items Arrive Here

**Automatic Collection:**
- Daily at 11pm ET, `cleanup-root` scans workspace root
- Any items not in protected directories are moved here
- Files get timestamped prefix: `20251027-230000_filename.ext`
- All moves logged to `N5/logs/.cleanup_log.jsonl`

**Protected directories** (never moved):
- Knowledge/, Lists/, Records/, N5/, Documents/
- Careerspan/, Personal/, Articles/, Images/
- projects/, Recipes/, Inbox/, .git

---

## How Items Leave Here

**Three Paths:**

### Path A: Auto-Route (High Confidence ≥85%)
- AI analyzes file content + metadata
- Determines destination with high confidence
- Automatically moves to correct location
- Logged in `N5/logs/.inbox_analysis.jsonl`

### Path B: Suggested Route (Medium Confidence 60-84%)
- AI suggests destination but not confident enough to auto-route
- Listed in `REVIEW.md` for your review
- You manually move after reviewing suggestion
- Provide feedback to improve future routing

### Path C: Manual Review (Low Confidence <60%)
- AI can't confidently classify
- Flagged in `REVIEW.md` as requiring manual decision
- You review and move to appropriate location
- Helps system learn edge cases

---

## Time To Live (TTL)

**Target:** Items should leave Inbox within **7 days**  
**Alert:** System warns if items exceed **14 days**

If items are stuck here:
- Check `REVIEW.md` for pending decisions
- Manually route ambiguous files
- Consider if new routing rules needed

---

## The REVIEW.md File

**Auto-generated weekly** (Sunday 8pm ET) by `inbox-process`

**Contains:**
- Summary of pending items
- TTL warnings (files >14 days old)
- Auto-route candidates (will move on next run)
- Suggested routings (need your decision)
- Manual review items (need classification)
- Instructions for processing

**Regenerate anytime:** Run `python3 N5/scripts/inbox_review_generator.py`

---

## Workflow Overview

```
Root Directory
    ↓ (cleanup-root, daily 11pm)
Inbox/
    ↓ (inbox-process, weekly Sunday 8pm)
    ├─→ Auto-route (≥85%) → Knowledge/, Documents/, etc.
    ├─→ Suggest (60-84%) → Flagged in REVIEW.md
    └─→ Manual (<60%) → Flagged in REVIEW.md
```

---

## File Naming Convention

**Format:** `YYYYMMDD-HHMMSS_originalname.ext`

**Example:** `20251027-230015_meeting-notes.md`

**Why timestamps?**
- Preserves chronological order
- Prevents name collisions
- Enables audit trail
- Easy to identify when file arrived

---

## Human Actions Required

### Weekly Review (5-10 minutes)
1. Open `Inbox/REVIEW.md`
2. Review suggested routings (60-84% confidence)
3. Classify manual review items (<60% confidence)
4. Move files to appropriate destinations
5. (Future) Provide feedback on corrections

### As Needed
- Run `inbox-review` to see current status
- Manually route urgent items before weekly processing
- Check for TTL violations

---

## System Integration

**Commands:**
- `cleanup-root` - Move root items here
- `inbox-process` - Analyze, route, generate review
- `inbox-review` - Regenerate REVIEW.md

**Scheduled Tasks:**
- **Daily 11pm ET:** cleanup-root (collect from root)
- **Sunday 8pm ET:** inbox-process (analyze and route)

**Logs:**
- `N5/logs/.cleanup_log.jsonl` - Root cleanup operations
- `N5/logs/.inbox_analysis.jsonl` - File analyses and routing
- (Future) `N5/logs/.inbox_feedback.jsonl` - Human corrections

---

## Design Philosophy

This system embodies N5OS principles:

**Flow Over Pools (ZT2):**
- Information flows through stages, doesn't pool indefinitely
- Time limits enforce movement (7-day target, 14-day alert)

**Maintenance Over Organization (ZT4):**
- System organizes automatically, you review exceptions
- Target: <15% touch rate (you only handle edge cases)

**Minimal Touch (ZT8):**
- High-confidence items route without your involvement
- You focus on ambiguous cases that need judgment

**Self-Aware Systems (ZT9):**
- System tracks its own health (TTL violations, error rates)
- Alerts when attention needed

---

## Configuration

**Files:**
- `N5/config/root_cleanup_config.json` - What to collect
- `N5/config/routing_config.json` - Where to route, confidence thresholds

**Key Settings:**
- Auto-route threshold: 85% confidence
- Suggest threshold: 60% confidence
- TTL warning: 14 days
- Valid destinations: Whitelist of allowed paths

---

## Troubleshooting

**Inbox filling up:**
- Check `REVIEW.md` for pending decisions
- Lower confidence threshold if too conservative
- Add routing rules for common patterns

**Wrong auto-routes:**
- Review `N5/logs/.inbox_analysis.jsonl`
- Raise confidence threshold if too aggressive
- Provide feedback to improve LLM prompts

**Nothing being analyzed:**
- Check weekly processing ran: `list_scheduled_tasks`
- Manually run: `python3 N5/scripts/inbox_analyzer.py`
- Review logs for errors

---

## Future Enhancements

**Planned:**
- Feedback logging system (track corrections)
- Learning from feedback (improve routing over time)
- Confidence threshold auto-tuning
- Pattern detection (similar files → create rules)
- Bulk operations (move all suggestions at once)

---

## Related Documentation

- `file 'N5/commands/cleanup-root.md'` - Root cleanup command
- `file 'N5/commands/inbox-process.md'` - Processing workflow
- `file 'N5/commands/inbox-review.md'` - Review generation
- `file 'Knowledge/architectural/planning_prompt.md'` - Design philosophy
- `file 'Knowledge/architectural/architectural_principles.md'` - System principles

---

**Last Updated:** 2025-10-27  
**Status:** Active  
**Owner:** System (automated) + V (exception review)
