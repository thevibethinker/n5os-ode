#!/usr/bin/env python3
"""
LinkedIn Voice Primitives Extractor

Extracts linguistic and conceptual primitives from V's LinkedIn corpus
to seed the Voice Library V2.

Pipeline:
  1. prep     - Extract comments + shares from DuckDB, build frequency data
  2. chunk    - Semantic chunking + primitive extraction (batched LLM)
  3. synth    - Deduplicate, find patterns, rank
  4. review   - Generate human review queue
  5. import   - Load approved primitives to voice_library.db

Usage:
  python3 linkedin_voice_extractor.py prep
  python3 linkedin_voice_extractor.py chunk [--batch-size 15]
  python3 linkedin_voice_extractor.py synth
  python3 linkedin_voice_extractor.py review
  python3 linkedin_voice_extractor.py import --approved review_file.md

Created: 2026-01-12
Provenance: con_wPcuQVQiz9f4L7Te
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp
import duckdb

# Use centralized paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from N5.lib.paths import N5_ROOT, N5_DATA_DIR, WORKSPACE_ROOT

# Paths - derived from centralized constants
LINKEDIN_DB = WORKSPACE_ROOT / "Datasets" / "linkedin-full-pre-jan-10" / "data.duckdb"
BUILD_DIR = N5_ROOT / "builds" / "voice-library-v2"
VOICE_LIBRARY_DB = N5_DATA_DIR / "voice_library.db"
REVIEW_DIR = N5_ROOT / "review" / "voice"

# Output files
CORPUS_FILE = BUILD_DIR / "linkedin_corpus.jsonl"
FREQUENCY_FILE = BUILD_DIR / "linkedin_frequency.json"
PRIMITIVES_RAW_FILE = BUILD_DIR / "linkedin_primitives_raw.jsonl"
PRIMITIVES_RANKED_FILE = BUILD_DIR / "linkedin_primitives_ranked.jsonl"

# Config
MIN_COMMENT_LENGTH = 100
BATCH_SIZE = 15
MAX_CONCURRENT_REQUESTS = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)


# =============================================================================
# STEP 1: Data Prep
# =============================================================================

def extract_corpus():
    """Extract comments and shares from LinkedIn DuckDB into unified corpus."""
    log.info(f"Connecting to {LINKEDIN_DB}")
    
    conn = duckdb.connect(str(LINKEDIN_DB), read_only=True)
    
    corpus = []
    
    # Extract comments (≥100 chars)
    log.info("Extracting comments...")
    comments = conn.execute("""
        SELECT 
            message as text,
            commented_at as timestamp,
            link as context_url
        FROM comments
        WHERE message IS NOT NULL 
          AND LENGTH(message) >= ?
        ORDER BY commented_at DESC
    """, [MIN_COMMENT_LENGTH]).fetchall()
    
    for text, ts, url in comments:
        corpus.append({
            "id": f"comment_{len(corpus)}",
            "type": "comment",
            "text": text.strip(),
            "timestamp": str(ts) if ts else None,
            "context_url": url,
            "char_count": len(text)
        })
    
    log.info(f"  Found {len(comments)} comments ≥{MIN_COMMENT_LENGTH} chars")
    
    # Extract shares with commentary
    log.info("Extracting shares with commentary...")
    shares = conn.execute("""
        SELECT 
            share_commentary as text,
            shared_at as timestamp,
            share_link as context_url
        FROM shares
        WHERE share_commentary IS NOT NULL 
          AND share_commentary != ''
          AND LENGTH(share_commentary) >= 50
        ORDER BY shared_at DESC
    """).fetchall()
    
    for text, ts, url in shares:
        corpus.append({
            "id": f"share_{len(corpus)}",
            "type": "share",
            "text": text.strip(),
            "timestamp": str(ts) if ts else None,
            "context_url": url,
            "char_count": len(text)
        })
    
    log.info(f"  Found {len(shares)} shares with commentary")
    
    conn.close()
    
    # Write corpus
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    with open(CORPUS_FILE, "w") as f:
        for item in corpus:
            f.write(json.dumps(item) + "\n")
    
    log.info(f"Wrote {len(corpus)} items to {CORPUS_FILE}")
    return corpus


def compute_frequency(corpus: list[dict]) -> dict:
    """Compute n-gram frequency within V's corpus."""
    log.info("Computing n-gram frequencies...")
    
    # Combine all text
    all_text = " ".join(item["text"] for item in corpus)
    
    # Normalize
    all_text = all_text.lower()
    
    # Extract n-grams (2-5 words)
    words = re.findall(r'\b\w+\b', all_text)
    
    ngram_counts = {}
    for n in range(2, 6):
        ngrams = [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]
        counts = Counter(ngrams)
        # Keep only those appearing 2+ times
        frequent = {k: v for k, v in counts.items() if v >= 2}
        ngram_counts[f"{n}-gram"] = dict(sorted(frequent.items(), key=lambda x: -x[1])[:100])
    
    # Also track distinctive phrases (manual patterns)
    patterns = {
        "em_dash_pivots": len(re.findall(r'—', all_text)),
        "rhetorical_questions": len(re.findall(r'\?[^?]*\?', all_text)),
        "not_about_x_about_y": len(re.findall(r"not about .{3,30}—.{3,30}about", all_text, re.I)),
    }
    
    frequency_data = {
        "corpus_size": len(corpus),
        "total_words": len(words),
        "ngrams": ngram_counts,
        "patterns": patterns,
        "generated_at": datetime.now().isoformat()
    }
    
    with open(FREQUENCY_FILE, "w") as f:
        json.dump(frequency_data, f, indent=2)
    
    log.info(f"Wrote frequency data to {FREQUENCY_FILE}")
    
    # Log top findings
    log.info("Top 5 repeated 3-grams:")
    for phrase, count in list(ngram_counts.get("3-gram", {}).items())[:5]:
        log.info(f"  '{phrase}': {count}x")
    
    return frequency_data


def cmd_prep(args):
    """Step 1: Data prep command."""
    corpus = extract_corpus()
    frequency = compute_frequency(corpus)
    
    print(f"\n✓ Data prep complete")
    print(f"  Corpus: {len(corpus)} items → {CORPUS_FILE}")
    print(f"  Frequency: {frequency['total_words']} words analyzed → {FREQUENCY_FILE}")


# =============================================================================
# STEP 2: Semantic Chunking + Extraction
# =============================================================================

EXTRACTION_PROMPT = """You are analyzing V's LinkedIn writing to extract distinctive linguistic primitives for a voice library.

## Your Task
For each piece of writing below, do TWO things:

### 1. SEMANTIC CHUNKING
Break the text into semantic blocks — each block is ONE complete thought, argument, or point.
Mark block boundaries with [BLOCK_START] and [BLOCK_END].

### 2. PRIMITIVE EXTRACTION  
From each block, extract any of these primitives:

| Type | What to look for | Example |
|------|------------------|---------|
| signature_phrase | Distinctive coined terms or repeated phrases | "the talent cliff", "career optionality" |
| syntactic_pattern | Structural devices: em-dash pivots, short declaratives | "X—but actually Y", "That's not strategy. That's hope." |
| conceptual_frame | "It's not about X, it's about Y" reframes | "It's not about finding a job—it's about building options" |
| metaphor | Conceptual mappings | "career as portfolio", "skills as currency" |
| analogy | X is like Y comparisons | "Networking is like compound interest" |
| rhetorical_device | Questions, inversions, repetition for effect | "What if...?", "The question isn't X, it's Y" |

## Output Format
For each piece, output valid JSONL (one JSON object per line):

Example:
{{"source_id": "comment_123", "block_num": 1, "block_text": "the semantic block text", "primitives": [{{"type": "metaphor", "text": "career as portfolio", "extractable_form": "X as Y (where X is professional element, Y is financial metaphor)", "context": "used when discussing job changes"}}]}}

If a block has no extractable primitives, just omit that block from the output.

## Frequency Hints
These phrases appear multiple times in V's corpus (strong signal for signature phrases):
{frequency_hints}

## Writing Samples to Analyze
{samples}

## Output (JSONL only, no commentary):
"""


async def call_zo_ask(session: aiohttp.ClientSession, prompt: str) -> str:
    """Call the /zo/ask API."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    async with session.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json={"input": prompt}
    ) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"Zo API error {resp.status}: {text}")
        result = await resp.json()
        return result["output"]


async def process_batch(
    session: aiohttp.ClientSession,
    batch: list[dict],
    frequency_hints: str,
    batch_num: int
) -> list[dict]:
    """Process a batch of corpus items through LLM extraction."""
    
    # Format samples
    samples = "\n\n".join([
        f"### {item['id']} ({item['type']}, {item['char_count']} chars)\n{item['text']}"
        for item in batch
    ])
    
    prompt = EXTRACTION_PROMPT.format(
        frequency_hints=frequency_hints,
        samples=samples
    )
    
    log.info(f"Processing batch {batch_num} ({len(batch)} items)...")
    
    try:
        response = await call_zo_ask(session, prompt)
        
        # Parse JSONL response
        results = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("{"):
                try:
                    obj = json.loads(line)
                    results.append(obj)
                except json.JSONDecodeError:
                    log.warning(f"Failed to parse line: {line[:100]}...")
        
        log.info(f"  Batch {batch_num}: extracted {len(results)} blocks")
        return results
        
    except Exception as e:
        log.error(f"Batch {batch_num} failed: {e}")
        return []


async def run_extraction(batch_size: int):
    """Run semantic chunking + extraction on entire corpus."""
    
    # Load corpus
    if not CORPUS_FILE.exists():
        log.error(f"Corpus not found. Run 'prep' first.")
        sys.exit(1)
    
    corpus = []
    with open(CORPUS_FILE) as f:
        for line in f:
            corpus.append(json.loads(line))
    
    # Load frequency hints
    frequency_hints = "No frequency data available."
    if FREQUENCY_FILE.exists():
        with open(FREQUENCY_FILE) as f:
            freq = json.load(f)
            top_phrases = list(freq.get("ngrams", {}).get("3-gram", {}).items())[:10]
            if top_phrases:
                frequency_hints = "\n".join([f"- \"{p}\": {c}x" for p, c in top_phrases])
    
    # Batch corpus
    batches = [corpus[i:i+batch_size] for i in range(0, len(corpus), batch_size)]
    log.info(f"Processing {len(corpus)} items in {len(batches)} batches of {batch_size}")
    
    # Process with concurrency limit
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    all_results = []
    
    async with aiohttp.ClientSession() as session:
        async def bounded_process(batch, batch_num):
            async with semaphore:
                return await process_batch(session, batch, frequency_hints, batch_num)
        
        tasks = [bounded_process(batch, i+1) for i, batch in enumerate(batches)]
        batch_results = await asyncio.gather(*tasks)
        
        for results in batch_results:
            all_results.extend(results)
    
    # Write raw primitives
    with open(PRIMITIVES_RAW_FILE, "w") as f:
        for item in all_results:
            f.write(json.dumps(item) + "\n")
    
    # Count primitives
    total_primitives = sum(len(r.get("primitives", [])) for r in all_results)
    log.info(f"Extraction complete: {len(all_results)} blocks, {total_primitives} primitives")
    
    return all_results


def cmd_chunk(args):
    """Step 2: Semantic chunking + extraction command."""
    results = asyncio.run(run_extraction(args.batch_size))
    
    total_primitives = sum(len(r.get("primitives", [])) for r in results)
    print(f"\n✓ Chunking + extraction complete")
    print(f"  Blocks: {len(results)}")
    print(f"  Raw primitives: {total_primitives}")
    print(f"  Output: {PRIMITIVES_RAW_FILE}")


# =============================================================================
# STEP 3: Synthesis (Local Heuristics - No LLM)
# =============================================================================

# Generic engagement openers to EXCLUDE (too common, not distinctive)
GENERIC_OPENERS = {
    "couldn't agree more",
    "couldn t agree more",
    "love this",
    "great post",
    "thanks for sharing",
    "well said",
    "so true",
    "this is great",
    "great point",
    "exactly this",
    "100%",
    "this resonates",
    "spot on",
    "nailed it",
    "perfectly said",
    "agree completely",
    "absolutely",
    "totally agree",
    "yes yes yes",
    "preach",
    "louder for the people",
    "this right here",
    "underrated take",
    "underrated post",
    "here for this",
    "following for",
    "great share",
    "interesting read",
    "food for thought",
    "makes you think",
    "good stuff",
    "nice one",
    "congrats",
    "congratulations",
    "well deserved",
    "so proud",
    "amazing work",
    "keep it up",
    "keep going",
}

# Domain keywords for tagging
DOMAIN_KEYWORDS = {
    "career-coaching": ["career", "coaching", "coach", "transition", "pivot", "reinvention", "path", "trajectory", "growth"],
    "hiring": ["hiring", "hire", "recruiter", "recruiting", "talent acquisition", "sourcing", "employer", "candidate experience"],
    "recruiting": ["recruiting", "recruitment", "headhunter", "talent", "pipeline", "outreach", "sourcing"],
    "interviewing": ["interview", "interviewing", "behavioral", "questions", "screening", "assessment"],
    "job-search": ["job search", "job hunting", "apply", "application", "resume", "cv", "cover letter", "linkedin"],
    "networking": ["network", "networking", "connection", "relationship", "warm intro", "referral"],
    "leadership": ["leader", "leadership", "manage", "management", "team", "culture", "org"],
    "entrepreneurship": ["founder", "startup", "entrepreneur", "venture", "business", "company"],
    "personal-brand": ["brand", "branding", "visibility", "content", "thought leader", "presence"],
    "skills": ["skill", "skills", "competency", "learning", "upskill", "reskill"],
}

# Pattern reversal detection patterns
PATTERN_REVERSAL_PATTERNS = [
    r"not\s+(?:about\s+)?(.{3,40})[\s—\-]+(?:it'?s\s+)?about\s+(.{3,40})",
    r"it'?s\s+not\s+(.{3,40})[\s—\-]+it'?s\s+(.{3,40})",
    r"the\s+(?:real\s+)?(?:question|problem|issue)\s+isn'?t\s+(.{3,40})[\s—\-]+(?:it'?s|but)\s+(.{3,40})",
    r"stop\s+(?:asking|thinking|worrying)\s+(?:about\s+)?(.{3,40})[\s—\-]+(?:start|focus|instead)\s+(.{3,40})",
    r"less\s+(.{3,20})\s*[,—\-]+\s*more\s+(.{3,20})",
    r"(.{3,30})\s+is\s+overrated[\s,—\-]+(.{3,30})\s+is\s+underrated",
]


def is_generic_opener(text: str) -> bool:
    """Check if text is a generic engagement opener."""
    normalized = text.lower().strip()
    # Direct match
    if normalized in GENERIC_OPENERS:
        return True
    # Prefix match (e.g., "couldn't agree more with this")
    for opener in GENERIC_OPENERS:
        if normalized.startswith(opener):
            return True
    return False


def compute_distinctiveness(text: str, prim_type: str, corpus_freq: dict) -> float:
    """
    Compute distinctiveness score (0-1) based on:
    - Length (longer = more specific, up to a point)
    - Presence of distinctive markers (em-dash, colon pivots)
    - Type-specific bonuses
    - Penalize very short or very generic
    """
    score = 0.5  # baseline
    
    # Length factor (sweet spot: 20-100 chars)
    length = len(text)
    if length < 15:
        score -= 0.3  # too short, likely fragment
    elif length < 30:
        score -= 0.1
    elif 30 <= length <= 100:
        score += 0.1  # good length
    elif length > 150:
        score -= 0.05  # might be too context-specific
    
    # Structural markers (em-dash, pivot phrases)
    if "—" in text:
        score += 0.15
    if ":" in text and len(text.split(":")) == 2:
        score += 0.05
    
    # Type bonuses
    if prim_type == "conceptual_frame":
        score += 0.1
    elif prim_type == "metaphor":
        score += 0.1
    elif prim_type == "analogy":
        score += 0.1
    elif prim_type == "signature_phrase":
        score += 0.05
    
    # Penalize if contains generic engagement language
    lower_text = text.lower()
    generic_words = ["agree", "love this", "great", "thanks", "amazing", "awesome"]
    for gw in generic_words:
        if gw in lower_text and length < 50:
            score -= 0.2
            break
    
    # Bonus for specificity markers
    specificity_markers = ["the", "a", "an"]  # Articles suggest concrete reference
    if any(lower_text.startswith(m + " ") for m in specificity_markers):
        score += 0.02
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, score))


def detect_domains(text: str) -> list[str]:
    """Detect which domains a primitive relates to."""
    lower_text = text.lower()
    domains = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in lower_text:
                domains.append(domain)
                break
    return list(set(domains))


def detect_pattern_reversal(text: str) -> bool:
    """Detect if text uses a 'not X but Y' or similar reversal pattern."""
    for pattern in PATTERN_REVERSAL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    # Also check for simple structural markers
    lower = text.lower()
    if "not about" in lower and "about" in lower[lower.find("not about")+10:]:
        return True
    if "isn't" in lower and ("it's" in lower or "but" in lower):
        return True
    return False


def compute_synthesis():
    """
    Local synthesis: deduplicate, score, tag, rank primitives.
    No LLM call - pure heuristics.
    """
    if not PRIMITIVES_RAW_FILE.exists():
        log.error("Raw primitives not found. Run 'chunk' first.")
        sys.exit(1)
    
    # Load raw primitives
    raw_blocks = []
    with open(PRIMITIVES_RAW_FILE) as f:
        for line in f:
            raw_blocks.append(json.loads(line))
    
    # Load frequency data for corpus-level signals
    corpus_freq = {}
    if FREQUENCY_FILE.exists():
        with open(FREQUENCY_FILE) as f:
            corpus_freq = json.load(f)
    
    # Extract all primitives with their source info
    all_primitives = []
    for block in raw_blocks:
        source_id = block.get("source_id", "unknown")
        for prim in block.get("primitives", []):
            prim["source_ids"] = [source_id]
            all_primitives.append(prim)
    
    log.info(f"Processing {len(all_primitives)} raw primitives...")
    
    # Step 1: Filter out generic openers
    filtered = []
    generic_count = 0
    for p in all_primitives:
        text = p.get("text", "").strip()
        if is_generic_opener(text):
            generic_count += 1
            continue
        if len(text) < 10:  # too short
            continue
        filtered.append(p)
    
    log.info(f"  Filtered out {generic_count} generic openers, {len(all_primitives) - len(filtered) - generic_count} too-short")
    log.info(f"  Remaining: {len(filtered)} candidates")
    
    # Step 2: Deduplicate by normalized text
    seen_texts = {}
    deduplicated = []
    for p in filtered:
        text = p.get("text", "").strip()
        norm_text = text.lower().strip()
        
        if norm_text in seen_texts:
            # Merge source_ids
            seen_texts[norm_text]["source_ids"].extend(p.get("source_ids", []))
            seen_texts[norm_text]["frequency"] = len(set(seen_texts[norm_text]["source_ids"]))
        else:
            p["frequency"] = 1
            seen_texts[norm_text] = p
            deduplicated.append(p)
    
    log.info(f"  After dedup: {len(deduplicated)} unique primitives")
    
    # Step 3: Score, tag, and enrich each primitive
    ranked = []
    for i, p in enumerate(deduplicated):
        text = p.get("text", "")
        prim_type = p.get("type", "unknown")
        
        # Compute distinctiveness
        distinctiveness = compute_distinctiveness(text, prim_type, corpus_freq)
        
        # Detect domains
        domains = detect_domains(text)
        
        # Detect pattern reversal
        is_reversal = detect_pattern_reversal(text)
        
        # Build tags
        tags = domains.copy()
        if is_reversal:
            tags.append("pattern_reversal")
        
        # Compute final score (distinctiveness * log(frequency + 1))
        import math
        freq = p.get("frequency", 1)
        score = distinctiveness * (1 + 0.1 * math.log(freq + 1))
        
        ranked.append({
            "id": f"VP-{i+1:04d}",
            "type": prim_type,
            "text": text,
            "extractable_form": p.get("extractable_form", ""),
            "context": p.get("context", ""),
            "score": round(score, 3),
            "distinctiveness": round(distinctiveness, 3),
            "frequency": freq,
            "domains": domains,
            "tags": tags,
            "source_ids": list(set(p.get("source_ids", [])))[:5],  # cap at 5
        })
    
    # Sort by score descending
    ranked.sort(key=lambda x: x["score"], reverse=True)
    
    # Filter to score >= 0.4 (remove low-distinctiveness)
    high_quality = [r for r in ranked if r["score"] >= 0.4]
    log.info(f"  High quality (score >= 0.4): {len(high_quality)} primitives")
    
    # Cap at 150 for review
    final = high_quality[:150]
    
    # Write ranked primitives
    with open(PRIMITIVES_RANKED_FILE, "w") as f:
        for item in final:
            f.write(json.dumps(item) + "\n")
    
    log.info(f"Synthesis complete: {len(final)} primitives written to {PRIMITIVES_RANKED_FILE}")
    
    return final


def cmd_synth(args):
    """Step 3: Synthesis command (local heuristics, no LLM)."""
    results = compute_synthesis()
    
    # Stats by type
    type_counts = Counter(r["type"] for r in results)
    
    print(f"\n✓ Synthesis complete (local heuristics)")
    print(f"  Total ranked primitives: {len(results)}")
    print(f"  By type:")
    for t, c in type_counts.most_common():
        print(f"    {t}: {c}")
    print(f"  Output: {PRIMITIVES_RANKED_FILE}")


# =============================================================================
# STEP 4: Human Review (Grouped by Type)
# =============================================================================

def cmd_review(args):
    """Step 4: Generate human review queue, grouped by type."""
    
    if not PRIMITIVES_RANKED_FILE.exists():
        log.error("Ranked primitives not found. Run 'synth' first.")
        sys.exit(1)
    
    # Load ranked primitives
    items = []
    with open(PRIMITIVES_RANKED_FILE) as f:
        for line in f:
            items.append(json.loads(line))
    
    # Group by type
    by_type = {}
    for item in items:
        t = item.get("type", "unknown")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(item)
    
    # Sort types by count (most first)
    sorted_types = sorted(by_type.keys(), key=lambda t: -len(by_type[t]))
    
    # Generate review markdown
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    review_file = REVIEW_DIR / f"{date_str}_linkedin-primitives_review.md"
    
    md = f"""---
created: {date_str}
last_edited: {date_str}
version: 2.0
provenance: linkedin_voice_extractor (local synthesis)
status: pending_review
---

# LinkedIn Voice Primitives Review

**Generated:** {datetime.now().isoformat()}  
**Total Candidates:** {len(items)}  
**Grouped by:** Type (with domain + pattern tags)

## Instructions

Review each primitive. Mark with:
- `[x]` — **Approve** for import to voice library  
- `[ ]` — **Reject** (not distinctive enough, too generic, etc.)  
- `[~]` — **Refine** (edit the text in place before approving)

**Tags Legend:**
- Domain tags (e.g., `career-coaching`, `hiring`) indicate topical relevance
- `pattern_reversal` = uses "not X but Y" or similar inversion structure

---

"""
    
    # Write each type section
    for prim_type in sorted_types:
        type_items = by_type[prim_type]
        md += f"""## {prim_type.replace('_', ' ').title()} ({len(type_items)})

"""
        
        for p in type_items:
            tags_str = ", ".join(p.get("tags", [])) if p.get("tags") else "—"
            domains_str = ", ".join(p.get("domains", [])) if p.get("domains") else "—"
            
            md += f"""### [ ] {p.get('id')}: {p.get('text', 'No text')}

| Field | Value |
|-------|-------|
| **Score** | {p.get('score', 0):.2f} |
| **Distinctiveness** | {p.get('distinctiveness', 0):.2f} |
| **Frequency** | {p.get('frequency', 1)}x |
| **Domains** | {domains_str} |
| **Tags** | {tags_str} |
| **Extractable Form** | {p.get('extractable_form', 'N/A')} |
| **Context** | {p.get('context', 'N/A')} |

---

"""
    
    # Summary at end
    md += f"""
## Summary by Type

| Type | Count |
|------|-------|
"""
    for t in sorted_types:
        md += f"| {t} | {len(by_type[t])} |\n"
    
    md += f"""
---

**Next Steps:**
1. Review and mark primitives with `[x]` to approve
2. Run: `python3 N5/scripts/linkedin_voice_extractor.py import --approved "{review_file}"`
"""
    
    with open(review_file, "w") as f:
        f.write(md)
    
    print(f"\n✓ Review queue generated (grouped by type)")
    print(f"  File: {review_file}")
    print(f"  Total candidates: {len(items)}")
    print(f"  Types: {', '.join(sorted_types)}")
    print(f"\nNext: Edit the file, mark approved items with [x], then run:")
    print(f"  python3 N5/scripts/linkedin_voice_extractor.py import --approved {review_file}")


# =============================================================================
# STEP 5: Import
# =============================================================================

def cmd_import(args):
    """Step 5: Import approved primitives to voice_library.db."""
    
    if not args.approved:
        log.error("Must specify --approved file")
        sys.exit(1)
    
    review_file = Path(args.approved)
    if not review_file.exists():
        log.error(f"File not found: {review_file}")
        sys.exit(1)
    
    # Parse approved primitives from markdown
    content = review_file.read_text()
    
    # Find all [x] marked items
    approved_ids = re.findall(r'\[x\]\s+(VP-\d+):', content)
    
    if not approved_ids:
        print("No approved primitives found (mark with [x])")
        return
    
    log.info(f"Found {len(approved_ids)} approved primitives")
    
    # Load full primitive data
    primitives_data = {}
    with open(PRIMITIVES_RANKED_FILE) as f:
        for line in f:
            item = json.loads(line)
            if item.get("id", "").startswith("VP-"):
                primitives_data[item["id"]] = item
    
    # Import to voice_library.db
    import sqlite3
    conn = sqlite3.connect(str(VOICE_LIBRARY_DB))
    cursor = conn.cursor()
    
    imported = 0
    for pid in approved_ids:
        if pid not in primitives_data:
            log.warning(f"Primitive {pid} not found in ranked data, skipping")
            continue
        
        p = primitives_data[pid]
        
        # Generate new ID for voice library
        cursor.execute("SELECT COUNT(*) FROM primitives")
        count = cursor.fetchone()[0]
        new_id = f"VL-LI-{count+1:04d}"
        
        cursor.execute("""
            INSERT INTO primitives (
                id, primitive_type, exact_text, pattern_template,
                source, domains_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            new_id,
            p.get("type", "unknown"),
            p.get("text", ""),
            p.get("extractable_form", ""),
            "linkedin",
            json.dumps(p.get("domains", []))
        ))
        
        imported += 1
        log.info(f"  Imported {new_id}: {p.get('text', '')[:50]}...")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Import complete")
    print(f"  Imported: {imported} primitives")
    print(f"  Database: {VOICE_LIBRARY_DB}")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Voice Primitives Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # prep
    prep_parser = subparsers.add_parser("prep", help="Step 1: Extract corpus + frequency analysis")
    prep_parser.set_defaults(func=cmd_prep)
    
    # chunk
    chunk_parser = subparsers.add_parser("chunk", help="Step 2: Semantic chunking + extraction")
    chunk_parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    chunk_parser.set_defaults(func=cmd_chunk)
    
    # synth
    synth_parser = subparsers.add_parser("synth", help="Step 3: Synthesis + ranking")
    synth_parser.set_defaults(func=cmd_synth)
    
    # review
    review_parser = subparsers.add_parser("review", help="Step 4: Generate review queue")
    review_parser.set_defaults(func=cmd_review)
    
    # import
    import_parser = subparsers.add_parser("import", help="Step 5: Import approved to voice_library.db")
    import_parser.add_argument("--approved", type=str, help="Path to reviewed markdown file")
    import_parser.set_defaults(func=cmd_import)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()






