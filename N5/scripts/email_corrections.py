#!/usr/bin/env python3
"""
Email Corrections — Extract factual corrections from draft vs sent email diffs
Facts-based validation system: sent email = ground truth
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher

# Ensure sibling scripts import when running as a standalone script
sys.path.insert(0, str(Path(__file__).parent))

# === V3 CONTENT LIBRARY IMPORT ===
from content_library_v3 import ContentLibraryV3
# === END V3 IMPORT ===

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


@dataclass
class Correction:
    """A factual correction extracted from draft vs sent diff"""
    category: str  # stakeholder | business_terms | content_library | tone | links
    field: str  # What field was corrected
    draft_value: str
    sent_value: str
    action: str  # update | deprecate | add | remove
    target: str  # Path to update (e.g., "Knowledge/crm/individuals/brin.md")
    auto_apply: bool  # Can this be auto-applied?
    confidence: float  # 0-1
    rationale: str
    context: Optional[str] = None


class EmailDiffEngine:
    """Extract semantic differences between draft and sent emails"""
    
    def __init__(self, content_library_path: Optional[Path] = None):
        """Initialize with ContentLibraryV3.
        
        content_library_path is kept for backward compatibility but ignored.
        """
        self.content_library = ContentLibraryV3()
    
    def extract_corrections(
        self,
        draft_email: str,
        sent_email: str,
        meeting_id: str,
        stakeholder_name: str
    ) -> List[Correction]:
        """
        Extract all factual corrections from draft vs sent diff
        """
        corrections = []
        
        # 1. Relationship depth corrections
        corrections.extend(self._detect_relationship_corrections(
            draft_email, sent_email, stakeholder_name
        ))
        
        # 2. Business terms corrections
        corrections.extend(self._detect_business_corrections(
            draft_email, sent_email, stakeholder_name
        ))
        
        # 3. Link corrections
        corrections.extend(self._detect_link_corrections(
            draft_email, sent_email
        ))
        
        # 4. Content library corrections (snippets deprecated/updated)
        corrections.extend(self._detect_content_corrections(
            draft_email, sent_email
        ))
        
        # 5. Tone adjustments (per-conversation)
        corrections.extend(self._detect_tone_corrections(
            draft_email, sent_email
        ))
        
        logger.info(f"Extracted {len(corrections)} corrections")
        return corrections
    
    def _detect_relationship_corrections(
        self,
        draft: str,
        sent: str,
        stakeholder: str
    ) -> List[Correction]:
        """Detect relationship depth misreads"""
        corrections = []
        
        # Pattern: Third-party references removed = closer relationship
        draft_mentions = re.findall(r'\b(\w+)\s+(mentioned|referred|recommended|suggested)\b', draft, re.I)
        sent_mentions = re.findall(r'\b(\w+)\s+(mentioned|referred|recommended|suggested)\b', sent, re.I)
        
        if len(draft_mentions) > len(sent_mentions):
            removed_refs = set(m[0] for m in draft_mentions) - set(m[0] for m in sent_mentions)
            if removed_refs:
                corrections.append(Correction(
                    category="stakeholder",
                    field="relationship_depth",
                    draft_value="warm_referral",
                    sent_value="existing_relationship",
                    action="update",
                    target=f"Knowledge/crm/individuals/{stakeholder.lower().replace(' ', '-')}.md",
                    auto_apply=True,
                    confidence=0.9,
                    rationale=f"Removed third-party reference to {', '.join(removed_refs)}. Indicates closer direct relationship.",
                    context=f"Draft mentioned: {', '.join(removed_refs)}"
                ))
        
        # Pattern: Formality reduced = friendlier relationship
        draft_formal = len(re.findall(r'\b(Dear|Sincerely|Best regards|Kind regards)\b', draft))
        sent_formal = len(re.findall(r'\b(Dear|Sincerely|Best regards|Kind regards)\b', sent))
        
        if draft_formal > sent_formal:
            corrections.append(Correction(
                category="stakeholder",
                field="formality_level",
                draft_value="professional",
                sent_value="casual",
                action="update",
                target=f"Knowledge/crm/individuals/{stakeholder.lower().replace(' ', '-')}.md",
                auto_apply=True,
                confidence=0.8,
                rationale="Reduced formality in sent email indicates more casual relationship",
                context=f"Draft: {draft_formal} formal markers, Sent: {sent_formal}"
            ))
        
        return corrections
    
    def _detect_business_corrections(
        self,
        draft: str,
        sent: str,
        stakeholder: str
    ) -> List[Correction]:
        """Detect business term corrections (pricing, product names, etc.)"""
        corrections = []
        
        # Pattern: Pricing changes
        draft_prices = re.findall(r'\$(\d+)(?:/month|/mo|per month)?', draft)
        sent_prices = re.findall(r'\$(\d+)(?:/month|/mo|per month| one-time)?', sent)
        
        if draft_prices and sent_prices and draft_prices != sent_prices:
            draft_recurring = 'month' in draft or '/mo' in draft
            sent_recurring = 'month' in sent or '/mo' in sent
            
            if draft_recurring and not sent_recurring:
                corrections.append(Correction(
                    category="business_terms",
                    field="pricing_model",
                    draft_value=f"${draft_prices[0]}/month",
                    sent_value=f"${sent_prices[0]} one-time",
                    action="update",
                    target=f"Knowledge/crm/individuals/{stakeholder.lower().replace(' ', '-')}.md",
                    auto_apply=False,  # Pricing is critical, require review
                    confidence=1.0,
                    rationale="CRITICAL: Pricing model corrected from recurring to one-time",
                    context="Blocks knowledge promotion until reviewed"
                ))
        
        # Pattern: Product/service name changes
        draft_caps = set(re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', draft))
        sent_caps = set(re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', sent))
        
        changed_terms = draft_caps - sent_caps
        if changed_terms:
            for term in changed_terms:
                if len(term) > 3 and term not in ['Dear', 'Best', 'Thanks', 'I', 'You']:
                    corrections.append(Correction(
                        category="business_terms",
                        field="product_terminology",
                        draft_value=term,
                        sent_value="[removed or replaced]",
                        action="update",
                        target="N5/prefs/communication/terminology.json",
                        auto_apply=False,
                        confidence=0.7,
                        rationale=f"Product term '{term}' removed/changed in sent email",
                        context="May indicate incorrect product reference"
                    ))
        
        return corrections
    
    def _detect_link_corrections(self, draft: str, sent: str) -> List[Correction]:
        """Detect link additions/removals/changes"""
        corrections = []
        
        # Extract URLs from both
        draft_urls = set(re.findall(r'https?://[^\s\)]+', draft))
        sent_urls = set(re.findall(r'https?://[^\s\)]+', sent))
        
        # Links removed
        removed = draft_urls - sent_urls
        for url in removed:
            corrections.append(Correction(
                category="links",
                field="link_set",
                draft_value=url,
                sent_value="[removed]",
                action="deprecate",
                target="N5/prefs/communication/content-library.json",
                auto_apply=False,
                confidence=0.8,
                rationale=f"Link removed in sent email: {url}",
                context="May be irrelevant or incorrect for this stakeholder"
            ))
        
        # Links added
        added = sent_urls - draft_urls
        for url in added:
            corrections.append(Correction(
                category="links",
                field="link_set",
                draft_value="[missing]",
                sent_value=url,
                action="add",
                target="N5/prefs/communication/content-library.json",
                auto_apply=True,
                confidence=0.9,
                rationale=f"Link added in sent email: {url}",
                context="Should be considered for content library"
            ))
        
        return corrections
    
    def _detect_content_corrections(self, draft: str, sent: str) -> List[Correction]:
        """Detect snippets that were removed/changed"""
        corrections: List[Correction] = []
        
        # Get all snippets from content library v3
        all_snippets = self.content_library.search(
            query=None,
            item_type="snippet",
            limit=1000,
        )
        
        for snippet in all_snippets:
            content = snippet.get("content") or ""
            if not content:
                continue
            in_draft = content in draft
            in_sent = content in sent
            
            # Snippet was in draft but removed from sent = deprecate
            if in_draft and not in_sent:
                corrections.append(Correction(
                    category="content_library",
                    field="snippet",
                    draft_value=snippet["id"],
                    sent_value="[removed]",
                    action="deprecate",
                    target=f"N5/prefs/communication/content-library.json#{snippet['id']}",
                    auto_apply=False,
                    confidence=0.7,
                    rationale=f"Snippet '{snippet.get('title', snippet['id'])}' removed in sent email",
                    context=f"Content: {content[:50]}..."
                ))
        
        return corrections
    
    def _detect_tone_corrections(self, draft: str, sent: str) -> List[Correction]:
        """Detect tone adjustments (per-conversation, not global)"""
        corrections = []
        
        # Measure sentence length (shorter = more casual)
        draft_sentences = re.split(r'[.!?]+', draft)
        sent_sentences = re.split(r'[.!?]+', sent)
        
        draft_avg_len = sum(len(s.split()) for s in draft_sentences if s.strip()) / max(len(draft_sentences), 1)
        sent_avg_len = sum(len(s.split()) for s in sent_sentences if s.strip()) / max(len(sent_sentences), 1)
        
        if abs(draft_avg_len - sent_avg_len) > 5:
            tone_shift = "more_concise" if sent_avg_len < draft_avg_len else "more_detailed"
            corrections.append(Correction(
                category="tone",
                field="sentence_length",
                draft_value=f"{draft_avg_len:.1f} words/sentence",
                sent_value=f"{sent_avg_len:.1f} words/sentence",
                action="update",
                target="[per-conversation variable]",
                auto_apply=True,
                confidence=0.6,
                rationale=f"Tone adjusted: {tone_shift}",
                context="Applies to this conversation only"
            ))
        
        return corrections
    
    def apply_corrections(
        self,
        corrections: List[Correction],
        dry_run: bool = False
    ) -> Dict:
        """Apply corrections to relevant files"""
        results = {
            "applied": [],
            "skipped": [],
            "blocked": [],
            "requires_review": []
        }
        
        for correction in corrections:
            if not correction.auto_apply:
                results["requires_review"].append(correction)
                logger.info(f"⚠ Requires review: [{correction.category}] {correction.field}")
                continue
            
            if dry_run:
                results["skipped"].append(correction)
                logger.info(f"[DRY RUN] Would apply: [{correction.category}] {correction.field}")
                continue
            
            # Apply correction based on category
            try:
                if correction.category == "stakeholder":
                    self._apply_stakeholder_correction(correction)
                elif correction.category == "content_library":
                    self._apply_content_library_correction(correction)
                elif correction.category == "links":
                    self._apply_link_correction(correction)
                
                results["applied"].append(correction)
                logger.info(f"✓ Applied: [{correction.category}] {correction.field}")
            except Exception as e:
                logger.error(f"Failed to apply correction: {e}")
                results["blocked"].append(correction)
        
        return results
    
    def _apply_stakeholder_correction(self, correction: Correction):
        """Apply correction to stakeholder CRM file"""
        target_file = Path("/home/workspace") / correction.target
        
        if not target_file.exists():
            logger.warning(f"Target file not found: {target_file}")
            return
        
        # Read file
        content = target_file.read_text()
        
        # Apply correction (simplified - would need more robust logic)
        if correction.field == "relationship_depth":
            content = re.sub(
                r'\*\*Relationship Depth:\*\* \w+',
                f'**Relationship Depth:** {correction.sent_value}',
                content
            )
        
        # Write back
        target_file.write_text(content)
        logger.info(f"Updated {target_file}")
    
    def _apply_content_library_correction(self, correction: Correction):
        """Apply correction to content library"""
        if correction.action == "deprecate":
            # Extract snippet ID from target
            snippet_id = correction.draft_value
            # Would call ContentLibrary.deprecate(snippet_id)
            logger.info(f"Would deprecate snippet: {snippet_id}")
    
    def _apply_link_correction(self, correction: Correction):
        """Apply link correction to content library"""
        if correction.action == "add":
            # Would add link to content library
            logger.info(f"Would add link: {correction.sent_value}")


def cmd_extract(args) -> int:
    """Extract corrections from draft vs sent email"""
    engine = EmailDiffEngine()
    
    # Read emails
    draft = Path(args.draft).read_text()
    sent = Path(args.sent).read_text()
    
    # Extract corrections
    corrections = engine.extract_corrections(
        draft_email=draft,
        sent_email=sent,
        meeting_id=args.meeting_id,
        stakeholder_name=args.stakeholder
    )
    
    # Display results
    print(f"\n{'='*70}")
    print(f"CORRECTIONS EXTRACTED: {len(corrections)}")
    print(f"{'='*70}\n")
    
    auto_apply = [c for c in corrections if c.auto_apply]
    requires_review = [c for c in corrections if not c.auto_apply]
    
    if auto_apply:
        print(f"✓ Auto-Apply ({len(auto_apply)}):")
        for c in auto_apply:
            print(f"  [{c.category}] {c.field}: {c.draft_value} → {c.sent_value}")
    
    if requires_review:
        print(f"\n⚠ Requires Review ({len(requires_review)}):")
        for c in requires_review:
            print(f"  [{c.category}] {c.field}: {c.draft_value} → {c.sent_value}")
            print(f"    Rationale: {c.rationale}")
    
    # Save to file
    if args.output:
        output = {
            "meeting_id": args.meeting_id,
            "stakeholder": args.stakeholder,
            "corrections": [asdict(c) for c in corrections],
            "summary": {
                "total": len(corrections),
                "auto_apply": len(auto_apply),
                "requires_review": len(requires_review)
            }
        }
        Path(args.output).write_text(json.dumps(output, indent=2))
        print(f"\n✓ Saved to: {args.output}")
    
    # Apply if requested
    if args.apply:
        results = engine.apply_corrections(corrections, dry_run=args.dry_run)
        print(f"\n{'='*70}")
        print("APPLICATION RESULTS")
        print(f"{'='*70}")
        print(f"Applied: {len(results['applied'])}")
        print(f"Requires Review: {len(results['requires_review'])}")
        print(f"Blocked: {len(results['blocked'])}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Email Factual Corrections")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Extract corrections
    extract_p = subparsers.add_parser('extract', help='Extract corrections from draft vs sent')
    extract_p.add_argument('--draft', required=True, help='Path to draft email')
    extract_p.add_argument('--sent', required=True, help='Path to sent email')
    extract_p.add_argument('--meeting-id', required=True)
    extract_p.add_argument('--stakeholder', required=True)
    extract_p.add_argument('--output', help='Save corrections JSON')
    extract_p.add_argument('--apply', action='store_true', help='Apply auto-apply corrections')
    extract_p.add_argument('--dry-run', action='store_true')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        return cmd_extract(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

