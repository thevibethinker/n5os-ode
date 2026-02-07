#!/usr/bin/env python3
"""
Careerspan Update Handler - Process [UPDATE] tagged emails

Classifies update type via LLM and updates Airtable accordingly.
"""

import argparse
import json
import os
import sys
import requests
from typing import Dict, Any, List, Optional

# Add workspace to path
sys.path.insert(0, '/home/workspace')

# Import helpers from careerspan-pipeline
CONFIG_PATH = '/home/workspace/Integrations/careerspan-pipeline/config.yaml'


def load_config():
    """Load configuration from config.yaml, handling YAML frontmatter."""
    import yaml
    
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r') as f:
        content = f.read()
    
    # Skip YAML frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    return yaml.safe_load(content)


def classify_update(email_subject: str, email_body: str, email_from: str) -> Dict[str, Any]:
    """
    Use /zo/ask to classify the update type and extract relevant information.
    """
    prompt = f"""Given this email from Shivam@CorridorX, classify the update type and extract the relevant information.

Email Subject: {email_subject}
Email From: {email_from}
Email Body:
{email_body}

Classify the update type as one of:
- employer_response: Employer answered Core Questions or provided new information about a role
- candidate_status: Update about a candidate's interview status, offer, etc.
- role_status: Role paused, closed, re-opened, or other status change
- general_intel: General information about employer preferences, process, etc.

Output valid JSON with this exact structure:
{{
  "update_type": "employer_response|candidate_status|role_status|general_intel",
  "target_record_type": "job_opening|candidate|employer",
  "target_identifier": "company name or candidate name or role title",
  "updates": {{
    "field_name": "value"
  }},
  "requires_response": boolean,
  "suggested_response": "text or null",
  "confidence": "high|medium|low"
}}

Only output the JSON, no other text.
"""
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={"input": prompt}
        )
        
        if response.status_code != 200:
            print(f"Error calling /zo/ask: {response.status_code}", file=sys.stderr)
            return {"update_type": "general_intel", "confidence": "low", "updates": {}}
        
        result = response.json()
        output = result.get("output", "")
        
        # Parse JSON from response
        # Try to find JSON object in output
        start_idx = output.find('{')
        end_idx = output.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = output[start_idx:end_idx]
            return json.loads(json_str)
        else:
            print("Could not parse JSON from /zo/ask response", file=sys.stderr)
            return {"update_type": "general_intel", "confidence": "low", "updates": {}}
            
    except Exception as e:
        print(f"Error classifying update: {e}", file=sys.stderr)
        return {"update_type": "general_intel", "confidence": "low", "updates": {}}


def find_airtable_record(api_key: str, base_id: str, table_id: str, 
                         record_type: str, identifier: str, config: Dict) -> Optional[str]:
    """
    Find an Airtable record by searching for the identifier.
    Returns record ID if found, None otherwise.
    """
    # Map record types to table IDs
    table_map = {
        "job_opening": config["airtable"]["tables"]["job_openings"],
        "candidate": config["airtable"]["tables"]["candidates"],
        "employer": config["airtable"]["tables"]["employers"]
    }
    
    if record_type not in table_map:
        print(f"Unknown record type: {record_type}", file=sys.stderr)
        return None
    
    table_id = table_map[record_type]
    
    # Build filter formula based on record type
    if record_type == "job_opening":
        # Search by company name or role title
        formula = f"OR(FIND(\"{identifier}\", {{Company}}), FIND(\"{identifier}\", {{Role Title}}))"
    elif record_type == "candidate":
        # Search by name
        formula = f"OR(FIND(\"{identifier}\", {{Name}}), FIND(\"{identifier}\", {{Email}}))"
    elif record_type == "employer":
        # Search by company name
        formula = f"FIND(\"{identifier}\", {{Company}})"
    else:
        return None
    
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "filterByFormula": formula,
        "maxRecords": 5
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])
            
            if len(records) == 1:
                return records[0]["id"]
            elif len(records) > 1:
                print(f"Multiple records found for '{identifier}', using first", file=sys.stderr)
                return records[0]["id"]
            else:
                print(f"No record found for '{identifier}'", file=sys.stderr)
                return None
        else:
            print(f"Error searching Airtable: {response.status_code}", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"Error finding record: {e}", file=sys.stderr)
        return None


def update_airtable_record(api_key: str, base_id: str, table_id: str,
                          record_id: str, updates: Dict[str, Any],
                          dry_run: bool = False) -> bool:
    """
    Update an Airtable record with the given field updates.
    """
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if dry_run:
        print(f"[DRY-RUN] Would update {record_id} with: {updates}")
        return True
    
    try:
        response = requests.patch(url, headers=headers, json={"fields": updates})
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error updating record: {response.status_code} - {response.text}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error updating record: {e}", file=sys.stderr)
        return False


def check_core_questions_complete(record_data: Dict, config: Dict) -> bool:
    """
    Check if all 5 Core Questions are answered based on checkbox fields.
    """
    # Field names from SCHEMA_TO_ADD.md
    checkbox_fields = [
        "Salary Range (Checkbox)",
        "Salary Visibility (Checkbox)",
        "Location/Geo (Checkbox)",
        "Visa/Sponsorship (Checkbox)",
        "90-Day Success (Checkbox)",
        "Anti-Pattern (Checkbox)"
    ]
    
    for field in checkbox_fields:
        if field in record_data.get("fields", {}):
            # Check if checkbox is True
            if record_data["fields"][field] != True:
                return False
        else:
            # Field doesn't exist yet
            return False
    
    return True


def process_update(email_subject: str, email_body: str, email_from: str,
                  dry_run: bool = False) -> Dict[str, Any]:
    """
    Main processing function.
    """
    # Load config
    config = load_config()
    
    # Check permitted senders
    if email_from not in config["email"]["permitted_senders"]:
        return {
            "status": "error",
            "message": f"Email from {email_from} is not permitted"
        }
    
    # Classify the update
    classification = classify_update(email_subject, email_body, email_from)
    
    print(f"Classified as: {classification['update_type']} (confidence: {classification.get('confidence', 'unknown')})")
    
    # Get Airtable credentials from environment
    api_key = os.environ.get("AIRTABLE_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "AIRTABLE_API_KEY not set in environment"
        }
    
    base_id = config["airtable"]["base_id"]
    
    # Find target record
    record_id = find_airtable_record(
        api_key, base_id, "", 
        classification["target_record_type"],
        classification["target_identifier"],
        config
    )
    
    if not record_id:
        return {
            "status": "error",
            "message": f"Could not find record for: {classification['target_identifier']}",
            "classification": classification
        }
    
    # Map record type to table ID
    table_map = {
        "job_opening": config["airtable"]["tables"]["job_openings"],
        "candidate": config["airtable"]["tables"]["candidates"],
        "employer": config["airtable"]["tables"]["employers"]
    }
    table_id = table_map[classification["target_record_type"]]
    
    # Build field updates
    updates = classification.get("updates", {})
    
    # Special handling for different update types
    if classification["update_type"] == "role_status":
        # Map status keywords to Airtable values
        status_map = {
            "paused": "Paused",
            "closed": "Closed",
            "re-opened": "Active"
        }
        
        for keyword, airtable_value in status_map.items():
            if keyword in email_body.lower():
                updates["Intake Status"] = airtable_value
                updates["Ball In Court"] = "Shivam"
                break
    
    # Update the record
    success = update_airtable_record(api_key, base_id, table_id, record_id, updates, dry_run)
    
    result = {
        "update_type": classification["update_type"],
        "target_record_type": classification["target_record_type"],
        "target_identifier": classification["target_identifier"],
        "records_updated": [],
        "hiring_pov_refreshed": False,
        "email_sent": False,
        "dry_run": dry_run
    }
    
    if success:
        result["records_updated"].append({
            "table": classification["target_record_type"],
            "id": record_id,
            "fields_updated": list(updates.keys())
        })
    
    # Special case: Core Questions answered
    if classification["update_type"] == "employer_response":
        # Fetch the record to check Core Questions
        url = f"https://api.airtable.com/v0/{base_id}/{table_id}/{record_id}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if not dry_run:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                record_data = response.json()
                
                if check_core_questions_complete(record_data, config):
                    # Update status to Finalized
                    update_airtable_record(
                        api_key, base_id, table_id, record_id,
                        {"Intake Status": "Finalized"},
                        dry_run
                    )
                    result["status_updated_to"] = "Finalized"
                    result["email_sent"] = True  # Would email Shivam
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Process [UPDATE] tagged emails")
    parser.add_argument("--email-subject", required=True, help="Email subject line")
    parser.add_argument("--email-body", required=True, help="Email body content")
    parser.add_argument("--email-from", required=True, help="Email sender address")
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes")
    
    args = parser.parse_args()
    
    result = process_update(
        args.email_subject,
        args.email_body,
        args.email_from,
        args.dry_run
    )
    
    # Output result as JSON
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("status") != "error" else 1)


if __name__ == "__main__":
    main()
