---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_g62UmSAYGCHuZjmN
---
# WORKER ASSIGNMENT: Coaching Content Ingestion

**Assigned to:** Zo (Knowledge Architect)
**Objective:** Ingest Vrijen's complete coaching data dump into the permanent Knowledge Library.

## Context
V has provided a comprehensive set of coaching PDFs and text files covering resumes, networking, interviewing, and career strategy. These need to be preserved, indexed, and structured for future use by all system agents.

## Input Files
The files are currently located in `/home/.z/chat-uploads/`.
Key files include:
- Summary of _Peeling the Career Services Onion_ White Paper.pdf
- Essential Career Development Statistics and Data Points v2.0.pdf
- How ATS Systems Work - A Primer.pdf
- The AISS Resume Bullet Construction Principle.pdf
- On Breaking Into New Industries or Roles.pdf
- On Self Reflection and Its Relevance to Careers.pdf
- On LinkedIn and The Reality Thereof.pdf
- On Networking in the Modern Era.pdf
- On Resume Customization.pdf
- Advice for the Modern Jobseeker with The ApplyAI.pdf
- How to get an Internship that will (actually) help your career.pdf
- ... and others in the chat-uploads folder.

## Mission
1. **Catalog:** List all provided files.
2. **Ingest:** For each file:
   - Read the content.
   - Create a markdown copy in `Knowledge/content-library/coaching/`.
   - Use a standardized filename format (e.g., `Knowledge/content-library/coaching/resume-bullet-construction.md`).
   - Add YAML frontmatter with original filename and date.
3. **Structure:** Create a `Knowledge/content-library/coaching/INDEX.md` that categorizes the content into:
   - Resumes & Materials
   - Interviewing
   - Networking & LinkedIn
   - Career Strategy & Philosophy
   - Data & Trends
4. **Clean Up:** (Optional) If safe, move the upload files to an archive or confirm they are saved.

## Deliverables
- A populated `Knowledge/content-library/coaching/` directory.
- A categorized `INDEX.md`.
