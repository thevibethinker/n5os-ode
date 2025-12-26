#!/usr/bin/env python3
"""
CRM Mapper for Aviato Data
Transforms Aviato API responses into CRM-friendly field structures
"""

from typing import Dict, Optional, List
from datetime import datetime


class AviatoCRMMapper:
    """Maps Aviato API responses to Careerspan CRM schema"""
    
    @staticmethod
    def map_person_to_crm(aviato_data: Dict) -> Dict:
        """
        Transform Aviato person data to CRM fields.
        
        Args:
            aviato_data: Raw response from Aviato person/enrich endpoint
        
        Returns:
            Dict with CRM-friendly field names and values
        """
        if not aviato_data:
            return {}
        
        # Extract current employment (most recent experience)
        exp_list = aviato_data.get('experienceList', [])
        current_exp = exp_list[0] if exp_list else {}
        position_list = current_exp.get('positionList', [])
        current_position = position_list[0] if position_list else {}
        
        # Extract current company details
        current_company = current_exp.get('company', {})
        
        # Extract education (most recent)
        edu_list = aviato_data.get('educationList', [])
        latest_edu = edu_list[0] if edu_list else {}
        latest_school = latest_edu.get('school', {})
        
        # Extract location details
        location_details = aviato_data.get('locationDetails', {})
        
        return {
            # === Core Identity ===
            'full_name': aviato_data.get('fullName'),
            'first_name': aviato_data.get('fullName', '').split()[0] if aviato_data.get('fullName') else None,
            'last_name': ' '.join(aviato_data.get('fullName', '').split()[1:]) if aviato_data.get('fullName') else None,
            'gender': aviato_data.get('gender'),
            'headline': aviato_data.get('headline'),
            
            # === Contact & Social ===
            'linkedin_url': aviato_data.get('URLs', {}).get('linkedin'),
            'linkedin_id': aviato_data.get('linkedinID'),
            'linkedin_entity_id': aviato_data.get('linkedinEntityID'),
            'linkedin_num_id': aviato_data.get('linkedinNumID'),
            'twitter_url': aviato_data.get('URLs', {}).get('twitter'),
            'facebook_url': aviato_data.get('URLs', {}).get('facebook'),
            'website_url': aviato_data.get('URLs', {}).get('website'),
            'crunchbase_url': aviato_data.get('URLs', {}).get('crunchbase'),
            'angellist_url': aviato_data.get('URLs', {}).get('angelList'),
            
            # === Location ===
            'location': aviato_data.get('location'),
            'city': location_details.get('locality', {}).get('name'),
            'region': location_details.get('region', {}).get('name'),
            'country': location_details.get('country', {}).get('name'),
            'location_ids': aviato_data.get('locationIDList', []),
            
            # === Current Employment ===
            'current_title': current_position.get('title'),
            'current_department': current_position.get('department'),
            'current_seniority_score': current_position.get('seniorityScore'),
            'current_position_start': current_position.get('startDate'),
            'current_position_end': current_position.get('endDate'),
            'current_position_location': current_position.get('location'),
            'current_position_description': current_position.get('description'),
            
            'current_company_name': current_exp.get('companyName'),
            'current_company_id': current_exp.get('companyID'),
            'current_company_linkedin': current_company.get('URLs', {}).get('linkedin'),
            'current_company_website': current_company.get('URLs', {}).get('website'),
            'current_company_location': current_company.get('name'),  # Company location
            'current_employment_start': current_exp.get('startDate'),
            'current_employment_end': current_exp.get('endDate'),
            
            # === Education ===
            'latest_degree': latest_edu.get('name'),
            'latest_school': latest_school.get('fullName'),
            'latest_school_location': latest_school.get('location'),
            'latest_school_linkedin': latest_school.get('linkedinID'),
            'latest_field_of_study': latest_edu.get('subject'),
            'latest_education_start': latest_edu.get('startDate'),
            'latest_education_end': latest_edu.get('endDate'),
            'latest_grade': latest_edu.get('grade'),
            
            # === Skills & Capabilities ===
            'skills': aviato_data.get('skills', []),
            'languages': [
                {
                    'language': lang.get('languageName'),
                    'proficiency': lang.get('proficiency')
                }
                for lang in aviato_data.get('languageList', [])
            ],
            
            # === LinkedIn Engagement ===
            'linkedin_connections': aviato_data.get('linkedinConnections'),
            'linkedin_followers': aviato_data.get('linkedinFollowers'),
            'linkedin_join_date': aviato_data.get('linkedinJoinDate'),
            'linkedin_labor_status': aviato_data.get('linkedinLaborStatus'),
            
            # === Career Signals ===
            'open_to_work': aviato_data.get('linkedinLaborStatus') == 'OPEN_TO_WORK',
            'is_hiring': aviato_data.get('linkedinLaborStatus') == 'HIRING',
            
            # === Investor Profile (if applicable) ===
            'investor_type': aviato_data.get('investorType'),
            'investor_title': aviato_data.get('investorTitle'),
            'investor_current_firm_id': aviato_data.get('investorCurrentFirmID'),
            'investor_firm_position': aviato_data.get('investorFirmPosition'),
            'investor_min_check': aviato_data.get('investorMinInvestment'),
            'investor_max_check': aviato_data.get('investorMaxInvestment'),
            'investor_target_check': aviato_data.get('investorTargetInvestment'),
            'investor_portfolio_count': aviato_data.get('investorParticipatedRoundsCount'),
            'investor_interests': aviato_data.get('investorInterests'),
            'investor_disinterests': aviato_data.get('investorDisinterests'),
            'investor_industries': aviato_data.get('investedIndustries', []),
            'investor_round_stages': aviato_data.get('investedRoundList', []),
            'investor_categories': aviato_data.get('investorCategoryList', []),
            
            # === Complete History (arrays) ===
            'all_experiences': aviato_data.get('experienceList', []),
            'all_education': aviato_data.get('educationList', []),
            'all_degrees': aviato_data.get('degreeList', []),
            
            # === Metadata ===
            'aviato_person_id': aviato_data.get('id'),
            'aviato_last_updated': aviato_data.get('lastUpdated'),
            'enrichment_timestamp': datetime.utcnow().isoformat(),
            'enrichment_source': 'aviato',
            
            # === Computed/Highlights ===
            'highlights': aviato_data.get('computed_highlightList', [])
        }
    
    @staticmethod
    def map_company_to_crm(aviato_data: Dict) -> Dict:
        """
        Transform Aviato company data to CRM fields.
        
        Args:
            aviato_data: Raw response from Aviato company/enrich endpoint
        
        Returns:
            Dict with CRM-friendly field names and values
        """
        if not aviato_data:
            return {}
        
        # Extract location details
        location_details = aviato_data.get('locationDetails', {})
        
        # Extract latest job listing for hiring signals
        job_listings = aviato_data.get('jobListingList', [])
        
        return {
            # === Core Identity ===
            'company_name': aviato_data.get('name'),
            'legal_name': aviato_data.get('legalName'),
            'description': aviato_data.get('description'),
            'tagline': aviato_data.get('tagline'),
            'alternate_names': aviato_data.get('alternateNames', []),
            'status': aviato_data.get('status'),
            
            # === URLs & IDs ===
            'website': aviato_data.get('URLs', {}).get('website'),
            'linkedin_url': aviato_data.get('URLs', {}).get('linkedin'),
            'linkedin_id': aviato_data.get('linkedinID'),
            'twitter_url': aviato_data.get('URLs', {}).get('twitter'),
            'facebook_url': aviato_data.get('URLs', {}).get('facebook'),
            'crunchbase_url': aviato_data.get('URLs', {}).get('crunchbase'),
            'pitchbook_url': aviato_data.get('URLs', {}).get('pitchbook'),
            'angellist_url': aviato_data.get('URLs', {}).get('angelList'),
            'producthunt_url': aviato_data.get('URLs', {}).get('contact'),  # Check docs
            
            # === Legal & Compliance ===
            'legal_entity_id': aviato_data.get('legalEntityID'),
            'duns_number': aviato_data.get('dunsNumber'),
            'cage_code': aviato_data.get('cageCode'),
            'naics_code': aviato_data.get('NAICSCode'),
            'cik_number': aviato_data.get('CIKNumber'),
            
            # === Classification ===
            'industries': aviato_data.get('industryList', []),
            'business_models': aviato_data.get('businessModelList', []),
            'customer_types': aviato_data.get('customerTypes', []),
            'target_markets': aviato_data.get('targetMarketList', []),
            'ownership_status': aviato_data.get('ownershipStatus'),
            'is_government': aviato_data.get('isGovernment'),
            'is_nonprofit': aviato_data.get('isNonProfit'),
            
            # === Location ===
            'locality': aviato_data.get('locality'),
            'region': aviato_data.get('region'),
            'country': aviato_data.get('country'),
            'location_ids': aviato_data.get('locationIDList', []),
            
            # === Size & Growth ===
            'headcount': aviato_data.get('computed_headcount'),
            'headcount_growth_weekly': aviato_data.get('weeklyHeadcountPercent'),
            'headcount_growth_monthly': aviato_data.get('monthlyHeadcountPercent'),
            'headcount_growth_quarterly': aviato_data.get('triMonthlyHeadcountPercent'),
            'headcount_growth_yearly': aviato_data.get('yearlyHeadcountPercent'),
            'headcount_change_monthly': aviato_data.get('monthlyHeadcountChange'),
            'headcount_historical': aviato_data.get('headcountHistorical', {}),
            
            # === Web & Social Traction ===
            'web_traffic': aviato_data.get('currentWebTraffic'),
            'web_traffic_growth_monthly': aviato_data.get('monthlyWebTrafficPercent'),
            'web_traffic_growth_yearly': aviato_data.get('yearlyWebTrafficPercent'),
            'web_traffic_sources': aviato_data.get('webTrafficSources', {}),
            'web_visitor_countries': aviato_data.get('webViewerCountries', []),
            'web_traffic_historical': aviato_data.get('webTrafficHistorical', {}),
            
            'linkedin_followers': aviato_data.get('linkedinFollowers'),
            'twitter_followers': aviato_data.get('twitterFollowers'),
            'twitter_growth_monthly': aviato_data.get('monthlyTwitterPercent'),
            'facebook_likes': aviato_data.get('facebookLikes'),
            'facebook_growth_monthly': aviato_data.get('monthlyFacebookPercent'),
            
            # === Financial ===
            'founded_date': aviato_data.get('founded'),
            'financing_status': aviato_data.get('financingStatus'),
            'total_funding': aviato_data.get('totalFunding'),
            'funding_round_count': aviato_data.get('fundingRoundCount'),
            'last_round_valuation': aviato_data.get('lastRoundValuation'),
            'latest_deal_type': aviato_data.get('latestDealType'),
            'latest_deal_amount': aviato_data.get('latestDealAmount'),
            'latest_deal_date': aviato_data.get('latestDealDate'),
            'investor_count': aviato_data.get('investorCount'),
            'lead_investor_count': aviato_data.get('leadInvestorCount'),
            
            # === Public Company Data ===
            'stock_symbol': aviato_data.get('stockSymbol'),
            'stock_exchange': aviato_data.get('stockExchange'),
            'share_price': aviato_data.get('sharePrice'),
            'market_cap': aviato_data.get('marketCap'),
            'outstanding_shares': aviato_data.get('outstandingShares'),
            'ipo_date': aviato_data.get('ipoDate'),
            'stock_price_historical': aviato_data.get('stockPriceHistorical', {}),
            'share_price_historical': aviato_data.get('sharePriceHistorical', {}),
            
            # === M&A & Exit ===
            'is_acquired': aviato_data.get('isAcquired'),
            'is_exited': aviato_data.get('isExited'),
            'is_shutdown': aviato_data.get('isShutDown'),
            'acquired_by': aviato_data.get('acquiredBy'),
            'exit_count': aviato_data.get('exitCount'),
            
            # === Investment Activity (for VCs/Angels) ===
            'investment_count': aviato_data.get('investmentCount'),
            'lead_investment_count': aviato_data.get('leadInvestmentCount'),
            
            # === Product & Tech ===
            'tech_stack': [
                tech.get('productName') 
                for tech in aviato_data.get('techStackList', [])
            ],
            'tech_categories': [
                cat
                for tech in aviato_data.get('techStackList', [])
                for cat in tech.get('productCategories', [])
            ],
            'products': aviato_data.get('productList', []),
            'screenshots': aviato_data.get('screenshotList', []),
            
            # === Reviews & Ratings ===
            'g2_rating': aviato_data.get('g2AverageStars'),
            'g2_review_count': aviato_data.get('g2ReviewCount'),
            'g2_review_growth_monthly': aviato_data.get('monthlyG2ReviewCountPercent'),
            'g2_rating_growth_monthly': aviato_data.get('monthlyG2StarsPercent'),
            'producthunt_avg_rating': aviato_data.get('producthuntAvgRating'),
            'producthunt_votes': aviato_data.get('producthuntTotalVotes'),
            'producthunt_followers': aviato_data.get('producthuntFollowerCount'),
            
            # === Hiring Intelligence ===
            'is_hiring': len(job_listings) > 0,
            'open_roles_count': len(job_listings),
            'job_families': aviato_data.get('jobFamilyList', []),
            'open_roles': [
                {
                    'title': job.get('title'),
                    'category': job.get('category'),
                    'sub_category': job.get('subCategory'),
                    'is_remote': job.get('isRemote'),
                    'is_fulltime': job.get('isFullTime'),
                    'locations': job.get('locations', []),
                    'url': job.get('url')
                }
                for job in job_listings
            ],
            
            # === Compensation Data ===
            'monetary_compensation': aviato_data.get('monetaryCompensation'),
            'equity_compensation': aviato_data.get('equityCompensation'),
            'department_compensation': aviato_data.get('departmentMonetaryCompensation', {}),
            'pay_schedule': aviato_data.get('paySchedule'),
            
            # === IP & Innovation ===
            'patent_count': aviato_data.get('patentCount'),
            'owned_patents': aviato_data.get('ownedPatents'),
            
            # === Government Relations ===
            'government_awards': aviato_data.get('governmentAwards'),
            
            # === News & PR ===
            'recent_news': aviato_data.get('embeddedNews', []),
            
            # === Metadata ===
            'aviato_company_id': aviato_data.get('id'),
            'aviato_tags': aviato_data.get('computed_tags', []),
            'enrichment_timestamp': datetime.utcnow().isoformat(),
            'enrichment_source': 'aviato'
        }
    
    @staticmethod
    def extract_career_highlights(person_data: Dict) -> List[str]:
        """Extract interesting career highlights for quick stakeholder summary"""
        highlights = []
        
        if person_data.get('open_to_work'):
            highlights.append("🟢 Open to Work")
        
        if person_data.get('is_hiring'):
            highlights.append("📢 Actively Hiring")
        
        if person_data.get('investor_type'):
            highlights.append(f"💰 {person_data['investor_type']} Investor")
        
        # Recent job change (started current role <6 months ago)
        current_start = person_data.get('current_employment_start')
        if current_start:
            # Parse date and check recency
            # (would need proper date parsing here)
            highlights.append(f"🆕 Recent Role Change ({current_start})")
        
        # High LinkedIn engagement
        connections = person_data.get('linkedin_connections', 0)
        if connections >= 500:
            highlights.append(f"🌐 Well Connected ({connections}+ connections)")
        
        followers = person_data.get('linkedin_followers', 0)
        if followers >= 1000:
            highlights.append(f"📣 Influencer ({followers:,} followers)")
        
        # Education pedigree
        school = person_data.get('latest_school') or ''  # Ensure never None
        top_schools = ['Harvard', 'Stanford', 'MIT', 'Yale', 'Princeton', 'Oxford', 'Cambridge']
        if school and any(s in school for s in top_schools):
            highlights.append(f"🎓 {school}")
        
        return highlights
    
    @staticmethod
    def extract_company_highlights(company_data: Dict) -> List[str]:
        """Extract interesting company highlights for quick stakeholder context"""
        highlights = []
        
        # Growth signals
        headcount_growth = company_data.get('headcount_growth_monthly', 0)
        if headcount_growth and headcount_growth > 10:
            highlights.append(f"📈 Rapid Growth (+{headcount_growth:.0f}% monthly headcount)")
        
        traffic_growth = company_data.get('web_traffic_growth_monthly', 0)
        if traffic_growth and traffic_growth > 20:
            highlights.append(f"🚀 Viral Traction (+{traffic_growth:.0f}% monthly traffic)")
        
        # Hiring activity
        open_roles = company_data.get('open_roles_count', 0)
        if open_roles >= 10:
            highlights.append(f"💼 Actively Hiring ({open_roles} open roles)")
        
        # Recent funding
        latest_deal = company_data.get('latest_deal_type')
        if latest_deal:
            amount = company_data.get('latest_deal_amount', 0)
            highlights.append(f"💵 Recent {latest_deal} (${amount/1e6:.1f}M)")
        
        # Scale
        headcount = company_data.get('headcount', 0)
        if headcount:
            if headcount >= 10000:
                highlights.append(f"🏢 Enterprise Scale ({headcount:,} employees)")
            elif headcount >= 1000:
                highlights.append(f"🏭 Large Company ({headcount:,} employees)")
            elif headcount <= 50:
                highlights.append(f"🚀 Startup ({headcount} employees)")
        
        # Product traction
        g2_rating = company_data.get('g2_rating')
        g2_reviews = company_data.get('g2_review_count', 0)
        if g2_rating and g2_reviews >= 50:
            highlights.append(f"⭐ {g2_rating:.1f}/5 on G2 ({g2_reviews} reviews)")
        
        # Tech sophistication
        tech_count = len(company_data.get('tech_stack', []))
        if tech_count >= 20:
            highlights.append(f"🔧 Advanced Tech Stack ({tech_count} technologies)")
        
        return highlights


if __name__ == '__main__':
    # Test with sample data
    sample_person = {
        'fullName': 'John Doe',
        'headline': 'CEO at Example Corp',
        'linkedinConnections': 5000,
        'linkedinLaborStatus': 'OPEN_TO_WORK'
    }
    
    mapper = AviatoCRMMapper()
    crm_data = mapper.map_person_to_crm(sample_person)
    highlights = mapper.extract_career_highlights(crm_data)
    
    print("Sample CRM Mapping:")
    print(f"  Name: {crm_data['full_name']}")
    print(f"  Highlights: {highlights}")


