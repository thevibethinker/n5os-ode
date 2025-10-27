# VC Survey - Build Instructions for Tally UI

**Form ID**: wLAXN2  
**Edit URL**: https://tally.so/forms/wLAXN2/edit  
**Public URL**: https://tally.so/r/wLAXN2

---

## Form Setup

**Title**: VC Workflow Survey  
**Description**: 3-minute survey about your biggest productivity bottlenecks. If we can help, I'll show you what we're building.

---

## Questions to Add (in order)

### Q1: Email Management
**Type**: Multiple Choice (Single Select)  
**Question**: "How many inboxes do you actively manage?"  
**Required**: Yes

**Options**:
- 1 inbox
- 2-3 inboxes
- 4-5 inboxes
- 6+ inboxes

**Note**: 4+ inboxes = high qualification signal (Gabi's pain point)

---

### Q2: Email Triage Pain
**Type**: Linear Scale  
**Question**: "How often do you miss important emails because of volume?"  
**Required**: Yes  
**Scale**: 1-5

**Labels**:
- 1 = Rarely/Never
- 5 = Multiple times per day

**Note**: 4-5 = high signal

---

### Q3: Meeting Tasks
**Type**: Checkboxes (Multiple Select)  
**Question**: "Which meeting-related tasks eat up your time? (Select all)"  
**Required**: No (allow 0 selections)

**Options**:
- Writing follow-up emails
- Extracting action items from notes
- Remembering context from past conversations
- Preparing for meetings (research/briefing)
- Tracking deliverables across meetings
- None of these

**Note**: 3+ selections = high signal

---

### Q4: Investment Workflow
**Type**: Multiple Choice (Single Select)  
**Question**: "What slows down your investment process most?"  
**Required**: Yes

**Options**:
- Finding/synthesizing past deal patterns
- Writing investment memos
- Coordinating IC approvals
- Managing pipeline/CRM tracking
- Due diligence research
- Other

**Note**: First 2 options = high signal

---

### Q5: CRM Pain
**Type**: Linear Scale  
**Question**: "How painful is tracking startup interactions?"  
**Required**: Yes  
**Scale**: 1-5

**Labels**:
- 1 = Not painful, have good system
- 5 = Major bottleneck

**Note**: 4-5 = high signal

---

### Q6: Time Drains
**Type**: Matrix (if available) OR Multiple Checkboxes  
**Question**: "How often do these slow you down?"

**If Matrix available**:
- **Rows**: Can't find past context | Email triage | Meeting prep | Memo writing | CRM updates
- **Columns**: Never | Rarely | Weekly | Daily | Multiple/day

**If Matrix NOT available, use Checkboxes instead**:
- **Question**: "Which of these slow you down daily or more? (Select all)"
- **Options**:
  - Can't find past context fast enough
  - Email triage/inbox management
  - Meeting prep and follow-up
  - Investment memo writing
  - CRM/pipeline updates
  - None of these

**Note**: 3+ "Daily" or multiple/day = high signal

---

### Q7: Tool Budget
**Type**: Multiple Choice (Single Select)  
**Question**: "Monthly budget for productivity tools?"  
**Required**: Yes

**Options**:
- $0 (don't pay for tools)
- $1-50
- $50-150
- $150-300
- $300+

**Note**: $150+ = moderate/high signal

---

### Q8: Decision Authority
**Type**: Multiple Choice (Single Select)  
**Question**: "Who decides on new productivity tools at your firm?"  
**Required**: Yes

**Options**:
- I decide
- I strongly influence the decision
- Team decides together
- Someone else decides
- We don't adopt new tools

**Note**: First 2 options = high signal

---

### Q9: Willingness to Pay
**Type**: Multiple Choice (Single Select)  
**Question**: "What would you pay monthly for AI that knows every deal you've seen, drafts in your voice, never forgets context?"  
**Required**: Yes

**Options**:
- $0 (wouldn't use it)
- $50/month
- $100/month
- $200/month
- $300+/month

**Note**: $200+ = high signal

---

### Q10: Contact Info

**Name**:
- **Type**: Short Text
- **Question**: "Name"
- **Required**: No (optional)

**Email** (ALREADY EXISTS):
- **Type**: Email
- **Question**: "Email"
- **Required**: Yes

**LinkedIn**:
- **Type**: Short Text
- **Question**: "LinkedIn profile (optional)"
- **Required**: No
- **Placeholder**: "linkedin.com/in/..."

---

## Closing Message

**Add a closing screen with**:

```
Thanks for your time!

If your workflow has the problems we solve, I'll reach out with early access to N5OS.

Want to learn more now? Join the waitlist:
https://n5-waitlist-va.zocomputer.io/

— V
```

---

## Lead Scoring (for your reference)

**HIGH PRIORITY (20-25 points)**:
- Q1: 4-5 inboxes (4 pts)
- Q2: Scale 4-5 (3 pts)
- Q3: 3+ checked (3 pts)
- Q4: First 2 options (3 pts)
- Q5: Scale 4-5 (3 pts)
- Q6: 3+ Daily+ (4 pts)
- Q7: $150+ (2 pts)
- Q8: I decide (2 pts)
- Q9: $200+ (3 pts)

**MODERATE (12-19 points)**: Nurture  
**WEAK (<12 points)**: Newsletter only

---

## Design Notes

- Keep it clean and minimal
- Mobile-friendly
- Progress bar visible
- No branching logic needed (keep linear)
- All questions on one page if possible
- Use Tally's default styling (don't overthink design)

---

## After Building

1. Test the form yourself
2. Check mobile view
3. Submit a test response to verify data capture
4. Share the public URL with me for final review

---

*Created: 2025-10-26 21:08 ET*  
*Based on: Gabi's workflow pain points + Tally UI capabilities*
