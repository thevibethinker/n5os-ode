#!/usr/bin/env python3
"""
N5 Bootstrap Advisor Server
Provides read-only guidance to a bootstrapping N5 instance
Communication is unidirectional: new system queries, this system advises
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")

class BootstrapAdvisorHandler(BaseHTTPRequestHandler):
    """
    Read-only HTTP handler for bootstrap guidance
    SECURITY: Only GET requests, no write operations
    """
    
    def do_GET(self):
        """Handle GET requests only (read-only)"""
        path = self.path
        
        try:
            if path == "/health":
                self.send_health_check()
            
            elif path == "/bootstrap/principles":
                self.send_architectural_principles()
            
            elif path == "/bootstrap/structure":
                self.send_directory_structure()
            
            elif path == "/bootstrap/scripts":
                self.send_script_guidance()
            
            elif path == "/bootstrap/config":
                self.send_config_guidance()
            
            elif path == "/bootstrap/checklist":
                self.send_bootstrap_checklist()
            
            elif path.startswith("/bootstrap/help/"):
                topic = path.split("/")[-1]
                self.send_contextual_help(topic)
            
            else:
                self.send_error_response(404, "Endpoint not found")
        
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        """Handle POST requests for queries"""
        if self.path == "/bootstrap/query":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                query = json.loads(body)
                response = self.handle_query(query)
                self.send_json_response(response)
            except Exception as e:
                logger.error(f"Query error: {e}", exc_info=True)
                self.send_error_response(500, str(e))
        else:
            self.send_error_response(405, "Method not allowed")
    
    def handle_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle structured queries from bootstrap instance
        READ-ONLY: No modifications to this system
        """
        query_type = query.get("type")
        context = query.get("context", {})
        
        if query_type == "error":
            return self.diagnose_error(context)
        
        elif query_type == "next_step":
            return self.suggest_next_step(context)
        
        elif query_type == "validate":
            return self.validate_setup(context)
        
        elif query_type == "troubleshoot":
            return self.troubleshoot_issue(context)
        
        else:
            return {"error": f"Unknown query type: {query_type}"}
    
    def diagnose_error(self, context: Dict) -> Dict:
        """Diagnose common bootstrap errors"""
        error = context.get("error", "")
        phase = context.get("phase", "unknown")
        
        common_errors = {
            "FileNotFoundError": {
                "diagnosis": "Missing required file",
                "solutions": [
                    "Check if bootstrap package was fully extracted",
                    "Verify directory structure matches target",
                    "Run: tree -L 2 /home/workspace to verify"
                ]
            },
            "ImportError": {
                "diagnosis": "Missing Python dependencies",
                "solutions": [
                    "Run: pip install -r requirements.txt",
                    "Check Python version: python3 --version (need 3.12+)",
                    "Install specific: pip install <missing_module>"
                ]
            },
            "PermissionError": {
                "diagnosis": "File permissions issue",
                "solutions": [
                    "Run: chmod +x N5/scripts/*.py",
                    "Check ownership: ls -la /home/workspace",
                    "You should be root in Zo"
                ]
            }
        }
        
        for error_type, info in common_errors.items():
            if error_type in error:
                return {
                    "diagnosis": info["diagnosis"],
                    "solutions": info["solutions"],
                    "phase": phase
                }
        
        return {
            "diagnosis": "Unknown error",
            "solutions": [
                "Share full error message",
                "Check logs for stack trace",
                "Verify all files extracted correctly"
            ]
        }
    
    def suggest_next_step(self, context: Dict) -> Dict:
        """Suggest next bootstrap step based on current state"""
        current_phase = context.get("phase", 0)
        completed = context.get("completed", [])
        
        bootstrap_sequence = [
            {
                "phase": 1,
                "name": "Directory Structure",
                "verify": "ls -la /home/workspace/N5",
                "next": "Create base directories: Knowledge, Lists, N5, Documents"
            },
            {
                "phase": 2,
                "name": "Core Scripts",
                "verify": "ls /home/workspace/N5/scripts | wc -l",
                "next": "Copy scripts from package, chmod +x"
            },
            {
                "phase": 3,
                "name": "Config Files",
                "verify": "ls /home/workspace/N5/config/*.json | wc -l",
                "next": "Copy config files, create credentials/"
            },
            {
                "phase": 4,
                "name": "Schemas",
                "verify": "ls /home/workspace/N5/schemas/*.json | wc -l",
                "next": "Copy schema files"
            },
            {
                "phase": 5,
                "name": "Session State",
                "verify": "python3 /home/workspace/N5/scripts/session_state_manager.py --help",
                "next": "Test session state system"
            },
            {
                "phase": 6,
                "name": "Commands",
                "verify": "ls /home/workspace/Recipes/*/*.md | wc -l",
                "next": "Copy command files"
            },
            {
                "phase": 7,
                "name": "Test Run",
                "verify": "python3 /home/workspace/N5/scripts/n5_safety.py",
                "next": "Run safety checks, verify core functionality"
            }
        ]
        
        if current_phase < len(bootstrap_sequence):
            step = bootstrap_sequence[current_phase]
            return {
                "phase": step["phase"],
                "name": step["name"],
                "verify_command": step["verify"],
                "next_action": step["next"],
                "progress": f"{current_phase}/{len(bootstrap_sequence)}"
            }
        
        return {"status": "Bootstrap complete!", "next": "Test core functionality"}
    
    def validate_setup(self, context: Dict) -> Dict:
        """Validate current setup state"""
        checks = {
            "directories": ["N5", "Knowledge", "Lists", "Documents"],
            "core_scripts": ["session_state_manager.py", "n5_safety.py"],
            "configs": ["commands.jsonl", "emoji-legend.json"]
        }
        
        return {
            "validation_checks": checks,
            "instructions": "Run each check and report results"
        }
    
    def troubleshoot_issue(self, context: Dict) -> Dict:
        """Provide troubleshooting guidance"""
        issue = context.get("issue", "")
        
        troubleshooting_guide = {
            "conditional_rules": {
                "problem": "Conditional rules not working",
                "cause": "User rules in Zo settings not configured",
                "solution": [
                    "Go to https://[yourhandle].zo.computer/settings",
                    "Navigate to 'Rules' section",
                    "Copy conditional rules from Documents/N5.md",
                    "Add each CONDITIONAL RULE",
                    "Test with a simple command"
                ]
            },
            "commands_not_found": {
                "problem": "Slash commands don't appear",
                "cause": "Commands directory or files missing",
                "solution": [
                    "Verify: ls /home/workspace/Commands/*.md",
                    "Should see ~90+ .md files",
                    "Check file format: head Commands/knowledge-add.md",
                    "Restart Zo session if needed"
                ]
            },
            "scripts_failing": {
                "problem": "Scripts throwing errors",
                "cause": "Dependencies or paths incorrect",
                "solution": [
                    "Check Python version: python3 --version",
                    "Install deps: pip install pathlib argparse logging",
                    "Verify paths: pwd should be /home/workspace",
                    "Test individual script: python3 N5/scripts/n5_safety.py"
                ]
            }
        }
        
        if issue in troubleshooting_guide:
            return troubleshooting_guide[issue]
        
        return {
            "available_topics": list(troubleshooting_guide.keys()),
            "message": "Specify issue from list or provide details"
        }
    
    def send_health_check(self):
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "service": "N5 Bootstrap Advisor",
            "version": "1.0.0",
            "mode": "read-only",
            "message": "Mobius maneuver active"
        }
        self.send_json_response(response)
    
    def send_architectural_principles(self):
        """Send architectural principles"""
        principles_file = WORKSPACE / "Knowledge" / "architectural" / "architectural_principles.md"
        
        if principles_file.exists():
            with open(principles_file) as f:
                content = f.read()
            
            response = {
                "principles": content,
                "source": "Knowledge/architectural/architectural_principles.md"
            }
        else:
            response = {
                "error": "Principles file not found",
                "fallback": "Check bootstrap package documentation"
            }
        
        self.send_json_response(response)
    
    def send_directory_structure(self):
        """Send expected directory structure"""
        structure = {
            "workspace_root": "/home/workspace",
            "core_directories": {
                "N5": {
                    "scripts": "Core Python scripts",
                    "config": "System configuration",
                    "schemas": "JSON schemas",
                    "commands": "Slash commands",
                    "prefs": "Preferences and protocols"
                },
                "Knowledge": "Single source of truth",
                "Lists": "Action items and tasks",
                "Documents": "System documentation",
                "Records": "Meeting and temporary files",
                "Exports": "Public deliverables"
            },
            "creation_command": "mkdir -p N5/{scripts,config,schemas,commands,prefs} Knowledge Lists Documents Records Exports"
        }
        self.send_json_response(structure)
    
    def send_script_guidance(self):
        """Send script setup guidance"""
        guidance = {
            "script_count": "~72 core scripts",
            "location": "/home/workspace/N5/scripts/",
            "permissions": "chmod +x N5/scripts/*.py",
            "test_script": "python3 N5/scripts/n5_safety.py",
            "common_scripts": [
                "session_state_manager.py",
                "n5_safety.py",
                "n5_commands_manage.py",
                "n5_knowledge_add.py",
                "n5_lists_add.py"
            ]
        }
        self.send_json_response(guidance)
    
    def send_config_guidance(self):
        """Send config setup guidance"""
        guidance = {
            "config_location": "/home/workspace/N5/config/",
            "required_files": [
                "commands.jsonl",
                "emoji-legend.json",
                "front_matter_schema.yaml"
            ],
            "optional_files": [
                "enrichment_settings.json",
                "tag_mapping.json",
                "relationship_thresholds.json"
            ],
            "create_dirs": [
                "N5/config/credentials"
            ],
            "note": "Most config files are already in bootstrap package"
        }
        self.send_json_response(guidance)
    
    def send_bootstrap_checklist(self):
        """Send complete bootstrap checklist"""
        checklist = {
            "phase_1_structure": {
                "tasks": [
                    "Extract bootstrap package",
                    "Create directory structure",
                    "Verify extraction: tree -L 2"
                ],
                "verify": "ls -la /home/workspace/N5"
            },
            "phase_2_scripts": {
                "tasks": [
                    "Copy scripts to N5/scripts/",
                    "chmod +x N5/scripts/*.py",
                    "Test one: python3 N5/scripts/n5_safety.py"
                ],
                "verify": "ls N5/scripts/*.py | wc -l"
            },
            "phase_3_config": {
                "tasks": [
                    "Copy configs to N5/config/",
                    "Create credentials directory",
                    "Copy schemas to N5/schemas/"
                ],
                "verify": "ls N5/config/*.json N5/schemas/*.json"
            },
            "phase_4_commands": {
                "tasks": [
                    "Copy commands to Commands/ (not N5/commands!)",
                    "Verify markdown format",
                    "Test slash command appears"
                ],
                "verify": "ls Commands/*.md | wc -l"
            },
            "phase_5_docs": {
                "tasks": [
                    "Copy Documents/N5.md",
                    "Copy Knowledge/architectural/",
                    "Copy N5/prefs/"
                ],
                "verify": "cat Documents/N5.md"
            },
            "phase_6_rules": {
                "tasks": [
                    "Go to Zo settings",
                    "Add conditional rules from N5.md",
                    "Add always-applied rules",
                    "Test rules active"
                ],
                "verify": "Ask Zo to load Documents/N5.md"
            },
            "phase_7_test": {
                "tasks": [
                    "Run: /init-state-session",
                    "Run: /knowledge-add with test data",
                    "Verify SESSION_STATE.md created",
                    "Test core functionality"
                ],
                "verify": "ls -la .z/workspaces/*/SESSION_STATE.md"
            }
        }
        self.send_json_response(checklist)
    
    def send_contextual_help(self, topic: str):
        """Send help for specific topic"""
        help_topics = {
            "session_state": {
                "purpose": "Track conversation context and state",
                "location": "Each conversation workspace",
                "init": "python3 N5/scripts/session_state_manager.py init --convo-id <id> --type build",
                "common_issues": [
                    "File not found: Need to init first",
                    "Wrong location: Must be in conversation workspace",
                    "Type missing: Specify --type (build/research/discussion/planning)"
                ]
            },
            "commands": {
                "purpose": "Slash commands for quick actions",
                "location": "/home/workspace/Commands/ (NOT N5/commands!)",
                "format": "Markdown with YAML frontmatter",
                "test": "Type / in Zo chat to see list",
                "debug": "Check file exists, has .md extension, valid YAML"
            },
            "conditional_rules": {
                "purpose": "Context-aware AI behavior",
                "location": "Zo settings > Rules",
                "setup": "Copy from Documents/N5.md to settings",
                "test": "Reference a file, check if AI mentions it correctly"
            }
        }
        
        if topic in help_topics:
            self.send_json_response(help_topics[topic])
        else:
            self.send_json_response({
                "error": f"Topic '{topic}' not found",
                "available": list(help_topics.keys())
            })
    
    def send_json_response(self, data: Dict):
        """Send JSON response"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow any Zo workspace
        self.end_headers()
        
        response_bytes = json.dumps(data, indent=2).encode()
        self.wfile.write(response_bytes)
        
        logger.info(f"Sent response for {self.path}")
    
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


def main(port: int = 8765):
    """Run bootstrap advisor server"""
    try:
        server = HTTPServer(('0.0.0.0', port), BootstrapAdvisorHandler)
        logger.info(f"🚀 N5 Bootstrap Advisor Server running on port {port}")
        logger.info(f"Mode: READ-ONLY (no modifications possible)")
        logger.info(f"Health check: http://localhost:{port}/health")
        logger.info(f"Waiting for bootstrap queries...")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.shutdown()
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="N5 Bootstrap Advisor Server")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    args = parser.parse_args()
    
    sys.exit(main(port=args.port))
