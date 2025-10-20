# Job Source Extraction Command

## Quick Usage

Simply send me a job posting URL and I will:

1. **Extract** the full job description using browser rendering (handles JavaScript/Notion pages)
2. **Verify** 100% accuracy by re-reading and comparing
3. **Parse** the structured data (title, location, description, URL)
4. **Update** your Google Drive "sourced jobs" sheet

## Example

```
https://company.notion.site/job-posting
```

I will automatically:
- Use `view_webpage` to get the full rendered content
- Extract: Date, Full Role Title, Location, Full Job Description, Application URL
- Verify the extraction is character-perfect
- Append to your Google Sheet (File ID: 1LMShFZQ7IwZpsOxs1RWB67LHV1cFmClc)

## Verification Process

1. Extract job page HTML + markdown
2. Re-read the extracted markdown
3. Compare against source HTML semantically
4. Confirm all key information is present and accurate
5. Only proceed to Google Drive update if 100% verified

## Google Sheet Format

| Date | Full Role Title | Location | Full Job Description | Application URL |
|------|----------------|----------|---------------------|-----------------|
| 10/13/2025 | Chief of Staff | Montreal | [Full description...] | https://... |

## Supported Job Boards

- Notion pages (e.g., tatosolutions.notion.site)
- Greenhouse (boards.greenhouse.io)
- Lever (jobs.lever.co)
- Workable (apply.workable.com)
- Custom career pages
- Any JavaScript-rendered job posting

## Notes

- Uses browser rendering to handle dynamic content
- Preserves exact formatting and wording
- Double-verification before updating spreadsheet
- Automatic date stamping
- Handles authentication if you're signed in to Zo's browser
