#!/usr/bin/env python3
"""
PDF extraction script for career coaching materials
Extracts text from all PDFs and creates markdown files with frontmatter
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import re

# File mappings from the brief
FILE_MAPPINGS = [
    ("Summary of _Peeling the Career Services Onion_ White Paper.pdf", "1v_WiU4EfnDiGnafLVUbIhug7Ovrv6_mm"),
    ("Essential Career Development Statistics and Data Points v2.0.pdf", "1wuUcHn_eVaYOMuJOf22yI_xQgXtFK9Im"),
    ("How ATS Systems Work - A Primer.pdf", "1wVfUvuZUm1XzYCNKeQrqGs9pOGeHgOPJ"),
    ("ALERT - INSERT ME INTO THE PROJECT LEVEL INSTRUCTIONS - prompting file.txt", "1wvT1Ou7-WQt0sxwqsJBcKoggHg9ACvlR"),
    ("The AISS Resume Bullet Construction Principle.pdf", "1wNROkMC6ez2XIhEtFN0v-J7hGoRS7mOL"),
    ("On Breaking Into New Industries or Roles.pdf", "1wTsPlgVCeQkkaswpm-0mXrSJnkfQJTIP"),
    ("On Self Reflection and Its Relevance to Careers.pdf", "1wrourIsLjuiOV96oIlRPd1EUxNrybVei"),
    ("On LinkedIn and The Reality Thereof.pdf", "1ve5hF5SBGmqRbttmKftEtARjoixEqK4l"),
    ("On Networking in the Modern Era.pdf", "1wtNMF4SjHcmNqtKRcR4WIIiFqq19ihzQ"),
    ("On Resume Customization.pdf", "1wCvKbJUs47qhHVpsclbEj-pnc4lMRkFv"),
    ("Tactical Career and Job Hunting Advice from Damon Cassidy Podcast Interview.pdf", "1vaxgrLMM_SlF0SXttIQeGg5t_UuDwDT2"),
    ("Advice for the Modern Jobseeker with The ApplyAI.pdf", "1wYMoIHwpdnQlQ0MeHIcSG3vEIxZjpIoo"),
    ("How to get an Internship that will (actually) help your career.pdf", "1vdINNQhM8vh8lZGgSsDwNhhvjcyKUwk_"),
    ("Emory University Presentation - Using AI to create great cover letters.pptx.pdf", "1wtOhrem2y0OKf0tDG7gqT0hhqO0hIyOk"),
    ("The Art of Career Preparation_ A Strategic Guide to Job Search Readiness.pdf", "1vvmtpNRTJ5mN5tBBrOJdLyXm-QXP2CAk"),
    ("Beyond Keywords_ The Modern Guide to Resume Optimization.pdf", "1w2bICindQ1OJtgcciNCzMM1zx3lMaTC2"),
    ("The Strategic Guide to Modern Cover Letters_ When, Why, and How.pdf", "1wAIx3PuxhKOlBXQTrsPHr7o8wlCm_keZ"),
    ("Prompting Claude for LinkedIn.pdf", "1vYi7EIwpIJN6SZzpfLfelLI2mh_EUXN9"),
    ("Cover Letter Guide - with commentary.docx.pdf", "1x48XlqyYyQJfDenj6T3gmvx8KatJTT32"),
    ("Materials Preparation (OG).pdf", "1wDJyzZ8vTPsQ4pvlAsAcfcnMjZZtBxaH"),
    ("Job Hunt Materials Preparation Advice 1.0.pdf", "1x4BVupcKqXl3gydiEFMerVJdlHeHrcGu"),
    ("The Art of The Brag.pdf", "1vpjtebX6YauBmPOdtJW7wyrDvrp9-WoA"),
    ("Public Facing Stats v 1.0.pdf", "1w9B1J67kYR4jfiWoN0JbC_KbylOAo3gP"),
    ("V Thoughts on the Job Market v1.0.pdf", "1wtIvMsqGDQCnLFeGNiMq6Olqqd41Rd6g")
]

def sanitize_filename(filename):
    """Convert filename to safe markdown filename"""
    # Remove extension
    name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    # Replace problematic characters with hyphens
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    name = name.strip('-').lower()
    return f"{name}.md"

def extract_pdf_text(pdf_path):
    """Extract text from PDF using pdftotext"""
    try:
        result = subprocess.run(['pdftotext', '-layout', str(pdf_path), '-'], 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error extracting from {pdf_path}: {e}")
        return None
    except FileNotFoundError:
        print("pdftotext not found, installing poppler-utils...")
        subprocess.run(['apt', 'update'], check=True)
        subprocess.run(['apt', 'install', '-y', 'poppler-utils'], check=True)
        try:
            result = subprocess.run(['pdftotext', '-layout', str(pdf_path), '-'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout
        except Exception as e:
            print(f"Failed to extract from {pdf_path} even after installing tools: {e}")
            return None

def extract_text_file(txt_path):
    """Read text from TXT file"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {txt_path}: {e}")
        return None

def create_markdown_file(text_content, original_filename, source_id, output_path):
    """Create markdown file with frontmatter"""
    if not text_content:
        return False
    
    frontmatter = f"""---
source_file: {original_filename}
source_id: {source_id}
extracted: {datetime.now().strftime('%Y-%m-%d')}
provenance: career-coaching-hotline/D1.1
---

"""
    
    # Clean up the text content a bit
    lines = text_content.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Skip empty lines for now
            cleaned_lines.append(line)
    
    # Add title if we can infer it
    title = original_filename.replace('.pdf', '').replace('.txt', '')
    title = title.replace('_', ' ')
    
    content = frontmatter + f"# {title}\n\n" + '\n\n'.join(cleaned_lines)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {output_path}: {e}")
        return False

def count_words(text):
    """Count words in text"""
    return len(text.split()) if text else 0

def main():
    source_dir = Path("/home/workspace/N5/builds/career-coaching-hotline/artifacts/source-pdfs")
    extract_dir = Path("/home/workspace/N5/builds/career-coaching-hotline/artifacts/extracted")
    
    # Ensure extract directory exists
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "extracted": datetime.now().isoformat(),
        "total_files": len(FILE_MAPPINGS),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "files": []
    }
    
    for original_filename, source_id in FILE_MAPPINGS:
        print(f"Processing: {original_filename}")
        
        # Find the actual file (may have slight name variations due to download)
        source_files = list(source_dir.glob(f"*{original_filename.split('.')[0].replace('(', '?').replace(')', '?')}*"))
        if not source_files:
            # Try more flexible matching
            base_name = original_filename.split('.')[0][:20]  # First 20 chars
            source_files = list(source_dir.glob(f"*{base_name}*"))
        
        if not source_files:
            print(f"  ❌ Source file not found")
            manifest["failed_extractions"] += 1
            manifest["files"].append({
                "original_filename": original_filename,
                "source_id": source_id,
                "status": "source_not_found",
                "word_count": 0
            })
            continue
        
        source_path = source_files[0]  # Use first match
        output_filename = sanitize_filename(original_filename)
        output_path = extract_dir / output_filename
        
        # Extract text based on file type
        if source_path.suffix.lower() == '.pdf':
            text_content = extract_pdf_text(source_path)
        elif source_path.suffix.lower() == '.txt':
            text_content = extract_text_file(source_path)
        else:
            print(f"  ❌ Unsupported file type: {source_path.suffix}")
            text_content = None
        
        if text_content and create_markdown_file(text_content, original_filename, source_id, output_path):
            word_count = count_words(text_content)
            print(f"  ✅ Extracted successfully ({word_count:,} words)")
            manifest["successful_extractions"] += 1
            manifest["files"].append({
                "original_filename": original_filename,
                "source_id": source_id,
                "extracted_filename": output_filename,
                "status": "success",
                "word_count": word_count,
                "detected_topics": []  # Will be populated later if needed
            })
        else:
            print(f"  ❌ Extraction failed")
            manifest["failed_extractions"] += 1
            manifest["files"].append({
                "original_filename": original_filename,
                "source_id": source_id,
                "status": "extraction_failed",
                "word_count": 0
            })
    
    # Write manifest
    manifest_path = Path("/home/workspace/N5/builds/career-coaching-hotline/artifacts/extraction-manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nExtraction complete!")
    print(f"✅ Successful: {manifest['successful_extractions']}")
    print(f"❌ Failed: {manifest['failed_extractions']}")
    print(f"📄 Manifest saved to: {manifest_path}")

if __name__ == "__main__":
    main()