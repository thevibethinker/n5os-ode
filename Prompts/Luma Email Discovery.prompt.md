---
title: Luma Email Discovery
description: Scans newsletters and listservs for new Luma events
tags: [luma, discovery, email]
tool: true
---

# Luma Email Discovery

This prompt scans your newsletters and listservs for Luma event links.
It runs incrementally (only new emails since the last check).

<system>
1. **Load State**
   - Read `/home/workspace/N5/data/email_scan_state.json` to get `last_history_id` or `last_timestamp`.
   - Default to "1 day ago" if no state exists.

2. **Fetch Emails**
   - Use `use_app_gmail(tool_name="gmail-list-messages", ...)`
   - Query: `label:newsletters OR label:listservs OR label:events OR "lu.ma/event"`
   - Filter: `after:<last_timestamp>` (if using date) or process logic using history ID.
   - Limit: 50 (for safety).

3. **Process**
   - Save the email data (snippet/body) to `/home/workspace/N5/data/email_scan_temp.json`.
   - Run the discovery script:
   ```bash
   python3 /home/workspace/N5/scripts/luma_email_discovery.py --email-file /home/workspace/N5/data/email_scan_temp.json
   ```

4. **Update State**
   - Save the current timestamp/ID to `/home/workspace/N5/data/email_scan_state.json`.

5. **Report & Feedback**
   - List newly discovered events.
   - Show their "Scores" (run `python3 N5/scripts/luma_scorer.py` if needed).
   - Check for any events that have been "attended" (date passed + approved/on calendar).
   - Ask the user: "Did you attend [Event Name]? How was it?"
   - If they provide feedback, log it to `N5/data/luma_feedback.jsonl` (to be used for organizer reputation scoring later).
</system>

