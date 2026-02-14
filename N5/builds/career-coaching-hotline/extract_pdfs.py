import os
import json
import datetime
import subprocess

SOURCE_DIR = "/home/workspace/N5/builds/career-coaching-hotline/artifacts/source-pdfs/"
EXTRACTED_DIR = "/home/workspace/N5/builds/career-coaching-hotline/artifacts/extracted/"
MANIFEST_PATH = "/home/workspace/N5/builds/career-coaching-hotline/artifacts/extraction-manifest.json"

FILES_MAP = {
    "Summary of _Peeling the Career Services Onion_ White Paper.pdf": "1v_WiU4EfnDiGnafLVUbIhug7Ovrv6_mm",
    "Essential Career Development Statistics and Data Points v2.0.pdf": "1wuUcHn_eVaYOMuJOf22yI_xQgXtFK9Im",
    "How ATS Systems Work - A Primer.pdf": "1wVfUvuZUm1XzYCNKeQrqGs9pOGeHgOPJ",
    "ALERT - INSERT ME INTO THE PROJECT LEVEL INSTRUCTIONS - prompting file.txt": "1wvT1Ou7-WQt0sxwqsJBcKoggHg9ACvlR",
    "The AISS Resume Bullet Construction Principle.pdf": "1wNROkMC6ez2XIhEtFN0v-J7hGoRS7mOL",
    "On Breaking Into New Industries or Roles.pdf": "1wTsPlgVCeQkkaswpm-0mXrSJnkfQJTIP",
    "On Self Reflection and Its Relevance to Careers.pdf": "1wrourIsLjuiOV96oIlRPd1EUxNrybVei",
    "On LinkedIn and The Reality Thereof.pdf": "1ve5hF5SBGmqRbttmKftEtARjoixEqK4l",
    "On Networking in the Modern Era.pdf": "1wtNMF4SjHcmNqtKRcR4WIIiFqq19ihzQ",
    "On Resume Customization.pdf": "1wCvKbJUs47qhHVpsclbEj-pnc4lMRkFv",
    "Tactical Career and Job Hunting Advice from Damon Cassidy Podcast Interview.pdf": "1vaxgrLMM_SlF0SXttIQeGg5t_UuDwDT2",
    "Advice for the Modern Jobseeker with The ApplyAI.pdf": "1wYMoIHwpdnQlQ0MeHIcSG3vEIxZjpIoo",
    "How to get an Internship that will (actually) help your career.pdf": "1vdINNQhM8vh8lZGgSsDwNhhvjcyKUwk_",
    "Emory University Presentation - Using AI to create great cover letters.pptx.pdf": "1wtOhrem2y0OKf0tDG7gqT0hhqO0hIyOk",
    "The Art of Career Preparation_ A Strategic Guide to Job Search Readiness.pdf": "1vvmtpNRTJ5mN5tBBrOJdLyXm-QXP2CAk",
    "Beyond Keywords_ The Modern Guide to Resume Optimization.pdf": "1w2bICindQ1OJtgcciNCzMM1zx3lMaTC2",
    "The Strategic Guide to Modern Cover Letters_ When, Why, and How.pdf": "1wAIx3PuxhKOlBXQTrsPHr7o8wlCm_keZ",
    "Prompting Claude for LinkedIn.pdf": "1vYi7EIwpIJN6SZzpfLfelLI2mh_EUXN9",
    "Cover Letter Guide - with commentary.docx.pdf": "1x48XlqyYyQJfDenj6T3gmvx8KatJTT32",
    "Materials Preparation (OG).pdf": "1wDJyzZ8vTPsQ4pvlAsAcfcnMjZZtBxaH",
    "Job Hunt Materials Preparation Advice 1.0.pdf": "1x4BVupcKqXl3gydiEFMerVJdlHeHrcGu",
    "The Art of The Brag.pdf": "1vpjtebX6YauBmPOdtJW7wyrDvrp9-WoA",
    "Public Facing Stats v 1.0.pdf": "1w9B1J67kYR4jfiWoN0JbC_KbylOAo3gP",
    "V Thoughts on the Job Market v1.0.pdf": "1wtIvMsqGDQCnLFeGNiMq6Olqqd41Rd6g"
}

def find_file(filename):
    # Try exact match
    path = os.path.join(SOURCE_DIR, filename)
    if os.path.exists(path):
        return path
    
    # Try sanitization (replace parens with hyphens)
    sanitized = filename.replace("(", "-").replace(")", "-")
    path = os.path.join(SOURCE_DIR, sanitized)
    if os.path.exists(path):
        return path
    
    # Try primitive fuzzy match (first 10 chars)
    prefix = filename[:10]
    files = os.listdir(SOURCE_DIR)
    for f in files:
        if f.startswith(prefix):
             return os.path.join(SOURCE_DIR, f)
    
    return None

manifest = []

for filename, file_id in FILES_MAP.items():
    filepath = find_file(filename)
    if not filepath:
        print(f"Warning: Could not find file for {filename}")
        continue
    
    print(f"Processing {filepath}...")
    
    text = ""
    try:
        if filepath.endswith(".txt"):
            with open(filepath, 'r') as f:
                text = f.read()
        else:
            # Use pdftotext
            result = subprocess.run(['pdftotext', '-layout', filepath, '-'], capture_output=True, text=True)
            if result.returncode == 0:
                text = result.stdout
            else:
                print(f"Error processing {filepath}: {result.stderr}")
                text = ""
    except Exception as e:
        print(f"Exception processing {filepath}: {e}")
        text = ""
        
    word_count = len(text.split())
    
    # Create markdown
    # Sanitize output filename to avoid spaces and ensure valid markdown reference
    safe_name = os.path.basename(filepath).replace(" ", "_").replace(".pdf", "").replace(".txt", "") + ".md"
    md_path = os.path.join(EXTRACTED_DIR, safe_name)
    
    frontmatter = f"""---
source_file: "{filename}"
source_id: "{file_id}"
extracted: "{datetime.date.today().isoformat()}"
provenance: "career-coaching-hotline/D1.1"
word_count: {word_count}
---

"""
    with open(md_path, 'w') as f:
        f.write(frontmatter + text)
        
    manifest.append({
        "original_filename": filename,
        "file_id": file_id,
        "extracted_filename": safe_name,
        "word_count": word_count,
        "status": "success" if text else "failed"
    })

with open(MANIFEST_PATH, 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"Extraction complete. Manifest written to {MANIFEST_PATH}")
