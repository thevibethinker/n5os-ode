#!/usr/bin/env python3
"""
V's X Voice Model

Core principle: SIMPLICITY and ELEGANCE over cleverness.
Say what you mean, clearly and naturally.
"""


def get_transform_prompt(neutral_insight: str, original_tweet: str = "", author: str = "") -> str:
    """Transform a neutral insight into V's voice."""
    return f"""Transform this insight into a brief, genuine reply.

TWEET: @{author or 'someone'}: {original_tweet or '(context)'}

INSIGHT: {neutral_insight}

RULES:
- Talk TO them, not AT an audience
- React, don't lecture
- One thought, simply put
- Under 200 chars preferred, 280 max

Reply:"""


def quick_ai_check(text: str) -> dict:
    """Quick heuristic check for obvious AI patterns."""
    issues = []
    
    if text.count('—') > 1:
        issues.append("multiple_em_dashes")
    
    if "isn't" in text.lower() and "it's" in text.lower():
        issues.append("balanced_pivot")
    
    abstract_terms = ["infrastructure", "leverage", "optimize", "framework", "ecosystem"]
    if sum(1 for t in abstract_terms if t in text.lower()) >= 2:
        issues.append("abstract_overload")
    
    return {
        "likely_passes": len(issues) == 0,
        "issues": issues
    }


if __name__ == "__main__":
    print(get_transform_prompt(
        neutral_insight="Headcount growth often impresses investors more than it serves customers.",
        original_tweet="Just hired our 50th employee! Scaling fast",
        author="founder"
    ))

