#!/usr/bin/env python3
"""
Voice Transformation Engine
Applies voice profiles to style-free content using few-shot transformation.

Part of system-wide voice transformation system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TransformationResult:
    """Result of voice transformation"""
    content: str
    profile_used: str
    angle_name: str
    confidence: float
    metadata: Dict


class VoiceTransformer:
    """
    Core transformation engine.
    
    Process:
    1. Load voice profile + examples
    2. Apply transformation using few-shot pattern
    3. Validate output quality
    4. Return transformed content
    """
    
    def __init__(self, profiles_path: Path = None):
        """Initialize with path to voice profiles"""
        if profiles_path is None:
            profiles_path = Path("/home/workspace/N5/prefs/communication/voice-profiles.json")
        
        self.profiles_path = profiles_path
        self.profiles = self._load_profiles()
        self.content_library = self._load_content_library()
    
    def _load_profiles(self) -> Dict:
        """Load voice profile registry"""
        try:
            if self.profiles_path.exists():
                with open(self.profiles_path) as f:
                    return json.load(f)
            logger.warning(f"Profiles not found at {self.profiles_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading profiles: {e}")
            return {}
    
    def _load_content_library(self) -> Dict:
        """Load content library with examples"""
        try:
            lib_path = Path("/home/workspace/N5/prefs/communication/content-library.json")
            if lib_path.exists():
                with open(lib_path) as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading content library: {e}")
            return {}
    
    def get_profile(self, content_type: str) -> Optional[Dict]:
        """Get voice profile for content type"""
        return self.profiles.get(content_type)
    
    def get_examples(self, content_type: str, angle: str = None, limit: int = 3) -> List[Dict]:
        """
        Get few-shot examples for transformation.
        
        Args:
            content_type: Type of content (email, blog, etc)
            angle: Specific angle/approach (optional)
            limit: Max examples to return
            
        Returns:
            List of example pairs (style-free → voiced)
        """
        examples = []
        
        if content_type in self.content_library:
            content_examples = self.content_library[content_type].get("examples", [])
            
            # Filter by angle if specified
            if angle:
                content_examples = [
                    ex for ex in content_examples 
                    if ex.get("angle") == angle
                ]
            
            examples = content_examples[:limit]
        
        logger.info(f"Retrieved {len(examples)} examples for {content_type}")
        return examples
    
    def transform(
        self,
        content: str,
        content_type: str,
        angle: str = "standard",
        use_override: bool = False
    ) -> TransformationResult:
        """
        Transform style-free content into voiced content.
        
        Args:
            content: Style-free draft content
            content_type: Type of content (email, blog, doc, social, note)
            angle: Messaging angle/approach
            use_override: If True, use neutral/professional tone instead
            
        Returns:
            TransformationResult with transformed content
        """
        logger.info(f"Transforming {content_type} content (angle: {angle}, override: {use_override})")
        
        # Get profile
        profile_key = "override" if use_override else content_type
        profile = self.get_profile(profile_key)
        
        if not profile:
            logger.warning(f"No profile found for {profile_key}, returning original")
            return TransformationResult(
                content=content,
                profile_used=profile_key,
                angle_name=angle,
                confidence=0.0,
                metadata={"error": "profile_not_found"}
            )
        
        # Get few-shot examples
        examples = self.get_examples(content_type, angle)
        
        # Build transformation instruction
        instruction = self._build_transformation_instruction(
            content=content,
            profile=profile,
            examples=examples,
            angle=angle
        )
        
        # This is a framework - actual LLM transformation happens at runtime
        # when this is called from the main system
        logger.info(f"✓ Transformation instruction built for {content_type}")
        
        return TransformationResult(
            content=instruction,  # Returns instruction for now
            profile_used=profile_key,
            angle_name=angle,
            confidence=1.0,
            metadata={
                "examples_used": len(examples),
                "profile": profile.get("name", profile_key)
            }
        )
    
    def _build_transformation_instruction(
        self,
        content: str,
        profile: Dict,
        examples: List[Dict],
        angle: str
    ) -> str:
        """
        Build transformation instruction for LLM.
        
        This creates the few-shot prompt that will be executed.
        """
        instruction_parts = [
            "# VOICE TRANSFORMATION TASK",
            "",
            f"**Content Type:** {profile.get('name', 'Unknown')}",
            f"**Angle:** {angle}",
            "",
            "## Voice Profile",
            ""
        ]
        
        # Add profile attributes
        if "attributes" in profile:
            instruction_parts.append("**Key Attributes:**")
            for attr, value in profile["attributes"].items():
                instruction_parts.append(f"- {attr}: {value}")
            instruction_parts.append("")
        
        # Add structural rules
        if "structure" in profile:
            instruction_parts.append("**Structural Rules:**")
            for rule in profile["structure"]:
                instruction_parts.append(f"- {rule}")
            instruction_parts.append("")
        
        # Add few-shot examples
        if examples:
            instruction_parts.append("## Examples (Style-Free → Voiced)")
            instruction_parts.append("")
            
            for i, ex in enumerate(examples, 1):
                instruction_parts.append(f"### Example {i}")
                instruction_parts.append("")
                instruction_parts.append("**Style-Free:**")
                instruction_parts.append(ex.get("style_free", ""))
                instruction_parts.append("")
                instruction_parts.append("**Voiced:**")
                instruction_parts.append(ex.get("voiced", ""))
                instruction_parts.append("")
        
        # Add content to transform
        instruction_parts.extend([
            "## Content to Transform",
            "",
            content,
            "",
            "## Instructions",
            "",
            "Transform the above content following the voice profile and examples.",
            "Maintain all factual information while applying voice characteristics.",
            "Output ONLY the transformed content, no meta-commentary."
        ])
        
        return "\n".join(instruction_parts)
    
    def validate_output(
        self,
        content: str,
        content_type: str,
        original_draft: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate transformed content meets quality requirements.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Basic checks
        if not content or len(content.strip()) < 10:
            issues.append("Output too short")
        
        if content == original_draft:
            issues.append("No transformation applied")
        
        # Content-type specific validation
        if content_type == "email":
            if not any(greeting in content.lower() for greeting in ["hi", "hello", "hey"]):
                issues.append("Email missing greeting")
        
        elif content_type == "doc":
            # Docs require highest accuracy
            if "TODO" in content or "PLACEHOLDER" in content:
                issues.append("Document contains placeholders")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info(f"✓ Validation passed for {content_type}")
        else:
            logger.warning(f"Validation issues for {content_type}: {issues}")
        
        return is_valid, issues


def main():
    """Test/demo of transformer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Transformer")
    parser.add_argument("--content", required=True, help="Content to transform")
    parser.add_argument("--type", required=True, help="Content type")
    parser.add_argument("--angle", default="standard", help="Messaging angle")
    parser.add_argument("--override", action="store_true", help="Use neutral override")
    
    args = parser.parse_args()
    
    transformer = VoiceTransformer()
    result = transformer.transform(
        content=args.content,
        content_type=args.type,
        angle=args.angle,
        use_override=args.override
    )
    
    print("\n" + "="*80)
    print("TRANSFORMATION RESULT")
    print("="*80)
    print(f"\nProfile: {result.profile_used}")
    print(f"Angle: {result.angle_name}")
    print(f"Confidence: {result.confidence}")
    print(f"\nOutput:\n{result.content}")
    print("\n" + "="*80)
    
    return 0


if __name__ == "__main__":
    exit(main())
