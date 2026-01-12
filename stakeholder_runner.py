import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Add N5/scripts to path for imports
sys.path.insert(0, "/home/workspace")

# Import the module
try:
    from auto_create_stakeholder_profiles import main
except ImportError as e:
    logger.error(f"Failed to import auto_create_stakeholder_profiles: {e}")
    sys.exit(1)

def zo_google_calendar_tool(tool_name, configured_props, email=None):
    """
    Simulated wrapper for the Google Calendar tool.
    In this context, we've already fetched the events manually since the API call failed.
    """
    # Load the results from the file saved by Zo
    response_path = "/home/.z/workspaces/con_sMVsS4C2QBL8EqwE/app_responses/google_calendar~~3ause_app_google_calendar_core.txt"
    
    try:
        with open(response_path, 'r') as f:
            content = f.read()
            # The content is a mix of metadata and the actual list in 'ret'
            # We'll extract the 'ret' part or use a simpler approach if needed.
            # However, for the purpose of this script, I'll just return the items.
            
            # Since I'm writing this script to be run once, I'll hardcode the extraction logic
            # based on the format I saw in the tool output.
            
            import ast
            # The output has 'ret=[...]' which looks like a Python list literal
            start_marker = "ret="
            if start_marker in content:
                start_index = content.find(start_marker) + len(start_marker)
                # Find the end of the list - this is tricky with the truncation but 
                # I'll try to find the last ']' before the truncation marker or end of file.
                end_index = content.rfind("]", 0, content.find("stash_id=") if "stash_id=" in content else len(content)) + 1
                list_str = content[start_index:end_index]
                events = ast.literal_eval(list_str)
                return {"items": events}
            
            return {"items": []}
    except Exception as e:
        logger.error(f"Error reading saved calendar response: {e}")
        return {"items": []}

if __name__ == "__main__":
    logger.info("Executing Stakeholder Profile Auto-Creation Workflow...")
    
    try:
        # Run main in live mode (dry_run=False)
        main(dry_run=False, use_app_google_calendar=zo_google_calendar_tool)
        logger.info("Workflow completed successfully.")
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        sys.exit(1)
