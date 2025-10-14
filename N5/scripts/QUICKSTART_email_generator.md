# Email Follow-Up Generator — Quick Start

⚡ **Generate follow-up emails in <1 second with full v11.0.1 compliance**

---

## One-Line Command

```bash
python3 N5/scripts/n5_follow_up_email_generator.py --meeting-folder /path/to/meeting
```

---

## Most Common Usage

```bash
# 1. Find your meeting folder
ls N5/records/meetings/ | grep stakeholder-name

# 2. Generate email (replace folder name)
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit

# 3. Check outputs
ls N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/DELIVERABLES/

# 4. Copy/paste the .txt file into Gmail
cat N5/records/meetings/.../DELIVERABLES/follow_up_email_copy_paste.txt
```

---

## What You Get

**4 files in `/DELIVERABLES/`:**
1. `follow_up_email_draft.md` — Markdown version
2. `follow_up_email_copy_paste.txt` — **Use this for Gmail**
3. `follow_up_email_summary.md` — Quality metrics
4. `follow_up_email_artifacts.json` — Pipeline data

---

## Preview Before Generating

```bash
# Add --dry-run to see output without writing files
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit \
  --dry-run
```

---

## What It Does (13 Steps)

1. Loads transcript + stakeholder profile
2. Maps links from essential-links.json
3. Infers dial settings (formality, warmth, CTA)
4. Generates initial draft
5. Reviews for voice compliance
6. Extracts resonant conversation details
7. Extracts stakeholder quotes
8. Builds natural phrase pool
9. Loads your voice config
10. Revises draft
11. Compresses to ~300 words
12. **Verifies all links (P16: no fabrication)**
13. Validates readability (FK ≤ 10)

---

## Quality Guarantees

✅ **All links from essential-links.json** (no fabrication)  
✅ **FK readability ≤ 10** (accessible technical)  
✅ **Voice compliance** (no buzzwords, first-person)  
✅ **Dial calibration** (relationship-appropriate tone)  
✅ **Execution <1 second**

---

## Troubleshooting

### "Meeting folder not found"
Use absolute path starting with `/home/workspace/`

### "No transcript found"
Meeting folder needs `*transcript*.txt` or `*transcript*.md`

### "Fabricated links found"
Check essential-links.json — script will list violations

---

## Full Help

```bash
python3 N5/scripts/n5_follow_up_email_generator.py --help
```

---

## Documentation

- **Usage Guide:** `file 'N5/scripts/README_follow_up_email_generator.md'`
- **Spec:** `file 'N5/commands/follow-up-email-generator.md'` (v11.0.1)
- **Implementation:** `file 'N5/logs/.../PHASE_1_COMPLETE.md'`

---

## Example Output

```
**Subject:** Following Up — Hamoon x Careerspan [partnership pathways]

Hi Hamoon,

Great connecting last week. I appreciated your thoughtful questions about 
how we could potentially work together.

[...concrete use cases with specific details...]

You can see more at mycareerspan.com, and happy to grab 30 minutes to 
discuss further if either resonates.

Looking forward to your thoughts.

Best,
Vrijen
```

---

**Status:** ✅ Production-ready | **Version:** 1.0.0 | **Updated:** 2025-10-13
