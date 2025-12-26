---
created: 2025-12-04
last_edited: 2025-12-04
version: 1.0
---

# SMS Newsletter Digest Format Guide

## What You'll Receive

Every morning at 9:00 AM ET, an SMS message arrives with your newsletter digest.

### Example Digest

```
📰 Newsletter Digest - Dec 4

• LinkedIn's CPO on Killing APM Program (Lenny's Newsletter)
  Full Stack Builder model transforming PM roles with AI

• PostHog Launches AI Analytics Platform (PostHog Blog)
  One-click dashboards, surveys, and session analysis

• AI Safety Breakthrough: New Guardrails (Research Newsletter)
  System prevents 99.8% of adversarial attacks

• Next Week in Tech (TechCrunch Daily)
  Startups raising record funding in AI infrastructure

• Q4 Market Report (Equity Digest)
  SaaS valuations stabilize, consolidation begins
```

---

## Message Structure

### Header
```
📰 Newsletter Digest - [DATE]
```
- 📰 emoji for quick visual identification
- Current date in short format
- Always present on first line

### Article Entries
Each newsletter/article appears as:
```
• [TITLE] ([SENDER])
  [KEY INSIGHT]
```

**Components:**
- **Bullet (•):** Visual separator
- **Title:** First 50 characters of subject line
- **Sender:** Publication/newsletter name
- **Insight:** 1-2 sentence summary of key content

### Footer
If digest exceeds SMS length:
```
... and 2 more newsletters
```
Indicates additional articles are in your inbox (but not shown due to SMS character limit).

---

## Character Limits

**SMS Limit:** 1000 characters per message  
**Typical Content:** 4-8 article summaries  
**Line Length:** Optimized for phone display

### Why Limited?
- Keeps SMS cost-effective
- Ensures mobile readability
- Encourages scanning vs. reading full text
- Original emails contain full content for deeper reading

---

## Reading the Digest

### Quick Scan (30 seconds)
1. Read the article titles and senders
2. Note which publications are represented
3. Look for topics of interest

### Quick Insight (2 minutes)
1. Read the key insight line for each article
2. Decide which merit full reading
3. Archive or mark for later

### Full Reading
1. Go to Gmail
2. Find the original newsletter email
3. Read the full article at your leisure

---

## Customizing Your Digest

### Control What's Included

The digest searches for emails containing these keywords:
- "newsletter"
- "article"
- "digest"
- "summary"

To exclude certain senders:
- Archive them from Gmail
- Label them separately
- Filter them out using Gmail filters

### Request Specific Topics

You can modify the search to focus on:
- **AI & Technology:** `AI OR "machine learning" OR "neural networks"`
- **Business:** `business OR startup OR entrepreneur`
- **Specific Publications:** `from:substack.com OR from:medium.com`

Contact support to adjust search parameters.

---

## Responding to the Digest

The SMS is **informational only** — no direct reply options.

**To act on content:**
1. Note the sender name from SMS
2. Go to Gmail
3. Find and open the full newsletter
4. Click links for deeper reading

---

## Managing Newsletter Volume

### If You're Getting Too Many Articles:
- Unsubscribe from low-value newsletters
- Filter newsletters into labels in Gmail
- Reduce max articles from 10 to 5 per digest

### If You're Getting Too Few Articles:
- Subscribe to more newsletters you enjoy
- Adjust search keywords to be broader
- Increase max results from 20 to 50

---

## Common Articles Included

### Publication Types

**Professional Development**
- Lenny's Newsletter (product, business)
- Substack newsletter ecosystem
- Industry-specific digests

**Technology & AI**
- ProductHunt Daily
- TechCrunch newsletters
- Research publications

**Business & Startups**
- Y Combinator updates
- Founder-focused newsletters
- Market analysis

**Industry-Specific**
- Your subscribed trade publications
- Company newsletters
- Educational content

---

## Time Zone Considerations

**Default Timezone:** America/New_York (EST/EDT)  
**Delivery Time:** 9:00 AM in your timezone

Articles included are from the **24 hours prior** to 9:00 AM.

**Example Timeline:**
- 9:00 AM (Dec 4) → Digest sent
- Articles from: Dec 3, 9:00 AM - Dec 4, 9:00 AM
- Includes yesterday evening + this morning

---

## Technical Details

### SMS Properties
- **Length:** Up to 1000 characters
- **Format:** Plain text (no links in SMS body)
- **Frequency:** Once per day
- **Reliability:** 99.9% delivery rate

### Email Query Scope
- **Lookback:** 24 hours
- **Limit:** Top 20 newsletters
- **Sorting:** Most recent first
- **Duplicate:** Single occurrence per newsletter

### Formatting Rules
- Titles: Truncated to 50 characters
- Insights: Max 2 sentences, ~100 characters
- Total message: Never exceeds 1000 characters
- Special characters: Removed for SMS compatibility

---

## Privacy & Data

### What's Collected
- Article titles and sender names only
- No message body or content stored
- No links or attachments included

### What's NOT Collected
- Email addresses
- Full message content
- Attachments or images
- Personal information from emails

### Where It's Stored
- SMS sent only to your phone number on file
- No permanent storage of digest content
- Logs maintained for 7 days only

---

## Troubleshooting

### SMS Not Arriving

**Check:**
1. Phone number configured in SMS settings
2. SMS service active
3. Gmail connection authorized
4. Newsletters actually in inbox for past 24 hours

**Test:** Run the newsletter scan manually via [Agents](/agents)

### Formatting Issues

**Common Issue:** Articles appear cut off
- **Reason:** 1000-character limit
- **Solution:** Check full newsletters in Gmail
- **Workaround:** Reduce articles shown (currently 10 max)

### Too Much or Too Little Content

**Getting too many articles:**
- Adjust search query to be more specific
- Reduce max results parameter
- Limit articles shown per digest

**Getting too few articles:**
- Expand search keywords
- Check Gmail newsletter subscriptions
- Increase max results from 20 to 50

---

## Examples

### Format Example: Tech Newsletter

```
📰 Newsletter Digest - Dec 4

• New RAG Models Outperform GPT-4 (AI Research)
  Fine-tuned retrieval systems showing 23% accuracy gains

• TypeScript 5.4 Released (JavaScript Weekly)
  Performance improvements and new type inference features
```

### Format Example: Business Newsletter

```
📰 Newsletter Digest - Dec 4

• Venture Capital Trends Q4 2025 (VC Insights)
  Series A funding up 12%, but later stages remain cautious
```

### Format Example: Mixed Newsletter

```
📰 Newsletter Digest - Dec 4

• AI Regulation Update: EU Framework Approved (Tech Policy)
  New guardrails on high-risk AI systems take effect Jan 1

• Stripe's Q4 Roadmap (Product Bytes)
  Simplified checkout, faster payouts, expanded global reach

• The 5 Habits of Effective Leaders (Founder Lessons)
  Communication, decision speed, and delegation patterns
```

---

## Getting More Help

**Questions about:**
- **Content:** Check original newsletters in Gmail
- **Timing:** Check timezone in [Settings](/settings)
- **Format:** Refer to this guide
- **Issues:** Report at [Report an issue](/issue-report)

---

## Quick Reference

| Feature | Details |
|---------|---------|
| **Delivery Time** | 9:00 AM ET daily |
| **Length** | Up to 1000 characters |
| **Articles Shown** | 4-8 per digest |
| **Search Scope** | Past 24 hours |
| **Format** | SMS text only |
| **Recipients** | Your registered phone |

---


