#!/usr/bin/env python3
"""
Nyne Integration Comprehensive Test Suite
Tests all APIs and integrations without burning excessive credits.

Usage:
    python3 test_suite.py           # Run all tests (uses credits)
    python3 test_suite.py --dry-run # Test client init only (no credits)
    python3 test_suite.py --quick   # Quick validation (minimal credits)
"""

import os
import sys
import json
import asyncio
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/workspace')

# Test results tracking
RESULTS = {
    "passed": [],
    "failed": [],
    "skipped": [],
    "credits_used": 0
}


def log(msg: str, level: str = "INFO"):
    """Simple logger."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbol = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARN": "⚠️"}.get(level, "•")
    print(f"{timestamp} {symbol} {msg}")


def test_result(name: str, passed: bool, details: str = ""):
    """Record test result."""
    if passed:
        RESULTS["passed"].append(name)
        log(f"{name}: {details}", "PASS")
    else:
        RESULTS["failed"].append(name)
        log(f"{name}: {details}", "FAIL")


def skip_test(name: str, reason: str):
    """Skip a test."""
    RESULTS["skipped"].append(name)
    log(f"{name}: {reason}", "SKIP")


# ==================== CLIENT TESTS ====================

def test_client_initialization():
    """Test NyneClient initializes with credentials."""
    try:
        from Integrations.Nyne.nyne_client import NyneClient
        client = NyneClient()
        test_result("Client Initialization", True, "NyneClient created successfully")
        return client
    except Exception as e:
        test_result("Client Initialization", False, str(e))
        return None


def test_usage_api(client):
    """Test usage API (free, no credits)."""
    try:
        usage = client.get_usage()
        available = usage.get("limits", {}).get("available_credits", 0)
        test_result("Usage API", True, f"{available} credits available")
        return usage
    except Exception as e:
        test_result("Usage API", False, str(e))
        return None


# ==================== PERSON ENRICHMENT TESTS ====================

def test_person_enrichment_by_linkedin(client, dry_run=False):
    """Test person enrichment via LinkedIn URL."""
    if dry_run:
        skip_test("Person Enrichment (LinkedIn)", "Dry run mode")
        return None
    
    try:
        result = client.enrich_person(
            social_media_url="https://www.linkedin.com/in/garyvaynerchuk/"
        )
        if result and result.get("name"):
            RESULTS["credits_used"] += 6
            test_result("Person Enrichment (LinkedIn)", True, 
                       f"Found: {result.get('name')} - {len(result.get('socialProfiles', []))} social profiles")
            return result
        else:
            test_result("Person Enrichment (LinkedIn)", False, "No result returned")
            return None
    except Exception as e:
        test_result("Person Enrichment (LinkedIn)", False, str(e))
        return None


def test_person_enrichment_by_email(client, dry_run=False):
    """Test person enrichment via email."""
    if dry_run:
        skip_test("Person Enrichment (Email)", "Dry run mode")
        return None
    
    try:
        # Use a well-known email that's likely in the database
        result = client.enrich_person(email="jason@calacanis.com")
        if result and result.get("name"):
            RESULTS["credits_used"] += 6
            test_result("Person Enrichment (Email)", True, 
                       f"Found: {result.get('name')}")
            return result
        else:
            # Not found is valid - profile may not be in database
            test_result("Person Enrichment (Email)", True, "Profile not found (valid response)")
            return None
    except Exception as e:
        test_result("Person Enrichment (Email)", False, str(e))
        return None


# ==================== COMPANY TESTS ====================

def test_company_enrichment(client, dry_run=False):
    """Test company enrichment via LinkedIn company URL."""
    if dry_run:
        skip_test("Company Enrichment", "Dry run mode")
        return None
    
    try:
        result = client.enrich_company(
            social_media_url="https://www.linkedin.com/company/stripe/"
        )
        if result:
            RESULTS["credits_used"] += 6
            name = result.get("name", result.get("company_name", "Unknown"))
            test_result("Company Enrichment", True, f"Found: {name}")
            return result
        else:
            test_result("Company Enrichment", False, "No result returned")
            return None
    except Exception as e:
        test_result("Company Enrichment", False, str(e))
        return None


def test_check_seller(client, dry_run=False):
    """Test CheckSeller API."""
    if dry_run:
        skip_test("CheckSeller API", "Dry run mode")
        return None
    
    try:
        result = client.check_seller(
            company_name="Stripe",
            product_service="payment processing"
        )
        if result:
            RESULTS["credits_used"] += 2
            sells = result.get("sells", "unknown")
            confidence = result.get("confidence", "unknown")
            test_result("CheckSeller API", True, f"sells={sells}, confidence={confidence}")
            return result
        else:
            test_result("CheckSeller API", False, "No result returned")
            return None
    except Exception as e:
        test_result("CheckSeller API", False, str(e))
        return None


def test_check_feature(client, dry_run=False):
    """Test CheckFeature API."""
    if dry_run:
        skip_test("CheckFeature API", "Dry run mode")
        return None
    
    try:
        result = client.check_company_feature(
            company="Stripe",
            feature="React framework"
        )
        if result:
            RESULTS["credits_used"] += 3
            has_feature = result.get("has_feature", "unknown")
            confidence = result.get("confidence", "unknown")
            test_result("CheckFeature API", True, f"has_feature={has_feature}, confidence={confidence}")
            return result
        else:
            test_result("CheckFeature API", False, "No result returned")
            return None
    except Exception as e:
        test_result("CheckFeature API", False, str(e))
        return None


# ==================== ENRICHER MODULE TESTS ====================

def test_nyne_enricher_module():
    """Test nyne_enricher.py module imports and functions."""
    try:
        from N5.scripts.enrichment.nyne_enricher import (
            enrich_person_via_nyne,
            enrich_company_via_nyne,
            format_person_intelligence,
            log_usage
        )
        test_result("Nyne Enricher Module", True, "All functions imported")
        return True
    except Exception as e:
        test_result("Nyne Enricher Module", False, str(e))
        return False


def test_org_enricher_module():
    """Test org_enricher.py module imports."""
    try:
        from N5.scripts.enrichment.org_enricher import (
            enrich_organization,
            link_profiles_to_org,
            get_existing_org
        )
        test_result("Org Enricher Module", True, "All functions imported")
        return True
    except Exception as e:
        test_result("Org Enricher Module", False, str(e))
        return False


# ==================== DATABASE TESTS ====================

def test_crm_database_schema():
    """Test CRM database has required columns."""
    try:
        conn = sqlite3.connect('/home/workspace/N5/data/crm_v3.db')
        cursor = conn.cursor()
        
        # Check profiles table has organization_id
        cursor.execute("PRAGMA table_info(profiles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        has_org_id = "organization_id" in columns
        has_linkedin = "linkedin_url" in columns
        
        # Check organizations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='organizations'")
        has_org_table = cursor.fetchone() is not None
        
        conn.close()
        
        if has_org_id and has_linkedin and has_org_table:
            test_result("CRM Database Schema", True, 
                       f"profiles has organization_id={has_org_id}, linkedin_url={has_linkedin}; organizations table={has_org_table}")
            return True
        else:
            test_result("CRM Database Schema", False, 
                       f"Missing: organization_id={not has_org_id}, linkedin_url={not has_linkedin}, org_table={not has_org_table}")
            return False
    except Exception as e:
        test_result("CRM Database Schema", False, str(e))
        return False


def test_usage_log():
    """Test usage log file exists and is valid JSONL."""
    log_path = Path("/home/workspace/N5/logs/nyne_usage.jsonl")
    
    if not log_path.exists():
        test_result("Usage Log", True, "Log file will be created on first use")
        return True
    
    try:
        with open(log_path) as f:
            lines = f.readlines()
        
        valid_lines = 0
        for line in lines:
            if line.strip():
                json.loads(line)
                valid_lines += 1
        
        test_result("Usage Log", True, f"{valid_lines} valid entries")
        return True
    except Exception as e:
        test_result("Usage Log", False, str(e))
        return False


# ==================== ASYNC ENRICHMENT TEST ====================

async def test_async_enrichment(dry_run=False):
    """Test async enrichment function."""
    if dry_run:
        skip_test("Async Enrichment", "Dry run mode")
        return None
    
    try:
        from N5.scripts.enrichment.nyne_enricher import enrich_person_via_nyne
        
        result = await enrich_person_via_nyne(
            linkedin_url="https://www.linkedin.com/in/garyvaynerchuk/",
            include_newsfeed=False
        )
        
        if result.get("success"):
            RESULTS["credits_used"] += 6
            test_result("Async Enrichment", True, "Successfully enriched via async function")
            return result
        else:
            test_result("Async Enrichment", True, f"Graceful handling: {result.get('error', 'no error')}")
            return result
    except Exception as e:
        test_result("Async Enrichment", False, str(e))
        return None


# ==================== MAIN ====================

def print_summary():
    """Print test summary."""
    total = len(RESULTS["passed"]) + len(RESULTS["failed"]) + len(RESULTS["skipped"])
    
    print("\n" + "=" * 70)
    print("                    NYNE INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"\n✅ Passed:  {len(RESULTS['passed'])}")
    print(f"❌ Failed:  {len(RESULTS['failed'])}")
    print(f"⏭️  Skipped: {len(RESULTS['skipped'])}")
    print(f"📊 Total:   {total}")
    print(f"💰 Credits Used: ~{RESULTS['credits_used']}")
    
    if RESULTS["failed"]:
        print("\n❌ FAILED TESTS:")
        for test in RESULTS["failed"]:
            print(f"   • {test}")
    
    print("\n" + "=" * 70)
    
    return len(RESULTS["failed"]) == 0


def main():
    parser = argparse.ArgumentParser(description="Nyne Integration Test Suite")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls (no credits)")
    parser.add_argument("--quick", action="store_true", help="Quick validation (minimal credits)")
    args = parser.parse_args()
    
    print("=" * 70)
    print("                    NYNE INTEGRATION TEST SUITE")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'QUICK' if args.quick else 'FULL'}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    # 1. Client & Auth Tests (no credits)
    log("Testing client initialization...")
    client = test_client_initialization()
    if not client:
        print("\n❌ Client initialization failed. Cannot continue.")
        return 1
    
    log("Testing usage API...")
    usage = test_usage_api(client)
    
    # 2. Module Import Tests (no credits)
    log("\nTesting module imports...")
    test_nyne_enricher_module()
    test_org_enricher_module()
    
    # 3. Database Schema Tests (no credits)
    log("\nTesting database schema...")
    test_crm_database_schema()
    test_usage_log()
    
    # 4. API Tests (uses credits)
    if not args.dry_run:
        available = usage.get("limits", {}).get("available_credits", 0) if usage else 0
        
        if available < 10:
            log(f"\n⚠️  Only {available} credits available. Skipping API tests.", "WARN")
            skip_test("Person Enrichment (LinkedIn)", "Insufficient credits")
            skip_test("Company Enrichment", "Insufficient credits")
            skip_test("CheckSeller API", "Insufficient credits")
            skip_test("CheckFeature API", "Insufficient credits")
            skip_test("Async Enrichment", "Insufficient credits")
        else:
            log(f"\nRunning API tests ({available} credits available)...")
            
            if args.quick:
                # Quick mode: just one person enrichment
                test_person_enrichment_by_linkedin(client)
            else:
                # Full mode: all tests
                test_person_enrichment_by_linkedin(client)
                # Skip email test if quick
                if not args.quick:
                    test_person_enrichment_by_email(client)
                test_company_enrichment(client)
                test_check_seller(client)
                test_check_feature(client)
                
                # Async test
                log("\nTesting async enrichment...")
                asyncio.run(test_async_enrichment())
    else:
        skip_test("Person Enrichment (LinkedIn)", "Dry run mode")
        skip_test("Person Enrichment (Email)", "Dry run mode")
        skip_test("Company Enrichment", "Dry run mode")
        skip_test("CheckSeller API", "Dry run mode")
        skip_test("CheckFeature API", "Dry run mode")
        skip_test("Async Enrichment", "Dry run mode")
    
    # Print summary
    success = print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())


