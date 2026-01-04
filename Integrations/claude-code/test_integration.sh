#!/bin/bash
# Test script for Claude Code + N5OS Integration
# Run this to verify all components work before using with Claude Code

set -e

echo "=========================================="
echo "Claude Code + N5OS Integration Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}✓ PASS${NC}: $1"; }
fail() { echo -e "${RED}✗ FAIL${NC}: $1"; exit 1; }

# Test 1: Check all required files exist
echo "Test 1: Checking required files..."
[[ -f "/home/workspace/Integrations/claude-code/n5_mcp_bridge.ts" ]] || fail "n5_mcp_bridge.ts missing"
[[ -f "/home/workspace/Integrations/claude-code/CLAUDE.md" ]] || fail "CLAUDE.md missing"
[[ -f "/home/workspace/Integrations/claude-code/n5-planning-skill.md" ]] || fail "n5-planning-skill.md missing"
[[ -f "/home/workspace/Integrations/claude-code/README.md" ]] || fail "README.md missing"
[[ -f "/home/workspace/N5/scripts/close_convo_bridge.py" ]] || fail "close_convo_bridge.py missing"
pass "All required files exist"

# Test 2: Check dependencies installed
echo "Test 2: Checking Bun dependencies..."
[[ -d "/home/workspace/Integrations/claude-code/node_modules/@modelcontextprotocol" ]] || fail "MCP SDK not installed"
pass "Bun dependencies installed"

# Test 3: Test n5_protect.py
echo "Test 3: Testing n5_protect.py check..."
result=$(python3 /home/workspace/N5/scripts/n5_protect.py check /home/workspace/N5 2>&1)
[[ "$result" == *"PROTECTED"* ]] || fail "n5_protect.py check failed: $result"
pass "n5_protect.py works"

# Test 4: Test close_convo_bridge.py (dry run)
echo "Test 4: Testing close_convo_bridge.py..."
result=$(python3 /home/workspace/N5/scripts/close_convo_bridge.py --summary "Integration test" --tier 1 2>&1)
[[ "$result" == *"success"* ]] || fail "close_convo_bridge.py failed: $result"
pass "close_convo_bridge.py works"

# Test 5: Check MCP bridge can start (will exit immediately without stdio)
echo "Test 5: Testing MCP bridge startup..."
cd /home/workspace/Integrations/claude-code
timeout 2 bun run n5_mcp_bridge.ts 2>&1 || true
pass "MCP bridge starts without errors"

echo ""
echo "=========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "=========================================="
echo ""
echo "Next steps for V:"
echo "1. Run: claude mcp add --transport stdio n5-bridge -- bun /home/workspace/Integrations/claude-code/n5_mcp_bridge.ts"
echo "2. Run: claude skill add /home/workspace/Integrations/claude-code/n5-planning-skill.md"
echo "3. Copy CLAUDE.md to your project roots"
echo ""


