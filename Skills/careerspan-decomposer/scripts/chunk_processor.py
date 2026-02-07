#!/usr/bin/env python3
"""
Chunked Document Processor for Careerspan Decomposer

For large Intelligence Briefs (>1500 lines), splits the document into logical
chunks and processes them in parallel via /zo/ask API.

This is significantly faster and more reliable than single-pass extraction
for large documents (76+ page briefs).
"""

import asyncio
import aiohttp
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional


# Section patterns to detect chunk boundaries
SECTION_PATTERNS = [
    (r'^Responsibilities$', 'responsibilities'),
    (r'^Soft Skills$', 'soft_skills'),
    (r'^Hard Skills$', 'hard_skills'),
    (r'^Background', 'background'),
    (r'^Overall:', 'overview'),
]

# Minimum lines threshold for chunked processing
CHUNK_THRESHOLD = 1500


async def call_zo_ask(session: aiohttp.ClientSession, prompt: str, timeout: int = 300) -> str:
    """Call /zo/ask API for LLM processing."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    async with session.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json={"input": prompt},
        timeout=aiohttp.ClientTimeout(total=timeout)
    ) as resp:
        result = await resp.json()
        return result.get("output", "")


def detect_sections(content: str) -> Dict[str, Tuple[int, int]]:
    """
    Detect section boundaries in the document.
    Returns dict of section_name -> (start_line, end_line)
    """
    lines = content.split('\n')
    sections = {}
    current_section = 'overview'
    current_start = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        for pattern, section_name in SECTION_PATTERNS:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                # Close previous section
                if current_section and current_start < i:
                    if current_section not in sections:
                        sections[current_section] = (current_start, i - 1)
                current_section = section_name
                current_start = i
                break
    
    # Close final section
    if current_section and current_start < len(lines):
        sections[current_section] = (current_start, len(lines) - 1)
    
    return sections


def split_document(content: str) -> Dict[str, str]:
    """
    Split document into logical chunks based on section headers.
    
    Returns dict of chunk_name -> chunk_content
    """
    lines = content.split('\n')
    total_lines = len(lines)
    
    # For very large docs, look for specific section markers
    chunks = {}
    
    # Find key line numbers
    resp_detail_start = None
    soft_detail_start = None
    hard_detail_start = None
    
    # Pattern: detailed sections appear after summary sections
    # Summary: "Responsibilities" followed by skill list
    # Detail: "Responsibilities" with individual skill breakdowns (longer)
    
    resp_count = 0
    soft_count = 0
    hard_count = 0
    
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        
        if line_lower == 'responsibilities':
            resp_count += 1
            if resp_count == 2:  # Second occurrence is detail section
                resp_detail_start = i
        elif line_lower == 'soft skills':
            soft_count += 1
            if soft_count == 2:
                soft_detail_start = i
        elif line_lower == 'hard skills':
            hard_count += 1
            if hard_count == 2:
                hard_detail_start = i
    
    # Build chunks based on detected boundaries
    if resp_detail_start and soft_detail_start and hard_detail_start:
        # Overview + summary (first section up to detailed responsibilities)
        chunks['01_overview'] = '\n'.join(lines[0:resp_detail_start])
        
        # Responsibilities details
        chunks['02_responsibilities'] = '\n'.join(lines[resp_detail_start:soft_detail_start])
        
        # Soft skills details
        chunks['03_soft_skills'] = '\n'.join(lines[soft_detail_start:hard_detail_start])
        
        # Hard skills details
        chunks['04_hard_skills'] = '\n'.join(lines[hard_detail_start:])
    else:
        # Fallback: split by line count
        chunk_size = total_lines // 4
        chunks['01_overview'] = '\n'.join(lines[0:chunk_size])
        chunks['02_section_a'] = '\n'.join(lines[chunk_size:chunk_size*2])
        chunks['03_section_b'] = '\n'.join(lines[chunk_size*2:chunk_size*3])
        chunks['04_section_c'] = '\n'.join(lines[chunk_size*3:])
    
    return chunks


def should_use_chunked_processing(content: str) -> bool:
    """Determine if document is large enough to warrant chunked processing."""
    line_count = content.count('\n') + 1
    return line_count > CHUNK_THRESHOLD


OVERVIEW_PROMPT = """You are extracting structured overview data from a Careerspan Intelligence Brief.

Extract the following and return ONLY valid JSON (no markdown fences):

{{
  "overall_score": <integer 0-100, extract from "X\\nOverall score" pattern>,
  "bottom_line": "<exact bottom line text>",
  "overall_strengths": "<summary of key strengths>",
  "overall_weaknesses": "<summary of key weaknesses>",
  "potential_dealbreakers": ["<question 1>", "<question 2>"],
  "category_scores": {{
    "background": {{"score": <int>, "max": 100}},
    "uniqueness": {{"score": <int>, "max": 100}},
    "responsibilities": {{"score": <int>, "max": 100}},
    "hard_skills": {{"score": <int>, "max": 100}},
    "soft_skills": {{"score": <int>, "max": 100}}
  }}
}}

IMPORTANT: 
- Look for scores like "Background: 78/100" or "Hard skills: 58/100"
- The overall score appears as a number followed by "Overall score" on the next line
- Extract exact text for bottom_line, not a summary

SOURCE DOCUMENT:
{doc}

Return ONLY the JSON."""


SKILLS_PROMPT = """You are extracting skill assessments from a Careerspan Intelligence Brief section.

For each skill assessment in this section, extract:

[
  {{
    "skill_name": "<exact skill name>",
    "category": "<Responsibility|Hard Skill|Soft Skill>",
    "rating": "<Excellent|Good|Fair|Gap>",
    "importance": <1-10 integer>,
    "direct_experience_score": <1-10 integer from "Direct experience: X/10">,
    "experience_type": "<Direct|Transferable>",
    "evidence_type": "<Story + profile|Story|Profile|Resume|Gap>",
    "our_take": "<FULL verbatim 'Our take' text - do NOT summarize>",
    "contributing_skills": ["<skill1>", "<skill2>"],
    "support": [
      {{
        "source": "<story ID or 'Resume'>",
        "type": "<Direct|Transferable>",
        "score": "<X/10>",
        "rating": "<Excellent|Good|Fair|Gap>",
        "is_best": <true if marked as Best, else false>
      }}
    ]
  }}
]

IMPORTANT:
- our_take MUST be the FULL verbatim text, not summarized
- Each skill has an "Our take:" section - extract it completely
- If rating is "Weak", normalize to "Gap"
- contributing_skills should be an empty array [] if not present, NOT null

SOURCE SECTION:
{doc}

Return ONLY the JSON array."""


async def extract_overview(session: aiohttp.ClientSession, chunk: str) -> dict:
    """Extract overview data from the first chunk."""
    prompt = OVERVIEW_PROMPT.format(doc=chunk[:50000])  # Limit to 50k chars
    
    response = await call_zo_ask(session, prompt, timeout=120)
    
    # Clean response
    response = response.strip()
    if response.startswith('```'):
        response = re.sub(r'^```(?:json)?\n?', '', response)
        response = re.sub(r'\n?```$', '', response)
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"  ✗ Overview JSON error: {e}")
        return {}


async def extract_skills_from_chunk(session: aiohttp.ClientSession, chunk_name: str, chunk: str) -> List[dict]:
    """Extract skills from a chunk."""
    prompt = SKILLS_PROMPT.format(doc=chunk[:80000])  # Limit to 80k chars
    
    response = await call_zo_ask(session, prompt, timeout=300)
    
    # Clean response
    response = response.strip()
    if response.startswith('```'):
        response = re.sub(r'^```(?:json)?\n?', '', response)
        response = re.sub(r'\n?```$', '', response)
    
    try:
        skills = json.loads(response)
        if isinstance(skills, list):
            return skills
        return []
    except json.JSONDecodeError as e:
        print(f"  ✗ {chunk_name} JSON error: {e}")
        # Try to salvage partial results
        return salvage_partial_json(response)


def salvage_partial_json(response: str) -> List[dict]:
    """Attempt to extract valid skill objects from truncated JSON."""
    skills = []
    
    # Find all complete skill objects
    depth = 0
    obj_start = None
    
    for i, c in enumerate(response):
        if c == '{':
            if depth == 0:
                obj_start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and obj_start is not None:
                obj_str = response[obj_start:i+1]
                try:
                    obj = json.loads(obj_str)
                    if 'skill_name' in obj:
                        skills.append(obj)
                except:
                    pass
                obj_start = None
    
    if skills:
        print(f"    Salvaged {len(skills)} skills from truncated response")
    
    return skills


def normalize_skills(skills: List[dict]) -> List[dict]:
    """Normalize skill data to match canonical schema."""
    rating_map = {
        "weak": "Gap",
        "poor": "Gap",
        "none": "Gap",
        "excellent": "Excellent",
        "good": "Good",
        "fair": "Fair",
        "gap": "Gap"
    }
    
    for skill in skills:
        # Normalize rating
        rating = skill.get("rating")
        if rating and isinstance(rating, str):
            skill["rating"] = rating_map.get(rating.lower(), rating)
        
        # Normalize support ratings
        for support in skill.get("support", []):
            sr = support.get("rating")
            if sr and isinstance(sr, str):
                support["rating"] = rating_map.get(sr.lower(), sr)
        
        # Ensure arrays are arrays, not null
        for array_field in ["contributing_skills", "support"]:
            if skill.get(array_field) is None:
                skill[array_field] = []
    
    return skills


async def process_document_chunked(
    doc_content: str,
    work_dir: Path
) -> Tuple[dict, List[dict]]:
    """
    Process a large document using chunked parallel extraction.
    
    Returns: (overview_data, skills_list)
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # Split document
    chunks = split_document(doc_content)
    print(f"  Split into {len(chunks)} chunks:")
    for name, content in chunks.items():
        print(f"    {name}: {content.count(chr(10)) + 1} lines")
    
    # Save chunks for debugging
    chunks_dir = work_dir / "chunks"
    chunks_dir.mkdir(exist_ok=True)
    for name, content in chunks.items():
        (chunks_dir / f"{name}.txt").write_text(content)
    
    async with aiohttp.ClientSession() as session:
        # Extract overview from first chunk
        print("  Extracting overview...")
        overview = await extract_overview(session, chunks.get('01_overview', ''))
        (work_dir / "overview.json").write_text(json.dumps(overview, indent=2))
        print("    ✓ Overview extracted")
        
        # Extract skills from remaining chunks in parallel
        skill_chunks = {k: v for k, v in chunks.items() if k != '01_overview'}
        
        print(f"  Extracting skills from {len(skill_chunks)} chunks in parallel...")
        
        tasks = []
        chunk_names = []
        for name, content in skill_chunks.items():
            tasks.append(extract_skills_from_chunk(session, name, content))
            chunk_names.append(name)
        
        results = await asyncio.gather(*tasks)
        
        # Merge and normalize skills
        all_skills = []
        for name, skills in zip(chunk_names, results):
            if skills:
                print(f"    ✓ {name}: {len(skills)} skills")
                all_skills.extend(skills)
            else:
                print(f"    ✗ {name}: no skills extracted")
        
        all_skills = normalize_skills(all_skills)
    
    return overview, all_skills


def calculate_signal_strength(skills: List[dict]) -> dict:
    """Calculate signal strength percentages from skills."""
    evidence_counts = {"story": 0, "resume": 0, "inferred": 0}
    
    for skill in skills:
        ev_type = (skill.get("evidence_type") or "").lower()
        if "story" in ev_type:
            evidence_counts["story"] += 1
        elif "resume" in ev_type or "profile" in ev_type:
            evidence_counts["resume"] += 1
        else:
            evidence_counts["inferred"] += 1
    
    total = len(skills) if skills else 1
    return {
        "story_verified_pct": round(evidence_counts["story"] / total * 100, 1),
        "resume_only_pct": round(evidence_counts["resume"] / total * 100, 1),
        "inferred_pct": round(evidence_counts["inferred"] / total * 100, 1)
    }


def build_scores_complete(overview: dict, skills: List[dict]) -> dict:
    """Build the scores_complete.json structure."""
    return {
        "overall_score": overview.get("overall_score"),
        "bottom_line": overview.get("bottom_line", ""),
        "overall_strengths": overview.get("overall_strengths"),
        "overall_weaknesses": overview.get("overall_weaknesses"),
        "potential_dealbreakers": overview.get("potential_dealbreakers", []),
        "category_scores": overview.get("category_scores", {
            "background": {"score": None, "max": 100},
            "uniqueness": {"score": None, "max": 100},
            "responsibilities": {"score": None, "max": 100},
            "hard_skills": {"score": None, "max": 100},
            "soft_skills": {"score": None, "max": 100}
        }),
        "signal_strength": calculate_signal_strength(skills),
        "skills": skills
    }


# Export key functions for use by decompose.py
__all__ = [
    'should_use_chunked_processing',
    'process_document_chunked',
    'build_scores_complete',
    'CHUNK_THRESHOLD'
]
