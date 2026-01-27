#!/usr/bin/env python3
"""
Survey Dashboard Generator
Generalized skill for creating Gamma dashboards from Fillout surveys.
"""

import os
import sys
import json
import argparse
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
GAMMA_SCRIPT = "/home/workspace/Skills/gamma/scripts/gamma.ts"
STATE_DIR = Path("/home/workspace/N5/data")

def load_config(config_path: str) -> dict:
    """Load aesthetic configuration"""
    with open(config_path) as f:
        return json.load(f)

def get_state_file(form_id: str) -> Path:
    """Get state file path for a form"""
    return STATE_DIR / f"survey_dashboard_{form_id}.json"

def load_state(form_id: str) -> dict:
    """Load state for a form"""
    state_file = get_state_file(form_id)
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {"last_update": None, "last_gamma_url": None, "response_count": 0, "history": []}

def save_state(form_id: str, state: dict):
    """Save state for a form"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(get_state_file(form_id), 'w') as f:
        json.dump(state, f, indent=2)

def get_fillout_api_key(account: str = None) -> str:
    """Get Fillout API key from environment"""
    if account:
        key = os.environ.get(f"FILLOUT_SECRET_{account.upper()}")
        if key:
            return key
    # Try common account names
    for acc in ["CAREERSPAN", "PERSONAL", ""]:
        key = os.environ.get(f"FILLOUT_SECRET_{acc}" if acc else "FILLOUT_API_KEY")
        if key:
            return key
    raise ValueError("No Fillout API key found. Set FILLOUT_SECRET_<ACCOUNT> or FILLOUT_API_KEY")

def fetch_survey_data(form_id: str, api_key: str) -> list:
    """Fetch all survey responses from Fillout API"""
    url = f"https://api.fillout.com/v1/api/forms/{form_id}/submissions"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["responses"]

def get_answer(response: dict, question_id: str):
    """Extract answer for a specific question"""
    for q in response.get("questions", []):
        if q.get("id") == question_id:
            return q.get("value")
    return None

def analyze_responses(responses: list, question_mapping: dict = None) -> dict:
    """Analyze survey responses and compute statistics"""
    n = len(responses)
    if n == 0:
        return None
    
    # Default question mapping (can be overridden by config)
    qmap = question_mapping or {}
    
    # Generic analysis - count all questions
    question_stats = {}
    for r in responses:
        for q in r.get("questions", []):
            qid = q.get("id")
            qname = q.get("name", qid)
            value = q.get("value")
            
            if qid not in question_stats:
                question_stats[qid] = {
                    "name": qname,
                    "values": {},
                    "raw_values": []
                }
            
            if value:
                # Handle multi-select
                if isinstance(value, list):
                    for v in value:
                        v_str = str(v)
                        question_stats[qid]["values"][v_str] = question_stats[qid]["values"].get(v_str, 0) + 1
                else:
                    v_str = str(value)[:50]  # Truncate long values
                    question_stats[qid]["values"][v_str] = question_stats[qid]["values"].get(v_str, 0) + 1
                question_stats[qid]["raw_values"].append(value)
    
    # Convert counts to percentages
    for qid in question_stats:
        for v in question_stats[qid]["values"]:
            question_stats[qid]["values"][v] = round(question_stats[qid]["values"][v] / n * 100)
    
    return {
        "n": n,
        "questions": question_stats,
        "timestamp": datetime.now().isoformat()
    }

def generate_dashboard_content(stats: dict, config: dict, survey_link: str = None) -> str:
    """Generate markdown content for Gamma dashboard"""
    today = datetime.now().strftime("%b %d, %Y")
    n = stats["n"]
    branding = config.get("branding", {})
    title_prefix = branding.get("title_prefix", "Survey Insights")
    cta_text = branding.get("cta_text", "Take the Survey")
    cta_secondary = branding.get("cta_text_secondary", "Add Your Voice")
    
    # Build sections from question stats
    sections = []
    for qid, qdata in stats["questions"].items():
        if qdata["values"]:
            # Create table for this question
            rows = "\n".join([
                f"| {v} | {pct}% |" 
                for v, pct in sorted(qdata["values"].items(), key=lambda x: -x[1])[:8]
            ])
            sections.append(f"""
## {qdata['name']}

| Response | % |
|----------|---|
{rows}
""")
    
    survey_cta = f"\n[{cta_text}]({survey_link})\n" if survey_link else ""
    survey_cta_end = f"\n[{cta_secondary}]({survey_link})\n" if survey_link else ""
    
    content = f"""# {title_prefix}

## {today}

Real-time intelligence from {n} survey responses.
{survey_cta}
---

## At A Glance

**{n}** total responses analyzed

---
{"".join(sections)}
---

{survey_cta_end}

*Last updated: {today} • N={n} responses*
"""
    return content

def generate_gamma_dashboard(content: str, config: dict) -> str:
    """Call Gamma API to generate dashboard"""
    import tempfile
    gamma_config = config.get("gamma", {})
    
    # Write content to temp file to avoid shell escaping issues
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        content_file = f.name
    
    try:
        # Read content from file in the command
        cmd = [
            "bun", "run", GAMMA_SCRIPT, "generate", content,
            "--format", gamma_config.get("format", "webpage"),
            "--mode", gamma_config.get("mode", "preserve"),
            "--amount", gamma_config.get("amount", "detailed"),
            "--images", gamma_config.get("images", "noImages"),
            "--dimensions", gamma_config.get("dimensions", "fluid"),
            "--theme", gamma_config.get("theme", "breeze"),
            "--cards", str(gamma_config.get("cards", 10)),
            "--wait"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        output = result.stdout + result.stderr
        
        if result.returncode != 0:
            print(f"Gamma command failed with return code {result.returncode}")
            print(f"stdout: {result.stdout[:500]}")
            print(f"stderr: {result.stderr[:500]}")
        
        # Parse the gamma URL from output
        import re
        if "gammaUrl" in output:
            match = re.search(r'"gammaUrl":\s*"([^"]+)"', output)
            if match:
                return match.group(1)
        
        if "gamma.app/docs/" in output:
            match = re.search(r'https://gamma\.app/docs/[a-zA-Z0-9]+', output)
            if match:
                return match.group(0)
        
        raise Exception(f"Failed to parse Gamma URL from output: {output[:500]}")
    finally:
        os.unlink(content_file)

def main():
    parser = argparse.ArgumentParser(description="Generate Gamma dashboard from Fillout survey")
    parser.add_argument("--form-id", required=True, help="Fillout form ID")
    parser.add_argument("--config", default=str(SKILL_DIR / "assets/configs/zo-style.json"),
                        help="Path to aesthetic config JSON")
    parser.add_argument("--account", help="Fillout account name (for API key lookup)")
    parser.add_argument("--survey-link", help="Short link to survey for CTAs")
    parser.add_argument("--force", action="store_true", help="Force regeneration even if no new responses")
    parser.add_argument("--status", action="store_true", help="Just show current status")
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    print(f"=== Survey Dashboard Generator ===")
    print(f"Config: {config.get('name', 'Unknown')}")
    print(f"Theme: {config.get('gamma', {}).get('theme', 'default')}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Load state
    state = load_state(args.form_id)
    
    if args.status:
        print(f"\nForm: {args.form_id}")
        print(f"Last update: {state.get('last_update', 'Never')}")
        print(f"Response count: {state.get('response_count', 0)}")
        print(f"Current URL: {state.get('last_gamma_url', 'None')}")
        print(f"Total generations: {len(state.get('history', []))}")
        return
    
    print(f"\nPrevious update: {state.get('last_update', 'Never')}")
    print(f"Previous response count: {state.get('response_count', 0)}")
    
    # Get API key and fetch data
    api_key = get_fillout_api_key(args.account)
    print("\nFetching survey data...")
    responses = fetch_survey_data(args.form_id, api_key)
    n = len(responses)
    print(f"Found {n} responses")
    
    # Check if we need to regenerate
    if not args.force and n == state.get("response_count", 0) and state.get("last_gamma_url"):
        print("No new responses since last update. Skipping regeneration.")
        print(f"Current dashboard: {state['last_gamma_url']}")
        return state["last_gamma_url"]
    
    # Analyze
    print("\nAnalyzing responses...")
    stats = analyze_responses(responses)
    if not stats:
        print("No responses to analyze")
        return None
    
    print(f"Analyzed {n} responses across {len(stats['questions'])} questions")
    
    # Generate content
    print("\nGenerating dashboard content...")
    content = generate_dashboard_content(stats, config, args.survey_link)
    
    # Generate Gamma dashboard
    print("\nCalling Gamma API...")
    gamma_url = generate_gamma_dashboard(content, config)
    print(f"Generated: {gamma_url}")
    
    # Update state
    state["last_update"] = datetime.now().isoformat()
    state["last_gamma_url"] = gamma_url
    state["response_count"] = n
    state["config_used"] = args.config
    state["history"].append({
        "timestamp": state["last_update"],
        "url": gamma_url,
        "response_count": n,
        "config": config.get("name")
    })
    save_state(args.form_id, state)
    
    print(f"\n✅ Dashboard updated!")
    print(f"URL: {gamma_url}")
    print(f"Responses: {n}")
    
    return gamma_url

if __name__ == "__main__":
    main()
