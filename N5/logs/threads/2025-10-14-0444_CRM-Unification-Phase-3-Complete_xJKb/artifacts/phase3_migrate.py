#!/usr/bin/env python3
"""Phase 3: Stakeholder → CRM Profile Migration with Duplicate Detection"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
STAKEHOLDERS_DIR = WORKSPACE / "N5/stakeholders"
CRM_PROFILES_DIR = WORKSPACE / "Knowledge/crm/profiles"
CRM_INDEX = WORKSPACE / "Knowledge/crm/index.jsonl"

def load_stakeholder_index() -> List[Dict]:
    """Load stakeholder index"""
    with open(STAKEHOLDERS_DIR / "index.jsonl") as f:
        return [json.loads(line) for line in f if line.strip()]

def load_crm_profiles() -> Dict[str, Path]:
    """Map emails to existing CRM profiles"""
    email_to_file = {}
    for profile_path in CRM_PROFILES_DIR.glob("*.md"):
        if profile_path.name.startswith("_"):
            continue
        content = profile_path.read_text()
        # Extract email from markdown (look for **Email:** pattern)
        for line in content.split("\n"):
            if "**Email:**" in line or "- **Email:**" in line:
                email = line.split("**Email:**")[-1].strip().strip("`,")
                if email and "@" in email:
                    email_to_file[email.lower()] = profile_path
                    break
    return email_to_file

def migrate_profiles(dry_run: bool = False) -> Dict:
    """Migrate stakeholder profiles to CRM, detecting duplicates"""
    stakeholders = load_stakeholder_index()
    existing_crm = load_crm_profiles()
    
    results = {
        "migrated": [],
        "skipped_duplicates": [],
        "errors": []
    }
    
    for stakeholder in stakeholders:
        email = stakeholder.get("email", "").lower()
        slug = stakeholder.get("slug") or stakeholder.get("profile_file", "").replace(".md", "")
        source_file = STAKEHOLDERS_DIR / f"{slug}.md"
        
        if not source_file.exists():
            logger.warning(f"Source file not found: {source_file}")
            results["errors"].append({"slug": slug, "reason": "source_not_found"})
            continue
        
        # Check for duplicate by email
        if email in existing_crm:
            logger.info(f"⚠️  DUPLICATE: {slug} ({email}) exists as {existing_crm[email].name}")
            results["skipped_duplicates"].append({
                "slug": slug,
                "email": email,
                "existing_file": existing_crm[email].name
            })
            continue
        
        # Check for duplicate by filename
        target_file = CRM_PROFILES_DIR / f"{slug}.md"
        if target_file.exists():
            logger.info(f"⚠️  DUPLICATE: {slug}.md already exists in CRM profiles")
            results["skipped_duplicates"].append({
                "slug": slug,
                "reason": "filename_conflict"
            })
            continue
        
        # Migrate
        if not dry_run:
            content = source_file.read_text()
            target_file.write_text(content)
            logger.info(f"✅ Migrated: {slug}.md → Knowledge/crm/profiles/")
        else:
            logger.info(f"[DRY RUN] Would migrate: {slug}.md")
        
        results["migrated"].append({
            "slug": slug,
            "email": email,
            "source": str(source_file),
            "target": str(target_file)
        })
    
    return results

def update_crm_index(migrated: List[Dict]) -> None:
    """Update CRM index.jsonl with migrated profiles"""
    with open(CRM_INDEX, "a") as f:
        for profile in migrated:
            entry = {
                "slug": profile["slug"],
                "email": profile["email"],
                "file": f"Knowledge/crm/profiles/{profile['slug']}.md",
                "migrated_from": "N5/stakeholders",
                "migration_date": "2025-10-14"
            }
            f.write(json.dumps(entry) + "\n")
    logger.info(f"✅ Updated CRM index with {len(migrated)} entries")

def main(dry_run: bool = False) -> int:
    try:
        logger.info("Starting Phase 3: Profile Migration")
        
        results = migrate_profiles(dry_run=dry_run)
        
        logger.info(f"\n📊 Migration Summary:")
        logger.info(f"  ✅ Migrated: {len(results['migrated'])}")
        logger.info(f"  ⚠️  Duplicates skipped: {len(results['skipped_duplicates'])}")
        logger.info(f"  ❌ Errors: {len(results['errors'])}")
        
        if results["skipped_duplicates"]:
            logger.info("\n⚠️  Duplicate Details:")
            for dup in results["skipped_duplicates"]:
                logger.info(f"  - {dup}")
        
        if not dry_run and results["migrated"]:
            update_crm_index(results["migrated"])
        
        # Write results to file
        results_file = Path("/home/.z/workspaces/con_AQkMr6eIFcwHUaHp/phase3_results.json")
        results_file.write_text(json.dumps(results, indent=2))
        logger.info(f"\n✅ Results written to: {results_file}")
        
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    exit(main(dry_run=parser.parse_args().dry_run))
