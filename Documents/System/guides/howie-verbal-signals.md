# Howie Verbal Signals Guide

**Version:** 1.0  
**Purpose:** Natural language patterns that signal Howie tag choices  
**For:** V to use during meetings to leave breadcrumbs for intelligent tag generation

---

## Overview

This guide maps **natural phrases you can use during meetings** to **specific Howie tags**. When these phrases appear in transcripts, the Howie Context Analyzer will detect them and recommend appropriate V-OS tags.

### How It Works

1. **During meetings**, use these natural phrases when discussing scheduling
2. **After meetings**, transcript contains your verbal signals
3. **Zo analyzes** the transcript and detects signals
4. **Howie tags** are automatically generated based on detected patterns
5. **Email signature** includes intelligent scheduling instructions for Howie

---

## Priority & Accommodation Signals

### "I'm happy to work around your schedule"
**Signal:** High accommodation (A-2), External priority (GPT-E)

**Use when:** You want to be maximally flexible
- "Whatever works best for you, I'm happy to work around your schedule"
- "Let me know what times are good for you, I'll make it work"
- "Totally flexible on my end"

**Generates:** `[GPT-E] [A-2]`

---

### "Let me know some times that work for you"
**Signal:** External priority (GPT-E), Awaiting their preferences

**Use when:** Deferring to their availability
- "Send me some times that work and I'll make one of them happen"
- "What does your schedule look like next week?"
- "Let me know your availability"

**Generates:** `[GPT-E] [A-1]` or `[A-2]` (depending on urgency)

**Howie behavior:** Waits for them to propose times

---

### "I'll have my assistant send you some options"
**Signal:** Internal priority (GPT-I) or balanced (GPT-E with A-1), Howie proposes times

**Use when:** You want Howie to drive scheduling
- "My assistant Howie will reach out with some times"
- "I'll send you a few options that work on my end"
- "Let me propose some slots"

**Generates:** `[GPT-E] [A-1]` or `[GPT-I] [A-0]`

**Howie behavior:** Proactively proposes 3-5 time slots

---

### "On our terms" / "When it works for us"
**Signal:** Internal priority (GPT-I), Minimal accommodation (A-0)

**Use when:** Low-priority relationship, your convenience only
- "We can find a time that works for us"
- "I'll check my calendar and let you know"
- "If we have availability, we'll let you know"

**Generates:** `[GPT-I] [A-0]`

**Howie behavior:** Only proposes times that are optimal for you

---

### "Logan should join this"
**Signal:** Founders priority (GPT-F), Logan alignment (LOG)

**Use when:** Both founders should be present
- "Let me see when Logan is free"
- "I want Logan on this call too"
- "Can you meet with both me and Logan?"
- "The founders should be on this together"

**Generates:** `[GPT-F] [LOG]`

**Howie behavior:** Checks Logan's calendar, only proposes mutual availability

---

## Urgency & Timeline Signals

### "This week would be great"
**Signal:** High urgency, 5-day timeline (D5)

**Use when:** Time-sensitive but not emergency
- "Let's try to connect this week"
- "Can we make this happen in the next few days?"
- "Sooner rather than later"

**Generates:** `[D5]`

**Howie behavior:** Proposes times within 5 business days

---

### "Let's find time soon, but no rush"
**Signal:** Normal urgency, flexible timeline (D5+)

**Use when:** Standard follow-up, 1-2 week window fine
- "Next week or the week after works"
- "Sometime in the next couple weeks"
- "No particular hurry"

**Generates:** `[D5+]`

**Howie behavior:** Proposes times within 10 business days

---

### "This is urgent" / "ASAP"
**Signal:** Override urgency (!!)

**Use when:** Emergency/critical timing
- "We need to talk this week, ideally tomorrow or the next day"
- "This is time-sensitive"
- "Can we jump on a call ASAP?"
- "Is there any chance you're free in the next 48 hours?"

**Generates:** `[!!]`

**Howie behavior:** Overrides normal constraints, proposes best available slots in next 2 days

---

### "If we don't hear back by [date], we'll follow up"
**Signal:** Follow-up reminder (F-X)

**Use when:** Setting explicit follow-up expectation
- "If I don't hear back by Friday, I'll ping you again"
- "I'll check back in a week if I haven't heard from you"
- "Let's reconnect if we don't connect by end of week"

**Generates:** `[F-5]` or `[F-7]` (depending on timeline mentioned)

**Howie behavior:** Sends follow-up reminder as your assistant after X days

---

## Relationship & Stakeholder Type Signals

### "Would love to get your feedback" / "Pick your brain"
**Signal:** Networking/advisory type (LD-NET)

**Use when:** Seeking advice, lower-stakes relationship
- "I'd love to get your thoughts on this"
- "Would be great to hear your perspective"
- "Can I pick your brain about X?"

**Generates:** `[LD-NET] [GPT-E] [A-1]`

---

### "Let's explore a partnership" / "Collaboration opportunity"
**Signal:** Community/partnership type (LD-COM)

**Use when:** Ecosystem play, mutual value
- "I think there's a collaboration opportunity here"
- "This could be a good fit for both our communities"
- "Let's see how we can work together"

**Generates:** `[LD-COM] [GPT-E] [A-2]`

---

### "Want to discuss our series [X]" / "Fundraising conversation"
**Signal:** Investor type (LD-INV)

**Use when:** Investor relations, fundraising
- "Would love to talk about potential investment"
- "We're raising our seed round"
- "Interested in learning more about your fund"

**Generates:** `[LD-INV] [GPT-E] [A-2] [D5]`

**Special:** Auto-includes Tuesday/Thursday preference for investors

---

### "Interview conversation" / "Candidate discussion"
**Signal:** Hiring type (LD-HIR)

**Use when:** Recruiting, candidate evaluation
- "Let's schedule a time to chat about the role"
- "Would love to hear about your background"
- "Want to discuss the opportunity"

**Generates:** `[LD-HIR] [A-1] [D5]`

---

## Flexibility & Constraints Signals

### "Totally flexible" / "Whenever works"
**Signal:** Flexible meeting (FLX)

**Use when:** Meeting can slide within same day
- "Anytime that day is fine"
- "Morning or afternoon both work"
- "Super flexible"

**Generates:** `[FLX]`

**Howie behavior:** Allows same-day rescheduling without confirmation

---

### "Weekend works if needed"
**Signal:** Weekend acceptable (WEX)

**Use when:** Willing to meet on weekends
- "I'm around on weekends too if that helps"
- "Saturday or Sunday could work"

**Generates:** `[WEX]`

**Howie behavior:** Includes weekend slots if weekday scheduling difficult

---

### "Actually, prefer a weekend"
**Signal:** Weekend preferred (WEP)

**Use when:** Weekends are better for you
- "Weekends are actually easier for me"
- "Do you have time on Saturday?"

**Generates:** `[WEP]`

**Howie behavior:** Prioritizes weekend slots

---

### "Need to loop in [person]"
**Signal:** Alignment tag (LOG, ILS, etc)

**Use when:** Others need to be included
- "Let me see when Logan is free" → `[LOG]`
- "I'll need to check with Ilias" → `[ILS]`

**Howie behavior:** Checks specified person's calendar

---

## Termination & Special Signals

### "Let's put a pin in this" / "Not the right time"
**Signal:** Terminate thread (TERM)

**Use when:** No longer pursuing this meeting
- "Let's revisit this in a few months"
- "Actually, I don't think we need to meet right now"
- "Let's put this on hold"

**Generates:** `[TERM]`

**Howie behavior:** Stops all scheduling attempts, removes from queue

---

### "This doesn't need a meeting" / "Let's just email"
**Signal:** Ignore thread (INC)

**Use when:** Meeting isn't needed despite scheduling discussion
- "Actually, we can handle this over email"
- "No need to meet, I'll just send you the info"

**Generates:** `[INC]`

**Howie behavior:** Ignores all scheduling requests in this thread

---

## Combination Patterns

### "Urgent investor meeting, need Logan there too"
**Verbal signals:**
- "urgent" → `[!!]`
- "investor" → `[LD-INV]`
- "Logan" → `[LOG]` `[GPT-F]`

**Generated tags:** `[LD-INV] [GPT-F] [LOG] [!!] *`

**Meaning:** Investor meeting, both founders, urgent timing, override constraints

---

### "Community member, happy to work around their schedule, let's connect this week"
**Verbal signals:**
- "community" → `[LD-COM]`
- "work around their schedule" → `[A-2]` `[GPT-E]`
- "this week" → `[D5]`

**Generated tags:** `[LD-COM] [GPT-E] [A-2] [D5] *`

**Meaning:** Community relationship, high accommodation, 5-day timeline

---

### "Networking coffee, I'll send them some times, no rush"
**Verbal signals:**
- "networking coffee" → `[LD-NET]`
- "I'll send them times" → `[A-1]` (Howie proposes)
- "no rush" → `[D5+]`

**Generated tags:** `[LD-NET] [GPT-E] [A-1] [D5+] *`

**Meaning:** Networking meeting, balanced accommodation, Howie proposes times, flexible timeline

---

## Advanced Patterns

### CRM Integration Signals

**"Make a note that they prefer mornings"**
- Stores preference in stakeholder CRM
- Future meetings auto-apply morning preference

**"They're in Pacific time"**
- Stores timezone in CRM
- Auto-converts proposed times

**"Flag this as a warm lead"**
- Updates relationship stage in CRM
- Adjusts accommodation level for future

**"This is a high-priority relationship"**
- Marks as strategic value in CRM
- Auto-applies `[GPT-E]` `[A-2]` for future meetings

---

## Signal Confidence Levels

### High Confidence (90%+)
Explicit, unambiguous phrases:
- "urgent" → urgency
- "Logan should join" → alignment
- "investor meeting" → stakeholder type

### Medium Confidence (60-90%)
Contextual clues:
- "this week" → timeline (but not emergency)
- "work around your schedule" → accommodation (but degree unclear)
- "would love your thoughts" → networking (but could be strategic)

### Low Confidence (30-60%)
Vague or ambiguous:
- "soon" → timeline (how soon?)
- "important" → priority (how important?)
- "let's chat" → meeting type (what about?)

**Recommendation:** Use explicit phrases for critical tag choices (urgency, alignment). Context clues are fine for secondary tags (accommodation level).

---

## Natural Conversation Examples

### Example 1: High-Stakes Investor Meeting

**V during call:** "This sounds really promising. I'd love to continue the conversation with you and get Logan on the call too. We're finalizing our deck this week, so ideally we'd connect by end of week. Totally flexible on timing though, whatever works best for your schedule."

**Detected signals:**
- "investor" context (implicit from "deck")
- "Logan on the call" → `[LOG]` `[GPT-F]`
- "by end of week" → `[D5]`
- "whatever works best for your schedule" → `[A-2]` `[GPT-E]`

**Generated tags:** `[LD-INV] [GPT-E] [LOG] [A-2] [D5] *`

---

### Example 2: Networking/Advisory

**V during call:** "I'd love to pick your brain about the fundraising process. No particular rush, next week or the week after works. I'll have my assistant send you a few time options."

**Detected signals:**
- "pick your brain" → `[LD-NET]`
- "no particular rush" → `[D5+]`
- "my assistant send you options" → `[A-1]` (Howie proposes)

**Generated tags:** `[LD-NET] [GPT-E] [A-1] [D5+] *`

---

### Example 3: Internal/Low Priority

**V during call:** "If it makes sense for us to connect, we can find a time that works on our end. No need to rush, whenever we have availability."

**Detected signals:**
- "if it makes sense" → low priority
- "works on our end" → `[GPT-I]`
- "whenever we have availability" → `[A-0]`

**Generated tags:** `[GPT-I] [A-0] [D5+] *`

---

## Quick Reference Card

### 🚨 Urgency
| Say This | Get This | Meaning |
|----------|----------|---------|
| "ASAP" / "urgent" / "this week ideally tomorrow" | `[!!]` | Override constraints, next 2 days |
| "This week" / "next few days" / "sooner rather than later" | `[D5]` | Within 5 business days |
| "No rush" / "next week or two" / "whenever" | `[D5+]` | Within 10 business days |

### 🤝 Accommodation
| Say This | Get This | Meaning |
|----------|----------|---------|
| "Whatever works for you" / "work around your schedule" | `[A-2]` | Fully accommodating |
| "I'll send you some options" / "let me know what works" | `[A-1]` | Balanced, mutual convenience |
| "When it works for us" / "if we have availability" | `[A-0]` | On our terms only |

### 👥 Priority
| Say This | Get This | Meaning |
|----------|----------|---------|
| "Happy to work around your schedule" | `[GPT-E]` | External stakeholder priority |
| "Logan should join" / "both founders" | `[GPT-F]` | Founders priority |
| "On our terms" / "when we're available" | `[GPT-I]` | Internal priority |

### 🏷️ Stakeholder Type
| Say This | Get This | Meaning |
|----------|----------|---------|
| "Investor" / "fundraising" / "our round" | `[LD-INV]` | Investor (auto: Tue/Thu) |
| "Interview" / "candidate" / "role" | `[LD-HIR]` | Hiring |
| "Partnership" / "collaboration" / "ecosystem" | `[LD-COM]` | Community |
| "Pick your brain" / "get your thoughts" | `[LD-NET]` | Networking |

### 👯 Alignment
| Say This | Get This | Meaning |
|----------|----------|---------|
| "Logan should join" / "get Logan on this" | `[LOG]` | Align with Logan |
| "Check with Ilias" / "Ilias should be there" | `[ILS]` | Align with Ilias |

### ⏰ Follow-up
| Say This | Get This | Meaning |
|----------|----------|---------|
| "I'll follow up in 5 days if I don't hear back" | `[F-5]` | Reminder in 5 days |
| "Let's reconnect next week if we don't connect" | `[F-7]` | Reminder in 7 days |

### 🛑 Special
| Say This | Get This | Meaning |
|----------|----------|---------|
| "Let's put this on hold" / "not the right time" | `[TERM]` | Stop scheduling |
| "We can handle this over email" / "no need to meet" | `[INC]` | Ignore scheduling |
| "Totally flexible" / "anytime that day" | `[FLX]` | Same-day flexibility |
| "Weekend works" / "Saturday is fine" | `[WEX]` | Weekend acceptable |

---

## Tips for Effective Signaling

### 1. **Be Explicit in Key Moments**
When urgency, alignment, or priority matters, use explicit phrases:
- ✅ "This is urgent, we need Logan on this call, and I'm happy to work around your schedule"
- ❌ "Let's try to connect soon"

### 2. **Front-Load Signals**
Say key signals early in the meeting or immediately after scheduling discussion:
- ✅ "Before we wrap up: this is time-sensitive, so let's try to connect this week. I'll have my assistant send you some options."
- ❌ Scattered signals throughout 30-min conversation

### 3. **Confirm at Meeting End**
Recap scheduling instructions explicitly:
- "So to recap: I'll have Howie send you some time options for this week, and we'll include Logan on the call."

### 4. **Use Action Item Language**
Frame scheduling as action item in B-Block extraction:
- "Action item: Schedule follow-up with Logan, high priority, this week"

### 5. **Avoid Ambiguity**
Don't mix conflicting signals:
- ❌ "This is urgent but no rush"
- ❌ "Whatever works for you, but on our terms"
- ✅ Be consistent: urgent = urgent, flexible = flexible

---

## Future: CRM Preference Learning

### Stakeholder Preference Storage

**When you say:**
"Make a note that Sarah prefers Tuesday mornings"

**Zo will:**
1. Extract preference: `{day: 'Tuesday', time: 'morning'}`
2. Store in CRM: `stakeholders/sarah.json`
3. Auto-apply to future meetings with Sarah

**When you say:**
"This is a high-value relationship, always be accommodating"

**Zo will:**
1. Mark stakeholder: `{value: 'strategic'}`
2. Auto-apply: `[GPT-E] [A-2]` for future meetings
3. Store in CRM for all team members

### Pattern Learning

After 10+ meetings with similar stakeholder types:
- "Investors who respond within 24 hours convert 80% of the time"
- "Community partners prefer afternoon slots"
- "Hiring candidates ghost less when we propose within 48 hours"

**Auto-optimization:**
- Adjust default tags based on learned patterns
- Suggest optimal timing based on historical data
- Flag relationships that need different approach

---

## Implementation Status

### ✅ Phase 1 (Current)
- Keyword detection for all tag types
- Confidence scoring
- Natural language inference
- Context-aware generation

### 🔄 Phase 2 (In Progress)
- Enhanced signal dictionary (this document)
- Multi-signal combination logic
- Confidence thresholds for ambiguous cases

### 📋 Phase 3 (Planned)
- CRM integration for preference storage
- Historical pattern learning
- Auto-optimization based on outcomes
- Stakeholder-specific default tags

---

**Version:** 1.0  
**Created:** 2025-10-22  
**Maintained By:** Zo (Vibe Builder)  
**Last Updated:** 2025-10-22 11:44 ET
