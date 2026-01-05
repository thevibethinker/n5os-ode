#!/usr/bin/env python3
"""
V-OS Tag Parser (LLM-Native)
----------------------------
Uses LLM interpretation to parse V-OS tags from email bodies.

No regex—just semantic understanding of the tag format.

Format:
    V-OS Tags: {Zo} [CRM] [F-7] [DONE] * {Howie} [GPT-I] *
               ↑ AI target   ↑ tags      ↑ trigger

Usage:
    from vos_tag_parser import parse_vos_tags
    result = await parse_vos_tags(email_body)
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import aiohttp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent / "config" / "vos_tags.json"
ZO_API_URL = "https://api.zo.computer/zo/ask"


@dataclass
class AITagBlock:
    """Parsed tags for a single AI system."""
    ai_system: str  # "zo" or "howie"
    tags: list = field(default_factory=list)
    triggered: bool = False


@dataclass 
class VOSParseResult:
    """Complete parse result for V-OS tags."""
    zo: Optional[AITagBlock] = None
    howie: Optional[AITagBlock] = None
    is_template: bool = False
    follow_up_days: Optional[int] = None
    raw_line: str = ""
    
    def zo_triggered(self) -> bool:
        return self.zo is not None and self.zo.triggered and not self.is_template
    
    def howie_triggered(self) -> bool:
        return self.howie is not None and self.howie.triggered and not self.is_template
    
    def get_zo_tags(self) -> list:
        if self.zo_triggered():
            return self.zo.tags
        return []
    
    def has_tag(self, tag: str, ai: str = "zo") -> bool:
        tag_upper = tag.upper().strip("[]")
        if ai == "zo" and self.zo_triggered():
            return any(t.upper().strip("[]") == tag_upper for t in self.zo.tags)
        elif ai == "howie" and self.howie_triggered():
            return any(t.upper().strip("[]") == tag_upper for t in self.howie.tags)
        return False
    
    def get_follow_up_days(self) -> Optional[int]:
        return self.follow_up_days


PARSE_PROMPT = """Parse this email text for V-OS tags. V-OS tags are a structured instruction system embedded in emails.

FORMAT RULES:
- V-OS Tags appear after email signatures, often in white/hidden text
- {{Zo}} or {{Howie}} in curly braces indicates which AI should act
- Tags in brackets like [CRM], [F-7], [DONE] are instructions
- An asterisk (*) after tags means "execute these" (triggered)
- No asterisk means template signature (ignore/don't execute)
- A "template signature" has many category groups like {{TWIN}}, {{CATG}}, {{FLUP}} with unexpanded placeholder tags

EXAMPLES:
- "V-OS Tags: {{Zo}} [CRM] [F-7] *" → Zo triggered with CRM and F-7 tags
- "V-OS Tags: {{Zo}} [CRM] * {{Howie}} [LOG] *" → Both AIs triggered
- "V-OS Tags: {{Zo}} [CRM]" → NOT triggered (no asterisk)
- "{{TWIN}} [!!][D5] {{CATG}} [LD-INV][LD-HIR]..." → Template signature, ignore

EMAIL TEXT:
---
{email_text}
---

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "found_vos_tags": true/false,
  "raw_line": "the V-OS tags line if found",
  "is_template": true/false,
  "zo": {{
    "triggered": true/false,
    "tags": ["TAG1", "TAG2"]
  }},
  "howie": {{
    "triggered": true/false, 
    "tags": ["TAG1"]
  }},
  "follow_up_days": null or integer (from F-7 style tags)
}}"""


async def parse_vos_tags_llm(email_text: str) -> VOSParseResult:
    """
    Parse V-OS tags using LLM interpretation.
    
    Args:
        email_text: Full email body text
        
    Returns:
        VOSParseResult with semantically parsed tags
    """
    result = VOSParseResult()
    
    # Quick check - if no hint of V-OS tags, skip API call
    text_lower = email_text.lower()
    if 'v-os' not in text_lower and '{zo}' not in text_lower and '{howie}' not in text_lower:
        return result
    
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        logger.warning("ZO_CLIENT_IDENTITY_TOKEN not set, falling back to simple parse")
        return _simple_parse(email_text)
    
    prompt = PARSE_PROMPT.format(email_text=email_text[:3000])  # Limit size
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                ZO_API_URL,
                headers={
                    "authorization": token,
                    "content-type": "application/json"
                },
                json={
                    "input": prompt,
                    "output_format": {
                        "type": "object",
                        "properties": {
                            "found_vos_tags": {"type": "boolean"},
                            "raw_line": {"type": "string"},
                            "is_template": {"type": "boolean"},
                            "zo": {
                                "type": "object",
                                "properties": {
                                    "triggered": {"type": "boolean"},
                                    "tags": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "howie": {
                                "type": "object", 
                                "properties": {
                                    "triggered": {"type": "boolean"},
                                    "tags": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "follow_up_days": {"type": ["integer", "null"]}
                        },
                        "required": ["found_vos_tags"]
                    }
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Zo API error: {resp.status}")
                    return _simple_parse(email_text)
                
                data = await resp.json()
                parsed = data.get("output", {})
                
                if not parsed.get("found_vos_tags"):
                    return result
                
                result.raw_line = parsed.get("raw_line", "")
                result.is_template = parsed.get("is_template", False)
                result.follow_up_days = parsed.get("follow_up_days")
                
                zo_data = parsed.get("zo", {})
                if zo_data and zo_data.get("tags"):
                    result.zo = AITagBlock(
                        ai_system="zo",
                        tags=zo_data.get("tags", []),
                        triggered=zo_data.get("triggered", False)
                    )
                
                howie_data = parsed.get("howie", {})
                if howie_data and howie_data.get("tags"):
                    result.howie = AITagBlock(
                        ai_system="howie",
                        tags=howie_data.get("tags", []),
                        triggered=howie_data.get("triggered", False)
                    )
                
                return result
                
    except asyncio.TimeoutError:
        logger.error("Zo API timeout")
        return _simple_parse(email_text)
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return _simple_parse(email_text)


def _simple_parse(email_text: str) -> VOSParseResult:
    """
    Minimal fallback parser when LLM unavailable.
    Just looks for obvious patterns, not comprehensive.
    """
    result = VOSParseResult()
    
    for line in email_text.split('\n'):
        line_lower = line.lower()
        if 'v-os' in line_lower or ('{zo}' in line_lower or '{howie}' in line_lower):
            result.raw_line = line.strip()
            
            # Template detection: multiple category markers
            template_markers = ['{twin}', '{catg}', '{flup}', '{cord}', '{acmd}']
            if sum(1 for m in template_markers if m in line_lower) >= 2:
                result.is_template = True
                return result
            
            # Zo block
            if '{zo}' in line_lower:
                # Find tags between {zo} and next { or end
                zo_start = line_lower.find('{zo}')
                zo_end = line.find('{', zo_start + 4)
                if zo_end == -1:
                    zo_end = len(line)
                zo_block = line[zo_start:zo_end]
                
                triggered = '*' in zo_block
                tags = [t.strip('[]') for t in zo_block.split('[')[1:] if ']' in t]
                tags = [t.split(']')[0] for t in tags]
                
                result.zo = AITagBlock(ai_system="zo", tags=tags, triggered=triggered)
                
                # Follow-up days
                for tag in tags:
                    if tag.upper().startswith('F') and any(c.isdigit() for c in tag):
                        digits = ''.join(c for c in tag if c.isdigit())
                        if digits:
                            result.follow_up_days = int(digits)
                            break
            
            # Howie block
            if '{howie}' in line_lower:
                howie_start = line_lower.find('{howie}')
                howie_end = line.find('{', howie_start + 7)
                if howie_end == -1:
                    howie_end = len(line)
                howie_block = line[howie_start:howie_end]
                
                triggered = '*' in howie_block
                tags = [t.strip('[]') for t in howie_block.split('[')[1:] if ']' in t]
                tags = [t.split(']')[0] for t in tags]
                
                result.howie = AITagBlock(ai_system="howie", tags=tags, triggered=triggered)
            
            break
    
    return result


# Sync wrapper for non-async contexts
def parse_vos_tags(email_text: str) -> VOSParseResult:
    """Synchronous wrapper for parse_vos_tags_llm."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context, use simple parse
            return _simple_parse(email_text)
        return loop.run_until_complete(parse_vos_tags_llm(email_text))
    except RuntimeError:
        return asyncio.run(parse_vos_tags_llm(email_text))


# CLI for testing
if __name__ == "__main__":
    import sys
    
    test_cases = [
        "V-OS Tags: {Zo} [CRM] [F-7] *",
        "V-OS Tags: {Zo} [CRM] [DONE] * {Howie} [GPT-I] *",
        "V-OS Tags: {Howie} [LOG] *",
        "V-OS Tags: {Zo} [CRM]",
        "V-OS Tags: {TWIN} [!!][D5] [D5+] [D10] {CATG} [LD-INV] [LD-HIR] [LD-COM]",
    ]
    
    if len(sys.argv) > 1:
        test_cases = [" ".join(sys.argv[1:])]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {test}")
        result = parse_vos_tags(test)
        print(f"Is Template: {result.is_template}")
        print(f"Zo Triggered: {result.zo_triggered()}")
        if result.zo:
            print(f"  Zo Tags: {result.zo.tags}")
        print(f"Howie Triggered: {result.howie_triggered()}")
        if result.howie:
            print(f"  Howie Tags: {result.howie.tags}")
        print(f"Follow-up Days: {result.get_follow_up_days()}")
        print(f"Has [CRM]: {result.has_tag('CRM')}")
        print(f"Has [DONE]: {result.has_tag('DONE')}")


