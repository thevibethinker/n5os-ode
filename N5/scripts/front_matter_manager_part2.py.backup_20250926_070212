# === Internal LLM helper (uses Zo’s on-server LLM via edit_file_llm logic) ===
import re
import subprocess
import tempfile
import textwrap

def _quick_llm_json(prompt: str) -> dict:
    """Minimal wrapper to hit Zo’s LLM and parse JSON."""
    try:
        scratch = f"{prompt}\nAnswer in pure JSON:"
        script = textwrap.dedent(f"""
            import asyncio, sys, json
            async def run():
                from openai import AsyncOpenAI
                client = AsyncOpenAI(base_url="http://127.0.0.1:8000/v1", api_key="zo")
                r = await client.chat.completions.create(
                    model="zo-llm", messages=[{{"role":"user","content":{json.dumps(scratch)}}}],
                    temperature=0.2, max_tokens=150
                )
                print(r.choices[0].message.content.strip())
            asyncio.run(run())
        """)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(script)
            tmp.flush()
            result = subprocess.run([sys.executable, tmp.name], capture_output=True, text=True)
        Path(tmp.name).unlink(missing_ok=True)
        if result.returncode == 0:
            m = re.search(r'{.*}', result.stdout, flags=re.S)
            if m:
                return json.loads(m.group(0))
    except Exception as e:
        logger.debug(f"LLM JSON parse issue: {e}")
    return {}

def llm_infer_metadata(content_snippet, file_type, broken_paths=None):
    """Return inferred metadata JSON via Zo LLM."""
    prompt = f"""
Given {file_type} content starting with:
{content_snippet[:800]}
Produce JSON only:
{{
  \"tags\": [\"...\", \"...\"],        // 3-5 relevant keywords
  \"category\": \"workflow|output|doc\", // pick one
  \"priority\": \"high|medium|low\",
  \"suggested_links\": []         // optional fixes for broken paths {broken_paths or []}
}}
"""
    data = _quick_llm_json(prompt)
    return {
        'tags': data.get('tags', []),
        'category': data.get('category', 'unknown'),
        'priority': data.get('priority', 'medium'),
        'suggested_links': data.get('suggested_links', [])
    }
