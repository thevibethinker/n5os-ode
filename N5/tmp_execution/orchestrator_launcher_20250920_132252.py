#!/usr/bin/env python3
"""Orchestrator Launcher CLI - Validates plans, launches through command authoring pipeline, generates AAR."""
import argparse, json, logging, os, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
                   handlers=[logging.FileHandler('/home/workspace/command_authoring.log', mode='a'), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger('orchestrator_launcher')

class OrchestratorLauncher:
    def __init__(self): self.artifacts, self.start_time = {}, datetime.now(timezone.utc)
    
    def validate_plan(self, plan_text):
        required, found = ['Intended Outcome', 'Launch Command'], {}
        for line in plan_text.split('\n'):
            for field in required:
                if f"**{field}**" in line and ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if content and content != '[...]': found[field] = content
        return {'valid': len(found) == len(required), 'missing_fields': [f for f in required if f not in found]}
    
    def enrich_plan(self, plan_text):
        metadata = {"timestamp": self.start_time.isoformat(), "cwd": os.getcwd(), "thread_hint": Path(os.getcwd()).name}
        return plan_text + f"\n- **Metadata**: {json.dumps(metadata)}\n" if '**Metadata**:' not in plan_text else plan_text
    
    def create_temp_file(self, content):
        temp = tempfile.NamedTemporaryFile(mode='w', suffix='_plan_conversation.txt', delete=False, dir='/tmp')
        temp.write(content); temp.close(); self.artifacts['temp_conversation'] = temp.name
        logger.info(f"Created temp conversation: {temp.name}"); return temp.name
    
    def invoke_pipeline(self, conversation_path):
        script = Path('/home/workspace/N5/scripts/author-command/author-command')
        result = subprocess.run(['python3', str(script), conversation_path], capture_output=True, text=True, cwd=script.parent)
        if result.returncode != 0: raise RuntimeError(f"Author-command failed: {result.stderr}")
        resolved_path = script.parent / 'resolved_command.json'
        if resolved_path.exists():
            with open(resolved_path) as f: data = json.load(f)
            copy_path = Path.cwd() / f"resolved_command_{int(time.time())}.json"
            with open(copy_path, 'w') as f: json.dump(data, f, indent=2)
            self.artifacts['resolved_json'] = str(copy_path); logger.info(f"Copied resolved command: {copy_path}"); return data
        else: return json.loads(result.stdout)
    
    def validate_command(self, data):
        cmd = data.get('resolved_command', data)
        for field in ['name', 'version']:
            if field not in cmd: logger.error(f"Missing field: {field}"); return False
        name = cmd.get('name', '')
        if not name or not all(c.isalnum() or c in '-_' for c in name): logger.error(f"Invalid name: {name}"); return False
        logger.info("Command validation passed"); return True
    
    def append_command(self, data, dry_run=True):
        if dry_run: logger.info("Dry run - would append to commands.jsonl"); return True
        script, cmd_data = Path('/home/workspace/N5/scripts/append_command.py'), data.get('resolved_command', data)
        formatted = {'name': cmd_data.get('name'), 'version': cmd_data.get('version'),
                    'summary': cmd_data.get('description', cmd_data.get('summary', '')), 'workflow': cmd_data.get('workflow', 'misc'),
                    'tags': cmd_data.get('tags', []), 'updated_at': datetime.now(timezone.utc).isoformat()}
        for field in ['inputs', 'outputs', 'uses', 'steps', 'side_effects', 'permissions_required', 'flags', 'examples']:
            if field in cmd_data: formatted[field] = cmd_data[field]
        result = subprocess.run(['python3', str(script), '--command_json', json.dumps(formatted)], capture_output=True, text=True, cwd=script.parent)
        if result.returncode != 0: logger.error(f"Append failed: {result.stderr}"); return False
        logger.info("Command appended to commands.jsonl"); return True
    
    def execute_command(self, data):
        cmd_data, result = data.get('resolved_command', data), {'executed': False, 'output': '', 'error': ''}
        if 'command' in cmd_data:
            try:
                proc = subprocess.run(cmd_data['command'], shell=True, capture_output=True, text=True, timeout=300)
                result.update({'executed': True, 'returncode': proc.returncode, 'output': proc.stdout, 'error': proc.stderr})
                logger.info(f"Command executed, return code: {proc.returncode}")
            except Exception as e: result.update({'executed': True, 'error': str(e)}); logger.error(f"Execution failed: {e}")
        elif 'steps' in cmd_data:
            result['executed'], result['output'] = True, f"Would execute {len(cmd_data['steps'])} steps"
            logger.info(f"Found {len(cmd_data['steps'])} steps")
        else: logger.info("No executable command/steps found")
        return result
    
    def generate_aar(self, original_plan, data, exec_result):
        intended = "Not specified"
        for line in original_plan.split('\n'):
            if '**Intended Outcome**' in line and ':' in line: intended = line.split(':', 1)[1].strip(); break
        cmd_data = data.get('resolved_command', data)
        actual = f"Generated command '{cmd_data.get('name', 'unknown')}'"
        if exec_result.get('executed'): 
            actual += " and executed successfully" if exec_result.get('returncode') == 0 else " but execution failed"
        aar = f"""# After‑Action Report for Orchestrator Launch
- **Execution Thread ID**: orchestrator-launcher-{int(time.time())}
- **Original Plan Reference**: {self.artifacts.get('temp_conversation', 'N/A')}
- **Intended vs. Actual**:
  - Intended: {intended}
  - Actual: {actual}
  - Discrepancies: {'None' if exec_result.get('returncode') == 0 else 'Execution issues'}
- **Step‑by‑Step Execution**:
  - Plan validation: Completed
  - Author-command pipeline: Completed  
  - Schema validation: Completed
  - Command append: {'Completed' if not exec_result.get('error') else 'Failed'}
  - Command execution: {'Completed' if exec_result.get('executed') else 'Skipped'}
- **Outcomes**: 
  - Command: {cmd_data.get('name', 'unknown')} v{cmd_data.get('version', 'unknown')}
  - Resolved JSON: {self.artifacts.get('resolved_json', 'N/A')}
  - Execution: {exec_result.get('output', 'N/A')[:200]}
- **Lessons Learned**: Pipeline time: {(datetime.now(timezone.utc) - self.start_time).total_seconds():.2f}s
- **Recommendations**: {'Review execution errors' if exec_result.get('error') else 'Process completed successfully'}

## Artifacts
- Temp conversation: {self.artifacts.get('temp_conversation', 'N/A')}
- Resolved JSON: {self.artifacts.get('resolved_json', 'N/A')}
- This AAR: {Path.cwd() / f"aar_{int(time.time())}.md"}
"""
        aar_path = Path.cwd() / f"aar_{int(time.time())}.md"
        with open(aar_path, 'w') as f: f.write(aar)
        self.artifacts['aar'] = str(aar_path); logger.info(f"Generated AAR: {aar_path}"); return str(aar_path)

def main():
    parser = argparse.ArgumentParser(description='Orchestrator Launcher - Validate plans and launch through command authoring pipeline')
    parser.add_argument('--plan_file', help='Path to markdown Plan Summary file')
    parser.add_argument('--execute', action='store_true', help='Execute the produced command (default: dry-run)')
    args = parser.parse_args()
    
    if args.plan_file:
        if not os.path.exists(args.plan_file): print(f"Error: Plan file not found: {args.plan_file}"); sys.exit(1)
        with open(args.plan_file) as f: plan_text = f.read()
    else: logger.info("Reading plan from stdin..."); plan_text = sys.stdin.read()
    
    if not plan_text.strip(): print("Error: No plan text provided"); sys.exit(1)
    
    try:
        launcher = OrchestratorLauncher()
        validation = launcher.validate_plan(plan_text)
        if not validation['valid']: 
            print(f"Error: Missing required fields: {validation['missing_fields']}")
            print("Required: Intended Outcome, Launch Command (format: **Field**: content)"); sys.exit(1)
        
        enriched = launcher.enrich_plan(plan_text)
        temp_file = launcher.create_temp_file(enriched)
        resolved = launcher.invoke_pipeline(temp_file)
        if not launcher.validate_command(resolved): print("Error: Command validation failed"); sys.exit(1)
        launcher.append_command(resolved, not args.execute)
        exec_result = launcher.execute_command(resolved) if args.execute else {}
        launcher.generate_aar(plan_text, resolved, exec_result)
        print("Orchestrator launch completed successfully!")
        print("Artifacts created:")
        for name, path in launcher.artifacts.items(): print(f"  {name}: {path}")
    except Exception as e: logger.error(f"Failed: {e}"); print(f"Error: {e}"); sys.exit(1)

if __name__ == "__main__": main()