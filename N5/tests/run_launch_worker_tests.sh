#!/bin/bash

# Test Runner for n5 launch-worker
# Runs all tests and reports results

set -e

echo "======================================"
echo "N5 Launch Worker Test Suite"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Test 1: Help command
echo -n "Test 1: Help command... "
if n5 --help > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
fi

# Test 2: Launch worker help
echo -n "Test 2: Launch worker help... "
if n5 launch-worker --help > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
fi

# Test 3: Dry run with parent (should validate parent)
echo -n "Test 3: Basic validation (dry-run)... "
if n5 launch-worker --parent con_uiRqdJ0LqrrAEyjc --dry-run > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
fi

# Test 4: Type validation
echo -n "Test 4: Worker types supported... "
if n5 launch-worker --help | grep -q "build.*research.*analysis"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
fi

# Test 5: Instruction enhancement check
echo -n "Test 5: Instruction enhancement... "
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from n5_launch_worker import LaunchWorker
lw = LaunchWorker('con_test')
result = lw.enhance_instruction('Test instruction', 'build')
assert 'optimized' in result.lower()
" > /dev/null 2>&1 && {
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
}

# Test 6: Wizard validation (check if wizard starts)
echo -n "Test 6: Wizard initialization... "
timeout 3 bash -c "echo 'con_test' | n5 launch-worker --wizard --dry-run" 2>&1 | grep -q "Wizard" && {
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
}

# Test 7: Invalid parent format
echo -n "Test 7: Invalid parent validation... "
n5 launch-worker --parent invalid_id 2>&1 | grep -q "must start with" && {
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
}

# Test 8: Integration with spawn_worker
echo -n "Test 8: Integration with spawn_worker... "
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from n5_launch_worker import LaunchWorker
lw = LaunchWorker('con_test')
assert hasattr(lw, 'spawn_worker')
" > /dev/null 2>&1 && {
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
}

# Summary
echo ""
echo "======================================"
echo -e "Tests Passed: ${GREEN}$PASS${NC}"
echo -e "Tests Failed: ${RED}$FAIL${NC}"
echo "======================================"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi

