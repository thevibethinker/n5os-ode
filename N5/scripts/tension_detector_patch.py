import time
import requests
import os

def detect_tension_llm_with_retry(pos1, pos2, max_retries=3):
    prompt = f"""Analyze whether these two positions are in TENSION (contradiction, conflict, or incompatibility).

POSITION A:
Domain: {pos1.get('domain', 'unknown')}
Insight: {pos1.get('insight', '')}
Reasoning: {pos1.get('reasoning', '')}

POSITION B:
Domain: {pos2.get('domain', 'unknown')}
Insight: {pos2.get('insight', '')}
Reasoning: {pos2.get('reasoning', '')}

Respond with a JSON object:
{{
  "is_tension": true/false,
  "confidence": 0.0-1.0,
  "tension_type": "contradicts" | "qualifies" | "supersedes" | "none",
  "explanation": "Brief explanation of the tension or why there is none",
  "synthesis_hint": "If tension exists, how might these be reconciled?"
}}

Only mark is_tension=true if there is a genuine logical conflict or incompatibility.
Positions can both be true without tension if they apply to different contexts.
"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", ""),
                    "content-type": "application/json"
                },
                json={
                    "input": prompt,
                    "output_format": {
                        "type": "object",
                        "properties": {
                            "is_tension": {"type": "boolean"},
                            "confidence": {"type": "number"},
                            "tension_type": {"type": "string"},
                            "explanation": {"type": "string"},
                            "synthesis_hint": {"type": "string"}
                        },
                        "required": ["is_tension", "confidence", "tension_type", "explanation"]
                    }
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get("output", {})
            elif response.status_code == 429:
                time.sleep(5 * (attempt + 1))
            else:
                print(f"API Error {response.status_code}")
        except requests.exceptions.ReadTimeout:
            print(f"Timeout (attempt {attempt+1}/{max_retries})...", end=" ")
            time.sleep(2 * (attempt + 1))
        except Exception as e:
            print(f"Error: {e}")
            break
    return {"is_tension": False, "confidence": 0, "tension_type": "error", "explanation": "Max retries reached"}

# We will apply this via edit_file_llm later if needed, but for now let's just use it to wrap the call.
