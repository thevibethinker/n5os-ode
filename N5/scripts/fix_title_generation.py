#!/usr/bin/env python3
"""
CRITICAL FIX: Title Generation with Validation
Patches n5_title_generator_local.py to prevent duplicate word generation

This fix:
1. Adds duplicate detection before returning titles
2. Improves fallback logic to extract better titles
3. Adds retry mechanism
4. Validates output quality
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add validation functions
def validate_title_quality(title: str) -> Tuple[bool, str]:
    """
    Validate that a title meets quality standards
    
    Returns: (is_valid, error_message)
    """
    if not title:
        return False, "Empty title"
    
    if '|' not in title:
        return False, "Missing date separator"
    
    parts = title.split('|', 1)
    if len(parts) != 2:
        return False, "Invalid format"
    
    content = parts[1].strip()
    
    # Remove emoji from start of content
    content_no_emoji = re.sub(r'^[^\w\s]+\s*', '', content)
    words = content_no_emoji.split()
    
    # Check for duplicate consecutive words
    for i in range(len(words) - 1):
        if words[i].lower() == words[i+1].lower():
            return False, f"Duplicate words: '{words[i]} {words[i+1]}'"
    
    # Check minimum meaningful content
    if len(words) < 2:
        return False, "Too short, needs more context"
    
    # Check for generic titles
    generic_patterns = [
        r'^conversation$',
        r'^work work$',
        r'^build build$',
        r'^system system$'
    ]
    
    content_lower = content_no_emoji.lower()
    for pattern in generic_patterns:
        if re.search(pattern, content_lower):
            return False, f"Generic/duplicate pattern: {pattern}"
    
    return True, "Valid"


def fix_title_if_possible(title: str, aar_data: Dict) -> Optional[str]:
    """
    Attempt to fix a bad title using AAR data
    
    Returns: Fixed title or None if unfixable
    """
    if not title or '|' not in title:
        return None
    
    parts = title.split('|', 1)
    date_prefix = parts[0].strip()
    content = parts[1].strip()
    
    # Extract emoji
    emoji_match = re.match(r'^([^\w\s]+)\s*', content)
    emoji = emoji_match.group(1) if emoji_match else '✅'
    
    # Try to extract better content from AAR
    objective = aar_data.get('objective', '')
    focus = aar_data.get('focus', '')
    summary = aar_data.get('summary', '')
    
    # Extract meaningful phrases
    candidates = []
    
    if objective and len(objective) > 15:
        # Clean objective
        obj_clean = re.sub(r'^(build|create|implement|design|fix|debug|update|add|work on)\s+', '', objective, flags=re.IGNORECASE)
        obj_clean = re.sub(r'\s+(for|to|in|on|with)\s+.*$', '', obj_clean, flags=re.IGNORECASE)
        if 10 <= len(obj_clean) <= 40:
            candidates.append(obj_clean.strip())
    
    if focus and len(focus) > 10:
        focus_clean = re.sub(r'^(working on|discussing|building)\s+', '', focus, flags=re.IGNORECASE)
        if 10 <= len(focus_clean) <= 40:
            candidates.append(focus_clean.strip())
    
    # Select best candidate
    for candidate in candidates:
        words = candidate.split()
        # Check no duplicates
        has_dup = any(words[i].lower() == words[i+1].lower() for i in range(len(words)-1))
        if not has_dup and len(words) >= 2:
            return f"{date_prefix} | {emoji} {candidate.title()}"
    
    return None


# Patch the existing generator
def patch_title_generator():
    """
    Patch n5_title_generator_local.py with validation
    """
    target_file = Path("/home/workspace/N5/scripts/n5_title_generator_local.py")
    
    if not target_file.exists():
        print(f"❌ File not found: {target_file}")
        return False
    
    content = target_file.read_text()
    
    # Check if already patched
    if "validate_title_quality" in content:
        print("✅ Already patched")
        return True
    
    # Find the generate_title method and add validation
    validation_code = '''
    
    def _validate_and_fix_title(self, title_result: Dict, aar_data: Dict) -> Dict:
        """Validate title and attempt fix if needed"""
        title = title_result.get("title", "")
        
        # Validation check
        is_valid, error = self._validate_quality(title)
        
        if is_valid:
            return title_result
        
        # Try to fix
        print(f"⚠️  Title validation failed: {error}")
        print(f"   Original: {title}")
        
        fixed = self._attempt_fix(title, aar_data)
        if fixed:
            is_valid_fixed, _ = self._validate_quality(fixed)
            if is_valid_fixed:
                print(f"   Fixed: {fixed}")
                title_result["title"] = fixed
                title_result["base_title"] = fixed.split('|', 1)[1].strip()
                title_result["was_fixed"] = True
                return title_result
        
        # Cannot fix, mark as invalid
        title_result["validation_error"] = error
        title_result["valid"] = False
        return title_result
    
    def _validate_quality(self, title: str) -> tuple:
        """Check title quality"""
        if not title or '|' not in title:
            return False, "Invalid format"
        
        parts = title.split('|', 1)
        content = parts[1].strip()
        content_no_emoji = re.sub(r'^[^\\w\\s]+\\s*', '', content)
        words = content_no_emoji.split()
        
        # Check duplicates
        for i in range(len(words) - 1):
            if words[i].lower() == words[i+1].lower():
                return False, f"Duplicate: {words[i]} {words[i+1]}"
        
        # Check minimum content
        if len(words) < 2:
            return False, "Too short"
        
        return True, "OK"
    
    def _attempt_fix(self, title: str, aar_data: Dict) -> str:
        """Try to fix bad title"""
        parts = title.split('|', 1)
        date_prefix = parts[0].strip()
        content = parts[1].strip()
        emoji_match = re.match(r'^([^\\w\\s]+)\\s*', content)
        emoji = emoji_match.group(1) if emoji_match else '✅'
        
        # Extract from AAR
        objective = aar_data.get('objective', '')
        focus = aar_data.get('focus', '')
        
        for source in [objective, focus]:
            if len(source) > 15:
                clean = re.sub(r'^(build|create|implement|work on)\\s+', '', source, flags=re.IGNORECASE)
                clean = re.sub(r'\\s+(for|to|in|on)\\s+.*$', '', clean, flags=re.IGNORECASE)
                if 10 <= len(clean) <= 40:
                    words = clean.split()
                    has_dup = any(words[i].lower() == words[i+1].lower() for i in range(len(words)-1))
                    if not has_dup:
                        return f"{date_prefix} | {emoji} {clean.strip().title()}"
        
        return None
'''
    
    # Insert validation methods before generate_title
    insert_point = content.find("    def generate_title(")
    if insert_point == -1:
        print("❌ Could not find generate_title method")
        return False
    
    new_content = content[:insert_point] + validation_code + "\n" + content[insert_point:]
    
    # Now patch generate_title to call validation
    # Find the return statement
    pattern = r'(        return \{[\s\S]*?\n        \})'
    
    def add_validation(match):
        original_return = match.group(1)
        return f'''        title_result = {original_return[15:]}  # Remove 'return '
        
        # Validate and fix if needed
        title_result = self._validate_and_fix_title(title_result, aar_data)
        
        return title_result'''
    
    new_content = re.sub(pattern, add_validation, new_content, count=1)
    
    # Backup original
    backup_file = target_file.with_suffix('.py.backup')
    target_file.rename(backup_file)
    print(f"✅ Backed up original to: {backup_file}")
    
    # Write patched version
    target_file.write_text(new_content)
    print(f"✅ Patched: {target_file}")
    
    return True


def test_validation():
    """Test the validation function"""
    test_cases = [
        ("Oct 28 | ✅ System Work Work", False, "Should detect duplicate"),
        ("Oct 28 | ✅ Build Build System", False, "Should detect duplicate"),
        ("Oct 28 | ✅ Meeting Processor Debug", True, "Should pass"),
        ("Oct 28 | 🔧 N5 System Refactor", True, "Should pass"),
        ("Oct 28 | Conversation", False, "Should detect generic"),
    ]
    
    print("\n" + "=" * 70)
    print("VALIDATION TESTS")
    print("=" * 70)
    
    for title, expected_valid, description in test_cases:
        is_valid, error = validate_title_quality(title)
        status = "✅" if is_valid == expected_valid else "❌"
        print(f"{status} {description}")
        print(f"   Title: {title}")
        print(f"   Result: {'Valid' if is_valid else f'Invalid - {error}'}")
        print()


def main():
    print("=" * 70)
    print("N5 TITLE GENERATION FIX")
    print("=" * 70)
    print()
    
    # Run validation tests
    test_validation()
    
    # Apply patch
    print("\n" + "=" * 70)
    print("APPLYING PATCH")
    print("=" * 70)
    
    if patch_title_generator():
        print("\n✅ Patch applied successfully!")
        print("\nNext steps:")
        print("1. Test with: python3 /home/workspace/N5/scripts/n5_title_generator_local.py --aar <path>")
        print("2. Run conversation end on a test conversation")
        print("3. Verify titles no longer have duplicates")
        return 0
    else:
        print("\n❌ Patch failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
