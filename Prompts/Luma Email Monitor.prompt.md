---
title: Luma Email Monitor
description: Scans Gmail for Luma event approvals and updates system status
tags: [luma, automation, email, sms]
tool: true
---

# Luma Email Monitor

1. **Search Gmail**
   Call `use_app_gmail` with `tool_name="gmail-search-messages"` and `configured_props={"q": "from:(support@lu.ma OR no-reply@lu.ma) subject:(\"Registration Approved\" OR \"You're in\" OR \"Ticket\") newer_than:1d"}`.

2. **Process Results**
   For each email found in the search results:
   a. **Read Email:** Use `use_app_gmail` with `tool_name="gmail-get-message"` (or assume snippet is enough if title is visible) to identify the **Event Title**. Look for text like "You're in for [Event Name]" or "Your ticket for [Event Name]".
   b. **Update System:**
      Run the following command for each confirmed event:
      ```bash
      python3 /home/workspace/N5/scripts/luma_email_helper.py --approve-by-title "<Event Title>"
      ```

3. **Report**
   Summarize which events were confirmed.

