import json
import os
import fcntl
import tempfile
from contextlib import contextmanager
from pathlib import Path

class SyncError(Exception):
    pass

@contextmanager
def fs_lock(lock_path: Path):
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def atomic_write(path: Path, data: str):
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    tmp_path.replace(path)


def write_upgrade(md_path: Path, jsonl_path: Path, item: dict):
    lock_path = jsonl_path.parent / ".lock"
    with fs_lock(lock_path):
        # Load existing items from JSONL
        items = []
        if jsonl_path.exists():
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        items.append(json.loads(line))

        # Append new item
        items.append(item)

        # Write JSONL
        jsonl_data = "".join(json.dumps(it, ensure_ascii=False) + "\n" for it in items)
        atomic_write(jsonl_path, jsonl_data)

        # Write Markdown
        md_content = "# System Upgrades\n\n"
        categories = sorted(set(it.get('category', 'Planned') for it in items))
        for cat in categories:
            md_content += f"## {cat}\n\n"
            for it in items:
                if it.get('category', 'Planned') == cat:
                    md_content += f"### {it['title']}\n\n{it.get('body', '')}\n\n"
        atomic_write(md_path, md_content)


def edit_upgrade(jsonl_path: Path, item_id: str, patch: dict):
    lock_path = jsonl_path.parent / ".lock"
    with fs_lock(lock_path):
        # Load items
        items = []
        if jsonl_path.exists():
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        items.append(json.loads(line))

        found = False
        for item in items:
            if item.get('id') == item_id:
                item.update(patch)
                found = True
                break

        if not found:
            raise SyncError(f"Item with ID {item_id} not found")

        # Write JSONL
        jsonl_data = "".join(json.dumps(it, ensure_ascii=False) + "\n" for it in items)
        atomic_write(jsonl_path, jsonl_data)

        # Write Markdown
        md_content = "# System Upgrades\n\n"
        categories = sorted(set(it.get('category', 'Planned') for it in items))
        for cat in categories:
            md_content += f"## {cat}\n\n"
            for it in items:
                if it.get('category', 'Planned') == cat:
                    md_content += f"### {it['title']}\n\n{it.get('body', '')}\n\n"
        atomic_write(jsonl_path.parent / "system-upgrades.md", md_content)


def list_upgrades(jsonl_path: Path, filters: dict = None) -> list:
    items = []
    if jsonl_path.exists():
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line))
    if filters:
        for k, v in filters.items():
            items = [item for item in items if item.get(k) == v]
    return items


def render_markdown(items: list) -> str:
    md_content = "# System Upgrades\n\n"
    categories = sorted(set(it.get('category', 'Planned') for it in items))
    for cat in categories:
        md_content += f"## {cat}\n\n"
        for it in items:
            if it.get('category', 'Planned') == cat:
                md_content += f"### {it['title']}\n\n{it.get('body', '')}\n\n"
    return md_content
