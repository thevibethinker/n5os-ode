# Howie Signature System

**Version:** 1.0  
**Created:** 2025-10-22  
**Purpose:** Generate intelligent V-OS tags for Howie scheduling bot

---

## Overview

Howie is V's scheduling assistant bot that manages calendar coordination and meeting scheduling. Howie reads **V-OS tags** embedded in email signatures to understand scheduling preferences, constraints, and priorities for each thread.

This system provides:
1. **Intelligent tag generation** based on meeting context
2. **Pre-built presets** for common scenarios
3. **Context inference** from natural language descriptions

---

## Tag Reference

### Lead Type Tags (LD-*)

Categorize the type of meeting/stakeholder:

| Tag | Meaning | Day Preferences | Follow-up |
|-----|---------|----------------|-----------|
| `[LD-INV]` | Investor | Tue/Thu | 10min next day |
| `[LD-HIR]` | Hiring candidate | Mon/Wed/Fri | 15min same day |
| `[LD-COM]` | Community/partner | Tue/Thu (+ Logan) | 15min same day |
| `[LD-NET]` | Networking | Tue/Fri | 10min next day |
| `[LD-GEN]` | General lead | Wed | 10min next day |

### Priority Tags (GPT-*)

Whose preferences to prioritize:

| Tag | Meaning |
|-----|---------|
| `[GPT-E]` | Prioritize **external** stakeholder preferences |
| `[GPT-I]` | Prioritize **internal** stakeholder preferences |
| `[GPT-F]` | Prioritize **founders'** (Vrijen + Logan) preferences |

### Accommodation Level (A-*)

How flexible to be:

| Tag | Meaning |
|-----|---------|
| `[A-0]` | Only on our terms |
| `[A-1]` | Baseline accommodation |
| `[A-2]` | Fully accommodating |

### Scheduling Constraints

Timeline and alignment:

| Tag | Meaning |
|-----|---------|
| `[!!]` | **URGENT** - Override constraints, propose best slots in next 2 business days |
| `[D5]` | Schedule within 5 business days |
| `[D5+]` | Schedule 5+ business days out |
| `[D10]` | Schedule 10+ business days out |
| `[LOG]` | Align with Logan's availability |
| `[ILS]` | Align with Ilse's availability |

### Follow-up Rules

Automated reminders:

| Tag | Meaning |
|-----|---------|
| `[F-X]` | After X days no response, Howie sends reminder as "Vrijen's assistant" |
| `[FL-X]` | After X days, send Logan private follow-up (don't cc everyone) |
| `[FM-X]` | After X days, send reminder only to me (not participants) |

### Special Modifiers

| Tag | Meaning |
|-----|---------|
| `[FLX]` | Flexible - can shift within work hours same day |
| `[WEX]` | Weekend OK - allow weekend slots before 5pm |
| `[WEP]` | Weekend prefer - prefer weekend scheduling |
| `[TERM]` | Terminate Howie's involvement (reactivate with `*`) |
| `[INC]` | Ignore email entirely |

### Activation Symbol

| Symbol | Meaning |
|--------|---------|
| `*` | **ACTIVATED** - Howie will process these tags (required) |

---

## Usage

### Command Line

```bash
# Basic usage
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type investor \
  --urgency high \
  --priority external \
  --accommodation 2

# Output: [LD-INV] [GPT-E] [A-2] [D5] *

# With explanations
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type investor \
  --urgency high \
  --priority external \
  --accommodation 2 \
  --explain

# Full email signature
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type hire \
  --urgency normal \
  --accommodation 1 \
  --full-signature

# Context-based inference
python3 N5/scripts/howie_signature_generator.py \
  --context "urgent investor meeting with Logan this week" \
  --explain

# Output: [LD-INV] [GPT-I] [LOG] [!!] *
```

### Python API

```python
from N5.scripts.howie_signature_generator import HowieSignatureGenerator

generator = HowieSignatureGenerator()

# Generate tags
tags = generator.generate(
    recipient_type="investor",
    urgency="high",
    priority="external",
    accommodation=2
)

# Get signature line
signature_line = tags.to_signature_line()
# "[LD-INV] [GPT-E] [A-2] [D5] *"

# Get full email signature
full_sig = generator.create_full_signature(tags)
print(full_sig)

# Get explanations
explanations = tags.get_explanation()
for tag, meaning in explanations.items():
    print(f"{tag}: {meaning}")
```

---

## Common Scenarios & Presets

### Investor Meetings

**High Priority Investor**
```
[LD-INV] [GPT-E] [A-2] [D5] *
```
Meaning: Investor meeting, prioritize their schedule, fully accommodating, within 5 days

**Urgent Investor**
```
[LD-INV] [GPT-E] [!!] *
```
Meaning: Investor meeting, prioritize their schedule, URGENT (next 2 days)

### Hiring Candidates

**Standard Hire**
```
[LD-HIR] [A-1] [D5+] *
```
Meaning: Hiring candidate, baseline accommodation, 5+ days out, auto 15min follow-up

**Urgent Hire**
```
[LD-HIR] [A-1] [D5] *
```
Meaning: Hiring candidate, baseline accommodation, within 5 days

### Community/Partners

**Community Meeting with Logan**
```
[LD-COM] [GPT-F] [LOG] [F-5] *
```
Meaning: Community lead, prioritize founders, align with Logan, follow-up in 5 days

### Networking

**Standard Networking**
```
[LD-NET] [A-1] [D5+] *
```
Meaning: Networking lead, baseline accommodation, 5+ days out, prefer Tue/Fri

### Internal Meetings

**Internal with Logan**
```
[GPT-I] [LOG] [FLX] *
```
Meaning: Internal priority, align with Logan, flexible timing

**Founders Only**
```
[GPT-F] [FLX] *
```
Meaning: Founders meeting, flexible

### Special Cases

**On Our Terms**
```
[GPT-I] [A-0] *
```
Meaning: Internal priority, only on our terms

**Maximum Accommodation**
```
[GPT-E] [A-2] [D5+] *
```
Meaning: External priority, fully accommodating, 5+ days out

---

## Integration with Email Composer

The signature generator integrates with `email_composer.py`:

```python
from N5.scripts.email_composer import EmailComposer
from N5.scripts.howie_signature_generator import HowieSignatureGenerator

composer = EmailComposer(recipient="investor@example.com")
howie_gen = HowieSignatureGenerator()

# Generate context-aware Howie tags
tags = howie_gen.generate(
    recipient_type="investor",
    urgency="high",
    priority="external",
    accommodation=2
)

# Compose email with Howie signature
email = composer.compose(
    subject="Following up on our conversation",
    context={"meeting_type": "investor"},
    howie_tags=tags
)
```

---

## Best Practices

### 1. **Always Activate Tags**
Include `*` at the end to activate Howie processing. Without it, Howie ignores the tags.

### 2. **Lead Type First**
Start with lead type (`LD-*`) to set day preferences and follow-up rules.

### 3. **Be Specific About Accommodation**
Use `A-0`, `A-1`, or `A-2` to clearly communicate flexibility level.

### 4. **Combine Priority with Lead Type**
- `[LD-INV] [GPT-E]` = Investor, their schedule priority
- `[LD-HIR] [GPT-I]` = Hire, our schedule priority
- `[LD-COM] [GPT-F]` = Community, founders' schedule priority

### 5. **Use Context Inference**
Let the generator infer tags from natural language:
```bash
--context "urgent investor meeting with Logan next week"
```
Generates: `[LD-INV] [GPT-I] [LOG] [D5] *`

### 6. **Follow-up Timing**
- `[F-5]` for external stakeholders (Howie sends as "assistant")
- `[FM-5]` for internal reminders (only to you, not participants)
- `[FL-5]` for Logan-specific follow-ups (private to her)

### 7. **Weekend Flexibility**
- `[WEX]` = Allow weekends if needed (before 5pm)
- `[WEP]` = Actually prefer weekends

### 8. **Emergency Override**
Use `[!!]` sparingly - it overrides all constraints and proposes immediate slots.

---

## Examples in Practice

### Example 1: Key Investor
**Context:** Important investor, high priority, need to move fast

```
Best,
Vrijen S Attawar
CEO @ Careerspan

Howie Tags: [LD-INV] [GPT-E] [A-2] [D5] *
```

**What Howie Does:**
- Prefers Tuesday or Thursday
- Prioritizes investor's schedule
- Fully accommodating to their constraints
- Schedules within 5 business days
- Auto-adds 10min follow-up next day

### Example 2: Hiring Candidate
**Context:** Promising candidate, move with urgency

```
Best,
Vrijen S Attawar
CEO @ Careerspan

Howie Tags: [LD-HIR] [A-1] [D5] [F-3] *
```

**What Howie Does:**
- Prefers Monday, Wednesday, or Friday
- Baseline accommodation
- Schedules within 5 business days
- Auto-adds 15min follow-up same day
- Sends reminder after 3 days if no response

### Example 3: Community Partner + Logan
**Context:** Partnership discussion, need Logan on the call

```
Best,
Vrijen S Attawar
CEO @ Careerspan

Howie Tags: [LD-COM] [GPT-F] [LOG] [D5+] *
```

**What Howie Does:**
- Prefers Tuesday or Thursday
- Prioritizes founders' schedules
- Aligns with Logan's availability
- Schedules 5+ business days out
- Auto-adds 15min follow-up same day

### Example 4: Urgent Investor Meeting
**Context:** Hot lead, need to move NOW

```
Best,
Vrijen S Attawar
CEO @ Careerspan

Howie Tags: [LD-INV] [GPT-E] [!!] *
```

**What Howie Does:**
- Overrides all normal constraints
- Proposes best available slots in next 2 business days
- Still prioritizes investor's preferences
- Still prefers Tuesday/Thursday if possible

---

## Files

| File | Purpose |
|------|---------|
| `N5/scripts/howie_signature_generator.py` | Main generator script |
| `N5/config/howie_presets.json` | Pre-built common scenarios |
| `Knowledge/context/howie_instructions/preferences.md` | Full Howie preferences (source of truth) |
| `N5/docs/howie-signature-system.md` | This documentation |

---

## Quick Reference Card

```
LEAD TYPES          PRIORITY           ACCOMMODATION
[LD-INV] Investor   [GPT-E] External   [A-0] Our terms only
[LD-HIR] Hire       [GPT-I] Internal   [A-1] Baseline
[LD-COM] Community  [GPT-F] Founders   [A-2] Fully accommodating
[LD-NET] Network
[LD-GEN] General    TIMELINE           SPECIAL
                    [!!]  Urgent       [LOG] Align Logan
FOLLOW-UP           [D5]  5 days       [ILS] Align Ilse
[F-X]  External     [D5+] 5+ days      [FLX] Flexible
[FL-X] Logan        [D10] 10+ days     [WEX] Weekend OK
[FM-X] Me only                         [WEP] Weekend prefer

ALWAYS END WITH: *
```

---

## Troubleshooting

**Howie not responding?**
- Check for `*` activation symbol
- Verify tags are in square brackets
- Ensure email thread isn't tagged `[INC]` or `[TERM]`

**Wrong day preferences?**
- Lead type tag sets day preferences
- Use correct `LD-*` tag for stakeholder type

**Scheduling conflicts?**
- Use `[LOG]` or `[ILS]` to align with others
- Increase accommodation level with `[A-2]`
- Use `[!!]` for urgent override

**No follow-up happening?**
- Lead types auto-add follow-ups
- Use `[F-X]` for explicit reminder timing
- Check Howie hasn't been terminated with `[TERM]`

---

**Last Updated:** 2025-10-22  
**Maintained By:** Zo (Vibe Builder)
