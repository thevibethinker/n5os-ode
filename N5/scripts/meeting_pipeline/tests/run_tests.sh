#!/bin/bash
# Test runner for meeting pipeline tests

set -e

echo "=========================================="
echo "Meeting Pipeline Test Suite"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Installing pytest..."
    pip install -q pytest
fi

# Run tests
echo "Running path resolution tests..."
python3 -m pytest test_path_resolution.py -v --tb=short

echo ""
echo "Running integration tests..."
python3 -m pytest test_integration.py -v --tb=short

echo ""
echo "=========================================="
echo "✓ All tests completed"
echo "=========================================="
