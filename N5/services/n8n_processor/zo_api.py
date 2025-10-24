#!/usr/bin/env python3
"""
Zo API endpoint for n8n workflows.
Acts as LLM processor for n8n automation workflows.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")

class ZoN8NHandler(BaseHTTPRequestHandler):
    """Handle n8n → Zo API requests."""
    
    def do_POST(self):
        """Process POST requests from n8n."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))
            
            action = request.get('action')
            data = request.get('data', {})
            
            logger.info(f"Processing action: {action}")
            
            # Route to appropriate handler
            if action == 'extract_tasks':
                result = self.extract_tasks(data)
            elif action == 'suggest_schedule':
                result = self.suggest_schedule(data)
            elif action == 'draft_warm_intro':
                result = self.draft_warm_intro(data)
            elif action == 'daily_briefing':
                result = self.daily_briefing(data)
            else:
                result = {'error': f'Unknown action: {action}'}
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def extract_tasks(self, data: Dict) -> Dict:
        """
        Extract actionable tasks from meeting notes/emails.
        
        Input: {text: "meeting notes...", context: {...}}
        Output: {tasks: [{title, when, duration, priority, project, tags, notes}]}
        """
        text = data.get('text', '')
        context = data.get('context', {})
        tasks = []
        
        # Warm intro pattern
        if context.get('type') == 'warm_intro' or 'connect' in text.lower():
            person_a = context.get('person_a', '')
            person_b = context.get('person_b', '')
            reason = context.get('reason', '')
            deadline = context.get('deadline', 'Tomorrow 10:00am ET')
            
            # Extract names from text if not in context
            if not person_a or not person_b:
                import re
                connect_match = re.search(r'connect\s+([^(]+(?:\([^)]+\))?)\s+with\s+([^.]+)', text, re.IGNORECASE)
                if connect_match:
                    person_a = connect_match.group(1).strip()
                    person_b = connect_match.group(2).strip()
            
            if person_a and person_b:
                # Task 1: Draft
                tasks.append({
                    "title": f"Draft intro: {person_a} → {person_b}",
                    "when": deadline,
                    "duration": "15m",
                    "priority": "High",
                    "project": "Networking",
                    "tags": ["warm_intro", "draft"],
                    "notes": f"Connect {person_a} with {person_b}. {reason}"
                })
                
                # Task 2: Send  
                from datetime import datetime, timedelta
                try:
                    dt = datetime.now() + timedelta(hours=1)
                    send_time = dt.strftime('%Y-%m-%d %I:%M%p ET')
                except:
                    send_time = "Tomorrow 11:00am ET"
                    
                tasks.append({
                    "title": f"Send intro: {person_a} → {person_b}",
                    "when": send_time,
                    "duration": "5m",
                    "priority": "High",
                    "project": "Networking",
                    "tags": ["warm_intro", "send"],
                    "notes": f"Review draft, finalize, and send double opt-in intro."
                })
                
                # Task 3: Follow-up
                try:
                    dt = datetime.now() + timedelta(days=7)
                    followup_time = dt.strftime('%Y-%m-%d %I:%M%p ET')
                except:
                    followup_time = "Next week 2:00pm ET"
                    
                tasks.append({
                    "title": f"Follow-up: {person_a} ↔ {person_b}",
                    "when": followup_time,
                    "duration": "10m",
                    "priority": "Normal",
                    "project": "Networking",
                    "tags": ["warm_intro", "follow_up"],
                    "notes": f"Check if they connected. If no response, gentle nudge."
                })
        
        # Generic action item pattern
        else:
            lines = text.split('\n')
            for line in lines:
                line_lower = line.lower().strip()
                # Look for action keywords
                if any(kw in line_lower for kw in ['draft', 'review', 'send', 'schedule', 'prepare', 'action:', '- ']):
                    if line.strip() and len(line.strip()) > 5:
                        tasks.append({
                            "title": line.strip().lstrip('-•*').strip(),
                            "when": "Tomorrow 10:00am ET",
                            "duration": "30m",
                            "priority": "Normal",
                            "project": "Operations",
                            "tags": ["action_item"],
                            "notes": f"From: {text[:100]}..."
                        })
        
        return {
            "tasks": tasks,
            "count": len(tasks),
            "processed_at": datetime.now().isoformat()
        }
    
    def suggest_schedule(self, data: Dict) -> Dict:
        """
        Suggest optimal times for tasks based on calendar.
        
        Input: {tasks: [...], calendar: [...]}
        Output: {scheduled_tasks: [...]}
        """
        tasks = data.get('tasks', [])
        calendar = data.get('calendar', [])
        
        # TODO: Implement calendar-aware scheduling logic
        # For now, space tasks 30min apart starting from 9am
        
        scheduled = []
        base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for i, task in enumerate(tasks):
            scheduled_time = base_time + timedelta(minutes=30 * i)
            task['when'] = scheduled_time.strftime('%Y-%m-%d %I:%M%p ET')
            scheduled.append(task)
        
        return {
            'scheduled_tasks': scheduled,
            'count': len(scheduled)
        }
    
    def draft_warm_intro(self, data: Dict) -> Dict:
        """
        Draft warm introduction email.
        
        Input: {person_a: {...}, person_b: {...}, context: "..."}
        Output: {subject: "...", body: "...", tasks: [...]}
        """
        person_a = data.get('person_a', {})
        person_b = data.get('person_b', {})
        context = data.get('context', '')
        
        # TODO: Implement actual drafting with context from Knowledge base
        
        subject = f"Intro: {person_a.get('name', 'Person A')} ↔ {person_b.get('name', 'Person B')}"
        body = f"""Hi {person_a.get('name', 'there')},

I'd like to introduce you to {person_b.get('name', 'someone')}. {context}

I think you two should connect!

Best,
V"""
        
        # Create 3-task pack: draft, send, follow-up
        tasks = [
            {
                'title': f"Draft intro: {person_a.get('name', 'A')} → {person_b.get('name', 'B')}",
                'when': 'Today 3:00pm ET',
                'duration': '15m',
                'priority': 'High',
                'project': 'Networking',
                'tags': ['warm_intro', 'draft'],
                'notes': f'Context: {context}'
            },
            {
                'title': f"Send intro: {person_a.get('name', 'A')} → {person_b.get('name', 'B')}",
                'when': 'Today 4:00pm ET',
                'duration': '5m',
                'priority': 'High',
                'project': 'Networking',
                'tags': ['warm_intro', 'send'],
                'notes': 'Review draft, finalize, and send'
            },
            {
                'title': f"Follow-up: {person_a.get('name', 'A')} ↔ {person_b.get('name', 'B')}",
                'when': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d 2:00pm ET'),
                'duration': '10m',
                'priority': 'Normal',
                'project': 'Networking',
                'tags': ['warm_intro', 'follow_up'],
                'notes': 'Check if they connected'
            }
        ]
        
        return {
            'subject': subject,
            'body': body,
            'tasks': tasks
        }
    
    def daily_briefing(self, data: Dict) -> Dict:
        """
        Generate daily briefing with calendar summary and priorities.
        
        Input: {date: "2025-10-23"}
        Output: {briefing: "...", priority_tasks: [...]}
        """
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # TODO: Implement actual briefing generation with calendar + task queries
        
        briefing = f"""Good morning! Here's your day ahead for {date}:

📅 Calendar:
- 9:30am: Leadership Team Sync (20m)
- 10:00am: Warm intro followup (15m)
- 11:00am: Review candidate pipeline (30m)

🎯 Priority Tasks:
- Draft recap for Leadership meeting
- Send warm intro
- Review top 5 candidates

⚡ Focus Time: 2:00pm-4:00pm (blocked for deep work)
"""
        
        return {
            'briefing': briefing,
            'date': date,
            'event_count': 3,
            'task_count': 3
        }
    
    def do_GET(self):
        """Health check endpoint."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'status': 'healthy',
                'service': 'zo-n8n-api',
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port: int = 8770):
    """Start the Zo API server for n8n."""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, ZoN8NHandler)
    logger.info(f'✓ Zo n8n API server running on port {port}')
    logger.info(f'Endpoint: http://localhost:{port}')
    httpd.serve_forever()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Zo API for n8n')
    parser.add_argument('--port', type=int, default=8770, help='Port to listen on')
    args = parser.parse_args()
    run_server(args.port)
