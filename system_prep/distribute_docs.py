#!/usr/bin/env python3
"""
Document Distribution Script
Handles automated distribution of cached documents to various destinations
"""

import os
import shutil
import json
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from cache_manager import CacheManager

class DocumentDistributor:
    def __init__(self, config_file: str = "/home/workspace/system_prep/distribution_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.cache_manager = CacheManager()
    
    def _load_config(self) -> Dict:
        """Load distribution configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "destinations": {
                "local_folders": {},
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": ""
                }
            },
            "rules": []
        }
    
    def _save_config(self):
        """Save distribution configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_local_destination(self, name: str, path: str):
        """Add a local folder destination"""
        self.config["destinations"]["local_folders"][name] = path
        self._save_config()
    
    def add_distribution_rule(self, category: str, destinations: List[str], 
                            conditions: Optional[Dict] = None):
        """Add a distribution rule"""
        rule = {
            "category": category,
            "destinations": destinations,
            "conditions": conditions or {}
        }
        self.config["rules"].append(rule)
        self._save_config()
    
    def distribute_category(self, category: str):
        """Distribute all files in a category according to rules"""
        files = self.cache_manager.list_files(category)
        if not files:
            print(f"No files found in category '{category}'")
            return
        
        # Apply rules for this category
        rules_for_category = [r for r in self.config["rules"] if r["category"] == category]
        
        if not rules_for_category:
            print(f"No distribution rules found for category '{category}'")
            return
        
        distributed_count = 0
        for rule in rules_for_category:
            for destination in rule["destinations"]:
                if destination in self.config["destinations"]["local_folders"]:
                    # Local folder distribution
                    dest_path = Path(self.config["destinations"]["local_folders"][destination])
                    dest_path.mkdir(parents=True, exist_ok=True)
                    
                    for file_info in files:
                        cached_path = file_info["cached_path"]
                        target_path = dest_path / file_info["filename"]
                        shutil.copy2(cached_path, target_path)
                        distributed_count += 1
                
                elif destination == "email":
                    # Email distribution (requires email configuration)
                    self._distribute_via_email(files, rule.get("conditions", {}))
        
        print(f"Distributed {distributed_count} files from category '{category}'")
    
    def _distribute_via_email(self, files: List[Dict], conditions: Dict):
        """Distribute files via email"""
        email_config = self.config["destinations"]["email"]
        if not all([email_config["username"], email_config["password"]]):
            print("Email credentials not configured")
            return
        
        recipients = conditions.get("recipients", [])
        if not recipients:
            print("No email recipients specified")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config["username"]
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = conditions.get("subject", f"Document Distribution - {files[0]['category']}")
            
            body = conditions.get("body", "Documents attached as requested.")
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            for file_info in files:
                cached_path = file_info["cached_path"]
                with open(cached_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {file_info["filename"]}'
                    )
                    msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent to {', '.join(recipients)}")
            
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    def show_config(self):
        """Display current configuration"""
        print(json.dumps(self.config, indent=2))

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Document Distributor")
    parser.add_argument("action", choices=["distribute", "add-destination", "add-rule", "show-config"])
    parser.add_argument("--category", help="Category to distribute")
    parser.add_argument("--name", help="Destination name for add-destination")
    parser.add_argument("--path", help="Destination path for add-destination")
    parser.add_argument("--destinations", nargs="+", help="Destinations for add-rule")
    parser.add_argument("--recipients", nargs="+", help="Email recipients")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Email body")
    
    args = parser.parse_args()
    
    distributor = DocumentDistributor()
    
    if args.action == "distribute":
        if not args.category:
            parser.error("--category required for distribute action")
        distributor.distribute_category(args.category)
    
    elif args.action == "add-destination":
        if not args.name or not args.path:
            parser.error("--name and --path required for add-destination action")
        distributor.add_local_destination(args.name, args.path)
        print(f"Added destination '{args.name}' -> {args.path}")
    
    elif args.action == "add-rule":
        if not args.category or not args.destinations:
            parser.error("--category and --destinations required for add-rule action")
        
        conditions = {}
        if args.recipients:
            conditions["recipients"] = args.recipients
        if args.subject:
            conditions["subject"] = args.subject
        if args.body:
            conditions["body"] = args.body
        
        distributor.add_distribution_rule(args.category, args.destinations, conditions)
        print(f"Added rule for category '{args.category}'")
    
    elif args.action == "show-config":
        distributor.show_config()