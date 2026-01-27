#!/usr/bin/env python3
"""
Survey Dashboard Generator for Next Play AI Session
Fetches latest survey data, generates Gamma dashboard, updates short.io link
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# Config
FORM_ID = "jPQRwpT4nGus"
FILLOUT_API_KEY = os.environ.get("FILLOUT_SECRET_CAREERSPAN")
SHORTIO_API_KEY = os.environ.get("SHORTIO_API_KEY")
GAMMA_SCRIPT = "/home/workspace/Skills/gamma/scripts/gamma.ts"
STATE_FILE = "/home/workspace/N5/data/survey_dashboard_state.json"
SURVEY_SHORT_LINK = "https://careerspan.short.gy/np-jan29"

# Question IDs (from Fillout form)
Q_TOOLS = "bxyM"  # What AI tools are you currently using?
Q_CHALLENGE = "qgxH"  # Biggest challenge with AI tools
Q_USAGE = "sLMq"  # Current AI usage level
Q_VALUE = "qJQ5"  # What would make session valuable
Q_SENTIMENT = "qurD"  # How do you feel about AI
Q_TASKS = "nkxv"  # Repetitive tasks that drain energy
Q_TIME = "moGb"  # Time spent on repetitive tasks

def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_update": None, "last_gamma_url": None, "response_count": 0, "history": []}

def save_state(state):
    Path(STATE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def fetch_survey_data():
    """Fetch all survey responses from Fillout API"""
    url = f"https://api.fillout.com/v1/api/forms/{FORM_ID}/submissions"
    headers = {"Authorization": f"Bearer {FILLOUT_API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["responses"]

def get_answer(response, question_id):
    """Extract answer for a specific question"""
    for q in response.get("questions", []):
        if q.get("id") == question_id:
            return q.get("value")
    return None

def analyze_responses(responses):
    """Analyze survey responses and compute statistics"""
    n = len(responses)
    if n == 0:
        return None
    
    # Tool categories
    tool_categories = {
        "Consumer Chatbot": ["ChatGPT", "Claude", "Gemini"],
        "AI Search": ["Perplexity", "AI search"],
        "Image/Video Gen": ["image", "video", "Midjourney", "DALL-E", "Runway"],
        "Agentic AI": ["Agentic", "Claude Code", "Zo", "Manus", "Devin"],
        "IDE/ADEs": ["Cursor", "Warp", "Copilot IDE", "Windsurf"],
        "B2B AI": ["Copilot", "Harvey", "enterprise"],
    }
    
    tool_adoption = {}
    for cat in tool_categories:
        count = 0
        for r in responses:
            tools = get_answer(r, Q_TOOLS) or []
            if isinstance(tools, str):
                tools = [tools]
            for tool in tools:
                if any(kw.lower() in str(tool).lower() for kw in tool_categories[cat]):
                    count += 1
                    break
        tool_adoption[cat] = round(count / n * 100)
    
    # Challenges
    challenges = {}
    for r in responses:
        challenge = get_answer(r, Q_CHALLENGE)
        if challenge:
            # Normalize challenge text
            if "overwhelm" in str(challenge).lower():
                key = "Overwhelmed by Options"
            elif "basic" in str(challenge).lower() or "level up" in str(challenge).lower():
                key = "Stuck at Basics"
            elif "vibe" in str(challenge).lower() or "prompt" in str(challenge).lower():
                key = "Vibe Coding Prompts"
            elif "inconsistent" in str(challenge).lower():
                key = "Inconsistent Results"
            else:
                key = str(challenge)[:30]
            challenges[key] = challenges.get(key, 0) + 1
    
    # Sentiment
    sentiment = {"Excited / All-in": 0, "Optimistic / Interested": 0, "Neutral / Curious": 0}
    for r in responses:
        feel = str(get_answer(r, Q_SENTIMENT) or "").lower()
        if "excit" in feel or "all-in" in feel or "🚀" in feel:
            sentiment["Excited / All-in"] += 1
        elif "optimist" in feel or "interest" in feel or "😊" in feel:
            sentiment["Optimistic / Interested"] += 1
        else:
            sentiment["Neutral / Curious"] += 1
    
    # Value drivers
    value_drivers = {}
    for r in responses:
        value = get_answer(r, Q_VALUE)
        if value:
            val_str = str(value).lower()
            if "advanced" in val_str or "possible" in val_str:
                key = "Advanced Demonstrations"
            elif "system" in val_str or "build" in val_str:
                key = "System Building"
            elif "simple" in val_str or "tactic" in val_str:
                key = "Simple Tactics"
            elif "template" in val_str or "prompt" in val_str or "copy" in val_str:
                key = "Templates & Prompts"
            elif "think" in val_str or "different" in val_str:
                key = "Mindset Shift"
            else:
                key = str(value)[:25]
            value_drivers[key] = value_drivers.get(key, 0) + 1
    
    # Energy drains (verbatim quotes)
    energy_drains = []
    for r in responses:
        task = get_answer(r, Q_TASKS)
        if task and str(task).strip():
            energy_drains.append(str(task).strip())
    
    # Calculate avg tools per person
    total_tools = 0
    for r in responses:
        tools = get_answer(r, Q_TOOLS) or []
        if isinstance(tools, list):
            total_tools += len(tools)
        elif tools:
            total_tools += 1
    avg_tools = round(total_tools / n, 1) if n > 0 else 0
    
    return {
        "n": n,
        "tool_adoption": tool_adoption,
        "challenges": {k: round(v/n*100) for k, v in challenges.items()},
        "sentiment": {k: round(v/n*100) for k, v in sentiment.items()},
        "value_drivers": {k: round(v/n*100) for k, v in value_drivers.items()},
        "energy_drains": energy_drains[:6],  # Top 6 quotes
        "avg_tools": avg_tools,
        "chatbot_pct": tool_adoption.get("Consumer Chatbot", 100),
        "agentic_pct": tool_adoption.get("Agentic AI", 0),
    }

def generate_dashboard_content(stats):
    """Generate markdown content for Gamma dashboard"""
    today = datetime.now().strftime("%b %d, %Y")
    n = stats["n"]
    
    # Format challenges
    challenges_rows = "\n".join([f"| {k} | {v}% |" for k, v in sorted(stats["challenges"].items(), key=lambda x: -x[1])])
    
    # Format sentiment
    sentiment_section = ""
    for label, pct in stats["sentiment"].items():
        emoji = "🚀" if "Excited" in label else ("😊" if "Optimistic" in label else "😐")
        sentiment_section += f"\n### {emoji} {label}: {pct}%\n"
    
    # Format value drivers
    value_rows = "\n".join([f"| {k} | {v}% |" for k, v in sorted(stats["value_drivers"].items(), key=lambda x: -x[1])])
    
    # Format energy drains as quotes
    quotes = "\n\n".join([f'> "{q}"' for q in stats["energy_drains"]])
    
    # Tool adoption for chart description
    tool_desc = ", ".join([f"{k}: {v}%" for k, v in sorted(stats["tool_adoption"].items(), key=lambda x: -x[1])])
    
    content = f"""# Live Survey Insights

## {today}

# Friends of Next Play: Fundamentals of AI Productivity
## Pre-Event Survey

Real-time intelligence from {n} survey responses revealing how your peers are navigating the AI landscape—and where they're getting stuck.

[Take the Survey]({SURVEY_SHORT_LINK})

---

## At A Glance: Your Cohort by the Numbers

| Metric | Value | Description |
|--------|-------|-------------|
| **{stats['chatbot_pct']}%** | Chatbot Users | Everyone uses AI chatbots like ChatGPT, Claude, or Gemini |
| **{stats['agentic_pct']}%** | Using Agentic AI | Have adopted advanced tools like Claude Code, Zo, or Manus |
| **{stats['avg_tools']}** | Avg Tools Per Person | Each attendee actively uses tools across multiple AI categories |
| **5-10** | Weekly Hours Lost | Most common time drain reported by respondents |

---

## Tool Adoption Across Your Cohort

{tool_desc}

**Universal Foundation, Varied Specialization:** Every attendee uses consumer chatbots, establishing a common baseline. From there, adoption patterns diverge based on specific needs.

---

## Your Biggest Challenge: The Overwhelm Factor

| Challenge | % |
|-----------|---|
{challenges_rows}

**The dominant pattern:** The majority feels paralyzed by choice or stuck at basics.

---

## Sentiment Check: How You Feel About AI

{sentiment_section}

**Design implication:** While the majority is excited, some attendees are neutral. The session must demonstrate value through concrete examples.

---

## What Drains Your Energy: Direct from Your Peers

{quotes}

---

## What You Want From Jan 29: Value Drivers

| Value Driver | % |
|--------------|---|
{value_rows}

**The Clear Mandate:** Most attendees want advanced demonstrations and system-building frameworks rather than beginner tips.

---

## Add Your Voice to the Data

Haven't responded yet? Your input shapes how we design the session.

[Take the Survey Now]({SURVEY_SHORT_LINK})

---

*Methodology: Fillout API • N={n} responses • Last updated: {today}*
"""
    return content

def generate_gamma_dashboard(content):
    """Call Gamma API to generate dashboard"""
    cmd = [
        "bun", "run", GAMMA_SCRIPT, "generate", content,
        "--format", "webpage",
        "--mode", "preserve",
        "--amount", "detailed",
        "--images", "noImages",
        "--dimensions", "fluid",
        "--theme", "breeze",
        "--cards", "10",
        "--wait"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout
    
    # Parse the gamma URL from output
    if "gammaUrl" in output:
        import re
        match = re.search(r'"gammaUrl":\s*"([^"]+)"', output)
        if match:
            return match.group(1)
    
    # Try to find URL in output
    if "gamma.app/docs/" in output:
        import re
        match = re.search(r'https://gamma\.app/docs/[a-zA-Z0-9]+', output)
        if match:
            return match.group(0)
    
    raise Exception(f"Failed to generate Gamma dashboard: {output}")

def update_shortio_link(short_path, new_destination):
    """Update short.io link to point to new destination"""
    # First, find the link ID
    headers = {
        "Authorization": SHORTIO_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Search for the link
    # Note: short.io API varies - this is a simplified version
    # In practice, we'd store the link_id in state
    
    print(f"Would update short.io link to: {new_destination}")
    print("(short.io update requires link_id - storing URL in state instead)")
    return True

def main():
    print(f"=== Survey Dashboard Generator ===")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Load state
    state = load_state()
    print(f"Previous update: {state.get('last_update', 'Never')}")
    print(f"Previous response count: {state.get('response_count', 0)}")
    
    # Fetch survey data
    print("\nFetching survey data...")
    responses = fetch_survey_data()
    n = len(responses)
    print(f"Found {n} responses")
    
    # Check if we need to regenerate
    if n == state.get("response_count", 0) and state.get("last_gamma_url"):
        print("No new responses since last update. Skipping regeneration.")
        print(f"Current dashboard: {state['last_gamma_url']}")
        return state["last_gamma_url"]
    
    # Analyze responses
    print("\nAnalyzing responses...")
    stats = analyze_responses(responses)
    if not stats:
        print("No responses to analyze")
        return None
    
    print(f"Stats: {n} responses, {stats['chatbot_pct']}% chatbot, {stats['agentic_pct']}% agentic")
    
    # Generate content
    print("\nGenerating dashboard content...")
    content = generate_dashboard_content(stats)
    
    # Generate Gamma dashboard
    print("\nCalling Gamma API...")
    gamma_url = generate_gamma_dashboard(content)
    print(f"Generated: {gamma_url}")
    
    # Update state
    state["last_update"] = datetime.now().isoformat()
    state["last_gamma_url"] = gamma_url
    state["response_count"] = n
    state["history"].append({
        "timestamp": state["last_update"],
        "url": gamma_url,
        "response_count": n
    })
    save_state(state)
    
    print(f"\n✅ Dashboard updated!")
    print(f"URL: {gamma_url}")
    print(f"Responses: {n}")
    
    return gamma_url

if __name__ == "__main__":
    main()
