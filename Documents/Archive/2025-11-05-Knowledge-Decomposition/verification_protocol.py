#!/usr/bin/env python3
"""
Verification Protocol: Check decomposed knowledge against source for hallucinations
"""

import re
from pathlib import Path

# Key claims to verify - sample from each decomposed file
VERIFICATION_SAMPLES = [
    {
        "file": "Knowledge/stable/company/positioning.md",
        "claim": "quality-of-hire prediction infrastructure",
        "source_section": "Section 1.1",
        "critical": True
    },
    {
        "file": "Knowledge/stable/company/overview.md",
        "claim": "Three-Layer Moat",
        "source_section": "Section 1.2",
        "critical": True
    },
    {
        "file": "Knowledge/semi_stable/current_metrics.md",
        "claim": "20% D30 retention",
        "source_section": "Section 1.3",
        "critical": True  # Metrics must be exact
    },
    {
        "file": "Knowledge/semi_stable/current_metrics.md",
        "claim": "50%+ multi-session",
        "source_section": "Section 1.3",
        "critical": True
    },
    {
        "file": "Knowledge/market_intelligence/competitive_landscape_2024.md",
        "claim": "ZipRecruiter",
        "source_section": "Section 3",
        "critical": False
    },
    {
        "file": "Knowledge/patterns/two_sided_marketplace_patterns.md",
        "claim": "engagement as moat multiplier",
        "source_section": "Section 7",
        "critical": True
    }
]

def check_claim_in_file(claim, filepath):
    """Check if claim exists in file"""
    try:
        content = Path(filepath).read_text()
        return claim.lower() in content.lower()
    except:
        return False

def check_claim_in_source(claim, source_path):
    """Check if claim exists in source report"""
    try:
        content = Path(source_path).read_text()
        return claim.lower() in content.lower()
    except:
        return False

def main():
    source_path = "/home/.z/workspaces/con_kSq36OtO8rmECYtW/Careerspan_Complete_Strategic_Intelligence_Report.md"
    workspace = "/home/workspace"
    
    print("VERIFICATION PROTOCOL: Checking for hallucinations\n")
    print("=" * 70)
    
    issues = []
    verified = []
    
    for sample in VERIFICATION_SAMPLES:
        file_path = f"{workspace}/{sample['file']}"
        claim = sample['claim']
        
        in_decomposed = check_claim_in_file(claim, file_path)
        in_source = check_claim_in_source(claim, source_path)
        
        status = "✓" if (in_decomposed and in_source) else "✗"
        
        print(f"\n{status} Claim: '{claim}'")
        print(f"   File: {sample['file']}")
        print(f"   In decomposed file: {in_decomposed}")
        print(f"   In source report: {in_source}")
        print(f"   Critical: {sample['critical']}")
        
        if in_decomposed and not in_source:
            issues.append(f"HALLUCINATION RISK: '{claim}' in {sample['file']} but NOT in source")
        elif in_decomposed and in_source:
            verified.append(claim)
        elif not in_decomposed:
            issues.append(f"MISSING: '{claim}' not found in {sample['file']}")
    
    print("\n" + "=" * 70)
    print(f"\n✓ Verified claims: {len(verified)}/{len(VERIFICATION_SAMPLES)}")
    
    if issues:
        print(f"\n⚠ Issues found: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("\n✓ No hallucinations detected in sample")
        return 0

if __name__ == "__main__":
    exit(main())
