import sys
import os
import asyncio
import json
import re

# Add the scripts directory to path
sys.path.append('/home/workspace/N5/scripts')

from auto_create_stakeholder_profiles import main

def tool_wrapper(tool_name, configured_props):
    import requests
    
    prompt = f"Call use_app_google_calendar(tool_name='{tool_name}', configured_props={json.dumps(configured_props)}) and return the raw JSON result only."
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
            "content-type": "application/json"
        },
        json={"input": prompt}
    )
    
    try:
        output_text = response.json()["output"]
        # Match markdown json block or the raw string
        json_match = re.search(r'```json\s*(.*?)\s*```', output_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            data = json.loads(output_text)
            
        # The script expects the response structure of the API, e.g. {'items': [...]}
        # If data is a list, wrap it in 'items'
        if isinstance(data, list):
            return {"items": data}
        return data
    except Exception as e:
        print(f"DEBUG: Tool call failed: {e}")
        return {"items": []}

async def execute():
    try:
        result = main(dry_run=False, use_app_google_calendar=tool_wrapper)
        if asyncio.iscoroutine(result):
            await result
        print("WORKFLOW_SUCCESS")
    except Exception as e:
        print(f"WORKFLOW_ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(execute())
