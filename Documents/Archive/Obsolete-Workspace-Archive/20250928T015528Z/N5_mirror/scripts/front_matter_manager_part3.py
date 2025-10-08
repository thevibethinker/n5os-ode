# === Core logic (deterministic + LLM) ===
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
        except Exception:
            pass
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
        data = json.loads(content) if content.strip() else {}
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
