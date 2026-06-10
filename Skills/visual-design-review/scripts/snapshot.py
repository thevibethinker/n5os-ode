#!/usr/bin/env python3
"""
visual-design-review: snapshot a URL across viewports + optional DOM telemetry.

Usage examples:
  snapshot.py URL --label my-page-before
  snapshot.py URL --all --selectors "h1, .hero, button"
  snapshot.py URL --viewports mobile,fold-cover --wait-for "main"

Output: <out>/<label>-<timestamp>/{manifest.json, screenshots/, dom/}

NOTE: Reconstructed from compiled bytecode (the original source was lost);
behavior matches the original CLI surface and capture flow.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    sys.stderr.write("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium\n")
    sys.exit(2)

PRESETS = {
    "mobile": {"width": 390, "height": 844, "device_scale_factor": 2, "is_mobile": True, "has_touch": True, "label": "iPhone-class mobile"},
    "desktop": {"width": 1440, "height": 900, "device_scale_factor": 1, "is_mobile": False, "has_touch": False, "label": "Standard desktop"},
    "fold-cover": {"width": 344, "height": 882, "device_scale_factor": 2.625, "is_mobile": True, "has_touch": True, "label": "Galaxy Z Fold cover (folded)"},
    "fold-inner": {"width": 884, "height": 1104, "device_scale_factor": 2, "is_mobile": True, "has_touch": True, "label": "Galaxy Z Fold inner (unfolded)"},
    "flip": {"width": 412, "height": 1004, "device_scale_factor": 2.625, "is_mobile": True, "has_touch": True, "label": "Galaxy Z Flip (unfolded)"},
}
DEFAULT_VIEWPORTS = ["mobile", "desktop"]
ALL_VIEWPORTS = list(PRESETS.keys())

DOM_TELEMETRY_JS = """
(selectors) => {
  const isVisible = (el) => {
    if (!el) return false;
    const cs = window.getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || cs.opacity === "0") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const out = [];
  for (const sel of selectors) {
    const nodes = Array.from(document.querySelectorAll(sel)).slice(0, 20);
    out.push({
      selector: sel,
      count: nodes.length,
      nodes: nodes.map((el) => {
        const r = el.getBoundingClientRect();
        const cs = window.getComputedStyle(el);
        return {
          tag: el.tagName.toLowerCase(),
          visible: isVisible(el),
          rect: { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height) },
          fontSize: cs.fontSize,
          fontWeight: cs.fontWeight,
          color: cs.color,
          background: cs.backgroundColor,
          overflowX: el.scrollWidth > el.clientWidth,
          text: (el.textContent || "").trim().slice(0, 120),
        };
      }),
    });
  }
  return {
    viewport: { w: window.innerWidth, h: window.innerHeight },
    docHeight: document.documentElement.scrollHeight,
    horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth,
    selectors: out,
  };
}
"""


def _slugify(s=None):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s or "").strip("-").lower()
    return s or "page"


def _default_out_dir():
    convo = os.environ.get("ZO_CONVERSATION_ID")
    if convo:
        base = Path("/home/.z/workspaces") / convo
        if base.is_dir():
            return base / "visual-review"
    return Path("/tmp/visual-review")


def parse_add_viewport(spec):
    if "=" not in spec or "x" not in spec.split("=", 1)[1].lower():
        raise argparse.ArgumentTypeError(f"--add-viewport must look like 'name=WIDTHxHEIGHT', got {spec!r}")
    name, dims = spec.split("=", 1)
    name = name.strip()
    w, h = re.split(r"[xX]", dims.strip(), 1)
    width, height = int(w), int(h)
    is_mobile = width <= 700
    return name, {
        "width": width,
        "height": height,
        "device_scale_factor": 2 if is_mobile else 1,
        "is_mobile": is_mobile,
        "has_touch": is_mobile,
        "label": f"Custom {name} ({width}x{height})",
    }


def split_selectors(raw):
    if not raw:
        return []
    raw = raw.strip()
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            return [str(s).strip() for s in parsed if str(s).strip()]
        except Exception:
            pass
    if "\n" in raw:
        return [s.strip() for s in raw.splitlines() if s.strip()]
    return [s.strip() for s in raw.split(",") if s.strip()]


def _load_netscape_cookies(path, url):
    cookies = []
    host = urlparse(url).hostname or ""
    try:
        for line in Path(path).read_text(errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            domain, _flag, cpath, secure, _expiry, name, value = parts[:7]
            if host and domain.lstrip(".") not in host and host not in domain.lstrip("."):
                continue
            cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": cpath or "/",
                "secure": secure.upper() == "TRUE",
            })
    except Exception as e:
        sys.stderr.write(f"cookie load: {e}\n")
    return cookies


def capture(url, label, out_dir, viewports, selectors, wait_for, wait_ms,
            full_page=True, above_fold=True, cookies_file=None, timeout_ms=30000, quiet=False):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = Path(out_dir) / f"{label}-{ts}"
    shots_dir = run_dir / "screenshots"
    dom_dir = run_dir / "dom"
    shots_dir.mkdir(parents=True, exist_ok=True)
    if selectors:
        dom_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "url": url,
        "label": label,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "viewports": {},
    }
    t0 = time.time()

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for vp_name in viewports:
            preset = PRESETS.get(vp_name)
            if not preset:
                if not quiet:
                    print(f"  skipping unknown viewport: {vp_name}")
                continue

            context = browser.new_context(
                viewport={"width": preset["width"], "height": preset["height"]},
                device_scale_factor=preset["device_scale_factor"],
                is_mobile=preset["is_mobile"],
                has_touch=preset["has_touch"],
            )
            if cookies_file:
                cookies = _load_netscape_cookies(cookies_file, url)
                if cookies:
                    context.add_cookies(cookies)

            page = context.new_page()
            console_errors = []
            page.on("pageerror", lambda exc: console_errors.append(f"pageerror: {exc}"))
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            entry = {"preset": preset, "console_errors": console_errors}
            try:
                page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            except PWTimeout:
                try:
                    page.goto(url, timeout=timeout_ms)
                except Exception as e:
                    entry["error"] = str(e)

            if wait_for:
                try:
                    page.wait_for_selector(wait_for, timeout=timeout_ms)
                except PWTimeout:
                    entry["warning"] = f"wait_for selector timeout: {wait_for}"
            if wait_ms:
                page.wait_for_timeout(wait_ms)

            entry["final_url"] = page.url

            if above_fold:
                p = shots_dir / f"{vp_name}-abovefold.png"
                page.screenshot(path=str(p))
                entry["above_fold"] = str(p.relative_to(run_dir))
            if full_page:
                p = shots_dir / f"{vp_name}-fullpage.png"
                page.screenshot(path=str(p), full_page=True)
                entry["full_page"] = str(p.relative_to(run_dir))

            if selectors:
                try:
                    telemetry = page.evaluate(DOM_TELEMETRY_JS, selectors)
                    dom_path = dom_dir / f"{vp_name}.json"
                    dom_path.write_text(json.dumps(telemetry, indent=2))
                    entry["dom_telemetry"] = str(dom_path.relative_to(run_dir))
                    entry["dom_summary"] = {
                        "horizontalOverflow": telemetry.get("horizontalOverflow"),
                        "docHeight": telemetry.get("docHeight"),
                    }
                except Exception as e:
                    entry["dom_telemetry_error"] = f"dom telemetry failed: {e}"

            manifest["viewports"][vp_name] = entry
            context.close()
        browser.close()

    manifest["elapsed_ms"] = int((time.time() - t0) * 1000)
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    manifest["_manifest_path"] = str(manifest_path)
    return manifest


def main():
    ap = argparse.ArgumentParser(description="Snapshot a URL across viewports with optional DOM telemetry.")
    ap.add_argument("url", help="Target URL")
    ap.add_argument("--label", help="Slug used in output dir name (default: derived from URL)")
    ap.add_argument("--out", help="Output dir (default: conversation workspace /visual-review/)")
    ap.add_argument("--viewports", help=f"Comma-separated. Available: {', '.join(ALL_VIEWPORTS)}. Default: {', '.join(DEFAULT_VIEWPORTS)}")
    ap.add_argument("--all", action="store_true", help="Use all built-in viewports including Galaxy foldables")
    ap.add_argument("--add-viewport", action="append", default=[], help="Add custom viewport: 'name=WIDTHxHEIGHT' (repeatable)")
    ap.add_argument("--selectors", help="CSS selectors for DOM telemetry. Pass a JSON array, newline-separated string, or single CSS selector list.")
    ap.add_argument("--wait-for", help="Wait for this selector to appear after networkidle")
    ap.add_argument("--wait-ms", type=int, default=300, help="Extra ms to wait after load+selector (default: 300)")
    ap.add_argument("--no-full-page", action="store_true", help="Skip full-page screenshots")
    ap.add_argument("--no-above-fold", action="store_true", help="Skip above-the-fold screenshots")
    ap.add_argument("--cookies-file", help="Netscape-format cookies.txt for authenticated sites")
    ap.add_argument("--timeout-ms", type=int, default=30000, help="Per-viewport navigation timeout (default: 30000)")
    ap.add_argument("--quiet", action="store_true", help="Less stdout")
    args = ap.parse_args()

    for spec in args.add_viewport:
        name, preset = parse_add_viewport(spec)
        PRESETS[name] = preset

    if args.all:
        viewports = list(PRESETS.keys())
    elif args.viewports:
        viewports = [v.strip() for v in args.viewports.split(",") if v.strip()]
    else:
        viewports = list(DEFAULT_VIEWPORTS)

    label = args.label or _slugify(urlparse(args.url).path or urlparse(args.url).hostname)
    out_dir = Path(args.out) if args.out else _default_out_dir()
    selectors = split_selectors(args.selectors)

    if not args.quiet:
        print(f"→ snapshot {args.url}")
        print(f"  label:     {label}")
        print(f"  out:       {out_dir}")
        print(f"  viewports: {', '.join(viewports)}")
        if selectors:
            print(f"  selectors: {selectors}")

    manifest = capture(
        args.url, label, out_dir, viewports, selectors,
        args.wait_for, args.wait_ms,
        full_page=not args.no_full_page,
        above_fold=not args.no_above_fold,
        cookies_file=args.cookies_file,
        timeout_ms=args.timeout_ms,
        quiet=args.quiet,
    )
    print(f"\n✓ manifest: {manifest['_manifest_path']}")
    print(f"  run_dir:  {Path(manifest['_manifest_path']).parent}")


if __name__ == "__main__":
    main()
