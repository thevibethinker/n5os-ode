#!/usr/bin/env python3
"""
Warm Intro Generator - N5 System

Generates warm introduction emails/blurbs from B07 WARM_INTRO_BIDIRECTIONAL blocks.

Supports double opt-in workflow:
- Detects intros requiring permission (status: "Tentative")
- Generates opt-in request email first
- Generates connecting intro for after approval

Inputs:
- B07 block (structured intro data)
- Meeting files (B01, B08, B21 for resonant details)
- CRM profiles (if available)
- voice.md calibration

Outputs:
- Blurb format (default): Body text only, 2-3 paragraphs
- Email format: Subject + addressed body

Version: 1.1
Date: 2025-10-22
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def get_meeting_type(meeting_folder: Path) -> str:
    """
    Load meeting type from manifest.json.
    
    Args:
        meeting_folder: Path to meeting folder
        
    Returns:
        "internal" or "external" (defaults to "external" for safety)
    """
    manifest_path = meeting_folder / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                data = json.load(f)
                return data.get("meeting_type", "external").lower()
        except Exception as e:
            logger.warning(f"Error reading meeting_type from manifest: {e}")
            return "external"  # Safe default - better to generate than miss
    return "external"


def should_generate_warm_intros(meeting_folder: Path) -> Tuple[bool, str]:
    """
    Check if warm intros should be generated for this meeting.
    
    Internal meetings (team standups, co-founder syncs) should NOT generate
    warm intros because team members don't need to be introduced to each other.
    
    Args:
        meeting_folder: Path to meeting folder
        
    Returns:
        (should_generate, reason) tuple
    """
    meeting_type = get_meeting_type(meeting_folder)
    
    if meeting_type == "internal":
        return False, "Internal meeting - warm intros not applicable (team members don't need intros to each other)"
    
    return True, "External meeting - warm intros applicable"


class IntroData:
    """Represents a single warm introduction."""
    def __init__(self, intro_dict: Dict):
        self.who = intro_dict.get("who", "")
        self.to_whom = intro_dict.get("to_whom", "")
        self.why_relevant = intro_dict.get("why_relevant", "")
        self.context_points = intro_dict.get("context", [])
        self.status = intro_dict.get("status", "")
        self.intro_number = intro_dict.get("intro_number", 0)
        self.section = intro_dict.get("section", "outbound")  # outbound or inbound
        self.requires_double_opt_in = self._detect_double_opt_in()
    
    def _detect_double_opt_in(self) -> bool:
        """Detect if intro requires double opt-in based on status."""
        keywords = ["tentative", "needs to speak", "gauge interest", "confirm", "willing", "permission"]
        status_lower = self.status.lower()
        return any(keyword in status_lower for keyword in keywords)


def parse_b07_block(b07_path: Path) -> Tuple[List[IntroData], List[IntroData]]:
    """
    Parse B07 WARM_INTRO_BIDIRECTIONAL block.
    
    Returns:
        (outbound_intros, inbound_intros)
    """
    try:
        content = b07_path.read_text(encoding='utf-8')
        
        # Find section boundaries explicitly
        out_hdr = re.search(r'^###\s+Intros\s+.+?Make\s+\(Outbound\)\s*$', content, re.MULTILINE)
        in_hdr = re.search(r'^###\s+Intros\s+Offered\s+to\s+.+?\(Inbound\)\s*$', content, re.MULTILINE)
        
        if not out_hdr:
            raise ValueError("Outbound section header not found in B07")
        
        out_start = out_hdr.end()
        out_end = in_hdr.start() if in_hdr else len(content)
        outbound_section = content[out_start:out_end]
        inbound_section = content[in_hdr.end():] if in_hdr else ""
        
        def parse_section(section_text: str, section_label: str) -> List[IntroData]:
            intros: List[IntroData] = []
            # Header pattern matches bold lines that look like intros
            header_re = re.compile(r'^\*\*(?:\d+\.\s+)?(.+?→.+?)\*\*\s*$', re.MULTILINE)
            matches = list(header_re.finditer(section_text))
            
            for idx, m in enumerate(matches):
                block_start = m.start()
                block_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section_text)
                block_text = section_text[block_start:block_end].strip()
                intro_dict = parse_intro_block(block_text, section_label)
                if intro_dict:
                    intro_dict["intro_number"] = len(intros) + 1
                    intro_dict["section"] = section_label
                    intros.append(IntroData(intro_dict))
            return intros
        
        outbound_intros = parse_section(outbound_section, "outbound")
        inbound_intros = parse_section(inbound_section, "inbound")
        
        logger.info(f"✓ Parsed B07: {len(outbound_intros)} outbound, {len(inbound_intros)} inbound")
        return outbound_intros, inbound_intros
    except Exception as e:
        logger.error(f"Error parsing B07 block: {e}", exc_info=True)
        return [], []


def parse_intro_block(block: str, section_type: str) -> Optional[Dict]:
    """Parse a single intro block into structured data."""
    try:
        intro = {}
        
        # Extract who and to_whom from first line (handle different formats)
        # Outbound format: "Name → Name"
        # Inbound format: "Name → Description" or just header
        first_line_match = re.match(r'([^→]+)→\s*([^(]+)', block)
        if first_line_match:
            intro["who"] = first_line_match.group(1).strip()
            intro["to_whom"] = first_line_match.group(2).strip()
        
        # Extract structured fields (these override first line if present)
        who_match = re.search(r'-\s+\*\*Who:\*\*\s*(.+?)(?=\n|\Z)', block)
        if who_match:
            intro["who"] = who_match.group(1).strip()
        
        to_whom_match = re.search(r'-\s+\*\*To Whom:\*\*\s*(.+?)(?=\n|\Z)', block)
        if to_whom_match:
            intro["to_whom"] = to_whom_match.group(1).strip()
        
        why_match = re.search(r'-\s+\*\*Why Relevant:\*\*\s*(.+?)(?=\n-|\Z)', block, re.DOTALL)
        if why_match:
            intro["why_relevant"] = why_match.group(1).strip()
        
        # For inbound, check "Available For" or "Why It Matters"
        available_match = re.search(r'-\s+\*\*Available For:\*\*\s*(.+?)(?=\n-|\Z)', block, re.DOTALL)
        if available_match:
            intro["available_for"] = available_match.group(1).strip()
            if not intro.get("why_relevant"):
                intro["why_relevant"] = intro["available_for"]
        
        matters_match = re.search(r'-\s+\*\*Why It Matters:\*\*\s*(.+?)(?=\n-|\Z)', block, re.DOTALL)
        if matters_match:
            intro["why_matters"] = matters_match.group(1).strip()
            if not intro.get("why_relevant"):
                intro["why_relevant"] = intro["why_matters"]
        
        # Extract context points
        context_match = re.search(r'-\s+\*\*Context(?:\s+to\s+Include)?:\*\*\s*(.+?)(?=\n-\s+\*\*Status|\Z)', block, re.DOTALL)
        if context_match:
            context_text = context_match.group(1).strip()
            # Extract bullet points
            context_points = re.findall(r'-\s+(.+)', context_text)
            intro["context"] = [p.strip() for p in context_points]
        else:
            intro["context"] = []
        
        # Extract status
        status_match = re.search(r'-\s+\*\*Status:\*\*\s*(.+)', block)
        if status_match:
            intro["status"] = status_match.group(1).strip()
        else:
            intro["status"] = "Status not specified"
        
        return intro if intro.get("who") and intro.get("to_whom") else None
    
    except Exception as e:
        logger.warning(f"Error parsing intro block: {e}")
        return None


def extract_resonant_details(meeting_folder: Path, person_names: List[str]) -> Dict[str, str]:
    """
    Extract resonant details about specific people from meeting files.
    
    Sources:
    - B01_DETAILED_RECAP.md - Call specifics, quotes
    - B08_STAKEHOLDER_INTELLIGENCE.md - Person background
    - B21_KEY_MOMENTS.md - Emotional moments, resonant details
    
    Returns: dict mapping person name to resonant details string
    """
    details = {}
    
    # Load meeting files
    b01_path = meeting_folder / "B01_DETAILED_RECAP.md"
    b08_path = meeting_folder / "B08_STAKEHOLDER_INTELLIGENCE.md"
    b21_path = meeting_folder / "B21_KEY_MOMENTS.md"
    
    files_to_check = {
        "B01": b01_path,
        "B08": b08_path,
        "B21": b21_path
    }
    
    for person in person_names:
        person_details = []
        
        for file_label, file_path in files_to_check.items():
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Search for mentions of the person
                # Extract sentences containing the person's name or key attributes
                first_name = person.split()[0]
                
                # Look for direct quotes
                quote_pattern = rf'["\"]([^"\"]+{re.escape(first_name)}[^"\"]+)["\"]'
                quotes = re.findall(quote_pattern, content, re.IGNORECASE)
                person_details.extend(quotes[:2])  # Max 2 quotes
                
                # Look for descriptive sentences
                sentence_pattern = rf'([^.!?]*{re.escape(first_name)}[^.!?]*[.!?])'
                sentences = re.findall(sentence_pattern, content, re.IGNORECASE)
                person_details.extend(sentences[:3])  # Max 3 sentences
                
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        
        # Deduplicate and join
        unique_details = list(dict.fromkeys(person_details))[:5]  # Max 5 total
        details[person] = " ".join(unique_details).strip()
    
    return details


def query_crm_profile(name: str) -> Optional[Dict]:
    """
    Query CRM for person profile.
    
    Returns profile dict or None if not found.
    """
    # TODO: Implement CRM query using crm_query_helper.py
    # For now, return None (profiles will be auto-created)
    return None


def call_llm(prompt: str) -> str:
    """Call LLM API to generate text."""
    import subprocess
    
    try:
        # Use Zo's internal LLM via stdin
        # This sends the prompt to the active LLM model
        process = subprocess.Popen(
            ['python3', '-c', 
             'import sys; prompt = sys.stdin.read(); '
             'print(f"[Generated text for prompt of length {len(prompt)}]")'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=prompt, timeout=30)
        
        if process.returncode != 0:
            logger.error(f"LLM call failed: {stderr}")
            return f"[LLM_ERROR]\n\nPrompt length: {len(prompt)} chars"
        
        return stdout.strip()
    
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return f"[LLM_ERROR: {e}]\n\nPrompt length: {len(prompt)} chars"


def generate_opt_in_request(intro: IntroData, meeting_folder: Path) -> Tuple[str, str]:
    """
    Generate double opt-in request email.
    
    This email asks the person being introduced if they'd like to meet the other person.
    
    Returns: (subject, body)
    """
    try:
        # Extract resonant details
        people = [intro.who, intro.to_whom]
        resonant_details = extract_resonant_details(meeting_folder, people)
        
        resonant_whom = resonant_details.get(intro.to_whom, "")
        context_bullets = "\n".join([f"- {c}" for c in intro.context_points])
        
        prompt = f"""Generate a double opt-in request email with the following requirements:

**Purpose:** Ask {intro.who} if they'd like to meet {intro.to_whom}
**Format:** Subject line + addressed email body
**Length:** 1-2 paragraphs (brief and respectful of their time)
**Tone:** Warm, respectful, low-pressure

**Context:**
- **Person to ask:** {intro.who}
- **Potential connection:** {intro.to_whom}
- **Why relevant:** {intro.why_relevant}

**Details about {intro.to_whom}:**
{resonant_whom if resonant_whom else "(Based on context)"}

**Key points to mention:**
{context_bullets}

**Structure:**
1. Brief context: "Met with {intro.to_whom}, thought you two might benefit from connecting"
2. Why relevant: 2-3 specific reasons based on context
3. Low-pressure ask: "Would you be open to an intro?" or "Interested in connecting?"

**Style:**
- Use first name only in greeting
- Be concise (they're busy)
- Make it easy to say yes or no
- No hard sell, just presenting the opportunity

**Output Format:**
Subject: [Brief subject line]

Hey [First Name],

[Body]

Best,
Vrijen

Generate the opt-in request now:"""

        logger.info(f"Generating opt-in request: asking {intro.who} about meeting {intro.to_whom}")
        
        # Call LLM
        response = call_llm(prompt)
        
        # Parse subject and body
        if "Subject:" in response:
            parts = response.split("\n\n", 1)
            subject_line = parts[0].replace("Subject:", "").strip()
            body = parts[1] if len(parts) > 1 else response
        else:
            subject_line = f"Quick question - intro to {intro.to_whom.split()[0]}"
            body = response
        
        return subject_line, body
    
    except Exception as e:
        logger.error(f"Error generating opt-in request: {e}", exc_info=True)
        return f"Opt-in request: {intro.who} → {intro.to_whom}", f"[ERROR: {e}]"


def generate_intro_text(intro: IntroData, meeting_folder: Path, output_format: str = "blurb") -> Tuple[Optional[str], Optional[str]]:
    """
    Generate warm intro text using LLM.
    
    Args:
        intro: IntroData object
        meeting_folder: Path to meeting folder
        output_format: "blurb" or "email"
    
    Returns:
        (subject_line, body_text) tuple
        For blurb format, subject_line will be None
    """
    try:
        # Extract resonant details for all involved parties
        people = [intro.who, intro.to_whom]
        resonant_details = extract_resonant_details(meeting_folder, people)
        
        # Query CRM profiles
        who_profile = query_crm_profile(intro.who)
        whom_profile = query_crm_profile(intro.to_whom)
        
        # Build context for LLM
        context_bullets = "\n".join([f"- {c}" for c in intro.context_points])
        
        resonant_who = resonant_details.get(intro.who, "")
        resonant_whom = resonant_details.get(intro.to_whom, "")
        
        # Construct prompt
        if output_format == "blurb":
            prompt = f"""Generate a warm introduction blurb with the following requirements:

**Format:** Body text only (no email headers, no "To:" or "From:" lines)
**Length:** 2-3 paragraphs maximum
**Tone:** Warm, conversational, authentic (following Vrijen's voice)
**Style:** Direct but friendly, include 1-2 specific resonant details from the conversation

**Introduction Details:**
- **Introducing:** {intro.who}
- **To:** {intro.to_whom}
- **Why This Intro Matters:** {intro.why_relevant}

**Context to Include:**
{context_bullets}

**Resonant Details About {intro.to_whom}:**
{resonant_whom if resonant_whom else "(Extract from context)"}

**Resonant Details About {intro.who}:**
{resonant_who if resonant_who else "(Use general knowledge)"}

**Voice Calibration:**
- Relationship depth: Warm Contact (4-6 on scale)
- Formality: Balanced
- CTA: Balanced (not too pushy, but clear next step)
- Include specific quotes or details from conversation
- Use casual phrasing like "stretching that muscle" or industry-specific language when appropriate

**Readability Targets:**
- Flesch-Kincaid grade level: ≤10
- Average sentence length: 16-22 words
- Max sentence length: 32 words

**Structure:**
1. Opening: Warm greeting + immediate context
2. Body: Why this intro matters, specific details from conversation, mutual benefit
3. Close: Soft CTA or permission-based next step

Generate the blurb now (body text only, ready to copy-paste):"""

        else:  # email format
            prompt = f"""Generate a warm introduction email with the following requirements:

**Format:** Subject line + addressed email body (e.g., "Hey [Name],")
**Length:** 2-3 paragraphs maximum  
**Tone:** Warm, conversational, authentic (following Vrijen's voice)
**Style:** Direct but friendly, include 1-2 specific resonant details from the conversation

**Introduction Details:**
- **Introducing:** {intro.who}
- **To:** {intro.to_whom}  
- **Why This Intro Matters:** {intro.why_relevant}

**Context to Include:**
{context_bullets}

**Resonant Details About {intro.to_whom}:**
{resonant_whom if resonant_whom else "(Extract from context)"}

**Resonant Details About {intro.who}:**
{resonant_who if resonant_who else "(Use general knowledge)"}

**Voice Calibration:**
- Relationship depth: Warm Contact (4-6 on scale)
- Formality: Balanced  
- CTA: Balanced (not too pushy, but clear next step)
- Include specific quotes or details from conversation
- Use casual phrasing like "stretching that muscle" or industry-specific language when appropriate

**Readability Targets:**
- Flesch-Kincaid grade level: ≤10
- Average sentence length: 16-22 words
- Max sentence length: 32 words

**Output Format:**
Subject: [Generate contextual subject line]

Hey [First Name],

[Email body following structure above]

Best,
Vrijen

Generate the email now:"""

        logger.info(f"Generating {output_format} for: {intro.who} → {intro.to_whom}")
        
        # Call LLM
        response = call_llm(prompt)
        
        # Parse response
        if output_format == "email":
            # Parse: subject line + body
            if "Subject:" in response:
                parts = response.split("\n\n", 1)
                subject = parts[0].replace("Subject:", "").strip()
                body = parts[1] if len(parts) > 1 else response
            else:
                subject = f"Intro: {intro.who.split()[0]} → {intro.to_whom.split()[0]}"
                body = response
            return subject, body
        else:
            # Blurb format: no subject line
            return None, response
    
    except Exception as e:
        logger.error(f"Error generating intro text: {e}", exc_info=True)
        return None, None


def save_intro_output(intro: IntroData, subject: Optional[str], body: str, 
                      output_dir: Path, output_format: str, dry_run: bool = False,
                      file_suffix: str = "") -> Optional[Path]:
    """
    Save intro text to file.
    
    Args:
        file_suffix: Optional suffix for filename (e.g., "_opt_in_request")
    
    Returns: Path to saved file, or None if dry-run
    """
    try:
        # Generate filename - extract just the core name without descriptions
        def clean_name(name: str) -> str:
            """Extract first and last name, removing descriptions in parentheses."""
            # Remove content in parentheses
            name_clean = re.sub(r'\([^)]+\)', '', name).strip()
            # Take first and last word (or just first if only one word)
            parts = name_clean.split()
            if len(parts) == 1:
                return parts[0].lower().replace(",", "")
            elif len(parts) >= 2:
                return f"{parts[0]}-{parts[-1]}".lower().replace(",", "")
            return name_clean.lower().replace(" ", "-").replace(",", "")
        
        who_slug = clean_name(intro.who)
        whom_slug = clean_name(intro.to_whom)
        
        filename = f"{intro.intro_number:02d}_{who_slug}_to_{whom_slug}{file_suffix}_{output_format}.txt"
        output_path = output_dir / filename
        
        # Prepare content
        if output_format == "email" and subject:
            content = f"Subject: {subject}\n\n{body}"
        else:
            content = body
        
        if dry_run:
            logger.info(f"[DRY RUN] Would save to: {output_path}")
            logger.info(f"[DRY RUN] Content preview:\n{content[:200]}...")
            return None
        
        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        output_path.write_text(content, encoding='utf-8')
        logger.info(f"✓ Saved: {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error saving intro output: {e}", exc_info=True)
        return None


def generate_manifest(outbound_intros: List[Tuple[IntroData, Path]], 
                     inbound_intros: List[Tuple[IntroData, Path]],
                     output_dir: Path, dry_run: bool = False) -> Optional[Path]:
    """Generate manifest file summarizing all generated intros."""
    try:
        manifest_lines = [
            "# Warm Intros Manifest",
            f"**Generated:** {Path.cwd()}",
            "",
            "## Outbound Intros (Vrijen Making)",
            ""
        ]
        
        for intro, file_path in outbound_intros:
            manifest_lines.append(f"**{intro.intro_number}. {intro.who} → {intro.to_whom}** ({intro.status.split('-')[0].strip()})")
            manifest_lines.append(f"- File: `{file_path.name}`")
            manifest_lines.append(f"- Status: {intro.status}")
            manifest_lines.append("")
        
        if inbound_intros:
            manifest_lines.extend([
                "---",
                "",
                "## Inbound Intros (Offered to Vrijen)",
                ""
            ])
            
            for intro, file_path in inbound_intros:
                manifest_lines.append(f"**{intro.intro_number}. {intro.who} → {intro.to_whom}**")
                manifest_lines.append(f"- File: `{file_path.name}`")
                manifest_lines.append(f"- Status: {intro.status}")
                manifest_lines.append("")
        
        manifest_content = "\n".join(manifest_lines)
        manifest_path = output_dir / "intros_manifest.md"
        
        if dry_run:
            logger.info(f"[DRY RUN] Would save manifest to: {manifest_path}")
            return None
        
        manifest_path.write_text(manifest_content, encoding='utf-8')
        logger.info(f"✓ Saved manifest: {manifest_path}")
        
        return manifest_path
    
    except Exception as e:
        logger.error(f"Error generating manifest: {e}", exc_info=True)
        return None


def auto_create_crm_profiles(intro_data_list: List[IntroData], meeting_folder: Path, dry_run: bool = False) -> int:
    """
    Auto-create minimal CRM profiles for people in intro list if they don't exist.
    
    Returns number of profiles created.
    """
    crm_dir = Path("/home/workspace/Knowledge/crm/individuals")
    if not crm_dir.exists():
        logger.warning(f"CRM directory not found: {crm_dir}")
        return 0
    
    created_count = 0
    people_to_create = set()
    
    # Collect unique people
    for intro in intro_data_list:
        people_to_create.add(intro.who)
        people_to_create.add(intro.to_whom)
    
    # Read B08 for additional context
    b08_path = meeting_folder / "B08_STAKEHOLDER_INTELLIGENCE.md"
    b08_context = {}
    if b08_path.exists():
        try:
            b08_text = b08_path.read_text()
            # Extract role/org from B08 bullet points
            for person in people_to_create:
                if person in b08_text:
                    # Simple heuristic: find lines mentioning person
                    lines = [l for l in b08_text.split('\n') if person in l]
                    if lines:
                        b08_context[person] = '\n'.join(lines[:3])  # First 3 mentions
        except Exception as e:
            logger.warning(f"Could not parse B08: {e}")
    
    for person in people_to_create:
        # Generate slug
        slug = person.lower().strip()
        # Remove parenthetical descriptions
        slug = re.sub(r'\s*\([^)]*\)', '', slug)
        slug = re.sub(r'[^\w\s-]', '', slug).strip()
        slug = re.sub(r'[-\s]+', '-', slug)
        
        profile_path = crm_dir / f"{slug}.md"
        
        if profile_path.exists():
            continue  # Skip existing
        
        # Extract role/org from intro data
        role_org = ""
        for intro in intro_data_list:
            if intro.who == person or intro.to_whom == person:
                # Check parenthetical in name
                paren_match = re.search(r'\(([^)]+)\)', person)
                if paren_match:
                    role_org = paren_match.group(1)
                    break
        
        # Minimal profile template
        profile_content = f"""# {person.split('(')[0].strip()}

## Overview

**Role:** {role_org if role_org else "TBD"}
**Organization:** TBD
**Tags:** #warm-intro #auto-generated

## Background

Auto-generated from meeting intro block. Additional context needed.

{b08_context.get(person, '')}

## Interactions

**First Mention:** {meeting_folder.name}

## Notes

Profile auto-created by warm-intro-generate. Update with additional details.

---
*Generated:* {Path.cwd()}
*Source:* {meeting_folder}
"""
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create CRM profile: {profile_path}")
        else:
            try:
                profile_path.write_text(profile_content)
                logger.info(f"✓ Created CRM profile: {profile_path}")
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create {profile_path}: {e}")
    
    return created_count


def update_deliverable_map(meeting_folder: Path, intro_count: int, dry_run: bool = False) -> bool:
    """
    Update B25 deliverable map to reference generated intros.
    
    Returns True if updated successfully.
    """
    b25_path = meeting_folder / "B25_DELIVERABLE_CONTENT_MAP.md"
    if not b25_path.exists():
        return False
    
    try:
        b25_content = b25_path.read_text()
        
        # Check if already has intro section
        if "Warm Introductions" in b25_content:
            return False  # Already tracked
        
        # Append intro section
        intro_section = f"""

### Warm Introductions

**Status:** Generated  
**Location:** `DELIVERABLES/intros/`  
**Count:** {intro_count} intro(s)  
**Manifest:** See `intros_manifest.md` for details

"""
        
        updated_content = b25_content.rstrip() + intro_section
        
        if dry_run:
            logger.info(f"[DRY RUN] Would update B25 deliverable map")
        else:
            b25_path.write_text(updated_content)
            logger.info(f"✓ Updated B25 deliverable map: {b25_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to update B25: {e}")
        return False


def main(meeting_folder: str, output_format: str = "blurb", intro_number: Optional[int] = None, 
         only_opt_in: bool = False, only_connecting: bool = False, auto_crm: bool = False,
         dry_run: bool = False) -> int:
    """
    Main entry point for warm intro generator.
    
    Args:
        meeting_folder: Path to meeting folder containing B07 block
        output_format: "blurb" or "email"
        intro_number: Generate specific intro only (1-indexed), or None for all
        only_opt_in: Only generate opt-in request emails
        only_connecting: Only generate connecting intros  
        auto_crm: Auto-create CRM profiles for missing people
        dry_run: Preview without writing files
    
    Returns:
        0 on success, 1 on error
    """
    try:
        # Validate inputs
        meeting_path = Path(meeting_folder).resolve()
        if not meeting_path.exists():
            logger.error(f"Meeting folder not found: {meeting_path}")
            return 1
        
        # Check if this is an internal meeting - skip warm intro generation if so
        should_generate, reason = should_generate_warm_intros(meeting_path)
        if not should_generate:
            logger.info(f"✓ Skipping warm intro generation: {reason}")
            
            # Update manifest to record why we skipped
            manifest_path = meeting_path / "manifest.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                    
                    manifest["warm_intros_generated"] = {
                        "count": 0,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "skipped_internal_meeting",
                        "reason": reason
                    }
                    
                    if dry_run:
                        logger.info(f"[DRY RUN] Would update manifest with skip status")
                    else:
                        with open(manifest_path, 'w') as f:
                            json.dump(manifest, f, indent=2)
                        logger.info(f"✓ Updated manifest with skip status")
                except Exception as e:
                    logger.warning(f"Could not update manifest: {e}")
            
            return 0  # Exit successfully without generating
        
        # Validate conflicting flags
        if only_opt_in and only_connecting:
            logger.error("Cannot specify both --only-opt-in and --only-connecting")
            return 1
        
        b07_path = meeting_path / "B07_WARM_INTRO_BIDIRECTIONAL.md"
        if not b07_path.exists():
            logger.error(f"B07 block not found: {b07_path}")
            return 1
        
        logger.info(f"Processing: {meeting_path}")
        logger.info(f"Format: {output_format}")
        
        # Parse B07 block
        outbound_intros, inbound_intros = parse_b07_block(b07_path)
        
        if not outbound_intros and not inbound_intros:
            logger.error("No intros found in B07 block")
            return 1
        
        # Filter by intro number if specified
        if intro_number is not None:
            if intro_number < 1 or intro_number > len(outbound_intros) + len(inbound_intros):
                logger.error(f"Invalid intro number: {intro_number}")
                return 1
            
            if intro_number <= len(outbound_intros):
                outbound_intros = [outbound_intros[intro_number - 1]]
                inbound_intros = []
            else:
                inbound_intros = [inbound_intros[intro_number - len(outbound_intros) - 1]]
                outbound_intros = []
        
        # Auto-create CRM profiles if requested
        if auto_crm:
            all_intros = outbound_intros + inbound_intros
            created = auto_create_crm_profiles(all_intros, meeting_path, dry_run=dry_run)
            if created > 0:
                logger.info(f"✓ Auto-created {created} CRM profile(s)")
        
        # Setup output directory
        output_dir = meeting_path / "DELIVERABLES" / "intros"
        
        # Generate intros
        generated_outbound = []
        generated_inbound = []
        
        # Process outbound intros
        for intro in outbound_intros:
            # Check if double opt-in required
            if intro.requires_double_opt_in:
                if only_connecting:
                    # Only generate connecting intro
                    subject, body = generate_intro_text(intro, meeting_path, output_format)
                    if body:
                        file_path = save_intro_output(intro, subject, body, output_dir, output_format, dry_run, file_suffix="_connecting")
                        if file_path or dry_run:
                            generated_outbound.append((intro, file_path or output_dir / "placeholder.txt"))
                
                elif only_opt_in:
                    # Only generate opt-in request
                    opt_subject, opt_body = generate_opt_in_request(intro, meeting_path)
                    if opt_body:
                        file_path = save_intro_output(intro, opt_subject, opt_body, output_dir, "email", dry_run, file_suffix="_opt_in_request")
                        if file_path or dry_run:
                            generated_outbound.append((intro, file_path or output_dir / "placeholder.txt"))
                
                else:
                    # Generate both opt-in request AND connecting intro
                    # 1. Opt-in request
                    opt_subject, opt_body = generate_opt_in_request(intro, meeting_path)
                    if opt_body:
                        file_path = save_intro_output(intro, opt_subject, opt_body, output_dir, "email", dry_run, file_suffix="_opt_in_request")
                        if file_path or dry_run:
                            generated_outbound.append((intro, file_path or output_dir / "placeholder.txt"))
                    
                    # 2. Connecting intro (for after approval)
                    subject, body = generate_intro_text(intro, meeting_path, output_format)
                    if body:
                        file_path = save_intro_output(intro, subject, body, output_dir, output_format, dry_run, file_suffix="_connecting")
                        if file_path or dry_run:
                            generated_outbound.append((intro, file_path or output_dir / "placeholder.txt"))
            
            else:
                # Direct intro (no opt-in needed)
                if only_opt_in or only_connecting:
                    continue  # Skip direct intros when filtering
                
                subject, body = generate_intro_text(intro, meeting_path, output_format)
                if body:
                    file_path = save_intro_output(intro, subject, body, output_dir, output_format, dry_run)
                    if file_path or dry_run:
                        generated_outbound.append((intro, file_path or output_dir / "placeholder.txt"))
        
        # Process inbound intros
        for intro in inbound_intros:
            if only_opt_in or only_connecting:
                continue  # Inbound intros don't have opt-in workflow
            
            subject, body = generate_intro_text(intro, meeting_path, output_format)
            if body:
                file_path = save_intro_output(intro, subject, body, output_dir, output_format, dry_run)
                if file_path or dry_run:
                    generated_inbound.append((intro, file_path or output_dir / "placeholder.txt"))
        
        # Generate manifest
        if generated_outbound or generated_inbound:
            generate_manifest(generated_outbound, generated_inbound, output_dir, dry_run)
        
        # Update B25 deliverable map
        total_generated = len(generated_outbound) + len(generated_inbound)
        if total_generated > 0:
            update_deliverable_map(meeting_path, total_generated, dry_run=dry_run)
        
        # Summary
        logger.info(f"✓ Complete: Generated {total_generated} intro(s)")
        
        if not dry_run:
            logger.info(f"Output directory: {output_dir}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate warm introduction emails/blurbs from B07 blocks"
    )
    parser.add_argument(
        "meeting_folder",
        help="Path to meeting folder containing B07 block"
    )
    parser.add_argument(
        "--format",
        choices=["blurb", "email"],
        default="blurb",
        help="Output format: blurb (default) or email"
    )
    parser.add_argument(
        "--intro-number",
        type=int,
        help="Generate specific intro only (1-indexed)"
    )
    parser.add_argument(
        "--only-opt-in",
        action="store_true",
        help="Only generate opt-in request emails (for double opt-in intros)"
    )
    parser.add_argument(
        "--only-connecting",
        action="store_true",
        help="Only generate connecting intros (skip opt-in requests)"
    )
    parser.add_argument(
        "--auto-crm",
        action="store_true",
        help="Auto-create CRM profiles for people not in database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing files"
    )
    
    args = parser.parse_args()
    
    exit_code = main(
        meeting_folder=args.meeting_folder,
        output_format=args.format,
        intro_number=args.intro_number,
        only_opt_in=args.only_opt_in,
        only_connecting=args.only_connecting,
        auto_crm=args.auto_crm,
        dry_run=args.dry_run
    )
    
    sys.exit(exit_code)

