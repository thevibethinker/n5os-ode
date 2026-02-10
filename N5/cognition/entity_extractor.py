#!/usr/bin/env python3
"""
N5 Entity Extractor — LLM-based entity and relationship extraction.

Uses /zo/ask API for extraction to leverage Zo's context.
"""

import json
import os
import hashlib
import logging
import requests
from requests import RequestException
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import time

LOG = logging.getLogger("entity_extractor")

CACHE_DIR = Path("/home/workspace/N5/cognition/entity_cache")

# Set to True to skip OpenAI entirely (e.g., when rate limited for the day)
SKIP_OPENAI = os.environ.get("SKIP_OPENAI", "").lower() in ("1", "true", "yes")

RATE_LIMIT_STATE = {
    "consecutive_failures": 0,
    "last_backoff_seconds": 0
}

@dataclass
class Entity:
    name: str
    type: str  # PERSON, CONCEPT, ORGANIZATION, BELIEF, TOOL, EVENT
    context: str = ""
    canonical_name: str = ""
    
    def __post_init__(self):
        if not self.canonical_name:
            self.canonical_name = self.name.lower().strip()

@dataclass 
class Relationship:
    from_entity: str
    to_entity: str
    relation_type: str  # BELIEVES, KNOWS, WORKS_WITH, USES, MENTIONS, RELATED_TO
    context: str = ""
    confidence: float = 1.0

EXTRACTION_PROMPT = """
# Entity Extraction Prompt

Extract entities and relationships from the following text about V (Vrijen)'s knowledge system.

## Entity Types

- PERSON — People mentioned (collaborators, contacts, friends)
- CONCEPT — Ideas, beliefs, frameworks, principles
- ORG — Companies, communities, institutions
- TOOL — Software, processes, techniques
- EVENT — Meetings, milestones, occurrences

## Relationship Types

- KNOWS, WORKS_WITH, ADVISES — Person relationships
- BELIEVES, USES, RELATED_TO — Concept/tool relationships

## Output Format

Return valid JSON with "entities" array and "relationships" array.
Each entity: name, type, context (brief).
Each relationship: from, to, type, context.

Focus on clearly named entities. Skip vague references.

TEXT TO ANALYZE:
"""


def get_cache_key(text: str) -> str:
    """Generate cache key for text."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def get_cached_extraction(text: str) -> Optional[Dict]:
    """Check if we have cached extraction for this text."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{get_cache_key(text)}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None


def cache_extraction(text: str, result: Dict):
    """Cache extraction result."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{get_cache_key(text)}.json"
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(result, f)
    except Exception as e:
        LOG.warning(f"Failed to cache extraction: {e}")


def apply_backoff():
    """Apply exponential backoff based on rate limit state."""
    failures = RATE_LIMIT_STATE["consecutive_failures"]
    failure_number = failures + 1
    backoff_seconds = 1 << min(failure_number, 6)
    LOG.info(f"Rate limit hit. Sleeping for {backoff_seconds} seconds...")
    time.sleep(backoff_seconds)
    RATE_LIMIT_STATE["consecutive_failures"] = min(failure_number, 6)
    RATE_LIMIT_STATE["last_backoff_seconds"] = backoff_seconds


def extract_entities_via_zo(text: str, use_cache: bool = True) -> Dict[str, List]:
    """
    Extract entities and relationships using /zo/ask API.
    
    Args:
        text: Text to extract from
        use_cache: Whether to use cached results
        
    Returns:
        Dict with 'entities' and 'relationships' lists
    """
    # Check cache first
    if use_cache:
        cached = get_cached_extraction(text)
        if cached:
            LOG.debug("Using cached extraction")
            return cached
    
    # Truncate text if too long
    max_text_len = 4000
    if len(text) > max_text_len:
        text = text[:max_text_len] + "..."
    
    prompt = EXTRACTION_PROMPT + text
    
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        LOG.error("ZO_CLIENT_IDENTITY_TOKEN not set, cannot extract entities")
        return {"entities": [], "relationships": []}
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={
                "input": prompt,
                "output_format": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "context": {"type": "string"}
                                },
                                "required": ["name", "type"]
                            }
                        },
                        "relationships": {
                            "type": "array", 
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from": {"type": "string"},
                                    "to": {"type": "string"},
                                    "type": {"type": "string"},
                                    "context": {"type": "string"}
                                },
                                "required": ["from", "to", "type"]
                            }
                        }
                    },
                    "required": ["entities", "relationships"]
                }
            },
            timeout=60
        )
        
        if response.status_code == 429:
            LOG.warning("Zo API rate limited (429). Response: %s", response.text)
            apply_backoff()
            return None
        
        if not response.ok:
            LOG.error("Zo API error: %s - %s", response.status_code, response.text)
            apply_backoff()
            return None
        
        try:
            result = response.json()
        except ValueError as exc:
            LOG.warning(
                "Zo response not JSON (len=%d). Preview: %s...",
                len(response.text),
                response.text[:160]
            )
            apply_backoff()
            return None
        
        output = result.get("output")
        if not isinstance(output, dict):
            LOG.warning("Zo output missing expected structure: %r", output)
            apply_backoff()
            return None
        
        entities = output.get("entities", [])
        relationships = output.get("relationships", [])
        
        # Normalize entity types
        valid_types = {"PERSON", "CONCEPT", "ORG", "BELIEF", "TOOL", "EVENT"}
        for e in entities:
            if e.get("type", "").upper() not in valid_types:
                e["type"] = "CONCEPT"  # Default
            else:
                e["type"] = e["type"].upper()
        
        # Normalize relationship types
        valid_rel_types = {"BELIEVES", "KNOWS", "WORKS_WITH", "USES", "MENTIONS", "RELATED_TO"}
        for r in relationships:
            if r.get("type", "").upper() not in valid_rel_types:
                r["type"] = "RELATED_TO"  # Default
            else:
                r["type"] = r["type"].upper()
        
        result = {"entities": entities, "relationships": relationships}
        
        # Cache the result
        if use_cache:
            cache_extraction(text, result)
        
        RATE_LIMIT_STATE["consecutive_failures"] = 0
        RATE_LIMIT_STATE["last_backoff_seconds"] = 0
        
        return result
        
    except RequestException as exc:
        LOG.error("Zo API request failed: %s", exc)
        apply_backoff()
        return None
    except Exception as e:
        LOG.error(f"Unexpected Zo extraction failure: {e}")
        apply_backoff()
        return None


def extract_entities_via_openai(text: str, use_cache: bool = True) -> Dict[str, List]:
    """
    Extract entities using direct OpenAI API call.
    Faster and more reliable than /zo/ask for batch processing.
    
    Returns:
        Dict with entities/relationships on success.
        None on rate limit or truncated response (caller falls back to /zo/ask).
        Empty dict on other errors.
    """
    if not text or len(text.strip()) < 50:
        return {"entities": [], "relationships": []}
    
    # Check cache first
    if use_cache:
        cached = get_cached_extraction(text)
        if cached:
            LOG.debug("Using cached extraction")
            return cached
    
    try:
        from openai import OpenAI, RateLimitError, APITimeoutError
        client = OpenAI()
        
        # Truncate very long text
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        prompt = f"""Extract entities and relationships from this text about V (Vrijen)'s knowledge system.

Text:
{text}

Return ONLY valid JSON:
{{
  "entities": [
    {{"name": "exact name as written", "type": "PERSON|CONCEPT|ORG|BELIEF|TOOL|EVENT", "context": "brief context"}}
  ],
  "relationships": [
    {{"from": "entity name", "to": "entity name", "type": "BELIEVES|KNOWS|WORKS_WITH|USES|MENTIONS|RELATED_TO", "context": "how related"}}
  ]
}}

Focus on: people V knows, concepts V believes in, tools V uses, organizations mentioned.
Only include entities that are clearly named or defined. Skip vague references."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=30
        )
        
        content = response.choices[0].message.content
        
        if content is None or len(content.strip()) < 20:
            LOG.warning(f"OpenAI returned truncated/empty response (len={len(content) if content else 0}), treating as rate limit")
            apply_backoff()
            return None
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            LOG.warning(f"OpenAI returned malformed JSON (len={len(content)}, preview={content[:80]!r}): {e}")
            apply_backoff()
            return None
        
        # Cache result
        if use_cache:
            cache_extraction(text, result)
        
        RATE_LIMIT_STATE["consecutive_failures"] = 0
        RATE_LIMIT_STATE["last_backoff_seconds"] = 0
        
        return result
        
    except RateLimitError as e:
        LOG.warning(f"OpenAI rate limit hit: {e}")
        apply_backoff()
        return None
    except APITimeoutError as e:
        LOG.warning(f"OpenAI timeout: {e}")
        apply_backoff()
        return None
    except Exception as e:
        error_str = str(e)
        LOG.error(f"OpenAI extraction failed: {e}")
        # Return None on rate limits so caller falls back to /zo/ask
        if "429" in error_str or "rate_limit" in error_str.lower() or "rate limit" in error_str.lower():
            apply_backoff()
            return None
        return {"entities": [], "relationships": []}


def extract_entities(text: str, use_cache: bool = True) -> tuple[List[Entity], List[Relationship]]:
    """
    Extract entities and relationships from text.
    
    Args:
        text: Text to extract from
        use_cache: Whether to use cached results
        
    Returns:
        Tuple of (entities, relationships)
    """
    if SKIP_OPENAI:
        raw = extract_entities_via_zo(text, use_cache=use_cache)
    else:
        raw = extract_entities_via_openai(text, use_cache=use_cache)
        if raw is None:  # Rate limited - fall back to /zo/ask
            LOG.info("OpenAI rate limited, falling back to /zo/ask")
            raw = extract_entities_via_zo(text, use_cache=use_cache)
        elif not raw:  # Empty result
            raw = extract_entities_via_zo(text, use_cache=use_cache)
    
    if not isinstance(raw, dict):
        raw = {"entities": [], "relationships": []}
    
    entities = [
        Entity(
            name=e.get("name", ""),
            type=e.get("type", "CONCEPT"),
            context=e.get("context", "")
        )
        for e in raw.get("entities", [])
        if e.get("name")
    ]
    
    relationships = [
        Relationship(
            from_entity=r.get("from", ""),
            to_entity=r.get("to", ""),
            relation_type=r.get("type", "RELATED_TO"),
            context=r.get("context", ""),
            confidence=r.get("confidence", 1.0)
        )
        for r in raw.get("relationships", [])
        if r.get("from") and r.get("to")
    ]
    
    return entities, relationships


# CLI for testing
if __name__ == "__main__":
    import sys
    
    test_text = sys.argv[1] if len(sys.argv) > 1 else """
    V met with David Spiegel to discuss networking capabilities in Zo. 
    David emphasized that while search and tracking can be automated, 
    the last mile of message writing needs a human in the loop.
    They discussed integrating with LinkedIn and using Careerspan for career coaching.
    """
    
    print(f"Extracting from: {test_text[:100]}...")
    entities, relationships = extract_entities(test_text, use_cache=False)
    
    print(f"\nEntities ({len(entities)}):")
    for e in entities:
        print(f"  [{e.type}] {e.name}: {e.context}")
    
    print(f"\nRelationships ({len(relationships)}):")
    for r in relationships:
        print(f"  {r.from_entity} --{r.relation_type}--> {r.to_entity}: {r.context}")


# Class wrapper for cleaner imports
class EntityExtractor:
    """Wrapper class for entity extraction functions."""
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
    
    def extract(self, text: str) -> tuple[List[Entity], List[Relationship]]:
        """Extract entities and relationships from text."""
        return extract_entities(text, use_cache=self.use_cache)
    
    @staticmethod
    def extract_batch(texts: List[str], use_cache: bool = True) -> List[Dict[str, List]]:
        """Extract from multiple texts."""
        return [extract_entities(t, use_cache=use_cache) for t in texts]
