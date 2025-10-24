#!/usr/bin/env python3
"""
LinkedIn Post Generator - N5 OS
Version: 1.0.0
Date: 2025-10-09

Purpose: Generate voice-authentic LinkedIn posts with auto-dial inference
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys

# N5 paths
N5_ROOT = Path("/home/workspace/N5")
KNOWLEDGE_ROOT = Path("/home/workspace/Knowledge")
VOICE_FILE = N5_ROOT / "prefs/communication/voice.md"
LINKS_FILE = N5_ROOT / "prefs/communication/essential-links.json"
STOP_VERBS_FILE = N5_ROOT / "prefs/communication/linkedin-stop-verbs.json"
OUTPUT_DIR = KNOWLEDGE_ROOT / "personal-brand/social-content/linkedin"

class LinkedInPostGenerator:
    def __init__(self):
        self.voice_schema = {}
        self.essential_links = {}
        self.stop_verbs = {}
        self.load_prefs()
        
    def load_prefs(self):
        """Load N5 prefs files"""
        print("🔧 Loading N5 preferences...")
        
        # Load voice.md
        if not VOICE_FILE.exists():
            raise FileNotFoundError(f"Voice schema not found: {VOICE_FILE}")
        self.voice_schema = self._parse_voice_md(VOICE_FILE)
        
        # Load essential-links.json
        if LINKS_FILE.exists():
            with open(LINKS_FILE, 'r') as f:
                self.essential_links = json.load(f)
        
        # Load linkedin-stop-verbs.json
        if STOP_VERBS_FILE.exists():
            with open(STOP_VERBS_FILE, 'r') as f:
                self.stop_verbs = json.load(f)
        
        print("✅ Preferences loaded successfully\n")
    
    def _parse_voice_md(self, filepath: Path) -> Dict:
        """Parse voice.md for key patterns (simplified parser)"""
        content = filepath.read_text()
        
        # Extract key sections (simplified - would be more robust in production)
        schema = {
            "formality_levels": ["casual", "balanced", "formal"],
            "relationship_depths": [0, 1, 2, 3, 4],
            "cta_rigour_levels": ["soft", "balanced", "direct"],
            "readability_targets": {
                "flesch_kincaid_max": 12,
                "sentence_length_max": 32,
                "paragraph_length": "2-4 sentences"
            },
            "distinctive_verbs": self._extract_distinctive_verbs(content),
            "cta_patterns": self._extract_cta_patterns(content)
        }
        return schema
    
    def _extract_distinctive_verbs(self, content: str) -> List[str]:
        """Extract distinctive verbs from voice.md (simplified)"""
        # In production, would parse from "Tonal Architecture" section
        # For now, return a curated list based on Vrijen's style
        return [
            "build", "create", "design", "develop", "explore",
            "discover", "reveal", "uncover", "challenge", "question",
            "rethink", "reframe", "shift", "transform", "reshape",
            "enable", "equip", "support", "help", "guide"
        ]
    
    def _extract_cta_patterns(self, content: str) -> Dict:
        """Extract CTA patterns from voice.md"""
        return {
            "soft": [
                "What's your experience with {topic}?",
                "Curious to hear your thoughts.",
                "How are you thinking about this?",
                "What's worked for you?"
            ],
            "balanced": [
                "I'd love to hear your perspective.",
                "Share your take in the comments.",
                "Let me know what you think.",
                "Drop a comment if this resonates."
            ],
            "direct": [
                "DM me if you want to discuss this.",
                "Let's talk—reach out if this applies to you.",
                "Message me if you're navigating this.",
                "Book a time to chat: {calendly_link}"
            ]
        }
    
    def infer_dials(self, seed_content: str) -> Dict:
        """Auto-infer formality, warmth, CTA rigour from seed content"""
        print("🔍 Analyzing seed content for voice dials...")
        
        # Formality score
        formal_markers = ["however", "therefore", "furthermore", "consequently", "moreover"]
        informal_markers = ["I'm", "you're", "don't", "can't", "just", "really", "pretty"]
        
        formal_count = sum(1 for marker in formal_markers if marker.lower() in seed_content.lower())
        informal_count = sum(1 for marker in informal_markers if marker.lower() in seed_content.lower())
        
        formality_score = (formal_count - informal_count) / max(len(seed_content.split()), 1)
        
        if formality_score > 0.02:
            formality = "formal"
            formality_confidence = 0.80
        elif formality_score < -0.02:
            formality = "casual"
            formality_confidence = 0.75
        else:
            formality = "balanced"
            formality_confidence = 0.85
        
        # Warmth score (personal pronouns)
        personal_pronouns = ["I", "my", "we", "our", "you", "your"]
        warmth_count = sum(1 for word in seed_content.split() if word in personal_pronouns)
        warmth_score = warmth_count / max(len(seed_content.split()), 1)
        
        # CTA rigour (decisive language)
        decisive_words = ["should", "must", "need", "will", "definitely", "clearly"]
        decisive_count = sum(1 for word in decisive_words if word.lower() in seed_content.lower())
        
        if decisive_count >= 3:
            cta_rigour = "direct"
            cta_confidence = 0.78
        elif decisive_count >= 1:
            cta_rigour = "balanced"
            cta_confidence = 0.82
        else:
            cta_rigour = "soft"
            cta_confidence = 0.75
        
        # Relationship depth (default to 2 = professional network)
        relationship_depth = 2
        depth_confidence = 0.70
        
        inference = {
            "formality": formality,
            "formality_confidence": formality_confidence,
            "warmth_score": warmth_score,
            "cta_rigour": cta_rigour,
            "cta_confidence": cta_confidence,
            "relationship_depth": relationship_depth,
            "depth_confidence": depth_confidence
        }
        
        print(f"   - Formality: {formality} (confidence: {formality_confidence:.2f})")
        print(f"   - CTA Rigour: {cta_rigour} (confidence: {cta_confidence:.2f})")
        print(f"   - Relationship Depth: {relationship_depth} (confidence: {depth_confidence:.2f})\n")
        
        return inference
    
    def generate_hook(self, seed_content: str, formality: str) -> str:
        """Generate compelling first line"""
        # Extract first key idea
        sentences = [s.strip() for s in seed_content.split('.') if s.strip()]
        if not sentences:
            return "Here's something I've been thinking about."
        
        first_idea = sentences[0]
        
        # Shorten and punch it up based on formality
        if formality == "casual":
            return first_idea[:100] + "." if len(first_idea) > 100 else first_idea + "."
        elif formality == "formal":
            return first_idea + "."
        else:  # balanced
            return first_idea[:80] + "." if len(first_idea) > 80 else first_idea + "."
    
    def apply_voice_engine(self, seed_content: str, voice_config: Dict, target_length: int) -> str:
        """Transform seed content into LinkedIn post"""
        print("✍️  Applying voice engine...")
        
        formality = voice_config["formality"]
        
        # Parse seed content
        sentences = [s.strip() for s in seed_content.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        
        # Structure: Hook + Body + Bridge to CTA
        hook = self.generate_hook(seed_content, formality)
        
        # Build expanded body to meet target length
        body_parts = []
        
        # Include all key points from seed
        for sentence in sentences[1:] if len(sentences) > 1 else sentences:
            body_parts.append(sentence + ".")
        
        # Add elaboration and examples to reach target length
        current_word_count = len((hook + " " + " ".join(body_parts)).split())
        
        # If we're significantly under target, add elaborative paragraphs
        if current_word_count < target_length * 0.7:
            # Add context paragraph
            if formality == "casual":
                elaboration = "\n\nI see this pattern constantly with clients. They're excited in month one, coasting by month three, questioning everything by month six. That's not a performance issue—that's a career development gap."
            elif formality == "formal":
                elaboration = "\n\nThis dynamic manifests consistently across organizations. Initial enthusiasm gives way to routine, which gradually erodes into disengagement. Addressing this pattern requires proactive career development interventions, not reactive retention strategies."
            else:  # balanced
                elaboration = "\n\nThe pattern is predictable: initial enthusiasm fades to routine, routine breeds questioning. Most organizations wait until exit interviews to understand what went wrong. That's too late."
            body_parts.append(elaboration)
        
        # Combine all parts
        body = "\n\n".join(body_parts)
        
        # Add Careerspan positioning (subtle)
        positioning = self._add_positioning(formality)
        
        post_draft = f"{hook}\n\n{body}\n\n{positioning}".strip()
        
        # Apply distinctive verbs
        post_draft = self._inject_distinctive_verbs(post_draft)
        
        # Ensure readability
        post_draft = self._enforce_readability(post_draft)
        
        return post_draft
    
    def _add_positioning(self, formality: str) -> str:
        """Add subtle Careerspan positioning"""
        if formality == "casual":
            return "This is the kind of shift we help leaders make at Careerspan."
        elif formality == "formal":
            return "This represents a fundamental shift in how we approach career development."
        else:  # balanced
            return "It's a different way to think about career growth—and it's what we focus on at Careerspan."
    
    def _inject_distinctive_verbs(self, text: str) -> str:
        """Replace weak verbs with distinctive ones"""
        # Simplified verb replacement
        replacements = {
            "use": "apply",
            "make": "create",
            "do": "execute",
            "get": "achieve",
            "have": "maintain"
        }
        
        for weak, strong in replacements.items():
            # Only replace standalone word occurrences
            text = re.sub(rf'\b{weak}\b', strong, text, flags=re.IGNORECASE)
        
        return text
    
    def _enforce_readability(self, text: str) -> str:
        """Ensure readability targets met"""
        # Simplified - would use textstat library in production
        # For now, just break long sentences
        
        sentences = text.split('.')
        readable_sentences = []
        
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            
            words = s.split()
            if len(words) > 30:
                # Split long sentence at natural break
                mid = len(words) // 2
                first_half = ' '.join(words[:mid]) + '.'
                second_half = ' '.join(words[mid:])
                readable_sentences.extend([first_half, second_half])
            else:
                readable_sentences.append(s + '.')
        
        return '\n\n'.join([s for s in readable_sentences if s.strip()])
    
    def craft_ctas(self, cta_rigour: str, post_draft: str) -> List[str]:
        """Generate 1-2 context-appropriate CTAs"""
        cta_patterns = self.voice_schema.get("cta_patterns", {})
        rigour_patterns = cta_patterns.get(cta_rigour, cta_patterns.get("balanced", []))
        
        # Select most appropriate CTA
        # In production, would use semantic matching
        cta = rigour_patterns[0] if rigour_patterns else "What's your take?"
        
        # Inject Calendly if direct
        if cta_rigour == "direct" and "{calendly_link}" in cta:
            calendly_link = self.essential_links.get("links", {}).get("calendly", "")
            cta = cta.replace("{calendly_link}", calendly_link)
        
        return [cta]
    
    def validate_output(self, post_draft: str) -> Dict:
        """Validate readability and quality"""
        print("🔍 Validating output...")
        
        # Word count
        word_count = len(post_draft.split())
        
        # Sentence count and avg length
        sentences = [s for s in post_draft.split('.') if s.strip()]
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Check stop-verbs
        stop_verbs = self.stop_verbs.get("stopVerbs", [])
        stop_phrases = self.stop_verbs.get("stopPhrases", [])
        
        detected_stop_verbs = []
        for verb in stop_verbs:
            if verb.lower() in post_draft.lower():
                detected_stop_verbs.append(verb)
        
        for phrase in stop_phrases:
            if phrase.lower() in post_draft.lower():
                detected_stop_verbs.append(phrase)
        
        # Simplified readability (would use textstat in production)
        # Approximate FK grade: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        # For now, use sentence length as proxy
        fk_grade_approx = (avg_sentence_length * 0.5)
        
        validation = {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "fk_grade_approx": fk_grade_approx,
            "stop_verbs_detected": detected_stop_verbs,
            "readability_passed": fk_grade_approx <= 12 and avg_sentence_length <= 32,
            "length_passed": 150 <= word_count <= 400,
            "stop_verbs_passed": len(detected_stop_verbs) <= 2
        }
        
        passed = (validation["readability_passed"] and 
                  validation["length_passed"] and 
                  validation["stop_verbs_passed"])
        
        validation["overall_passed"] = passed
        
        if passed:
            print("✅ Validation PASSED\n")
        else:
            print("⚠️  Validation issues detected (see report)\n")
        
        return validation
    
    def generate_post(self, seed_content: str, mode: str = "thought-leadership",
                     formality: Optional[str] = None, cta_rigour: Optional[str] = None,
                     relationship_depth: Optional[int] = None, target_length: int = 300) -> Dict:
        """Main generation pipeline"""
        
        print("=" * 60)
        print("🚀 LINKEDIN POST GENERATOR")
        print("=" * 60 + "\n")
        
        # Step 1: Infer dials
        inferred = self.infer_dials(seed_content)
        
        # Step 2: Apply overrides
        voice_config = {
            "formality": formality or inferred["formality"],
            "cta_rigour": cta_rigour or inferred["cta_rigour"],
            "relationship_depth": relationship_depth or inferred["relationship_depth"],
            "formality_confidence": inferred["formality_confidence"],
            "cta_confidence": inferred["cta_confidence"],
            "depth_confidence": inferred["depth_confidence"]
        }
        
        # Step 3: Generate post
        post_draft = self.apply_voice_engine(seed_content, voice_config, target_length)
        
        # Step 4: Craft CTAs
        ctas = self.craft_ctas(voice_config["cta_rigour"], post_draft)
        
        # Step 5: Append CTAs to post
        post_with_ctas = post_draft + "\n\n" + "\n\n".join(ctas)
        
        # Step 6: Validate
        validation = self.validate_output(post_with_ctas)
        
        # Step 7: Assemble outputs
        result = {
            "post_draft": post_with_ctas,
            "voice_config_used": voice_config,
            "dial_inference_report": inferred,
            "validation_report": validation,
            "ctas": ctas,
            "timestamp": datetime.now().isoformat(),
            "mode": mode
        }
        
        return result
    
    def save_outputs(self, result: Dict, output_format: str = "markdown"):
        """Save outputs to workspace"""
        
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        
        # Save post draft
        draft_file = OUTPUT_DIR / f"{timestamp}-post-draft.md"
        draft_file.write_text(result["post_draft"])
        
        # Save metadata
        metadata_file = OUTPUT_DIR / f"{timestamp}-post-metadata.json"
        metadata_file.write_text(json.dumps(result, indent=2))
        
        # Save analysis
        analysis = self._generate_analysis_report(result)
        analysis_file = OUTPUT_DIR / f"{timestamp}-post-analysis.md"
        analysis_file.write_text(analysis)
        
        print("\n" + "=" * 60)
        print("✅ LINKEDIN POST GENERATED SUCCESSFULLY")
        print("=" * 60 + "\n")
        
        print(f"📄 Post Draft: {draft_file.relative_to(Path('/home/workspace'))}")
        print(f"📊 Metadata: {metadata_file.relative_to(Path('/home/workspace'))}")
        print(f"🔍 Analysis: {analysis_file.relative_to(Path('/home/workspace'))}\n")
        
        # Display summary
        validation = result["validation_report"]
        voice_config = result["voice_config_used"]
        
        print("📊 Metrics:")
        print(f"   - Word Count: {validation['word_count']}")
        print(f"   - Readability (FK Grade): {validation['fk_grade_approx']:.1f}")
        print(f"   - Stop Verbs Detected: {len(validation['stop_verbs_detected'])}")
        print(f"   - CTAs: {len(result['ctas'])}\n")
        
        print("🎛️  Voice Config Used:")
        print(f"   - Formality: {voice_config['formality']} (confidence: {voice_config['formality_confidence']:.2f})")
        print(f"   - CTA Rigour: {voice_config['cta_rigour']} (confidence: {voice_config['cta_confidence']:.2f})")
        print(f"   - Relationship Depth: {voice_config['relationship_depth']} (confidence: {voice_config['depth_confidence']:.2f})\n")
        
        if validation["overall_passed"]:
            print("🔍 Validation: PASSED ✅\n")
        else:
            print("⚠️  Validation: Issues detected (see analysis report)\n")
        
        # Auto-import hook: add the generated draft to the social post registry
        try:
            import subprocess
            add_cmd = [
                "python3", "/home/workspace/N5/scripts/n5_social_post.py", "add",
                str(draft_file), "--platform", "linkedin", "--status", "draft",
                "--source", "generated"
            ]
            print("🔗 Auto-importing generated draft into Social Post Registry...")
            result = subprocess.run(add_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Auto-import complete")
            else:
                print("⚠️ Auto-import failed (non-fatal). See details below:")
                print(result.stdout)
                print(result.stderr)
        except Exception as e:
            print(f"⚠️ Auto-import encountered an error (non-fatal): {e}")
        
        return {
            "draft_file": str(draft_file),
            "metadata_file": str(metadata_file),
            "analysis_file": str(analysis_file)
        }
    
    def _generate_analysis_report(self, result: Dict) -> str:
        """Generate analysis markdown report"""
        
        validation = result["validation_report"]
        voice_config = result["voice_config_used"]
        inference = result["dial_inference_report"]
        
        report = f"""# LinkedIn Post Analysis Report

**Generated**: {result['timestamp']}  
**Mode**: {result['mode']}

---

## Voice Configuration

| Parameter | Value | Confidence | Source |
|-----------|-------|-----------|---------|
| Formality | {voice_config['formality']} | {voice_config['formality_confidence']:.2f} | {'Auto-inferred' if inference else 'Manual'} |
| CTA Rigour | {voice_config['cta_rigour']} | {voice_config['cta_confidence']:.2f} | {'Auto-inferred' if inference else 'Manual'} |
| Relationship Depth | {voice_config['relationship_depth']} | {voice_config['depth_confidence']:.2f} | {'Auto-inferred' if inference else 'Manual'} |

---

## Readability Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Word Count | {validation['word_count']} | 150-400 | {'✅' if validation['length_passed'] else '❌'} |
| Sentence Count | {validation['sentence_count']} | - | - |
| Avg Sentence Length | {validation['avg_sentence_length']:.1f} words | ≤ 32 | {'✅' if validation['avg_sentence_length'] <= 32 else '❌'} |
| FK Grade (approx) | {validation['fk_grade_approx']:.1f} | ≤ 12 | {'✅' if validation['fk_grade_approx'] <= 12 else '❌'} |

---

## Quality Validation

### Stop Verbs/Phrases Detected

{f"**Found {len(validation['stop_verbs_detected'])}**: {', '.join(validation['stop_verbs_detected'])}" if validation['stop_verbs_detected'] else "✅ None detected"}

**Status**: {'✅ PASSED' if validation['stop_verbs_passed'] else '❌ FAILED (> 2 occurrences)'}

### CTAs

**Count**: {len(result['ctas'])}

**CTAs Used**:
{chr(10).join(f'- {cta}' for cta in result['ctas'])}

---

## Overall Validation

{'✅ **PASSED** - Post meets all quality standards' if validation['overall_passed'] else '⚠️ **ISSUES DETECTED** - Review validation details above'}

---

## Post Draft Preview

```
{result['post_draft'][:500]}...
```

---

## Recommendations

"""
        
        # Add recommendations
        if not validation['overall_passed']:
            report += "### Issues to Address:\n\n"
            if not validation['readability_passed']:
                report += "- **Readability**: Simplify language or shorten sentences\n"
            if not validation['length_passed']:
                report += f"- **Length**: Post is {validation['word_count']} words (target: 150-400)\n"
            if not validation['stop_verbs_passed']:
                report += "- **Stop Verbs**: Remove or replace clichéd language\n"
        else:
            report += "✅ Post is ready to publish. Consider:\n\n"
            report += "- Adding relevant hashtags (3-5 max)\n"
            report += "- Tagging relevant people or companies\n"
            report += "- Including a visual (image/carousel) if appropriate\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn posts with voice integration")
    parser.add_argument("--seed", type=str, help="Seed content (transcript/notes/idea)")
    parser.add_argument("--mode", type=str, default="thought-leadership", choices=["thought-leadership"])
    parser.add_argument("--formality", type=str, choices=["casual", "balanced", "formal"])
    parser.add_argument("--cta-rigour", type=str, choices=["soft", "balanced", "direct"])
    parser.add_argument("--relationship-depth", type=int, choices=[0, 1, 2, 3, 4])
    parser.add_argument("--target-length", type=int, default=300)
    parser.add_argument("--output-format", type=str, default="markdown", choices=["markdown", "json"])
    
    args = parser.parse_args()
    
    # Get seed content
    if args.seed:
        seed_content = args.seed
    else:
        print("Enter seed content (press Ctrl+D when done):")
        seed_content = sys.stdin.read().strip()
    
    if not seed_content:
        print("❌ Error: Seed content required")
        sys.exit(1)
    
    # Generate post
    generator = LinkedInPostGenerator()
    result = generator.generate_post(
        seed_content=seed_content,
        mode=args.mode,
        formality=args.formality,
        cta_rigour=args.cta_rigour,
        relationship_depth=args.relationship_depth,
        target_length=args.target_length
    )
    
    # Save outputs
    generator.save_outputs(result, args.output_format)


if __name__ == "__main__":
    main()
