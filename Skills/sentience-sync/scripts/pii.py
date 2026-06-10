"""
PII stripping module — comprehensive patterns for scrubbing
personal information before pushing to external systems.
"""

import re

PII_PATTERNS = [
    # Emails
    (re.compile(r'[\w.+-]+@[\w.-]+\.\w{2,}'), '[EMAIL]'),
    (re.compile(r'[\w.+-]+\s*\[at\]\s*[\w.-]+\s*\[?dot\]?\s*\w{2,}', re.I), '[EMAIL]'),

    # Phone numbers — US formats
    (re.compile(r'\+?1?\s*\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4}\b'), '[PHONE]'),
    # International
    (re.compile(r'\+\d{1,3}\s?\(?\d{1,4}\)?[\s.-]*\d{2,4}[\s.-]*\d{2,4}[\s.-]*\d{0,4}'), '[PHONE]'),

    # Addresses — broader patterns
    (re.compile(r'\b\d{1,5}\s+[\w\s]{1,30}\b(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Road|Rd|Lane|Ln|Way|Court|Ct|Place|Pl|Circle|Cir|Terrace|Ter|Parkway|Pkwy|Highway|Hwy)\b', re.I), '[ADDRESS]'),
    (re.compile(r'\b(?:Apt|Suite|Unit|#)\s*\d+\w?\b', re.I), '[ADDRESS]'),
    (re.compile(r'\b(?:PO|P\.O\.)\s*Box\s*\d+\b', re.I), '[ADDRESS]'),

    # API keys and tokens — broad coverage
    (re.compile(r'\b(?:sk_live|sk_test|sk-ant-|sk-)[A-Za-z0-9_-]{20,}\b'), '[REDACTED_KEY]'),
    (re.compile(r'\b(?:whsec_|ghp_|github_pat_|gho_|ghu_|ghs_)[A-Za-z0-9_-]{20,}\b'), '[REDACTED_KEY]'),
    (re.compile(r'\b(?:xoxb-|xoxp-|xoxa-|xoxr-)[A-Za-z0-9_-]{20,}\b'), '[REDACTED_KEY]'),
    (re.compile(r'\bAIza[A-Za-z0-9_-]{30,}\b'), '[REDACTED_KEY]'),
    (re.compile(r'\bAKIA[A-Z0-9]{16}\b'), '[REDACTED_KEY]'),
    (re.compile(r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'), '[REDACTED_KEY]'),
    (re.compile(r'\beyJ[A-Za-z0-9_-]{50,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'), '[REDACTED_JWT]'),

    # URLs with sensitive params
    (re.compile(r'https?://\S*(?:password|token|key|secret|auth|sig|code|state)=[^\s&]+', re.I), '[REDACTED_URL]'),
    # Meeting/calendar links (contain identifiers)
    (re.compile(r'https?://(?:meet\.google\.com|zoom\.us|teams\.microsoft\.com)/\S+'), '[MEETING_LINK]'),
    (re.compile(r'https?://calendly\.com/\S+'), '[CALENDAR_LINK]'),

    # SSN-like
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN]'),

    # Credit card last4 in context
    (re.compile(r'(?:card|ending|last\s*4)\s*[:#]?\s*\d{4}\b', re.I), '[CARD]'),
]

# Frontmatter — linear-time, safe for large YAML (no nested quantifiers)
# Matches: --- (at start) + one or more lines + --- (on its own line) + blank line
FRONTMATTER_RE = re.compile(r'\A---\n(?:[^\n]*\n){1,}?(?=^---\n)', flags=re.MULTILINE)


def strip_pii(text: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub('', text, count=1)


def clean(text: str) -> str:
    text = strip_frontmatter(text)
    text = strip_pii(text)
    return text.strip()
