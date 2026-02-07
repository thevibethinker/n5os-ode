---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_eVfYGwoqnltAwS7i
---

# JD Intake Link Protocol

## When it fires
- Shivam now sometimes sends `[JD]` emails that include a link (e.g., Ashby, Greenhouse) instead of a file attachment.
- Treat those emails the same as attachments: the goal is to capture the JD text, generate a structured Hiring POV, and continue the usual intake flow.

## Steps
1. **Record the link:** copy the URL from the email (e.g., `https://jobs.ashbyhq.com/glide/...`).
2. **Fetch the page:** run `read_webpage` or open it via Zo's browser and save a markdown snapshot in `read_webpage/`. The resulting markdown is the canonical source of truth for that JD (e.g., `read_webpage/jobs.ashbyhq.com~~2fglide~~2f...md`).
3. **Normalize the text:** copy the markdown into a plain-text file (our example is `glide_software_engineering_manager_jd.txt` inside the current conversation workspace). Strip out placeholder lines and images so the JD is just the prose.
4. **Generate the POV:** run the canonical generator:

   ```bash
   python3 Skills/careerspan_hiring_intel/scripts/hiring_pov.py \
     --jd-file <plain-text-jd> \
     --employer "<employer name>" \
     --role "<role title>" \
     --output-json <path>.json \
     --output-md <path>.md
   ```

   Store the markdown output for later review (e.g., `glide_hiring_pov.md`).
5. **Attach to intake:** link the markdown or JSON paths in the JD intake Airtable record and share the POV with Shivam when we reply. If the JD still lacks key answers, note them in `missing_info` and ask the same Core Questions we normally send.
6. **Document for automation:** update the intake script (e.g., `Skills/careerspan-jd-intake/scripts/process_jd.py`) to accept either attachments or links, fetch the link content via `read_webpage`, and pass the resulting text to `generate_hiring_pov_with_markdown()`.

## Notes
- Keep a record of the link snapshot in the conversation workspace (the timestamped markdown saved by `read_webpage` is enough).
- Use the same validation questions we rely on for attachments; nothing changes besides where the text originates.
- When replying to Shivam, mention that we captured the Ashby link and generated the POV from the published page.

## Automation status
- **Implemented:** The automated JD intake script now supports link-based JDs (Ashby/Greenhouse/Lever), and it generates a branded PDF Hiring POV via Skills/branded-pdf when available, uploading both MD + PDF + cleaned JD text to Drive.
- **Requires orchestrator support:** Placeholders for any additional steps or integrations that are not yet automated.
