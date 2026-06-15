#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Optional

import requests

WORKSPACE = Path("/home/workspace")
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

from N5.lib.meeting_shapes import (
    PRIMARY_SHAPES,
    POST_PROCESSORS,
    MACHINE_READABLE_SHAPE_FILES,
    build_context,
    render_context_markdown,
    determine_shape_plan,
    build_shape_prompt,
    build_evidence_json_prompt,
    build_graph_edges_prompt,
    sanitize_model_output,
    sanitize_json_output,
    read_shape_bundle,
    shape_filename,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def _ts() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def _call_zo(prompt: str, timeout: int = 300, retries: int = 2, json_mode: bool = False) -> str:
    token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
    if not token:
        raise RuntimeError('ZO_CLIENT_IDENTITY_TOKEN not set')
    last_error: Optional[str] = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                'https://api.zo.computer/zo/ask',
                headers={'authorization': token, 'content-type': 'application/json'},
                json={'input': prompt},
                timeout=timeout,
            )
            if resp.status_code != 200:
                last_error = f'HTTP {resp.status_code}: {resp.text[:200]}'
            else:
                out = resp.json().get('output', '')
                if not isinstance(out, str):
                    out = json.dumps(out)
                if out and out.strip():
                    return out
                last_error = 'empty output'
        except Exception as e:
            last_error = str(e)
        if attempt < retries:
            logger.warning(f'    zo/ask attempt {attempt}/{retries} failed: {last_error}; retrying')
    raise RuntimeError(f'zo/ask failed after {retries} attempts: {last_error}')


def _read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2))


def _append_status(manifest: dict[str, Any], status: str) -> None:
    history = manifest.setdefault('status_history', [])
    if history and history[-1].get('status') == status:
        return
    history.append({'status': status, 'at': _ts()})

def generate_shapes(meeting_path: Path, manifest: dict[str, Any], transcript: str, *, dry_run: bool = False) -> dict[str, Any]:
    context = build_context(meeting_path, manifest, transcript)
    selected, selection_meta = determine_shape_plan(transcript, context)
    shape_codes = [c for c in selected if c in PRIMARY_SHAPES or c in ('S08',)]
    post_processors = [c for c in selected if c in POST_PROCESSORS]

    if dry_run:
        return {
            'dry_run': True,
            'shape_codes': shape_codes,
            'post_processors': post_processors,
            'selection': selection_meta,
        }

    manifest['shape_selection'] = {'selected_at': _ts(), **selection_meta}
    manifest.setdefault('shapes', {})
    manifest['shapes']['policy'] = 'shape_router_v1'
    manifest['shapes']['requested'] = shape_codes + post_processors
    manifest['shapes']['generated'] = []
    manifest['shapes']['failed'] = []
    manifest['status'] = 'processing'
    _append_status(manifest, 'processing')

    generated: list[str] = []
    failed: list[dict[str, str]] = []

    # S01 is deterministic/local
    if 'S01' in shape_codes:
        s01_path = meeting_path / shape_filename('S01')
        s01_path.write_text(render_context_markdown(context))
        generated.append('S01')
        manifest['shapes']['generated'].append('S01')
        logger.info('    ✓ Written: S01_CONTEXT.md')

    # LLM shapes
    for code in [c for c in shape_codes if c != 'S01']:
        try:
            logger.info(f'  Generating {code}...')
            prompt = build_shape_prompt(code, transcript, context, meeting_path)
            output = sanitize_model_output(_call_zo(prompt))
            out_path = meeting_path / shape_filename(code)
            out_path.write_text(output)
            generated.append(code)
            manifest['shapes']['generated'].append(code)
            logger.info(f'    ✓ Written: {out_path.name}')

            if code == 'S03':
                json_prompt = build_evidence_json_prompt(transcript, context, meeting_path)
                evidence_json = sanitize_json_output(_call_zo(json_prompt))
                mr_path = meeting_path / MACHINE_READABLE_SHAPE_FILES['S03']
                mr_path.write_text(json.dumps(evidence_json, indent=2))
                logger.info(f'    ✓ Written: {mr_path.name}')
        except Exception as e:
            failed.append({'shape': code, 'error': str(e)})
            manifest['shapes']['failed'].append(code)
            logger.error(f'    ✗ Failed {code}: {e}')
        _write_manifest(meeting_path / 'manifest.json', manifest)

    # Post-processors read shape bundle, not transcript
    bundle = read_shape_bundle(meeting_path)
    for code in post_processors:
        try:
            if code == 'PP_GRAPH_EDGES':
                prompt = build_graph_edges_prompt(meeting_path, context, bundle)
                output = _call_zo(prompt)
                out_path = meeting_path / shape_filename(code)
                out_path.write_text(output.strip() + '\n')
                generated.append(code)
                manifest['shapes']['generated'].append(code)
                logger.info(f'    ✓ Written: {out_path.name}')
        except Exception as e:
            failed.append({'shape': code, 'error': str(e)})
            manifest['shapes']['failed'].append(code)
            logger.error(f'    ✗ Failed {code}: {e}')
        _write_manifest(meeting_path / 'manifest.json', manifest)

    manifest['shapes']['selection'] = selection_meta
    manifest['shapes']['generated'] = generated
    manifest['shapes']['failed'] = [f['shape'] for f in failed]
    if failed and not generated:
        manifest['status'] = 'failed'
        _append_status(manifest, 'failed')
    elif failed:
        manifest['status'] = 'partial'
        _append_status(manifest, 'partial')
    else:
        manifest['status'] = 'processed'
        manifest.setdefault('timestamps', {})['processed_at'] = _ts()
        _append_status(manifest, 'processed')
    _write_manifest(meeting_path / 'manifest.json', manifest)

    return {
        'path': str(meeting_path),
        'shapes_generated': generated,
        'shapes_failed': failed,
        'selection_metadata': selection_meta,
        'status': manifest['status'],
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate canonical S-shapes for a meeting folder')
    parser.add_argument('meeting_path')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    meeting_path = Path(args.meeting_path)
    manifest_path = meeting_path / 'manifest.json'
    transcript_path = meeting_path / 'transcript.md'
    if not manifest_path.exists():
        raise SystemExit('manifest.json missing')
    if not transcript_path.exists():
        raise SystemExit('transcript.md missing')
    manifest = _read_manifest(manifest_path)
    transcript = transcript_path.read_text()
    result = generate_shapes(meeting_path, manifest, transcript, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
