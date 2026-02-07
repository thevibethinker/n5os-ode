#!/usr/bin/env python3
"""
Careerspan Decomposer - LLM-Based Semantic Extraction

This script uses LLM calls (via /zo/ask) for ALL extraction.
NO regex. NO string parsing (except score detection). Pure semantic understanding.

For large documents (>1500 lines), automatically uses chunked parallel processing
for faster and more reliable extraction.

Usage:
    python3 decompose.py --doc <careerspan_doc> --jd <jd_file_or_text> --candidate <name> --company <company>
    
Example:
    python3 decompose.py --doc /path/to/careerspan.md --jd /path/to/jd.md --candidate hardik --company flowfuse
"""

import argparse
import asyncio
import aiohttp
import os
import json
import yaml
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Import chunked processor for large documents
try:
    from chunk_processor import (
        should_use_chunked_processing,
        process_document_chunked,
        build_scores_complete,
        CHUNK_THRESHOLD
    )
    HAS_CHUNK_PROCESSOR = True
except ImportError:
    HAS_CHUNK_PROCESSOR = False
    CHUNK_THRESHOLD = 1500
    def should_use_chunked_processing(content): return False

# Output location
INBOX_PATH = Path("/home/workspace/Careerspan/meta-resumes/inbox")
SCHEMA_PATH = Path(__file__).parent.parent / "assets" / "canonical_schema.json"

# LLM extraction prompts for each category
EXTRACTION_PROMPTS = {
    "overview": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract the OVERVIEW information and return ONLY valid YAML (no markdown code fences, no explanation).

IMPORTANT: Look for the overall Careerspan score. It appears as a number followed by "Overall score" on the next line.
For example:
90
Overall score
means the score is 90.

Category scores are on a /100 scale (e.g., "Background: 78/100", "Hard skills: 85/100").

The YAML structure must be:
```
careerspan_score:
  overall: <number 0-100>
  max: 100
  qualification: "<Well-aligned|Partially aligned|Not aligned>"
  qualification_detail: "<Atypical Background|Industry Shift|Career Pivot|null>"
  career_trajectory: "<Industry Shift|Lateral Move|Career Pivot|Step Up|Step Down>"
category_scores:
  background:
    score: <integer 0-100>
    max: 100
  uniqueness:
    score: <integer 0-100>
    max: 100
  responsibilities:
    score: <integer 0-100>
    max: 100
  hard_skills:
    score: <integer 0-100>
    max: 100
  soft_skills:
    score: <integer 0-100>
    max: 100
recommendation: "<STRONG_YES|YES|CONDITIONAL|NO|STRONG_NO>"
summary: "<2-3 sentence synthesis of who this person is>"
bottom_line: "<the exact 'Bottom line' text if present>"
elevator_pitch: "<the elevator pitch if present, or null>"
overall_strengths: "<summary of key strengths from the brief>"
overall_weaknesses: "<summary of key weaknesses or gaps from the brief>"
potential_dealbreakers:
  - "<dealbreaker question 1>"
  - "<dealbreaker question 2>"
key_strengths:
  - "<strength 1>"
  - "<strength 2>"
  - "<strength 3>"
key_concerns:
  - "<concern 1>"
  - "<concern 2>"
verdict: "<1 sentence bottom line>"
```

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "profile": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract the PROFILE/BACKGROUND information and return ONLY valid YAML.

The YAML structure must be:
```
name: "<full name>"
current_title: "<most recent title>"
current_company: "<most recent company>"
years_experience: <number>
education:
  - institution: "<school name>"
    degree: "<degree type>"
    field: "<field of study>"
    years: "<start - end>"
    honors: "<any honors, or null>"
location: "<city, country or Remote>"
linkedin: "<linkedin url or null>"
notable_credentials:
  - "<credential 1>"
  - "<credential 2>"
```

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "experience": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract ALL WORK EXPERIENCE and return ONLY valid YAML.

The YAML structure must be:
```
positions:
  - company: "<company name>"
    title: "<job title>"
    duration: "<start - end>"
    type: "<fulltime|contract|founding>"
    summary: "<1-2 sentence description of role>"
    key_accomplishments:
      - text: "<accomplishment>"
        quantified: <true|false>
        impact: "<business impact if stated>"
    technologies:
      - "<tech 1>"
      - "<tech 2>"
    team_context: "<solo|small team|large team|led team of N>"
```

Include ALL positions mentioned. Be thorough.

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "hard_skills": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract TECHNICAL/HARD SKILLS with evidence and return ONLY valid YAML.

The YAML structure must be:
```
skill_categories:
  ai_ml:
    skills:
      - name: "<skill>"
        level: "<expert|proficient|familiar|claimed>"
        evidence: "<where/how demonstrated>"
  backend:
    skills:
      - name: "<skill>"
        level: "<level>"
        evidence: "<evidence>"
  frontend:
    skills:
      - name: "<skill>"
        level: "<level>"
        evidence: "<evidence>"
  infrastructure:
    skills:
      - name: "<skill>"
        level: "<level>"
        evidence: "<evidence>"
  data:
    skills:
      - name: "<skill>"
        level: "<level>"
        evidence: "<evidence>"
gaps_identified:
  - skill: "<missing skill>"
    severity: "<critical|moderate|minor>"
    note: "<why it matters>"
```

Be honest about gaps. If a skill is claimed but not evidenced, mark level as "claimed".

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "soft_skills": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract SOFT SKILLS and WORKING STYLE and return ONLY valid YAML.

The YAML structure must be:
```
demonstrated_strengths:
  - trait: "<trait name>"
    evidence: "<specific example from their history>"
    confidence: "<high|medium|low>"
working_style:
  autonomy: "<high|medium|low>"
  collaboration: "<async-native|sync-preferred|unknown>"
  communication: "<written-strong|verbal-strong|both|unknown>"
  ambiguity_tolerance: "<high|medium|low>"
leadership_signals:
  - "<signal 1>"
potential_concerns:
  - "<concern about working style>"
unknown_factors:
  - "<thing we can't assess from the doc>"
```

Be honest about unknowns. Don't invent evidence.

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "tools": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract ALL TOOLS and TECHNOLOGIES mentioned and return ONLY valid YAML.

The YAML structure must be:
```
languages:
  - "<language 1>"
frameworks:
  - "<framework 1>"
databases:
  - "<db 1>"
infrastructure:
  - "<tool 1>"
ai_ml_tools:
  - "<tool 1>"
other:
  - "<tool 1>"
not_mentioned:
  - "<common tool in their domain that's absent>"
```

List everything explicitly mentioned. Note significant absences.

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "achievements": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract ACHIEVEMENTS, AWARDS, and NOTABLE ACCOMPLISHMENTS and return ONLY valid YAML.

The YAML structure must be:
```
quantified_achievements:
  - achievement: "<what they did>"
    metric: "<the number/percentage>"
    context: "<where/when>"
    verification: "<independently verifiable|self-reported|unclear>"
awards_recognition:
  - award: "<award name>"
    year: "<year or null>"
    significance: "<why this matters>"
academic_achievements:
  - achievement: "<achievement>"
    context: "<context>"
patterns:
  - "<pattern observed across achievements>"
```

Focus on QUANTIFIED results. Note verification level.

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "interests": """You are extracting structured data from a Careerspan Intelligence Brief.

Extract HOBBIES, INTERESTS, and PERSONAL INFORMATION and return ONLY valid YAML.

The YAML structure must be:
```
hobbies:
  - "<hobby 1>"
interests:
  - "<interest 1>"
side_projects:
  - name: "<project>"
    description: "<what it is>"
publications_talks:
  - "<publication or talk>"
personality_signals:
  - "<signal about who they are as a person>"
culture_fit_indicators:
  - "<indicator>"
data_availability: "<rich|moderate|sparse>"
note: "<any caveat about limited personal data>"
```

If personal info is sparse, say so explicitly.

SOURCE DOCUMENT:
{doc}

Return ONLY the YAML, nothing else.""",

    "alignment": """You are analyzing alignment between a candidate and a job description.

Given the CANDIDATE DATA and JOB DESCRIPTION, produce an alignment analysis as ONLY valid YAML.

The YAML structure must be:
```
requirements_alignment:
  - requirement_id: "R1"
    jd_text: "<exact requirement from JD>"
    category: "<core|secondary>"
    verdict: "<CLEAR|PARTIAL|GAP|UNKNOWN>"
    evidence: "<specific evidence from candidate>"
    confidence: "<high|medium|low>"
    note: "<any nuance>"

culture_alignment:
  - signal: "<culture element from JD>"
    candidate_fit: "<strong|moderate|weak|unknown>"
    evidence: "<evidence>"

overall_alignment:
  core_requirements_met: "<X of Y>"
  critical_gaps:
    - "<gap 1>"
  interview_priorities:
    - "<what to probe>"
```

Be rigorous. Don't inflate alignment.

JOB DESCRIPTION:
{jd}

CANDIDATE DATA:
{doc}

Return ONLY the YAML, nothing else.""",

    "skills_assessment": """You are extracting ALL skill assessments from a Careerspan Intelligence Brief.

This is the MOST CRITICAL extraction. You must capture EVERY skill assessment with its full "Our Take" narrative.

Return ONLY valid JSON array (no markdown code fences, no explanation).

Each skill must have this EXACT structure:
{{
  "skill_name": "<exact skill name from the document>",
  "category": "<Responsibility|Hard Skill|Soft Skill>",
  "rating": "<Excellent|Good|Fair|Gap>",
  "required_level": "<Novice|Intermediate|Advanced|Expert>",
  "importance": <integer 1-10 from "Importance: X/10">,
  "max_importance": 10,
  "direct_experience_score": <integer 1-10 from "Direct experience: X/10">,
  "max_experience_score": 10,
  "experience_type": "<Direct|Transferable>",
  "evidence_type": "<Story + profile|Story|Profile|Resume|Gap>",
  "our_take": "<FULL verbatim Our Take text - do NOT summarize, preserve complete text>",
  "contributing_skills": ["<skill that contributes to this assessment>", ...],
  "support": [
    {{
      "source": "<story ID like o94wesBFvqnIgr9l5YVz or null>",
      "type": "<Direct|Transferable>",
      "score": "<score like 9/10 or null>",
      "rating": "<Excellent|Good|Fair|Gap or null>",
      "is_best": <true if marked as "Best", false otherwise>
    }}
  ],
  "support_note": "<'No strong support found' or similar note if present, otherwise null>",
  "source_page": "<page reference or null>"
}}

CRITICAL RULES:
1. Extract EVERY skill mentioned (typically 30-50 skills)
2. Preserve "Our Take" text VERBATIM - this is the core value
3. Use integers for numeric fields (importance: 10, not "10/10")
4. Include ALL evidence sources in support array
5. Mark is_best: true for any story marked as "Best" in the document
6. If a field is unclear, use null, never guess
7. Contributing skills appear under "Contributing skills" heading for each skill

CRITICAL: The "our_take" field MUST be copied CHARACTER-FOR-CHARACTER from the source.
Do not paraphrase, summarize, or rephrase. If you cannot find the exact text, return null for that skill.

SOURCE DOCUMENT:
{doc}

Return ONLY the JSON array, nothing else.""",

    "skills_batch": """You are extracting specific skill assessments from a Careerspan Intelligence Brief.

Extract ONLY the skills listed below and return ONLY valid JSON array (no markdown code fences, no explanation).

Skills to extract:
{skill_list}

Each skill must have this EXACT structure:
{{
  "skill_name": "<exact skill name from the document>",
  "category": "<Responsibility|Hard Skill|Soft Skill>",
  "rating": "<Excellent|Good|Fair|Gap>",
  "required_level": "<Novice|Intermediate|Advanced|Expert>",
  "importance": <integer 1-10 from "Importance: X/10">,
  "max_importance": 10,
  "direct_experience_score": <integer 1-10 from "Direct experience: X/10">,
  "max_experience_score": 10,
  "experience_type": "<Direct|Transferable>",
  "evidence_type": "<Story + profile|Story|Profile|Resume|Gap>",
  "our_take": "<FULL verbatim Our Take text - do NOT summarize, preserve complete text>",
  "contributing_skills": ["<skill that contributes to this assessment>", ...],
  "support": [
    {{
      "source": "<story ID like o94wesBFvqnIgr9l5YVz or null>",
      "type": "<Direct|Transferable>",
      "score": "<score like 9/10 or null>",
      "rating": "<Excellent|Good|Fair|Gap or null>",
      "is_best": <true if marked as "Best", false otherwise>
    }}
  ],
  "support_note": "<'No strong support found' or similar note if present, otherwise null>",
  "source_page": "<page reference or null>"
}}

CRITICAL: The "our_take" field MUST be copied CHARACTER-FOR-CHARACTER from the source.
Do not paraphrase, summarize, or rephrase. If you cannot find the exact text, return null for that skill.

SOURCE DOCUMENT:
{doc}

Return ONLY the JSON array, nothing else.""",

    "culture_signals": """You are extracting CULTURE SIGNALS and REQUIREMENTS from a job description.

These will be used to evaluate candidate culture fit. Extract BOTH explicit values and implied cultural requirements.

Return ONLY valid YAML (no markdown code fences, no explanation).

The YAML structure must be:
```
explicit_values:
  - name: "<value name from JD>"
    description: "<how the company describes this value>"
    observable_behaviors:
      - "<specific behavior that demonstrates this value>"
      - "<another observable behavior>"
    interview_signals:
      - "<what to look for in candidate's stories>"

implied_requirements:
  - trait: "<inferred cultural trait needed for role>"
    why_needed: "<why this role requires this trait>"
    evidence_markers:
      - "<what would demonstrate this in a candidate>"

working_style_signals:
  autonomy_level: "<high|medium|low> - with reasoning"
  collaboration_mode: "<async-heavy|sync-heavy|balanced> - with reasoning"  
  ambiguity_tolerance: "<high|medium|low> - with reasoning"
  pace: "<fast-paced|steady|variable> - with reasoning"

red_flags:
  - "<candidate trait that would be a culture mismatch>"

culture_fit_questions:
  - question: "<interview question to assess culture fit>"
    assesses: "<which value/trait this probes>"
```

JOB DESCRIPTION:
{jd}

Return ONLY the YAML, nothing else.""",
}


async def call_llm(session: aiohttp.ClientSession, prompt: str, timeout: int = 180) -> str:
    """Call /zo/ask API for semantic extraction."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise ValueError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    async with session.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json={"input": prompt},
        timeout=aiohttp.ClientTimeout(total=timeout)
    ) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"LLM call failed: {resp.status} - {text}")
        result = await resp.json()
        return result.get("output", "")


def clean_response(response: str, format: str = "yaml") -> str:
    """Remove markdown code fences if present."""
    response = response.strip()
    fence_start = f"```{format}"
    if response.startswith(fence_start):
        response = response[len(fence_start):]
    elif response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    return response.strip()


def extract_score_from_text(doc_content: str) -> int | None:
    """Extract careerspan score from document.
    
    Handles multiple formats:
    1. Web format with newline: "90\nOverall score"
    2. Web format inline: "90 Overall score" (space separated)
    3. Legacy format: "Referred 89 ©" or "Referred 89 ®"
    """
    # Try web format with newline: "90\nOverall score"
    match = re.search(r'(\d{1,3})\s*\n\s*Overall\s+score', doc_content, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Try web format inline: "90 Overall score"
    match = re.search(r'(\d{1,3})\s+Overall\s+score', doc_content, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Try legacy format: "Referred 89 ©"
    match = re.search(r'Referred\s+(\d+)\s*[©®]', doc_content)
    if match:
        return int(match.group(1))
    
    return None


def verify_our_take_exists(our_take: str, doc_content: str, threshold: float = 0.95) -> bool:
    """
    Verify that the our_take text exists in the source document.
    Uses fuzzy matching to handle minor variations.
    """
    if not our_take or our_take == "null" or not our_take.strip():
        return True  # null/empty is acceptable
    
    try:
        from rapidfuzz import fuzz
        
        # Clean our_take for comparison
        our_take_clean = our_take.strip()
        if len(our_take_clean) < 10:
            return True  # Very short text is likely acceptable
        
        # Check if our_take appears with high similarity anywhere in the document
        similarity = fuzz.partial_ratio(our_take_clean.lower(), doc_content.lower()) / 100.0
        return similarity >= threshold
    except ImportError:
        # Fallback to simple substring match if rapidfuzz not available
        return our_take.strip().lower() in doc_content.lower()


def fuzzy_substring_match(our_take: str, doc_content: str, threshold: float = 0.95) -> tuple[bool, float]:
    """
    Check if our_take text matches content in doc with fuzzy matching.
    Returns (matches, confidence_score).
    """
    if not our_take or our_take == "null" or not our_take.strip():
        return True, 1.0  # null/empty is acceptable
    
    try:
        from rapidfuzz import fuzz
        
        # Clean our_take for comparison
        our_take_clean = our_take.strip()
        if len(our_take_clean) < 10:
            return True, 1.0  # Very short text is likely acceptable
        
        # Check if our_take appears with high similarity anywhere in the document
        similarity = fuzz.partial_ratio(our_take_clean.lower(), doc_content.lower()) / 100.0
        return similarity >= threshold, similarity
    except ImportError:
        # Fallback to simple substring match if rapidfuzz not available
        matches = our_take.strip().lower() in doc_content.lower()
        return matches, 1.0 if matches else 0.0


def process_structured_input(json_path: str, doc_content: str, output_dir: Path) -> tuple[list, list]:
    """
    Process pre-structured JSON input.
    
    Expected JSON structure:
    {
        "candidate": {...},
        "skills": [
            {
                "skill_name": "...",
                "category": "...",
                "rating": "...",
                "our_take": "...",  # COPY VERBATIM
                "story_ids": ["..."],
                ...
            }
        ],
        "stories": {
            "STORY_ID": {
                "title": "...",
                "content": "..."
            }
        }
    }
    
    Returns: (skills_list, validation_failures)
    """
    with open(json_path) as f:
        data = json.load(f)
    
    skills = []
    failures = []
    
    for skill_data in data.get('skills', []):
        # COPY verbatim fields directly - NO LLM
        skill = {
            'skill_name': skill_data.get('skill_name'),
            'category': skill_data.get('category'),
            'rating': skill_data.get('rating'),
            'required_level': skill_data.get('required_level'),
            'required_score': skill_data.get('required_score'),
            'max_score': 5,
            'importance': skill_data.get('importance'),
            'max_importance': 10,
            'evidence_type': skill_data.get('evidence_type'),
            'our_take': skill_data.get('our_take'),  # VERBATIM
            'support': [],
            'source_page': skill_data.get('source_page')
        }
        
        # Build support array from story_ids
        for story_id in skill_data.get('story_ids', []):
            skill['support'].append({
                'source': story_id,
                'type': skill_data.get('evidence_type', 'Direct'),
                'score': None,
                'rating': None
            })
        
        # STILL VERIFY against source doc
        if skill['our_take'] and not fuzzy_substring_match(skill['our_take'], doc_content)[0]:
            failures.append({
                'skill_name': skill['skill_name'],
                'reason': 'our_take from JSON not found in source doc',
                'extracted_text': skill['our_take'][:200] if skill['our_take'] else 'null'
            })
        else:
            skills.append(skill)
    
    return skills, failures


async def identify_skill_sections(session: aiohttp.ClientSession, doc_content: str) -> List[str]:
    """Identify all skill names mentioned in the document for batching."""
    prompt = f"""
    Scan this Careerspan Intelligence Brief and identify ALL skill names mentioned in the skills assessment section.
    
    Return ONLY a JSON array of skill names, nothing else:
    ["skill name 1", "skill name 2", "skill name 3", ...]
    
    Be comprehensive - include EVERY skill that has an assessment.
    
    SOURCE DOCUMENT:
    {doc_content}
    
    Return ONLY the JSON array, nothing else.
    """
    
    print("    Identifying skill sections...")
    response = await call_llm(session, prompt)
    cleaned = clean_response(response, "json")
    
    try:
        skills = json.loads(cleaned)
        if isinstance(skills, list):
            print(f"    Found {len(skills)} skills to extract")
            return skills
        else:
            print("    WARNING: Expected array for skill identification")
            return []
    except json.JSONDecodeError as e:
        print(f"    WARNING: Could not parse skill list: {e}")
        return []


async def extract_batch(session: aiohttp.ClientSession, skill_names: List[str], doc_content: str) -> List[Dict]:
    """Extract a batch of skills."""
    skill_list_text = "\n".join([f"- {name}" for name in skill_names])
    prompt = EXTRACTION_PROMPTS["skills_batch"].format(doc=doc_content, skill_list=skill_list_text)
    
    response = await call_llm(session, prompt, timeout=600)
    cleaned = clean_response(response, "json")
    
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        else:
            return [data] if data else []
    except json.JSONDecodeError as e:
        print(f"    WARNING: JSON parse error in batch: {e}")
        return []


async def extract_skills_assessment_batched(
    session: aiohttp.ClientSession, 
    doc_content: str,
    batch_size: int = 7
) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract skills in batches with inline verification.
    
    Returns: (verified_skills, failures)
    
    If any batch fails verification:
    - Return immediately with partial results + failures
    - Caller decides whether to continue or abort
    """
    all_skills = []
    failures = []
    
    # First pass: identify all skill sections in doc
    skill_sections = await identify_skill_sections(session, doc_content)
    
    if not skill_sections:
        print("  WARNING: No skills identified for extraction")
        return [], []
    
    # Process in batches
    total_batches = (len(skill_sections) + batch_size - 1) // batch_size
    print(f"  Processing {len(skill_sections)} skills in {total_batches} batches...")
    
    for i in range(0, len(skill_sections), batch_size):
        batch_num = (i // batch_size) + 1
        batch = skill_sections[i:i+batch_size]
        
        print(f"    Batch {batch_num}/{total_batches}: {len(batch)} skills")
        
        # Extract this batch
        batch_skills = await extract_batch(session, batch, doc_content)
        
        # Verify each skill's our_take
        batch_verified = 0
        for skill in batch_skills:
            if not isinstance(skill, dict):
                continue
            
            our_take = skill.get('our_take', '')
            if verify_our_take_exists(our_take, doc_content):
                all_skills.append(skill)
                batch_verified += 1
            else:
                failures.append({
                    'skill_name': skill.get('skill_name', 'Unknown'),
                    'reason': 'our_take not found in source',
                    'extracted_text': our_take[:200] if our_take else 'null'
                })
        
        print(f"    Batch {batch_num}: {batch_verified}/{len(batch_skills)} verified")
        
        # Fail-fast: stop on first verification failure
        if failures:
            print(f"  ⚠️ Verification failed at batch {batch_num}")
            break
    
    return all_skills, failures


def write_failure_report(output_dir: Path, failures: List[Dict], doc_path: str, candidate: str, company: str):
    """Write FAILED.md with details about what went wrong."""
    
    failed_path = output_dir / "FAILED.md"
    
    content = f"""---
created: {datetime.now().isoformat()}
status: failed
candidate: {candidate}
company: {company}
source: {doc_path}
failure_count: {len(failures)}
---

# Decomposition Failed

**Candidate:** {candidate}
**Company:** {company}
**Source:** {doc_path}

## Verification Failures

The following extractions could not be verified against the source document:

"""
    for f in failures:
        content += f"""### {f['skill_name']}
- **Reason:** {f['reason']}
- **Extracted text (first 200 chars):**
  > {f.get('extracted_text', 'N/A')}

"""
    
    content += """
## Next Steps

1. Check if the source document is complete/uncorrupted
2. Review the skill sections manually
3. Re-run decomposition after fixing source issues

---
*This file indicates decomposition was attempted but failed verification.*
*No partial outputs were written to prevent downstream hallucination propagation.*
"""
    
    failed_path.write_text(content)


async def extract_category(
    session: aiohttp.ClientSession,
    category: str,
    doc_content: str,
    jd_content: str = None
) -> dict:
    """Extract a single category using LLM."""
    prompt_template = EXTRACTION_PROMPTS[category]
    
    if category == "alignment":
        prompt = prompt_template.format(doc=doc_content, jd=jd_content)
    else:
        prompt = prompt_template.format(doc=doc_content)
    
    print(f"  Extracting {category}...")
    response = await call_llm(session, prompt)
    
    # Clean and parse YAML
    cleaned = clean_response(response, "yaml")
    try:
        data = yaml.safe_load(cleaned)
        return data
    except yaml.YAMLError as e:
        print(f"  WARNING: YAML parse error for {category}: {e}")
        return {"_raw": cleaned, "_error": str(e)}


async def extract_skills_assessment(session: aiohttp.ClientSession, doc_content: str) -> list:
    """Extract all skill assessments using LLM."""
    prompt = EXTRACTION_PROMPTS["skills_assessment"].format(doc=doc_content)
    
    print("  Extracting skills_assessment (this may take a minute)...")
    response = await call_llm(session, prompt, timeout=600)  # Longer timeout for big extraction
    
    cleaned = clean_response(response, "json")
    
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            print(f"    Extracted {len(data)} skills")
            return data
        else:
            print(f"    WARNING: Expected array, got {type(data)}")
            return [data] if data else []
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse error: {e}")
        # Try to salvage partial JSON
        try:
            # Sometimes the response gets cut off - try to find valid JSON
            if cleaned.startswith('['):
                # Find last complete object
                last_brace = cleaned.rfind('}')
                if last_brace > 0:
                    truncated = cleaned[:last_brace+1] + ']'
                    data = json.loads(truncated)
                    print(f"    Salvaged {len(data)} skills from truncated response")
                    return data
        except:
            pass
        return [{"_error": str(e), "_raw": cleaned[:1000]}]


def validate_scores(scores: list) -> tuple[bool, list]:
    """Validate scores against canonical schema. Returns (is_valid, errors)."""
    if not HAS_JSONSCHEMA:
        print("  WARNING: jsonschema not installed, skipping validation")
        return True, []
    
    if not SCHEMA_PATH.exists():
        print(f"  WARNING: Schema not found at {SCHEMA_PATH}")
        return True, []
    
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    
    errors = []
    try:
        jsonschema.validate(scores, schema)
        return True, []
    except jsonschema.ValidationError as e:
        errors.append(str(e.message))
        return False, errors


async def decompose(doc_path: str, jd_input: str, candidate: str, company: str, 
                    input_json: str = None, fail_fast: bool = True):
    """Main decomposition function."""
    
    # Read source document
    with open(doc_path, 'r') as f:
        doc_content = f.read()
    
    # Read JD (could be file path or inline text)
    if os.path.exists(jd_input):
        with open(jd_input, 'r') as f:
            jd_content = f.read()
    else:
        jd_content = jd_input
    
    # Extract careerspan_score from text pattern
    detected_score = extract_score_from_text(doc_content)
    if detected_score:
        print(f"  Detected careerspan_score from text: {detected_score}")

    # Create output directory
    slug = f"{candidate.lower()}-{company.lower()}"
    output_dir = INBOX_PATH / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Decomposing {candidate} for {company}...")
    print(f"Output: {output_dir}")
    print()
    
    # Check if document is large enough to warrant chunked processing
    line_count = doc_content.count('\n') + 1
    use_chunked = HAS_CHUNK_PROCESSOR and should_use_chunked_processing(doc_content)
    
    if use_chunked:
        # MODE C: Chunked parallel processing for large documents
        print(f"Using chunked processing mode ({line_count} lines > {CHUNK_THRESHOLD} threshold)")
        work_dir = output_dir / ".work"
        overview_data, skills = await process_document_chunked(doc_content, work_dir)
        
        # Use overview from chunk processor, fall back to detected score
        if not overview_data.get("overall_score") and detected_score:
            overview_data["overall_score"] = detected_score
        
        # Build scores_data using chunk processor helper
        scores_data = build_scores_complete(overview_data, skills)
        
        # Write scores_complete.json
        scores_path = output_dir / "scores_complete.json"
        with open(scores_path, 'w') as f:
            json.dump(scores_data, f, indent=2, ensure_ascii=False)
        print(f"  Wrote scores_complete.json ({len(skills)} skills)")
        
        # Copy JD and source
        jd_filepath = output_dir / "jd.yaml"
        with open(jd_filepath, 'w') as f:
            f.write(f"# Job Description\n# Source: Provided JD\n\nraw_jd: |\n")
            for line in jd_content.split('\n'):
                f.write(f"  {line}\n")
        print(f"  Wrote jd.yaml")
        
        # Write source OCR
        ocr_path = output_dir / "careerspan_full_ocr.txt"
        with open(ocr_path, 'w') as f:
            f.write(doc_content)
        print(f"  Wrote careerspan_full_ocr.txt")
        
        # Write overview.yaml for backward compatibility
        overview_yaml_path = output_dir / "overview.yaml"
        with open(overview_yaml_path, 'w') as f:
            yaml.dump({
                "candidate": candidate,
                "company": company,
                "careerspan_score": {
                    "overall": scores_data.get("overall_score"),
                    **{k: v.get("score") for k, v in scores_data.get("category_scores", {}).items()}
                },
                "bottom_line": scores_data.get("bottom_line"),
                "overall_strengths": scores_data.get("overall_strengths"),
                "overall_weaknesses": scores_data.get("overall_weaknesses"),
                "potential_dealbreakers": scores_data.get("potential_dealbreakers", [])
            }, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"  Wrote overview.yaml")
        
        # Validate
        is_valid, errors = validate_scores(scores_data)
        if not is_valid:
            print(f"  WARNING: Schema validation failed: {errors[:3]}")
        else:
            print(f"  ✓ Schema validation passed")
        
        # Count ratings
        rating_counts = {}
        for skill in skills:
            if isinstance(skill, dict):
                r = skill.get("rating", "Unknown")
                rating_counts[r] = rating_counts.get(r, 0) + 1
        
        # Write manifest
        manifest = {
            "schema_version": "1.0",
            "created": datetime.now().isoformat(),
            "framework": "careerspan-decomposer",
            "extraction_method": "chunked-parallel",
            "candidate": candidate,
            "company": company,
            "slug": slug,
            "source_doc": str(doc_path),
            "careerspan_score": scores_data.get("overall_score"),
            "processing": {
                "mode": "chunked_parallel",
                "line_count": line_count,
                "threshold": CHUNK_THRESHOLD
            },
            "files": ["overview.yaml", "jd.yaml", "scores_complete.json", "careerspan_full_ocr.txt"],
            "counts": {
                "total_skills": len(skills),
                "by_rating": rating_counts
            },
            "validation": {
                "schema_valid": is_valid,
                "errors": errors[:5] if errors else []
            },
            "status": "complete"
        }
        
        manifest_path = output_dir / "manifest.yaml"
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"  Wrote manifest.yaml")
        
        print()
        print(f"✓ Decomposition complete (chunked mode): {output_dir}")
        print(f"  Skills: {len(skills)} ({rating_counts})")
        print(f"  Score: {scores_data.get('overall_score')}/100")
        
        return str(output_dir)
    
    elif input_json:
        # MODE B: Structured input - minimal LLM, maximum trust
        print("Using structured input mode (--input-json)")
        skills, failures = process_structured_input(input_json, doc_content, output_dir)
        
        if failures:
            write_failure_report(output_dir, failures, doc_path, candidate, company)
            print(f"\n❌ VALIDATION FAILED: {len(failures)} issues in structured input")
            print(f"   See: {output_dir}/FAILED.md")
            sys.exit(1)
    else:
        # MODE A: LLM extraction from OCR/text (existing path, now with batching)
        async with aiohttp.ClientSession() as session:
            if fail_fast:
                skills, failures = await extract_skills_assessment_batched(session, doc_content)
                
                if failures:
                    # FAIL FAST: Write FAILED.md and exit
                    write_failure_report(output_dir, failures, doc_path, candidate, company)
                    print(f"\n❌ DECOMPOSITION FAILED: {len(failures)} verification failures")
                    print(f"   See: {output_dir}/FAILED.md")
                    sys.exit(1)
            else:
                # Original extraction method
                skills = await extract_skills_assessment(session, doc_content)
    
    # Continue with rest of extraction for both modes
    async with aiohttp.ClientSession() as session:
        results = {}
        
        # Run first batch in parallel
        batch1 = ["overview", "profile", "experience", "tools"]
        tasks1 = [extract_category(session, cat, doc_content) for cat in batch1]
        batch1_results = await asyncio.gather(*tasks1)
        for cat, result in zip(batch1, batch1_results):
            results[cat] = result
        
        # Inject detected score if overview extraction missed it
        if detected_score and results.get("overview"):
            if isinstance(results["overview"], dict):
                if not results["overview"].get("careerspan_score") or \
                   results["overview"].get("careerspan_score", {}).get("overall") is None:
                    results["overview"]["careerspan_score"] = {
                        "overall": detected_score,
                        "max": 100,
                        "qualification": results["overview"].get("careerspan_score", {}).get("qualification", "Unknown"),
                        "career_trajectory": results["overview"].get("careerspan_score", {}).get("career_trajectory", "Unknown")
                    }
                    print(f"  Injected detected score {detected_score} into overview")
        
        # Run second batch in parallel
        batch2 = ["hard_skills", "soft_skills", "achievements", "interests"]
        tasks2 = [extract_category(session, cat, doc_content) for cat in batch2]
        batch2_results = await asyncio.gather(*tasks2)
        for cat, result in zip(batch2, batch2_results):
            results[cat] = result
        
        # Alignment needs both doc and JD
        print("  Extracting alignment...")
        results["alignment"] = await extract_category(session, "alignment", doc_content, jd_content)
        
        # Culture signals extraction from JD only
        print("  Extracting culture signals from JD...")
        results["culture_signals"] = await extract_category(session, "culture_signals", jd_content, None)
    
    # Write YAML files
    file_mapping = {
        "overview": "overview.yaml",
        "profile": "profile.yaml",
        "experience": "experience.yaml",
        "hard_skills": "hard_skills.yaml",
        "soft_skills": "soft_skills.yaml",
        "tools": "tools.yaml",
        "achievements": "achievements.yaml",
        "interests": "interests.yaml",
        "alignment": "alignment.yaml",
        "culture_signals": "culture_signals.yaml"
    }
    
    for category, filename in file_mapping.items():
        filepath = output_dir / filename
        with open(filepath, 'w') as f:
            f.write(f"# {category.replace('_', ' ').title()}\n")
            f.write(f"# Extracted: {datetime.now().isoformat()}\n")
            f.write(f"# Method: Structured extraction\n")
            f.write(f"# DO NOT EDIT\n\n")
            yaml.dump(results[category], f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"  Wrote {filename}")
    
    # Write JD
    jd_filepath = output_dir / "jd.yaml"
    with open(jd_filepath, 'w') as f:
        f.write(f"# Job Description\n")
        f.write(f"# Source: Provided JD\n\n")
        f.write(f"raw_jd: |\n")
        for line in jd_content.split('\n'):
            f.write(f"  {line}\n")
    print(f"  Wrote jd.yaml")
    
    # Build signal_strength from evidence_type distribution
    signal_counts = {"story_verified": 0, "resume_only": 0, "inferred": 0}
    for skill in skills:
        if isinstance(skill, dict):
            et = skill.get("evidence_type", "").lower().replace("+", "_").replace(" ", "_")
            if "story" in et:
                signal_counts["story_verified"] += 1
            elif "resume" in et or "profile" in et:
                signal_counts["resume_only"] += 1
            else:
                signal_counts["inferred"] += 1
    
    total_signals = sum(signal_counts.values()) or 1
    signal_strength = {
        "story_verified_pct": round(100 * signal_counts["story_verified"] / total_signals, 1),
        "resume_only_pct": round(100 * signal_counts["resume_only"] / total_signals, 1),
        "inferred_pct": round(100 * signal_counts["inferred"] / total_signals, 1)
    }
    
    # Get category scores from overview extraction or default
    category_scores = {}
    if isinstance(results.get("overview"), dict):
        cat_scores_raw = results["overview"].get("category_scores", {})
        for cat in ["background", "uniqueness", "responsibilities", "hard_skills", "soft_skills"]:
            if isinstance(cat_scores_raw.get(cat), dict):
                category_scores[cat] = cat_scores_raw[cat]
            else:
                category_scores[cat] = {"score": None, "max": 100}
    else:
        for cat in ["background", "uniqueness", "responsibilities", "hard_skills", "soft_skills"]:
            category_scores[cat] = {"score": None, "max": 100}
    
    # Get bottom_line from overview
    bottom_line = ""
    overall_strengths = None
    overall_weaknesses = None
    potential_dealbreakers = []
    
    if isinstance(results.get("overview"), dict):
        overview = results["overview"]
        # Try multiple fields for bottom_line
        bottom_line = overview.get("bottom_line") or overview.get("verdict") or overview.get("summary") or ""
        overall_strengths = overview.get("overall_strengths")
        overall_weaknesses = overview.get("overall_weaknesses")
        potential_dealbreakers = overview.get("potential_dealbreakers", [])
    
    # Build the wrapped scores structure
    scores_data = {
        "overall_score": detected_score,
        "bottom_line": bottom_line,
        "overall_strengths": overall_strengths,
        "overall_weaknesses": overall_weaknesses,
        "potential_dealbreakers": potential_dealbreakers,
        "category_scores": category_scores,
        "signal_strength": signal_strength,
        "skills": skills
    }
    
    # Write scores_complete.json
    scores_path = output_dir / "scores_complete.json"
    with open(scores_path, 'w') as f:
        json.dump(scores_data, f, indent=2, ensure_ascii=False)
    print(f"  Wrote scores_complete.json ({len(skills)} skills)")
    
    # Write scores_complete.csv for spreadsheet analysis
    csv_path = output_dir / "scores_complete.csv"
    with open(csv_path, 'w') as f:
        f.write("skill_name,category,rating,required_level,importance,direct_experience_score,experience_type,evidence_type\n")
        for skill in skills:
            if isinstance(skill, dict) and "skill_name" in skill:
                f.write(f'"{skill.get("skill_name", "")}",'\
                       f'"{skill.get("category", "")}",'\
                       f'"{skill.get("rating", "")}",'\
                       f'"{skill.get("required_level", "")}",'\
                       f'{skill.get("importance", "")},'\
                       f'{skill.get("direct_experience_score", "")},'\
                       f'"{skill.get("experience_type", "")}",'\
                       f'"{skill.get("evidence_type", "")}"\n')
    print(f"  Wrote scores_complete.csv")
    
    # Validate against schema
    is_valid, errors = validate_scores(scores_data)  # Pass wrapped structure
    if not is_valid:
        print(f"  WARNING: Schema validation failed: {errors[:3]}")
    else:
        print(f"  ✓ Schema validation passed")
    
    # Count ratings
    rating_counts = {}
    for skill in skills:  # Use skills array directly
        if isinstance(skill, dict):
            r = skill.get("rating", "Unknown")
            rating_counts[r] = rating_counts.get(r, 0) + 1
    
    # Write manifest
    manifest = {
        "schema_version": "1.0",
        "created": datetime.now().isoformat(),
        "framework": "careerspan-decomposer",
        "extraction_method": "structured-json" if input_json else ("llm-semantic-batched" if fail_fast else "llm-semantic"),
        "candidate": candidate,
        "company": company,
        "slug": slug,
        "source_doc": str(doc_path),
        "careerspan_score": detected_score,
        "files": list(file_mapping.values()) + ["jd.yaml", "scores_complete.json", "scores_complete.csv"],
        "counts": {
            "total_skills": len(skills),
            "by_rating": rating_counts
        },
        "validation": {
            "schema_valid": is_valid,
            "errors": errors[:5] if errors else []
        },
        "status": "complete",
        "notes": "Extracted via LLM semantic analysis. DO NOT manually edit extraction files." if not input_json else "Extracted from structured JSON input with validation. DO NOT manually edit extraction files."
    }
    
    manifest_path = output_dir / "manifest.yaml"
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Wrote manifest.yaml")
    
    print()
    print(f"✓ Decomposition complete: {output_dir}")
    print(f"  Skills: {len(skills)} ({rating_counts})")
    print(f"  Score: {detected_score}/100" if detected_score else "  Score: Not detected")
    print(f"  Status: Ready for Meta-Resume Generator")
    
    return str(output_dir)


def main():
    parser = argparse.ArgumentParser(description="Careerspan Decomposer - LLM-based semantic extraction")
    parser.add_argument("--doc", required=True, help="Path to Careerspan Intelligence Brief (text/OCR)")
    parser.add_argument("--jd", required=True, help="Path to JD file or JD text")
    parser.add_argument("--candidate", required=True, help="Candidate name (for slug)")
    parser.add_argument("--company", required=True, help="Company name (for slug)")
    parser.add_argument("--input-json", help="Path to structured JSON input from endpoint")
    parser.add_argument("--no-fail-fast", action="store_true", 
                        help="Continue on verification failures (not recommended)")
    
    args = parser.parse_args()
    
    fail_fast = not args.no_fail_fast
    
    output_path = asyncio.run(decompose(args.doc, args.jd, args.candidate, args.company, args.input_json, fail_fast))
    print(f"\nOutput directory: {output_path}")


if __name__ == "__main__":
    main()
