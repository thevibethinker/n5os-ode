#!/usr/bin/env python3
"""
N5OS-Aligned Transcript Processing Workflow Prototype

Processes a provided text transcript into a content map and generates custom outputs 
for internal/external meetings. Outputs to JSONL for queryability.

Usage: python transcript_processor.py <transcript_path> --type <internal|external> --output_dir <dir>

Dependencies: json, datetime (standard libs). For voice fidelity, placeholder used—expand later.
"""

import json
import sys
import os
from datetime import datetime

# Placeholder for MasterVoiceSchema (to be integrated from system-level file)
MASTER_VOICE = {
    "tone": "professional, concise, action-oriented",
    "diction": "clear, vivid, resonant details",
    "signoff": "Best regards,\nV"
}

# Placeholder for Essential Links (to be pulled from system-level reference)
ESSENTIAL_LINKS = {
    "careerspan_site": "https://careerspan.com",
    "demo_link": "https://careerspan.com/demo"
}

def parse_transcript(transcript_text):
    """Step 1: Parse transcript into segments (simplified from chunk1_parser.py)."""
    # Dummy parsing: Split by lines, extract speakers/topics (expand with NLP later)
    segments = []
    lines = transcript_text.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            speaker = line.split(':')[0] if ':' in line else "Unknown"
            content = line.split(':', 1)[1] if ':' in line else line
            segments.append({
                "timestamp": i,  # Placeholder
                "speaker": speaker.strip(),
                "content": content.strip()
            })
    return segments

def generate_content_map(segments, meeting_type):
    """Step 2: Build content map with key extractions."""
    content_map = {
        "meeting_type": meeting_type,
        "decisions": [],  # e.g., ["Decision: Proceed with Q3 plan"]
        "conflicts": [],  # e.g., ["Disagreement on budget"]
        "agreements": [],  # e.g., ["Alignment on goals"]
        "next_steps": [],  # e.g., ["Action: Follow up by Friday"]
        "insights": [],   # e.g., ["Key idea: Market shift in AI"]
        "entities": [],   # e.g., [{"name": "John Doe", "context": "Potential intro"}]
        "quotes": [],     # e.g., [{"speaker": "V", "quote": "Let's connect them"}]
        "intro_opportunities": []  # e.g., [{"person1": "A", "person2": "B", "reason": "Shared interest", "platform": "LinkedIn"}]
    }
    
    # Dummy extraction logic (replace with AI/NLP)
    for seg in segments:
        if "decision" in seg["content"].lower():
            content_map["decisions"].append(seg["content"])
        if "disagree" in seg["content"].lower():
            content_map["conflicts"].append(seg["content"])
        if "agree" in seg["content"].lower():
            content_map["agreements"].append(seg["content"])
        if "next" in seg["content"].lower() or "action" in seg["content"].lower():
            content_map["next_steps"].append(seg["content"])
        if "idea" in seg["content"].lower() or "insight" in seg["content"].lower():
            content_map["insights"].append(seg["content"])
        if "introduce" in seg["content"].lower() or "connect" in seg["content"].lower():
            content_map["intro_opportunities"].append({
                "reason": seg["content"],
                "platform": "LinkedIn"  # Default
            })
    
    return content_map

def generate_outputs(content_map, meeting_date):
    """Step 3: Generate emails, intros, summaries in voice."""
    outputs = []
    
    # Calculate delay
    now = datetime.now()
    days_elapsed = (now - meeting_date).days  # Assuming meeting_date is datetime
    apology = f"I apologize for the delayed follow-up—it's been {days_elapsed} days since our discussion." if days_elapsed > 2 else ""
    
    # Follow-up Email (adapted from v10.6 structure)
    if content_map["meeting_type"] == "external":
        email_draft = f"""
Subject: Follow-Up Email – [Recipient] x Careerspan [Keyword1 • Keyword2]

Dear [Recipient],

{apology}

[Resonance Intro: Vivid recap of key moments]

Recap:
- [Bullet from agreements/decisions]

Next Steps:
- [Bullet from next_steps]

{MASTER_VOICE["signoff"]}
"""
        outputs.append({"type": "email_draft", "content": email_draft})
    
    # Warm Intro Draft
    for intro in content_map["intro_opportunities"]:
        intro_draft = f"""
[Platform: LinkedIn Message]

Hi [Person1 and Person2],

I'm connecting you because {intro['reason']}. [Brief why each is great].

Best,
V
"""
        outputs.append({"type": "warm_intro", "content": intro_draft})
    
    # Knowledge Summary
    summary = "## Meeting Summary\n\nInsights:\n" + "\n".join(f"- {i}" for i in content_map["insights"])
    outputs.append({"type": "knowledge_summary", "content": summary})
    
    return outputs

def validate_outputs(content_map, outputs):
    """Step 4: Basic validation."""
    validation = {
        "accuracy": len(content_map["insights"]) > 0,  # Dummy check
        "issues": [] if len(content_map["insights"]) > 0 else ["Low insight count"]
    }
    return validation

def main(transcript_path, meeting_type, output_dir, meeting_date_str="2025-09-20"):
    if not os.path.exists(transcript_path):
        print(f"Error: Transcript file not found: {transcript_path}")
        sys.exit(1)
    
    with open(transcript_path, 'r') as f:
        transcript_text = f.read()
    
    segments = parse_transcript(transcript_text)
    content_map = generate_content_map(segments, meeting_type)
    meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%d")  # Placeholder
    outputs = generate_outputs(content_map, meeting_date)
    validation = validate_outputs(content_map, outputs)
    
    # Save to JSONL
    output_path = os.path.join(output_dir, "processed.jsonl")
    with open(output_path, 'w') as f:
        for item in [content_map] + outputs + [validation]:
            f.write(json.dumps(item) + '\n')
    
    print(f"Prototype processing complete. Outputs saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python transcript_processor.py <transcript_path> --type <internal|external> --output_dir <dir>")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    meeting_type = sys.argv[3]  # Simplified arg parsing
    output_dir = sys.argv[5]
    main(transcript_path, meeting_type, output_dir)
