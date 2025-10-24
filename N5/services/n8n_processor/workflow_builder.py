#!/usr/bin/env python3
"""
Programmatically create n8n workflows via API.
Builds automation workflows that use Zo as the LLM processor.
"""
import json
import requests
import logging
from typing import Dict, List, Any
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

class N8NWorkflowBuilder:
    """Build and deploy n8n workflows programmatically."""
    
    def __init__(self, api_key: str, base_url: str = "https://n8n-va.zocomputer.io/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-N8N-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        self.zo_api_url = "http://localhost:8770"
    
    def create_workflow(self, workflow: Dict) -> Dict:
        """Create a new workflow."""
        url = f"{self.base_url}/workflows"
        response = requests.post(url, headers=self.headers, json=workflow)
        response.raise_for_status()
        result = response.json()
        logger.info(f"✓ Created workflow: {result.get('name')} (ID: {result.get('id')})")
        return result
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Activate a workflow."""
        url = f"{self.base_url}/workflows/{workflow_id}/activate"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        logger.info(f"✓ Activated workflow: {workflow_id}")
        return response.json()
    
    def build_meeting_to_tasks_workflow(self) -> Dict:
        """
        Workflow: Email with meeting notes → Zo extracts tasks → Akiflow
        
        Trigger: Manual/Webhook
        1. Receive meeting notes text
        2. POST to Zo API: extract_tasks
        3. Zo returns structured tasks
        4. Format for Aki email
        5. Send via Gmail
        """
        return {
            "name": "Meeting → Tasks → Akiflow",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "meeting-notes",
                        "responseMode": "responseNode",
                        "options": {}
                    },
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                    "webhookId": "meeting-notes-webhook"
                },
                {
                    "parameters": {
                        "url": f"{self.zo_api_url}",
                        "method": "POST",
                        "jsonParameters": True,
                        "options": {},
                        "bodyParametersJson": "={{ {\"action\": \"extract_tasks\", \"data\": {\"text\": $json.body.text, \"context\": $json.body.context}} }}"
                    },
                    "name": "Zo: Extract Tasks",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "jsCode": "// Format tasks for Aki email\nconst tasks = $input.item.json.tasks;\nconst formatted = tasks.map(t => `Task: ${t.title}\\nWhen: ${t.when}\\nDuration: ${t.duration}\\nPriority: ${t.priority}\\nProject: ${t.project}\\nTags: ${t.tags.join(', ')}\\nNotes: ${t.notes}`).join('\\n\\n---\\n\\n');\n\nreturn { emailBody: formatted, taskCount: tasks.length };"
                    },
                    "name": "Format for Aki",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [650, 300]
                },
                {
                    "parameters": {
                        "url": "https://n8n-va.zocomputer.io/webhook/meeting-response",
                        "options": {},
                        "responseCode": 200,
                        "responseData": "={{ {\"status\": \"success\", \"tasks_created\": $json.taskCount} }}"
                    },
                    "name": "Respond to Webhook",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [850, 300]
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [[{"node": "Zo: Extract Tasks", "type": "main", "index": 0}]]
                },
                "Zo: Extract Tasks": {
                    "main": [[{"node": "Format for Aki", "type": "main", "index": 0}]]
                },
                "Format for Aki": {
                    "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
                }
            },
            "active": False,
            "settings": {
                "executionOrder": "v1"
            }
        }
    
    def build_calendar_reader_workflow(self) -> Dict:
        """
        Workflow: Read today's Akiflow tasks via IFTTT
        
        Trigger: Schedule (daily 7am)
        1. Trigger: Schedule
        2. HTTP Request to IFTTT Akiflow query
        3. Parse response
        4. Send to Zo for briefing
        5. Email/SMS to V
        """
        return {
            "name": "Daily Calendar Reader",
            "nodes": [
                {
                    "parameters": {
                        "rule": {
                            "interval": [{"field": "cronExpression", "expression": "0 7 * * *"}]
                        }
                    },
                    "name": "Schedule: 7am Daily",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "jsCode": "// Get today's date\nconst today = new Date().toISOString().split('T')[0];\nreturn { date: today };"
                    },
                    "name": "Get Today's Date",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "url": f"{self.zo_api_url}",
                        "method": "POST",
                        "jsonParameters": True,
                        "bodyParametersJson": "={{ {\"action\": \"daily_briefing\", \"data\": {\"date\": $json.date}} }}"
                    },
                    "name": "Zo: Generate Briefing",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [650, 300]
                }
            ],
            "connections": {
                "Schedule: 7am Daily": {
                    "main": [[{"node": "Get Today's Date", "type": "main", "index": 0}]]
                },
                "Get Today's Date": {
                    "main": [[{"node": "Zo: Generate Briefing", "type": "main", "index": 0}]]
                }
            },
            "active": False,
            "settings": {
                "executionOrder": "v1"
            }
        }
    
    def build_warm_intro_workflow(self) -> Dict:
        """
        Workflow: Warm intro trigger → Draft + 3 tasks → Akiflow
        
        Trigger: Webhook
        1. Receive: person_a, person_b, context
        2. Zo drafts intro email
        3. Zo creates 3-task pack (draft, send, follow-up)
        4. Push to Akiflow via Aki email
        """
        return {
            "name": "Warm Intro Automation",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "warm-intro",
                        "responseMode": "responseNode"
                    },
                    "name": "Webhook: Warm Intro",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                    "webhookId": "warm-intro-webhook"
                },
                {
                    "parameters": {
                        "url": f"{self.zo_api_url}",
                        "method": "POST",
                        "jsonParameters": True,
                        "bodyParametersJson": "={{ {\"action\": \"draft_warm_intro\", \"data\": $json.body} }}"
                    },
                    "name": "Zo: Draft Intro",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "url": "https://n8n-va.zocomputer.io/webhook/intro-response",
                        "responseData": "={{ {\"status\": \"success\", \"tasks\": $json.tasks.length, \"subject\": $json.subject} }}"
                    },
                    "name": "Respond",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [650, 300]
                }
            ],
            "connections": {
                "Webhook: Warm Intro": {
                    "main": [[{"node": "Zo: Draft Intro", "type": "main", "index": 0}]]
                },
                "Zo: Draft Intro": {
                    "main": [[{"node": "Respond", "type": "main", "index": 0}]]
                }
            },
            "active": False
        }
    
    def deploy_all_workflows(self):
        """Create and activate all workflows."""
        workflows = [
            self.build_meeting_to_tasks_workflow(),
            self.build_calendar_reader_workflow(),
            self.build_warm_intro_workflow()
        ]
        
        created = []
        for workflow in workflows:
            try:
                result = self.create_workflow(workflow)
                created.append(result)
                logger.info(f"Created: {workflow['name']}")
            except Exception as e:
                logger.error(f"Failed to create {workflow['name']}: {e}")
        
        return created

def main(api_key: str):
    """Build and deploy workflows."""
    builder = N8NWorkflowBuilder(api_key)
    
    logger.info("Building workflows...")
    workflows = builder.deploy_all_workflows()
    
    logger.info(f"\n✓ Created {len(workflows)} workflows")
    for wf in workflows:
        logger.info(f"  - {wf['name']} (ID: {wf['id']})")
    
    logger.info("\nTo activate: Visit https://n8n-va.zocomputer.io and activate each workflow")
    
    return workflows

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Build n8n workflows')
    parser.add_argument('--api-key', required=True, help='n8n API key')
    args = parser.parse_args()
    main(args.api_key)
