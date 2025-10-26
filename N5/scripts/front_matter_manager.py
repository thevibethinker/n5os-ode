#!/usr/bin/env python3
"""
Front Matter Manager for N5 OS (Zo-LLM edition)
Programmatically applies, updates, and validates front matter using Zo’s local LLM.
"""

import yaml
import hashlib
import re
import json
from pathlib import Path
from datetime import datetime
import logging
import re
import subprocess
import tempfile
import textwrap

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SCHEMA_PATH = Path('/home/workspace/N5_mirror/config/front_matter_schema.yaml')
if not SCHEMA_PATH.exists():
    default_schema = {
        '.md': {
            'title': None,
            'date': None,
            'version': '1.0',
            'status': 'production-ready',
            'category': None,
            'tags': [],
            'related_files': [],
            'anchors': {},
            'validation': 'n5os-compliant',
            'last-tested': None
        },
        '.json': {
            'source': None,
            'generated_date': None,
            'priority': 'medium',
            'tags': [],
            'related_files': [],
            'voice_schema': {},
            'checksum': None
        }
    }
    SCHEMA_PATH.parent.mkdir(exist_ok=True)
    with open(SCHEMA_PATH, 'w') as f:
        yaml.dump(default_schema, f)
SCHEMA = yaml.safe_load(open(SCHEMA_PATH))

# === Internal LLM helper (uses Zo’s on-server LLM via edit_file_llm logic) ===
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

def generate_metadata(file_path: Path, content: str):
    """Build complete metadata dict."""
    file_type = file_path.suffix
    metadata = SCHEMA.get(file_type, {}).copy()

    now = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    metadata['date'] = now
    metadata['last-tested'] = now
    metadata['generated_date'] = now
    metadata['checksum'] = hashlib.md5(content.encode()).hexdigest()

    paths = re.findall(r'/home/workspace/[\w/.-]+\.\w+', content)
    valid_links = [p for p in paths if Path(p).exists()]
    broken_paths = [p for p in paths if p not in valid_links]

    inferred = llm_infer_metadata(content[:1000], file_type, broken_paths)
    metadata['tags'] = inferred.get('tags', [])
    metadata['category'] = inferred.get('category', 'unknown')
    metadata['priority'] = inferred.get('priority', 'medium')
    metadata['related_files'] = inferred.get('suggested_links', valid_links)

    metadata['anchors'] = {
        'input': valid_links[0] if valid_links else None,
        'output': str(file_path)
    }

    return metadata

def parse_front_matter(file_path: Path) -> dict:
    """Return existing YAML block or empty dict."""
    content = file_path.read_text()
    if file_path.suffix == '.md' and content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return yaml.safe_load(content[3:end]) or {}
    elif file_path.suffix == '.json':
        try:
            data = json.loads(content)
            return data.get('metadata', {})
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error in {file_path}: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Unexpected error parsing JSON in {file_path}: {e}")
            return {}
    return {}

def apply_front_matter(file_path: Path):
    """Idempotent apply/merge front matter."""
    logger.info(f"Processing: {file_path}")
    content = file_path.read_text()
    existing = parse_front_matter(file_path)

    new_metadata = generate_metadata(file_path, content)
    merged = {**existing, **new_metadata}  # new wins

    if file_path.suffix == '.md':
        yaml_str = yaml.dump(merged, sort_keys=False)
        body = content.split('---\n', 2)[-1] if content.startswith('---') else content
        file_path.write_text(f"---\n{yaml_str}---\n{body}")
    elif file_path.suffix == '.json':
        try:
            data = json.loads(content) if content.strip() else {}
        except json.JSONDecodeError as e:
            logger.warning(f"Skipping {file_path} due to JSON decode error: {e}")
            return
        except Exception as e:
            logger.warning(f"Skipping {file_path} due to unexpected error: {e}")
            return
        data['metadata'] = merged
        file_path.write_text(json.dumps(data, indent=2))

    logger.info(f"Updated front matter on: {file_path}")

def validate_links(metadata: dict) -> bool:
    """Return True if all related_files exist; else log."""
    ok = True
    for link in metadata.get('related_files', []):
        if not Path(link).exists():
            logger.warning(f"Broken link: {link}")
            ok = False
    return ok

def scan_and_apply(root_dir: str = '/home/workspace/N5_mirror', patterns=None):
    """Walk workspace and apply missing/invalid front matter."""
    patterns = patterns or ['*.md', '*.json']
    root = Path(root_dir)
    for pat in patterns:
        for file in root.rglob(pat):
            if any(skip in str(file) for skip in ('logs', '__pycache__', '.git')):
                continue
            existing = parse_front_matter(file)
            if not existing or not validate_links(existing):
                apply_front_matter(file)

if __name__ == '__main__':
    scan_and_apply()
