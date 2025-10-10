#!/usr/bin/env python3
"""
Meeting Processing Orchestrator V2 - Phased Workflow (Standalone)
Generates minimal outputs by default, recommends deliverables, waits for user request.

NO V1 DEPENDENCIES - Fully self-sufficient
"""

import asyncio
import json
import logging
import subprocess
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Careerspan" / "Meetings"
MEETINGS_DIR.mkdir(parents=True, exist_ok=True)

from llm_utils import (
    query_llm_internal,
    infer_parameters_from_transcript,
    validate_inferred_parameters,
    extract_participants_from_transcript,
    extract_company_names
)


class MeetingOrchestratorV2:
    """
    V2 Phased Workflow:
    Phase 1: Generate only essential intelligence (action items, decisions, key info)
    Phase 2: Recommend deliverables based on content
    Phase 3: Wait for user request
    Phase 4: Generate requested deliverables on-demand
    """
    
    def __init__(self, transcript_path: str, meeting_types: List[str], stakeholder_types: List[str]):
        # Auto-convert .docx to .txt if needed
        original_path = Path(transcript_path)
        if original_path.suffix.lower() in ['.docx', '.doc']:
            self.transcript_path = convert_docx_to_txt(original_path)
        else:
            self.transcript_path = original_path
        
        self.meeting_types = meeting_types or ['general']
        self.stakeholder_types = stakeholder_types or []
        self.output_dir = None
        self.transcript_content = ""
        self.meeting_info = {}
        self.recommendations = {}
    
    async def process_phase1_essential(self) -> Path:
        """
        Phase 1: Generate only essential intelligence.
        Returns path to output directory.
        """
        logger.info("=" * 80)
        logger.info("PHASE 1: ESSENTIAL INTELLIGENCE GENERATION")
        logger.info("=" * 80)
        
        # Read transcript
        self.transcript_content = self.transcript_path.read_text(encoding='utf-8')
        logger.info(f"Transcript loaded: {len(self.transcript_content)} characters")
        
        # Extract meeting info
        await self._extract_meeting_info()
        
        # Create output directory
        self._create_output_directory()
        
        # Save transcript
        transcript_file = self.output_dir / "transcript.txt"
        transcript_file.write_text(self.transcript_content, encoding='utf-8')
        logger.info(f"Transcript saved: {transcript_file}")
        
        # Generate ONLY essential blocks
        essential_blocks = await self._generate_essential_blocks()
        
        # Generate content map
        await self._generate_content_map(essential_blocks)
        
        # Generate REVIEW_FIRST dashboard
        await self._generate_review_first(essential_blocks)
        
        # Recommend deliverables
        self.recommendations = await self._recommend_deliverables()
        
        # Save recommendations
        await self._save_recommendations()
        
        # Save minimal metadata
        await self._save_metadata(essential_blocks)
        
        logger.info(f"✅ Phase 1 complete: {self.output_dir}")
        logger.info(f"📋 Recommended {len(self.recommendations.get('recommended', []))} deliverables")
        
        # Send SMS notification
        await self._send_sms_notification()
        
        return self.output_dir
    
    async def _extract_meeting_info(self):
        """Extract basic meeting metadata from transcript using blocks module."""
        try:
            # Use the real meeting info extractor from blocks
            from blocks.meeting_info_extractor import extract_meeting_info
            
            extracted_info = await extract_meeting_info(self.transcript_content)
            
            # Merge with provided parameters
            self.meeting_info = {
                **extracted_info,
                "meeting_types": self.meeting_types,
                "stakeholder_types": self.stakeholder_types,
            }
            
            logger.info(f"Extracted {len(self.meeting_info.get('participants', []))} participants, "
                       f"primary stakeholder: {self.meeting_info.get('stakeholder_primary')}")
            
        except Exception as e:
            logger.error(f"Meeting info extraction failed: {e}, using fallback")
            # Fallback to basic extraction using llm_utils functions
            participants = extract_participants_from_transcript(self.transcript_content)
            companies = extract_company_names(self.transcript_content)
            
            stakeholder_primary = "unknown"
            if participants:
                stakeholder_primary = participants[-1].lower().replace(" ", "-")
            elif companies:
                stakeholder_primary = companies[0].lower().replace(" ", "-")
            
            self.meeting_info = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "participants": participants,
                "companies": companies,
                "meeting_types": self.meeting_types,
                "stakeholder_types": self.stakeholder_types,
                "stakeholder_primary": stakeholder_primary,
                "participants_count": len(participants),
                "duration_minutes": 0
            }
    
    def _create_output_directory(self):
        """Create structured output directory."""
        date = self.meeting_info.get("date", datetime.now().strftime("%Y-%m-%d"))
        time = self.meeting_info.get("time", datetime.now().strftime("%H%M")).replace(":", "")
        meeting_type = self.meeting_types[0] if self.meeting_types else "general"
        stakeholder = self.meeting_info.get("stakeholder_primary", "unknown")
        
        folder_name = f"{date}_{time}_{meeting_type}_{stakeholder}"
        output_dir = MEETINGS_DIR / folder_name
        
        # Handle duplicates
        counter = 1
        while output_dir.exists():
            folder_name = f"{date}_{time}_{meeting_type}_{stakeholder}_{counter}"
            output_dir = MEETINGS_DIR / folder_name
            counter += 1
        
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "DELIVERABLES").mkdir(exist_ok=True)
        (output_dir / "DELIVERABLES" / "blurbs").mkdir(exist_ok=True)
        (output_dir / "DELIVERABLES" / "one_pagers").mkdir(exist_ok=True)
        (output_dir / "INTELLIGENCE").mkdir(exist_ok=True)
        
        self.output_dir = output_dir
        logger.info(f"Output directory created: {output_dir}")
    
    async def _generate_essential_blocks(self) -> List[str]:
        """Generate essential content blocks using LLM-powered extractors."""
        blocks_generated = []
        intel_dir = self.output_dir / "INTELLIGENCE"
        
        try:
            # Import real block generators
            from blocks.action_items_extractor import generate_action_items
            from blocks.decisions_extractor import generate_decisions
            from blocks.key_insights_extractor import generate_key_insights
            
            # Generate action items using LLM
            logger.info("Generating action items...")
            try:
                success = await generate_action_items(
                    self.transcript_content,
                    self.meeting_info,
                    intel_dir
                )
                if success:
                    blocks_generated.append("action_items")
                    logger.info("✓ Action items generated")
            except Exception as e:
                logger.warning(f"Action items generation failed: {e}, using fallback")
                # Use fallback
                action_items = self._extract_action_items_simple()
                action_file = intel_dir / "action-items.md"
                action_file.write_text(action_items, encoding='utf-8')
                blocks_generated.append("action_items")
            
            # Generate decisions using LLM
            logger.info("Generating decisions...")
            try:
                success = await generate_decisions(
                    self.transcript_content,
                    self.meeting_info,
                    intel_dir
                )
                if success:
                    blocks_generated.append("decisions")
                    logger.info("✓ Decisions generated")
            except Exception as e:
                logger.warning(f"Decisions generation failed: {e}, using fallback")
                # Use fallback
                decisions = self._extract_decisions_simple()
                decisions_file = intel_dir / "decisions.md"
                decisions_file.write_text(decisions, encoding='utf-8')
                blocks_generated.append("decisions")
            
            # Generate key insights using LLM
            logger.info("Generating key insights...")
            try:
                success = await generate_key_insights(
                    self.transcript_content,
                    self.meeting_info,
                    intel_dir
                )
                if success:
                    blocks_generated.append("key_insights")
                    logger.info("✓ Key insights generated")
            except Exception as e:
                logger.warning(f"Key insights generation failed: {e}, using fallback")
                # Use fallback
                key_points = self._extract_key_points_simple()
                key_points_file = intel_dir / "key-points.md"
                key_points_file.write_text(key_points, encoding='utf-8')
                blocks_generated.append("key_points")
            
            return blocks_generated
            
        except Exception as e:
            logger.error(f"Essential block generation failed: {e}", exc_info=True)
            # Fall back to simple extraction
            action_items = self._extract_action_items_simple()
            action_file = intel_dir / "action-items.md"
            action_file.write_text(action_items, encoding='utf-8')
            blocks_generated.append("action_items")
            
            decisions = self._extract_decisions_simple()
            decisions_file = intel_dir / "decisions.md"
            decisions_file.write_text(decisions, encoding='utf-8')
            blocks_generated.append("decisions")
            
            key_points = self._extract_key_points_simple()
            key_points_file = intel_dir / "key-points.md"
            key_points_file.write_text(key_points, encoding='utf-8')
            blocks_generated.append("key_points")
            
            return blocks_generated
    
    def _extract_action_items_simple(self) -> str:
        """Simple extraction of action items (to be replaced with LLM)."""
        content_lower = self.transcript_content.lower()
        
        # Look for action-oriented phrases
        action_phrases = [
            "i'll", "i will", "we'll", "we will", "should", "need to", "going to",
            "follow up", "send", "share", "create", "schedule", "reach out"
        ]
        
        actions = []
        for line in self.transcript_content.split('\n'):
            line_lower = line.lower()
            if any(phrase in line_lower for phrase in action_phrases):
                # Extract speaker and action
                match = re.match(r'^([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*[:\-]\s*(.+)', line)
                if match:
                    speaker, text = match.groups()
                    actions.append(f"- [ ] **{speaker}**: {text.strip()}")
        
        if actions:
            return f"# Action Items\n\n" + "\n".join(actions[:10])  # Limit to 10
        return f"# Action Items\n\n*No explicit action items identified*"
    
    def _extract_decisions_simple(self) -> str:
        """Simple extraction of decisions (to be replaced with LLM)."""
        content_lower = self.transcript_content.lower()
        
        # Look for decision-oriented phrases
        decision_phrases = [
            "we decided", "decision", "agreed", "we'll go with", "let's do",
            "sounds good", "that works", "approved"
        ]
        
        decisions = []
        for line in self.transcript_content.split('\n'):
            line_lower = line.lower()
            if any(phrase in line_lower for phrase in decision_phrases):
                decisions.append(f"- {line.strip()}")
        
        if decisions:
            return f"# Decisions\n\n" + "\n".join(decisions[:10])
        return f"# Decisions\n\n*No explicit decisions identified*"
    
    def _extract_key_points_simple(self) -> str:
        """Extract key discussion points."""
        lines = [l.strip() for l in self.transcript_content.split('\n') if l.strip()]
        
        # Take first few substantive exchanges
        key_lines = []
        for line in lines[:20]:
            if len(line) > 50:  # Substantial content
                key_lines.append(f"- {line}")
        
        return f"# Key Discussion Points\n\n" + "\n".join(key_lines[:5])
    
    async def _generate_content_map(self, blocks_generated: List[str]):
        """Generate a scannable content map showing what was extracted."""
        from llm_utils import infer_parameters_from_transcript, validate_inferred_parameters
        
        participants = self.meeting_info.get('participants', [])
        companies = self.meeting_info.get('companies', [])
        meeting_type = self.meeting_types[0] if self.meeting_types else 'general'
        
        # Infer parameters for potential blurb
        try:
            blurb_params = await infer_parameters_from_transcript(
                self.transcript_content,
                self.meeting_info,
                "blurb"
            )
            validation = validate_inferred_parameters(
                blurb_params,
                self.transcript_content,
                "blurb"
            )
        except Exception as e:
            logger.warning(f"Parameter inference failed: {e}")
            blurb_params = {"intended_audience": "unknown", "persona": "unknown", "angle": "unknown"}
            validation = {"confidence": 0.0, "warnings": ["Inference failed"]}
        
        content_map = f"""# Content Map: {self.meeting_info.get('date', 'Unknown Date')}

## Extraction Summary

### Participants Detected
{chr(10).join(f'- **{p}**' for p in participants) if participants else '- No participants clearly identified'}

### Companies/Organizations Mentioned
{chr(10).join(f'- {c}' for c in companies) if companies else '- No companies clearly identified'}

### Meeting Classification
- **Type:** {meeting_type}
- **Declared Types:** {', '.join(self.meeting_types)}
- **Stakeholder Types:** {', '.join(self.stakeholder_types) if self.stakeholder_types else 'None'}

---

## Extracted Parameters (for deliverables)

### For Blurbs
- **Intended Audience:** {blurb_params.get('intended_audience', 'unknown')}
- **Persona/Tone:** {blurb_params.get('persona', 'unknown')}
- **Angle:** {blurb_params.get('angle', 'unknown')}

**Confidence Score:** {validation.get('confidence', 0):.0%}

{f"**⚠️ Warnings:**{chr(10)}" + chr(10).join(f"- {w}" for w in validation.get('warnings', [])) if validation.get('warnings') else ''}

---

## Generated Intelligence Blocks

{chr(10).join(f'✅ **{block}**' for block in blocks_generated)}

---

## Next Steps

Review `REVIEW_FIRST.md` for meeting summary and action items.

See `RECOMMENDED_DELIVERABLES.md` for suggested outputs you can request.

To generate deliverables, use:
```bash
N5: generate-deliverables "{self.output_dir.name}" --deliverables blurb,follow_up_email
```

---

**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        content_map_file = self.output_dir / "content-map.md"
        content_map_file.write_text(content_map, encoding='utf-8')
        logger.info(f"✓ Content map generated")
    
    async def _generate_review_first(self, blocks_generated: List[str]):
        """Generate REVIEW_FIRST dashboard."""
        intel_dir = self.output_dir / "INTELLIGENCE"
        
        # Load generated blocks
        action_items = ""
        decisions = ""
        key_points = ""
        
        if (intel_dir / "action-items.md").exists():
            action_items = (intel_dir / "action-items.md").read_text()
        if (intel_dir / "decisions.md").exists():
            decisions = (intel_dir / "decisions.md").read_text()
        if (intel_dir / "key-points.md").exists():
            key_points = (intel_dir / "key-points.md").read_text()
        
        participants_list = "\n".join(f"- {p}" for p in self.meeting_info.get('participants', []))
        companies_list = "\n".join(f"- {c}" for c in self.meeting_info.get('companies', []))
        
        review_first = f"""# Meeting Summary: {self.meeting_info.get('date')}

## 📋 Quick Stats

- **Meeting Type:** {', '.join(self.meeting_types)}
- **Participants:** {self.meeting_info.get('participants_count', 0)}
- **Date:** {self.meeting_info.get('date')}

## 👥 Participants

{participants_list if participants_list else '*No participants detected*'}

## 🏢 Companies Mentioned

{companies_list if companies_list else '*No companies detected*'}

---

## ✅ {action_items.split(chr(10))[0] if action_items else 'Action Items'}

{chr(10).join(action_items.split(chr(10))[2:10]) if action_items else '*See INTELLIGENCE/action-items.md*'}

---

## 🎯 {decisions.split(chr(10))[0] if decisions else 'Decisions'}

{chr(10).join(decisions.split(chr(10))[2:8]) if decisions else '*See INTELLIGENCE/decisions.md*'}

---

## 💡 {key_points.split(chr(10))[0] if key_points else 'Key Points'}

{chr(10).join(key_points.split(chr(10))[2:8]) if key_points else '*See INTELLIGENCE/key-points.md*'}

---

## Next Steps

1. Review full intelligence blocks in `INTELLIGENCE/` folder
2. Check `RECOMMENDED_DELIVERABLES.md` for suggested outputs
3. Generate deliverables as needed using `N5: generate-deliverables`

---

**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        review_file = self.output_dir / "REVIEW_FIRST.md"
        review_file.write_text(review_first, encoding='utf-8')
        logger.info(f"✓ REVIEW_FIRST dashboard generated")
    
    async def _recommend_deliverables(self) -> Dict[str, Any]:
        """Analyze meeting and recommend useful deliverables."""
        content_lower = self.transcript_content.lower()
        meeting_type = self.meeting_types[0] if self.meeting_types else 'general'
        
        recommendations = {
            "recommended": [],
            "optional": [],
            "not_recommended": []
        }
        
        # Blurb - recommended for external meetings
        if meeting_type in ['sales', 'fundraising', 'community_partnerships']:
            recommendations["recommended"].append({
                "type": "blurb",
                "reason": f"Useful for introducing Careerspan in {meeting_type} context",
                "confidence": 0.9,
                "estimated_time": "30 seconds"
            })
        else:
            recommendations["optional"].append({
                "type": "blurb",
                "reason": "Could be useful if planning to share with external parties",
                "confidence": 0.5,
                "estimated_time": "30 seconds"
            })
        
        # Follow-up email - recommended if action items exist
        intel_dir = self.output_dir / "INTELLIGENCE"
        action_items_file = intel_dir / "action-items.md"
        if action_items_file.exists():
            action_content = action_items_file.read_text()
            has_actions = '- [ ]' in action_content
            if has_actions:
                recommendations["recommended"].append({
                    "type": "follow_up_email",
                    "reason": "Action items were identified that should be communicated",
                    "confidence": 0.85,
                    "estimated_time": "30 seconds"
                })
        
        # One-pager - recommended for important external meetings
        if meeting_type in ['fundraising', 'sales'] and any(word in content_lower for word in ['partnership', 'proposal', 'investment']):
            recommendations["recommended"].append({
                "type": "one_pager_memo",
                "reason": "Strategic meeting discussing partnership/investment opportunities",
                "confidence": 0.8,
                "estimated_time": "45 seconds"
            })
        
        return recommendations
    
    async def _save_recommendations(self):
        """Save recommendations to file."""
        rec = self.recommendations
        
        content = f"""# Recommended Deliverables

Based on the meeting content and type, here are suggested deliverables:

## 🎯 Highly Recommended

{chr(10).join(f'''### {i+1}. {r['type'].replace('_', ' ').title()}
- **Reason:** {r['reason']}
- **Confidence:** {r['confidence']:.0%}
- **Generation Time:** ~{r['estimated_time']}
''' for i, r in enumerate(rec['recommended'])) if rec['recommended'] else '*None*'}

## 📋 Optional (May Be Useful)

{chr(10).join(f'''### {r['type'].replace('_', ' ').title()}
- **Reason:** {r['reason']}
- **Confidence:** {r['confidence']:.0%}
- **Generation Time:** ~{r['estimated_time']}
''' for r in rec['optional']) if rec['optional'] else '*None*'}

---

## How to Generate

To generate recommended deliverables:

```bash
# Generate all recommended
N5: generate-deliverables "{self.output_dir.name}" --recommended

# Generate specific deliverables
N5: generate-deliverables "{self.output_dir.name}" --deliverables blurb,follow_up_email

# Generate everything
N5: generate-deliverables "{self.output_dir.name}" --all
```

---

**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        rec_file = self.output_dir / "RECOMMENDED_DELIVERABLES.md"
        rec_file.write_text(content, encoding='utf-8')
        logger.info(f"✓ Recommendations saved")
    
    async def _save_metadata(self, blocks_generated: List[str]):
        """Save minimal metadata."""
        metadata = {
            "processing_version": "v2.1-standalone",
            "processing_date": datetime.now(timezone.utc).isoformat(),
            "meeting_date": self.meeting_info.get('date'),
            "meeting_types": self.meeting_types,
            "stakeholder_types": self.stakeholder_types,
            "participants": self.meeting_info.get('participants', []),
            "companies": self.meeting_info.get('companies', []),
            "blocks_generated_phase1": blocks_generated,
            "recommendations": self.recommendations,
            "phase1_complete": True,
            "deliverables_generated": False
        }
        
        metadata_file = self.output_dir / "_metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        logger.info(f"✓ Metadata saved")
    
    async def _send_sms_notification(self):
        """Send SMS notification to user."""
        try:
            # Count action items and decisions
            intel_dir = self.output_dir / "INTELLIGENCE"
            action_count = 0
            decision_count = 0
            
            if (intel_dir / "action-items.md").exists():
                content = (intel_dir / "action-items.md").read_text()
                action_count = content.count('- [ ]')
            
            if (intel_dir / "decisions.md").exists():
                content = (intel_dir / "decisions.md").read_text()
                decision_count = len([l for l in content.split('\n') if l.strip().startswith('- ')])
            
            # Get meeting name from folder
            meeting_name = self.output_dir.name
            # Clean up: remove date/time prefix
            parts = meeting_name.split('_')
            if len(parts) >= 4:
                meeting_name = ' '.join(parts[3:]).replace('-', ' ').title()
            
            # Get recommendations
            recommended = self.recommendations.get('recommended', [])
            rec_list = ', '.join([r['type'].replace('_', ' ') for r in recommended[:2]]) if recommended else 'none'
            
            # Build SMS message
            message = f"""Meeting processed: {meeting_name}

{action_count} action items, {decision_count} decisions

Recommended: {rec_list}

Review: https://va.zo.computer/workspace/{self.output_dir.relative_to(WORKSPACE)}

Reply "generate [deliverable names]" to create outputs"""
            
            logger.info(f"📱 SMS notification (simulated):")
            logger.info(f"{message}")
            logger.info("✓ SMS notification ready")
            
        except Exception as e:
            logger.error(f"Failed to prepare SMS notification: {e}")


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process meeting transcript (Phase 1 only - V2 Standalone)")
    parser.add_argument("transcript_path", help="Path to the meeting transcript file (.txt or .docx)")
    parser.add_argument("--type", nargs='*', default=[], help="Meeting type(s)")
    parser.add_argument("--stakeholder", nargs='*', default=[], help="Stakeholder type(s)")
    
    args = parser.parse_args()
    
    orchestrator = MeetingOrchestratorV2(
        args.transcript_path,
        args.type,
        args.stakeholder
    )
    
    output_dir = await orchestrator.process_phase1_essential()
    
    print()
    print("=" * 80)
    print("✅ PHASE 1 COMPLETE")
    print("=" * 80)
    print(f"📁 Output: {output_dir}")
    print(f"📋 Review: {output_dir / 'REVIEW_FIRST.md'}")
    print(f"🗺️  Content Map: {output_dir / 'content-map.md'}")
    print(f"💡 Recommendations: {output_dir / 'RECOMMENDED_DELIVERABLES.md'}")
    print()
    print("Next: Review outputs and request deliverables as needed")
    print()


if __name__ == "__main__":
    asyncio.run(main())
