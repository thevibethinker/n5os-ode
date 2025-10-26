#!/usr/bin/env python3
"""
Weekly Stakeholder Review Generator

Generates comprehensive weekly stakeholder review digest with:
- New contacts discovered (past 7 days)
- Tag suggestions with confidence scores
- Enrichment highlights (for critical priority)
- Strategic insights and Careerspan relevance

Part of: N5 Stakeholder Auto-Tagging System (Phase 2B)
Version: 1.0.0
"""

import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
log = logging.getLogger(__name__)

# Paths
N5_ROOT = Path("/home/workspace/N5")
DIGESTS_DIR = N5_ROOT / "digests"
STAGING_DIR = N5_ROOT / "records" / "crm" / "staging"


class WeeklyStakeholderReview:
    """
    Generate weekly stakeholder review digest
    """
    
    def __init__(
        self,
        email_scanner=None,
        pattern_analyzer=None,
        enricher=None
    ):
        """
        Initialize review generator
        
        Args:
            email_scanner: scan_meeting_emails module
            pattern_analyzer: pattern_analyzer module
            enricher: enrich_stakeholder_contact module
        """
        self.scanner = email_scanner
        self.analyzer = pattern_analyzer
        self.enricher = enricher
        
        DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_review(self, week_start_date: Optional[str] = None) -> Dict:
        """
        Main function: generate weekly stakeholder review
        
        Args:
            week_start_date: ISO date string (defaults to last Sunday)
            
        Returns:
            dict with review_path, contacts_reviewed, stats
        """
        log.info("Starting weekly stakeholder review generation")
        
        # Calculate week date range
        if not week_start_date:
            # Default: last Sunday
            today = datetime.now()
            week_start_date = today.strftime('%Y-%m-%d')  # Simplified for now
        
        # Step 1: Discover new contacts (email scanner)
        log.info("Scanning Gmail for new contacts...")
        discovered = self._discover_new_contacts()
        
        # Step 2: Enrich critical priority contacts
        log.info("Enriching critical priority contacts...")
        enriched = self._enrich_contacts(discovered)
        
        # Step 3: Analyze patterns and suggest tags
        log.info("Analyzing patterns and suggesting tags...")
        analyzed = self._analyze_and_tag(enriched)
        
        # Step 4: Generate markdown digest
        log.info("Generating review digest...")
        digest_path = self._generate_digest_markdown(analyzed, week_start_date)
        
        # Step 5: Summary stats
        stats = {
            'new_contacts': len(discovered),
            'enriched_contacts': len(enriched),
            'high_confidence_tags': sum(1 for c in analyzed for t in c.get('suggested_tags', []) if t.get('confidence', 0) > 0.80),
            'review_path': str(digest_path)
        }
        
        log.info(f"Weekly review complete: {stats['new_contacts']} new contacts")
        return stats
    
    def _discover_new_contacts(self) -> List[Dict]:
        """
        Discover new external contacts from past 7 days
        
        Returns:
            List of discovered contact dicts
        """
        if not self.scanner:
            log.warning("Email scanner not available")
            return []
        
        # Use email scanner to find contacts
        # For now, load from staging directory
        discovered = []
        
        if STAGING_DIR.exists():
            for filepath in STAGING_DIR.glob("*.json"):
                if filepath.name.startswith('.'):
                    continue
                
                try:
                    with open(filepath, 'r') as f:
                        contact = json.load(f)
                        discovered.append(contact)
                except Exception as e:
                    log.warning(f"Error loading {filepath.name}: {e}")
        
        return discovered
    
    def _enrich_contacts(self, contacts: List[Dict]) -> List[Dict]:
        """
        Enrich critical priority contacts only
        
        Binary enrichment:
        - Critical → Full (web + LinkedIn + research)
        - Non-critical → Basic only (domain)
        """
        enriched = []
        
        for contact in contacts:
            # Determine priority (will be inferred by pattern analyzer)
            # For now, use stakeholder type to determine
            inferred_type = contact.get('inferred_stakeholder_type', 'prospect')
            
            # Critical types: investor, advisor, customer
            is_critical = inferred_type in ['investor', 'advisor', 'customer']
            
            if is_critical:
                log.info(f"Enriching critical contact: {contact.get('name')}")
                # Would call enricher.enrich_contact() here
                contact['enrichment_level'] = 'full'
            else:
                log.info(f"Basic enrichment: {contact.get('name')}")
                contact['enrichment_level'] = 'basic'
            
            enriched.append(contact)
        
        return enriched
    
    def _analyze_and_tag(self, contacts: List[Dict]) -> List[Dict]:
        """
        Run pattern analyzer on contacts, generate tag suggestions
        """
        analyzed = []
        
        for contact in contacts:
            if self.analyzer:
                # Run pattern analyzer
                suggested_tags = self.analyzer.analyze_contact(
                    contact_data=contact,
                    email_context=contact.get('email_context'),
                    enrichment_data=contact.get('enrichment_data')
                )
                contact['suggested_tags'] = suggested_tags
            else:
                contact['suggested_tags'] = []
            
            analyzed.append(contact)
        
        return analyzed
    
    def _generate_digest_markdown(self, contacts: List[Dict], week_date: str) -> Path:
        """
        Generate markdown digest for V's review
        
        Args:
            contacts: Analyzed contacts with tag suggestions
            week_date: Week identifier
            
        Returns:
            Path to generated digest
        """
        digest_path = DIGESTS_DIR / f"weekly-stakeholder-review-{week_date}.md"
        
        # Build digest content
        content = self._build_digest_content(contacts, week_date)
        
        # Write to file
        with open(digest_path, 'w') as f:
            f.write(content)
        
        log.info(f"Digest written to: {digest_path}")
        return digest_path
    
    def _build_digest_content(self, contacts: List[Dict], week_date: str) -> str:
        """Build markdown content for digest"""
        
        lines = []
        lines.append(f"# Weekly Stakeholder Review — Week of {week_date}")
        lines.append("")
        lines.append(f"**New contacts discovered:** {len(contacts)}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}")
        lines.append("")
        
        if not contacts:
            lines.append("No new contacts discovered this week.")
            lines.append("")
            lines.append("**Next review:** Next Sunday at 6:00 PM ET")
            return '\n'.join(lines)
        
        lines.append("**Action required:** Review suggested tags below")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## New Contacts ({len(contacts)})")
        lines.append("")
        
        # Generate section for each contact
        for i, contact in enumerate(contacts, 1):
            lines.append(self._format_contact_section(i, contact))
            lines.append("")
        
        # Summary statistics
        lines.append("---")
        lines.append("")
        lines.append("## Summary Statistics")
        lines.append("")
        lines.append(self._format_statistics(contacts))
        lines.append("")
        
        # Instructions
        lines.append("---")
        lines.append("")
        lines.append("## How to Respond")
        lines.append("")
        lines.append("**Option 1: Bulk approve**")
        lines.append('Reply: "Approve all"')
        lines.append("")
        lines.append("**Option 2: Selective approval**")
        lines.append('Reply: "Approve #1, #3. Edit #2: change to #stakeholder:customer. Skip #4."')
        lines.append("")
        lines.append("**Option 3: Add notes**")
        lines.append('Reply: "Approve all. Note: Contact #2 is actually high priority."')
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"**Next review:** Next Sunday at 6:00 PM ET")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _format_contact_section(self, index: int, contact: Dict) -> str:
        """Format individual contact section"""
        lines = []
        
        name = contact.get('name', 'Unknown')
        company = contact.get('company', 'Unknown')
        email = contact.get('email', 'Unknown')
        
        lines.append(f"### {index}. {name} ({company})")
        lines.append("")
        lines.append(f"**Email:** {email}")
        
        # LinkedIn if available
        if contact.get('linkedin_url'):
            lines.append(f"**LinkedIn:** [{name}]({contact['linkedin_url']})")
        
        # Role if available
        if contact.get('linkedin_data', {}).get('current_role'):
            lines.append(f"**Current role:** {contact['linkedin_data']['current_role']}")
        
        lines.append("")
        lines.append("**Suggested tags:**")
        
        # List tags with confidence levels
        tags = contact.get('suggested_tags', [])
        for tag_info in tags:
            tag = tag_info.get('tag', '')
            confidence = tag_info.get('confidence', 0)
            conf_label = self._confidence_label(confidence)
            
            lines.append(f"- {conf_label} `{tag}` ({conf_label} confidence - {confidence*100:.0f}%)")
        
        lines.append("")
        lines.append("**Reasoning:**")
        
        # Group reasoning by tag
        for tag_info in tags:
            tag = tag_info.get('tag', '')
            reasoning = tag_info.get('reasoning', 'No reasoning provided')
            lines.append(f"- **{tag}:** {reasoning}")
        
        lines.append("")
        
        # Enrichment highlights (if critical)
        if contact.get('enrichment_level') == 'full':
            lines.append("**Enrichment highlights:**")
            lines.append("*(Full enrichment data would appear here)*")
            lines.append("")
        
        lines.append(f"**Action:** Approve all | Edit tags | Skip")
        
        return '\n'.join(lines)
    
    def _format_statistics(self, contacts: List[Dict]) -> str:
        """Format summary statistics"""
        lines = []
        
        # Count by stakeholder type
        type_counts = {}
        for contact in contacts:
            tags = contact.get('suggested_tags', [])
            for tag_info in tags:
                tag = tag_info.get('tag', '')
                if tag.startswith('#stakeholder:'):
                    type_counts[tag] = type_counts.get(tag, 0) + 1
        
        lines.append("**Stakeholder types:**")
        for tag, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            pct = (count / len(contacts)) * 100
            lines.append(f"- {tag}: {count} ({pct:.0f}%)")
        
        lines.append("")
        
        # Confidence distribution
        high_conf = sum(1 for c in contacts for t in c.get('suggested_tags', []) if t.get('confidence', 0) >= 0.80)
        med_conf = sum(1 for c in contacts for t in c.get('suggested_tags', []) if 0.60 <= t.get('confidence', 0) < 0.80)
        low_conf = sum(1 for c in contacts for t in c.get('suggested_tags', []) if t.get('confidence', 0) < 0.60)
        
        lines.append("**Confidence distribution:**")
        lines.append(f"- High confidence (>80%): {high_conf} tags")
        lines.append(f"- Medium confidence (60-80%): {med_conf} tags")
        lines.append(f"- Low confidence (<60%): {low_conf} tags")
        
        return '\n'.join(lines)
    
    def _confidence_label(self, confidence: float) -> str:
        """Convert confidence score to label with emoji"""
        if confidence >= 0.80:
            return "✅"
        elif confidence >= 0.60:
            return "⚠️"
        else:
            return "❓"


def run_weekly_review_with_zo_tools(
    use_app_gmail,
    use_app_google_calendar,
    web_search,
    view_webpage
):
    """
    Run weekly stakeholder review with Zo's API tools
    
    This is the entry point for the scheduled task
    """
    log.info("Weekly stakeholder review triggered")
    
    # Import modules
    from scan_meeting_emails import run_scan_with_zo_tools
    from pattern_analyzer import StakeholderPatternAnalyzer
    
    # Step 1: Scan emails (past 7 days)
    log.info("Step 1: Scanning Gmail for new contacts...")
    scan_summary = run_scan_with_zo_tools(
        use_app_gmail,
        use_app_google_calendar,
        lookback_days=7
    )
    
    # Step 2: Load staged contacts
    log.info("Step 2: Loading staged contacts...")
    staged_contacts = []
    if STAGING_DIR.exists():
        for filepath in STAGING_DIR.glob("*.json"):
            if filepath.name.startswith('.'):
                continue
            try:
                with open(filepath, 'r') as f:
                    contact = json.load(f)
                    staged_contacts.append(contact)
            except Exception as e:
                log.warning(f"Error loading {filepath.name}: {e}")
    
    # Step 3: Analyze and tag
    log.info(f"Step 3: Analyzing {len(staged_contacts)} contacts...")
    analyzer = StakeholderPatternAnalyzer()
    
    analyzed_contacts = []
    for contact in staged_contacts:
        suggested_tags = analyzer.analyze_contact(
            contact_data=contact,
            email_context=contact.get('email_context'),
            enrichment_data=contact.get('enrichment_data')
        )
        contact['suggested_tags'] = suggested_tags
        analyzed_contacts.append(contact)
    
    # Step 4: Generate digest
    log.info("Step 4: Generating weekly review digest...")
    review_gen = WeeklyStakeholderReview()
    
    week_date = datetime.now().strftime('%Y-%m-%d')
    digest_path = review_gen._generate_digest_markdown(analyzed_contacts, week_date)
    
    log.info(f"Weekly review complete: {digest_path}")
    
    return {
        'digest_path': str(digest_path),
        'new_contacts': len(analyzed_contacts),
        'scan_summary': scan_summary
    }


def main():
    """CLI entry point"""
    print("Weekly Stakeholder Review Generator v1.0.0")
    print("=" * 60)
    print("Part of: N5 Stakeholder Auto-Tagging System (Phase 2B)")
    print("")
    print("This script generates comprehensive weekly stakeholder reviews.")
    print("")
    print("Workflow:")
    print("  1. Scan Gmail for new contacts (past 7 days)")
    print("  2. Enrich critical priority contacts (web + LinkedIn + research)")
    print("  3. Analyze patterns and suggest tags")
    print("  4. Generate review digest for V's approval")
    print("")
    print("Scheduled: Sundays at 6:00 PM ET")
    print("Notification: SMS text when complete")
    print("")
    print(f"Output directory: {DIGESTS_DIR}")
    print("")


if __name__ == "__main__":
    main()
