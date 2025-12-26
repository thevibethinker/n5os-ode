---
created: 2025-12-04
last_edited: 2025-12-04
version: 1.0
---

# Daily Newsletter Scan & SMS Delivery Setup

## Overview

A fully automated workflow that scans your Gmail inbox for newsletters and articles received in the past 24 hours, then delivers a concise digest via SMS at 9:00 AM ET.

**Status:** ✅ Active and running  
**Schedule:** Daily at 9:00 AM ET  
**Delivery Method:** SMS  
**Next Run:** 2025-12-05 at 9:00 AM ET

---

## How It Works

### Step 1: Gmail Query (Automatic)
- Searches for emails with "newsletter" or "article" keywords
- Looks back 24 hours from the scheduled run time
- Retrieves up to 20 emails
- Filters by sender domains and subject lines

### Step 2: Analysis & Extraction
For each newsletter found:
- **Title/Subject:** Full email subject line
- **Sender:** Clean sender name (removes email address)
- **Insight:** 1-2 sentence summary of key content
- **Timestamp:** When the email was received

### Step 3: Digest Formatting
Creates a concise SMS message (max 1000 characters):
```
📰 Newsletter Digest - Dec 4

• LinkedIn's CPO on Full Stack Builders (Lenny's Newsletter)
  AI transforming product management roles and team structures
• Product Updates & Feature Releases (ProductHunt Digest)
  New AI tools hitting 1M+ users in weeks
• Weekly Tech News (TechCrunch)
  Market trends in autonomous systems and enterprise AI
```

### Step 4: SMS Delivery
- Sends formatted digest directly to your phone
- Arrives before your morning schedule
- Easy scanning of newsletter headlines
- Links and deeper reading available in original emails

---

## What Gets Included

The scan automatically captures:

✅ **Newsletter Services**
- Lenny's Newsletter
- ProductHunt
- TechCrunch
- Substack newsletters
- Industry digests

✅ **Email Features**
- Articles and curated lists
- Product updates
- Newsletter digests
- Research summaries

❌ **Excluded**
- Promotional emails
- Marketing campaigns
- System notifications
- Personal messages

---

## Customization Options

### Adjust Search Criteria
To modify what newsletters are included, edit the Gmail query in the scheduled task:

**Current Query:** `newsletter OR article`

**Other Options:**
- `from:newsletter@substack.com` - Substack only
- `subject:"Newsletter"` - Subject line specific
- `before:2025-12-04 after:2025-12-03` - Specific date range

### Change Delivery Time
Default: 9:00 AM ET

To adjust timing:
1. Go to [Agents](/agents)
2. Find "Daily Newsletter Scan"
3. Edit schedule using RRULE format:
   - `FREQ=DAILY;BYHOUR=8;BYMINUTE=0` for 8:00 AM
   - `FREQ=DAILY;BYHOUR=17;BYMINUTE=30` for 5:30 PM

### Limit Number of Articles
Default: Top 10 articles per SMS

Edit the digest generation to show more/fewer articles:
- 5 articles: More concise, focused
- 10 articles: Comprehensive overview
- 15+ articles: Split across multiple SMS

---

## Integration with Your Workflow

### Timing with Other Tasks
- **9:00 AM:** Newsletter Digest (SMS)
- **10:00 AM:** Meeting Prep Generation (separate agent)
- **17:30:** Evening wrap-up (if configured)

### Data Flow
```
Gmail → Filter Newsletters → Extract Info → Format SMS → Send
  ↓          ↓                   ↓             ↓        ↓
Every 24h  Keep last 24h    Key details    <1000 ch  Your phone
```

---

## Settings & Configuration

### Email Address
- Connected Gmail: `vrijen@mycareerspan.com`
- SMS Delivery: Phone number on file in SMS settings

### Search Scope
- Time Range: Last 24 hours
- Max Results: 20 emails
- Filter Type: Content-based

### Output Format
- **Length:** Under 1000 characters
- **Structure:** Bullet points with sender
- **Emoji:** Newsletter indicator (📰)
- **Timestamp:** Date included in digest

---

## Troubleshooting

### Not Receiving SMS?

1. **Check Gmail Connection**
   - Verify settings at [Integrations](/settings#integrations)
   - Gmail must be connected and authorized

2. **Check SMS Settings**
   - Phone number configured in SMS integrations
   - SMS service active and funded

3. **Check Search Results**
   - Your newsletters may not match the search query
   - Try broader search terms if getting no results

### Too Many or Too Few Articles?

1. Adjust the Gmail search query
2. Modify `maxResults` parameter (currently 20)
3. Edit filtering logic in scheduled task

### Wrong Time Zone?

The schedule uses your account timezone (currently America/New_York).
To change:
1. Go to [Settings](/settings)
2. Update timezone setting
3. Schedule will automatically adjust

---

## Advanced Usage

### Combining with Other Tools

You can create follow-up workflows using this digest:

1. **Automatic Archiving**
   - Mark processed newsletters as read
   - Apply labels (e.g., "Scanned")

2. **Email Follow-ups**
   - Send follow-up emails with full articles
   - Create filtered collection of key insights

3. **Data Collection**
   - Log digest contents to database
   - Track newsletter frequency
   - Analyze topics over time

### Manual Execution

To run the newsletter scan manually at any time:
1. Go to [Agents](/agents)
2. Click "Daily Newsletter Scan"
3. Click "Run Now" button

---

## Related Workflows

**Other Scheduled Tasks:**
- Meeting Prep Generation (10:00 AM)
- Day-end Summary (6:00 PM)

**Related Settings:**
- [Gmail Integration](/settings#integrations)
- [SMS Setup](/settings#integrations)
- [Timezone](/settings)

---

## How to Modify

### Edit the Schedule
1. Navigate to [Agents](/agents)
2. Find "Daily Newsletter Scan"
3. Click edit icon
4. Modify the RRULE (RFC 5545 format)

### Edit the Instructions
Update the Gmail query and SMS formatting by editing the task instruction.

### Run Immediately
Click "Run Now" to execute immediately without waiting for 9:00 AM.

---

## Questions?

For detailed help:
- Check Gmail integration status at [Integrations](/settings#integrations)
- Review SMS settings configuration
- Contact support via [Report an issue](/issue-report)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-04 | Initial setup and configuration |


