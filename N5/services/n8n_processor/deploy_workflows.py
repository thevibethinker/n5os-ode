#!/usr/bin/env python3
"""
Deploy n8n workflows for Akiflow integration.
Uses correct n8n API v1 schema.
"""
import json
import requests
import logging
import subprocess
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

N8N_URL = "https://n8n-va.zocomputer.io"

# Load API key from secrets manager (P34)
try:
    API_KEY = subprocess.check_output(
        ["python3", "/home/workspace/N5/scripts/n5_secrets.py", "get", "n8n_api_key"],
        stderr=subprocess.DEVNULL,
        text=True
    ).strip()
    logger.info("✓ Loaded n8n_api_key from secrets manager")
except subprocess.CalledProcessError as e:
    logger.error(f"Failed to load n8n_api_key from secrets manager: {e}")
    raise

def create_workflow(name: str, nodes: List[Dict], connections: Dict) -> Dict:
    """Create a workflow via n8n API."""
    workflow = {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"}
    }
    
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{N8N_URL}/api/v1/workflows", headers=headers, json=workflow)
    response.raise_for_status()
    return response.json()

def webhook_to_akiflow():
    """Workflow: Webhook → Zo API → Gmail (Akiflow)."""
    nodes = [
        {
            "id": "webhook1",
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300],
            "webhookId": "akiflow-tasks",
            "parameters": {
                "path": "akiflow/tasks",
                "httpMethod": "POST",
                "responseMode": "onReceived"
            }
        },
        {
            "id": "zo_api",
            "name": "Zo: Extract Tasks",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [450, 300],
            "parameters": {
                "url": "http://localhost:8770",
                "method": "POST",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ action: 'extract_tasks', data: $json }) }}",
                "options": {}
            }
        },
        {
            "id": "gmail_send",
            "name": "Gmail: Send to Aki",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [650, 300],
            "parameters": {
                "operation": "send",
                "toList": "={{ $json.akiEmail || 'aki+qztlypb6-d@aki.akiflow.com' }}",
                "subject": "={{ $json.subject || '[N8N] Tasks' }}",
                "message": "={{ $json.body }}"
            }
        }
    ]
    
    connections = {
        "Webhook": {"main": [[{"node": "Zo: Extract Tasks", "type": "main", "index": 0}]]},
        "Zo: Extract Tasks": {"main": [[{"node": "Gmail: Send to Aki", "type": "main", "index": 0}]]}
    }
    
    return create_workflow("Akiflow: Webhook → Tasks", nodes, connections)

def main():
    logger.info("Deploying n8n workflows...")
    
    try:
        wf1 = webhook_to_akiflow()
        logger.info(f"✓ Created: {wf1['name']} (ID: {wf1['id']})")
        logger.info(f"  Webhook URL: {N8N_URL}/webhook/akiflow/tasks")
        
        logger.info("\n✓ Deployment complete!")
        logger.info(f"\nNext: Visit {N8N_URL} to:")
        logger.info("1. Configure Gmail credentials")
        logger.info("2. Activate the workflow")
        logger.info("3. Test via webhook POST")
        
        return [wf1]
    
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise

if __name__ == '__main__':
    main()
