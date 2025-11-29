#!/usr/bin/env python3
"""
Test Aviato API connection and basic enrichment
"""

import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv('/home/workspace/Integrations/Aviato/.env')

API_KEY = os.getenv('AVIATO_API_KEY')
BASE_URL = os.getenv('AVIATO_API_BASE_URL')

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def test_person_enrich():
    """Test person enrichment with a sample LinkedIn URL"""
    print("\\n=== Testing Person Enrichment ===")
    
    # Using Bill Gates as a test case (public figure with rich data)
    params = {
        'linkedinURL': 'https://linkedin.com/in/williamhgates'
    }
    
    try:
        response = requests.get(
            f'{BASE_URL}/person/enrich',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Person enrichment successful")
        print(f"  Name: {data.get('fullName')}")
        print(f"  Headline: {data.get('headline')}")
        print(f"  Location: {data.get('location')}")
        print(f"  LinkedIn ID: {data.get('linkedinID')}")
        
        # Show current employment
        if data.get('experienceList'):
            exp = data['experienceList'][0]
            print(f"  Current Role: {exp.get('companyName')}")
        
        # Save raw response for inspection
        with open('/home/workspace/Integrations/Aviato/test_person_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\\n  Full response saved to: test_person_response.json")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        print(f"  Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_company_enrich():
    """Test company enrichment with a sample domain"""
    print("\\n=== Testing Company Enrichment ===")
    
    # Using Google as a test case
    params = {
        'linkedinURL': 'https://linkedin.com/company/google'
    }
    
    try:
        response = requests.get(
            f'{BASE_URL}/company/enrich',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Company enrichment successful")
        print(f"  Name: {data.get('name')}")
        print(f"  Description: {data.get('description', '')[:100]}...")
        print(f"  Headcount: {data.get('computed_headcount')}")
        print(f"  Web Traffic: {data.get('currentWebTraffic')}")
        print(f"  Industries: {', '.join(data.get('industryList', [])[:3])}")
        
        # Save raw response for inspection
        with open('/home/workspace/Integrations/Aviato/test_company_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\\n  Full response saved to: test_company_response.json")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        print(f"  Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Aviato API Connection Test")
    print("=" * 60)
    
    # Test authentication
    print(f"\\nAPI Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print(f"Base URL: {BASE_URL}")
    
    # Run tests
    person_ok = test_person_enrich()
    company_ok = test_company_enrich()
    
    # Summary
    print("\\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Person Enrichment: {'✓ PASS' if person_ok else '✗ FAIL'}")
    print(f"  Company Enrichment: {'✓ PASS' if company_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if person_ok and company_ok:
        print("\\n✓ All tests passed! Aviato integration is ready.")
        exit(0)
    else:
        print("\\n✗ Some tests failed. Check error messages above.")
        exit(1)

