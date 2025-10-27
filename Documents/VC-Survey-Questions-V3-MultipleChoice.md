# VC Survey Questions - V3 (Multiple Choice Design)

**Based on**: Gabi's actual pain points (5 inboxes, meeting overload, CRM chaos, investment memo workflow)

**Design Pattern**: Minimize free response, maximize multiple choice/scales/matrices

---

## Survey Structure

### Opening
**Title**: "VC Workflow Survey"  
**Description**: "3-minute survey to understand your biggest productivity bottlenecks. If we can help, we'll show you what we're building."

---

## Questions

### Q1: Email Pain (MULTIPLE CHOICE - Single Select)
**Question**: "How many inboxes do you actively manage?"

**Options**:
- 1 inbox
- 2-3 inboxes
- 4-5 inboxes ⭐ (Gabi's pain point)
- 6+ inboxes

**Qualification**: 4+ = HIGH signal

---

### Q2: Email Triage Problem (SCALE 1-5)
**Question**: "How often do you miss important emails because of volume?"

**Scale**: 
- 1 = Rarely/Never
- 2 = Occasionally
- 3 = Weekly
- 4 = Daily ⭐
- 5 = Multiple times per day

**Qualification**: 4-5 = HIGH signal

---

### Q3: Meeting Intelligence (CHECKBOXES - Multiple Select)
**Question**: "Which meeting-related tasks eat up your time? (Select all)"

**Options**:
- [ ] Writing follow-up emails
- [ ] Extracting action items from notes
- [ ] Remembering context from past conversations ⭐
- [ ] Preparing for meetings (research/briefing)
- [ ] Tracking deliverables across meetings
- [ ] None of these

**Qualification**: 3+ checked = HIGH signal

---

### Q4: Investment Workflow Bottleneck (MULTIPLE CHOICE - Single Select)
**Question**: "What slows down your investment process most?"

**Options**:
- Finding/synthesizing past deal patterns ⭐ (Gabi's need)
- Writing investment memos
- Coordinating IC approvals
- Managing pipeline/CRM tracking
- Due diligence research
- Other

**Qualification**: First 2 options = HIGH signal

---

### Q5: CRM Pain Scale (SCALE 1-5)
**Question**: "How painful is tracking startup interactions?"

**Scale**:
- 1 = Not painful, have good system
- 2 = Manageable
- 3 = Sometimes frustrating
- 4 = Regularly painful ⭐
- 5 = Major bottleneck

**Qualification**: 4-5 = HIGH signal

---

### Q6: Time Drain Matrix (MATRIX - Frequency Rating)
**Question**: "How often do these slow you down?"

**Rows** (Tasks):
- Can't find past context fast enough
- Email triage/inbox zero
- Meeting prep and follow-up
- Investment memo writing
- CRM/pipeline updates

**Columns** (Frequency):
- Never
- Rarely
- Weekly
- Daily
- Multiple/day

**Qualification**: 3+ "Daily" or "Multiple/day" = HIGH signal

---

### Q7: Tool Budget (MULTIPLE CHOICE - Single Select)
**Question**: "Monthly budget for productivity tools?"

**Options**:
- $0 (don't pay for tools)
- $1-50
- $50-150
- $150-300 ⭐
- $300+

**Qualification**: $150+ = MODERATE/HIGH signal

---

### Q8: Decision Authority (MULTIPLE CHOICE - Single Select)
**Question**: "Who decides on new productivity tools?"

**Options**:
- I decide ⭐
- I strongly influence
- Team decides together
- Someone else decides
- We don't adopt new tools

**Qualification**: First 2 = HIGH signal

---

### Q9: Willingness to Pay (MULTIPLE CHOICE - Single Select)
**Question**: "What would you pay for AI that knows every deal you've seen, drafts in your voice, never forgets context?"

**Options**:
- $0 (wouldn't use it)
- $50/month
- $100/month
- $200/month ⭐
- $300+/month

**Qualification**: $200+ = HIGH signal

---

### Q10: Contact (TEXT + EMAIL)
**Name**: Short text (optional)  
**Email**: Required  
**LinkedIn**: Short text (optional)

---

## Scoring System

**HIGH (20-25 points)**:
- Q1: 4-5 inboxes (4 pts)
- Q2: Scale 4-5 (3 pts)
- Q3: 3+ checked (3 pts)
- Q4: First 2 options (3 pts)
- Q5: Scale 4-5 (3 pts)
- Q6: 3+ Daily+ (4 pts)
- Q7: $150+ (2 pts)
- Q8: I decide (2 pts)
- Q9: $200+ (3 pts)

**MODERATE (12-19 points)**: Warm lead  
**WEAK (<12 points)**: Newsletter only

---

## Why This Works

**Based on Gabi's Pain Points**:
1. ✅ 5 inboxes = highest pain (Q1, Q2)
2. ✅ Meeting overload (Q3, Q6)
3. ✅ CRM chaos (Q5, Q6)
4. ✅ Finding past deal context (Q4, Q6)
5. ✅ Investment memo workflow (Q4)

**Fast to Complete**:
- No long text boxes
- Click-through design
- 2-3 minutes max

**Qualification Built-In**:
- Budget questions
- Decision authority
- Pain intensity scales
- Willingness to pay

---

## Next Steps

**PROBLEM**: Tally API doesn't render multiple choice options properly

**OPTIONS**:
1. Build this manually in Tally UI using their form builder
2. Debug API issue (figure out missing field/structure)
3. Use different form tool (Typeform, Google Forms)

**RECOMMENDATION**: Build manually in Tally UI - it's faster than debugging API

---

*Created: 2025-10-26 21:05 ET*  
*Based on: Gabi's Executive Summary + Tally API learnings*
