# Social Media Ideas

Quick-capture list for social media content ideas, observations, and themes.

**Format:** Paragraph blocks with ID, title, body, optional tags

---

## Inbox

<!-- New ideas captured here; each gets an ID like I-2025-10-22-001 -->


## In Review

<!-- Ideas shortlisted for this week's generation -->


---

## Combined

<!-- Synthesized concepts referencing multiple idea IDs -->


---

## Processed

<!-- Ideas that have been generated or archived -->


**ID:** I-2025-10-22-001  
**Title:** Example: When "vulnerability" becomes strategic clarity  
**Body:**

I've noticed the difference between dumping emotion and showing the exact decision point. The through-line is what changed in my operating model, not just how I felt. 

Contrasts: "feelings" posts vs "operating notes." Founders don't need more catharsis; they need decision frameworks wrapped in story.

**Tags:** #founders #vulnerability #operating-model

---
**Status:** Generated → [post_post_33d5261fa50e]

---

<!-- Format:
**ID:** I-2025-10-22-XXX  
**Status:** Generated → [post_abc123] | Archived - reason
**Date:** 2025-10-22
-->

---

## Quick Reference

**Add idea (manual):**
1. Open this file
2. Copy the template from Inbox example
3. Paste under "## Inbox"
4. Update ID (next sequential number for today), title, body, tags
5. Save

**Add idea (CLI):**
```bash
python3 N5/scripts/n5_social_idea_add.py --title "Your title" --body "Your detailed thought..." --tags "tag1,tag2"
```

**Generate from idea:**
```bash
# Single idea
python3 N5/scripts/n5_social_idea_generate.py --id I-2025-10-22-001

# Combine multiple
python3 N5/scripts/n5_social_idea_generate.py --id I-2025-10-22-001 --id I-2025-10-22-004

# With options
python3 N5/scripts/n5_social_idea_generate.py --id I-2025-10-22-001 --platform linkedin --mode insight
```

**View generated posts:**
```bash
python3 N5/scripts/n5_social_post.py list --status draft --platform linkedin
```

---

**Last Updated:** 2025-10-22  
**Version:** 1.0.0
