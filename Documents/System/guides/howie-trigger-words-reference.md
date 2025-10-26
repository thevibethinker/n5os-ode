# Howie Trigger Words - Quick Reference Card (DX System)

**Version:** 2.0  
**Updated:** 2025-10-22  
**Purpose:** Natural phrases to use during meetings for automatic Howie tag generation

---

## 🎯 Quick Reference Table

| What You Want | Say This | Generated Tags |
| --- | --- | --- |
| Urgent (by tomorrow) | "This is urgent" / "ASAP" / "today or tomorrow" | `[D1-] *` |
| High priority (this week) | "Can we do this this week?" / "early next week" | `[D3-] *` |
| Standard timeline | "No rush" / "sometime this week or next" | `[D3+] *` |
| Push out | "Let’s do this next week or later" | `[D7+] *` |
| Follow-up | "Nudge me if no reply in 5 days" | `[F-5] *` |
| Align Logan | "Logan should join" | `[LOG] *` |
| Align Ilse | "Loop Ilse in" / "align with Ilse" | `[ILS] *` |
| Our terms | "We’ll propose times" | `[A-0] *` |
| Balanced | "Let’s find a time that works for both" | `[A-1] *` |
| Fully accommodating | "We’ll work around your schedule" | `[A-2] *` |
| Async preferred | "We can handle this async / over email" | `[ASYNC] *` |
| Terminate scheduling | "Let’s put a pin in this" / "not the right time" | `[TERM] *` |
| Weekend preferred | "Weekend works best" | `[WEP] *` |
| Weekend extension OK | "Weekend is fine if needed" | `[WEX] *` |
| Same‑day flexibility | "We can shift same day if needed" | `[FLX] *` |

---

## 🧭 Examples

- Founder, align Logan, by end of week, follow‑up in 5 days:  
  `Howie Tags: [LD-FND] [GPT-F] [LOG] [A-1] [D3-] [F-5] *`

- Community partner, async, no rush:  
  `Howie Tags: [LD-COM] [GPT-E] [ASYNC] [D3+] *`

- Hiring call, flexible, weekend OK:  
  `Howie Tags: [LD-HIR] [A-1] [FLX] [WEX] [D3+] *`

---

## ⚙️ Notes

- DX system: `D3` = exactly 3 business days; `D3+` = ≥3; `D3-` = ≤3  
- Add a trailing `*` to activate Howie; no star = ignored  
- Be explicit: say "Logan should join" to ensure `[LOG]` gets picked up  

---

Print this card. Use it during meetings.
