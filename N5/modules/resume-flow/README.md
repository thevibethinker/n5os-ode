# Resume Flow Module

**Purpose**: Self-contained module for resume detection and routing

## Module Architecture (Zero-Doc)

Self-contained module with single responsibility. Intersects with system via:
- **Reads**: `N5/data/learned_patterns.json`, `N5/config/anchors.json`
- **Called by**: `file_flow_router.py`
- **No direct filesystem access**: Returns routing decision; router executes

## Detection Logic

**High confidence (0.95)**:
- Filename contains: "resume", "cv", "curriculum vitae"

**Medium confidence (0.75)**:
- PDF/DOCX with underscore/hyphen (name pattern)
- No system-file keywords

## Filename Normalization

Input: `Amanda Sachs-GP Resume-July 17 v1.docx`  
Output: `Amanda_Sachs_GP_Resume.docx`

## Learning Integration

- Reads `learned_patterns.json` for accuracy boost
- If resume pattern accuracy > 90%, confidence +0.05

## Usage

```python
from N5.modules.resume_flow.classifier import classify

result = classify(Path('/home/workspace/somefile.pdf'), learned_patterns)
# Returns: {'matched': True, 'confidence': 0.95, 'destination': 'Documents/Resumes', ...}
```

## Testing

```bash
python3 /home/workspace/N5/modules/resume-flow/classifier.py /path/to/test.pdf
```

---

**Version**: 1.0  
**Updated**: 2025-10-24
