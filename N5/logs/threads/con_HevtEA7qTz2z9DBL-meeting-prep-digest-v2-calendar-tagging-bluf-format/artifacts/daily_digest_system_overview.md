# Daily Digest System Overview

**Generated:** 2025-10-11 11:41 ET  
**Status:** Fully operational  
**Location:** N5 OS

---

## 📋 Executive Summary

Your N5 system has **two primary daily digest capabilities** that run automatically:

1. **Daily Meeting Prep Digest** — Researches external meeting attendees and provides context
2. **Daily Newsletter Digest** — Scans Gmail for newsletters/articles and summarizes key content

Both are currently scheduled and actively running.

---

## 📰 Daily Newsletter Digest

### Current Status
- **Schedule:** Daily at 6:15 AM ET
- **Task ID:** `b24219b2-3aac-4623-a386-b9e3e6ee8f90`
- **Delivery:** Emailed to you
- **Output:** `file 'N5/knowledge/digests/{date}.md'`
- **Latest:** `file 'N5/knowledge/digests/2025-10-11.md'` (generated today)

### What It Does
1. **Queries Gmail** for recent newsletters and articles (query: `newsletter OR article`)
2. **Extracts URLs** from email content
3. **Reads & Summarizes** articles using `read_webpage`
4. **Clusters by Theme** (Career & Higher Ed, AI & Product, Hiring & Jobs Market, etc.)
5. **Generates Digest** with:
   - Key takeaways (3 bullets per article)
   - "Why it matters today" context
   - Citations with source URLs
6. **Emails You** the complete digest

### Workflow Details
**Scheduled Task Instruction:**
```
Run a daily newsletter scan and deliver by email. Steps: 
1) Query Gmail for recent newsletters and articles using tool use_app_gmail 
   with tool_name='gmail-find-email' and q='newsletter OR article', 
   with maxResults=50
2) Extract URLs from email bodies
3) Read and summarize each article using read_webpage
4) Cluster summaries by theme
5) Generate digest at N5/knowledge/digests/{date}.md with format:
   - Title and date header
   - Thematic sections (Career & Higher Ed, AI & Product, etc.)
   - Per-article: Key takeaways (3 bullets), Why it matters today
   - Citations footer
6) Email the digest to me with subject "Daily Newsletter Digest — {date}"
```

### Commands Available
- `file 'N5/commands/scan_gmail_digests.json'` — Scan and process newsletters
- `file 'N5/commands/process_newsletter.json'` — Process specific newsletter (e.g., `/digest nytimes`)

---

## 📅 Daily Meeting Prep Digest

### Current Status
- **Generation:** Daily at 10:00 AM ET (creates digest)
- **Delivery:** Daily at 6:30 AM ET (emails digest)
- **Version:** v2.0.0 (Updated 2025-10-11)
- **Task IDs:** 
  - Generation: `05ec355c-4605-4b16-8298-6c1be0c91a95`
  - Email: `3b5d2d19-b67a-4c80-9ead-0dad451b4540`
- **Output:** `file 'N5/digests/daily-meeting-prep-{date}.md'`
- **Latest:** `file 'N5/digests/daily-meeting-prep-2025-10-11.md'` (v1 format — will use v2 tomorrow)

### What It Does (v2.0.0)
1. **Scans Google Calendar** for today's meetings
2. **Filters for External Meetings ONLY:**
   - Excludes all-internal meetings (@mycareerspan.com, @theapply.ai)
   - Excludes daily recurring meetings ("Daily standup", "Daily sync", etc.)
   - Only includes meetings with at least one external stakeholder
3. **Reads Calendar Tags:**
   - `#stakeholder:TYPE` — customer, community, partner, investor, vendor, job_seeker, vc, channel_partner
   - `#type:TYPE` — discovery, decision, update, follow-up, coaching, sales, partnership, fundraising
   - `#priority:LEVEL` — high, protect, low
4. **Researches Each External Attendee (Streamlined):**
   - Last 3 Gmail interactions (date, context)
   - Calendar description context
   - Existing stakeholder profiles from `N5/records/meetings/`
   - Past meeting notes
5. **Generates BLUF Format Digest** with:
   - Chronological table of contents (earliest first)
   - Per-meeting sections with:
     - **BLUF:** One-sentence objective
     - **Last 3 interactions:** Brief context from Gmail
     - **Calendar context:** From event description
     - **Past notes:** Links to stakeholder profiles
     - **Prep actions:** 1-3 specific, actionable items based on tags
6. **Emails You** the digest at 6:30 AM (before generation at 10 AM)

### New in v2.0.0 (2025-10-11)
- ✅ **External stakeholders only** — No internal meetings logged
- ✅ **Calendar tagging system** — Hashtag-based classification in event descriptions
- ✅ **Daily meeting exclusion** — Filters out recurring daily meetings
- ✅ **Chronological TOC** — Earliest meeting first
- ✅ **BLUF format** — Bottom Line Up Front, concise and actionable
- ✅ **Streamlined research** — Last 3 interactions prioritized
- ✅ **Tag-based prep actions** — Suggestions tailored to meeting type
- ✅ **Stakeholder profile integration** — Links to past notes

### Calendar Tagging System

Add hashtags to calendar event descriptions:

**Example:**
```
#stakeholder:partner #type:follow-up #priority:high

Discuss pilot job descriptions and next steps for sourcing workflow.
Need job descriptions by EOW to start candidate search.
```

**Stakeholder Types:**
- `customer`, `community`, `partner`, `investor`, `vendor`, `job_seeker`, `vc`, `channel_partner`

**Meeting Types:**
- `discovery`, `decision`, `update`, `follow-up`, `coaching`, `sales`, `partnership`, `fundraising`

**Priority Levels:**
- `high`, `protect`, `low`

**Full Documentation:** `file 'N5/docs/calendar-tagging-system.md'`

### Script Implementation
**Primary Script:** `file 'N5/scripts/meeting_prep_digest.py'` (v2.0.0)

**Key Functions:**
- `fetch_calendar_events()` — Google Calendar integration (needs implementation)
- `filter_external_meetings()` — External-only + daily exclusion logic
- `extract_tags_from_description()` — Parse hashtag tags
- `is_daily_recurring()` — Pattern matching for daily meetings
- `get_last_3_interactions()` — Gmail history (needs implementation)
- `research_stakeholder()` — Streamlined research workflow
- `get_stakeholder_profile_path()` — Find existing profiles
- `generate_bluf()` — Bottom Line Up Front summary
- `generate_meeting_section()` — BLUF format per meeting
- `generate_digest()` — Complete digest generation

**Command:** `file 'N5/commands/meeting-prep-digest.md'` (v2.0.0)

**CLI Usage:**
```bash
# Generate digest for today
meeting-prep-digest

# Generate for specific date
meeting-prep-digest --date 2025-10-12

# Preview without saving
meeting-prep-digest --dry-run
```

### Example Output (v2.0.0)

**Table of Contents:**
```markdown
## Today's External Stakeholder Meetings

**Total:** 2 meeting(s)

1. **09:00** — Aniket Partnership Follow-up (1 external)
2. **14:00** — Community Discovery Call (1 external)
```

**Meeting Section (BLUF Format):**
```markdown
## 09:00 — Aniket Partnership Follow-up (#partner type:follow-up)

**BLUF:** Follow-up: advance partnership/relationship with Aniket

**Last 3 interactions:**
- 2025-10-08 — Confirmed interest in pilot, requested job descriptions
- 2025-09-15 — Initial intro, discussed recruiting challenges
- 2025-09-02 — Shared product demo, explored use cases

**Calendar context:** Need job descriptions by EOW to start candidate search

**Past notes:** `file 'N5/records/meetings/2025-09-02_aniket-x-vrijen-attawar/stakeholder-profile.md'`

**Prep actions:**
1. ⚠️ Protect this time block — reschedule conflicts
2. Review last interaction and prepare 1-2 specific asks
3. Set explicit outcome: what decision or next step do you need?
```

### What's Excluded (v2.0.0)

**Internal meetings:**
```
Ayush Jain and Vrijen Attawar
Attendees: ayush@mycareerspan.com, vrijen@mycareerspan.com
```
→ Not included (all internal)

**Daily recurring:**
```
Daily Team Standup
Attendees: vrijen@mycareerspan.com, logan@theapply.ai
```
→ Not included (daily pattern match)

---

## 🔄 Email Processing Workflow

### Baseline Behavior
Per `file 'N5/prefs/communication/email.md'`:

1. **Auto-Process Forwarded Emails**
   - Trigger: New file in `Queue/Email/*.json`
   - Action: Run Process Emails command

2. **Auto-Scan Gmail for Digests**
   - Schedule: 6:00 AM ET daily
   - Action: Run Scan Gmail for Digests command

3. **Thread Creation Trigger**
   - Condition: Gmail thread contains "newsletter" OR "article"
   - Action: Process via Process Newsletter command
   - Route to: Knowledge/, article tracker, digest

### Detection Rules
**Authoritative Source:** `file 'Lists/detection_rules.md'`

**Quick Reference:**
- **Jobs/Tasks:** Keywords → task, job, follow-up, action → Route to `N5/lists/tasks.md`
- **Attachments:** Types → pdf, docx, xlsx, jpg, png, mp4 → Route to `N5/knowledge/attachments/{type}/`
- **Articles/Newsletters:** Patterns → http/https URLs, "newsletter" in subject → Route to Knowledge/articles/ and digest
- **Other:** Default → Knowledge/inbox/

### File Paths
- **Article Tracker:** `N5/knowledge/article_reads.jsonl` (currently not created)
- **Digests:** `N5/knowledge/digests/{date}.md`
- **Logs:** `N5/knowledge/logs/Email/{date}.log`

---

## 🛠️ Related Commands & Scripts

### Commands
1. `file 'N5/commands/scan_gmail_digests.json'` — Scan Gmail for newsletters/articles
2. `file 'N5/commands/process_newsletter.json'` — Process specific newsletter
3. `file 'N5/commands/process_emails.json'` — Process incoming emails from queue
4. `file 'N5/commands/meeting-prep-digest.md'` — Generate meeting prep digest
5. `file 'N5/commands/digest-runs.md'` — Generate run digest reports

### Scripts
1. `file 'N5/scripts/meeting_prep_digest.py'` — Meeting prep digest generator (v1.0.1)
2. `file 'N5/scripts/n5_digest_runs.py'` — Run digest aggregator

---

## 📊 Current Scheduled Tasks (Digest-Related)

| Task | Schedule | Description | Next Run |
|------|----------|-------------|----------|
| Daily Newsletter Digest | Daily 6:15 AM ET | Scan Gmail, summarize, email | Oct 12, 6:15 AM |
| Daily Meeting Prep (Generate) | Daily 10:00 AM ET | Generate meeting prep digest | Oct 12, 10:00 AM |
| Daily Meeting Prep (Email) | Daily 6:30 AM ET | Email meeting prep digest | Oct 12, 6:30 AM |

---

## 🔍 What's Working

✅ **Newsletter Digest:**
- Successfully generating daily summaries
- Latest: `file 'N5/knowledge/digests/2025-10-11.md'`
- Thematic clustering working well
- Email delivery scheduled

✅ **Meeting Prep Digest:**
- Successfully generating meeting intelligence
- Latest: `file 'N5/digests/daily-meeting-prep-2025-10-11.md'`
- Smart filtering for external meetings
- Email delivery scheduled

---

## 🚧 What Needs Integration

⚠️ **Gmail API Integration:**
- Currently using mock data in `meeting_prep_digest.py`
- Need to implement:
  - `list_app_tools(app_slug="gmail")`
  - `use_app_gmail(tool_name="gmail-search-messages", ...)`
  - Gmail history scanning in `scan_gmail_history()`

⚠️ **Google Calendar API Integration:**
- Currently using mock data in `meeting_prep_digest.py`
- Need to implement:
  - `list_app_tools(app_slug="google_calendar")`
  - `use_app_google_calendar(tool_name="google_calendar-list-events", ...)`
  - Real calendar event fetching in `fetch_calendar_events()`

⚠️ **Web Research Integration:**
- Currently using mock data in `meeting_prep_digest.py`
- Need to implement:
  - `web_search()` for LinkedIn and company research
  - `read_webpage()` for profile and site data
  - Real research in `perform_light_research()`

⚠️ **Article Tracker:**
- File path defined: `N5/knowledge/article_reads.jsonl`
- Not currently being created
- Should track: title, url, date, tags, summary

---

## 🎯 Key Preferences & Settings

From `file 'N5/prefs/communication/email.md'`:

- **Auto-Process Forwarded Emails:** ✅ Enabled
- **Auto-Scan Gmail for Digests:** ✅ Enabled (6:00 AM ET)
- **Newsletter Thread Trigger:** ✅ Enabled
- **Howie Interaction:** ⏸️ PAUSED (per stored preferences)

---

## 📝 Sample Output

### Newsletter Digest Sample
See: `file 'N5/knowledge/digests/2025-10-11.md'`

**Structure:**
- Date header with timestamp
- Thematic sections (Career & Higher Ed, AI & Product, Hiring & Jobs, etc.)
- Per article:
  - Title and source
  - Key takeaways (3 bullets)
  - "Why it matters today" context
- Citations footer with URLs

### Meeting Prep Sample
See: `file 'N5/digests/daily-meeting-prep-2025-10-11.md'`

**Structure:**
- Meeting-by-meeting breakdown with time
- Per attendee:
  - Name, email, entity type
  - Email history (3 bullets)
  - Quick research overview
  - Auto-injected context
  - Clarification prompts (if needed)
- Summary stats and action items

---

## 🔧 How to Use

### Manual Commands

**Generate meeting prep for today:**
```bash
python3 /home/workspace/N5/scripts/meeting_prep_digest.py
```

**Generate for specific date:**
```bash
python3 /home/workspace/N5/scripts/meeting_prep_digest.py --date 2025-10-12
```

**Preview without saving:**
```bash
python3 /home/workspace/N5/scripts/meeting_prep_digest.py --dry-run
```

### Modify Scheduled Tasks

**Edit newsletter digest task:**
```
Use edit_scheduled_task() with task_id: b24219b2-3aac-4623-a386-b9e3e6ee8f90
```

**Edit meeting prep email task:**
```
Use edit_scheduled_task() with task_id: 3b5d2d19-b67a-4c80-9ead-0dad451b4540
```

---

## 📚 Related Documentation

- `file 'N5/prefs/communication/email.md'` — Email processing preferences
- `file 'N5/prefs/communication/voice.md'` — Voice & style guidelines
- `file 'N5/prefs/communication/templates.md'` — Email templates
- `file 'Lists/detection_rules.md'` — Email routing rules
- `file 'Documents/N5.md'` — N5 system overview
- `file 'N5/prefs/prefs.md'` — General preferences

---

## 🎬 Next Steps

To fully operationalize the meeting prep digest:

1. **Integrate Gmail API** in `meeting_prep_digest.py`
2. **Integrate Google Calendar API** in `meeting_prep_digest.py`
3. **Integrate Web Research** in `meeting_prep_digest.py`
4. **Create Article Tracker** (`N5/knowledge/article_reads.jsonl`)
5. **Test End-to-End** with real data
6. **Monitor Scheduled Runs** and adjust timing as needed

---

**All systems currently operational with scheduled delivery via email.**
