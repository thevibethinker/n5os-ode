---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Aviato CRM Integration Plan
## Stakeholder Enrichment for Careerspan

### Executive Summary

Aviato is a comprehensive people and company data enrichment platform that provides 233M+ person profiles and 8M+ company profiles. This integration will enhance Careerspan's stakeholder CRM profiles with rich professional data, employment history, contact information, company intelligence, and career trajectory insights.

---

## 1. What is Aviato?

**Aviato** is a data enrichment engine that provides detailed, continuously refreshed information about people and organizations from public and proprietary sources[^1][^2].

### Key Capabilities:
- **People Data**: 233M profiles with 90+ datapoints including work history, education, skills, compensation, contact info
- **Company Data**: 8M+ organizations with 240+ datapoints including financials, headcount, web traffic, tech stack
- **Real-time Updates**: Data refreshed on regular intervals for accuracy
- **Exclusive Insights**: Vesting schedules, compensation data, investment info, web traffic metrics

### Data Coverage Highlights:
| Data Type | Coverage |
|-----------|----------|
| **People** | |
| Experience Data | >99.9% |
| Education Data | >95.3% |
| Contact Info | ~62.7% |
| Geocoded Location | 93.8% |
| **Companies** | |
| Financial Data | >97.5% of funded companies |
| Web Traffic | 52.3% |
| Employee Breakdown | >99.9% |

---

## 2. Core API Endpoints for CRM Enrichment

### 2.1 Person Enrichment
**Endpoint**: `GET /person/enrich`

**Input Options** (flexible lookups):
- LinkedIn ID/URL
- Email address
- Twitter ID
- Crunchbase ID
- AngelList ID

**Rich Output Data**:
```
• Basic Info: Name, headline, location (geocoded)
• Professional: Current/past titles, companies, departments, seniority scores
• Education: Degrees, schools, fields of study
• Contact: Email, phone, social profiles
• Career Signals: Skills, languages, LinkedIn connections/followers
• Investment Profile: (for investors) portfolio, interests, check sizes
• Compensation: Salary ranges, equity data
• Engagement: LinkedIn join date, labor status (OPEN_TO_WORK, HIRING)
```

### 2.2 Company Enrichment
**Endpoint**: `GET /company/enrich`

**Input Options**:
- LinkedIn company ID/URL
- Website domain
- Crunchbase/Pitchbook/AngelList/Wellfound IDs
- Twitter/Facebook IDs

**Rich Output Data**:
```
• Fundamentals: Name, description, tagline, industry, headcount
• Growth Metrics: Headcount trends (weekly/monthly/yearly %), web traffic
• Financial: Funding rounds, valuation, total raised, market cap, share price
• Social Signals: LinkedIn/Twitter/Facebook followers (current + historical)
• Product Intel: Tech stack, screenshots, G2 reviews, Product Hunt data
• Hiring Signals: Job listings by department, seniority, remote/on-site
• Location: Geocoded HQ and office locations
• Legal/Compliance: DUNS, CAGE code, NAICS code, government awards
• Acquisition/Exit: Acquisition status, acquirer, IPO date
```

---

## 3. Integration Architecture

### 3.1 Integration Patterns

**Option A: Real-time API Integration** (Recommended for high-value enrichment)
```
Workflow:
1. Stakeholder profile created/updated in CRM
2. Trigger enrichment → Call Aviato API with identifier
3. Parse response → Map to CRM fields
4. Update CRM profile with enriched data
5. Log enrichment timestamp for cache management
```

**Option B: Batch Enrichment** (Recommended for bulk updates)
```
Workflow:
1. Export stakeholder list from CRM (daily/weekly)
2. Batch API calls with rate limiting (300 req/min)
3. Aggregate enriched data
4. Bulk import back into CRM
5. Update "Last Enriched" field
```

**Option C: Hybrid** (Best of both)
- Real-time for VIP stakeholders (executives, key decision-makers)
- Batch for broader stakeholder database
- Scheduled refresh for stale data (>30 days old)

### 3.2 Technical Implementation

**Authentication**:
```bash
Authorization: Bearer 07bf454c7e41b8e82df7337b20e9792c03a18ffbb9182232
```

**Rate Limits**:
- 300 requests/minute (5-minute rolling window)
- Handle 429 errors with exponential backoff

**Example API Call** (Person):
```bash
curl -G https://data.api.aviato.co/person/enrich \
  -H "Authorization: Bearer ${AVIATO_API_KEY}" \
  --data-urlencode "email=stakeholder@company.com" \
  --data-urlencode "linkedinURL=https://linkedin.com/in/profile"
```

**Example API Call** (Company):
```bash
curl -G https://data.api.aviato.co/company/enrich \
  -H "Authorization: Bearer ${AVIATO_API_KEY}" \
  --data-urlencode "website=company.com" \
  --data-urlencode "linkedinURL=https://linkedin.com/company/acme"
```

---

## 4. CRM Schema Mapping

### 4.1 Stakeholder Profile Fields (Person Data)

| CRM Field | Aviato Field | Value |
|-----------|--------------|-------|
| **Core Identity** | | |
| Full Name | `fullName` | Full name |
| Email | `email` (input) | Email |
| LinkedIn URL | `URLs.linkedin` | Profile link |
| Location | `location` + `locationDetails` | City, Region, Country (geocoded) |
| **Professional** | | |
| Current Title | `experienceList[0].positionList[0].title` | Latest position |
| Current Company | `experienceList[0].companyName` | Current employer |
| Company LinkedIn | `experienceList[0].company.URLs.linkedin` | Company profile |
| Seniority Level | `experienceList[0].positionList[0].seniorityScore` | 1-10 score |
| Department | `experienceList[0].positionList[0].department` | Dept/function |
| Start Date | `experienceList[0].startDate` | Employment start |
| Work History | `experienceList` (full array) | Complete career path |
| **Education** | | |
| Degrees | `degreeList` | All degrees |
| Schools | `educationList` | Education history |
| **Contact & Social** | | |
| LinkedIn Connections | `linkedinConnections` | Network size |
| LinkedIn Followers | `linkedinFollowers` | Influence metric |
| Twitter | `URLs.twitter` | Social handle |
| Skills | `skills` | Skill list |
| Languages | `languageList` | Languages + proficiency |
| **Career Signals** | | |
| Open to Work | `linkedinLaborStatus` | OPEN_TO_WORK flag |
| LinkedIn Join Date | `linkedinJoinDate` | Platform tenure |
| **Investor Profile** (if applicable) | | |
| Investor Type | `investorType` | Angel/VC/etc |
| Check Size Range | `investorMinInvestment` - `investorMaxInvestment` | Investment range |
| Investment Focus | `investorInterests` | Sectors of interest |
| Portfolio Count | `investorParticipatedRoundsCount` | # investments |

### 4.2 Company Profile Fields (Organization Data)

| CRM Field | Aviato Field | Value |
|-----------|--------------|-------|
| **Core Identity** | | |
| Company Name | `name` | Official name |
| Website | `URLs.website` | Domain |
| Description | `description` | Company bio |
| Tagline | `tagline` | Mission/slogan |
| Industries | `industryList` | Industry tags |
| **Size & Growth** | | |
| Headcount | `computed_headcount` | Current employees |
| Headcount Trend (1M) | `monthlyHeadcountPercent` | Growth % |
| Headcount Trend (1Y) | `yearlyHeadcountPercent` | Annual growth |
| Headcount History | `headcountHistorical` | Time series |
| **Traction Metrics** | | |
| Web Traffic | `currentWebTraffic` | Monthly visitors |
| Traffic Trend (1M) | `monthlyWebTrafficPercent` | Growth % |
| Traffic Sources | `webTrafficSources` | Direct/search/social breakdown |
| LinkedIn Followers | `linkedinFollowers` | Social reach |
| Twitter Followers | `twitterFollowers` | Social reach |
| G2 Rating | `g2AverageStars` | Product reviews |
| G2 Review Count | `g2ReviewCount` | Review volume |
| **Financial** | | |
| Funding Status | `financingStatus` | Stage |
| Total Funding | `totalFunding` | Amount raised |
| Funding Rounds | `fundingRoundCount` | # of rounds |
| Last Round Valuation | `lastRoundValuation` | Valuation |
| Latest Deal | `latestDealType`, `latestDealAmount`, `latestDealDate` | Recent raise |
| Stock Symbol | `stockSymbol` | Ticker (if public) |
| Share Price | `sharePrice` | Current price |
| Market Cap | `marketCap` | Public valuation |
| **Operational Intel** | | |
| Tech Stack | `techStackList` | Technologies used |
| Job Openings | `jobListingList` | Open roles |
| Hiring Depts | `jobFamilyList` | Departments hiring |
| Remote Jobs | `jobListingList[].isRemote` | Remote flags |
| Office Locations | `locationDetails` | Geo data |
| **Strategic** | | |
| Acquisition Status | `isAcquired`, `acquiredBy` | M&A info |
| Exit Status | `isExited` | Liquidity event |
| Investment Count | `investmentCount` | Portfolio size (if investor) |
| Patents | `patentCount` | IP holdings |

---

## 5. Integration Workflow

### Phase 1: Setup & Validation (Week 1)
**Tasks**:
1. ✓ Store API key securely in `/home/workspace/Integrations/Aviato/.env`
2. Build Python integration module (`aviato_client.py`)
3. Test API authentication and basic enrichment calls
4. Validate data quality with sample stakeholder profiles
5. Map Aviato fields to Careerspan CRM schema
6. Define error handling and retry logic

**Success Criteria**:
- Successful authentication
- 10+ test enrichments complete
- Field mapping documented
- Error handling validated

### Phase 2: Core Integration Build (Week 2)
**Tasks**:
1. Build Python SDK wrapper for Aviato API
   - Person enrichment function
   - Company enrichment function
   - Batch enrichment orchestration
   - Rate limit management
   - Response parsing and normalization
2. Create CRM update functions
   - Map Aviato data → CRM fields
   - Handle missing/null values
   - Preserve existing data where appropriate
3. Build enrichment queue system
   - Priority queue (VIP stakeholders first)
   - Deduplication logic
   - Retry mechanism for failures

**Success Criteria**:
- Working SDK with error handling
- CRM update functions tested
- Queue system operational

### Phase 3: Data Quality & Validation (Week 3)
**Tasks**:
1. Data quality checks:
   - Validate email deliverability
   - Cross-reference LinkedIn URLs
   - Verify company-person relationships
   - Flag suspicious/outdated data
2. Build audit trail:
   - Log all enrichments (timestamp, source, fields updated)
   - Track data freshness
   - Monitor API usage and costs
3. Create dashboard for enrichment metrics:
   - Enrichment success rate
   - Data coverage by field
   - API call volume and cost
   - Stale data alerts

**Success Criteria**:
- Data quality rules defined and implemented
- Audit logging operational
- Metrics dashboard functional

### Phase 4: Production Deployment (Week 4)
**Tasks**:
1. Schedule batch enrichments:
   - Daily: New stakeholders added to CRM
   - Weekly: Update high-priority stakeholders
   - Monthly: Refresh entire database
2. Implement real-time triggers:
   - New stakeholder creation
   - Profile viewed by team member
   - Pre-meeting enrichment (auto-enrich before scheduled meetings)
3. Create enrichment status UI in CRM:
   - "Last Enriched" timestamp
   - "Enrichment Status" (Complete/Partial/Failed)
   - "Data Freshness" indicator
   - Manual "Re-enrich" button

**Success Criteria**:
- Automated enrichment workflows live
- Team can see enrichment status
- Manual enrichment available

---

## 6. Enrichment Use Cases for Careerspan

### 6.1 Stakeholder Intelligence
**Scenario**: Career coach preparing for client meeting

**Enriched Insights**:
- Current role, company, department, seniority
- Career trajectory (job history with dates)
- Education background
- Skills and competencies
- LinkedIn engagement metrics (network size, followers)
- "Open to Work" status

**Value**: Personalized coaching based on complete professional context

### 6.2 Company Research
**Scenario**: Understanding stakeholder's employer

**Enriched Insights**:
- Company size, growth trajectory (headcount trends)
- Funding status, investors, valuation
- Tech stack and product offerings
- Hiring activity and departments
- Market traction (web traffic, G2 reviews)
- Recent news and announcements

**Value**: Context for industry trends, company stability, career opportunities

### 6.3 Network Mapping
**Scenario**: Identifying connections and referrals

**Enriched Insights**:
- Previous employers (alumni networks)
- Education institutions (school networks)
- Investor connections (for founders/entrepreneurs)
- Geographic clustering (local professional communities)

**Value**: Warm introduction paths, community building

### 6.4 Engagement Scoring
**Scenario**: Prioritizing outreach and follow-up

**Enriched Signals**:
- LinkedIn activity level (connection growth, followers)
- Job tenure (recent start = transition moment)
- "Open to Work" status (high intent signal)
- Company hiring activity (potential referral opportunities)

**Value**: Data-driven engagement timing and messaging

### 6.5 Market Intelligence
**Scenario**: Industry and sector analysis

**Enriched Insights**:
- Stakeholder concentration by industry/company
- Emerging companies (funding + growth metrics)
- Hiring trends across portfolio companies
- Geographic distribution of stakeholders

**Value**: Market positioning, content strategy, program development

---

## 7. Integration Implementation

### 7.1 Python SDK Structure

```python
# /home/workspace/Integrations/Aviato/aviato_client.py

import os
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv
import time
from datetime import datetime

class AviatoClient:
    def __init__(self):
        load_dotenv('/home/workspace/Integrations/Aviato/.env')
        self.api_key = os.getenv('AVIATO_API_KEY')
        self.base_url = os.getenv('AVIATO_API_BASE_URL')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def enrich_person(self, 
                     email: Optional[str] = None,
                     linkedin_url: Optional[str] = None,
                     linkedin_id: Optional[str] = None) -> Dict:
        \"\"\"Enrich a person profile using email or LinkedIn identifier\"\"\"
        params = {}
        if email:
            params['email'] = email
        if linkedin_url:
            params['linkedinURL'] = linkedin_url
        if linkedin_id:
            params['linkedinID'] = linkedin_id
        
        response = requests.get(
            f'{self.base_url}/person/enrich',
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def enrich_company(self,
                      website: Optional[str] = None,
                      linkedin_url: Optional[str] = None,
                      linkedin_id: Optional[str] = None) -> Dict:
        \"\"\"Enrich a company profile using domain or LinkedIn identifier\"\"\"
        params = {}
        if website:
            params['website'] = website
        if linkedin_url:
            params['linkedinURL'] = linkedin_url
        if linkedin_id:
            params['linkedinID'] = linkedin_id
        
        response = requests.get(
            f'{self.base_url}/company/enrich',
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def batch_enrich_people(self, profiles: List[Dict], 
                           rate_limit_delay: float = 0.2) -> List[Dict]:
        \"\"\"Batch enrich multiple person profiles with rate limiting\"\"\"
        results = []
        for profile in profiles:
            try:
                enriched = self.enrich_person(**profile)
                results.append({
                    'input': profile,
                    'output': enriched,
                    'status': 'success',
                    'timestamp': datetime.utcnow().isoformat()
                })
            except Exception as e:
                results.append({
                    'input': profile,
                    'output': None,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
            time.sleep(rate_limit_delay)  # Rate limiting
        return results
```

### 7.2 CRM Mapper Structure

```python
# /home/workspace/Integrations/Aviato/crm_mapper.py

from typing import Dict, Optional

class AviatoCRMMapper:
    \"\"\"Maps Aviato API responses to Careerspan CRM schema\"\"\"
    
    @staticmethod
    def map_person_to_crm(aviato_data: Dict) -> Dict:
        \"\"\"Transform Aviato person data to CRM fields\"\"\"
        
        # Extract current employment (most recent)
        current_exp = aviato_data.get('experienceList', [{}])[0] if aviato_data.get('experienceList') else {}
        current_position = current_exp.get('positionList', [{}])[0] if current_exp.get('positionList') else {}
        
        # Extract education (most recent)
        latest_edu = aviato_data.get('educationList', [{}])[0] if aviato_data.get('educationList') else {}
        
        return {
            # Core Identity
            'full_name': aviato_data.get('fullName'),
            'email': aviato_data.get('email'),  # From input
            'linkedin_url': aviato_data.get('URLs', {}).get('linkedin'),
            'twitter_url': aviato_data.get('URLs', {}).get('twitter'),
            'location': aviato_data.get('location'),
            'city': aviato_data.get('locationDetails', {}).get('locality', {}).get('name'),
            'region': aviato_data.get('locationDetails', {}).get('region', {}).get('name'),
            'country': aviato_data.get('locationDetails', {}).get('country', {}).get('name'),
            
            # Professional
            'current_title': current_position.get('title'),
            'current_company': current_exp.get('companyName'),
            'current_company_id': current_exp.get('companyID'),
            'current_department': current_position.get('department'),
            'seniority_score': current_position.get('seniorityScore'),
            'employment_start_date': current_exp.get('startDate'),
            
            # Education
            'latest_degree': latest_edu.get('name'),
            'latest_school': latest_edu.get('school', {}).get('fullName'),
            'field_of_study': latest_edu.get('subject'),
            
            # Engagement Metrics
            'linkedin_connections': aviato_data.get('linkedinConnections'),
            'linkedin_followers': aviato_data.get('linkedinFollowers'),
            'linkedin_join_date': aviato_data.get('linkedinJoinDate'),
            
            # Career Signals
            'open_to_work': aviato_data.get('linkedinLaborStatus') == 'OPEN_TO_WORK',
            'skills': aviato_data.get('skills', []),
            'languages': [lang.get('languageName') for lang in aviato_data.get('languageList', [])],
            
            # Metadata
            'aviato_last_updated': aviato_data.get('lastUpdated'),
            'aviato_person_id': aviato_data.get('id'),
            'enrichment_timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def map_company_to_crm(aviato_data: Dict) -> Dict:
        \"\"\"Transform Aviato company data to CRM fields\"\"\"
        
        return {
            # Core Identity
            'company_name': aviato_data.get('name'),
            'website': aviato_data.get('URLs', {}).get('website'),
            'linkedin_url': aviato_data.get('URLs', {}).get('linkedin'),
            'description': aviato_data.get('description'),
            'tagline': aviato_data.get('tagline'),
            'industries': aviato_data.get('industryList', []),
            
            # Size & Location
            'headcount': aviato_data.get('computed_headcount'),
            'location': aviato_data.get('locality'),
            'region': aviato_data.get('region'),
            'country': aviato_data.get('country'),
            
            # Growth Metrics
            'headcount_growth_monthly': aviato_data.get('monthlyHeadcountPercent'),
            'headcount_growth_yearly': aviato_data.get('yearlyHeadcountPercent'),
            'web_traffic': aviato_data.get('currentWebTraffic'),
            'traffic_growth_monthly': aviato_data.get('monthlyWebTrafficPercent'),
            
            # Financial
            'funding_status': aviato_data.get('financingStatus'),
            'total_funding': aviato_data.get('totalFunding'),
            'funding_rounds': aviato_data.get('fundingRoundCount'),
            'valuation': aviato_data.get('lastRoundValuation'),
            'latest_deal_type': aviato_data.get('latestDealType'),
            'latest_deal_amount': aviato_data.get('latestDealAmount'),
            'latest_deal_date': aviato_data.get('latestDealDate'),
            
            # Signals
            'is_hiring': len(aviato_data.get('jobListingList', [])) > 0,
            'open_roles': len(aviato_data.get('jobListingList', [])),
            'tech_stack': [tech.get('productName') for tech in aviato_data.get('techStackList', [])],
            'g2_rating': aviato_data.get('g2AverageStars'),
            'g2_reviews': aviato_data.get('g2ReviewCount'),
            
            # Metadata
            'aviato_company_id': aviato_data.get('id'),
            'enrichment_timestamp': datetime.utcnow().isoformat()
        }
```

### 7.3 Orchestration Script

```python
# /home/workspace/Integrations/Aviato/enrich_stakeholders.py

from aviato_client import AviatoClient
from crm_mapper import AviatoCRMMapper
import json
from datetime import datetime

def enrich_stakeholder(email: str, linkedin_url: Optional[str] = None):
    \"\"\"Enrich a single stakeholder with Aviato data\"\"\"
    client = AviatoClient()
    mapper = AviatoCRMMapper()
    
    # Enrich person
    person_data = client.enrich_person(email=email, linkedin_url=linkedin_url)
    crm_person = mapper.map_person_to_crm(person_data)
    
    # Enrich their current company (if available)
    company_id = person_data.get('experienceList', [{}])[0].get('companyID')
    company_data = None
    if company_id:
        company_data = client.enrich_company(linkedin_id=company_id)
        crm_company = mapper.map_company_to_crm(company_data)
    else:
        crm_company = None
    
    return {
        'person': crm_person,
        'company': crm_company,
        'raw_aviato_person': person_data,
        'raw_aviato_company': company_data
    }

def enrich_stakeholder_list(stakeholders: List[Dict]):
    \"\"\"Batch enrich a list of stakeholders\"\"\"
    client = AviatoClient()
    
    # Prepare enrichment inputs
    profiles = [
        {'email': s.get('email'), 'linkedin_url': s.get('linkedin_url')}
        for s in stakeholders
    ]
    
    # Batch enrich
    results = client.batch_enrich_people(profiles)
    
    # Map to CRM and return
    mapped_results = []
    mapper = AviatoCRMMapper()
    for result in results:
        if result['status'] == 'success':
            mapped = mapper.map_person_to_crm(result['output'])
            mapped_results.append(mapped)
    
    return mapped_results
```

---

## 8. Cost & Usage Considerations

### 8.1 API Pricing Model
- Aviato uses a **credit-based system**
- Need to request pricing details from Aviato team
- Monitor usage via API logs: `https://data.aviato.co/dashboard/api-logs`

### 8.2 Optimization Strategies
1. **Cache Management**: Store enriched data, refresh only when stale (>30 days)
2. **Prioritize VIPs**: Enrich high-value stakeholders first
3. **Batch Efficiently**: Group enrichments to maximize throughput (300/min)
4. **Selective Fields**: Only request data you'll actually use in CRM
5. **Deduplication**: Don't re-enrich recently updated profiles

### 8.3 Estimated Usage
**Assumptions**:
- 1,000 stakeholders in CRM
- 50 new stakeholders/month
- Refresh cycle: 30 days

**Monthly API Calls**:
- New stakeholders: 50 person + 50 company = 100 calls
- Refresh existing: 1,000/30 × 30 = 1,000 calls (person only)
- **Total: ~1,100 API calls/month**

---

## 9. Next Steps

### Immediate Actions:
1. ✓ API key stored securely
2. ✓ Documentation reviewed and integration plan created
3. **Build Python SDK** (`aviato_client.py` and `crm_mapper.py`)
4. **Test enrichment** with 5-10 sample stakeholders
5. **Validate data quality** and field mapping accuracy
6. **Define CRM update logic** (which fields to overwrite vs. append)

### Technical Decisions Needed:
1. **CRM Platform**: What CRM are you using? (For building the update/sync logic)
2. **Enrichment Triggers**: Real-time, batch, or hybrid approach?
3. **Data Retention**: How long to keep raw Aviato responses?
4. **Field Priorities**: Which Aviato fields are must-have vs. nice-to-have?
5. **Refresh Strategy**: How often to re-enrich existing stakeholders?

### Questions for Planning:
1. What CRM system are you currently using for stakeholder management?
2. Do you have existing stakeholder data that needs to be enriched retroactively?
3. What are the top 5 data points you most want to add to stakeholder profiles?
4. Are there specific use cases or workflows this enrichment should enable?
5. Do you want manual enrichment controls or fully automated?

---

## 10. Resources

### Documentation:
- Aviato API Docs: https://docs.data.aviato.co/
- Person Enrich Endpoint: https://docs.data.aviato.co/api-reference/person/enrich
- Company Enrich Endpoint: https://docs.data.aviato.co/api-reference/company/enrich
- Authentication Guide: https://docs.data.aviato.co/intro/introduction-auth
- Data Overview: https://docs.data.aviato.co/intro/data-overview

### API Dashboard:
- Login: https://data.aviato.co/login
- API Playground: https://docs.data.aviato.co/api-reference/company/enrich?explorer=true
- Usage Logs: https://data.aviato.co/dashboard/api-logs

[^1]: https://www.aviato.co/
[^2]: https://docs.data.aviato.co/intro/introduction-auth

