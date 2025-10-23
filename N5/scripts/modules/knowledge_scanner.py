#!/usr/bin/env python3
"""
Knowledge Scanner Module
Purpose: Light-touch scan of stable knowledge for content enrichment
Version: 1.0.0
Date: 2025-10-20
"""

import re
from pathlib import Path
from typing import Dict, List

KNOWLEDGE_ROOT = Path("/home/workspace/Knowledge")
BIO_FILE = KNOWLEDGE_ROOT / "personal-brand/bio.md"


class KnowledgeScanner:
    """Scans stable knowledge sources for enrichment details"""
    
    def __init__(self):
        self.bio_data = {}
        self.load_bio()
    
    def load_bio(self):
        """Load personal brand bio"""
        if not BIO_FILE.exists():
            return
        
        with open(BIO_FILE, 'r') as f:
            content = f.read()
        
        self.bio_data = self._parse_bio(content)
    
    def _parse_bio(self, content: str) -> Dict:
        """Extract key facts from bio markdown"""
        data = {
            "credentials": [],
            "system_stats": [],
            "examples": [],
            "differentiators": []
        }
        
        # Extract credentials
        cred_match = re.search(r'## Core Credentials(.*?)##', content, re.DOTALL)
        if cred_match:
            cred_text = cred_match.group(1)
            if "decade" in cred_text.lower():
                data["credentials"].append("decade of experience coaching founders")
            if "4 years" in cred_text:
                data["credentials"].append("4 years as entrepreneur and in tech")
            if "Careerspan" in cred_text:
                data["credentials"].append("Founder & CEO of Careerspan")
        
        # Extract system stats
        stats_match = re.search(r'## System Stats(.*?)##', content, re.DOTALL)
        if stats_match:
            stats_text = stats_match.group(1)
            # Find specific numbers
            profiles = re.search(r'(\d+)\s+stakeholder profiles', stats_text)
            if profiles:
                data["system_stats"].append(f"{profiles.group(1)} stakeholder profiles")
            
            agents = re.search(r'(\d+)\s+scheduled agents', stats_text)
            if agents:
                data["system_stats"].append(f"{agents.group(1)} autonomous agents")
            
            artifacts = re.search(r'(\d+)\s+distinct artifacts', stats_text)
            if artifacts:
                data["system_stats"].append(f"{artifacts.group(1)} artifacts per meeting")
        
        # Extract examples
        examples_match = re.search(r'## Common Examples(.*?)##', content, re.DOTALL)
        if examples_match:
            examples_text = examples_match.group(1)
            if "Reflection Pipeline" in examples_text:
                data["examples"].append("reflection_pipeline")
            if "Meeting Processing" in examples_text:
                data["examples"].append("meeting_processing")
            if "Daily Digest" in examples_text:
                data["examples"].append("daily_digest")
            if "Stakeholder CRM" in examples_text:
                data["examples"].append("stakeholder_crm")
        
        # Extract differentiators
        diff_match = re.search(r'## Key Differentiators(.*?)##', content, re.DOTALL)
        if diff_match:
            diff_text = diff_match.group(1)
            if "Files beat databases" in diff_text:
                data["differentiators"].append("files_over_databases")
            if "Context > prompts" in diff_text:
                data["differentiators"].append("context_over_prompts")
            if "your infrastructure" in diff_text.lower():
                data["differentiators"].append("owned_infrastructure")
        
        return data
    
    def get_enrichment(self, content_type: str = "social") -> Dict:
        """
        Get relevant enrichment details for content type
        
        Args:
            content_type: Type of content being enriched ("social", "email", "demo")
        
        Returns:
            Dict with enrichment suggestions
        """
        enrichment = {
            "credentials": self.bio_data.get("credentials", [])[:2],  # Max 2
            "system_stats": self.bio_data.get("system_stats", [])[:2],  # Max 2
            "examples": self.bio_data.get("examples", [])[:1],  # Max 1
            "differentiators": self.bio_data.get("differentiators", [])[:1]  # Max 1
        }
        
        return enrichment
    
    def suggest_replacements(self, draft_text: str) -> List[Dict]:
        """
        Suggest specific replacements for generic statements
        
        Args:
            draft_text: The draft content to analyze
        
        Returns:
            List of replacement suggestions
        """
        suggestions = []
        
        # Generic patterns to replace
        patterns = {
            r"I['']ve worked with (many |lots of )?founders": 
                "After a decade coaching founders",
            r"I built a system":
                f"I built N5 OS with {self.bio_data.get('system_stats', ['11 agents'])[0] if self.bio_data.get('system_stats') else '11 agents'}",
            r"We can (help|assist|support)":
                "I can typically spin up within 48 hours if schedule permits",
            r"I['']m (a |an )?entrepreneur":
                "As founder of Careerspan with 4 years in tech",
        }
        
        for pattern, replacement in patterns.items():
            matches = re.finditer(pattern, draft_text, re.IGNORECASE)
            for match in matches:
                suggestions.append({
                    "original": match.group(0),
                    "suggested": replacement,
                    "start": match.start(),
                    "end": match.end()
                })
        
        return suggestions


def scan_knowledge(content_type: str = "social") -> Dict:
    """
    Convenience function for quick knowledge scan
    
    Args:
        content_type: Type of content being enriched
    
    Returns:
        Enrichment dictionary
    """
    scanner = KnowledgeScanner()
    return scanner.get_enrichment(content_type)


if __name__ == "__main__":
    # Test the scanner
    scanner = KnowledgeScanner()
    print("=== Knowledge Scanner Test ===\n")
    
    enrichment = scanner.get_enrichment("social")
    print("Enrichment data:")
    for key, values in enrichment.items():
        print(f"\n{key}:")
        for val in values:
            print(f"  - {val}")
    
    # Test replacement suggestions
    test_draft = "I've worked with many founders and I built a system to help."
    print("\n\nReplacement suggestions for test draft:")
    suggestions = scanner.suggest_replacements(test_draft)
    for suggestion in suggestions:
        print(f"  '{suggestion['original']}' → '{suggestion['suggested']}'")
