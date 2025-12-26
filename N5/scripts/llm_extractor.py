#!/usr/bin/env python3
"""
LLM Extraction Service

Replaces hardcoded pattern matching with flexible LLM reasoning.
Uses structured JSON output for reliable parsing.

Usage:
    from llm_extractor import LLMExtractor
    
    extractor = LLMExtractor()
    resources = extractor.extract_resources(transcript, library_items)
    actions = extractor.extract_action_items(transcript)

Note: This service requires API access. When run within Zo's context
(scheduled tasks, agents), API access is automatic. For standalone testing,
set ANTHROPIC_API_KEY environment variable.
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PROMPT_DIR = Path("/home/workspace/N5/prompts/extraction")


@dataclass
class ExtractionResult:
    """Structured extraction result"""
    items: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: str = ""
    model_used: str = ""
    tokens_used: int = 0


class LLMExtractor:
    """
    Unified extraction service using LLM reasoning.
    
    Replaces brittle regex/keyword patterns with flexible LLM understanding.
    """
    
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize extractor with specified model.
        
        Args:
            model: Anthropic model to use. Defaults to Claude Sonnet.
        """
        self.model = model
        self.client = None
        self.api_available = False
        self._init_client()
        self.prompts = self._load_prompts()
    
    def _init_client(self):
        """Initialize Anthropic client with available credentials"""
        try:
            import anthropic
            
            # Try environment variable first
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.api_available = True
                logger.info("LLMExtractor initialized with ANTHROPIC_API_KEY")
                return
            
            # When running in Zo's scheduled task context, the API may be
            # available through internal routing. We'll try and handle errors gracefully.
            logger.warning(
                "ANTHROPIC_API_KEY not set. LLM extraction will be unavailable. "
                "Set the environment variable or run within Zo's context."
            )
            self.api_available = False
            
        except ImportError:
            logger.error("anthropic package not installed. Run: pip install anthropic")
            self.api_available = False
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load extraction prompts from template files"""
        prompts = {}
        if PROMPT_DIR.exists():
            for prompt_file in PROMPT_DIR.glob("*.md"):
                # Skip frontmatter, get content only
                content = prompt_file.read_text()
                # Remove YAML frontmatter if present
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()
                prompts[prompt_file.stem] = content
        return prompts
    
    def _call_llm(self, prompt: str, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Call LLM and parse JSON response.
        
        Args:
            prompt: Full prompt text
            max_tokens: Maximum response tokens
            
        Returns:
            Parsed JSON dict from response, or empty dict on error
        """
        if not self.api_available or self.client is None:
            logger.warning("LLM API not available, returning empty result")
            return {}
        
        try:
            import anthropic
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find raw JSON object
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    logger.warning("No JSON found in response, returning empty")
                    return {}
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {}
        except Exception as e:
            # Catch all API errors and log appropriately
            logger.error(f"LLM API error: {e}")
            return {}
    
    def extract_resources(
        self, 
        transcript: str, 
        library_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract resources V committed to sending.
        
        Args:
            transcript: Meeting transcript text
            library_items: List of Content Library items for matching
            
        Returns:
            Dict with 'resources' and 'unmatched_commitments' lists
        """
        if "extract_resources" not in self.prompts:
            logger.error("extract_resources prompt template not found")
            return {"resources": [], "unmatched_commitments": []}
        
        # Simplify library items for prompt (reduce tokens)
        simplified_items = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "url": item.get("url"),
                "type": item.get("item_type"),
            }
            for item in library_items
            if item.get("id")  # Skip items without ID
        ]
        
        prompt = self.prompts["extract_resources"]
        prompt = prompt.replace("{transcript}", transcript[:15000])  # Limit transcript length
        prompt = prompt.replace("{library_items}", json.dumps(simplified_items, indent=2))
        
        result = self._call_llm(prompt)
        logger.info(f"Extracted {len(result.get('resources', []))} resources")
        return result
    
    def extract_action_items(self, transcript: str) -> Dict[str, Any]:
        """
        Extract action items with owners and deadlines.
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            Dict with 'action_items', 'v_actions', 'other_actions' lists
        """
        if "extract_actions" not in self.prompts:
            logger.error("extract_actions prompt template not found")
            return {"action_items": [], "v_actions": [], "other_actions": []}
        
        prompt = self.prompts["extract_actions"]
        prompt = prompt.replace("{transcript}", transcript[:15000])
        
        result = self._call_llm(prompt)
        logger.info(f"Extracted {len(result.get('action_items', []))} action items")
        return result
    
    def extract_decisions(self, transcript: str) -> Dict[str, Any]:
        """
        Extract decisions made during the call.
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            Dict with 'decisions', 'open_questions', 'key_agreements' lists
        """
        if "extract_decisions" not in self.prompts:
            logger.error("extract_decisions prompt template not found")
            return {"decisions": [], "open_questions": [], "key_agreements": []}
        
        prompt = self.prompts["extract_decisions"]
        prompt = prompt.replace("{transcript}", transcript[:15000])
        
        result = self._call_llm(prompt)
        logger.info(f"Extracted {len(result.get('decisions', []))} decisions")
        return result
    
    def extract_topics(self, transcript: str) -> Dict[str, Any]:
        """
        Detect conversation topics dynamically.
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            Dict with 'topics', 'primary_topic', 'topic_breakdown', etc.
        """
        if "extract_topics" not in self.prompts:
            logger.error("extract_topics prompt template not found")
            return {"topics": [], "primary_topic": None}
        
        prompt = self.prompts["extract_topics"]
        prompt = prompt.replace("{transcript}", transcript[:15000])
        
        result = self._call_llm(prompt)
        logger.info(f"Extracted {len(result.get('topics', []))} topics")
        return result
    
    def extract_quotable_moments(self, transcript: str) -> Dict[str, Any]:
        """
        Find eloquent, quotable moments.
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            Dict with 'quotes', 'top_3_quotes', 'content_opportunities'
        """
        if "extract_quotes" not in self.prompts:
            logger.error("extract_quotes prompt template not found")
            return {"quotes": [], "top_3_quotes": []}
        
        prompt = self.prompts["extract_quotes"]
        prompt = prompt.replace("{transcript}", transcript[:15000])
        
        result = self._call_llm(prompt)
        logger.info(f"Extracted {len(result.get('quotes', []))} quotable moments")
        return result
    
    def extract_all(
        self, 
        transcript: str, 
        library_items: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Run all extractions and return combined results.
        
        Args:
            transcript: Meeting transcript text
            library_items: Optional Content Library items for resource matching
            
        Returns:
            Combined dict with all extraction results
        """
        results = {
            "topics": self.extract_topics(transcript),
            "actions": self.extract_action_items(transcript),
            "decisions": self.extract_decisions(transcript),
            "quotes": self.extract_quotable_moments(transcript),
        }
        
        if library_items:
            results["resources"] = self.extract_resources(transcript, library_items)
        
        return results


def main():
    """Test the extractor with sample text"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Extraction Service")
    parser.add_argument("--transcript", "-t", help="Path to transcript file")
    parser.add_argument("--type", "-T", choices=["resources", "actions", "decisions", "topics", "quotes", "all"], default="all")
    parser.add_argument("--model", "-m", default="claude-sonnet-4-20250514")
    args = parser.parse_args()
    
    extractor = LLMExtractor(model=args.model)
    
    if args.transcript:
        transcript = Path(args.transcript).read_text()
    else:
        # Sample test text
        transcript = """
        V: Great to meet you! So you're looking for a co-founder?
        
        Guest: Yes, I've been searching for a few months now.
        
        V: You should definitely check out YC's founder matching - it's been really effective for people I know.
        I'll send you the link after this call. Also, have you thought about South Park Commons?
        
        Guest: I haven't, tell me more.
        
        V: It's a great community. Let me share some info about that too. And I'll introduce you to a couple
        people in my network who might be good fits.
        
        Guest: That would be amazing!
        
        V: So action items - I'll send you the YC founder match link, the SPC info, and I'll make those intros
        by end of week. Sound good?
        
        Guest: Perfect, thank you so much!
        """
    
    if args.type == "all":
        results = extractor.extract_all(transcript)
    elif args.type == "resources":
        # Would need library items for full test
        results = extractor.extract_resources(transcript, [])
    elif args.type == "actions":
        results = extractor.extract_action_items(transcript)
    elif args.type == "decisions":
        results = extractor.extract_decisions(transcript)
    elif args.type == "topics":
        results = extractor.extract_topics(transcript)
    elif args.type == "quotes":
        results = extractor.extract_quotable_moments(transcript)
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()




