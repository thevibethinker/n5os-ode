#!/usr/bin/env python3
"""
Example: Complete Stakeholder Enrichment Workflow
Demonstrates how to enrich a stakeholder and their company, then display insights
"""

from aviato_client import AviatoClient
from crm_mapper import AviatoCRMMapper
import json
from datetime import datetime


def enrich_stakeholder_profile(email: str = None, linkedin_url: str = None):
    """
    Complete enrichment workflow for a single stakeholder.
    
    This demonstrates:
    1. Person enrichment
    2. Company enrichment (from person's current employer)
    3. Data mapping to CRM fields
    4. Insight extraction for quick stakeholder intel
    """
    
    client = AviatoClient()
    mapper = AviatoCRMMapper()
    
    print("=" * 80)
    print("STAKEHOLDER ENRICHMENT WORKFLOW")
    print("=" * 80)
    
    # === STEP 1: Enrich Person ===
    print("\\n[1/4] Enriching person profile...")
    person_data = client.enrich_person(email=email, linkedin_url=linkedin_url)
    
    if not person_data:
        print("✗ Person not found in Aviato database")
        return None
    
    person_crm = mapper.map_person_to_crm(person_data)
    print(f"✓ Found: {person_crm['full_name']}")
    
    # === STEP 2: Enrich Company (if employed) ===
    company_crm = None
    if person_crm.get('current_company_id'):
        print("\\n[2/4] Enriching current employer...")
        company_data = client.enrich_company(id=person_crm['current_company_id'])
        
        if company_data:
            company_crm = mapper.map_company_to_crm(company_data)
            print(f"✓ Found: {company_crm['company_name']}")
        else:
            print("⚠ Company data not available")
    else:
        print("\\n[2/4] Skipping company enrichment (no current employer)")
    
    # === STEP 3: Generate Insights ===
    print("\\n[3/4] Generating stakeholder insights...")
    
    person_highlights = mapper.extract_career_highlights(person_crm)
    company_highlights = mapper.extract_company_highlights(company_crm) if company_crm else []
    
    # === STEP 4: Display Stakeholder Intelligence ===
    print("\\n[4/4] Stakeholder Intelligence Report")
    print("=" * 80)
    
    # Personal Profile
    print("\\n📋 PERSONAL PROFILE")
    print("-" * 80)
    print(f"Name:          {person_crm['full_name']}")
    print(f"Headline:      {person_crm['headline']}")
    print(f"Location:      {person_crm['city']}, {person_crm['region']}, {person_crm['country']}")
    print(f"LinkedIn:      {person_crm['linkedin_url']}")
    
    # Current Role
    print("\\n💼 CURRENT ROLE")
    print("-" * 80)
    print(f"Title:         {person_crm['current_title']}")
    print(f"Company:       {person_crm['current_company_name']}")
    print(f"Department:    {person_crm['current_department']}")
    print(f"Seniority:     {person_crm['current_seniority_score']}/10")
    print(f"Started:       {person_crm['current_employment_start']}")
    
    # Education
    print("\\n🎓 EDUCATION")
    print("-" * 80)
    print(f"Degree:        {person_crm['latest_degree']}")
    print(f"School:        {person_crm['latest_school']}")
    print(f"Field:         {person_crm['latest_field_of_study']}")
    
    # Network & Engagement
    print("\\n🌐 NETWORK & ENGAGEMENT")
    print("-" * 80)
    print(f"Connections:   {person_crm['linkedin_connections']:,}" if person_crm['linkedin_connections'] else "Connections:   N/A")
    print(f"Followers:     {person_crm['linkedin_followers']:,}" if person_crm['linkedin_followers'] else "Followers:     N/A")
    print(f"Status:        {person_crm['linkedin_labor_status']}")
    
    # Skills
    if person_crm.get('skills'):
        skills_preview = ', '.join(person_crm['skills'][:8])
        print(f"Top Skills:    {skills_preview}")
    
    # Career Signals
    if person_highlights:
        print("\\n🔔 CAREER SIGNALS")
        print("-" * 80)
        for highlight in person_highlights:
            print(f"  {highlight}")
    
    # Company Intelligence (if available)
    if company_crm:
        print("\\n\\n🏢 CURRENT EMPLOYER INTELLIGENCE")
        print("=" * 80)
        
        print("\\n📊 COMPANY PROFILE")
        print("-" * 80)
        print(f"Name:          {company_crm['company_name']}")
        print(f"Description:   {company_crm['description'][:150]}..." if company_crm['description'] else "Description:   N/A")
        print(f"Industries:    {', '.join(company_crm['industries'][:3])}" if company_crm['industries'] else "Industries:    N/A")
        print(f"Website:       {company_crm['website']}")
        
        print("\\n📈 SIZE & GROWTH")
        print("-" * 80)
        print(f"Headcount:     {company_crm['headcount']:,}" if company_crm['headcount'] else "Headcount:     N/A")
        
        if company_crm.get('headcount_growth_monthly'):
            print(f"Growth (1M):   {company_crm['headcount_growth_monthly']:+.1f}%")
        if company_crm.get('headcount_growth_yearly'):
            print(f"Growth (1Y):   {company_crm['headcount_growth_yearly']:+.1f}%")
        
        print("\\n💰 FINANCIAL")
        print("-" * 80)
        print(f"Status:        {company_crm['financing_status']}")
        
        if company_crm.get('total_funding'):
            print(f"Total Funding: ${company_crm['total_funding']:,.0f}")
        if company_crm.get('funding_round_count'):
            print(f"Rounds:        {company_crm['funding_round_count']}")
        if company_crm.get('last_round_valuation'):
            print(f"Valuation:     ${company_crm['last_round_valuation']:,.0f}")
        
        if company_crm.get('stock_symbol'):
            print(f"\\nPublic:        {company_crm['stock_symbol']}")
            print(f"Share Price:   ${company_crm['share_price']:.2f}" if company_crm['share_price'] else "Share Price:   N/A")
            print(f"Market Cap:    ${company_crm['market_cap']:,.0f}" if company_crm['market_cap'] else "Market Cap:    N/A")
        
        print("\\n🌍 TRACTION")
        print("-" * 80)
        if company_crm.get('web_traffic'):
            print(f"Web Visitors:  {company_crm['web_traffic']:,.0f}/month")
            if company_crm.get('web_traffic_growth_monthly'):
                print(f"Growth:        {company_crm['web_traffic_growth_monthly']:+.1f}% monthly")
        
        if company_crm.get('linkedin_followers'):
            print(f"LinkedIn:      {company_crm['linkedin_followers']:,} followers")
        if company_crm.get('g2_rating'):
            print(f"G2 Rating:     {company_crm['g2_rating']:.1f}/5 ({company_crm['g2_review_count']} reviews)")
        
        print("\\n💼 HIRING ACTIVITY")
        print("-" * 80)
        print(f"Open Roles:    {company_crm['open_roles_count']}")
        if company_crm.get('job_families'):
            print(f"Departments:   {', '.join(company_crm['job_families'][:5])}")
        
        # Show first 3 open roles
        if company_crm.get('open_roles'):
            print("\\nRecent Postings:")
            for job in company_crm['open_roles'][:3]:
                remote = "🏠 Remote" if job['is_remote'] else "🏢 On-site"
                fulltime = "Full-time" if job['is_fulltime'] else "Part-time"
                print(f"  • {job['title']} ({remote}, {fulltime})")
        
        print("\\n🔧 TECHNOLOGY")
        print("-" * 80)
        if company_crm.get('tech_stack'):
            tech_preview = ', '.join(company_crm['tech_stack'][:10])
            print(f"Stack:         {tech_preview}")
        
        # Company signals
        if company_highlights:
            print("\\n🔔 COMPANY SIGNALS")
            print("-" * 80)
            for highlight in company_highlights:
                print(f"  {highlight}")
    
    # === Save Complete Report ===
    report = {
        'person': person_crm,
        'company': company_crm,
        'person_highlights': person_highlights,
        'company_highlights': company_highlights,
        'generated_at': datetime.utcnow().isoformat()
    }
    
    filename = f"enrichment_report_{person_crm['full_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\\n" + "=" * 80)
    print(f"✓ Complete report saved: {filename}")
    print("=" * 80)
    
    return report


if __name__ == '__main__':
    """
    Example usage: Enrich a stakeholder
    
    Usage:
      python3 example_enrichment.py
    
    Or import and use programmatically:
      from example_enrichment import enrich_stakeholder_profile
      result = enrich_stakeholder_profile(email="stakeholder@company.com")
    """
    
    # EXAMPLE 1: Enrich using LinkedIn URL (public figure for demo)
    print("\\n🔍 EXAMPLE 1: Enrich using LinkedIn URL")
    enrich_stakeholder_profile(linkedin_url='https://linkedin.com/in/williamhgates')
    
    # EXAMPLE 2: Enrich using email (replace with real stakeholder)
    # print("\\n\\n🔍 EXAMPLE 2: Enrich using email")
    # enrich_stakeholder_profile(email='your.stakeholder@company.com')
    
    print("\\n\\n✅ Enrichment complete! Check the generated JSON file for full data.")

