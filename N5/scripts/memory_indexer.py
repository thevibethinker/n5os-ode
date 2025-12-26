#!/usr/bin/env python3
"""Worker 3 (Memory Indexer) for the N5 Cognition build."""

from __future__ import annotations

import argparse
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from N5.cognition.n5_memory_client import N5MemoryClient


LOG = logging.getLogger("memory_indexer")


@dataclass
class Block:
    content: str
    block_type: str
    start_line: int
    end_line: int


class BlockChunker:
    """Chunk files into smaller semantic blocks."""

    MAX_CHARS = 2_400

    def chunk(self, path: Path) -> List[Block]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        blocks: List[Block] = []
        buffer: List[str] = []
        start_line = 0

        def flush(block_type: str = "paragraph"):
            nonlocal buffer, start_line

            if not buffer:
                start_line = 0
                return

            content = "\n".join(buffer).strip()
            if content:
                blocks.append(Block(content=content, block_type=block_type, start_line=start_line, end_line=start_line + len(buffer) - 1))

            buffer = []
            start_line = 0

        for idx, raw_line in enumerate(lines, start=1):
            line = raw_line.rstrip()
            stripped = line.strip()

            if stripped.startswith("#"):
                flush()
                heading = stripped.lstrip("# ").strip()
                if heading:
                    blocks.append(Block(content=heading, block_type="heading", start_line=idx, end_line=idx))
                continue

            if not stripped:
                flush()
                continue

            if not buffer:
                start_line = idx

            buffer.append(line)

            if len("\n".join(buffer)) > self.MAX_CHARS:
                flush()

        flush()
        return blocks


class MemoryIndexPlan:
    """Handles the orchestration of indexing and logging."""

    def __init__(self, client: N5MemoryClient, chunker: BlockChunker, dry_run: bool = False):
        self.client = client
        self.chunker = chunker
        self.dry_run = dry_run
        self.stats = {"files": 0, "blocks": 0, "with_dates": 0}

    def _compute_hash(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def run(self, paths: Sequence[Path]) -> None:
        for path in self._expand_paths(paths):
            self.stats["files"] += 1
            self._index_file(path)

        LOG.info(
            "Indexed %d files (%d with dates) producing %d blocks.",
            self.stats["files"],
            self.stats["with_dates"],
            self.stats["blocks"]
        )

    def _expand_paths(self, roots: Sequence[Path]) -> Iterator[Path]:
        for root in roots:
            if root.is_file():
                yield root
            elif root.is_dir():
                for candidate in root.rglob("*.md"):
                    yield candidate
            else:
                LOG.warning("Skipping missing path %s", root)

    def _index_file(self, path: Path) -> None:
        try:
            resource_hash = self._compute_hash(path)
            
            # Check if resource is up to date (resuming logic)
            existing_res = self.client._get_db().execute(
                "SELECT hash FROM resources WHERE path = ?", (str(path),)
            ).fetchone()
            
            if existing_res and existing_res[0] == resource_hash:
                LOG.debug("Skipping %s (unchanged)", path)
                return

            LOG.info("Indexing %s", path)
            
            # Extract content_date from frontmatter
            content_date = self.client.extract_content_date(str(path))
            if content_date:
                self.stats["with_dates"] += 1
                LOG.debug("Extracted content_date: %s", content_date)
            
            resource_id = self.client.store_resource(str(path), resource_hash, content_date=content_date)

            if self.dry_run:
                LOG.info("Dry run enabled. Would remove blocks for %s.", resource_id)
                return

            self.client.delete_resource_blocks(resource_id)
            blocks = self.chunker.chunk(path)

            if not blocks:
                LOG.debug("No content block extracted for %s", path)
                return

            for block in blocks:
                if not block.content:
                    continue
                self.client.add_block(
                    resource_id=resource_id,
                    content=block.content,
                    block_type=block.block_type,
                    start_line=block.start_line,
                    end_line=block.end_line,
                    content_date=content_date,
                )
                self.stats["blocks"] += 1
        except Exception as e:
            LOG.error("Failed to index %s: %s", path, e)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index files into the N5 cognition brain at block-level granularity.")
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files or directories to index (directories scan for .md files recursively).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Scan and chunk files without writing to the database.")
    parser.add_argument("--log-level", default="INFO", help="Set the log level (DEBUG | INFO | WARNING | ERROR).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")

    chunker = BlockChunker()
    client = N5MemoryClient()
    plan = MemoryIndexPlan(client=client, chunker=chunker, dry_run=args.dry_run)

    plan.run(args.paths)


if __name__ == "__main__":
    main()






