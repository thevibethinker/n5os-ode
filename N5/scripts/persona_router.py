#!/usr/bin/env python3
"""
Persona Auto-Routing System
Analyzes user messages and routes to appropriate persona when confidence >= 80%

Usage:
    python3 persona_router.py analyze "user message here"
    python3 persona_router.py list-personas
    python3 persona_router.py test
"""

import sys
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

# Persona definitions with routing triggers
PERSONAS = {
    "operator": {
        "id": "90a7486f-46f9-41c9-a98c-21931fa5c5f6",
        "name": "Vibe Operator",
        "domains": ["execution", "file operations", "navigation", "state tracking", "workflow execution"],
        "triggers": [
            r"\b(move|copy|delete|organize|rename)\s+files?\b",
            r"\brun\s+(workflow|recipe|script)\b",
            r"\bexecute\b",
            r"\btrack\s+state\b",
            r"\bnavigat(e|ion)\b",
            r"\bbatch\s+operation\b",
        ],
        "keywords": ["execute", "run", "move", "copy", "organize", "track", "navigate", "batch"],
        "default": True
    },
    "strategist": {
        "id": "39309f92-3f9e-448e-81e2-f23eef5c873c",
        "name": "Vibe Strategist",
        "domains": ["strategy", "planning", "decision making", "options", "approaches", "frameworks"],
        "triggers": [
            r"\b(strategy|strategic|should (we|i)|decide|decision|options|approach)\b",
            r"\b(recommend|recommendation|best way|which way|what if)\b",
            r"\b(plan|roadmap|framework)\b",
            r"\b(proof-of-concept|poc|assess|feasibility)\b",  # From real data
            r"\b(deliver.*plan|concrete plan)\b",
        ],
        "keywords": [
            "strategy", "strategic", "should we", "should i", "decide",
            "decision", "options", "approach", "recommend", "best way",
            "plan", "roadmap", "framework", "choose", "tradeoffs",
            "proof-of-concept", "assess", "feasibility", "deliver", "opportunities"  # From real data
        ],
        "default": False
    },
    "researcher": {
        "id": "d0f04503-3ab4-447f-ba24-e02611993d90",
        "name": "Vibe Researcher",
        "domains": ["research", "information gathering", "scanning", "investigation", "discovery", "data collection"],
        "triggers": [
            r"\b(research|find|search|scan|investigate|explore|discover|gather|collect)\b",
            r"\b(look up|looking for)\b",
            r"\btranscripts?\b",  # Very common in real data
            r"\bmeeting.*(scan|detect|find)\b",
            r"\bsources?\b",
        ],
        "keywords": [
            "research", "find", "search", "scan", "investigate", "explore",
            "discover", "gather", "collect", "information", "data",
            "transcripts", "meeting", "items", "gdrive_ids", "fireflies",  # From real data
            "sources", "detect", "existing"
        ],
        "default": False
    },
    "teacher": {
        "id": "ec6ea742-dd28-4a73-b50b-fd2b9fb35e1d",
        "name": "Vibe Teacher",
        "domains": ["teaching", "explaining", "learning", "understanding", "concepts", "demonstrations"],
        "triggers": [
            r"\b(explain|how does|what is|why does|help me understand|walk me through)\b",
            r"\b(teach|learn|understand|clarify|demonstrate|show me|demo)\b",
            r"\b(outline.*demo|demo.*outline)\b",  # From real data
            r"\b(produce.*outline)\b",
            r"\b(capabilities|understanding)\b",  # From real data
        ],
        "keywords": [
            "explain", "how does", "what is", "understand", "learn",
            "teach", "why does", "clarify", "help understand", "walk through",
            "demo", "demonstrate", "show", "guide",
            "outline", "capabilities", "understanding", "highlights"  # From real data
        ],
        "default": False
    },
    "builder": {
        "id": "1426816f-b0d5-4f6c-ae26-71ae6f7fe4d4",
        "name": "Vibe Builder",
        "domains": ["development", "building", "coding", "implementation", "construction", "creation"],
        "triggers": [
            r"\b(build|create|implement|develop|code|script|make)\b",
            r"\b(set up|setup|install|configure|deploy)\b",
            r"\b(write.*(script|code|program))\b",
            r"\b(construct|assemble)\b",
            r"\b(create.*(json|request|file))\b",  # Very common in real data
            r"\b(scheduled task|cron job|automation)\b",  # From real data
        ],
        "keywords": [
            "build", "create", "implement", "develop", "code", "script",
            "make", "construct", "setup", "install", "configure", "deploy",
            "write code", "program", "develop",
            "jsons", "request", "scheduled", "task", "automation",  # From real data
            "compliant", "download", "convert", "register"  # From real data
        ],
        "default": False
    },
    "architect": {
        "id": "74e0a70d-398a-4337-bcab-3e5a3a9d805c",
        "name": "Vibe Architect",
        "domains": ["design", "architecture", "structure", "persona design", "system design"],
        "triggers": [
            r"\bdesign\b.*\b(persona|system|architecture|structure)\b",
            r"\bcreate\b.*\b(persona|prompt)\b",
            r"\b(architect|structure) (a |the )?system\b",
        ],
        "keywords": ["design", "architecture", "persona", "structure", "architect"],
        "default": False
    },
    "writer": {
        "id": "5cbe0dd8-9bfb-4cff-b2da-23112572a6b8",
        "name": "Vibe Writer",
        "domains": ["writing", "content creation", "documentation", "prose"],
        "triggers": [
            r"\bwrite\b.*\b(article|post|blog|document|content|email|message)\b",
            r"\bdraft (a |an )\b",
            r"\bcreate content\b",
        ],
        "keywords": ["write", "draft", "content", "article", "document", "prose"],
        "default": False
    },
    "debugger": {
        "id": "17def82c-ca82-4c03-9c98-4994e79f785a",
        "name": "Vibe Debugger",
        "domains": ["debugging", "troubleshooting", "problem solving", "error analysis"],
        "triggers": [
            r"\b(debug|troubleshoot|fix|broken|error|bug|not working|failed)\b",
            r"\bwhy (is|isn.?t|does|doesn.?t)\b.*\b(work|working)\b",
            r"\bhelp.*\b(stuck|blocked|error)\b",
        ],
        "keywords": ["debug", "fix", "error", "bug", "troubleshoot", "broken", "stuck"],
        "default": False
    }
}

@dataclass
class RoutingDecision:
    persona_key: str
    persona_name: str
    persona_id: str
    confidence: float
    reasoning: str
    should_switch: bool
    matches: List[str]

class PersonaRouter:
    def __init__(self, confidence_threshold: float = 0.80):
        self.threshold = confidence_threshold
        self.personas = PERSONAS
    
    def analyze(self, message: str) -> RoutingDecision:
        """Analyze message and determine appropriate persona"""
        message_lower = message.lower()
        
        scores = {}
        match_details = {}
        
        for key, persona in self.personas.items():
            if persona["default"]:
                continue  # Skip default persona (Operator)
            
            score = 0.0
            matches = []
            
            # Check regex triggers (high weight - INCREASED)
            for trigger in persona["triggers"]:
                if re.search(trigger, message_lower, re.IGNORECASE):
                    score += 0.5  # Increased from 0.3
                    matches.append(f"trigger: {trigger}")
            
            # Check keywords (medium weight - INCREASED)
            keyword_matches = 0
            for keyword in persona["keywords"]:
                if keyword.lower() in message_lower:
                    keyword_matches += 1
                    matches.append(f"keyword: {keyword}")
            
            if keyword_matches > 0:
                # Scale keyword contribution - INCREASED
                score += min(keyword_matches * 0.2, 0.5)  # Increased from 0.15, cap at 0.5
            
            # Domain matching (low weight - INCREASED)
            domain_matches = sum(1 for domain in persona["domains"] if domain.lower() in message_lower)
            if domain_matches > 0:
                score += min(domain_matches * 0.15, 0.3)  # Increased from 0.1
                matches.append(f"domains: {domain_matches}")
            
            # Cap at 1.0
            score = min(score, 1.0)
            
            if score > 0:
                scores[key] = score
                match_details[key] = matches
        
        # Find best match
        if not scores:
            # Default to Operator
            return RoutingDecision(
                persona_key="operator",
                persona_name="Vibe Operator",
                persona_id=self.personas["operator"]["id"],
                confidence=1.0,
                reasoning="No specialized persona match, defaulting to Operator",
                should_switch=False,
                matches=[]
            )
        
        best_key = max(scores, key=scores.get)
        best_score = scores[best_key]
        best_persona = self.personas[best_key]
        
        return RoutingDecision(
            persona_key=best_key,
            persona_name=best_persona["name"],
            persona_id=best_persona["id"],
            confidence=best_score,
            reasoning=f"Matched {len(match_details[best_key])} signals for {best_persona['name']}",
            should_switch=best_score >= self.threshold,
            matches=match_details[best_key]
        )
    
    def format_decision(self, decision: RoutingDecision) -> str:
        """Format routing decision for output"""
        output = []
        output.append(f"Persona: {decision.persona_name}")
        output.append(f"Confidence: {decision.confidence:.0%}")
        output.append(f"Should Switch: {'YES' if decision.should_switch else 'NO'}")
        output.append(f"Reasoning: {decision.reasoning}")
        
        if decision.matches:
            output.append(f"Matches ({len(decision.matches)}):")
            for match in decision.matches[:5]:  # Show first 5
                output.append(f"  - {match}")
        
        if decision.should_switch and decision.persona_id != "TBD":
            output.append(f"\nAction: set_active_persona('{decision.persona_id}')")
        elif decision.should_switch and decision.persona_id == "TBD":
            output.append(f"\nWarning: Persona {decision.persona_name} not yet created (ID=TBD)")
        
        return "\n".join(output)

def list_personas():
    """List all personas and their trigger patterns"""
    print("Available Personas:\n")
    for key, persona in PERSONAS.items():
        print(f"{persona['name']} ({key})")
        print(f"  ID: {persona['id']}")
        print(f"  Domains: {', '.join(persona['domains'])}")
        print(f"  Keywords: {', '.join(persona['keywords'][:5])}")
        print(f"  Default: {persona['default']}")
        print()

def test_router():
    """Test routing with example messages"""
    router = PersonaRouter()
    
    test_cases = [
        "Should we pivot to B2B or focus on B2C? Help me think through the tradeoffs.",
        "Research the top 10 AI coding assistants and compare their features",
        "Explain how LLMs work in simple terms",
        "Build me a task tracker with SQLite backend",
        "Move all files from Inbox to Archive",
        "Debug why my script keeps throwing connection errors",
        "Write a blog post about our new product launch",
        "Design a new persona for customer support",
        "What's the weather today?",
    ]
    
    print("Testing Persona Router\n")
    print("=" * 70)
    
    for i, message in enumerate(test_cases, 1):
        print(f"\nTest {i}: \"{message}\"")
        print("-" * 70)
        decision = router.analyze(message)
        print(router.format_decision(decision))
        print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: persona_router.py analyze \"message\"")
            sys.exit(1)
        
        message = sys.argv[2]
        router = PersonaRouter()
        decision = router.analyze(message)
        print(router.format_decision(decision))
        
        # Output JSON for programmatic use
        if "--json" in sys.argv:
            print("\nJSON Output:")
            print(json.dumps({
                "persona": decision.persona_key,
                "name": decision.persona_name,
                "id": decision.persona_id,
                "confidence": decision.confidence,
                "should_switch": decision.should_switch,
                "reasoning": decision.reasoning
            }, indent=2))
    
    elif command == "list-personas":
        list_personas()
    
    elif command == "test":
        test_router()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
