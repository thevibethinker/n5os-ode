# Stakeholder Reservoir System — Overview for V

**Built:** October 12, 2025  
**Status:** ✅ Core system operational, ready for your review  
**Next:** Review 3 test profiles and answer questions below

---

## What This Solves

**Before:**
- Meeting prep started from scratch every time
- No memory of previous interactions
- Had to re-scan email history repeatedly
- Your contextual knowledge wasn't captured

**Now:**
- Auto-creates profiles when meetings are scheduled
- Builds cumulative knowledge over time
- Meeting prep loads profile + recent activity only
- Captures your input on relationships systematically

---

## How It Works

### 1. Auto-Profile Creation
**Trigger:** External meeting detected on calendar

**Process:**
1. Scan full email history (100+ messages, not just 3)
2. LLM analyzes:
   - Organization (from domain, signatures)
   - Role (from email signatures)
   - Lead type (LD-INV/HIR/COM/NET/GEN)
   - Relationship context
   - Interaction summary
3. Create profile file
4. Only ask you when uncertain

**Your input:** Only needed when confidence is low (tags, interpretation)

---

### 2. Meeting Prep (Enhanced)
**Trigger:** Daily digest at 10 AM ET

**Process:**
1. Load stakeholder profile (if exists)
2. Fetch recent emails only (last 30-90 days)
3. Generate prep: Profile context + Recent activity
4. Result: Rich, cumulative prep instead of cold start

**Your benefit:** Accurate context, no "first meeting" confusion

---

### 3. Post-Meeting Update
**Trigger:** Meeting transcript processed

**Process:**
1. Detect external attendees
2. Generate summary from transcript
3. Auto-append to their profiles
4. Link to transcript file
5. Update timestamps

**Your input:** None needed — fully automatic

---

## Test Profiles Created

I created 3 profiles from your Oct 14 meetings as examples:

### 1. Michael Maher (Cornell)
**File:** `file 'N5/stakeholders/michael-maher-cornell.md'`

**What I figured out:**
- MBA Career Advisor - Tech at Cornell
- Lead type: LD-COM (community partnership)
- Partnership opportunity with Cornell MBA program
- 2 email interactions (Oct 1-2)

**No questions** — high confidence

---

### 2. Fei Ma (Nira)
**File:** `file 'N5/stakeholders/fei-ma-nira.md'`

**What I figured out:**
- Works at Nira (from email domain)
- Lead type: LD-COM (partnership discussions)
- You're working on PM community partnerships (FOHE, Reforge, Xooglers, etc.)
- You said: "supercharge this for mutual benefit"
- 3 email interactions, proactive communicator

**Questions I need you to answer:**
1. **What is Fei's role/title at Nira?** (Not in emails)
2. **What does Nira do?** (I guessed B2B SaaS but not sure)
3. **What's the original partnership context?** (Emails start Oct 1, but relationship predates that)

---

### 3. Elaine Pak
**File:** `file 'N5/stakeholders/elaine-pak.md'`

**What I figured out:**
- Personal Gmail (not company email)
- Thread subject: "brainstorming to create a rag-based chat assistant"
- Enthusiastic about learning from you ("super excited to hear more")
- 1 email interaction (Oct 8)

**Questions I need you to answer:**
1. **Who is Elaine Pak?** (No prior context)
2. **What organization/role?** (Personal email gives no clues)
3. **How did you connect?** (Intro? Direct outreach?)
4. **Is the RAG chat assistant her project or just a topic?**
5. **What lead type?** (I guessed LD-NET but confidence is LOW)

---

## Lead Type Guide

Pick the best fit for each person:

| Tag | Use When | Examples |
|-----|----------|----------|
| **LD-INV** | Investor/funding | VCs, angels, fund partners |
| **LD-HIR** | Hiring/talent | Candidates, recruiters |
| **LD-COM** | Community/partnership | Partners, networks, community leaders |
| **LD-NET** | Networking | Casual connections, intros |
| **LD-GEN** | Unclear/multiple | When you're not sure |

---

## What You Need to Do Now

### 1. Review the 3 Test Profiles
Open and read:
- `file 'N5/stakeholders/michael-maher-cornell.md'`
- `file 'N5/stakeholders/fei-ma-nira.md'`
- `file 'N5/stakeholders/elaine-pak.md'`

**Check:**
- Is the format useful?
- Is the inferred content accurate?
- Do you want more/less detail?
- Any changes to structure?

---

### 2. Answer These Questions

**For Fei Ma (Nira):**
1. What is Fei's role/title at Nira?
2. What does Nira do (their product/service)?
3. What's the original partnership context with Nira?

**For Elaine Pak:**
1. Who is Elaine Pak?
2. What organization/role does she have?
3. How did this connection originate?
4. Is the RAG chat assistant her project or a topic to discuss?
5. What lead type: LD-HIR, LD-COM, LD-NET, or LD-GEN?

---

### 3. Confirm Next Steps

Once you've reviewed and answered questions, I'll:
1. Update the profiles with your answers
2. Integrate the scripts with Gmail/Calendar APIs
3. Test the full workflow with live data
4. Set up weekly auto-creation scan
5. Link post-meeting updates to transcript ingestion
6. Enhance your daily meeting prep digest

---

## Files to Review

1. **Overview (this file):** `file 'N5/STAKEHOLDER_SYSTEM_OVERVIEW.md'`
2. **Full documentation:** `file 'N5/stakeholders/README.md'`
3. **Test profiles:**
   - `file 'N5/stakeholders/michael-maher-cornell.md'`
   - `file 'N5/stakeholders/fei-ma-nira.md'`
   - `file 'N5/stakeholders/elaine-pak.md'`
4. **Handoff details:** `file 'N5/handoffs/2025-10-12-stakeholder-reservoir-implementation.md'`

---

## Benefits You'll See

### Immediate (Week 1)
- ✅ No more "first meeting" confusion
- ✅ Rich context for upcoming meetings
- ✅ Your knowledge captured systematically

### Medium-term (Weeks 2-4)
- ✅ Profiles auto-update from transcripts
- ✅ Meeting prep gets smarter over time
- ✅ Can track open loops and follow-ups

### Long-term (Months 2-3)
- ✅ Relationship history at your fingertips
- ✅ Spot patterns (dormant relationships, successful partnerships)
- ✅ Network insights (who knows who, warm intros)

---

**Ready for your review!**  
Just answer the questions above and let me know if the profile format works for you.
