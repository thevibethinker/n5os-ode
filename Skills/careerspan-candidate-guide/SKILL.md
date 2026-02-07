---
name: careerspan-candidate-guide
description: |
  Generates 1-page candidate guides that drive Careerspan conversion. Takes JD + resumes,
  produces a Hiring POV (internal) and per-candidate guides (shareable). Guides use neutral
  language to surface what candidates should discuss on Careerspan, framed as helping assess fit.
  All semantic work done via LLM — no regex parsing.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "2.0"
---

# Careerspan Candidate Guide Generator

## Purpose

This skill generates **candidate guides** that serve as a conversion tool for Careerspan. The guides:

1. Help candidates understand what experiences to discuss
2. Drive them to use Careerspan Stories to share those experiences
3. Are **founder-safe** — can be shared on the same email thread as the hiring manager

## Artifacts Produced

| Artifact | Audience | Purpose |
|----------|----------|---------|
| `HIRING_POV.md` | Internal (Careerspan) | What the founder/hiring manager actually cares about, derived from JD + screening form |
| `{Name}_Guide.md` | Candidate + Founder | 1-page guide with recommended stories to complete |
| `{Name}_Guide.pdf` | Candidate + Founder | PDF version for email attachment |

## Usage

### Step 1: Prepare Inputs

You need:
- **JD text** — Copy the full job description into a file (Notion pages don't scrape well)
- **Screening form URL** (optional) — If there's a screening questionnaire
- **Resumes** — PDF files for each candidate
- **CTA link** — The Careerspan link candidates should use

### Step 2: Run the Generator

```bash
python3 Skills/careerspan-candidate-guide/scripts/generate_guides.py \
  --jd-file "/path/to/jd.txt" \
  --form-url "https://forms.gle/xxx" \
  --resumes "/path/to/resume1.pdf" "/path/to/resume2.pdf" \
  --output "/path/to/output" \
  --cta "https://careerspan.link/xxx" \
  --company "Company Name" \
  --role "Role Title"
```

### Arguments

| Arg | Required | Description |
|-----|----------|-------------|
| `--jd-file` | Yes | Path to text file containing the full JD |
| `--form-url` | No | Screening form URL (will be fetched and analyzed) |
| `--resumes` | Yes | One or more PDF resume paths |
| `--output` | Yes | Output directory |
| `--cta` | No | Careerspan link for candidates (defaults to placeholder) |
| `--company` | No | Company name (extracted from JD if not provided) |
| `--role` | No | Role title (extracted from JD if not provided) |
| `--format` | No | `md`, `pdf`, or `both` (default: `both`) |

## Architecture

**Python handles:**
- File I/O (reading PDFs, writing output)
- Orchestration (sequencing the steps)
- PDF generation (pandoc conversion)

**LLM handles (via /zo/ask):**
- JD analysis → Hiring POV extraction
- Resume analysis → candidate strengths/gaps relative to role
- Guide generation → proper language, story bullet creation

This follows the "LLM-over-regex" principle: semantic understanding is never done with string manipulation.

## Guide Structure

```
# {Role} @ {Company}

{Brief role context — 2-3 sentences}

---

## How It Works

Careerspan Stories help us determine **fit signal** and **intent signal** for candidates.

- Your original transcript isn't shared with the employer — only a synthesized analysis
- There's no limit on stories — the more detail, the better we can assess fit
- Be specific: names, numbers, timelines, outcomes

---

## Recommended Careerspan Stories

Based on this role and your background, we recommend stories covering:

- {Experience from resume} — **clarify** {what to address}
- {Experience from resume} — **elaborate on** {what to address}
- {Gap or ambiguity} — **explain** {what needs context}
- {Transition or anomaly} — **provide context for** {what might raise questions}

---

## Next Step

Complete your Careerspan Stories here: {CTA_LINK}
```

## Language Rules

**Neutral verbs only:**
- ✅ clarify, elaborate on, explain, provide context for, describe, walk through
- ❌ emphasize, highlight, showcase, position, spin, frame

**Why:** The guide may be seen by the founder. It should read as helping candidates provide complete information, not coaching them to game the process.

## Files

- `scripts/generate_guides.py` — Main generator (orchestrates LLM calls)
- `assets/guide_template.md` — Template structure
- `references/guide_design.md` — Design principles and language rules
