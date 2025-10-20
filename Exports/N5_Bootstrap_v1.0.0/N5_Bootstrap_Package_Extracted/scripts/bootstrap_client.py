#!/usr/bin/env python3
"""
N5 Bootstrap Client
Connects to parent N5 instance for guidance during bootstrap
READ-ONLY communication: queries parent, receives advice
"""

import json
import logging
import sys
from typing import Dict, Any
import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Parent advisor URL (set this to your parent's service URL)
ADVISOR_URL = "https://n5-bootstrap-advisor-va.zocomputer.io"


class BootstrapClient:
    """Client for querying parent N5 instance"""
    
    def __init__(self, advisor_url: str = ADVISOR_URL):
        self.advisor_url = advisor_url.rstrip('/')
        logger.info(f"Bootstrap client initialized: {self.advisor_url}")
    
    def health_check(self) -> Dict:
        """Check if advisor is available"""
        try:
            response = self._get("/health")
            logger.info(f"✓ Advisor healthy: {response.get('status')}")
            return response
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": str(e)}
    
    def get_principles(self) -> Dict:
        """Get architectural principles from parent"""
        return self._get("/bootstrap/principles")
    
    def get_structure(self) -> Dict:
        """Get expected directory structure"""
        return self._get("/bootstrap/structure")
    
    def get_script_guidance(self) -> Dict:
        """Get guidance for setting up scripts"""
        return self._get("/bootstrap/scripts")
    
    def get_config_guidance(self) -> Dict:
        """Get guidance for configuration"""
        return self._get("/bootstrap/config")
    
    def get_checklist(self) -> Dict:
        """Get complete bootstrap checklist"""
        return self._get("/bootstrap/checklist")
    
    def get_help(self, topic: str) -> Dict:
        """Get contextual help on specific topic"""
        return self._get(f"/bootstrap/help/{topic}")
    
    def query(self, query_type: str, context: Dict = None) -> Dict:
        """
        Send structured query to advisor
        
        Query types:
        - error: Diagnose an error
        - next_step: Get next bootstrap step
        - validate: Validate current setup
        - troubleshoot: Get troubleshooting guidance
        """
        payload = {
            "type": query_type,
            "context": context or {}
        }
        return self._post("/bootstrap/query", payload)
    
    def diagnose_error(self, error_msg: str, phase: str = "unknown") -> Dict:
        """Diagnose a specific error"""
        return self.query("error", {"error": error_msg, "phase": phase})
    
    def get_next_step(self, current_phase: int, completed: list = None) -> Dict:
        """Get next step based on current progress"""
        return self.query("next_step", {
            "phase": current_phase,
            "completed": completed or []
        })
    
    def validate_setup(self) -> Dict:
        """Get validation checks for current setup"""
        return self.query("validate", {})
    
    def troubleshoot(self, issue: str) -> Dict:
        """Get troubleshooting guidance for an issue"""
        return self.query("troubleshoot", {"issue": issue})
    
    def _get(self, endpoint: str) -> Dict:
        """Make GET request to advisor"""
        url = f"{self.advisor_url}{endpoint}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read()
                return json.loads(data)
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP {e.code}: {e.reason}")
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}
    
    def _post(self, endpoint: str, payload: Dict) -> Dict:
        """Make POST request to advisor"""
        url = f"{self.advisor_url}{endpoint}"
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read()
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP {e.code}: {e.reason}")
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}


def interactive_mode(client: BootstrapClient):
    """Interactive mode for bootstrap assistance"""
    print("\n🚀 N5 Bootstrap Interactive Assistant")
    print("=" * 60)
    print("\nCommands:")
    print("  health       - Check advisor connection")
    print("  checklist    - Get bootstrap checklist")
    print("  next         - Get next step")
    print("  error <msg>  - Diagnose an error")
    print("  help <topic> - Get help on topic")
    print("  structure    - Show directory structure")
    print("  scripts      - Get script guidance")
    print("  config       - Get config guidance")
    print("  troubleshoot <issue> - Troubleshoot issue")
    print("  quit         - Exit")
    print("\nAvailable help topics: session_state, commands, conditional_rules")
    print("=" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip()
            
            if not cmd:
                continue
            
            if cmd == "quit":
                break
            
            parts = cmd.split(maxsplit=1)
            action = parts[0]
            arg = parts[1] if len(parts) > 1 else None
            
            if action == "health":
                result = client.health_check()
            elif action == "checklist":
                result = client.get_checklist()
            elif action == "next":
                phase = int(input("Current phase (0-7): "))
                result = client.get_next_step(phase)
            elif action == "error" and arg:
                result = client.diagnose_error(arg)
            elif action == "help" and arg:
                result = client.get_help(arg)
            elif action == "structure":
                result = client.get_structure()
            elif action == "scripts":
                result = client.get_script_guidance()
            elif action == "config":
                result = client.get_config_guidance()
            elif action == "troubleshoot" and arg:
                result = client.troubleshoot(arg)
            else:
                print(f"Unknown command: {cmd}")
                continue
            
            print("\nResponse:")
            print(json.dumps(result, indent=2))
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="N5 Bootstrap Client")
    parser.add_argument("--advisor-url", default=ADVISOR_URL,
                      help="URL of parent advisor service")
    parser.add_argument("--interactive", "-i", action="store_true",
                      help="Run in interactive mode")
    parser.add_argument("--health", action="store_true",
                      help="Check advisor health")
    parser.add_argument("--checklist", action="store_true",
                      help="Get bootstrap checklist")
    parser.add_argument("--next-step", type=int, metavar="PHASE",
                      help="Get next step for phase")
    parser.add_argument("--error", metavar="MSG",
                      help="Diagnose error message")
    parser.add_argument("--help-topic", metavar="TOPIC",
                      help="Get help on topic")
    
    args = parser.parse_args()
    
    client = BootstrapClient(args.advisor_url)
    
    if args.interactive:
        interactive_mode(client)
    elif args.health:
        result = client.health_check()
        print(json.dumps(result, indent=2))
    elif args.checklist:
        result = client.get_checklist()
        print(json.dumps(result, indent=2))
    elif args.next_step is not None:
        result = client.get_next_step(args.next_step)
        print(json.dumps(result, indent=2))
    elif args.error:
        result = client.diagnose_error(args.error)
        print(json.dumps(result, indent=2))
    elif args.help_topic:
        result = client.get_help(args.help_topic)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        print("\nQuick start:")
        print("  python3 bootstrap_client.py --health")
        print("  python3 bootstrap_client.py --interactive")


if __name__ == "__main__":
    main()
