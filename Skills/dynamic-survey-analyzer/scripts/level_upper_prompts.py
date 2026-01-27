"""
Level Upper Divergent Analysis Prompts

Reusable prompt templates for counterintuitive analysis of survey data.
Designed to surface patterns that conventional statistical analysis misses.
"""

DIVERGENT_ANALYSIS_PROMPTS = {
    "contrarian": "What would a thoughtful contrarian say about these results? What obvious conclusion is likely wrong?",

    "missing_questions": "What important questions does this survey NOT ask? What dimensions of reality are being ignored?",

    "outlier_stories": "What do the outliers tell us that the averages hide? Look at extreme responses as signal, not noise.",

    "second_order": "What are the second-order implications of these findings? If this pattern continues, what happens next?",

    "segment_surprise": "Which demographic segment shows the most surprising or counterintuitive pattern? Why?",

    "correlation_hunt": "What unexpected correlations exist between seemingly unrelated questions? What non-obvious relationships emerge?",

    "taleb_antifragile": "What would Nassim Taleb say about this? Where is there fragility masquerading as strength?",

    " uncomfortable_truth": "What's the uncomfortable truth hiding in plain sight? What finding are people likely to avoid acknowledging?",

    "survey_lies": "If this survey is lying to us, how? What biases, blind spots, or design flaws would produce these patterns?",

    "cannot_answer": "What's the most interesting question this data CANNOT answer? What's just outside the frame?",

    "who_benefits": "Who benefits from the obvious interpretation? What perspective is being privileged by the default analysis?",

    "time_travel": "What would this same survey look like in 6 months if the observed patterns continue? What would change?",

    "zero_point": "What assumptions are being made that aren't actually in the data? What's being read INTO the responses?",

    "emergent_patterns": "What emergent behaviors or workflows aren't captured by the predefined question structure?",

    "paradox_detection": "Where do responses contain internal contradictions? What do these paradoxes reveal?",

    "sentiment_calibration": "Is the sentiment scale measuring what we think it is? What else could 'excited' mean in context?",

    "tool_taxonomy_critique": "Is the tool categorization actually meaningful? Are we organizing by the wrong axis?",

    "skill_vs_confidence": "How does self-assessed skill level compare to actual tool usage patterns? Who's underconfident? Overconfident?",

    "adoption_trap": "What if high tool adoption is actually a trap? When does 'trying everything' signal lack of strategy?",

    "the_missing_negative": "Why are there no negative responses? Is this selection bias, design flaw, or genuinely positive sentiment?"
}


def get_prompt(key: str) -> str:
    """Get a specific divergent analysis prompt by key."""
    return DIVERGENT_ANALYSIS_PROMPTS.get(key, "")


def get_all_prompts() -> dict:
    """Get all divergent analysis prompts."""
    return DIVERGENT_ANALYSIS_PROMPTS


def get_prompts_for_analysis(analysis_type: str) -> list[str]:
    """
    Get relevant prompts based on analysis type.

    Args:
        analysis_type: One of: 'patterns', 'assumptions', 'blind_spots', 'segments', 'all'

    Returns:
        List of prompt keys relevant to the analysis type
    """
    prompt_mapping = {
        'patterns': [
            'contrarian', 'correlation_hunt', 'paradox_detection',
            'sentiment_calibration', 'skill_vs_confidence'
        ],
        'assumptions': [
            'contrarian', 'uncomfortable_truth', 'survey_lies',
            'zero_point', 'who_benefits'
        ],
        'blind_spots': [
            'missing_questions', 'cannot_answer', 'emergent_patterns',
            'tool_taxonomy_critique', 'the_missing_negative'
        ],
        'segments': [
            'segment_surprise', 'outlier_stories', 'taleb_antifragile'
        ]
    }

    if analysis_type == 'all':
        return list(DIVERGENT_ANALYSIS_PROMPTS.keys())
    return prompt_mapping.get(analysis_type, [])


if __name__ == "__main__":
    # Demo: print all prompts
    import json
    print(json.dumps(DIVERGENT_ANALYSIS_PROMPTS, indent=2))
