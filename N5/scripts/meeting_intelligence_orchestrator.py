"""
Meeting Intelligence Orchestrator - Template Manager

⚠️  DEPRECATED: This template-based approach has been superseded by the Registry System.
⚠️  See: N5/prefs/block_type_registry.json (v1.3+) and N5/commands/meeting-process.md (v4.0.0+)
⚠️  Preserved for historical reference only.

This module served as a TEMPLATE MANAGER and DATA STRUCTURE PROVIDER ONLY.
It does NOT call LLMs or perform content extraction.

Old Purpose:
- Load appropriate templates based on stakeholder classification
- Provide data structures for block definitions
- Manage file paths and meeting directory structure
- Load essential links and registry data

The LLM extraction work is done by Zo directly when invoked via:
- command 'meeting-process' (now uses registry directly)
- Scheduled tasks
- Manual invocation

New Architecture (2025-10-12):
  Processing Request → Load Registry → Zo Analyzes → B##_BLOCKNAME.md files generated

Old Architecture (Deprecated):
  Python Script → Metadata/Templates → Zo invoked → Zo processes directly
"""

import json
import os
from datetime import datetime
from pathlib import Path

BLOCK_REGISTRY_DEFAULT = "/home/workspace/N5/prefs/block_type_registry.json"
ESSENTIAL_LINKS_DEFAULT = "/home/workspace/N5/prefs/communication/essential-links.json"
# DEPRECATED: Templates moved to Archive/block_templates_deprecated_2025-10-12
BLOCK_TEMPLATES_DIR = "/home/workspace/N5/prefs/Archive/block_templates_deprecated_2025-10-12/block_templates"
LOG_DIR = "/home/workspace/N5/logs"


class TemplateManager:
    """
    Manages templates and data structures for meeting intelligence processing.
    
    This class DOES NOT perform LLM calls or content extraction.
    It only loads templates, manages paths, and provides data structures.
    """
    
    def __init__(self, meeting_id, stakeholder_classification='external'):
        """
        Initialize the template manager.
        
        Args:
            meeting_id: Unique identifier for the meeting
            stakeholder_classification: 'internal' or 'external'
        """
        self.meeting_id = meeting_id
        self.stakeholder_classification = stakeholder_classification
        self.meeting_dir = f"/home/workspace/N5/records/meetings/{self.meeting_id}"
        self.templates = {}
        self.essential_links = {}
        self.registry = {}
        
        os.makedirs(self.meeting_dir, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
        self.log_file = os.path.join(LOG_DIR, f"template_manager_{self.meeting_id}.log")
    
    def _log(self, message: str):
        """Log messages to file for debugging."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def load_templates(self) -> dict:
        """
        Load appropriate templates based on stakeholder classification.
        
        Returns:
            dict: Mapping of template names to their content
        """
        template_dir = Path(BLOCK_TEMPLATES_DIR) / self.stakeholder_classification
        
        if not template_dir.exists():
            self._log(f"⚠️  Template directory not found: {template_dir}, falling back to external")
            template_dir = Path(BLOCK_TEMPLATES_DIR) / "external"
        
        self._log(f"📁 Loading templates from: {template_dir}")
        
        # Load all .template.md files from the appropriate directory
        for template_file in template_dir.glob("*.template.md"):
            template_name = template_file.stem.replace('.template', '')
            self.templates[template_name] = template_file.read_text()
            self._log(f"  ✓ Loaded template: {template_name}")
        
        return self.templates
    
    def load_essential_links(self, links_path=ESSENTIAL_LINKS_DEFAULT) -> dict:
        """
        Load essential links configuration.
        
        Args:
            links_path: Path to essential links JSON file
            
        Returns:
            dict: Essential links data
        """
        try:
            with open(links_path, "r") as f:
                self.essential_links = json.load(f)
            self._log(f"✓ Loaded essential links from: {links_path}")
            return self.essential_links
        except Exception as e:
            self._log(f"⚠️  Failed to load essential links: {e}")
            return {}
    
    def load_registry(self, registry_path=BLOCK_REGISTRY_DEFAULT) -> dict:
        """
        Load block type registry.
        
        Args:
            registry_path: Path to block registry JSON file
            
        Returns:
            dict: Block registry data
        """
        try:
            with open(registry_path, "r") as f:
                self.registry = json.load(f)
            self._log(f"✓ Loaded block registry from: {registry_path}")
            return self.registry
        except Exception as e:
            self._log(f"⚠️  Failed to load registry: {e}")
            return {}
    
    def get_template(self, template_name: str) -> str:
        """
        Get a specific template by name.
        
        Args:
            template_name: Name of the template (without .template.md extension)
            
        Returns:
            str: Template content or empty string if not found
        """
        return self.templates.get(template_name, "")
    
    def get_block_definition(self, block_id: str) -> dict:
        """
        Get block definition from registry.
        
        Args:
            block_id: Block ID (e.g., "B01")
            
        Returns:
            dict: Block definition or empty dict if not found
        """
        return self.registry.get("blocks", {}).get(block_id, {})
    
    def list_available_templates(self) -> list:
        """
        List all available template names.
        
        Returns:
            list: Template names
        """
        return list(self.templates.keys())
    
    def get_meeting_dir(self) -> str:
        """
        Get the meeting directory path.
        
        Returns:
            str: Absolute path to meeting directory
        """
        return self.meeting_dir
    
    def write_artifact(self, filename: str, content: str) -> str:
        """
        Write an artifact to the meeting directory.
        
        Args:
            filename: Name of the file to write
            content: Content to write
            
        Returns:
            str: Absolute path to written file
        """
        path = os.path.join(self.meeting_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        self._log(f"✓ Wrote artifact: {path}")
        return path
    
    def load_all(self):
        """
        Load all necessary data: templates, essential links, and registry.
        
        Returns:
            dict: Combined data structure
        """
        return {
            "templates": self.load_templates(),
            "essential_links": self.load_essential_links(),
            "registry": self.load_registry(),
            "meeting_dir": self.meeting_dir,
            "stakeholder_classification": self.stakeholder_classification
        }


def get_block_extraction_instructions(block_id: str) -> dict:
    """
    Get extraction instructions for a specific block.
    
    These are used by Zo when processing meetings, not by Python scripts.
    This function exists to document the extraction patterns.
    
    Args:
        block_id: Block ID (e.g., "B01")
        
    Returns:
        dict: Extraction instructions including prompt templates
    """
    extraction_guides = {
        "B01": {
            "name": "DETAILED_RECAP",
            "json_structure": {
                "outcome": "the main strategic decision or alignment reached",
                "rationale": "what was confirmed or committed to with reasoning",
                "mutual_understanding": "shared agreement or principle both parties endorsed",
                "next_step": "the critical next action item with owner"
            }
        },
        "B08": {
            "name": "RESONANCE_POINTS",
            "json_structure": {
                "moment": "specific topic/phrase that generated enthusiasm",
                "why_it_mattered": "why this resonated"
            }
        },
        "B21": {
            "name": "SALIENT_QUESTIONS",
            "json_structure": {
                "questions": [
                    {
                        "text": "the question (explicit or implicit)",
                        "why_it_matters": "strategic importance",
                        "speaker": "Me or Them",
                        "timestamp": "approximate time or 'unknown'",
                        "action_hint": "suggested next step",
                        "origin": "explicit or implicit"
                    }
                ],
                "secondary_questions": ["list of other noteworthy questions"]
            }
        },
        "B22": {
            "name": "DEBATE_TENSION_ANALYSIS",
            "json_structure": {
                "debates": [
                    {
                        "topic": "what was being debated",
                        "perspective_a_quote": "summary of first viewpoint",
                        "perspective_a_speaker": "Me or Them",
                        "perspective_b_quote": "summary of opposing viewpoint",
                        "perspective_b_speaker": "Me or Them",
                        "status": "Resolved, Stabilizing, or Ongoing",
                        "impact": "what this means for the project/relationship",
                        "resolution_owner": "who needs to resolve this"
                    }
                ]
            }
        },
        "B24": {
            "name": "PRODUCT_IDEA_EXTRACTION",
            "json_structure": {
                "ideas": [
                    {
                        "name": "product/feature name",
                        "description": "what it is",
                        "rationale": "why it matters",
                        "source_quote": "relevant quote from transcript",
                        "speaker": "Me or Them",
                        "timestamp": "approximate time or 'unknown'",
                        "confidence": "High, Medium, or Low"
                    }
                ]
            }
        },
        "B25": {
            "name": "DELIVERABLE_CONTENT_MAP",
            "json_structure": {
                "deliverables": [
                    {
                        "item": "deliverable name",
                        "promised_by": "Vrijen, Logan, or Careerspan",
                        "promised_when": "timing as stated",
                        "status": "NEED",
                        "link_or_file_id": "",
                        "send_with_email": True
                    }
                ]
            }
        },
        "B28": {
            "name": "FOUNDER_PROFILE_SUMMARY",
            "json_structure": {
                "company": "company name",
                "product": "product/service description",
                "motivation": "founder's motivation or mission",
                "funding": "funding stage",
                "challenges": "key challenges mentioned",
                "quote": "standout quote from founder"
            }
        },
        "B29": {
            "name": "KEY_QUOTES_HIGHLIGHTS",
            "json_structure": {
                "quotes": [
                    {
                        "text": "exact verbatim quote",
                        "speaker": "Me or Them",
                        "timestamp": "approximate time or 'unknown'",
                        "context_significance": "why this quote matters"
                    }
                ]
            }
        },
        "B14": {
            "name": "BLURBS_REQUESTED",
            "json_structure": {
                "blurb": "2-3 sentences describing Vrijen/Careerspan for warm intro"
            }
        },
        "B30": {
            "name": "INTRO_EMAIL_TEMPLATE",
            "json_structure": {
                "person_a": "Vrijen",
                "person_b": "person being introduced to",
                "hook": "connection topic",
                "introducee": "recipient name",
                "target": "target name",
                "why": "why this connection is relevant",
                "one_liner": "one sentence value prop",
                "bullets": "1-2 bullet points of context"
            }
        }
    }
    
    return extraction_guides.get(block_id, {})


if __name__ == "__main__":
    # Example usage for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Template Manager for Meeting Intelligence")
    parser.add_argument("--meeting-id", required=True, help="Meeting ID")
    parser.add_argument("--classification", default="external", 
                       choices=["internal", "external"], 
                       help="Stakeholder classification")
    
    args = parser.parse_args()
    
    manager = TemplateManager(args.meeting_id, args.classification)
    data = manager.load_all()
    
    print(f"\n✓ Loaded {len(data['templates'])} templates")
    print(f"✓ Loaded {len(data['registry'].get('blocks', {}))} block definitions")
    print(f"✓ Meeting directory: {data['meeting_dir']}")
    print(f"\nAvailable templates:")
    for template_name in manager.list_available_templates():
        print(f"  - {template_name}")
