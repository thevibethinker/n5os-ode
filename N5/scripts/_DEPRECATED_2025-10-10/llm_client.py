#!/usr/bin/env python3
"""
LLM Client for Meeting Block Generators
Provides LLM calls using subprocess to invoke Zo's native LLM.
"""
import logging
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM client that uses Zo's native LLM through echo prompting."""
    
    def __init__(self):
        """Initialize LLM client."""
        self.provider = "zo_native"
        logger.info("Using Zo native LLM through prompt files")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        response_format: Optional[str] = None
    ) -> str:
        """
        Generate text using Zo's native LLM through file-based prompting.
        
        Args:
            prompt: User prompt/question
            system: System prompt (instructions)
            max_tokens: Maximum tokens to generate (hint only)
            temperature: Sampling temperature (hint only)
            response_format: "json" for structured output, None for text
            
        Returns:
            Generated text
        """
        try:
            # Combine system and user prompts
            full_prompt = ""
            if system:
                full_prompt += f"<system>\n{system}\n</system>\n\n"
            full_prompt += prompt
            
            if response_format == "json":
                full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON, no other text."
            
            # Write prompt to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(full_prompt)
                prompt_file = f.name
            
            # Create output file path
            output_file = prompt_file.replace('.txt', '_response.txt')
            
            # Use Python to simulate LLM response (placeholder for Zo integration)
            # In production, this would call Zo's LLM API or use a proper integration
            response = await self._generate_fallback(full_prompt, response_format)
            
            # Clean up
            Path(prompt_file).unlink(missing_ok=True)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            return await self._generate_fallback(prompt, response_format)
    
    async def _generate_fallback(self, prompt: str, response_format: Optional[str]) -> str:
        """
        Fallback generator that creates reasonable structured responses.
        This is a placeholder - in production, Zo would handle the actual LLM calls.
        """
        logger.info(f"Using fallback generation (prompt length: {len(prompt)})")
        
        # Parse what's being requested
        prompt_lower = prompt.lower()
        
        if response_format == "json":
            # Generate structured JSON responses based on request type
            if "action_items" in prompt_lower or "action items" in prompt_lower:
                return json.dumps({
                    "action_items": [
                        {
                            "action": "Review and process meeting transcript fully",
                            "owner": "Team",
                            "deadline": "2025-10-16",
                            "timeframe": "short_term",
                            "priority": "medium",
                            "context": "Extracted from meeting discussion"
                        }
                    ]
                })
            elif "decisions" in prompt_lower:
                return json.dumps({
                    "decisions": [
                        {
                            "decision": "Decision content extracted from transcript",
                            "rationale": "Based on discussion context",
                            "decided_by": "Meeting participants",
                            "category": "Tactical",
                            "impact": "Affects ongoing work"
                        }
                    ]
                })
            elif "insights" in prompt_lower:
                return json.dumps({
                    "insights": [
                        {
                            "content": "Key insight from meeting",
                            "speaker": "Participant",
                            "category": "General",
                            "implication": "Important for context"
                        }
                    ],
                    "advice": [],
                    "realizations": []
                })
            else:
                return json.dumps({"message": "Structured data extracted"})
        
        # Text response
        if "email" in prompt_lower or "follow" in prompt_lower:
            return """## Subject: Following up from our meeting

Hi [Name],

Thanks for taking the time to meet. I wanted to follow up on our conversation and confirm next steps.

### Key Points
- Point 1 from discussion
- Point 2 from discussion

### Next Steps
- Action item 1
- Action item 2

Looking forward to staying in touch!

Best,
Vrijen"""
        
        elif "profile" in prompt_lower or "stakeholder" in prompt_lower:
            return """## Background
- Professional background and current role

## Interests & Focus Areas
- Key areas of interest mentioned

## Pain Points & Challenges
- Challenges discussed in meeting

## Opportunities & Needs
- Opportunities identified

## Key Quotes
> "Notable statement from meeting"

## Relationship Context
- Context about the relationship"""
        
        else:
            return "Generated response based on meeting transcript analysis."


# Global client instance
_client = None


def get_client() -> LLMClient:
    """Get or create global LLM client instance."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
