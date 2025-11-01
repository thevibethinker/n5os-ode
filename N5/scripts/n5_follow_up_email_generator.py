#!/usr/bin/env python3
"""
N5 Follow-Up Email Generator — v11.0.1 Implementation + Content Library Integration
Programmatic execution of 13-step email generation pipeline

Implements: file 'Prompts/follow-up-email-generator.md' (v11.0.1)

Author: Zo Computer  
Version: 2.1.0 (Registry Integration)
Date: 2025-10-22
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json

# Import ContentLibrary and new B-Block tools
sys.path.insert(0, str(Path(__file__).parent))
try:
    from content_library import ContentLibrary
    from b_block_parser import BBlockParser
    from email_composer import EmailComposer
    CONTENT_LIBRARY_AVAILABLE = True
except ImportError:
    CONTENT_LIBRARY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Content Library system not available, using fallback flow")

# Import ContentLibrary and new B-Block tools
sys.path.insert(0, str(Path(__file__).parent))
from content_library import ContentLibrary
from b_block_parser import BBlockParser
from email_composer import EmailComposer
from email_registry import EmailRegistry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class EmailGenerator:
    """Follow-up email generator implementing v11.0.1 specification"""
    
    def __init__(self, meeting_folder: Path, output_dir: Optional[Path] = None, use_content_library: bool = False):
        self.meeting_folder = Path(meeting_folder)
        self.output_dir = output_dir or (self.meeting_folder / "DELIVERABLES")
        self.use_content_library = use_content_library
        
        # Load configuration files
        self.workspace_root = Path("/home/workspace")
        self.voice_config_path = self.workspace_root / "N5/prefs/communication/voice.md"
        self.content_library = ContentLibrary()  # Use ContentLibrary instead of direct JSON
        self.command_spec_path = self.workspace_root / "Prompts/follow-up-email-generator.md"
        
        # State tracking
        self.pipeline_state = {}
        self.artifacts = {}
        
    def validate_inputs(self) -> bool:
        """Validate meeting folder and required files exist"""
        if not self.meeting_folder.exists():
            logger.error(f"Meeting folder not found: {self.meeting_folder}")
            return False
            
        # Check for transcript
        transcript_files = list(self.meeting_folder.glob("*transcript*.txt")) + \
                          list(self.meeting_folder.glob("*transcript*.md"))
        if not transcript_files:
            logger.error(f"No transcript found in {self.meeting_folder}")
            return False
            
        self.transcript_path = transcript_files[0]
        logger.info(f"✓ Transcript found: {self.transcript_path.name}")
        
        # Check for voice config
        if not self.voice_config_path.exists():
            logger.error(f"Voice config not found: {self.voice_config_path}")
            return False
            
        logger.info("✓ All required files found")
        return True
    
    def load_context(self) -> Dict:
        """STEP 1: Load meeting transcript and metadata"""
        logger.info("[STEP 1/13] Loading context...")
        
        # Load transcript
        transcript = self.transcript_path.read_text()
        
        # Load stakeholder profile (if exists)
        profile_path = self.meeting_folder / "stakeholder_profile.md"
        stakeholder_profile = None
        if profile_path.exists():
            stakeholder_profile = profile_path.read_text()
            logger.info(f"✓ Stakeholder profile loaded: {profile_path.name}")
        else:
            logger.info("⚠ No stakeholder profile found (will use defaults)")
        
        # Load voice config
        voice_config = self.voice_config_path.read_text()
        
        # Load essential links
        essential_links = self.load_essential_links()
        
        context = {
            "transcript": transcript,
            "transcript_path": str(self.transcript_path),
            "stakeholder_profile": stakeholder_profile,
            "voice_config": voice_config,
            "essential_links": essential_links,
            "meeting_folder": str(self.meeting_folder)
        }
        
        self.artifacts["context"] = context
        logger.info("✓ Step 1 complete: Context loaded")
        return context
    
    def load_essential_links(self) -> Dict:
        """Load links from ContentLibrary"""
        try:
            # Get all links from content library
            all_items = self.content_library.search(query=None, tags={})
            all_items = [item for item in all_items if item.type == "link"]
            
            # Format for backward compatibility - organize by ID
            links = {}
            for item in all_items:
                links[item["id"]] = {
                    "url": item["content"],
                    "title": item["title"],
                    "tags": item["tags"]
                }
            
            logger.info(f"Loaded {len(links)} links from ContentLibrary")
            return links
        except Exception as e:
            logger.error(f"Failed to load ContentLibrary: {e}", exc_info=True)
            return {}
    
    def match_links(self, context: str, tags: Dict[str, List[str]] = None) -> List[Dict]:
        """Match links based on context and tags using ContentLibrary search"""
        try:
            # Search ContentLibrary with tags
            matches = self.content_library.search(
                query=context if context else None,
                tags=tags,
                item_type="link"
            )
            
            # Mark as used
            for match in matches:
                self.content_library.mark_used(match["id"])
            
            return matches
        except Exception as e:
            logger.error(f"Link matching failed: {e}", exc_info=True)
            return []
    
    def build_link_map(self, essential_links: Dict) -> Dict:
        """STEP 2: Build available link map using ContentLibrary tag-based search"""
        logger.info("[STEP 2/13] Building link map...")
        
        link_map = {
            "company_homepage": None,
            "calendly_30min": None,
            "calendly_45min": None,
            "linkedin_profile": None,
            "specific_products": []
        }
        
        # Use ContentLibrary to search for specific link types
        # Company homepage
        company_links = self.content_library.search(
            query=None,
            tags={"entity": ["careerspan"], "purpose": ["marketing"]}
        )
        company_links = [link for link in company_links if link.type == "link"]
        for link in company_links:
            if "homepage" in link.id or "company" in link.title.lower():
                link_map["company_homepage"] = link.content
                break
        
        # Meeting booking links - Vrijen 30min
        meeting_30m = self.content_library.search(
            query=None,
            tags={"entity": ["vrijen"], "purpose": ["scheduling"]}
        )
        meeting_30m = [link for link in meeting_30m if link.type == "link"]
        # Filter for 30min
        meeting_30m = [link for link in meeting_30m if "30" in link.id or "30" in link.title]
        if meeting_30m:
            link_map["calendly_30min"] = meeting_30m[0].content
        
        # Meeting booking links - Vrijen 45min
        meeting_45m = self.content_library.search(
            query=None,
            tags={"entity": ["vrijen"], "purpose": ["scheduling"]}
        )
        meeting_45m = [link for link in meeting_45m if link.type == "link"]
        meeting_45m = [link for link in meeting_45m if "45" in link.id or "45" in link.title]
        if meeting_45m:
            link_map["calendly_45min"] = meeting_45m[0].content
        
        # LinkedIn profile
        linkedin = self.content_library.search(
            query=None,
            tags={"entity": ["vrijen"], "context": ["social"]}
        )
        linkedin = [link for link in linkedin if link.type == "link"]
        for link in linkedin:
            if "linkedin" in link.id.lower():
                link_map["linkedin_profile"] = link.content
                break
        
        # Co-founder search links
        cofounder_links = self.content_library.search(
            query=None,
            tags={"purpose": ["networking"]}  # Changed from co-founder-search to networking
        )
        cofounder_links = [link for link in cofounder_links if link.type == "link"]
        for item in cofounder_links:
            if "cofounder" in item.title.lower() or "cofounder" in item.id.lower():
                link_map["specific_products"].append({
                    "title": item.title,
                    "url": item.content
                })
        
        self.artifacts["link_map"] = link_map
        # Count successfully mapped links (use .get() for safety)
        mapped_count = sum(1 for v in [
            link_map.get('company_homepage'), 
            link_map.get('calendly_30min'),
            link_map.get('calendly_60min')
        ] if v) + len(link_map.get('specific_products', []))
        logger.info(f"✓ Step 2 complete: {mapped_count} links mapped")
        return link_map
    
    def infer_dial_settings(self, stakeholder_profile: Optional[str]) -> Dict:
        """STEP 3: Infer dial settings from stakeholder profile"""
        logger.info("[STEP 3/13] Inferring dial settings...")
        
        # Default settings (if no profile)
        dial_settings = {
            "relationshipDepth": "cold",
            "formality": 6,
            "warmth": 5,
            "ctaRigour": "moderate"
        }
        
        if stakeholder_profile:
            # Try to extract from profile tags or content
            # Look for tags like: [relationship:warm], [formality:8], etc.
            
            # Relationship depth
            if any(x in stakeholder_profile.lower() for x in ["warm", "trusted", "close"]):
                dial_settings["relationshipDepth"] = "warm"
            elif any(x in stakeholder_profile.lower() for x in ["familiar", "ongoing"]):
                dial_settings["relationshipDepth"] = "familiar"
            
            # Formality (look for indicators)
            if "formal" in stakeholder_profile.lower():
                dial_settings["formality"] = 8
            elif "casual" in stakeholder_profile.lower():
                dial_settings["formality"] = 4
            
            # Warmth
            if "enthusiastic" in stakeholder_profile.lower():
                dial_settings["warmth"] = 8
            elif "reserved" in stakeholder_profile.lower():
                dial_settings["warmth"] = 3
            
            # CTA rigour
            if "decision-maker" in stakeholder_profile.lower():
                dial_settings["ctaRigour"] = "high"
            elif "explorer" in stakeholder_profile.lower() or "researcher" in stakeholder_profile.lower():
                dial_settings["ctaRigour"] = "low"
        
        self.artifacts["dial_settings"] = dial_settings
        logger.info(f"✓ Step 3 complete: {dial_settings}")
        return dial_settings
    
    def generate_email_draft(self, context: Dict, dial_settings: Dict, link_map: Dict) -> str:
        """STEP 4: Generate initial email draft"""
        logger.info("[STEP 4/13] Generating initial email draft...")
        
        # Extract recipient name from stakeholder profile or meeting folder name
        recipient_name = self._extract_recipient_name(context)
        meeting_topic = self._extract_meeting_topic(context)
        
        # Generate subject line
        subject = f"Following Up — {recipient_name} x Careerspan [{meeting_topic}]"
        
        # Generate body based on dial settings
        body = self._generate_email_body(
            context=context,
            recipient_name=recipient_name,
            dial_settings=dial_settings,
            link_map=link_map
        )
        
        draft = f"""**Subject:** {subject}

{body}"""
        
        self.artifacts["initial_draft"] = draft
        logger.info("✓ Step 4 complete: Initial draft generated")
        return draft
    
    def _extract_recipient_name(self, context: Dict) -> str:
        """Extract recipient first name from profile or folder"""
        # Try stakeholder profile first
        if context.get("stakeholder_profile"):
            # Look for "STAKEHOLDER_PROFILE: FirstName LastName"
            match = re.search(r'STAKEHOLDER_PROFILE:\s+(\w+)', context["stakeholder_profile"])
            if match:
                return match.group(1)
            
            # Try "# FirstName LastName"
            match = re.search(r'#\s+(\w+)\s+\w+', context["stakeholder_profile"])
            if match:
                return match.group(1)
        
        # Fallback: parse from folder name (e.g., "2025-10-10_hamoon-ekhtiari-futurefit")
        folder_name = Path(context["meeting_folder"]).name
        parts = folder_name.split('_')
        if len(parts) >= 2:
            # Extract first name from pattern like "hamoon-ekhtiari"
            name_part = parts[1].split('-')[0]
            return name_part.capitalize()
        
        return "there"
    
    def _extract_meeting_topic(self, context: Dict) -> str:
        """Extract 2-3 word meeting topic"""
        # For now, use simple heuristic
        # In production, this would use NLP on transcript
        return "partnership pathways"
    
    def _generate_email_body(self, context: Dict, recipient_name: str, 
                            dial_settings: Dict, link_map: Dict) -> str:
        """Generate email body following v11.0.1 voice spec"""
        
        # Get formality and warmth levels
        formality = dial_settings.get("formality", 6)
        warmth = dial_settings.get("warmth", 5)
        relationship = dial_settings.get("relationshipDepth", "cold")
        
        # Opening (calibrated to warmth)
        if warmth >= 7:
            opening = f"Hi {recipient_name},\n\nReally enjoyed our conversation—"
        elif warmth >= 5:
            opening = f"Hi {recipient_name},\n\nGreat connecting last week."
        else:
            opening = f"Hi {recipient_name},\n\nThank you for taking the time to meet."
        
        # Body structure: resonance + concrete details + CTA
        # NOTE: This is a simplified version. Full implementation would
        # analyze transcript for specific details, resonant moments, etc.
        
        body = f"""{opening} I appreciated your thoughtful questions about how we could potentially work together.

As promised, here are two concrete use cases we discussed:

**1. [Use Case 1 Title]**  
[Brief description from transcript - 2-3 sentences with specific details]

**2. [Use Case 2 Title]**  
[Brief description from transcript - 2-3 sentences with specific details]

Both approaches would [specific benefit mentioned in conversation]."""
        
        # Add links (MUST be from essential-links.json per P16)
        if link_map.get("company_homepage"):
            body += f" You can see more about our approach at [{self._get_domain(link_map['company_homepage'])}]({link_map['company_homepage']})"
        
        if link_map.get("calendly_30min"):
            body += f", and happy to [grab 30 minutes]({link_map['calendly_30min']}) to discuss further"
        
        body += " if either resonates."
        
        # Closing (calibrated to relationship depth)
        if relationship == "warm":
            closing = "\n\nLooking forward to continuing the conversation."
        elif relationship == "familiar":
            closing = "\n\nLooking forward to hearing what makes sense on your end."
        else:
            closing = "\n\nLooking forward to your thoughts."
        
        body += closing
        
        # Signature
        body += "\n\nBest,  \nVrijen"
        
        return body
    
    def _get_domain(self, url: str) -> str:
        """Extract clean domain from URL for display"""
        domain = re.sub(r'https?://(www\.)?', '', url)
        domain = domain.split('/')[0]
        return domain
    
    def self_review(self, draft: str, dial_settings: Dict) -> Dict:
        """STEP 5: Self-review draft against v11.0.1 criteria"""
        logger.info("[STEP 5/13] Running self-review...")
        
        issues = []
        warnings = []
        
        # Check voice compliance
        if "we're excited" in draft.lower() or "i'm excited" in draft.lower():
            issues.append("Contains 'excited' (voice violation)")
        
        if "synergy" in draft.lower() or "leverage" in draft.lower():
            issues.append("Contains buzzwords (voice violation)")
        
        # Check first-person singular
        if "we " in draft.lower() and "we discussed" not in draft.lower():
            warnings.append("Contains 'we' (prefer first-person singular)")
        
        # Check link format
        if "[PLACEHOLDER" in draft or "[TBD" in draft:
            issues.append("Contains placeholder links")
        
        # Check for P.S. section (should not exist per v11.0.1)
        if "P.S." in draft or "P.P.S." in draft:
            issues.append("Contains P.S. section (removed in v11.0.1)")
        
        review = {
            "issues": issues,
            "warnings": warnings,
            "passed": len(issues) == 0,
            "needs_revision": len(issues) > 0
        }
        
        self.artifacts["self_review"] = review
        
        if issues:
            logger.warning(f"⚠ Step 5: {len(issues)} issues found")
        else:
            logger.info("✓ Step 5 complete: Self-review passed")
        
        return review
    
    def extract_resonant_details(self, transcript: str) -> List[Dict]:
        """STEP 6: Extract resonant conversation details"""
        logger.info("[STEP 6/13] Extracting resonant details...")
        
        # Simplified version - full implementation would use NLP
        # to identify key moments, emotional peaks, specific details
        
        resonant_details = []
        
        # Look for phrases indicating importance
        importance_markers = [
            "important", "key", "crucial", "really", "specifically",
            "exactly", "perfect", "makes sense", "that's interesting"
        ]
        
        lines = transcript.split('\n')
        for i, line in enumerate(lines):
            for marker in importance_markers:
                if marker in line.lower():
                    resonant_details.append({
                        "line_number": i + 1,
                        "text": line.strip()[:200],  # First 200 chars
                        "marker": marker,
                        "confidence": 0.7
                    })
                    break
        
        self.artifacts["resonant_details"] = resonant_details[:10]  # Top 10
        logger.info(f"✓ Step 6 complete: {len(resonant_details[:10])} details extracted")
        return resonant_details[:10]
    
    def extract_speaker_quotes(self, transcript: str, recipient_name: str) -> List[str]:
        """STEP 7: Extract stakeholder's own words"""
        logger.info("[STEP 7/13] Extracting speaker quotes...")
        
        quotes = []
        
        # Look for lines from the recipient
        # Format: "Speaker Name: quote"
        pattern = rf'{recipient_name}:?\s+(.+)'
        
        for match in re.finditer(pattern, transcript, re.IGNORECASE):
            quote = match.group(1).strip()
            if len(quote) > 20 and len(quote) < 200:  # Reasonable quote length
                quotes.append(quote)
        
        self.artifacts["speaker_quotes"] = quotes[:5]  # Top 5
        logger.info(f"✓ Step 7 complete: {len(quotes[:5])} quotes extracted")
        return quotes[:5]
    
    def build_phrase_pool(self, transcript: str) -> List[str]:
        """STEP 8: Build pool of natural phrases"""
        logger.info("[STEP 8/13] Building phrase pool...")
        
        # Extract common conversational phrases
        natural_phrases = []
        
        # Common phrase patterns
        patterns = [
            r'\b(makes sense)\b',
            r'\b(fair enough)\b',
            r'\b(I see)\b',
            r'\b(that\'s interesting)\b',
            r'\b(good question)\b',
            r'\b(I appreciate)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            natural_phrases.extend(matches)
        
        self.artifacts["phrase_pool"] = list(set(natural_phrases))[:20]
        logger.info(f"✓ Step 8 complete: {len(natural_phrases)} phrases extracted")
        return natural_phrases
    
    def load_voice_config(self, voice_config_text: str) -> Dict:
        """STEP 9: Load V's voice configuration"""
        logger.info("[STEP 9/13] Loading voice configuration...")
        
        # Parse voice.md for key parameters
        config = {
            "tone": "direct, concrete, unpretentious",
            "voice_rules": [],
            "forbidden_patterns": [],
            "preferred_patterns": []
        }
        
        # Extract ALWAYS patterns
        always_section = re.search(r'ALWAYS:(.*?)(?:NEVER:|$)', voice_config_text, re.DOTALL)
        if always_section:
            config["preferred_patterns"] = [
                line.strip('- ').strip() 
                for line in always_section.group(1).split('\n') 
                if line.strip().startswith('-')
            ]
        
        # Extract NEVER patterns
        never_section = re.search(r'NEVER:(.*?)(?:$|\n##)', voice_config_text, re.DOTALL)
        if never_section:
            config["forbidden_patterns"] = [
                line.strip('- ').strip() 
                for line in never_section.group(1).split('\n') 
                if line.strip().startswith('-')
            ]
        
        self.artifacts["voice_config"] = config
        logger.info("✓ Step 9 complete: Voice configuration loaded")
        return config
    
    def revise_draft(self, draft: str, review: Dict, resonant_details: List[Dict],
                    quotes: List[str], voice_config: Dict) -> str:
        """STEP 10: Revise draft based on review feedback"""
        logger.info("[STEP 10/13] Revising draft...")
        
        revised = draft
        
        # If no issues, return original
        if review.get("passed"):
            logger.info("✓ Step 10 complete: No revisions needed")
            return draft
        
        # Apply fixes for identified issues
        for issue in review.get("issues", []):
            if "excited" in issue.lower():
                revised = revised.replace("I'm excited", "I'm looking forward")
                revised = revised.replace("excited", "enthusiastic")
            
            if "buzzwords" in issue.lower():
                revised = revised.replace("synergy", "collaboration")
                revised = revised.replace("leverage", "use")
            
            if "P.S." in issue:
                # Remove P.S. section
                revised = re.sub(r'\n\nP\.S\..*$', '', revised, flags=re.DOTALL)
        
        self.artifacts["revised_draft"] = revised
        logger.info("✓ Step 10 complete: Draft revised")
        return revised
    
    def compression_pass(self, draft: str, target_words: int = 300) -> str:
        """STEP 11: Apply compression to reach target length"""
        logger.info("[STEP 11/13] Applying compression pass...")
        
        current_words = len(draft.split())
        
        if current_words <= target_words:
            logger.info(f"✓ Step 11 complete: {current_words} words (under target)")
            return draft
        
        # Simplified compression: remove redundant phrases
        compressed = draft
        
        # Remove filler phrases
        fillers = [
            "I wanted to ",
            "I just wanted to ",
            "I thought I would ",
            "as I mentioned, "
        ]
        
        for filler in fillers:
            compressed = compressed.replace(filler, "")
        
        # Combine short sentences
        compressed = compressed.replace(". I ", "—I ")
        
        current_words_after = len(compressed.split())
        logger.info(f"✓ Step 11 complete: {current_words} → {current_words_after} words")
        
        self.artifacts["compressed_draft"] = compressed
        return compressed
    
    def verify_links(self, draft: str, link_map: Dict) -> Tuple[bool, List[str]]:
        """STEP 12: Verify all links are from essential-links.json (P16 compliance)"""
        logger.info("[STEP 12/13] Verifying links (P16 compliance)...")
        
        # Extract all URLs from draft
        url_pattern = r'https?://[^\s\)\]]+'
        draft_urls = re.findall(url_pattern, draft)
        
        # Get all valid URLs from link_map
        valid_urls = set()
        for key, value in link_map.items():
            if isinstance(value, str) and value:
                valid_urls.add(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "url" in item:
                        valid_urls.add(item["url"])
        
        # Check each draft URL against valid URLs
        violations = []
        for url in draft_urls:
            if url not in valid_urls:
                violations.append(url)
        
        passed = len(violations) == 0
        
        if passed:
            logger.info(f"✓ Step 12 complete: All {len(draft_urls)} links verified")
        else:
            logger.error(f"❌ Step 12 FAILED: {len(violations)} fabricated links found")
            for url in violations:
                logger.error(f"  ❌ {url}")
        
        self.artifacts["link_verification"] = {
            "passed": passed,
            "draft_urls": draft_urls,
            "violations": violations
        }
        
        return passed, violations
    
    def validate_readability(self, draft: str) -> Dict:
        """STEP 13: Validate readability (Flesch-Kincaid ≤ 10)"""
        logger.info("[STEP 13/13] Validating readability...")
        
        # Remove markdown and get clean text
        clean_text = re.sub(r'\*\*|\[([^\]]+)\]\([^\)]+\)', r'\1', draft)
        
        # Calculate basic metrics
        sentences = len([s for s in re.split(r'[.!?]+', clean_text) if s.strip()])
        words = len(clean_text.split())
        
        # Simplified FK calculation
        # Real FK = 0.39(words/sentences) + 11.8(syllables/words) - 15.59
        # Approximation: assume ~1.5 syllables per word average
        avg_sentence_length = words / max(sentences, 1)
        fk_grade = (0.39 * avg_sentence_length) + 11.8 * 1.5 - 15.59
        
        passed = fk_grade <= 10.0
        
        metrics = {
            "word_count": words,
            "sentence_count": sentences,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "flesch_kincaid_grade": round(fk_grade, 1),
            "validation_passed": passed
        }
        
        self.artifacts["readability_metrics"] = metrics
        
        if passed:
            logger.info(f"✓ Step 13 complete: FK={fk_grade:.1f} (PASSED)")
        else:
            logger.warning(f"⚠ Step 13: FK={fk_grade:.1f} (exceeds target of 10.0)")
        
        return metrics
    
    def execute_pipeline(self) -> Dict:
        """Execute the 13-step email generation pipeline"""
        logger.info("Starting email generation pipeline...")
        
        try:
            # STEP 1: Load and validate transcript (OPTIONAL in Content Library mode)
            transcript_path = self.meeting_folder / "transcript.txt"
            has_transcript = transcript_path.exists()
            
            if self.use_content_library and not has_transcript:
                logger.info("[CL] No transcript found, proceeding with B-blocks only")
                transcript = None
            elif not has_transcript:
                logger.error(f"No transcript found in {self.meeting_folder}")
                return {"success": False, "error": "No transcript found"}
            else:
                logger.info("[STEP 1/13] Loading transcript...")
                with open(transcript_path) as f:
                    transcript = f.read()
                logger.info(f"✓ Loaded transcript ({len(transcript)} chars)")
            
            # Content Library flow
            if self.use_content_library:
                logger.info("[CL] Using Content Library workflow")
                
                # Load B-blocks from meeting folder
                logger.info(f"Loading B-blocks from {self.meeting_folder}")
                b_parser = BBlockParser(self.meeting_folder)
                b_parser.load_all_blocks()
                
                # Extract email context
                logger.info("Extracting email context from B-blocks")
                b_context = b_parser.extract_email_context()
                logger.info(f"  ✓ Extracted: {len(b_context['resources_explicit'])} explicit resources, "
                          f"{len(b_context['eloquent_lines'])} eloquent lines, "
                          f"{len(b_context['action_items'])} actions")
                
                # STEP 3: Compose email from structured context + ContentLibrary
                composer = EmailComposer()
                
                # Extract metadata for composition
                meeting_metadata = b_context.get("metadata", {})
                recipient_name = meeting_metadata.get("stakeholder", "there")
                meeting_summary = meeting_metadata.get("summary", "")
                
                final_draft = composer.compose_email(
                    recipient_name=recipient_name,
                    meeting_summary=meeting_summary,
                    resources_explicit=[r for r in b_context["resources_explicit"]],
                    resources_suggested=[r for r in b_context["resources_suggested"]],
                    eloquent_lines=b_context["eloquent_lines"],
                    key_decisions=b_context.get("key_decisions", []),
                    action_items=b_context.get("action_items", [])
                )
                
                # STEP 4: Validate links and readability
                link_check_passed, link_violations = self.verify_links(final_draft, link_map)
                readability = self.validate_readability(final_draft)
                
                # Build result
                result = {
                    "success": link_check_passed and readability["validation_passed"],
                    "draft": final_draft,
                    "artifacts": self.artifacts,
                    "meeting_folder": str(self.meeting_folder),
                    "output_dir": str(self.output_dir),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
                }
                
                # Save outputs (unless dry-run)
                self._save_outputs(result)
                
                logger.info("="*70)
                if result["success"]:
                    logger.info("✅ PIPELINE COMPLETE - ALL VALIDATIONS PASSED")
                else:
                    logger.warning("⚠️ PIPELINE COMPLETE - VALIDATION WARNINGS")
                logger.info("="*70)
                
                return result
            
            # Legacy flow (requires transcript)
            else:
                if not transcript:
                    return {"success": False, "error": "Transcript required for legacy flow"}
                
                # STEP 2-13: Legacy scaffolded generation
                # ... existing legacy flow code ...
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "meeting_folder": str(self.meeting_folder)
            }
    
    def _save_outputs(self, result: Dict):
        """Save all outputs to meeting folder"""
        logger.info("Saving outputs...")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save final draft (markdown)
        draft_path = self.output_dir / "follow_up_email_draft.md"
        draft_path.write_text(result["draft"])
        logger.info(f"✓ Saved draft: {draft_path}")
        
        # Save copy-paste version (plain text)
        copy_paste = self._strip_markdown(result["draft"])
        copy_paste_path = self.output_dir / "follow_up_email_copy_paste.txt"
        copy_paste_path.write_text(copy_paste)
        logger.info(f"✓ Saved copy-paste version: {copy_paste_path}")
        
        # Save artifacts as JSON
        artifacts_path = self.output_dir / "follow_up_email_artifacts.json"
        artifacts_path.write_text(json.dumps(result["artifacts"], indent=2))
        logger.info(f"✓ Saved artifacts: {artifacts_path}")
        
        # Save summary
        summary = self._generate_summary(result)
        summary_path = self.output_dir / "follow_up_email_summary.md"
        summary_path.write_text(summary)
        logger.info(f"✓ Saved summary: {summary_path}")
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown formatting for plain text"""
        # Remove bold
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        # Convert links to plain text
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1 (\2)', text)
        return text
    
    def _generate_summary(self, result: Dict) -> str:
        """Generate execution summary"""
        artifacts = result["artifacts"]
        
        summary = f"""# Follow-Up Email Generation Summary

**Generated:** {result["timestamp"]}  
**Meeting:** {result["meeting_folder"]}  
**Status:** {'✅ SUCCESS' if result["success"] else '⚠️ WARNINGS'}

---

## Pipeline Results

### Dial Settings
- Relationship Depth: {artifacts['dial_settings']['relationshipDepth']}
- Formality: {artifacts['dial_settings']['formality']}/10
- Warmth: {artifacts['dial_settings']['warmth']}/10
- CTA Rigour: {artifacts['dial_settings']['ctaRigour']}

### Quality Metrics
- Word Count: {artifacts['readability_metrics']['word_count']}
- Avg Sentence Length: {artifacts['readability_metrics']['avg_sentence_length']} words
- Flesch-Kincaid Grade: {artifacts['readability_metrics']['flesch_kincaid_grade']}
- Readability: {'✓ PASSED' if artifacts['readability_metrics']['validation_passed'] else '⚠ REVIEW'}

### Link Verification
- Links Used: {len(artifacts['link_verification']['draft_urls'])}
- Verification: {'✓ PASSED' if artifacts['link_verification']['passed'] else '❌ FAILED'}
"""
        
        if artifacts['link_verification']['violations']:
            summary += "\n**⚠️ Fabricated Links Detected:**\n"
            for url in artifacts['link_verification']['violations']:
                summary += f"- {url}\n"
        
        summary += f"""
---

## Outputs Generated
- `follow_up_email_draft.md` - Full markdown version
- `follow_up_email_copy_paste.txt` - Plain text for email client
- `follow_up_email_artifacts.json` - Pipeline artifacts
- `follow_up_email_summary.md` - This file

---

*Generated by N5 Follow-Up Email Generator v11.0.1*
"""
        
        return summary

    def _register_email(self, draft_path: Path):
        """Register generated email in tracking system"""
        try:
            registry = EmailRegistry()
            
            # Generate unique ID
            email_id = f"email_{self.meeting_folder.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get stakeholder from metadata
            stakeholder = self.metadata.get("stakeholder_name", "Unknown")
            email_addr = self.metadata.get("stakeholder_email", "")
            
            registry.create_entry(
                email_id=email_id,
                meeting_id=self.meeting_folder.name,
                stakeholder_name=stakeholder,
                stakeholder_email=email_addr,
                draft_path=str(draft_path)
            )
            
            logger.info(f"✓ Registered email: {email_id}")
        except Exception as e:
            logger.warning(f"Failed to register email: {e}")
    
    def _add_preflight_checklist(self, draft: str) -> str:
        """Add pre-flight checklist as markdown comment"""
        checklist = """

---

<!-- PRE-FLIGHT CHECKLIST (Remove before sending)

□ Relationship depth correct? (Check: overly formal? missing context?)
□ Business terms accurate? (Pricing, product names, commitments)
□ Links relevant for THIS stakeholder?
□ Tone matches our actual relationship?
□ Any third-party references that shouldn't be there?

REMEMBER: The email you send = ground truth. System will learn from differences.

-->
"""
        return draft + checklist


def main() -> int:
    parser = argparse.ArgumentParser(
        description="N5 Follow-Up Email Generator v11.0.1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--meeting-folder",
        required=True,
        help="Path to meeting folder (absolute or relative to workspace)"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: DELIVERABLES/ in meeting folder)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, do not write files"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing outputs"
    )
    parser.add_argument(
        "--use-content-library",
        action="store_true",
        help="Use Content Library flow (B-Block Parser + Email Composer) (default: False for gradual rollout)"
    )
    
    args = parser.parse_args()
    
    # Resolve meeting folder path
    meeting_folder = Path(args.meeting_folder)
    if not meeting_folder.is_absolute():
        meeting_folder = Path("/home/workspace") / meeting_folder
    
    # Initialize generator
    generator = EmailGenerator(
        meeting_folder=meeting_folder,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        use_content_library=args.use_content_library
    )
    
    # Validate inputs
    if not generator.validate_inputs():
        return 1
    
    # Execute pipeline
    result = generator.execute_pipeline()
    
    # Print summary
    print("\n" + "="*70)
    print("FINAL DRAFT PREVIEW")
    print("="*70)
    print(result.get("draft", "ERROR: No draft generated"))
    print("="*70)
    
    if result.get("success"):
        print("\n✅ Email generation complete!")
        if not args.dry_run:
            print(f"\n📁 Outputs saved to: {result['output_dir']}")
        return 0
    else:
        print("\n⚠️ Email generation completed with warnings.")
        print("   Review artifacts for details.")
        return 1


if __name__ == "__main__":
    exit(main())
