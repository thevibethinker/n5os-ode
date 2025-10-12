#!/usr/bin/env python3
"""
Stakeholder Pattern Analyzer

Analyzes email communication patterns and enrichment data to automatically
suggest stakeholder tags with confidence scores.

Part of: N5 Stakeholder Auto-Tagging System (Phase 1B)
Version: 1.0.0
"""

import logging
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
log = logging.getLogger(__name__)

# Paths
N5_ROOT = Path("/home/workspace/N5")
CONFIG_DIR = N5_ROOT / "config"


class StakeholderPatternAnalyzer:
    """
    Analyze email patterns and enrichment data to suggest stakeholder tags
    """
    
    def __init__(self):
        """Initialize pattern analyzer with config"""
        self.tag_taxonomy = self._load_config("tag_taxonomy.json")
        self.stakeholder_rules = self._load_config("stakeholder_rules.json")
        self.enrichment_settings = self._load_config("enrichment_settings.json")
        
        # Confidence thresholds
        self.high_confidence = 0.80
        self.medium_confidence = 0.60
    
    def analyze_contact(
        self,
        contact_data: Dict[str, Any],
        email_context: Optional[Dict] = None,
        enrichment_data: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Main analysis function: generate tag suggestions
        
        Args:
            contact_data: Basic contact info (name, email, company)
            email_context: Email patterns (frequency, subjects, timing)
            enrichment_data: Web search, LinkedIn, research data
            
        Returns:
            List of tag dicts with tag, confidence, reasoning
        """
        log.info(f"Analyzing contact: {contact_data.get('name')} ({contact_data.get('email')})")
        
        suggested_tags = []
        
        # 1. Stakeholder type (primary classification)
        stakeholder_tag = self._infer_stakeholder_type(contact_data, email_context, enrichment_data)
        if stakeholder_tag:
            suggested_tags.append(stakeholder_tag)
        
        # 2. Relationship status
        relationship_tag = self._infer_relationship_status(email_context)
        if relationship_tag:
            suggested_tags.append(relationship_tag)
        
        # 3. Priority (binary: critical vs. non-critical)
        priority_tag = self._infer_priority(stakeholder_tag, enrichment_data)
        if priority_tag:
            suggested_tags.append(priority_tag)
        
        # 4. Engagement status
        engagement_tag = self._infer_engagement(email_context)
        if engagement_tag:
            suggested_tags.append(engagement_tag)
        
        # 5. Context/industry
        context_tags = self._infer_context(contact_data, enrichment_data)
        suggested_tags.extend(context_tags)
        
        # 6. Check for dual classification
        dual_tag = self._check_dual_classification(contact_data, email_context, enrichment_data)
        if dual_tag:
            suggested_tags.append(dual_tag)
        
        log.info(f"Generated {len(suggested_tags)} tag suggestions for {contact_data.get('name')}")
        return suggested_tags
    
    def _infer_stakeholder_type(
        self,
        contact_data: Dict,
        email_context: Optional[Dict],
        enrichment_data: Optional[Dict]
    ) -> Optional[Dict[str, Any]]:
        """
        Infer primary stakeholder type
        
        Signal priorities:
        1. LinkedIn job title (highest confidence)
        2. Email domain (high confidence for known domains)
        3. Email keywords (medium confidence)
        4. Company type from web search (medium confidence)
        """
        
        # Check LinkedIn data (highest priority)
        if enrichment_data and enrichment_data.get('linkedin_data'):
            linkedin = enrichment_data['linkedin_data']
            current_role = linkedin.get('current_role', '').lower()
            
            # Investor signals
            if any(kw in current_role for kw in ['investor', 'partner', 'vc', 'venture', 'general partner', 'gp']):
                return {
                    'tag': '#stakeholder:investor',
                    'confidence': 0.95,
                    'reasoning': f'LinkedIn role confirms investor: "{linkedin.get("current_role")}"',
                    'source': 'linkedin_job_title'
                }
            
            # Advisor signals (executive, former leader)
            if any(kw in current_role for kw in ['advisor', 'consultant', 'coach', 'former']) and \
               any(kw in current_role for kw in ['ceo', 'cto', 'vp', 'director', 'head of']):
                return {
                    'tag': '#stakeholder:advisor',
                    'confidence': 0.85,
                    'reasoning': f'LinkedIn role suggests advisor: "{linkedin.get("current_role")}"',
                    'source': 'linkedin_job_title'
                }
            
            # Community leader signals
            if any(kw in current_role for kw in ['community', 'network', 'association', 'nonprofit']):
                return {
                    'tag': '#stakeholder:community',
                    'confidence': 0.85,
                    'reasoning': f'LinkedIn role indicates community focus: "{linkedin.get("current_role")}"',
                    'source': 'linkedin_job_title'
                }
        
        # Check domain (known VC firms, recruiting companies)
        domain = contact_data.get('domain', '').lower()
        
        vc_domains = {
            'a16z.com', 'sequoiacap.com', 'greylock.com', 'bessemer.com',
            'accel.com', 'nea.com', 'khoslaventures.com', 'benchmark.com',
            'lightspeedvp.com', 'generalcatalyst.com', 'foundationcapital.com'
        }
        
        if domain in vc_domains:
            return {
                'tag': '#stakeholder:investor',
                'confidence': 0.90,
                'reasoning': f'Known VC firm domain: {domain}',
                'source': 'domain_analysis'
            }
        
        # Check for recruiting/HR companies
        if any(kw in domain for kw in ['recruiting', 'talent', 'hire', 'staffing', 'jobs']):
            return {
                'tag': '#stakeholder:job_seeker',
                'confidence': 0.70,
                'reasoning': f'Recruiting/HR company domain: {domain}',
                'source': 'domain_analysis'
            }
        
        # Check email keywords (subject lines, body content)
        if email_context and email_context.get('subjects'):
            subjects = ' '.join(email_context['subjects']).lower()
            
            # Partnership keywords
            if any(kw in subjects for kw in ['partnership', 'collaborate', 'partner with']):
                return {
                    'tag': '#stakeholder:partner:collaboration',
                    'confidence': 0.75,
                    'reasoning': 'Email subjects discuss partnership/collaboration',
                    'source': 'email_keywords'
                }
            
            # Investment keywords
            if any(kw in subjects for kw in ['investment', 'funding', 'series', 'round']):
                return {
                    'tag': '#stakeholder:investor',
                    'confidence': 0.80,
                    'reasoning': 'Email subjects discuss investment/funding',
                    'source': 'email_keywords'
                }
            
            # Advisory/coaching keywords
            if any(kw in subjects for kw in ['coaching', 'advisory', 'advice', 'session']):
                return {
                    'tag': '#stakeholder:advisor',
                    'confidence': 0.75,
                    'reasoning': 'Email subjects discuss coaching/advisory relationship',
                    'source': 'email_keywords'
                }
        
        # Default: prospect (needs more information)
        return {
            'tag': '#stakeholder:prospect',
            'confidence': 0.50,
            'reasoning': 'Insufficient data to determine specific type, defaulting to prospect',
            'source': 'default'
        }
    
    def _infer_relationship_status(self, email_context: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """
        Infer relationship status from email patterns
        
        Signals:
        - Email frequency (warm vs. cold)
        - Time since last contact (active vs. dormant)
        - Number of exchanges (new vs. established)
        """
        if not email_context:
            return {
                'tag': '#relationship:new',
                'confidence': 0.90,
                'reasoning': 'First discovery, no email history available',
                'source': 'default'
            }
        
        email_count = email_context.get('email_count', 0)
        last_contact_days = email_context.get('days_since_last_contact', 0)
        
        # New contact (1-2 emails)
        if email_count <= 2:
            return {
                'tag': '#relationship:new',
                'confidence': 1.0,
                'reasoning': f'First contact or limited exchanges ({email_count} emails)',
                'source': 'email_frequency'
            }
        
        # Warm contact (5+ emails, recent activity)
        if email_count >= 5 and last_contact_days <= 14:
            return {
                'tag': '#relationship:warm',
                'confidence': 0.85,
                'reasoning': f'{email_count} emails in past 2 weeks, active engagement',
                'source': 'email_frequency'
            }
        
        # Active collaboration (10+ emails, ongoing)
        if email_count >= 10:
            return {
                'tag': '#relationship:active',
                'confidence': 0.90,
                'reasoning': f'{email_count} total emails, ongoing relationship',
                'source': 'email_frequency'
            }
        
        # Cold (no recent contact)
        if last_contact_days > 30:
            return {
                'tag': '#relationship:cold',
                'confidence': 0.85,
                'reasoning': f'No contact in {last_contact_days} days',
                'source': 'email_recency'
            }
        
        # Dormant (past relationship, long gap)
        if email_count > 5 and last_contact_days > 90:
            return {
                'tag': '#relationship:dormant',
                'confidence': 0.80,
                'reasoning': f'Previous relationship ({email_count} emails) but {last_contact_days} days inactive',
                'source': 'email_frequency_and_recency'
            }
        
        # Default: warm (some activity, not cold)
        return {
            'tag': '#relationship:warm',
            'confidence': 0.65,
            'reasoning': f'{email_count} emails, moderate engagement',
            'source': 'email_frequency'
        }
    
    def _infer_priority(
        self,
        stakeholder_tag: Optional[Dict],
        enrichment_data: Optional[Dict]
    ) -> Optional[Dict[str, Any]]:
        """
        Infer priority (BINARY: critical vs. non-critical)
        
        Critical auto-assigned to:
        - Investors (always)
        - Advisors (always)
        - Customers (always)
        """
        if not stakeholder_tag:
            return None
        
        stakeholder_type = stakeholder_tag['tag']
        
        # Auto-assign critical priority
        critical_types = [
            '#stakeholder:investor',
            '#stakeholder:advisor',
            '#stakeholder:customer'
        ]
        
        if stakeholder_type in critical_types:
            return {
                'tag': '#priority:critical',
                'confidence': 0.95,
                'reasoning': f'Auto-assigned critical priority for {stakeholder_type} type',
                'source': 'auto_inheritance'
            }
        
        # All others: non-critical
        return {
            'tag': '#priority:non-critical',
            'confidence': 0.90,
            'reasoning': f'Standard priority for {stakeholder_type} type',
            'source': 'default'
        }
    
    def _infer_engagement(self, email_context: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """
        Infer engagement status from email response patterns
        """
        if not email_context:
            return None
        
        avg_response_hours = email_context.get('avg_response_time_hours', None)
        
        if avg_response_hours is None:
            # Not enough data
            return None
        
        # Responsive (<4 hours)
        if avg_response_hours < 4:
            return {
                'tag': '#engagement:responsive',
                'confidence': 0.85,
                'reasoning': f'Quick responses (avg {avg_response_hours:.1f} hours)',
                'source': 'email_response_time'
            }
        
        # Slow (>24 hours)
        if avg_response_hours > 24:
            return {
                'tag': '#engagement:slow',
                'confidence': 0.80,
                'reasoning': f'Slow responses (avg {avg_response_hours:.1f} hours)',
                'source': 'email_response_time'
            }
        
        return None  # Normal response time, no tag needed
    
    def _infer_context(
        self,
        contact_data: Dict,
        enrichment_data: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Infer context/industry tags
        
        Returns multiple context tags if applicable
        """
        context_tags = []
        
        # Check LinkedIn industry
        if enrichment_data and enrichment_data.get('linkedin_data'):
            industry = enrichment_data['linkedin_data'].get('industry', '').lower()
            
            industry_mapping = {
                'venture capital': ('#context:venture_capital', 0.95),
                'human resources': ('#context:hr_tech', 0.85),
                'recruiting': ('#context:hr_tech', 0.85),
                'software': ('#context:saas', 0.80),
                'enterprise software': ('#context:enterprise', 0.90),
                'nonprofit': ('#context:nonprofit', 0.95)
            }
            
            for keyword, (tag, confidence) in industry_mapping.items():
                if keyword in industry:
                    context_tags.append({
                        'tag': tag,
                        'confidence': confidence,
                        'reasoning': f'LinkedIn industry: {enrichment_data["linkedin_data"].get("industry")}',
                        'source': 'linkedin_industry'
                    })
                    break  # Take first match
        
        # Check company size for enterprise context
        if enrichment_data and enrichment_data.get('linkedin_data'):
            company_size = enrichment_data['linkedin_data'].get('company_size', '').lower()
            
            if any(indicator in company_size for indicator in ['1000+', '10,000+', 'enterprise', 'fortune']):
                context_tags.append({
                    'tag': '#context:enterprise',
                    'confidence': 0.90,
                    'reasoning': f'Large company size: {enrichment_data["linkedin_data"].get("company_size")}',
                    'source': 'linkedin_company_size'
                })
        
        # Check domain for HR tech signals
        domain = contact_data.get('domain', '').lower()
        if any(kw in domain for kw in ['career', 'talent', 'recruit', 'hire', 'jobs']):
            # Only add if not already added from LinkedIn
            if not any(tag['tag'] == '#context:hr_tech' for tag in context_tags):
                context_tags.append({
                    'tag': '#context:hr_tech',
                    'confidence': 0.70,
                    'reasoning': f'HR/recruiting keywords in domain: {domain}',
                    'source': 'domain_analysis'
                })
        
        return context_tags
    
    def _check_dual_classification(
        self,
        contact_data: Dict,
        email_context: Optional[Dict],
        enrichment_data: Optional[Dict]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if contact should have dual stakeholder classification
        
        Example: Community leader who is also job seeking (Kim Wilkes)
        """
        
        # Pattern: Community leader + job seeker
        is_community = False
        is_job_seeker = False
        
        # Check for community signals
        if email_context and email_context.get('subjects'):
            subjects = ' '.join(email_context['subjects']).lower()
            if any(kw in subjects for kw in ['community', 'network', 'women in tech', 'elpha', 'tech ladies']):
                is_community = True
        
        # Check for job seeker signals
        if email_context and email_context.get('subjects'):
            subjects = ' '.join(email_context['subjects']).lower()
            if any(kw in subjects for kw in ['interview', 'job search', 'using careerspan', 'product trial']):
                is_job_seeker = True
        
        # Check LinkedIn for dual signals
        if enrichment_data and enrichment_data.get('linkedin_data'):
            linkedin = enrichment_data['linkedin_data']
            
            # Community leadership in role or activities
            role = linkedin.get('current_role', '').lower()
            if any(kw in role for kw in ['community', 'employer brand', 'talent attraction']):
                is_community = True
            
            # Active job seeking in recent activity
            if linkedin.get('recent_activity') and 'job' in str(linkedin.get('recent_activity')).lower():
                is_job_seeker = True
        
        # If both signals present, suggest dual classification
        if is_community and is_job_seeker:
            return {
                'tag': '#stakeholder:job_seeker',
                'confidence': 0.80,
                'reasoning': 'DUAL CLASSIFICATION: Contact shows both community leadership and job seeking signals',
                'source': 'dual_classification_detection',
                'note': 'Consider tagging as both #stakeholder:community (primary) and #stakeholder:job_seeker (secondary)'
            }
        
        return None
    
    def _load_config(self, filename: str) -> Dict:
        """Load configuration file"""
        filepath = CONFIG_DIR / filename
        
        if not filepath.exists():
            log.warning(f"Config file not found: {filename}")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Error loading {filename}: {e}")
            return {}


def analyze_stakeholder_batch(contacts: List[Dict], enrichment_data_map: Optional[Dict] = None):
    """
    Batch analyze multiple contacts
    
    Args:
        contacts: List of contact dicts with email_context
        enrichment_data_map: Optional dict mapping email -> enrichment data
        
    Returns:
        List of analysis results
    """
    analyzer = StakeholderPatternAnalyzer()
    results = []
    
    for contact in contacts:
        email = contact.get('email')
        enrichment = enrichment_data_map.get(email) if enrichment_data_map else None
        
        suggested_tags = analyzer.analyze_contact(
            contact_data=contact,
            email_context=contact.get('email_context'),
            enrichment_data=enrichment
        )
        
        results.append({
            'contact': contact,
            'suggested_tags': suggested_tags,
            'enrichment_status': 'enriched' if enrichment else 'basic_only'
        })
    
    return results


def main():
    """CLI entry point"""
    print("Stakeholder Pattern Analyzer v1.0.0")
    print("=" * 60)
    print("Part of: N5 Stakeholder Auto-Tagging System (Phase 1B)")
    print("")
    print("Analyzes email patterns and enrichment data to suggest tags.")
    print("")
    print("Signal types analyzed:")
    print("  1. LinkedIn job title → Stakeholder type")
    print("  2. Email domain → Stakeholder type")
    print("  3. Email keywords → Stakeholder type, context")
    print("  4. Email frequency → Relationship status")
    print("  5. Response time → Engagement status")
    print("  6. Company size → Context (enterprise)")
    print("  7. Industry → Context tags")
    print("")
    print("Confidence scoring:")
    print("  - High (>80%): Likely accurate, suggest auto-approval")
    print("  - Medium (60-80%): Review recommended")
    print("  - Low (<60%): Requires V's input")
    print("")


if __name__ == "__main__":
    main()
