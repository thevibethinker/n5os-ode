# Howie Update Instructions - Batch Packets

**Version:** 2.0  
**Date:** 2025-10-22  
**Purpose:** Copy‑paste these to Howie one batch at a time

---

## Instructions for V

1. Send **Batch 1** to Howie, wait for confirmation
2. Send **Batch 2**, wait for confirmation
3. Send **Batch 3**, wait for confirmation
4. Test with a real email to confirm all changes work

**Total changes:** 3 batches × 3‑4 changes each = ~10 updates

---

## Batch 1 — Timeline DX System (3 changes)

```
Howie, I need you to update your timeline tag system. These changes replace the old D5/D5+/!! system.

1) **New Timeline Format: DX, DX+, DX-**
   - DX = schedule in exactly X business days
   - DX+ = schedule X or more business days out (that day onwards)
   - DX- = schedule by X business days at latest (deadline, no later than X)
   
   Examples:
   - [D1-] = by tomorrow at latest (urgent)
   - [D3+] = 3+ business days out (standard)
   - [D7+] = next week or later (low priority)
   - [D2] = exactly 2 business days

2) **Remove the !! tag entirely**
   - The !! emergency override tag is retired
   - Use D1- for urgent meetings instead

3) **Default timeline when no D* tag is present: D3+**
   - If you see an activated signature (*) with no DX tag, assume [D3+]
   - This means "3 or more business days out, standard timeline"

Confirm you understand these three timeline changes before I send the next batch.
```

---

## Batch 2 — Lead Type & Alignment Clarifications (4 changes)

```
Howie, now I need you to clarify and expand your lead type (LD-*) understanding.

1) **LD-COM = Community Organizations**
   - LD-COM refers to people affiliated with community groups/organizations
   - Examples: Future of Higher Ed Group, McKinsey Alumni Association, industry groups
   - NOT for individual founders (those are LD-FND)

2) **LD-FND = Strategic Founders**
   - Individual founders of companies (strategic relationships)
   - Kept separate from LD-COM
   - Examples: founder of a partner company, founder you're exploring collaboration with

3) **Alignment tags: LOG and ILS**
   - [LOG] = must align with Logan's calendar; if Logan unavailable, propose next best option and flag the conflict
   - [ILS] = must align with Ilse's calendar; same rule applies
   - When you see [LOG] or [ILS], check their calendars FIRST before proposing times

4) **Follow-up tags: F-X**
   - [F-X] = if no reply after X days, send a nudge **as Vrijen's assistant**
   - Include a brief context recap in your nudge
   - Example: [F-5] means "nudge after 5 days with context"

Confirm you understand these four clarifications before I send the final batch.
```

---

## Batch 3 — Phase 1 Utility Tags (4 new tags)

```
Howie, I'm adding four new utility tags to give you more context and enable smarter behaviors.

1) **[ASYNC] — Async Preferred**
   - This meeting doesn't need to happen; we can handle it over email
   - When you see [ASYNC], suggest email/async communication instead of proposing times
   - Example: "Happy to discuss this over email if that works better for you"

2) **[TERM] — Terminate Scheduling**
   - Stop all scheduling activity for this thread immediately
   - Used when: "let's put a pin in this" / "not the right time"
   - Do not propose times, do not follow up, but remain polite

3) **[FLX] — Flexible (same‑day shifts OK)**
   - The meeting can be moved within the same day if needed
   - Use this when proposing times: "These times work, but we can shift same‑day if needed"

4) **[WEX] vs [WEP] — Weekend Handling**
   - [WEX] = Weekend Extension allowed (can extend into weekend if needed)
   - [WEP] = Weekend Preferred (actively prefer weekend slots)
   - Both are optional; only use weekends when explicitly tagged

Confirm you understand these four new utility tags. Once confirmed, the update is complete.
```

---

## Testing Script

After all three batches are confirmed, test with this example:

**Test Email Draft:**
```
Subject: Quick sync on partnership
Body: Hey [Name], would love to sync on the partnership discussion. Logan should join. No rush, but let's aim for sometime next week or the week after.

Howie Tags: [LD-COM] [GPT-E] [LOG] [A-2] [D7+] [F-5] *
```

**Expected Howie Behavior:**
- Recognizes community partner (LD-COM)
- External priority (GPT-E)
- Checks Logan's calendar first (LOG)
- Fully accommodating (A-2)
- Proposes times 7+ business days out (D7+)
- Will nudge after 5 days if no reply (F-5)

---

## Quick Reference for V

**Timeline DX:**
- D1- = by tomorrow (urgent)
- D3- = by end of this week (high)
- D3+ = 3+ days out (normal, **default**)
- D7+ = next week+ (low)

**Phase 1 New Tags:**
- ASYNC = handle over email
- TERM = stop scheduling
- FLX = same‑day flexibility
- WEX/WEP = weekend handling

**Lead Types:**
- LD-INV = investor
- LD-HIR = hiring/candidate
- LD-COM = community org
- LD-NET = networking
- LD-FND = founder (strategic)
- LD-GEN = general

---

**Status:** Ready to send to Howie  
**Version:** 2.0 (DX system, Phase 1 tags)  
**Created:** 2025-10-22 04:16 PM ET
