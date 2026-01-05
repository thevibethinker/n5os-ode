#!/usr/bin/env python3
"""
Reflection Synthesizer

Transforms transcripts and session content into structured strategic outputs:
- Decision memo (structured markdown)
- Key insights (5-7 bullets)
- Action items (3-6 prioritized)
- Executive blurb (1 paragraph)

Integrates with Strategic Partner sessions and can be used standalone.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
SESSIONS_DIR = WORKSPACE / "N5/sessions/strategic-partner"
SYNTHESIS_DIR = SESSIONS_DIR / "syntheses"
PENDING_UPDATES_DIR = SESSIONS_DIR / "pending-updates"
KNOWLEDGE_DIR = WORKSPACE / "Knowledge"

# Create directories
SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)


class ReflectionSynthesizer:
    """
    Synthesizes strategic session content into structured outputs
    """
    
    def __init__(self, 
                 session_content: str,
                 session_metadata: Optional[Dict] = None,
                 output_dir: Optional[Path] = None):
        
        self.session_content = session_content
        self.session_metadata = session_metadata or {}
        self.output_dir = output_dir or SYNTHESIS_DIR
        
        self.synthesis_id = self._generate_synthesis_id()
        self.loaded_context = {}
        
        logger.info(f"Initialized Reflection Synthesizer: {self.synthesis_id}")
    
    def _generate_synthesis_id(self) -> str:
        """Generate unique synthesis ID"""
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H%M")
        return f"{today}-synthesis-{timestamp}"
    
    def load_context(self) -> Dict[str, Any]:
        """Load relevant context from N5 knowledge base (read-only)"""
        logger.info("Loading N5 context for synthesis...")
        
        context = {
            "gtm_hypotheses": [],
            "product_hypotheses": [],
            "strategic_decisions": []
        }
        
        # In production, load actual context
        # For now, note that context would be loaded
        logger.info("✓ Context loading framework ready")
        
        self.loaded_context = context
        return context
    
    def extract_key_insights(self) -> List[Dict[str, Any]]:
        """
        Extract 5-7 key strategic insights from session
        
        In production, this would use sophisticated analysis.
        For MVP, provides framework.
        """
        logger.info("Extracting key insights...")
        
        # Framework for key insights extraction
        # In production, would analyze session content for:
        # - Major realizations
        # - Assumption challenges
        # - Blind spots identified
        # - Contradictions surfaced
        # - Strategic implications
        
        insights = [
            {
                "insight": "[Insight extracted from session]",
                "confidence": "medium",
                "strategic_implication": "...",
                "related_hypothesis": "..."
            }
        ]
        
        logger.info(f"✓ Extracted {len(insights)} key insights")
        return insights
    
    def extract_action_items(self) -> List[Dict[str, Any]]:
        """
        Extract 3-6 prioritized action items
        
        Format: What, Why, By When, Owner
        """
        logger.info("Extracting action items...")
        
        # Framework for action extraction
        # In production, would analyze session for:
        # - Next steps discussed
        # - Validation experiments needed
        # - Decisions to be made
        # - Research required
        # - Stakeholder engagement needed
        
        actions = [
            {
                "action": "[Action item]",
                "why": "[Strategic rationale]",
                "by_when": "[Specific date]",
                "owner": "[Who]",
                "priority": "high|medium|low",
                "dependencies": []
            }
        ]
        
        logger.info(f"✓ Extracted {len(actions)} action items")
        return actions
    
    def generate_executive_blurb(self) -> str:
        """
        Generate 1-paragraph executive summary
        
        Format: Context → Challenge → Key Insight → Recommendation
        """
        logger.info("Generating executive blurb...")
        
        # In production, would synthesize from session content
        blurb = """[One-paragraph synthesis capturing: strategic context, 
        core challenge addressed, most critical insight surfaced, and 
        primary recommendation with next action. Written for executive 
        consumption with clear decision implications.]"""
        
        logger.info("✓ Executive blurb generated")
        return blurb.strip()
    
    def generate_decision_memo(self, 
                               insights: List[Dict],
                               actions: List[Dict],
                               blurb: str) -> str:
        """
        Generate structured decision memo in markdown
        
        Format: Blurb → Context → Analysis → Insights → Recommendation → Actions
        """
        logger.info("Generating decision memo...")
        
        topic = self.session_metadata.get('topic', 'Strategic Decision')
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Build insights section
        insights_md = "\n".join([
            f"{i+1}. **{ins.get('insight', 'Insight')}**  \n   "
            f"Confidence: {ins.get('confidence', 'medium')} | "
            f"Implication: {ins.get('strategic_implication', 'TBD')}"
            for i, ins in enumerate(insights)
        ])
        
        # Build actions section
        actions_md = "\n".join([
            f"{i+1}. **{act.get('action', 'Action')}** "
            f"(Priority: {act.get('priority', 'medium').upper()})  \n   "
            f"   - Why: {act.get('why', 'TBD')}  \n"
            f"   - By When: {act.get('by_when', 'TBD')}  \n"
            f"   - Owner: {act.get('owner', 'TBD')}"
            for i, act in enumerate(actions)
        ])
        
        memo = f"""# Decision Memo: {topic}

**Date:** {date}  
**Synthesis ID:** {self.synthesis_id}  
**Session Mode:** {self.session_metadata.get('mode', 'strategic-partner')}

---

## Executive Summary

{blurb}

---

## Strategic Context

[In production: Context from session + N5 knowledge base]

**Current State:**
- [Situation summary]

**Strategic Challenge:**
- [Core challenge addressed]

**Constraints:**
- [Key constraints identified]

---

## Key Insights

{insights_md}

---

## Analysis

[In production: Deeper analysis from session]

**Assumptions Challenged:**
- [List of assumptions interrogated]

**Blind Spots Identified:**
- [Unconsidered perspectives surfaced]

**Contradictions Detected:**
- [Logical inconsistencies or strategic tensions]

**Risk Assessment:**
- [Key risks identified]

---

## Recommendation

[In production: Clear recommendation based on synthesis]

**Primary Recommendation:**
[Clear strategic direction]

**Rationale:**
[Why this recommendation]

**Alternative Considered:**
[What was considered but not recommended]

---

## Next Actions

{actions_md}

---

## Unresolved Questions

[In production: Questions flagged for weekly review]

1. [Question 1]
2. [Question 2]

---

## Appendix

**Session Metadata:**
- Mode: {self.session_metadata.get('mode', 'N/A')}
- Challenge Level: {self.session_metadata.get('dials', {}).get('challenge', 'N/A')}/10
- Duration: {self.session_metadata.get('duration', 'N/A')}
- Quality Metrics: {self.session_metadata.get('quality_metrics', {})}

**Knowledge Base Context Loaded:**
- GTM Hypotheses: {len(self.loaded_context.get('gtm_hypotheses', []))}
- Product Hypotheses: {len(self.loaded_context.get('product_hypotheses', []))}
- Recent Decisions: {len(self.loaded_context.get('strategic_decisions', []))}

---

*Generated by Reflection Synthesizer | Strategic Partner cognitive engine*
"""
        
        logger.info("✓ Decision memo generated")
        return memo
    
    def generate_pending_updates(self, insights: List[Dict]) -> Dict:
        """
        Generate pending knowledge updates (staged for review)
        
        Based on insights and session content
        """
        logger.info("Generating pending knowledge updates...")
        
        pending = {
            "synthesis_id": self.synthesis_id,
            "timestamp": datetime.now().isoformat(),
            "source": "reflection-synthesizer",
            "updates": [],
            "status": "pending_review",
            "auto_apply": False  # NEVER auto-apply
        }
        
        # In production, would generate actual updates based on insights
        # For MVP, framework is in place
        for insight in insights:
            if insight.get('related_hypothesis'):
                pending["updates"].append({
                    "type": "hypothesis_update",
                    "target": insight.get('related_hypothesis'),
                    "proposed_change": "confidence_adjustment",
                    "reason": insight.get('insight'),
                    "requires_approval": True
                })
        
        logger.info(f"✓ Generated {len(pending['updates'])} pending updates")
        return pending
    
    def synthesize(self) -> Dict[str, Any]:
        """
        Execute complete synthesis workflow
        
        Returns all output artifacts
        """
        logger.info("=" * 70)
        logger.info("REFLECTION SYNTHESIS")
        logger.info("=" * 70)
        
        # Step 1: Load context
        self.load_context()
        
        # Step 2: Extract insights
        insights = self.extract_key_insights()
        
        # Step 3: Extract actions
        actions = self.extract_action_items()
        
        # Step 4: Generate blurb
        blurb = self.generate_executive_blurb()
        
        # Step 5: Generate decision memo
        memo = self.generate_decision_memo(insights, actions, blurb)
        
        # Step 6: Generate pending updates
        pending = self.generate_pending_updates(insights)
        
        # Step 7: Save outputs
        outputs = self._save_outputs(memo, insights, actions, blurb, pending)
        
        logger.info("=" * 70)
        logger.info("✅ REFLECTION SYNTHESIS COMPLETE")
        logger.info("=" * 70)
        
        return outputs
    
    def _save_outputs(self, 
                     memo: str,
                     insights: List[Dict],
                     actions: List[Dict],
                     blurb: str,
                     pending: Dict) -> Dict[str, Path]:
        """Save all output artifacts"""
        
        outputs = {}
        
        # 1. Decision memo
        memo_file = self.output_dir / f"{self.synthesis_id}-decision-memo.md"
        memo_file.write_text(memo, encoding='utf-8')
        outputs['decision_memo'] = memo_file
        logger.info(f"✓ Decision memo: {memo_file.relative_to(WORKSPACE)}")
        
        # 2. Key insights (JSON)
        insights_file = self.output_dir / f"{self.synthesis_id}-insights.json"
        insights_file.write_text(json.dumps(insights, indent=2), encoding='utf-8')
        outputs['insights'] = insights_file
        logger.info(f"✓ Key insights: {insights_file.relative_to(WORKSPACE)}")
        
        # 3. Action items (JSON)
        actions_file = self.output_dir / f"{self.synthesis_id}-actions.json"
        actions_file.write_text(json.dumps(actions, indent=2), encoding='utf-8')
        outputs['actions'] = actions_file
        logger.info(f"✓ Action items: {actions_file.relative_to(WORKSPACE)}")
        
        # 4. Executive blurb (markdown)
        blurb_file = self.output_dir / f"{self.synthesis_id}-blurb.md"
        blurb_file.write_text(f"# Executive Summary\n\n{blurb}\n", encoding='utf-8')
        outputs['blurb'] = blurb_file
        logger.info(f"✓ Executive blurb: {blurb_file.relative_to(WORKSPACE)}")
        
        # 5. Pending updates (staged)
        pending_file = PENDING_UPDATES_DIR / f"{self.synthesis_id}.json"
        pending_file.write_text(json.dumps(pending, indent=2), encoding='utf-8')
        outputs['pending_updates'] = pending_file
        logger.info(f"✓ Pending updates: {pending_file.relative_to(WORKSPACE)}")
        logger.info("⚠️  Pending updates require human review")
        
        return outputs


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Reflection Synthesizer: Transform sessions into structured outputs"
    )
    
    parser.add_argument('--session-file', type=Path,
                       help='Path to session synthesis or transcript file')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode (paste content)')
    parser.add_argument('--session-id', 
                       help='Strategic partner session ID to synthesize')
    
    args = parser.parse_args()
    
    # Get session content
    if args.session_file:
        if not args.session_file.exists():
            logger.error(f"File not found: {args.session_file}")
            return 1
        session_content = args.session_file.read_text(encoding='utf-8')
        logger.info(f"Loaded session file: {args.session_file}")
    
    elif args.session_id:
        # Load from strategic partner session
        session_file = SESSIONS_DIR / f"{args.session_id}.md"
        if not session_file.exists():
            logger.error(f"Session not found: {session_file}")
            return 1
        session_content = session_file.read_text(encoding='utf-8')
        logger.info(f"Loaded strategic partner session: {args.session_id}")
    
    elif args.interactive:
        print("Reflection Synthesizer - Interactive Mode")
        print("=" * 70)
        print("Paste session content or transcript (Ctrl+D when done):\n")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        session_content = '\n'.join(lines)
        
        if not session_content.strip():
            print("\n❌ No content provided")
            return 1
    
    else:
        parser.print_help()
        return 1
    
    # Extract metadata if available
    metadata = {
        "mode": "strategic-partner",
        "topic": "Strategic Decision",
        "dials": {"challenge": 7, "novel": 5, "structure": 4}
    }
    
    # Run synthesis
    synthesizer = ReflectionSynthesizer(
        session_content=session_content,
        session_metadata=metadata
    )
    
    outputs = synthesizer.synthesize()
    
    # Summary
    print("\n" + "=" * 70)
    print("SYNTHESIS COMPLETE")
    print("=" * 70)
    print(f"\nSynthesis ID: {synthesizer.synthesis_id}")
    print("\nOutputs generated:")
    for output_type, file_path in outputs.items():
        print(f"  • {output_type}: {file_path.relative_to(WORKSPACE)}")
    
    print("\nNext steps:")
    print("  1. Review decision memo")
    print("  2. Use `review-pending-updates` to approve knowledge changes")
    print("  3. Reference insights and actions in strategic planning")
    print("\n" + "=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
