#!/usr/bin/env python3
"""
Persona Auto-Routing System v2 - Enhanced Reliability
Analyzes user messages and routes to appropriate persona with improved confidence scoring

Improvements over v1:
- Increased trigger weights for more reliable detection
- Added combo bonuses for multiple signal types
- Stronger exact phrase matching
- Better handling of ambiguous cases
- More comprehensive keyword coverage

Usage:
    python3 persona_router_v2.py analyze "user message here"
    python3 persona_router_v2.py list-personas
    python3 persona_router_v2.py test
    python3 persona_router_v2.py compare  # Compare v1 vs v2
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
        "exact_phrases": [
            "run the", "execute the", "move all", "copy all", "organize files",
            "track progress", "navigate to"
        ],
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
            r"\b(proof-of-concept|poc|assess|feasibility)\b",
            r"\b(deliver.*plan|concrete plan)\b",
            r"\b(pivot|tradeoff|compare.*option)\b",
        ],
        "keywords": [
            "strategy", "strategic", "should we", "should i", "decide",
            "decision", "options", "approach", "recommend", "best way",
            "plan", "roadmap", "framework", "choose", "tradeoffs",
            "proof-of-concept", "assess", "feasibility", "deliver", "opportunities",
            "pivot", "evaluate", "alternative", "weigh"
        ],
        "exact_phrases": [
            "should we", "should i", "what if we", "help me think through",
            "which approach", "best way to", "recommend a", "strategic plan"
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
            r"\btranscripts?\b",
            r"\bmeeting.*(scan|detect|find)\b",
            r"\bsources?\b",
            r"\b(analyze|compare).*\b\d+\s+(top|best)\b",  # "analyze top 10", "compare 5 best"
        ],
        "keywords": [
            "research", "find", "search", "scan", "investigate", "explore",
            "discover", "gather", "collect", "information", "data",
            "transcripts", "meeting", "items", "gdrive_ids", "fireflies",
            "sources", "detect", "existing", "lookup", "locate", "identify"
        ],
        "exact_phrases": [
            "research the", "find all", "search for", "scan for",
            "investigate the", "look up", "looking for", "gather information"
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
            r"\b(outline.*demo|demo.*outline)\b",
            r"\b(produce.*outline)\b",
            r"\b(capabilities|understanding)\b",
            r"\b(in simple terms|eli5|for beginners)\b",
        ],
        "keywords": [
            "explain", "how does", "what is", "understand", "learn",
            "teach", "why does", "clarify", "help understand", "walk through",
            "demo", "demonstrate", "show", "guide",
            "outline", "capabilities", "understanding", "highlights",
            "simple terms", "beginner", "introduction"
        ],
        "exact_phrases": [
            "explain how", "explain why", "how does", "what is",
            "help me understand", "walk me through", "show me how",
            "in simple terms", "teach me"
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
            r"\b(create.*(json|request|file))\b",
            r"\b(scheduled task|cron job|automation)\b",
            r"\b(build me|make me|create me)\b",
        ],
        "keywords": [
            "build", "create", "implement", "develop", "code", "script",
            "make", "construct", "setup", "install", "configure", "deploy",
            "write code", "program", "develop",
            "jsons", "request", "scheduled", "task", "automation",
            "compliant", "download", "convert", "register", "backend", "tracker"
        ],
        "exact_phrases": [
            "build me", "build a", "create a", "make me", "develop a",
            "set up", "write a script", "implement a"
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
            r"\b(architect|structure)\s+(a\s+|the\s+)?system\b",
            r"\bdesign\s+a\s+new\b",
        ],
        "keywords": ["design", "architecture", "persona", "structure", "architect", "blueprint"],
        "exact_phrases": [
            "design a", "design the", "create a persona", "architecture for",
            "design a new persona"
        ],
        "default": False
    },
    "writer": {
        "id": "5cbe0dd8-9bfb-4cff-b2da-23112572a6b8",
        "name": "Vibe Writer",
        "domains": ["writing", "content creation", "documentation", "prose"],
        "triggers": [
            r"\bwrite\b.*\b(article|post|blog|document|content|email|message)\b",
            r"\bdraft\s+(a\s+|an\s+)\b",
            r"\bcreate content\b",
            r"\b(compose|author)\b.*\b(article|post|email|message)\b",
        ],
        "keywords": ["write", "draft", "content", "article", "document", "prose", 
                    "compose", "author", "blog", "post", "email"],
        "exact_phrases": [
            "write a", "write an", "draft a", "draft an", "create content",
            "compose a", "write me a"
        ],
        "default": False
    },
    "debugger": {
        "id": "17def82c-ca82-4c03-9c98-4994e79f785a",
        "name": "Vibe Debugger",
        "domains": ["debugging", "troubleshooting", "problem solving", "error analysis"],
        "triggers": [
            r"\b(debug|troubleshoot|fix|broken|error|bug|not working|failed)\b",
            r"\bwhy\s+(is|isn.?t|does|doesn.?t)\b.*\b(work|working)\b",
            r"\bhelp.*\b(stuck|blocked|error)\b",
            r"\b(issue|problem).*\b(with|in)\b",
        ],
        "keywords": ["debug", "fix", "error", "bug", "troubleshoot", "broken", "stuck",
                    "issue", "problem", "failing", "crash"],
        "exact_phrases": [
            "debug why", "fix the", "not working", "broken", "throwing errors",
            "help me fix"
        ],
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
    score_breakdown: Dict[str, float]

class PersonaRouter:
    def __init__(self, confidence_threshold: float = 0.80):
        self.threshold = confidence_threshold
        self.personas = PERSONAS
    
    def analyze(self, message: str) -> RoutingDecision:
        """Analyze message and determine appropriate persona with improved scoring"""
        message_lower = message.lower()
        
        scores = {}
        match_details = {}
        score_breakdowns = {}
        
        for key, persona in self.personas.items():
            if persona["default"]:
                continue  # Skip default persona (Operator)
            
            score = 0.0
            matches = []
            breakdown = {}
            
            # 1. Check exact phrases first (highest weight - NEW)
            exact_phrase_score = 0.0
            if "exact_phrases" in persona:
                for phrase in persona["exact_phrases"]:
                    if phrase.lower() in message_lower:
                        exact_phrase_score += 0.35  # Strong signal
                        matches.append(f"exact_phrase: '{phrase}'")
                
                if exact_phrase_score > 0:
                    exact_phrase_score = min(exact_phrase_score, 0.6)  # Cap at 0.6
                    score += exact_phrase_score
                    breakdown["exact_phrases"] = exact_phrase_score
            
            # 2. Check regex triggers (high weight - INCREASED)
            trigger_score = 0.0
            for trigger in persona["triggers"]:
                if re.search(trigger, message_lower, re.IGNORECASE):
                    trigger_score += 0.4  # Increased from 0.3 -> 0.5 in v1, now 0.4 for balance
                    matches.append(f"trigger: {trigger}")
            
            if trigger_score > 0:
                trigger_score = min(trigger_score, 0.5)  # Cap at 0.5
                score += trigger_score
                breakdown["triggers"] = trigger_score
            
            # 3. Check keywords (medium weight - INCREASED)
            keyword_matches = 0
            for keyword in persona["keywords"]:
                if keyword.lower() in message_lower:
                    keyword_matches += 1
                    if keyword_matches <= 5:  # Only show first 5
                        matches.append(f"keyword: {keyword}")
            
            if keyword_matches > 0:
                # Improved scaling: more generous at low counts
                keyword_score = min(keyword_matches * 0.15, 0.4)  # Increased from 0.2 cap to 0.4
                score += keyword_score
                breakdown["keywords"] = keyword_score
            
            # 4. Domain matching (low weight - INCREASED)
            domain_matches = sum(1 for domain in persona["domains"] if domain.lower() in message_lower)
            if domain_matches > 0:
                domain_score = min(domain_matches * 0.12, 0.25)  # Increased from 0.15 to 0.25
                score += domain_score
                breakdown["domains"] = domain_score
                matches.append(f"domains: {domain_matches}")
            
            # 5. Combo bonus (NEW) - boost if multiple signal types present
            signal_types = len([k for k, v in breakdown.items() if v > 0])
            if signal_types >= 3:
                combo_bonus = 0.15
                score += combo_bonus
                breakdown["combo_bonus"] = combo_bonus
                matches.append(f"combo_bonus: {signal_types} signal types")
            elif signal_types == 2:
                combo_bonus = 0.08
                score += combo_bonus
                breakdown["combo_bonus"] = combo_bonus
            
            # Cap at 1.0
            score = min(score, 1.0)
            
            if score > 0:
                scores[key] = score
                match_details[key] = matches
                score_breakdowns[key] = breakdown
        
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
                matches=[],
                score_breakdown={}
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
            matches=match_details[best_key],
            score_breakdown=score_breakdowns[best_key]
        )
    
    def format_decision(self, decision: RoutingDecision, verbose: bool = False) -> str:
        """Format routing decision for output"""
        output = []
        output.append(f"Persona: {decision.persona_name}")
        output.append(f"Confidence: {decision.confidence:.0%}")
        output.append(f"Should Switch: {'YES' if decision.should_switch else 'NO'}")
        output.append(f"Reasoning: {decision.reasoning}")
        
        if verbose and decision.score_breakdown:
            output.append(f"\nScore Breakdown:")
            for component, score in decision.score_breakdown.items():
                output.append(f"  {component}: +{score:.2f}")
        
        if decision.matches:
            output.append(f"\nMatches ({len(decision.matches)}):")
            for match in decision.matches[:7]:  # Show first 7
                output.append(f"  - {match}")
            if len(decision.matches) > 7:
                output.append(f"  ... and {len(decision.matches) - 7} more")
        
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
        if "exact_phrases" in persona:
            print(f"  Exact Phrases: {', '.join(persona['exact_phrases'][:3])}")
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
        # Additional edge cases
        "Draft an op-ed about AI safety",
        "Search for meeting transcripts from last week",
        "Help me understand how persona routing works",
    ]
    
    print("Testing Persona Router v2")
    print("\n" + "=" * 70)
    
    for i, message in enumerate(test_cases, 1):
        print(f"\nTest {i}: \"{message}\"")
        print("-" * 70)
        decision = router.analyze(message)
        print(router.format_decision(decision, verbose=True))
        print()

def compare_versions():
    """Compare v1 vs v2 routing decisions"""
    try:
        # Import v1
        import importlib.util
        spec = importlib.util.spec_from_file_location("v1", "/home/workspace/N5/scripts/persona_router.py")
        v1 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v1)
        
        router_v1 = v1.PersonaRouter()
        router_v2 = PersonaRouter()
        
        test_cases = [
            "Explain how LLMs work in simple terms",  # v1 fails (70%)
            "Write a blog post about our new product launch",  # v1 fails (70%)
            "Research trends in AI assistants",
            "Draft an op-ed about technology",
            "Help me understand neural networks",
        ]
        
        print("Comparing v1 vs v2 Routing\n")
        print("=" * 90)
        
        for i, message in enumerate(test_cases, 1):
            print(f"\nTest {i}: \"{message}\"")
            print("-" * 90)
            
            decision_v1 = router_v1.analyze(message)
            decision_v2 = router_v2.analyze(message)
            
            print(f"v1: {decision_v1.persona_name} @ {decision_v1.confidence:.0%} | Switch: {'YES' if decision_v1.should_switch else 'NO'}")
            print(f"v2: {decision_v2.persona_name} @ {decision_v2.confidence:.0%} | Switch: {'YES' if decision_v2.should_switch else 'NO'}")
            
            if decision_v1.persona_key == decision_v2.persona_key:
                if decision_v1.should_switch == decision_v2.should_switch:
                    print("✓ SAME - Both versions agree")
                else:
                    print(f"⚠ IMPROVED - v2 confidence {'above' if decision_v2.should_switch else 'below'} threshold")
            else:
                print(f"⚠ DIFFERENT - v1:{decision_v1.persona_name} vs v2:{decision_v2.persona_name}")
            print()
    
    except Exception as e:
        print(f"Error comparing versions: {e}")
        print("Run 'test' command instead to see v2 performance")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: persona_router_v2.py analyze \"message\"")
            sys.exit(1)
        
        message = sys.argv[2]
        router = PersonaRouter()
        decision = router.analyze(message)
        
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        print(router.format_decision(decision, verbose=verbose))
        
        # Output JSON for programmatic use
        if "--json" in sys.argv:
            print("\nJSON Output:")
            print(json.dumps({
                "persona": decision.persona_key,
                "name": decision.persona_name,
                "id": decision.persona_id,
                "confidence": decision.confidence,
                "should_switch": decision.should_switch,
                "reasoning": decision.reasoning,
                "score_breakdown": decision.score_breakdown
            }, indent=2))
    
    elif command == "list-personas":
        list_personas()
    
    elif command == "test":
        test_router()
    
    elif command == "compare":
        compare_versions()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
