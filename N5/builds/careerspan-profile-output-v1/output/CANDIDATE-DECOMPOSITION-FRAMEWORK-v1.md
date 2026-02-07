---
created: 2026-01-29
last_edited: 2026-01-29
version: 1.0
provenance: con_JTGSUg7MJeBHzmdq
source_conversation: con_4yp5BoXoZM2YzXXN
---

# Careerspan Candidate Decomposition Framework v1

> **Purpose:** Standardized methodology for extracting, structuring, and storing candidate intelligence from raw Careerspan analysis documents.

---

## Overview

This framework defines how to transform a raw Careerspan analysis (typically a Google Doc with multiple tabs) into a structured local data store optimized for downstream analysis, output generation, and retrieval.

### Input → Output

| Input | Output |
|-------|--------|
| Google Doc with 4-6 tabs of Careerspan analysis | 11 structured markdown files + media folder |
| Unstructured narrative + tables + images | Atomic, queryable data units |
| Single monolithic document | Modular files that can be selectively loaded |

---

## The 11-File Schema

### File Index

| # | Filename | Category | Contents |
|---|----------|----------|----------|
| 00 | `00-overview.md` | **Meta** | Score, status, recommendation, quick assessment |
| 01 | `01-profile-overview.md` | **Synthesis** | Elevator pitch, overall strengths, overall weaknesses |
| 02 | `02-contact.md` | **Facts** | Email, phone, LinkedIn, other contact info |
| 03 | `03-work-experience.md` | **History** | Full work history with company, dates, responsibilities |
| 04 | `04-education.md` | **History** | Degrees, certifications, institutions, dates |
| 05 | `05-awards-and-achievements.md` | **Signal** | Honors, hackathons, quantified accomplishments |
| 06 | `06-tools.md` | **Skills** | Technologies, platforms, tools (raw list) |
| 07 | `07-hard-skills.md` | **Skills** | Technical competencies (categorized) |
| 08 | `08-soft-skills.md` | **Skills** | Interpersonal, leadership, collaboration skills |
| 09 | `09-hobbies.md` | **Color** | Personal interests, non-work activities |
| 10 | `10-responsibilities-assessment.md` | **Analysis** | JD requirement fit analysis with ratings, evidence |
| -- | `media/` | **Assets** | Screenshots, images from original document |
| -- | `README.md` | **Index** | File manifest, key metrics, quick reference |

---

## Category Definitions

### Meta (00)
**Purpose:** Enable fast triage without reading full profile.

**Contains:**
- Overall score/rating
- Qualification status (Well-aligned, Marginal, Not aligned)
- One-line recommendation
- Key probe areas

**Source:** Usually the summary box or header section of the Careerspan doc.

---

### Synthesis (01)
**Purpose:** Pre-digested analysis—what the data adds up to.

**Contains:**
- Elevator pitch (2-4 sentences on what you get)
- Overall strengths (narrative, evidence-linked)
- Overall weaknesses (narrative, evidence-linked)

**Source:** "Profile Overview" tab or summary section.

**Key principle:** This is *judgment*, not *data*. The Careerspan analyst has already synthesized—we're capturing that synthesis.

---

### Facts (02)
**Purpose:** Objective, verifiable information.

**Contains:**
- Email, phone, LinkedIn
- Location (if available)
- Any other contact/identity info

**Source:** Contact section of the doc.

**Extraction rule:** No interpretation—verbatim extraction.

---

### History (03, 04)
**Purpose:** Timeline of what the candidate has done.

**03 (Work Experience) contains:**
- Company name
- Title
- Dates (start - end or "Present")
- Responsibilities/accomplishments (narrative)

**04 (Education) contains:**
- Institution
- Degree/certification
- Dates
- Field of study

**Source:** Experience Summary tab, Education section.

**Extraction rule:** Preserve chronological order (most recent first). Keep narrative intact—don't over-structure.

---

### Signal (05)
**Purpose:** Standout achievements that differentiate.

**Contains:**
- Awards and honors
- Hackathon results
- Quantified accomplishments
- Rankings/percentiles

**Source:** Awards & Honors section, scattered throughout narratives.

**Key principle:** This is the "remarkable" data—things a typical resume wouldn't highlight or that validate exceptional ability.

---

### Skills (06, 07, 08)
**Purpose:** What the candidate can do (claimed or demonstrated).

**06 (Tools):** Raw technology list—AWS, Kubernetes, React, etc.
- Extraction rule: Preserve as flat list, no categorization

**07 (Hard Skills):** Technical competency categories
- Examples: Machine Learning, CI/CD, System Architecture
- These are *capability claims*, not just tool familiarity

**08 (Soft Skills):** Interpersonal and leadership
- Examples: Team Leadership, Mentoring, Stakeholder Management
- Often harder to validate—note if story-backed

**Source:** Dedicated Skills sections, Tools section.

---

### Color (09)
**Purpose:** Humanizing information that may signal culture fit.

**Contains:**
- Hobbies and interests
- Non-work activities
- Personal projects

**Source:** Hobbies section.

**Key principle:** Don't dismiss this—"150+ plant collector" signals patience and care; "12+ years following a football club" signals loyalty and sustained interest. This is culture fit data.

---

### Analysis (10)
**Purpose:** Structured job-requirement fit assessment.

**Contains:**
For each JD responsibility:
- Rating (Excellent/Good/Fair/Poor)
- Required level (1-5)
- Importance (1-10)
- Evidence source (Story/Resume/Profile)
- "Our Take" narrative with specific evidence
- Contributing skills
- Support stories (with Story ID, type, score)
- Resume match rating

**Source:** "Responsibilities" tab of Careerspan doc (often includes screenshot/table).

**Key principle:** This is the most valuable data for output generation. It's where Careerspan's analysis engine has already matched candidate to JD.

---

## Extraction Process

### Step 1: Document Acquisition
```
Input: Google Doc URL
Action: Download via Google Drive API as .docx, convert to .md
Output: google_doc.md (raw markdown), google_doc.docx (original)
```

### Step 2: Tab/Section Identification
```
Identify logical sections in the document:
- Profile Overview → 01
- Contact → 02
- Experience Summary → 03, 04, 05
- Tools/Skills → 06, 07, 08
- Hobbies → 09
- Responsibilities → 10
```

### Step 3: Atomic Extraction
```
For each section:
1. Create target file with YAML frontmatter
2. Extract content verbatim (preserve formatting)
3. Add source attribution
4. Handle embedded images → media/
```

### Step 4: Meta Generation
```
Generate 00-overview.md from:
- Score (if present in doc)
- Status/recommendation (if present)
- Synthesize "probe areas" from weaknesses section
```

### Step 5: README Generation
```
Create README.md with:
- Source document link
- Extraction date
- File manifest with descriptions
- Key metrics summary
- Quick assessment
```

---

## Frontmatter Standard

Every file must include:

```yaml
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: <conversation_id>
source: <google_doc_url> [optional: (tab name)]
---
```

---

## When to Decompose vs. Keep Whole

**Decompose when:**
- Document has distinct tabs/sections that serve different purposes
- Downstream tasks need selective loading (e.g., "just give me skills")
- File would exceed ~5KB if kept whole

**Keep whole when:**
- Content is short and atomic already
- No clear categorical boundaries
- Splitting would lose important context

---

## Quality Checks

Before considering decomposition complete:

- [ ] All tabs/sections from source accounted for
- [ ] No content lost in extraction
- [ ] Images saved to media/ with correct paths
- [ ] Frontmatter on all files
- [ ] README accurately indexes all files
- [ ] Score/recommendation captured in 00-overview.md
- [ ] Responsibilities assessment (10) includes ratings and evidence

---

## Usage Notes

### For Output Generation
- Start with `00-overview.md` for triage
- Load `01-profile-overview.md` for synthesis (Thesis panel)
- Load `10-responsibilities-assessment.md` for JD fit (Hard Skills panel)
- Load `05-awards-and-achievements.md` for differentiators
- Cross-reference `03-work-experience.md` for evidence anchoring

### For Retrieval
- Files are designed to be selectively loaded
- ~2-5KB per file keeps token usage manageable
- Can load all 11 files for comprehensive analysis (~30KB total)

---

## Relationship to Anti-Resume Output Framework

This **Decomposition Framework** is the **input pipeline**.
The **Anti-Resume Output Framework** is the **output template**.

```
Raw Careerspan Doc
       ↓
[Decomposition Framework]
       ↓
11 Structured Files
       ↓
[Analysis + JD Context]
       ↓
[Anti-Resume Output Framework]
       ↓
Candidate Profile Page
```

---

*Careerspan Proprietary Framework*
