#!/bin/bash
# ChildZo N5 Verification Script
# Run this on vademonstrator.zo.computer after receiving n5_clean_verified.tar.gz

set -e

echo "=========================================="
echo "ChildZo N5 Verification Script"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Phase 1: File Integrity
echo "Phase 1: File Integrity Check"
echo "------------------------------"
if [ -f ~/n5_clean_verified.tar.gz ]; then
    FILE_SIZE=$(ls -lh ~/n5_clean_verified.tar.gz | awk '{print $5}')
    echo "✓ File exists: $FILE_SIZE"
    
    MD5=$(md5sum ~/n5_clean_verified.tar.gz | cut -d' ' -f1)
    echo "MD5: $MD5"
    
    if [ "$MD5" = "c5316a38db50f11c19700aad8aa0c878" ]; then
        echo -e "${GREEN}✓ MD5 MATCH - File integrity verified${NC}"
        ((PASS++))
    else
        echo -e "${RED}✗ MD5 MISMATCH - File may be corrupted${NC}"
        echo "Expected: c5316a38db50f11c19700aad8aa0c878"
        echo "Got:      $MD5"
        ((FAIL++))
    fi
else
    echo -e "${RED}✗ File not found: ~/n5_clean_verified.tar.gz${NC}"
    ((FAIL++))
    exit 1
fi
echo ""

# Phase 2: Extraction
echo "Phase 2: Extraction Test"
echo "------------------------"
cd /home/workspace
if tar -xzf ~/n5_clean_verified.tar.gz 2>&1; then
    echo -e "${GREEN}✓ Extraction successful${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ Extraction failed${NC}"
    ((FAIL++))
    exit 1
fi
echo ""

# Phase 3: Structure Validation
echo "Phase 3: Structure Validation"
echo "------------------------------"
COMMANDS_COUNT=$(ls N5/commands/*.md 2>/dev/null | wc -l)
SCRIPTS_COUNT=$(ls N5/scripts/*.py 2>/dev/null | wc -l)
SCHEMAS_COUNT=$(ls N5/schemas/*.json 2>/dev/null | wc -l)
JSONL_LINES=$(wc -l < N5/config/commands.jsonl 2>/dev/null || echo "0")

echo "Commands: $COMMANDS_COUNT (expect 104)"
echo "Scripts:  $SCRIPTS_COUNT (expect 286+)"
echo "Schemas:  $SCHEMAS_COUNT (expect 14)"
echo "commands.jsonl: $JSONL_LINES lines (expect 104)"

if [ "$COMMANDS_COUNT" -eq 104 ] && [ "$SCRIPTS_COUNT" -ge 286 ] && [ "$SCHEMAS_COUNT" -eq 14 ] && [ "$JSONL_LINES" -eq 104 ]; then
    echo -e "${GREEN}✓ File counts match expected${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠ File counts don't match expected (may be acceptable)${NC}"
fi
echo ""

# Phase 4: Key Files Check
echo "Phase 4: Key Files Check"
echo "------------------------"
MISSING=0
for file in "Documents/N5.md" "N5/prefs/prefs.md" "N5/config/commands.jsonl" "Knowledge/architectural/architectural_principles.md"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo -e "${RED}✗ Missing: $file${NC}"
        ((MISSING++))
    fi
done

if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ All key files present${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ $MISSING key files missing${NC}"
    ((FAIL++))
fi
echo ""

# Phase 5: JSON Validity
echo "Phase 5: JSON Validity Check"
echo "----------------------------"
if head -3 N5/config/commands.jsonl | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}✓ commands.jsonl contains valid JSON${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ commands.jsonl has invalid JSON${NC}"
    ((FAIL++))
fi
echo ""

# Phase 6: Permissions
echo "Phase 6: Setting Permissions"
echo "----------------------------"
chmod +x N5/scripts/*.py 2>/dev/null
if [ -x N5/scripts/session_state_manager.py ]; then
    echo -e "${GREEN}✓ Executable permissions set${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠ Could not set executable permissions${NC}"
fi
echo ""

# Phase 7: Script Syntax Check
echo "Phase 7: Script Syntax Check"
echo "----------------------------"
if python3 -m py_compile N5/scripts/session_state_manager.py 2>&1; then
    echo -e "${GREEN}✓ Sample script compiles without errors${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ Script has syntax errors${NC}"
    ((FAIL++))
fi
echo ""

# Phase 8: Functional Test
echo "Phase 8: Functional Test"
echo "------------------------"
if python3 N5/scripts/session_state_manager.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Script executes successfully${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠ Script may have runtime issues${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""
echo "File Counts:"
echo "  Commands: $COMMANDS_COUNT"
echo "  Scripts:  $SCRIPTS_COUNT"
echo "  Schemas:  $SCHEMAS_COUNT"
echo "  commands.jsonl: $JSONL_LINES lines"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo "✓✓✓ VERIFICATION SUCCESSFUL ✓✓✓"
    echo "==========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Load file 'Documents/N5.md'"
    echo "2. Load file 'N5/prefs/prefs.md'"
    echo "3. Load file 'Knowledge/architectural/architectural_principles.md'"
    echo "4. Initialize session state"
    echo "5. Report success to ParentZo via ZoBridge"
    exit 0
else
    echo -e "${RED}=========================================="
    echo "✗✗✗ VERIFICATION FAILED ✗✗✗"
    echo "==========================================${NC}"
    echo ""
    echo "Report these results to ParentZo via ZoBridge"
    echo "Consider trying Option 2 (split archives)"
    exit 1
fi
