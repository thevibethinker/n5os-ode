# Howie Signature Generator - Quick Start

**TL;DR:** Generate smart scheduling tags for Howie in 5 seconds

---

## The 30-Second Version

```bash
# Describe your meeting in plain English
python3 N5/scripts/howie_signature_generator.py \
  --context "urgent investor meeting with Logan" \
  --full-signature

# Output includes smart Howie tags:
# Howie Tags: [LD-INV] [GPT-I] [LOG] [!!] *
```

That's it. Copy-paste into your email.

---

## Common Scenarios

### Investor Meeting (High Priority)
```bash
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type investor \
  --urgency high \
  --priority external \
  --accommodation 2 \
  --full-signature
```

**Howie will:**
- Prefer Tuesday or Thursday
- Prioritize their schedule
- Be fully accommodating
- Schedule within 5 business days
- Auto-add 10min follow-up next day

### Hiring Candidate (Need to Move Fast)
```bash
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type hire \
  --urgency high \
  --accommodation 1 \
  --full-signature
```

**Howie will:**
- Prefer Monday, Wednesday, or Friday
- Baseline accommodation
- Schedule within 5 business days
- Auto-add 15min follow-up same day

### Community Partner + Logan
```bash
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type community \
  --align-logan \
  --priority founders \
  --full-signature
```

**Howie will:**
- Prefer Tuesday or Thursday
- Align with Logan's schedule
- Prioritize founders' preferences
- Auto-add 15min follow-up same day

---

## Just Show Me the Tags

Want just the tag line (no full signature)?

```bash
# Skip --full-signature
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type investor \
  --urgency high

# Output: [LD-INV] [D5] *
```

---

## What Do These Tags Mean?

Add `--explain` to any command:

```bash
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type investor \
  --urgency high \
  --priority external \
  --accommodation 2 \
  --explain
```

**Output:**
```
[LD-INV] [GPT-E] [A-2] [D5] *

--- Tag Explanations ---
LD-INV: Investor → prefer Tue/Thu
GPT-E: Prioritize external stakeholders' preferences
A-2: Fully accommodating
D5: Schedule within 5 business days
*: ACTIVATED - Howie will process these tags
```

---

## Cheat Sheet

### Quick Options

| Flag | Options | Meaning |
|------|---------|---------|
| `--recipient-type` | investor, hire, community, networking, general | Who you're meeting |
| `--urgency` | urgent, high, normal, low | How fast to schedule |
| `--priority` | external, internal, founders | Whose schedule matters most |
| `--accommodation` | 0, 1, 2 | How flexible (0=our terms, 2=theirs) |
| `--align-logan` | (flag) | Must include Logan |
| `--align-ilse` | (flag) | Must include Ilse |
| `--follow-up-days` | 3, 5, 7, etc. | Auto-reminder after X days |
| `--full-signature` | (flag) | Generate complete email signature |
| `--explain` | (flag) | Show what each tag means |

### Context Magic

**Instead of flags, just describe the meeting:**

```bash
--context "urgent investor meeting this week"
--context "hiring candidate, need to move fast"
--context "community partner discussion with Logan next month"
```

The generator infers:
- Recipient type (investor, hire, etc.)
- Urgency level
- Who to align with
- Priority

---

## Tag Quick Reference

```
RECIPIENT TYPES          PRIORITY              URGENCY
[LD-INV] Investor       [GPT-E] Their sched   [!!] URGENT (2 days)
[LD-HIR] Hiring         [GPT-I] Our sched     [D5] Within 5 days
[LD-COM] Community      [GPT-F] Founders      [D5+] 5+ days out
[LD-NET] Networking                           [D10] 10+ days out
[LD-GEN] General        

ACCOMMODATION           ALIGN WITH            FOLLOW-UP
[A-0] Our terms only    [LOG] Logan           [F-5] After 5 days
[A-1] Baseline          [ILS] Ilse            (Howie reminds as assistant)
[A-2] Fully flexible    

ALWAYS END WITH: *  ← Activates Howie
```

---

## Real Examples

### Example 1: Key Investor, Need to Close Fast

**Situation:** Hot investor lead, want to meet this week, be super flexible

**Command:**
```bash
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type investor \
  --urgency urgent \
  --priority external \
  --accommodation 2 \
  --follow-up-days 2
```

**Tags:** `[LD-INV] [GPT-E] [A-2] [!!] [F-2] *`

**What happens:**
- Overrides normal constraints
- Proposes slots in next 2 business days
- Still prefers Tue/Thu if possible
- Fully accommodating to their schedule
- Howie follows up after 2 days if no response

### Example 2: Promising Hire

**Situation:** Great candidate, want to interview soon but not emergency

**Command:**
```bash
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type hire \
  --urgency high \
  --accommodation 1 \
  --follow-up-days 3
```

**Tags:** `[LD-HIR] [A-1] [D5] [F-3] *`

**What happens:**
- Prefers Mon/Wed/Fri
- Schedule within 5 business days
- Baseline accommodation
- Auto 15min follow-up block
- Howie reminds after 3 days

### Example 3: Partnership Discussion with Logan

**Situation:** Community partner, need Logan on call, no rush

**Command:**
```bash
python3 N5/scripts/howie_signature_generator.py \
  --recipient-type community \
  --priority founders \
  --align-logan \
  --urgency normal
```

**Tags:** `[LD-COM] [GPT-F] [LOG] [D5+] *`

**What happens:**
- Prefers Tue/Thu
- Must work with Logan's schedule
- Prioritizes founders' preferences
- 5+ business days out
- Auto 15min follow-up block

---

## Pro Tips

1. **Always use `*`** - Without it, Howie ignores all tags
2. **Lead type sets defaults** - `LD-INV` auto-prefers Tue/Thu
3. **Context is smart** - Try natural language first, it usually works
4. **Explain when learning** - Use `--explain` to understand tags
5. **Test first** - Run command without email to see tags

---

## Need More?

**Full Documentation:** `file 'N5/docs/howie-signature-system.md'`

**Presets:** `file 'N5/config/howie_presets.json'`

**Howie Rules:** `file 'Knowledge/context/howie_instructions/preferences.md'`

---

**Version:** 1.0 | **Updated:** 2025-10-22
