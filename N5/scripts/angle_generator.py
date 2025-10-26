#!/usr/bin/env python3
"""
Multi-Angle Content Generator
Generates multiple distinct messaging angles, evaluates them, selects best.

Part of system-wide voice transformation system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Angle:
    """A messaging angle/approach"""
    name: str
    description: str
    tone: str
    emphasis: str
    structure_notes: str


@dataclass
class AngleResult:
    """Result for a single angle"""
    angle: Angle
    style_free_draft: str
    transformed_content: str
    score: float
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class MultiAngleResult:
    """Result of multi-angle generation"""
    best_angle: AngleResult
    all_angles: List[AngleResult]
    selection_reasoning: str


class AngleGenerator:
    """
    Generates and evaluates multiple messaging angles.
    
    Process:
    1. Generate 2-3 distinct angles based on content type + context
    2. Create style-free drafts for each angle
    3. Transform each draft using voice profile
    4. Evaluate all angles against criteria
    5. Select and return best
    """
    
    # Default angle templates per content type
    DEFAULT_ANGLES = {
        "email": [
            Angle(
                name="direct",
                description="Straightforward, businesslike, respectful",
                tone="professional-warm",
                emphasis="clarity and action items",
                structure_notes="Brief greeting, clear ask, specific next steps"
            ),
            Angle(
                name="collaborative",
                description="Partnership-oriented, inclusive",
                tone="warm-inviting",
                emphasis="shared goals and mutual benefit",
                structure_notes="We-focused language, open questions, joint ownership"
            ),
            Angle(
                name="urgent",
                description="Time-sensitive, action-oriented",
                tone="assertive-respectful",
                emphasis="timeline and consequences",
                structure_notes="Clear deadline, why it matters, specific request"
            ),
        ],
        "blog": [
            Angle(
                name="narrative",
                description="Story-driven, personal journey",
                tone="conversational-authentic",
                emphasis="relatability and emotional connection",
                structure_notes="Story arc, vulnerable moments, lessons learned"
            ),
            Angle(
                name="analytical",
                description="Framework-driven, systematic",
                tone="thoughtful-authoritative",
                emphasis="structure and actionable insights",
                structure_notes="Clear framework, numbered steps, practical examples"
            ),
            Angle(
                name="provocative",
                description="Challenge conventional wisdom",
                tone="bold-edgy",
                emphasis="contrarian view with evidence",
                structure_notes="Strong hook, unpopular truth, supporting arguments"
            ),
        ],
        "social": [
            Angle(
                name="vulnerable",
                description="Personal, honest, relatable",
                tone="authentic-warm",
                emphasis="shared human experience",
                structure_notes="Personal confession, emotional honesty, solidarity"
            ),
            Angle(
                name="satirical",
                description="Humorous critique, ironic observation",
                tone="witty-sharp",
                emphasis="entertainment with insight",
                structure_notes="Ironic setup, specific examples, punchline with truth"
            ),
            Angle(
                name="educational",
                description="Teaching moment, value-first",
                tone="helpful-clear",
                emphasis="practical takeaways",
                structure_notes="Problem/solution, framework, call to action"
            ),
        ],
        "doc": [
            Angle(
                name="comprehensive",
                description="Thorough, detailed, structured",
                tone="formal-precise",
                emphasis="completeness and accuracy",
                structure_notes="Sections, subsections, full context"
            ),
            Angle(
                name="executive",
                description="High-level, decision-focused",
                tone="concise-strategic",
                emphasis="key decisions and implications",
                structure_notes="Executive summary, critical points, recommendations"
            ),
        ],
        "note": [
            Angle(
                name="bullet",
                description="Quick capture, scannable",
                tone="neutral-efficient",
                emphasis="speed and clarity",
                structure_notes="Bullets, short phrases, minimal prose"
            ),
            Angle(
                name="narrative",
                description="Thinking-through-writing",
                tone="exploratory-loose",
                emphasis="thought process",
                structure_notes="Stream of thought, connections, open questions"
            ),
        ],
    }
    
    def __init__(self):
        """Initialize angle generator"""
        self.angles = self.DEFAULT_ANGLES
    
    def get_angles(
        self,
        content_type: str,
        custom_angles: Optional[List[Angle]] = None
    ) -> List[Angle]:
        """
        Get angles for content type.
        
        Args:
            content_type: Type of content
            custom_angles: Optional custom angles to use instead
            
        Returns:
            List of Angle objects
        """
        if custom_angles:
            return custom_angles
        
        return self.angles.get(content_type, self.angles["doc"])
    
    def generate_style_free_drafts(
        self,
        core_message: str,
        angles: List[Angle],
        content_type: str
    ) -> Dict[str, str]:
        """
        Generate style-free drafts for each angle.
        
        This returns the instruction template that will be executed.
        Actual generation happens at runtime.
        
        Args:
            core_message: Core content/message to convey
            angles: List of angles to explore
            content_type: Type of content
            
        Returns:
            Dict mapping angle name to generation instruction
        """
        instructions = {}
        
        for angle in angles:
            instruction = f"""# STYLE-FREE DRAFT GENERATION

**Content Type:** {content_type}
**Angle:** {angle.name}

## Angle Parameters
- Description: {angle.description}
- Tone: {angle.tone}
- Emphasis: {angle.emphasis}
- Structure: {angle.structure_notes}

## Core Message
{core_message}

## Instructions
Generate a STYLE-FREE draft that:
1. Conveys the core message using the specified angle
2. Follows the structural guidance
3. Emphasizes the key points indicated
4. Uses NEUTRAL, FACTUAL language (no voice/style yet)
5. Includes all necessary information

Output ONLY the style-free draft, no meta-commentary.
"""
            instructions[angle.name] = instruction
        
        logger.info(f"✓ Generated {len(instructions)} angle instructions for {content_type}")
        return instructions
    
    def evaluate_angle(
        self,
        angle: Angle,
        transformed_content: str,
        content_type: str,
        criteria: Optional[Dict] = None
    ) -> Tuple[float, List[str], List[str]]:
        """
        Evaluate a transformed angle against criteria.
        
        Args:
            angle: The angle used
            transformed_content: The voiced content
            content_type: Type of content
            criteria: Optional custom evaluation criteria
            
        Returns:
            (score, strengths, weaknesses)
        """
        if criteria is None:
            criteria = self._get_default_criteria(content_type)
        
        score = 0.0
        strengths = []
        weaknesses = []
        
        # Length appropriateness
        word_count = len(transformed_content.split())
        if content_type == "email":
            if 50 <= word_count <= 200:
                score += 2.0
                strengths.append(f"Good length ({word_count} words)")
            else:
                weaknesses.append(f"Length off-target ({word_count} words)")
        
        elif content_type == "social":
            if 100 <= word_count <= 300:
                score += 2.0
                strengths.append(f"Good length ({word_count} words)")
            else:
                weaknesses.append(f"Length off-target ({word_count} words)")
        
        # Structure checks
        paragraph_count = len([p for p in transformed_content.split("\n\n") if p.strip()])
        if paragraph_count >= 2:
            score += 1.0
            strengths.append("Good paragraph structure")
        
        # Tone alignment (heuristic)
        if angle.tone == "authentic-warm" and "I" in transformed_content:
            score += 1.5
            strengths.append("Personal voice maintained")
        
        if angle.tone == "formal-precise" and not any(emoji in transformed_content for emoji in ["😊", "🎉", "💡"]):
            score += 1.0
            strengths.append("Appropriate formality")
        
        # Content completeness (basic check)
        if len(transformed_content) > 50:
            score += 1.0
            strengths.append("Sufficient detail")
        else:
            weaknesses.append("Too brief")
        
        logger.info(f"Angle '{angle.name}' scored {score:.1f}/10")
        
        return score, strengths, weaknesses
    
    def _get_default_criteria(self, content_type: str) -> Dict:
        """Get default evaluation criteria for content type"""
        return {
            "length": "appropriate",
            "structure": "clear",
            "tone": "aligned",
            "completeness": "sufficient"
        }
    
    def select_best_angle(
        self,
        angle_results: List[AngleResult]
    ) -> Tuple[AngleResult, str]:
        """
        Select best angle from results.
        
        Args:
            angle_results: List of evaluated angle results
            
        Returns:
            (best_result, reasoning)
        """
        if not angle_results:
            raise ValueError("No angle results to select from")
        
        # Sort by score
        sorted_results = sorted(angle_results, key=lambda x: x.score, reverse=True)
        best = sorted_results[0]
        
        # Build reasoning
        reasoning_parts = [
            f"Selected angle: {best.angle.name}",
            f"Score: {best.score:.1f}/10",
            "",
            "Strengths:",
        ]
        reasoning_parts.extend(f"  - {s}" for s in best.strengths)
        
        if len(sorted_results) > 1:
            reasoning_parts.append("")
            reasoning_parts.append("Other angles considered:")
            for result in sorted_results[1:]:
                reasoning_parts.append(f"  - {result.angle.name} ({result.score:.1f}/10)")
        
        reasoning = "\n".join(reasoning_parts)
        
        logger.info(f"✓ Selected best angle: {best.angle.name}")
        return best, reasoning


def main():
    """Test/demo of angle generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Angle Generator")
    parser.add_argument("--type", required=True, help="Content type")
    parser.add_argument("--message", required=True, help="Core message")
    
    args = parser.parse_args()
    
    generator = AngleGenerator()
    angles = generator.get_angles(args.type)
    
    print("\n" + "="*80)
    print(f"ANGLES FOR: {args.type}")
    print("="*80)
    
    for angle in angles:
        print(f"\n{angle.name.upper()}")
        print(f"  Description: {angle.description}")
        print(f"  Tone: {angle.tone}")
        print(f"  Emphasis: {angle.emphasis}")
    
    print("\n" + "="*80)
    print("STYLE-FREE DRAFT INSTRUCTIONS")
    print("="*80)
    
    instructions = generator.generate_style_free_drafts(
        args.message, angles, args.type
    )
    
    for name, instruction in instructions.items():
        print(f"\n### {name} ###")
        print(instruction[:200] + "...")
    
    print("\n" + "="*80)
    
    return 0


if __name__ == "__main__":
    exit(main())
