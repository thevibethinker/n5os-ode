#!/usr/bin/env python3
"""
Email Staging LLM Processor - Phase 2 of Option B Architecture

Reads staged email JSON files and uses LLM (via Zo agent context) to extract
stakeholder information, then writes to Knowledge/Records.

Architecture:
  Phase 1 (gmail_fetch_staging.py): Service Account → Gmail API → Staging JSON
  Phase 2 (this script): Read Staging → LLM Extract → Knowledge/Records

NOTE: This script is designed to be called BY the Zo agent during scheduled
task execution. The agent has native LLM access and will inject LLM analysis.
"""

import logging
import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
log = logging.getLogger(__name__)

# Configuration
WORKSPACE_ROOT = Path("/home/workspace")
STAGING_ROOT = WORKSPACE_ROOT / "Records/Temporary/email_staging"
STAKEHOLDER_INDEX = WORKSPACE_ROOT / "Knowledge/stakeholder/index.md"
RECORDS_STAGING = WORKSPACE_ROOT / "Records/stakeholder_discovery"


def load_staging_files() -> List[Path]:
    """Load all unprocessed staging files"""
    staging_files = []
    
    if not STAGING_ROOT.exists():
        log.warning(f"Staging directory does not exist: {STAGING_ROOT}")
        return staging_files
    
    for date_dir in sorted(STAGING_ROOT.iterdir()):
        if not date_dir.is_dir():
            continue
        
        for json_file in sorted(date_dir.glob("msg_*.json")):
            staging_files.append(json_file)
    
    return staging_files


def extract_stakeholder_with_llm(email_data: Dict) -> Optional[Dict]:
    """
    Use LLM to extract rich stakeholder information from email.
    
    This function is a PLACEHOLDER for LLM injection by the Zo agent.
    When executed in scheduled task context, the agent will replace this
    with actual LLM analysis.
    
    Returns Dict with extracted stakeholder data or None if no actionable info.
    """
    
    # Build LLM prompt
    prompt = f"""Extract external stakeholder information from this email.

Subject: {email_data['subject']}
From: {email_data['from']}
To: {', '.join(email_data['to'])}
Cc: {', '.join(email_data['cc'])}
Date: {email_data['date']}

Body excerpt:
{email_data['body'][:2000]}

External participants: {', '.join(email_data['external_emails'])}

TASK:
For EACH external participant, extract:
1. Full name (from signature, email display name, or body)
2. Email address
3. Organization/company (infer from:
   - Email signature
   - Email domain (but get actual company name, not just domain)
   - Context in email body)
4. Job title/role (from signature or context)
5. Meeting context (what is this meeting about? relationship type?)
6. Decision-maker assessment (are they likely a decision-maker or support staff?)

RULES:
- Only extract EXTERNAL participants (not from mycareerspan.com, theapply.ai, zo.computer)
- If you can't determine a field confidently, use null
- For organization: prefer full company name over domain (e.g., "McKinsey & Company" not "mckinsey.com")
- For context: be specific about the business relationship or meeting purpose

Return ONLY valid JSON array:
[
  {{
    "name": "Full Name or null",
    "email": "email@domain.com",
    "organization": "Company Name or null",
    "title": "Job Title or null",
    "context": "Meeting purpose and relationship context",
    "is_decision_maker": true/false/null
  }}
]

If no actionable stakeholder info, return []
"""
    
    # NOTE: When this runs in scheduled task context, the Zo agent will
    # inject actual LLM analysis here. For now, return empty to signal
    # that LLM processing is needed.
    
    log.info("   [LLM PLACEHOLDER] This will be replaced by agent LLM analysis")
    return None


def write_stakeholder_record(stakeholder_data: Dict, source_email: Dict) -> Path:
    """Write stakeholder discovery record"""
    RECORDS_STAGING.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"discovery_{stakeholder_data['email']}_{timestamp}.json"
    filepath = RECORDS_STAGING / filename
    
    record = {
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "source": "email_scanner",
        "source_message_id": source_email['message_id'],
        "source_subject": source_email['subject'],
        "stakeholder": stakeholder_data
    }
    
    filepath.write_text(json.dumps(record, indent=2))
    return filepath


def process_staging_files(dry_run: bool = False) -> Dict:
    """
    Main function: Process staged emails with LLM extraction.
    """
    log.info("=== Email Staging LLM Processor (Phase 2) ===")
    
    # Load staging files
    staging_files = load_staging_files()
    log.info(f"✓ Found {len(staging_files)} staging files")
    
    if not staging_files:
        return {"status": "success", "processed": 0, "discoveries": 0}
    
    processed_count = 0
    discovery_count = 0
    
    for filepath in staging_files:
        try:
            email_data = json.loads(filepath.read_text())
            log.info(f"\nProcessing: {filepath.name}")
            log.info(f"   Subject: {email_data['subject'][:60]}")
            log.info(f"   External emails: {len(email_data['external_emails'])}")
            
            # Extract stakeholders with LLM
            stakeholders = extract_stakeholder_with_llm(email_data)
            
            if stakeholders is None:
                log.warning("   LLM extraction returned None (placeholder mode)")
                continue
            
            if not stakeholders:
                log.info("   No actionable stakeholder info")
            else:
                log.info(f"   ✓ Extracted {len(stakeholders)} stakeholder(s)")
                
                for stakeholder in stakeholders:
                    if dry_run:
                        log.info(f"      [DRY RUN] Would record: {stakeholder['email']}")
                        log.info(f"         Name: {stakeholder.get('name')}")
                        log.info(f"         Org: {stakeholder.get('organization')}")
                    else:
                        record_path = write_stakeholder_record(stakeholder, email_data)
                        log.info(f"      ✓ Recorded: {record_path.name}")
                        discovery_count += 1
            
            processed_count += 1
            
            # Clean up staging file after processing
            if not dry_run:
                filepath.unlink()
                log.info(f"   ✓ Cleaned staging file")
            
        except Exception as e:
            log.error(f"   Error processing {filepath.name}: {e}")
            continue
    
    log.info(f"\n✓ Complete: {processed_count} emails processed, {discovery_count} discoveries")
    
    return {
        "status": "success",
        "processed": processed_count,
        "discoveries": discovery_count
    }


def main(dry_run: bool = False) -> int:
    """Main execution"""
    try:
        result = process_staging_files(dry_run=dry_run)
        
        if result['status'] == 'success':
            return 0
        else:
            log.error(f"Processing failed: {result.get('error')}")
            return 1
            
    except Exception as e:
        log.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email staging LLM processor (Phase 2)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run))
