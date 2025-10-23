#!/usr/bin/env python3
"""
Angle Analyzer Module
Purpose: Identify distinct narrative angles from source content
Version: 1.0.0
Date: 2025-10-20
"""

import re
from typing import List, Dict


class AngleAnalyzer:
    """Identifies potential narrative angles from source material"""
    
    # Predefined angle templates
    ANGLE_TEMPLATES = {
        "founder_pain": {
            "name": "Founder Pain Point",
            "description": "Lead with problem/frustration, show solution",
            "keywords": ["problem", "frustrated", "drowning", "scattered", "manual", "tedious"],
            "structure": "Pain → Solution → Proof → CTA"
        },
        "technical_differentiation": {
            "name": "Technical Differentiation",
            "description": "Contrarian technical take, architecture decision",
            "keywords": ["architecture", "database", "files", "system", "design", "technical"],
            "structure": "Contrarian claim → Reasoning → Benefits → CTA"
        },
        "build_story": {
            "name": "Build Story",
            "description": "Personal journey from problem to building solution",
            "keywords": ["built", "gave up", "learned", "journey", "decided"],
            "structure": "What I tried → Why it failed → What I built → Offer"
        },
        "roi_outcome": {
            "name": "ROI/Outcome",
            "description": "Concrete results, time/money saved",
            "keywords": ["saved", "hours", "automated", "eliminated", "reduced"],
            "structure": "Before state → After state → How → Offer"
        },
        "insight_shift": {
            "name": "Insight/Mental Shift",
            "description": "Reframe how audience thinks about problem",
            "keywords": ["insight", "realized", "shift", "actually", "real problem"],
            "structure": "Common belief → Counter-insight → Why it matters → CTA"
        }
    }
    
    def __init__(self):
        pass
    
    def identify_angles(self, source_text: str, objective: str = "demo_booking") -> List[Dict]:
        """
        Identify potential angles from source text
        
        Args:
            source_text: The reflection or source content
            objective: The goal (demo_booking, brand_awareness, etc.)
        
        Returns:
            List of identified angles with scores
        """
        angles = []
        
        for angle_key, angle_data in self.ANGLE_TEMPLATES.items():
            score = self._score_angle(source_text, angle_data["keywords"])
            if score > 0:
                angles.append({
                    "key": angle_key,
                    "name": angle_data["name"],
                    "description": angle_data["description"],
                    "structure": angle_data["structure"],
                    "score": score,
                    "fit": "high" if score >= 3 else "medium" if score >= 2 else "low"
                })
        
        # Sort by score
        angles.sort(key=lambda x: x["score"], reverse=True)
        
        return angles
    
    def _score_angle(self, text: str, keywords: List[str]) -> int:
        """Score how well an angle fits the source text"""
        text_lower = text.lower()
        score = sum(1 for keyword in keywords if keyword in text_lower)
        return score
    
    def suggest_hooks(self, angle_key: str, source_text: str) -> List[str]:
        """
        Suggest opening hooks for a given angle
        
        Args:
            angle_key: The angle identifier
            source_text: Source content
        
        Returns:
            List of suggested hooks
        """
        hooks = {
            "founder_pain": [
                "Most founders I talk to are drowning in tools.",
                "I gave up fighting my productivity stack.",
                "Your best insights are scattered across 8 tools."
            ],
            "technical_differentiation": [
                "I built my productivity system on files, not databases.",
                "Everyone's racing toward vector stores. I went the opposite direction.",
                "The best personal AI architecture? Plain text files."
            ],
            "build_story": [
                "I gave up on Notion AI.",
                "After trying every productivity tool, I built my own.",
                "I stopped asking AI to remember and gave it my files instead."
            ],
            "roi_outcome": [
                "I automated 8 hours of manual work per week.",
                "My AI processes 77 stakeholder profiles while I sleep.",
                "One reflection becomes 26 artifacts in under 5 minutes."
            ],
            "insight_shift": [
                "The problem isn't bad AI. It's missing context.",
                "You don't need better prompts. You need better files.",
                "Personal AI isn't about smarter models—it's about your data."
            ]
        }
        
        return hooks.get(angle_key, [])
    
    def get_cta_for_angle(self, angle_key: str, objective: str) -> str:
        """Get appropriate CTA for angle + objective combination"""
        if objective == "demo_booking":
            ctas = {
                "founder_pain": "DM me if you want to see how this works. Usually spin up within 48 hours if schedule permits.",
                "technical_differentiation": "DM me if you want to see the architecture. Happy to walk through the design.",
                "build_story": "DM me if you want to see the build. I'm offering custom setups now.",
                "roi_outcome": "DM me for a walkthrough. Usually spin up within 48 hours if schedule permits.",
                "insight_shift": "DM me if you want to explore this for your workflow."
            }
            return ctas.get(angle_key, "DM me to discuss.")
        
        return "Let me know your thoughts."


def analyze_angles(source_text: str, objective: str = "demo_booking") -> List[Dict]:
    """
    Convenience function for angle analysis
    
    Args:
        source_text: Source content
        objective: Content objective
    
    Returns:
        List of angle suggestions
    """
    analyzer = AngleAnalyzer()
    return analyzer.identify_angles(source_text, objective)


if __name__ == "__main__":
    # Test the analyzer
    test_text = """
    I'm trying to figure out my strategy for deploying Zo. 
    I can set up a demonstrator account with productivity features.
    The system processes reflections, meetings, has a CRM built on files.
    I learned from building Careerspan and setting up the Zo system.
    I want to show how reflection processing works automatically.
    """
    
    print("=== Angle Analyzer Test ===\n")
    
    analyzer = AngleAnalyzer()
    angles = analyzer.identify_angles(test_text, "demo_booking")
    
    print("Identified angles:\n")
    for angle in angles:
        print(f"✓ {angle['name']} (score: {angle['score']}, fit: {angle['fit']})")
        print(f"  Structure: {angle['structure']}")
        print(f"  Hooks: {analyzer.suggest_hooks(angle['key'], test_text)[0]}")
        print(f"  CTA: {analyzer.get_cta_for_angle(angle['key'], 'demo_booking')}\n")
