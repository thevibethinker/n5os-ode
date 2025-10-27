#!/usr/bin/env python3
"""
Tally Survey Manager
Programmatic creation and management of Tally.so surveys via API

Usage:
    python3 tally_manager.py create --title "Survey Title" --description "Survey description"
    python3 tally_manager.py list
    python3 tally_manager.py get --form-id wdeWZD
    python3 tally_manager.py submissions --form-id wdeWZD
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
N5_ROOT = Path("/home/workspace/N5")
ENV_FILE = N5_ROOT / "config" / "tally_api_key.env"


class TallyAPI:
    """Tally.so API Client"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.tally.so"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            
            if response.status_code == 429:
                logger.error("Rate limit exceeded (100 requests/minute)")
                return {"error": "rate_limit", "message": "Rate limit exceeded"}
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return {"error": "http_error", "message": str(e)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": "request_failed", "message": str(e)}
        except json.JSONDecodeError:
            logger.error("Invalid JSON response")
            return {"error": "invalid_json", "message": "Server returned invalid JSON"}
    
    def list_forms(self, page: int = 1) -> Dict:
        """List all forms"""
        return self._request("GET", f"forms?page={page}")
    
    def get_form(self, form_id: str) -> Dict:
        """Get specific form details"""
        return self._request("GET", f"forms/{form_id}")
    
    def create_form(self, form_data: Dict) -> Dict:
        """Create new form"""
        return self._request("POST", "forms", json=form_data)
    
    def update_form(self, form_id: str, form_data: Dict) -> Dict:
        """Update existing form"""
        return self._request("PATCH", f"forms/{form_id}", json=form_data)
    
    def delete_form(self, form_id: str) -> Dict:
        """Delete form"""
        return self._request("DELETE", f"forms/{form_id}")
    
    def list_submissions(self, form_id: str, page: int = 1, filter_type: str = "all") -> Dict:
        """List form submissions"""
        return self._request("GET", f"forms/{form_id}/submissions?page={page}&filter={filter_type}")
    
    def get_user_info(self) -> Dict:
        """Get current user information"""
        return self._request("GET", "users/me")


class FormBuilder:
    """Build Tally forms from natural language descriptions"""
    
    BLOCK_TYPES = {
        "text": "INPUT_TEXT",
        "email": "INPUT_EMAIL",
        "number": "INPUT_NUMBER",
        "phone": "INPUT_PHONE_NUMBER",
        "url": "INPUT_LINK",
        "date": "INPUT_DATE",
        "time": "INPUT_TIME",
        "textarea": "TEXTAREA",
        "multiple_choice": "MULTIPLE_CHOICE",
        "dropdown": "DROPDOWN",
        "rating": "RATING",
        "scale": "LINEAR_SCALE",
        "file": "FILE_UPLOAD"
    }
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID for block"""
        return str(uuid.uuid4())
    
    @staticmethod
    def create_form_title(title: str, description: str = "") -> Dict:
        """Create form title block"""
        return {
            "uuid": FormBuilder.generate_uuid(),
            "type": "FORM_TITLE",
            "groupUuid": FormBuilder.generate_uuid(),
            "groupType": "TEXT",
            "payload": {
                "title": title,
                "html": description or title
            }
        }
    
    @staticmethod
    def create_text_input(label: str, required: bool = False, placeholder: str = "") -> List[Dict]:
        """Create text input field with title - returns list of blocks"""
        group_uuid = FormBuilder.generate_uuid()
        return [
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "TITLE",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "html": label
                }
            },
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "INPUT_TEXT",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "isRequired": required,
                    "placeholder": placeholder
                }
            }
        ]
    
    @staticmethod
    def create_email_input(label: str = "Email", required: bool = True) -> List[Dict]:
        """Create email input field with title - returns list of blocks"""
        group_uuid = FormBuilder.generate_uuid()
        return [
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "TITLE",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "html": label
                }
            },
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "INPUT_EMAIL",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "isRequired": required
                }
            }
        ]
    
    @staticmethod
    def create_textarea(label: str, required: bool = False, placeholder: str = "") -> List[Dict]:
        """Create textarea field with title - returns list of blocks"""
        group_uuid = FormBuilder.generate_uuid()
        return [
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "TITLE",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "html": label
                }
            },
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "TEXTAREA",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "isRequired": required,
                    "placeholder": placeholder
                }
            }
        ]
    
    @staticmethod
    def create_multiple_choice(label: str, options: List[str], required: bool = False) -> List[Dict]:
        """Create multiple choice field with title - returns list of blocks"""
        group_uuid = FormBuilder.generate_uuid()
        return [
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "TITLE",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "html": label
                }
            },
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "MULTIPLE_CHOICE",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "isRequired": required,
                    "options": [{"text": opt} for opt in options]
                }
            }
        ]
    
    @staticmethod
    def create_rating(label: str, max_rating: int = 5, required: bool = False) -> List[Dict]:
        """Create rating field with title - returns list of blocks"""
        group_uuid = FormBuilder.generate_uuid()
        return [
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "TITLE",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "html": label
                }
            },
            {
                "uuid": FormBuilder.generate_uuid(),
                "type": "LINEAR_SCALE",
                "groupUuid": group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "isRequired": required,
                    "min": 1,
                    "max": max_rating
                }
            }
        ]


def load_api_key() -> str:
    """Load API key from environment file"""
    if not ENV_FILE.exists():
        logger.error(f"API key file not found: {ENV_FILE}")
        sys.exit(1)
    
    with open(ENV_FILE) as f:
        for line in f:
            if line.startswith("TALLY_API_KEY="):
                return line.split("=", 1)[1].strip()
    
    logger.error("TALLY_API_KEY not found in config")
    sys.exit(1)


def cmd_list(api: TallyAPI, args):
    """List all forms"""
    logger.info("Fetching forms...")
    result = api.list_forms()
    
    if "error" in result:
        print(f"❌ Error: {result['message']}")
        return 1
    
    forms = result.get("items", [])
    print(f"\n📋 Found {len(forms)} form(s):\n")
    
    for form in forms:
        status_icon = "✅" if form["status"] == "PUBLISHED" else "📝"
        print(f"{status_icon} {form['name']}")
        print(f"   ID: {form['id']}")
        print(f"   Status: {form['status']}")
        print(f"   Submissions: {form['numberOfSubmissions']}")
        print(f"   Created: {form['createdAt']}")
        print(f"   URL: https://tally.so/r/{form['id']}\n")
    
    return 0


def cmd_get(api: TallyAPI, args):
    """Get form details"""
    logger.info(f"Fetching form {args.form_id}...")
    result = api.get_form(args.form_id)
    
    if "error" in result:
        print(f"❌ Error: {result['message']}")
        return 1
    
    print(f"\n📝 Form: {result['name']}")
    print(f"Status: {result['status']}")
    print(f"Submissions: {result.get('numberOfSubmissions', 'N/A')}")
    print(f"URL: https://tally.so/r/{result['id']}")
    
    if args.json:
        print("\n" + json.dumps(result, indent=2))
    
    return 0


def cmd_submissions(api: TallyAPI, args):
    """List form submissions"""
    logger.info(f"Fetching submissions for form {args.form_id}...")
    result = api.list_submissions(args.form_id, page=args.page, filter_type=args.filter)
    
    if "error" in result:
        print(f"❌ Error: {result['message']}")
        return 1
    
    submissions = result.get("submissions", [])
    print(f"\n📊 Found {len(submissions)} submission(s) (page {args.page}):\n")
    
    for sub in submissions:
        completed_icon = "✅" if sub["isCompleted"] else "⏳"
        print(f"{completed_icon} Submission {sub['id']}")
        print(f"   Submitted: {sub['submittedAt']}")
        print(f"   Respondent: {sub.get('respondentId', 'N/A')}")
        
        if args.verbose:
            for response in sub.get("responses", []):
                print(f"      → {response.get('value', 'N/A')}")
        print()
    
    if result.get("hasMore"):
        print(f"💡 More results available. Use --page {args.page + 1}")
    
    return 0


def cmd_create(api: TallyAPI, args):
    """Create new form"""
    logger.info(f"Creating form: {args.title}")
    
    # Build form structure
    blocks = [FormBuilder.create_form_title(args.title, args.description)]
    
    # Add default fields if requested
    if args.quick:
        # Extend with flattened blocks (each field method now returns list)
        for field_blocks in [
            FormBuilder.create_text_input("Name", required=True),
            FormBuilder.create_email_input(),
            FormBuilder.create_textarea("Comments")
        ]:
            blocks.extend(field_blocks)
    
    form_data = {
        "status": "DRAFT" if args.draft else "PUBLISHED",
        "blocks": blocks
    }
    
    if args.workspace:
        form_data["workspaceId"] = args.workspace
    
    result = api.create_form(form_data)
    
    if "error" in result:
        print(f"❌ Error: {result['message']}")
        return 1
    
    print(f"\n✅ Form created successfully!")
    print(f"   Name: {result['name']}")
    print(f"   ID: {result['id']}")
    print(f"   Status: {result['status']}")
    print(f"   URL: https://tally.so/r/{result['id']}")
    print(f"   Edit: https://tally.so/forms/{result['id']}/edit")
    
    return 0


def cmd_user(api: TallyAPI, args):
    """Get user information"""
    logger.info("Fetching user info...")
    result = api.get_user_info()
    
    if "error" in result:
        print(f"❌ Error: {result['message']}")
        return 1
    
    print(f"\n👤 {result['fullName']} ({result['email']})")
    print(f"   Plan: {result['subscriptionPlan']}")
    print(f"   Organization: {result['organizationId']}")
    print(f"   Timezone: {result['timezone']}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Tally Survey Manager")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    subparsers.add_parser("list", help="List all forms")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get form details")
    get_parser.add_argument("--form-id", required=True, help="Form ID")
    get_parser.add_argument("--json", action="store_true", help="Output full JSON")
    
    # Submissions command
    sub_parser = subparsers.add_parser("submissions", help="List form submissions")
    sub_parser.add_argument("--form-id", required=True, help="Form ID")
    sub_parser.add_argument("--page", type=int, default=1, help="Page number")
    sub_parser.add_argument("--filter", choices=["all", "completed", "partial"], default="all")
    sub_parser.add_argument("--verbose", "-v", action="store_true", help="Show responses")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new form")
    create_parser.add_argument("--title", required=True, help="Form title")
    create_parser.add_argument("--description", default="", help="Form description")
    create_parser.add_argument("--draft", action="store_true", help="Create as draft")
    create_parser.add_argument("--workspace", help="Workspace ID")
    create_parser.add_argument("--quick", action="store_true", help="Add default fields")
    
    # User command
    subparsers.add_parser("user", help="Get user information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Load API key and initialize client
    api_key = load_api_key()
    api = TallyAPI(api_key)
    
    # Route to command
    commands = {
        "list": cmd_list,
        "get": cmd_get,
        "submissions": cmd_submissions,
        "create": cmd_create,
        "user": cmd_user
    }
    
    return commands[args.command](api, args)


if __name__ == "__main__":
    sys.exit(main())
