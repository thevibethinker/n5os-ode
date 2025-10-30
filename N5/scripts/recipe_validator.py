#!/usr/bin/env python3
"""Recipe Quality Validator."""
import re, json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ValidationResult:
    recipe_name: str
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0
    
    @property
    def score(self) -> float:
        total = len(self.issues) * 2 + len(self.warnings)
        return max(0, 100 - (total * 5)) if total else 100.0

class RecipeValidator:
    PLACEHOLDER_PATTERNS = [
        r'\[.*?TODO.*?\]', r'\[.*?PLACEHOLDER.*?\]', r'\[.*?TBD.*?\]',
        r'TODO:', r'FIXME:', r'XXX:'
    ]
    MIN_CONTENT_LINES = 5
    
    def __init__(self, recipes_dir: Path):
        self.recipes_dir = recipes_dir
    
    def validate_recipe(self, recipe_file: Path) -> ValidationResult:
        result = ValidationResult(recipe_name=recipe_file.name)
        try:
            content = recipe_file.read_text()
        except Exception as e:
            result.issues.append(f"Cannot read: {e}")
            return result
        
        fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not fm_match:
            result.issues.append("Missing YAML frontmatter")
        else:
            fm = fm_match.group(1)
            if 'description:' not in fm:
                result.warnings.append("Missing description")
        
        body = content[fm_match.end():] if fm_match else content
        body_lines = [l for l in body.split('\n') if l.strip()]
        
        if len(body_lines) < self.MIN_CONTENT_LINES:
            result.issues.append(
                f"Only {len(body_lines)} lines (min: {self.MIN_CONTENT_LINES})"
            )
        
        for pattern in self.PLACEHOLDER_PATTERNS:
            if re.search(pattern, body, re.IGNORECASE):
                result.warnings.append("Contains placeholder text")
                break
        
        return result
    
    def validate_all(self) -> Dict[str, ValidationResult]:
        return {
            f.name: self.validate_recipe(f)
            for f in sorted(self.recipes_dir.glob("*.md"))
        }

# Run validation
validator = RecipeValidator(Path("/home/workspace/Recipes"))
results = validator.validate_all()

total = len(results)
valid = sum(1 for r in results.values() if r.is_valid)
avg = sum(r.score for r in results.values()) / total

print("=" * 70)
print("RECIPE QUALITY VALIDATION")
print("=" * 70)
print(f"\nTotal: {total} | Valid: {valid} ({valid/total*100:.1f}%) | Avg Score: {avg:.1f}/100\n")

issues = {n: r for n, r in results.items() if r.issues}
if issues:
    print(f"CRITICAL ISSUES: {len(issues)}")
    print("-" * 70)
    for name in sorted(issues.keys())[:15]:
        r = issues[name]
        print(f"❌ {name} ({r.score:.0f}/100)")
        for issue in r.issues[:2]:
            print(f"   • {issue}")

warnings_only = {n: r for n, r in results.items() if r.warnings and not r.issues}
if warnings_only:
    print(f"\nWARNINGS: {len(warnings_only)} (showing 10)")
    print("-" * 70)
    for name in sorted(warnings_only.keys())[:10]:
        r = warnings_only[name]
        print(f"⚠️  {name} ({r.score:.0f}/100): {r.warnings[0]}")

perfect = [n for n, r in results.items() if r.score == 100]
print(f"\n✅ PERFECT: {len(perfect)}")
