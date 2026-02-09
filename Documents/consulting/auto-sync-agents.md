---
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
provenance: con_ih5ObcEHG5Dgkdx8
---

# Auto-Sync Scheduled Agents

## Purpose

Automated GitHub substrate synchronization between va and zoputer instances via scheduled agents. Ensures Tier 0 skills are automatically pushed from va to GitHub, then pulled to zoputer, maintaining consistency across both environments.

## Architecture

```
9:00 AM ET  - va pushes to GitHub (automated)
              ↓ 
            GitHub substrate repository
              ↓
9:15 AM ET  - zoputer pulls from GitHub (manual setup required)
```

The 15-minute gap ensures GitHub has processed the push before zoputer attempts to pull.

## va-Side Agent (COMPLETE)

**Agent Details:**
- **Schedule:** Daily at 9:00 AM ET (14:00 UTC)
- **Instruction:** 
  ```
  Run the daily substrate sync to push Tier 0 skills to GitHub.
  
  1. Run: python3 Skills/git-substrate-sync/scripts/sync.py push
  2. If successful, no notification needed
  3. If failed, text V: "Substrate sync failed: [error summary]"
  4. Log result to audit system
  ```
- **Status:** ✅ Created and active
- **Delivery Method:** SMS (failures only)

## zoputer-Side Agent Setup (MANUAL REQUIRED)

V must manually create this agent on the zoputer instance.

### Steps to Create on zoputer:

1. **Navigate to Scheduled Tasks**
   - Go to [Scheduled Tasks](/?t=agents) on zoputer
   - Click "Create New Agent"

2. **Agent Configuration**
   - **Title:** Daily Substrate Pull from GitHub
   - **Schedule (RRULE):** `FREQ=DAILY;BYHOUR=14;BYMINUTE=15`
   - **Delivery Method:** None (or email for failures)
   
3. **Agent Instruction (Copy Exactly):**
   ```
   Pull latest content from the GitHub substrate.
   
   1. Run: python3 Skills/git-substrate-sync/scripts/pull.py
   2. If new content, log what was updated
   3. If failed, escalate to va: "Pull failed: [error]"
   4. If "nothing to sync" message, complete silently
   ```

4. **Verification**
   - Ensure schedule is 9:15 AM ET (15 minutes after va push)
   - Test manual execution once to verify script path is correct

## Change Detection Logic

Both scripts include skip-if-unchanged logic:
- **va push:** Detects if no Tier 0 content has changed since last push
- **zoputer pull:** Detects if GitHub has no new commits since last pull
- **Silent completion:** Agents complete without notification when no changes detected

## Sync Window Details

| Time (ET) | Action | Instance | Notes |
|-----------|---------|----------|-------|
| 9:00 AM | Push to GitHub | va | Automated |
| 9:15 AM | Pull from GitHub | zoputer | Manual setup |

This schedule ensures:
- va pushes changes to GitHub first
- GitHub has time to process the push
- zoputer pulls the latest changes reliably

## Error Handling

**va failures:**
- Text V with error summary
- Logged to audit system

**zoputer failures:**
- Should escalate to va (configure delivery method if desired)
- Manual monitoring recommended initially

## Notes

- Agents are NOT cornerstone (⇱) tasks and can be modified
- Uses existing git-substrate-sync skill (D1.2 dependency)
- No webhook setup needed - scheduled pulls are simpler and sufficient
- Content filtering handled by content-classifier integration in sync scripts

## Manual Action Required

⚠️ **V must create the zoputer pull agent using the configuration above**

The va-side agent is already created and will begin pushing to GitHub at 9:00 AM ET daily.