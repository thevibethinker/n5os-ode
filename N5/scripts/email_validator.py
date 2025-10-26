#!/usr/bin/env python3
"""
Email Output Guard/Extractor
- Accepts raw model output as text (stdin or --in path)
- Preferred format: JSON {"subject": str, "body": str}
- Fallbacks: <<<EMAIL>>> ... <<<END>>> delimiters; or heuristic extraction
- Validates and returns clean body (stdout) and optional subject (via --emit-subject)
Exit codes: 0 ok, 2 invalid schema, 3 validation failure
"""
import sys, json, re, argparse
from pathlib import Path

FORBIDDEN_PATTERNS = [r"```", r"\bEOF\b", r"\bwc -w\b", r"\bcat\s*>\b", r"^py(thon3?)?\b", r"count\s*=\s*len\("]
GREETING_RE = re.compile(r"^(Hi|Hey)\s+[A-Z][a-zA-Z\-']+,\s*$")
SIGNOFF_START_RE = re.compile(r"^(Best,|Thanks,|Thank you,|Warmly,|Sincerely,)\s*$")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SUBJECT_RE = re.compile(r"^\*\*Subject:\*\*\s*(.+)$|^Subject:\s*(.+)$", re.I)


def read_text(p: str | None) -> str:
    if p:
        return Path(p).read_text(encoding="utf-8", errors="ignore")
    return sys.stdin.read()


def try_json(text: str):
    try:
        data = json.loads(text)
        body = data.get("body") if isinstance(data, dict) else None
        subject = data.get("subject") if isinstance(data, dict) else None
        if isinstance(body, str) and body.strip():
            return subject, body
    except Exception:
        pass
    return None, None


def try_delimiters(text: str):
    m = re.search(r"<<<EMAIL>>>\s*(.*?)\s*<<<END>>>", text, re.S)
    if m:
        return None, m.group(1).strip()
    return None, None


def try_heuristic(text: str):
    lines = text.splitlines()
    subject = None
    # scan a subject line if present near the top
    for i in range(min(15, len(lines))):
        sm = SUBJECT_RE.search(lines[i])
        if sm:
            subject = next(g for g in sm.groups() if g) if sm else None
            break
    # find greeting
    start = None
    for i, ln in enumerate(lines):
        if GREETING_RE.match(ln.strip()):
            start = i
            break
    if start is None:
        return subject, None
    # find end: first empty line after a sign-off block containing V's signature or an email address
    end = None
    for j in range(start + 1, len(lines)):
        if SIGNOFF_START_RE.match(lines[j].strip()):
            # extend until we see an email or 6 lines ahead or blank after signature
            for k in range(j, min(j + 12, len(lines))):
                if EMAIL_RE.search(lines[k]) or lines[k].strip() == "" or k == len(lines) - 1:
                    end = k
                    break
            if end is not None:
                break
    # fallback: stop before a fenced code or EOF marker
    if end is None:
        for j in range(start + 1, len(lines)):
            if re.search(r"```|^EOF$", lines[j]):
                end = j - 1
                break
    if end is None:
        end = len(lines) - 1
    body = "\n".join(lines[start : end + 1]).strip()
    return subject, body if body else None


def has_forbidden(text: str) -> str | None:
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text, re.M):
            return pat
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path")
    ap.add_argument("--emit-subject", action="store_true")
    ap.add_argument("--min-words", type=int, default=120)
    args = ap.parse_args()

    raw = read_text(args.in_path)

    subject, body = try_json(raw)
    if not body:
        subject, body = try_delimiters(raw)
    if not body:
        subject, body = try_heuristic(raw)
    if not body:
        print(json.dumps({"ok": False, "error": "extraction_failed"}))
        sys.exit(2)

    fb = has_forbidden(body)
    wc = len(re.findall(r"\b\w+\b", body))
    if fb or wc < args.min_words:
        print(json.dumps({"ok": False, "error": "validation_failed", "forbidden": fb, "word_count": wc}))
        sys.exit(3)

    out = {"ok": True, "word_count": wc}
    if args.emit_subject:
        out["subject"] = subject
    # print clean body to stdout
    print(body)
    # and emit a side-channel JSON on stderr for logging
    print(json.dumps(out), file=sys.stderr)

if __name__ == "__main__":
    main()
