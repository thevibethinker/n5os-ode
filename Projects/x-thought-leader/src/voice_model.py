#!/usr/bin/env python3
"""
V's Voice Model for X Thought Leadership Engine

This module implements the TWO-STAGE TRANSFORMATION APPROACH:
1. NEUTRAL STAGE: Generate the raw insight (what to say)
2. TRANSFORM STAGE: Apply V's voice (how to say it)

Aligns with canonical voice system at:
  N5/prefs/communication/voice-transformation-system.md
  N5/prefs/communication/platforms/x.md
"""

# =============================================================================
# STAGE 1: NEUTRAL INSIGHT GENERATION
# =============================================================================

NEUTRAL_PROMPT = '''You are generating the RAW INSIGHT for a Twitter reply.

DO NOT apply any style or voice. Write in plain, neutral English.
Focus ONLY on the intellectual contribution — what's worth saying.

**Original tweet:** @{author}: "{original_tweet}"

**Context (why V might engage):** {relevance_context}

**Your task:** What is the non-obvious angle V could contribute?

Think about:
- What reframe or inversion illuminates something hidden?
- What specific experience/evidence could V add?
- What question reveals assumptions in the original?
- What adjacent domain connection is insightful?

**Output format:**
{{
  "insight": "The core point to make, in plain English (no style)",
  "angle": "reframe|question|evidence|connection|challenge",
  "strength": 0.0-1.0  // How strong is this insight?
}}

Write the insight as if explaining to a smart friend.
No wit, no Twitter-isms, no V-voice yet. Just the raw idea.'''


# =============================================================================
# STAGE 2: VOICE TRANSFORMATION (X PLATFORM)
# =============================================================================

PLATFORM_VOICE = """
V's X voice DNA (from 381-tweet corpus analysis):

DIMENSIONS:
- Directness: 0.85 (low hedging, assertive)
- Profanity comfort: 0.65 (9.4% natural, not forced)
- Wit/wordplay: 0.80 (puns land, comedic structure)
- Contrarian edge: 0.75 (pointed disagreement performs)
- Self-deprecation: 0.60 ("my toxic trait...")

LENGTH: Punchy. 46% under 100 chars. Default SHORT.

FORMATTING:
- Em-dash (—) for pivots, asides
- *asterisk actions* for comedic distance (*checks notes*)
- Single ALL CAPS word max (FUCK, not sentences)
- Parentheticals for callbacks, nerd refs
- Single emoji max, often none
"""

TRANSFORMATION_PAIRS = """
TRANSFORMATION EXAMPLES (Neutral → V's X Voice):

1. Verbose → Punchy:
   NEUTRAL: "I really enjoy using this product for my workflows."
   V's X: "My toxic trait is not shutting the fuck up about products I love until it has subsumed all around me"

2. Hedging → Direct:
   NEUTRAL: "Your perspective seems to be missing some nuances in this area."
   V's X: "The degree to which you've missed the point is staggering. Like [vivid analogy]."

3. Corporate → Authentic:
   NEUTRAL: "Congratulations to the team on their launch."
   V's X: "Absolutely fucking chuffed to support the good folks over at @company"

4. Explaining → Showing:
   NEUTRAL: "I integrated the API quickly without reading documentation."
   V's X: "What you see: one shot. What you don't see: <1h, <10 prompts, 0 lines of code read"

5. Question as Weapon:
   NEUTRAL: "It seems inconsistent to criticize X when similar practices by others are praised."
   V's X: "So when Musk does it, it isn't DEI and it's smart, but when others do, it is DEI and it's bad?"

QUICK HEURISTICS:
- "I think..." → Delete or direct statement
- "really good" → "fucking great" or "slaps"
- "interesting" → specific praise or "resonates hard"
- 3+ sentences → Compress to 1-2, use em-dashes
"""

ANTI_PATTERNS = """
V's X ANTI-PATTERNS (NEVER USE):

ENGAGEMENT BAIT:
- "Louder for the people in the back"
- "Let that sink in"
- "Read that again"
- "THIS 👆"
- "I'll go first..."

LINKEDIN ENERGY:
- "Thrilled to announce..."
- Motivational platitudes
- Excessive emoji (🚀🔥💯)

FORCED AUTHENTICITY:
- Stacked profanity ("holy fucking shit balls")
- Fake slang ("ngl lowkey fire no cap fr fr")
- Explaining wordplay
- Humble-brag as self-deprecation

STRUCTURAL:
- Thread when tweet will do
- 3+ emoji
- 3+ hashtags
- ALL CAPS sentences
"""

TRANSFORM_PROMPT = '''You are transforming a NEUTRAL INSIGHT into V's X/Twitter voice.

**NEUTRAL INSIGHT:**
"{neutral_text}"

**V's X Voice Profile:**
{platform_voice}

**Transformation Examples:**
{transformation_pairs}

**Anti-Patterns (NEVER USE):**
{anti_patterns}

**Requirements:**
1. UNDER 280 CHARACTERS (hard limit)
2. Apply V's voice transformation — punchy, direct, witty
3. Use em-dashes, *asterisks*, parentheticals naturally
4. Profanity only if it enhances (usually optional)
5. Default SHORT — if compressible, compress

**Output:**
{{
  "transformed": "The reply in V's voice (<280 chars)",
  "technique": "Which signature pattern you used",
  "profanity_used": true/false,
  "char_count": N
}}

Transform the neutral insight. Make it sound like V actually wrote it.'''


# =============================================================================
# SIGNATURE PATTERNS (for reference)
# =============================================================================

SIGNATURE_PATTERNS = {
    "devastating_analogy": {
        "pattern": "[Observation] is staggering. Like [vivid metaphor].",
        "example": "Like your understanding couldn't hit the broadside of a barn with a bazooka at 10 paces."
    },
    "toxic_trait": {
        "pattern": "My toxic trait is [relatable obsession]",
        "example": "My toxic trait is not shutting the fuck up about products I love"
    },
    "millennial_urge": {
        "pattern": "the millennial urge to [specific behavior]",
        "example": "the millennial urge to put song lyrics on social media"
    },
    "blessed_are": {
        "pattern": "Blessed are the [group], for they shall inherit [outcome]",
        "example": "Blessed are the try-hard, type-A sons-of-bitches"
    },
    "em_dash_pivot": {
        "pattern": "[Setup] — [twist/escalation]",
        "example": "Great point — but have you considered the inverse?"
    },
    "show_dont_show": {
        "pattern": "What you see: [X]. What you don't see: [longer list]",
        "example": "What you see: one shot. What you don't see: <1h, 0 lines of code read"
    },
    "pointed_question": {
        "pattern": "Rhetorical question exposing hypocrisy",
        "example": "So when X does it, it's smart — but when Y does it, it's bad?"
    },
    "checks_notes": {
        "pattern": "*checks notes* [observation]",
        "example": "*checks notes* ...still no definition of 'woke' that isn't just 'things I don't like'"
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_neutral_prompt(author: str, original_tweet: str, relevance_context: str = None) -> str:
    """Build the Stage 1 (neutral insight) prompt."""
    return NEUTRAL_PROMPT.format(
        author=author,
        original_tweet=original_tweet,
        relevance_context=relevance_context or "No additional context"
    )


def get_transform_prompt(neutral_text: str) -> str:
    """Build the Stage 2 (voice transformation) prompt."""
    return TRANSFORM_PROMPT.format(
        neutral_text=neutral_text,
        platform_voice=PLATFORM_VOICE,
        transformation_pairs=TRANSFORMATION_PAIRS,
        anti_patterns=ANTI_PATTERNS
    )


def get_iteration_prompt(neutral_text: str, feedback: str) -> str:
    """Refine the neutral insight based on feedback before re-transforming."""
    return f'''Refine this neutral insight based on feedback:

CURRENT INSIGHT: "{neutral_text}"

FEEDBACK: {feedback}

Produce an improved neutral insight (no style, just the refined idea):
{{"refined_insight": "...", "changes_made": "..."}}'''


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=== STAGE 1: Neutral Prompt ===")
    neutral = get_neutral_prompt(
        author="someuser",
        original_tweet="Hot take: most startups fail because founders optimize for fundraising instead of customers.",
        relevance_context="Connects to V's position on founder priorities"
    )
    print(neutral[:500] + "...")
    
    print("\n=== STAGE 2: Transform Prompt ===")
    transform = get_transform_prompt(
        neutral_text="The real issue isn't fundraising vs customers — it's that fundraising success metrics (ARR growth, headcount, valuation) became proxies for actual business health. The map replaced the territory."
    )
    print(transform[:500] + "...")

