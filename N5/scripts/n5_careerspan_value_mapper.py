#!/usr/bin/env python3
"""
Careerspan Value Mapping Module
Maps stakeholder goals to specific Careerspan capabilities and generates value propositions.

Author: N5 OS
Version: 1.0.0
Date: 2025-10-14
"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Careerspan Capabilities Database
CAREERSPAN_CAPABILITIES = {
    "career_services": {
        "personas": ["career_services_director", "university_administrator", "student_affairs"],
        "pain_points": [
            "Limited staff capacity for 1:1 coaching",
            "Difficulty tracking student outcomes",
            "Need for scalable career support",
            "Budget constraints for career services",
            "Alumni engagement and mentorship gaps"
        ],
        "careerspan_solutions": [
            "AI-powered career coaching at scale (24/7 availability)",
            "Automated resume review and optimization",
            "Job search strategy personalization",
            "Interview prep and practice tools",
            "Alumni network matching and warm intros",
            "Career outcomes tracking and analytics",
            "White-label platform for institutional branding"
        ],
        "value_props": [
            "Extend reach: Support 10x more students with same staff",
            "Improve outcomes: Data-driven career guidance increases placement rates",
            "Reduce cost: $X per student vs traditional 1:1 coaching",
            "Enhance reputation: Better career outcomes = stronger recruitment"
        ]
    },
    
    "students_job_seekers": {
        "personas": ["mba_student", "undergraduate", "career_changer", "job_seeker"],
        "pain_points": [
            "Unclear career direction",
            "Resume doesn't get responses",
            "Don't know how to network effectively",
            "Interview anxiety and lack of preparation",
            "Overwhelmed by job search process",
            "Limited access to mentors in target industry"
        ],
        "careerspan_solutions": [
            "Personalized career path recommendations",
            "AI resume optimization (ATS-friendly)",
            "Networking strategy and script templates",
            "Mock interview practice with feedback",
            "Job search workflow automation",
            "Alumni mentor matching",
            "Company research and interview prep"
        ],
        "value_props": [
            "Land your target role faster with AI-powered guidance",
            "Get expert feedback without expensive coaches",
            "Build confidence through structured practice",
            "Access insider knowledge from alumni in your field"
        ]
    },
    
    "employers": {
        "personas": ["recruiter", "hr_director", "talent_acquisition", "hiring_manager"],
        "pain_points": [
            "High volume of unqualified candidates",
            "Difficulty assessing soft skills at scale",
            "Candidate drop-off during application process",
            "DEI recruitment goals not being met",
            "Campus recruitment ROI unclear",
            "New hire retention issues"
        ],
        "careerspan_solutions": [
            "Pre-screened candidate pipeline from partner universities",
            "Skills assessment and validation tools",
            "Video interview analysis for soft skills",
            "Diversity recruiting analytics and tools",
            "Campus recruiting program management",
            "Early talent onboarding support"
        ],
        "value_props": [
            "Reduce time-to-hire with pre-qualified candidates",
            "Improve quality-of-hire through better assessment",
            "Meet DEI goals with targeted university partnerships",
            "Lower cost-per-hire vs traditional campus recruiting"
        ]
    },
    
    "investors": {
        "personas": ["vc_investor", "angel_investor", "ed_tech_investor"],
        "pain_points": [
            "Market size and growth potential unclear",
            "Business model scalability questions",
            "Competitive differentiation concerns",
            "Unit economics and path to profitability",
            "Customer acquisition cost validation",
            "Team execution capability"
        ],
        "careerspan_solutions": [
            "Access to traction metrics and growth data",
            "Customer case studies and testimonials",
            "Market research and competitive analysis",
            "Financial model and projections",
            "Product roadmap and technical architecture",
            "Team background and domain expertise"
        ],
        "value_props": [
            "Large TAM: $XX billion career services market",
            "Proven model: XX% MoM growth with strong unit economics",
            "Network effects: Platform grows more valuable with scale",
            "Strategic positioning: First-mover in AI-powered career coaching for universities"
        ]
    },
    
    "partners": {
        "personas": ["ed_tech_company", "career_platform", "university_system", "professional_association"],
        "pain_points": [
            "Limited career services offering",
            "Need to expand product portfolio",
            "Customer churn due to incomplete solutions",
            "Competition from full-stack platforms",
            "Integration and technical complexity"
        ],
        "careerspan_solutions": [
            "White-label career coaching platform",
            "API integration with existing systems",
            "Co-branded partnership opportunities",
            "Revenue share models",
            "Joint go-to-market strategies",
            "Complementary product bundling"
        ],
        "value_props": [
            "Expand offering without building from scratch",
            "Increase customer LTV through bundled services",
            "Reduce churn with more comprehensive solution",
            "Faster time-to-market vs in-house development"
        ]
    }
}


class CareerSpanValueMapper:
    """Maps stakeholder goals to Careerspan value propositions."""
    
    def __init__(self):
        self.capabilities = CAREERSPAN_CAPABILITIES
    
    def identify_persona(self, profile_data: Dict) -> str:
        """
        Identify stakeholder persona from profile data.
        
        Args:
            profile_data: Dict with keys: role, organization, goals, background
        
        Returns:
            Persona key (e.g., "career_services", "students_job_seekers")
        """
        role = profile_data.get('current_role', '').lower()
        org = profile_data.get('organization', '').lower()
        
        # Career services detection
        if any(term in role for term in ['career services', 'career development', 'student affairs', 'career center']):
            return "career_services"
        
        # Student/job seeker detection
        if any(term in role for term in ['student', 'mba', 'candidate', 'seeking']):
            return "students_job_seekers"
        
        # Employer detection
        if any(term in role for term in ['recruiter', 'talent acquisition', 'hr', 'hiring']):
            return "employers"
        
        # Investor detection
        if any(term in role for term in ['investor', 'venture', 'capital', 'vc', 'angel']):
            return "investors"
        
        # Partner detection
        if any(term in org for term in ['university', 'college', 'education', 'tech', 'platform']):
            return "partners"
        
        # Default fallback
        return "partners"
    
    def extract_goals_from_context(self, profile_data: Dict, linkedin_posts: List[Dict], emails: List[Dict]) -> List[str]:
        """
        Extract stakeholder goals from multiple intelligence sources.
        
        Args:
            profile_data: CRM profile data
            linkedin_posts: Recent LinkedIn posts
            emails: Recent email interactions
        
        Returns:
            List of inferred goals
        """
        goals = []
        
        # From profile
        if profile_data.get('goals'):
            goals.extend(profile_data['goals'])
        
        # From LinkedIn posts - look for themes
        for post in linkedin_posts:
            content = post.get('content', '').lower()
            themes = post.get('themes', [])
            
            # Detect goals from themes and content
            if 'hiring' in themes or 'hiring' in content:
                goals.append("Expand team / fill open positions")
            if 'growth' in themes or 'scaling' in content:
                goals.append("Scale operations and grow business")
            if 'student' in content or 'career services' in content:
                goals.append("Improve student career outcomes")
            if 'partnership' in themes or 'collaboration' in content:
                goals.append("Explore strategic partnerships")
        
        # From emails - look for asks or mentions
        for email in emails:
            subject = email.get('subject', '').lower()
            
            if 'demo' in subject or 'meeting' in subject:
                goals.append("Evaluate potential solutions")
            if 'follow up' in subject:
                goals.append("Continue exploration from previous conversation")
        
        # Deduplicate
        return list(set(goals))
    
    def map_value_propositions(self, persona: str, goals: List[str]) -> List[Dict]:
        """
        Map stakeholder goals to specific Careerspan value propositions.
        
        Args:
            persona: Identified persona type
            goals: List of stakeholder goals
        
        Returns:
            List of value proposition dicts with: goal, solution, value, action
        """
        if persona not in self.capabilities:
            return []
        
        persona_data = self.capabilities[persona]
        value_props = []
        
        # For each goal, find relevant Careerspan solution
        for goal in goals:
            goal_lower = goal.lower()
            
            # Match goal to pain points
            relevant_solutions = []
            for i, pain_point in enumerate(persona_data['pain_points']):
                # Simple keyword matching (could be enhanced with embeddings)
                pain_lower = pain_point.lower()
                
                # Check if goal relates to this pain point
                common_words = set(goal_lower.split()) & set(pain_lower.split())
                if len(common_words) >= 2 or any(word in pain_lower for word in goal_lower.split() if len(word) > 4):
                    # This pain point is relevant
                    if i < len(persona_data['careerspan_solutions']):
                        relevant_solutions.append({
                            'pain': pain_point,
                            'solution': persona_data['careerspan_solutions'][i]
                        })
            
            # If we found relevant solutions, create value prop
            if relevant_solutions:
                value_props.append({
                    'goal': goal,
                    'solutions': [s['solution'] for s in relevant_solutions[:2]],  # Top 2
                    'value': persona_data['value_props'][0] if persona_data['value_props'] else "Careerspan can help achieve this goal",
                    'action': self._suggest_action(persona, goal)
                })
        
        # If no goals matched, provide general value props for persona
        if not value_props:
            value_props.append({
                'goal': "General exploration",
                'solutions': persona_data['careerspan_solutions'][:2],
                'value': persona_data['value_props'][0],
                'action': "Explore how Careerspan can help"
            })
        
        return value_props
    
    def _suggest_action(self, persona: str, goal: str) -> str:
        """Suggest specific action based on persona and goal."""
        if persona == "career_services":
            return "Offer pilot program or demo"
        elif persona == "students_job_seekers":
            return "Provide free trial or coaching session"
        elif persona == "employers":
            return "Share candidate pipeline preview"
        elif persona == "investors":
            return "Share deck and traction metrics"
        elif persona == "partners":
            return "Discuss integration or partnership models"
        else:
            return "Explore specific use cases"
    
    def generate_possibilities(self, profile_data: Dict, linkedin_intel: Dict, email_intel: List[Dict]) -> Dict:
        """
        Main entry point: Generate 'What's Possible' section for digest.
        
        Args:
            profile_data: CRM profile
            linkedin_intel: Dict with posts, goals, themes
            email_intel: Recent email interactions
        
        Returns:
            Dict with: persona, goals, value_props, strategic_moves
        """
        # Identify persona
        persona = self.identify_persona(profile_data)
        
        # Extract goals
        linkedin_posts = linkedin_intel.get('posts', [])
        goals = self.extract_goals_from_context(profile_data, linkedin_posts, email_intel)
        
        # Map to value propositions
        value_props = self.map_value_propositions(persona, goals)
        
        # Generate strategic moves
        strategic_moves = self._generate_strategic_moves(persona, goals, value_props)
        
        return {
            'persona': persona,
            'goals': goals,
            'value_propositions': value_props,
            'strategic_moves': strategic_moves
        }
    
    def _generate_strategic_moves(self, persona: str, goals: List[str], value_props: List[Dict]) -> List[str]:
        """Generate 2-3 concrete strategic moves for the meeting."""
        moves = []
        
        # Always lead with curiosity
        moves.append(f"Ask about their current approach to: {goals[0] if goals else 'solving this problem'}")
        
        # Offer specific value
        if value_props:
            first_vp = value_props[0]
            moves.append(f"Share how Careerspan addresses: {first_vp['solutions'][0] if first_vp['solutions'] else 'this challenge'}")
        
        # Suggest next step
        if value_props and value_props[0].get('action'):
            moves.append(first_vp['action'])
        else:
            moves.append("Explore specific pain points and potential fit")
        
        return moves[:3]  # Max 3 moves


def main():
    """Test the value mapper with sample data."""
    mapper = CareerSpanValueMapper()
    
    # Test case: Career services director
    profile = {
        'current_role': 'Director of Career Services',
        'organization': 'Cornell University',
        'goals': ['Support more students with limited staff']
    }
    
    linkedin = {
        'posts': [
            {'content': 'Excited about scaling our career services!', 'themes': ['growth', 'career services']},
            {'content': 'Looking for innovative solutions', 'themes': ['partnership']}
        ]
    }
    
    emails = [
        {'subject': 'Follow up on our conversation'},
        {'subject': 'Demo request'}
    ]
    
    result = mapper.generate_possibilities(profile, linkedin, emails)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
