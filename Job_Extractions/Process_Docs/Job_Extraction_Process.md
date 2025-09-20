# Job Description Extraction Process for Customer Success Roles

## Overview
This process outlines the steps to extract full job descriptions for customer success roles in fintech companies located in New York, focusing on recent postings (within the last week). The output is generated in Markdown format to ensure clarity, readability, and direct fidelity to the source material.
## File Structure for Storage
All job extractions and related files are stored in a dedicated directory structure under `/home/workspace/Job_Extractions/` to maintain organization and facilitate future access.

### Directory Layout
- **Recent_Searches/**: For active, ongoing extractions.
  - **Fintech_NYC_Customer_Success/**: Subfolder for the specific search category.
    - **YYYY-MM-DD/**: Dated subfolders for each extraction session (e.g., 2025-09-20).
      - Individual job folders: Named by job title or unique ID.
        - `job_description.md`: Markdown file with extracted content.
        - `source_page.html`: Saved webpage file (if extracted).
  - **Other_Categories/**: For different search types if needed.
- **Archived_Jobs/**: For completed or historical extractions.
  - **By_Company/**: Subfolders by company name.
  - **By_Date/**: Subfolders by extraction date.
  - **By_Role_Type/**: Subfolders by role type (e.g., Customer_Success_Manager).
- **Process_Docs/**: For process documentation and updates.
  - `Job_Extraction_Process.md`: This document.
  - Other related guides.- **Individual Job Files**: Each job is saved as a separate Markdown file in the batch folder (e.g., `watershed_customer_success_manager_enterprise.md`), enabling flexible referencing in conversations using `file '<path>'`.

### Integration into Process
- After extraction, create the appropriate directories if they don't exist.
- Save each job's Markdown output and any downloaded files to the structured path.
- Update paths in the output document to reference the stored files.
- Maintain the structure to avoid clutter and enable easy retrieval.

## Key Principles
- **No Hallucinations**: Only extract and present information directly from the source pages. Do not add, interpret, approximate, or invent any content.
- **No Approximations**: Use exact dates, locations, and details as provided on the job pages. If a date is not specified, note it as "not specified" without estimating.
- **No Rounding Down or Inserting**: Include the full text of job descriptions verbatim. Do not summarize, shorten, or modify the content unless absolutely necessary for formatting (e.g., removing HTML artifacts while preserving meaning).
- **No Interpreting**: Present the content as-is. Do not draw conclusions, add context, or explain terms unless they are part of the original description.

## Steps to Follow
1. **Job Search**:
   - Use `web_search` tool with targeted queries to find recent customer success roles in fintech/NYC.
   - Example queries:
     - "customer success roles fintech New York last week"
     - "fintech customer success manager jobs NYC posted last 7 days"
     - "fintech startup customer success New York job openings last week"
   - Set time_range to "week" to focus on recent postings.
   - Collect URLs from non-LinkedIn sources to avoid potential access issues.
   - Create a dated subfolder under `Job_Extractions/Recent_Searches/Fintech_NYC_Customer_Success/YYYY-MM-DD/` for the session.

2. **Selection**:
   - Randomly select 3 URLs that match the criteria (customer success, fintech-related, New York, recent).
   - Prioritize accessible job boards like BuiltInNYC, Ziprecruiter, Indeed, etc.
   - Skip any sites that require captcha, premium access, or are behind paywalls.

3. **Extraction**:
   - Use `read_webpage` tool on each selected URL to retrieve the full page content.
   - Extract the job description section verbatim, including all subsections, bullet points, and details.
   - Capture key metadata: title, company, location, posted date (exact if available), URL.

4. **Output Generation**:
   - Compile the extracted content into a Markdown document.
   - Structure:
     - Top-level header: "# Customer Success Manager Roles in Fintech NYC"
     - For each job: Subheader with title, company, location, posted date, URL.
     - Include the full description in a code block or formatted text, preserving original structure.
   - Ensure the Markdown is valid and readable, but do not alter the content.
   - Save the compiled Markdown to `Job_Extractions/Recent_Searches/Fintech_NYC_Customer_Success/YYYY-MM-DD/extracted_jobs.md`.
   - For each job, create a subfolder (e.g., `job_title_cleaned/`) and save individual Markdown files and source HTML if available.   - Save each job as a separate Markdown file directly in the batch folder (e.g., `YYYY-MM-DD/job_title.md`) for easy access.

5. **Quality Check**:
   - Verify that all extracted text is directly from the source.
   - If a page is incomplete or inaccessible, skip and select another.
   - Do not include any generated summaries or AI interpretations.

## Example Output Structure
```
# Customer Success Manager Roles in Fintech NYC

## 1. [Job Title] - [Company]
**Company:** [Company Name]  
**Location:** [Location]  
**Posted:** [Exact Date or "not specified"]  
**Job URL:** [URL]  

[Full verbatim job description here]
```

## Tools Used
- `web_search`: For initial job discovery.
- `read_webpage`: For extracting full page content.
- `create_or_rewrite_file`: To save the final Markdown output.

This process ensures accurate, unaltered extraction of job descriptions while maintaining efficiency and avoiding any subjective additions.

## Maintenance
- Archive completed extractions by moving folders from Recent_Searches to Archived_Jobs.
- Regularly review and clean up outdated files.
- Update this process document as needed in Process_Docs/.

## Change Log
- **2025-09-20**: Initial process document created.
- **2025-09-20**: Added file structure section for storage organization.
- **2025-09-20**: Updated to adhere to existing file base, moved document to Process_Docs, created subdirectories.
- **2025-09-20**: Implemented individual job files in batch folders for flexible referencing.
- **2025-09-20**: Updated output generation to save separate files per job in batch folder.
