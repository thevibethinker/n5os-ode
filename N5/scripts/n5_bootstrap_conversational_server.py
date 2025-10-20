#!/usr/bin/env python3
"""
N5 Bootstrap Conversational Server - AI-to-AI Communication
Extends advisor server with bidirectional conversational API
Enables demonstrator Zo to ask questions and receive AI-generated responses
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import deque
from threading import Lock
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
CONVERSATION_LOG = WORKSPACE / "N5" / "logs" / "bootstrap_conversations.jsonl"
CONVERSATION_LOG.parent.mkdir(parents=True, exist_ok=True)

class ConversationManager:
    """
    Manages AI-to-AI conversation state and message queuing
    Thread-safe for concurrent requests
    """
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
        self.pending_responses: Dict[str, deque] = {}
        self.lock = Lock()
        
    def start_conversation(self, initiator: str, context: Dict) -> str:
        """Start new conversation thread"""
        conv_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        with self.lock:
            self.conversations[conv_id] = [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "init",
                "initiator": initiator,
                "context": context
            }]
            self.pending_responses[conv_id] = deque()
        
        logger.info(f"Started conversation {conv_id} by {initiator}")
        return conv_id
    
    def add_message(self, conv_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Add message to conversation"""
        if conv_id not in self.conversations:
            return False
        
        message = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        with self.lock:
            self.conversations[conv_id].append(message)
            self._log_to_file(conv_id, message)
        
        return True
    
    def get_conversation(self, conv_id: str) -> Optional[List[Dict]]:
        """Retrieve conversation history"""
        with self.lock:
            return self.conversations.get(conv_id, None)
    
    def queue_response(self, conv_id: str, response: str, metadata: Optional[Dict] = None):
        """Queue response for demonstrator to poll"""
        if conv_id not in self.pending_responses:
            return False
        
        response_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response": response,
            "metadata": metadata or {}
        }
        
        with self.lock:
            self.pending_responses[conv_id].append(response_obj)
        
        return True
    
    def get_pending_response(self, conv_id: str) -> Optional[Dict]:
        """Get next pending response for conversation"""
        if conv_id not in self.pending_responses:
            return None
        
        with self.lock:
            if self.pending_responses[conv_id]:
                return self.pending_responses[conv_id].popleft()
        
        return None
    
    def _log_to_file(self, conv_id: str, message: Dict):
        """Append message to persistent log"""
        log_entry = {
            "conversation_id": conv_id,
            **message
        }
        
        with open(CONVERSATION_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


conversation_manager = ConversationManager()


class ConversationalAdvisorHandler(BaseHTTPRequestHandler):
    """
    HTTP handler with conversational AI-to-AI capabilities
    Extends read-only advisor with bidirectional communication
    """
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests (read-only endpoints)"""
        path = self.path
        
        try:
            if path == "/health":
                self.send_health_check()
            
            elif path.startswith("/api/converse/history/"):
                conv_id = path.split("/")[-1]
                self.get_conversation_history(conv_id)
            
            elif path.startswith("/api/converse/poll/"):
                conv_id = path.split("/")[-1]
                self.poll_for_response(conv_id)
            
            # Original advisor endpoints
            elif path == "/bootstrap/principles":
                self.send_architectural_principles()
            
            elif path == "/bootstrap/structure":
                self.send_directory_structure()
            
            elif path == "/bootstrap/checklist":
                self.send_bootstrap_checklist()
            
            else:
                self.send_error_response(404, "Endpoint not found")
        
        except Exception as e:
            logger.error(f"Error handling GET: {e}", exc_info=True)
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        """Handle POST requests (conversational endpoints)"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            
            if self.path == "/api/converse/start":
                self.start_conversation(data)
            
            elif self.path == "/api/converse/ask":
                self.ask_question(data)
            
            elif self.path == "/api/converse/respond":
                self.submit_response(data)
            
            elif self.path == "/bootstrap/query":
                # Original query endpoint
                response = self.handle_query(data)
                self.send_json_response(response)
            
            else:
                self.send_error_response(404, "Endpoint not found")
        
        except json.JSONDecodeError as e:
            self.send_error_response(400, f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error handling POST: {e}", exc_info=True)
            self.send_error_response(500, str(e))
    
    # === AI-to-AI Conversational Endpoints ===
    
    def start_conversation(self, data: Dict):
        """Start new AI-to-AI conversation"""
        initiator = data.get("initiator", "unknown")
        context = data.get("context", {})
        
        conv_id = conversation_manager.start_conversation(initiator, context)
        
        response = {
            "conversation_id": conv_id,
            "status": "started",
            "message": "Conversation initiated. Use /api/converse/ask to send questions.",
            "poll_endpoint": f"/api/converse/poll/{conv_id}"
        }
        
        self.send_json_response(response)
    
    def ask_question(self, data: Dict):
        """
        Demonstrator asks question to parent Zo
        This creates a pending query that parent Zo will see and respond to
        """
        conv_id = data.get("conversation_id")
        question = data.get("question")
        metadata = data.get("metadata", {})
        
        if not conv_id or not question:
            self.send_error_response(400, "Missing conversation_id or question")
            return
        
        # Add question to conversation
        success = conversation_manager.add_message(
            conv_id, 
            "demonstrator", 
            question, 
            metadata
        )
        
        if not success:
            self.send_error_response(404, f"Conversation {conv_id} not found")
            return
        
        # Log for parent to see
        logger.info(f"❓ Question from demonstrator [{conv_id}]: {question}")
        
        # Create response instruction for parent
        response = {
            "status": "received",
            "conversation_id": conv_id,
            "question": question,
            "message": "Question logged. Parent Zo will respond.",
            "instructions": {
                "for_parent": "See conversation log in /api/converse/history",
                "respond_via": f"POST /api/converse/respond with conversation_id and answer"
            }
        }
        
        self.send_json_response(response)
    
    def submit_response(self, data: Dict):
        """
        Parent Zo submits response to demonstrator question
        Response is queued for demonstrator to poll
        """
        conv_id = data.get("conversation_id")
        answer = data.get("answer")
        metadata = data.get("metadata", {})
        
        if not conv_id or not answer:
            self.send_error_response(400, "Missing conversation_id or answer")
            return
        
        # Add response to conversation
        success = conversation_manager.add_message(
            conv_id,
            "parent",
            answer,
            metadata
        )
        
        if not success:
            self.send_error_response(404, f"Conversation {conv_id} not found")
            return
        
        # Queue for demonstrator to poll
        conversation_manager.queue_response(conv_id, answer, metadata)
        
        logger.info(f"💬 Parent response queued [{conv_id}]: {answer[:100]}...")
        
        response = {
            "status": "queued",
            "conversation_id": conv_id,
            "message": "Response queued for demonstrator to poll"
        }
        
        self.send_json_response(response)
    
    def poll_for_response(self, conv_id: str):
        """
        Demonstrator polls for pending responses
        Returns next response or null if none pending
        """
        response = conversation_manager.get_pending_response(conv_id)
        
        if response:
            self.send_json_response({
                "status": "response_available",
                "conversation_id": conv_id,
                **response
            })
        else:
            self.send_json_response({
                "status": "no_response",
                "conversation_id": conv_id,
                "message": "No pending responses"
            })
    
    def get_conversation_history(self, conv_id: str):
        """Get full conversation history"""
        history = conversation_manager.get_conversation(conv_id)
        
        if history is None:
            self.send_error_response(404, f"Conversation {conv_id} not found")
            return
        
        self.send_json_response({
            "conversation_id": conv_id,
            "message_count": len(history),
            "history": history
        })
    
    # === Original Advisor Endpoints (preserved) ===
    
    def handle_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Handle structured queries (original functionality)"""
        query_type = query.get("type")
        context = query.get("context", {})
        
        if query_type == "error":
            return self.diagnose_error(context)
        elif query_type == "next_step":
            return self.suggest_next_step(context)
        elif query_type == "validate":
            return self.validate_setup(context)
        else:
            return {"error": f"Unknown query type: {query_type}"}
    
    def diagnose_error(self, context: Dict) -> Dict:
        """Diagnose bootstrap errors"""
        error = context.get("error", "")
        
        common_errors = {
            "FileNotFoundError": {
                "diagnosis": "Missing required file",
                "solutions": [
                    "Check bootstrap package extraction",
                    "Verify directory structure",
                    "Run: tree -L 2 /home/workspace"
                ]
            },
            "ImportError": {
                "diagnosis": "Missing Python dependencies",
                "solutions": [
                    "Run: pip install -r requirements.txt",
                    "Check Python version: python3 --version"
                ]
            }
        }
        
        for error_type, info in common_errors.items():
            if error_type in error:
                return info
        
        return {"diagnosis": "Unknown error", "solutions": ["Share full error message"]}
    
    def suggest_next_step(self, context: Dict) -> Dict:
        """Suggest next bootstrap step"""
        phase = context.get("phase", 0)
        
        steps = [
            {"phase": 1, "action": "Create directory structure"},
            {"phase": 2, "action": "Copy core scripts"},
            {"phase": 3, "action": "Setup configs and schemas"},
            {"phase": 4, "action": "Copy commands"},
            {"phase": 5, "action": "Setup conditional rules"},
            {"phase": 6, "action": "Test core functionality"}
        ]
        
        if phase < len(steps):
            return steps[phase]
        
        return {"status": "Bootstrap complete"}
    
    def validate_setup(self, context: Dict) -> Dict:
        """Validate setup"""
        return {
            "checks": ["N5 directory", "Scripts present", "Configs present"],
            "instructions": "Run checks and report"
        }
    
    def send_health_check(self):
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "service": "N5 Bootstrap Conversational Server",
            "version": "2.0.0",
            "features": ["read-only guidance", "ai-to-ai conversation"],
            "endpoints": {
                "conversation": [
                    "POST /api/converse/start",
                    "POST /api/converse/ask",
                    "POST /api/converse/respond",
                    "GET /api/converse/history/{conv_id}",
                    "GET /api/converse/poll/{conv_id}"
                ],
                "guidance": [
                    "GET /bootstrap/principles",
                    "GET /bootstrap/structure",
                    "POST /bootstrap/query"
                ]
            }
        }
        self.send_json_response(response)
    
    def send_architectural_principles(self):
        """Send architectural principles"""
        principles_file = WORKSPACE / "Knowledge" / "architectural" / "architectural_principles.md"
        
        if principles_file.exists():
            with open(principles_file) as f:
                content = f.read()
            response = {"principles": content}
        else:
            response = {"error": "Principles file not found"}
        
        self.send_json_response(response)
    
    def send_directory_structure(self):
        """Send directory structure"""
        structure = {
            "workspace_root": "/home/workspace",
            "core_directories": {
                "N5": {
                    "scripts": "Core Python scripts",
                    "config": "System configuration",
                    "schemas": "JSON schemas",
                    "commands": "Slash commands"
                },
                "Knowledge": "Single source of truth",
                "Lists": "Action items",
                "Documents": "System documentation"
            }
        }
        self.send_json_response(structure)
    
    def send_bootstrap_checklist(self):
        """Send bootstrap checklist"""
        checklist = {
            "phase_1": {"tasks": ["Extract package", "Create directories"]},
            "phase_2": {"tasks": ["Copy scripts", "Set permissions"]},
            "phase_3": {"tasks": ["Copy configs", "Setup schemas"]}
        }
        self.send_json_response(checklist)
    
    # === Response Helpers ===
    
    def send_json_response(self, data: Dict):
        """Send JSON response"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        response_bytes = json.dumps(data, indent=2).encode()
        self.wfile.write(response_bytes)
    
    def send_error_response(self, code: int, message: str):
        """Send error response"""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        error = {"error": message, "code": code}
        self.wfile.write(json.dumps(error).encode())
        
        logger.warning(f"Error {code}: {message}")
    
    def log_message(self, format, *args):
        """Override to use logger"""
        logger.info(f"{self.address_string()} - {format % args}")


def main(port: int = 8769):
    """Run conversational bootstrap server"""
    try:
        server = HTTPServer(('0.0.0.0', port), ConversationalAdvisorHandler)
        
        logger.info(f"🤖 N5 Bootstrap Conversational Server running on port {port}")
        logger.info(f"Features: Read-only guidance + AI-to-AI conversation")
        logger.info(f"Health: http://localhost:{port}/health")
        logger.info(f"Conversation log: {CONVERSATION_LOG}")
        logger.info(f"Ready for AI-to-AI communication...")
        
        server.serve_forever()
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8769, help="Server port")
    args = parser.parse_args()
    
    main(port=args.port)
