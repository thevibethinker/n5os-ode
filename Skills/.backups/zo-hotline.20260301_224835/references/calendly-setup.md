---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: hotline-enhancement-v3 build (D1.3)
---

# Calendly Event Type Setup — Zo Hotline

This guide walks you through creating the Calendly event type for the Zo Hotline escalation flow.

## Overview

The hotline webhook automatically offers escalation to a 15-minute call with you when:
- Users explicitly request to talk to you
- The system can't help them after multiple attempts
- Context suggests a human conversation would be valuable

The webhook reads the booking link from the `ZO_HOTLINE_CALENDLY_LINK` environment variable. Once you create the event type and set this env var, escalation will work automatically — no code changes needed.

---

## Step 1: Create the Event Type

1. Go to [Calendly Event Types](https://calendly.com/event_types)
2. Click **+ Create** → **One-on-One**
3. Configure as follows:

### Basic Settings

| Field | Value |
|-------|-------|
| **Event name** | `Zo Hotline — Quick Chat with V` |
| **Duration** | 15 minutes |
| **Location** | Google Meet (or Zoom, your preference) |
| **Description** | `A focused 15-minute session with V to help you with a specific question or task. Come prepared — this is for tactical problem-solving, not open-ended exploration.` |

### Availability

| Field | Value |
|-------|-------|
| **Days** | Monday - Friday only |
| **Hours** | 12:00 PM - 4:00 PM Eastern Time |
| **Daily limit** | Max 2 bookings per day |
| **Buffer time** | 5 minutes before and after |
| **Minimum notice** | 4 hours (prevents same-day panic bookings) |
| **Rolling window** | 2 weeks out (don't let people book a month ahead) |

**How to set daily limits:**
- Under "Availability" → "Date Range" → "Invitees can schedule" → Set to "2 weeks into the future"
- Under "Limits" → "Maximum bookings per day" → Set to **2**

### Invitee Questions

Add these custom questions:

1. **What's your name?**
   - Type: Short text
   - Required: Yes

2. **What do you need help with?**
   - Type: Paragraph text
   - Required: Yes
   - Placeholder: "Be specific. What problem are you trying to solve?"

3. **How did you find the hotline?**
   - Type: Dropdown
   - Required: No
   - Options:
     - Twitter
     - LinkedIn
     - Word of mouth
     - Other

### Notifications & Confirmation

**Confirmation page message:**
```
You're booked! V will meet you at the scheduled time.

Come with a specific question or task in mind — this is a focused 15-minute session. The more prepared you are, the more value you'll get.

See you soon.
```

**Email reminders:**
- Use Calendly defaults (24 hours before + 1 hour before)
- Customize if you prefer different timing

### Save

Click **Save & Close** when done.

---

## Step 2: Copy the Booking URL

1. On the Event Types page, find your new event type
2. Click **Copy Link** (or click the event → "Share" tab → copy the link)
3. It will look like: `https://calendly.com/your-username/zo-hotline-15min`

---

## Step 3: Set the Environment Variable

1. Go to [Zo Settings → Advanced](https://zo.space/settings/advanced)
2. Find **Environment Variables** section
3. Add or update:
   - **Variable name:** `ZO_HOTLINE_CALENDLY_LINK`
   - **Value:** `<paste the URL you just copied>`
4. Save changes

---

## Step 4: Restart the Webhook Service

The webhook needs to reload the new env var:

```bash
# SSH into your Zo Computer
ssh zo

# Restart the hotline webhook service
supervisorctl restart zo-hotline-webhook
```

Or use the Zo web UI to restart the service if you prefer.

---

## Step 5: Test the Flow

1. Call the hotline: **+1-732-490-2074**
2. When the assistant answers, say something like:
   - "I need to talk to V"
   - "Can I schedule a call with you?"
   - "I have a question that needs a human"
3. The system should offer you the Calendly link via SMS

**Expected SMS:**
> "I'd love to connect with you. Book a 15-minute call here: [your Calendly link]. I'm available weekdays 12-4pm ET."

---

## Verification Checklist

After setup, confirm:

- [ ] Event type created in Calendly
- [ ] Booking link copied
- [ ] `ZO_HOTLINE_CALENDLY_LINK` env var set in Zo Settings
- [ ] Webhook service restarted
- [ ] Test call confirms escalation works
- [ ] Calendly booking confirmation email arrives as expected

---

## Maintenance Notes

**If you need to change the link later:**
1. Update the Calendly event type settings (or create a new one)
2. Copy the new URL
3. Update `ZO_HOTLINE_CALENDLY_LINK` in Zo Settings
4. Restart the webhook service

**No code changes required** — the webhook automatically reads from the env var.

---

## Technical Context (For Reference)

The escalation logic lives in `requestEscalation()` function in `/home/workspace/Skills/zo-hotline/scripts/hotline-webhook.ts` (line 431). It reads the env var like this:

```typescript
const calendlyLink = process.env.ZO_HOTLINE_CALENDLY_LINK ||
  'https://calendly.com/v-at-careerspan/zo-hotline-15min';
```

Once the env var is set, the webhook uses it automatically. The default placeholder link is there as a fallback.

---

**Questions?** This is a one-time setup. Once complete, escalations will work seamlessly.
